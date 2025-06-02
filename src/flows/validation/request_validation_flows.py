"""Request Validation Flows for OpenRouter Anthropic Server.

Prefect flows that orchestrate request validation tasks into comprehensive
validation pipelines for HTTP requests, API validation, and security assessment.

Part of Phase 6B comprehensive refactoring - Validation Flow Orchestration.
"""

import asyncio
from typing import Any, Dict, List, Optional

from prefect import flow
from prefect.task_runners import ConcurrentTaskRunner

from ...core.logging_config import get_logger
from ...models.instructor import ConversionResult
from ...tasks.validation.request_validation import (
    validate_http_request_task,
    validate_api_parameters_task,
    validate_anthropic_request_task,
    validate_request_rate_limit_task
)
from ...tasks.validation.security_validation import (
    validate_request_authentication_task,
    validate_request_origin_task,
    validate_content_safety_task
)

# Initialize logging
logger = get_logger("request_validation_flows")


@flow(
    name="http_request_validation",
    description="Comprehensive HTTP request validation pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "http", "requests"]
)
async def http_request_validation_flow(
    request_data: Dict[str, Any],
    validation_config: Dict[str, Any] = None,
    security_config: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform comprehensive HTTP request validation including headers, structure, and security.
    
    Args:
        request_data: HTTP request data to validate
        validation_config: HTTP validation configuration
        security_config: Security validation configuration
    
    Returns:
        ConversionResult with comprehensive HTTP validation results
    """
    logger.info("Starting HTTP request validation")
    
    try:
        if validation_config is None:
            validation_config = {}
        if security_config is None:
            security_config = {}
        
        validation_results = {
            "is_valid_request": True,
            "validation_summary": {
                "http_validation": None,
                "origin_validation": None,
                "authentication_validation": None,
                "security_assessment": None
            },
            "errors": [],
            "warnings": [],
            "request_metadata": {
                "method": request_data.get("method"),
                "url": request_data.get("url"),
                "content_type": None,
                "user_agent": None,
                "client_ip": None,
                "request_size": 0
            }
        }
        
        # Step 1: Basic HTTP request validation
        http_result = await validate_http_request_task(
            request_data=request_data,
            validation_rules=validation_config.get("http_rules", {})
        )
        
        validation_results["validation_summary"]["http_validation"] = http_result.converted_data
        
        if not http_result.success or not http_result.converted_data.get("is_valid_origin", True):
            validation_results["is_valid_request"] = False
            if http_result.errors:
                validation_results["errors"].extend(http_result.errors)
            
            if http_result.converted_data:
                validation_results["errors"].extend(http_result.converted_data.get("errors", []))
                validation_results["warnings"].extend(http_result.converted_data.get("warnings", []))
                
                # Extract request metadata
                request_info = http_result.converted_data.get("request_info", {})
                validation_results["request_metadata"].update(request_info)
        
        # Step 2: Request origin validation
        request_metadata = {
            "client_ip": request_data.get("client_ip") or request_data.get("headers", {}).get("x-forwarded-for"),
            "user_agent": request_data.get("headers", {}).get("user-agent"),
            "referer": request_data.get("headers", {}).get("referer"),
            "origin": request_data.get("headers", {}).get("origin"),
            "x_forwarded_for": request_data.get("headers", {}).get("x-forwarded-for")
        }
        
        origin_result = await validate_request_origin_task(
            request_metadata=request_metadata,
            origin_rules=security_config.get("origin_rules", {}),
            validation_options=security_config.get("origin_validation_options", {})
        )
        
        validation_results["validation_summary"]["origin_validation"] = origin_result.converted_data
        
        if not origin_result.success or not origin_result.converted_data.get("is_valid_origin", True):
            validation_results["is_valid_request"] = False
            if origin_result.errors:
                validation_results["errors"].extend(origin_result.errors)
            
            if origin_result.converted_data:
                validation_results["errors"].extend(origin_result.converted_data.get("errors", []))
                validation_results["warnings"].extend(origin_result.converted_data.get("warnings", []))
        
        # Step 3: Authentication validation
        auth_data = {
            "api_key": request_data.get("headers", {}).get("x-api-key"),
            "authorization": request_data.get("headers", {}).get("authorization"),
            "x_api_key": request_data.get("headers", {}).get("x-api-key")
        }
        
        if any(auth_data.values()):  # Only validate if auth data is present
            auth_result = await validate_request_authentication_task(
                auth_data=auth_data,
                auth_requirements=security_config.get("auth_requirements", {}),
                validation_options=security_config.get("auth_validation_options", {})
            )
            
            validation_results["validation_summary"]["authentication_validation"] = auth_result.converted_data
            
            if not auth_result.success:
                validation_results["is_valid_request"] = False
                if auth_result.errors:
                    validation_results["errors"].extend(auth_result.errors)
            
            if auth_result.converted_data:
                auth_data_result = auth_result.converted_data
                if not auth_data_result.get("is_authenticated", False) and security_config.get("require_auth", False):
                    validation_results["is_valid_request"] = False
                    validation_results["errors"].append("Authentication required but not provided or invalid")
                
                validation_results["warnings"].extend(auth_data_result.get("warnings", []))
        
        # Step 4: Security assessment
        security_assessment = await _perform_http_security_assessment(
            request_data, validation_results, security_config
        )
        validation_results["validation_summary"]["security_assessment"] = security_assessment
        
        if not security_assessment.get("is_secure", True):
            validation_results["is_valid_request"] = False
            validation_results["errors"].extend(security_assessment.get("security_violations", []))
        
        validation_results["warnings"].extend(security_assessment.get("security_warnings", []))
        
        # Generate recommendations
        recommendations = await _generate_http_validation_recommendations(validation_results)
        validation_results["recommendations"] = recommendations
        
        logger.info("HTTP request validation completed",
                   is_valid=validation_results["is_valid_request"],
                   method=validation_results["request_metadata"]["method"],
                   error_count=len(validation_results["errors"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "method": validation_results["request_metadata"]["method"],
                "validation_type": "http_request",
                "is_valid": validation_results["is_valid_request"]
            }
        )
        
    except Exception as e:
        error_msg = f"HTTP request validation failed: {str(e)}"
        logger.error("HTTP request validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(
    name="anthropic_request_validation",
    description="Comprehensive Anthropic API request validation pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "anthropic", "api"]
)
async def anthropic_request_validation_flow(
    request_data: Dict[str, Any],
    validation_config: Dict[str, Any] = None,
    tool_definitions: List[Dict[str, Any]] = None
) -> ConversionResult:
    """
    Perform comprehensive Anthropic API request validation.
    
    Args:
        request_data: Anthropic request data to validate
        validation_config: Anthropic validation configuration
        tool_definitions: Available tool definitions for validation
    
    Returns:
        ConversionResult with comprehensive Anthropic validation results
    """
    logger.info("Starting Anthropic request validation")
    
    try:
        if validation_config is None:
            validation_config = {}
        if tool_definitions is None:
            tool_definitions = []
        
        validation_results = {
            "is_valid_anthropic_request": True,
            "validation_summary": {
                "request_validation": None,
                "parameter_validation": None,
                "message_validation": None,
                "tool_validation": None
            },
            "errors": [],
            "warnings": [],
            "request_analysis": {
                "model": request_data.get("model"),
                "message_count": len(request_data.get("messages", [])),
                "has_system": bool(request_data.get("system")),
                "has_tools": bool(request_data.get("tools")),
                "stream": request_data.get("stream", False),
                "estimated_tokens": 0
            }
        }
        
        # Step 1: Basic Anthropic request validation
        anthropic_result = await validate_anthropic_request_task(
            request_data=request_data,
            validation_config=validation_config.get("anthropic_config", {})
        )
        
        validation_results["validation_summary"]["request_validation"] = anthropic_result.converted_data
        
        if not anthropic_result.success or not anthropic_result.converted_data.get("request_info", {}).get("model"):
            validation_results["is_valid_anthropic_request"] = False
            if anthropic_result.errors:
                validation_results["errors"].extend(anthropic_result.errors)
            
            if anthropic_result.converted_data:
                validation_results["errors"].extend(anthropic_result.converted_data.get("errors", []))
                validation_results["warnings"].extend(anthropic_result.converted_data.get("warnings", []))
                
                # Extract request analysis
                request_info = anthropic_result.converted_data.get("request_info", {})
                validation_results["request_analysis"].update(request_info)
        
        # Step 2: Parameter validation
        # Extract parameters for validation
        parameters = {
            key: value for key, value in request_data.items()
            if key not in ["messages", "system", "tools"]
        }
        
        if parameters:
            # Define parameter schema for Anthropic API
            parameter_schema = {
                "properties": {
                    "model": {"type": "string", "required": True},
                    "max_tokens": {"type": "integer", "minimum": 1, "maximum": 100000},
                    "temperature": {"type": "number", "minimum": 0, "maximum": 2},
                    "top_p": {"type": "number", "minimum": 0, "maximum": 1},
                    "top_k": {"type": "integer", "minimum": 1},
                    "stop_sequences": {"type": "array"},
                    "stream": {"type": "boolean"}
                },
                "required": ["model"]
            }
            
            param_result = await validate_api_parameters_task(
                parameters=parameters,
                parameter_schema=parameter_schema,
                validation_options=validation_config.get("parameter_options", {})
            )
            
            validation_results["validation_summary"]["parameter_validation"] = param_result.converted_data
            
            if not param_result.success or not param_result.converted_data.get("is_valid", True):
                validation_results["is_valid_anthropic_request"] = False
                if param_result.errors:
                    validation_results["errors"].extend(param_result.errors)
                
                if param_result.converted_data:
                    validation_results["errors"].extend(param_result.converted_data.get("errors", []))
                    validation_results["warnings"].extend(param_result.converted_data.get("warnings", []))
        
        # Step 3: Message validation
        messages = request_data.get("messages", [])
        if messages:
            # Import message validation flow
            from .message_validation_flows import comprehensive_message_validation_flow
            
            message_result = await comprehensive_message_validation_flow(
                messages=messages,
                validation_config=validation_config.get("message_config", {}),
                security_config=validation_config.get("security_config", {})
            )
            
            validation_results["validation_summary"]["message_validation"] = message_result.converted_data
            
            if not message_result.success or not message_result.converted_data.get("overall_valid", True):
                validation_results["is_valid_anthropic_request"] = False
                if message_result.errors:
                    validation_results["errors"].extend(message_result.errors)
                
                if message_result.converted_data:
                    validation_results["errors"].extend(message_result.converted_data.get("errors", []))
                    validation_results["warnings"].extend(message_result.converted_data.get("warnings", []))
        
        # Step 4: Tool validation
        tools = request_data.get("tools", [])
        if tools:
            from .message_validation_flows import tool_call_validation_flow
            
            # Extract tool calls from messages for validation
            tool_calls = []
            for message in messages:
                content = message.get("content", [])
                if isinstance(content, list):
                    tool_calls.extend([
                        block for block in content 
                        if isinstance(block, dict) and block.get("type") == "tool_use"
                    ])
            
            if tool_calls:
                tool_result = await tool_call_validation_flow(
                    tool_calls=tool_calls,
                    available_tools=tools,
                    validation_config=validation_config.get("tool_config", {})
                )
                
                validation_results["validation_summary"]["tool_validation"] = tool_result.converted_data
                
                if not tool_result.success or not tool_result.converted_data.get("is_valid", True):
                    validation_results["is_valid_anthropic_request"] = False
                    if tool_result.errors:
                        validation_results["errors"].extend(tool_result.errors)
                    
                    if tool_result.converted_data:
                        validation_results["errors"].extend(tool_result.converted_data.get("errors", []))
                        validation_results["warnings"].extend(tool_result.converted_data.get("warnings", []))
        
        # Estimate token usage
        token_estimate = await _estimate_request_tokens(request_data)
        validation_results["request_analysis"]["estimated_tokens"] = token_estimate
        
        # Check token limits
        max_tokens_limit = validation_config.get("max_total_tokens", 200000)
        if token_estimate > max_tokens_limit:
            validation_results["warnings"].append(f"Request may exceed token limit: {token_estimate} > {max_tokens_limit}")
        
        # Generate recommendations
        recommendations = await _generate_anthropic_validation_recommendations(validation_results)
        validation_results["recommendations"] = recommendations
        
        logger.info("Anthropic request validation completed",
                   is_valid=validation_results["is_valid_anthropic_request"],
                   model=validation_results["request_analysis"]["model"],
                   message_count=validation_results["request_analysis"]["message_count"],
                   estimated_tokens=validation_results["request_analysis"]["estimated_tokens"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "model": validation_results["request_analysis"]["model"],
                "validation_type": "anthropic_request",
                "is_valid": validation_results["is_valid_anthropic_request"]
            }
        )
        
    except Exception as e:
        error_msg = f"Anthropic request validation failed: {str(e)}"
        logger.error("Anthropic request validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(
    name="api_security_validation",
    description="Comprehensive API security validation pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "security", "api"]
)
async def api_security_validation_flow(
    request_data: Dict[str, Any],
    security_config: Dict[str, Any] = None,
    threat_intelligence: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform comprehensive API security validation including authentication, authorization, and threat detection.
    
    Args:
        request_data: Request data to validate for security
        security_config: Security validation configuration
        threat_intelligence: Threat intelligence data
    
    Returns:
        ConversionResult with comprehensive security validation results
    """
    logger.info("Starting API security validation")
    
    try:
        if security_config is None:
            security_config = {
                "enable_auth_validation": True,
                "enable_origin_validation": True,
                "enable_content_safety": True,
                "enable_threat_detection": True
            }
        if threat_intelligence is None:
            threat_intelligence = {}
        
        validation_results = {
            "is_secure": True,
            "security_score": 1.0,
            "validation_summary": {
                "authentication": None,
                "origin_validation": None,
                "content_safety": None,
                "threat_assessment": None
            },
            "security_violations": [],
            "security_warnings": [],
            "threat_indicators": [],
            "security_metrics": {
                "auth_score": 1.0,
                "origin_score": 1.0,
                "content_score": 1.0,
                "overall_risk": 0.0
            }
        }
        
        # Step 1: Authentication and authorization validation
        if security_config.get("enable_auth_validation", True):
            auth_data = {
                "api_key": request_data.get("headers", {}).get("x-api-key"),
                "authorization": request_data.get("headers", {}).get("authorization"),
                "x_api_key": request_data.get("headers", {}).get("x-api-key")
            }
            
            auth_result = await validate_request_authentication_task(
                auth_data=auth_data,
                auth_requirements=security_config.get("auth_requirements", {}),
                validation_options=security_config.get("auth_options", {})
            )
            
            validation_results["validation_summary"]["authentication"] = auth_result.converted_data
            
            if auth_result.success and auth_result.converted_data:
                auth_data_result = auth_result.converted_data
                
                if not auth_data_result.get("is_authenticated", False):
                    validation_results["is_secure"] = False
                    validation_results["security_violations"].append("Authentication failed")
                    validation_results["security_metrics"]["auth_score"] = 0.0
                elif not auth_data_result.get("is_authorized", False):
                    validation_results["is_secure"] = False
                    validation_results["security_violations"].append("Authorization failed")
                    validation_results["security_metrics"]["auth_score"] = 0.5
                
                validation_results["security_warnings"].extend(auth_data_result.get("warnings", []))
        
        # Step 2: Origin and source validation
        if security_config.get("enable_origin_validation", True):
            request_metadata = {
                "client_ip": request_data.get("client_ip") or request_data.get("headers", {}).get("x-forwarded-for"),
                "user_agent": request_data.get("headers", {}).get("user-agent"),
                "referer": request_data.get("headers", {}).get("referer"),
                "origin": request_data.get("headers", {}).get("origin"),
                "x_forwarded_for": request_data.get("headers", {}).get("x-forwarded-for")
            }
            
            origin_result = await validate_request_origin_task(
                request_metadata=request_metadata,
                origin_rules=security_config.get("origin_rules", {}),
                validation_options=security_config.get("origin_options", {})
            )
            
            validation_results["validation_summary"]["origin_validation"] = origin_result.converted_data
            
            if origin_result.success and origin_result.converted_data:
                origin_data = origin_result.converted_data
                
                if not origin_data.get("is_valid_origin", True):
                    validation_results["is_secure"] = False
                    validation_results["security_violations"].extend(origin_data.get("errors", []))
                
                if origin_data.get("is_suspicious", False):
                    validation_results["threat_indicators"].append("suspicious_origin")
                    validation_results["security_warnings"].append("Request from suspicious origin")
                
                risk_score = origin_data.get("risk_score", 0.0)
                validation_results["security_metrics"]["origin_score"] = max(0.0, 1.0 - risk_score)
                validation_results["security_metrics"]["overall_risk"] += risk_score
        
        # Step 3: Content safety validation
        if security_config.get("enable_content_safety", True):
            # Extract content from request body
            request_content = []
            
            # Check for JSON body content
            body = request_data.get("body")
            if isinstance(body, dict):
                # Extract messages content
                messages = body.get("messages", [])
                for message in messages:
                    content = message.get("content")
                    if isinstance(content, str):
                        request_content.append(content)
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                request_content.append(block.get("text", ""))
                
                # Extract system message
                if body.get("system"):
                    request_content.append(body["system"])
            
            if request_content:
                from .message_validation_flows import content_safety_validation_flow
                
                safety_result = await content_safety_validation_flow(
                    content_items=request_content,
                    safety_config=security_config.get("safety_config", {}),
                    sanitization_config=security_config.get("sanitization_config", {})
                )
                
                validation_results["validation_summary"]["content_safety"] = safety_result.converted_data
                
                if safety_result.success and safety_result.converted_data:
                    safety_data = safety_result.converted_data
                    
                    if not safety_data.get("overall_safe", True):
                        validation_results["is_secure"] = False
                        validation_results["security_violations"].append("Content safety violations detected")
                        validation_results["security_metrics"]["content_score"] = 0.0
                    
                    # Calculate content safety score
                    safe_content = safety_data.get("safety_summary", {}).get("safe_content", 0)
                    total_content = safe_content + safety_data.get("safety_summary", {}).get("unsafe_content", 0)
                    if total_content > 0:
                        validation_results["security_metrics"]["content_score"] = safe_content / total_content
                    
                    validation_results["security_warnings"].extend(safety_data.get("warnings", []))
        
        # Step 4: Threat assessment
        if security_config.get("enable_threat_detection", True):
            threat_assessment = await _perform_threat_assessment(
                request_data, validation_results, threat_intelligence
            )
            validation_results["validation_summary"]["threat_assessment"] = threat_assessment
            
            if threat_assessment.get("threat_detected", False):
                validation_results["is_secure"] = False
                validation_results["security_violations"].extend(threat_assessment.get("threats", []))
                validation_results["threat_indicators"].extend(threat_assessment.get("indicators", []))
            
            validation_results["security_warnings"].extend(threat_assessment.get("warnings", []))
            validation_results["security_metrics"]["overall_risk"] += threat_assessment.get("risk_increase", 0.0)
        
        # Calculate overall security score
        auth_score = validation_results["security_metrics"]["auth_score"]
        origin_score = validation_results["security_metrics"]["origin_score"]
        content_score = validation_results["security_metrics"]["content_score"]
        
        validation_results["security_score"] = (auth_score + origin_score + content_score) / 3
        
        # Apply security thresholds
        min_security_score = security_config.get("min_security_score", 0.7)
        if validation_results["security_score"] < min_security_score:
            validation_results["is_secure"] = False
            validation_results["security_violations"].append(f"Security score {validation_results['security_score']:.2f} below threshold {min_security_score}")
        
        # Generate security recommendations
        recommendations = await _generate_security_recommendations(validation_results)
        validation_results["recommendations"] = recommendations
        
        logger.info("API security validation completed",
                   is_secure=validation_results["is_secure"],
                   security_score=validation_results["security_score"],
                   violation_count=len(validation_results["security_violations"]),
                   threat_indicators=len(validation_results["threat_indicators"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "security_score": validation_results["security_score"],
                "validation_type": "api_security",
                "is_secure": validation_results["is_secure"]
            }
        )
        
    except Exception as e:
        error_msg = f"API security validation failed: {str(e)}"
        logger.error("API security validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(
    name="rate_limit_validation",
    description="Comprehensive rate limiting validation pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "rate-limit", "throttling"]
)
async def rate_limit_validation_flow(
    request_info: Dict[str, Any],
    rate_limit_config: Dict[str, Any] = None,
    current_usage: Dict[str, Any] = None,
    client_history: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform comprehensive rate limiting validation and usage tracking.
    
    Args:
        request_info: Request information for rate limiting
        rate_limit_config: Rate limiting configuration
        current_usage: Current usage statistics
        client_history: Historical client usage data
    
    Returns:
        ConversionResult with rate limiting validation results
    """
    logger.info("Starting rate limit validation")
    
    try:
        if rate_limit_config is None:
            rate_limit_config = {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "requests_per_day": 10000,
                "tokens_per_minute": 100000,
                "concurrent_requests": 10
            }
        
        if current_usage is None:
            current_usage = {
                "requests_last_minute": 0,
                "requests_last_hour": 0,
                "requests_last_day": 0,
                "tokens_last_minute": 0,
                "active_requests": 0
            }
        
        if client_history is None:
            client_history = {}
        
        validation_results = {
            "is_within_limits": True,
            "rate_limit_status": "allowed",
            "validation_summary": {
                "basic_rate_limit": None,
                "adaptive_limits": None,
                "client_analysis": None,
                "quota_analysis": None
            },
            "violations": [],
            "warnings": [],
            "rate_limit_info": {
                "client_id": request_info.get("client_id"),
                "user_id": request_info.get("user_id"),
                "current_usage": current_usage,
                "limits": rate_limit_config,
                "usage_percentages": {},
                "projected_usage": {}
            }
        }
        
        # Step 1: Basic rate limit validation
        rate_limit_result = await validate_request_rate_limit_task(
            request_info=request_info,
            rate_limit_config=rate_limit_config,
            current_usage=current_usage
        )
        
        validation_results["validation_summary"]["basic_rate_limit"] = rate_limit_result.converted_data
        
        if not rate_limit_result.success or not rate_limit_result.converted_data.get("is_valid", True):
            validation_results["is_within_limits"] = False
            validation_results["rate_limit_status"] = "rate_limited"
            
            if rate_limit_result.errors:
                validation_results["violations"].extend(rate_limit_result.errors)
            
            if rate_limit_result.converted_data:
                validation_results["violations"].extend(rate_limit_result.converted_data.get("errors", []))
                validation_results["warnings"].extend(rate_limit_result.converted_data.get("warnings", []))
                
                # Extract usage percentages
                rate_info = rate_limit_result.converted_data.get("rate_limit_info", {})
                validation_results["rate_limit_info"]["usage_percentages"] = rate_info.get("usage_percentages", {})
        
        # Step 2: Adaptive rate limiting
        adaptive_limits = await _calculate_adaptive_limits(
            client_history, rate_limit_config, request_info
        )
        validation_results["validation_summary"]["adaptive_limits"] = adaptive_limits
        
        if adaptive_limits.get("apply_stricter_limits", False):
            validation_results["rate_limit_status"] = "throttled"
            validation_results["warnings"].append("Adaptive rate limiting applied due to usage patterns")
            
            # Apply adaptive limits
            adapted_usage = await _check_adaptive_limits(current_usage, adaptive_limits["limits"])
            if not adapted_usage["within_limits"]:
                validation_results["is_within_limits"] = False
                validation_results["violations"].extend(adapted_usage["violations"])
        
        # Step 3: Client behavior analysis
        client_analysis = await _analyze_client_behavior(
            request_info, client_history, current_usage
        )
        validation_results["validation_summary"]["client_analysis"] = client_analysis
        
        if client_analysis.get("suspicious_behavior", False):
            validation_results["warnings"].append("Suspicious request patterns detected")
            validation_results["rate_limit_info"]["behavioral_flags"] = client_analysis.get("flags", [])
        
        if client_analysis.get("burst_detected", False):
            validation_results["warnings"].append("Burst activity detected")
            # Consider applying burst penalties
            if rate_limit_config.get("burst_penalty", False):
                validation_results["rate_limit_status"] = "burst_limited"
        
        # Step 4: Quota and billing analysis
        quota_analysis = await _analyze_quota_usage(
            request_info, current_usage, rate_limit_config
        )
        validation_results["validation_summary"]["quota_analysis"] = quota_analysis
        
        if quota_analysis.get("quota_exceeded", False):
            validation_results["is_within_limits"] = False
            validation_results["rate_limit_status"] = "quota_exceeded"
            validation_results["violations"].append("Usage quota exceeded")
        
        if quota_analysis.get("approaching_quota", False):
            validation_results["warnings"].append("Approaching usage quota limit")
        
        # Calculate projected usage
        projected_usage = await _calculate_projected_usage(current_usage, client_history)
        validation_results["rate_limit_info"]["projected_usage"] = projected_usage
        
        if projected_usage.get("will_exceed_limits", False):
            validation_results["warnings"].append("Current usage rate will exceed limits")
            validation_results["warnings"].extend(projected_usage.get("warnings", []))
        
        # Generate rate limiting recommendations
        recommendations = await _generate_rate_limit_recommendations(validation_results)
        validation_results["recommendations"] = recommendations
        
        logger.info("Rate limit validation completed",
                   is_within_limits=validation_results["is_within_limits"],
                   rate_limit_status=validation_results["rate_limit_status"],
                   client_id=request_info.get("client_id"),
                   violation_count=len(validation_results["violations"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "client_id": request_info.get("client_id"),
                "validation_type": "rate_limit",
                "is_within_limits": validation_results["is_within_limits"],
                "rate_limit_status": validation_results["rate_limit_status"]
            }
        )
        
    except Exception as e:
        error_msg = f"Rate limit validation failed: {str(e)}"
        logger.error("Rate limit validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


# Helper functions for request validation flows

async def _perform_http_security_assessment(
    request_data: Dict[str, Any],
    validation_results: Dict[str, Any],
    security_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Perform comprehensive HTTP security assessment."""
    assessment = {
        "is_secure": True,
        "security_violations": [],
        "security_warnings": [],
        "security_metrics": {}
    }
    
    try:
        # Check for common attack patterns in URL
        url = request_data.get("url", "")
        if any(pattern in url.lower() for pattern in ["../", "script", "eval", "exec"]):
            assessment["security_violations"].append("Suspicious URL patterns detected")
            assessment["is_secure"] = False
        
        # Check for suspicious headers
        headers = request_data.get("headers", {})
        suspicious_headers = ["x-forwarded-host", "x-forwarded-proto"]
        for header in suspicious_headers:
            if header in headers:
                assessment["security_warnings"].append(f"Potentially spoofed header: {header}")
        
        # Check for large request bodies
        body = request_data.get("body")
        if body:
            body_size = len(str(body))
            max_body_size = security_config.get("max_body_size", 1000000)  # 1MB
            if body_size > max_body_size:
                assessment["security_violations"].append(f"Request body too large: {body_size} bytes")
                assessment["is_secure"] = False
        
        # Check for HTTPS requirement
        if security_config.get("require_https", False):
            if not url.startswith("https://"):
                assessment["security_violations"].append("HTTPS required")
                assessment["is_secure"] = False
        
    except Exception:
        assessment["security_warnings"].append("Error performing security assessment")
    
    return assessment


async def _perform_threat_assessment(
    request_data: Dict[str, Any],
    validation_results: Dict[str, Any],
    threat_intelligence: Dict[str, Any]
) -> Dict[str, Any]:
    """Perform comprehensive threat assessment."""
    assessment = {
        "threat_detected": False,
        "threats": [],
        "indicators": [],
        "warnings": [],
        "risk_increase": 0.0
    }
    
    try:
        # Check against known threat IPs
        client_ip = request_data.get("client_ip")
        if client_ip and client_ip in threat_intelligence.get("malicious_ips", []):
            assessment["threat_detected"] = True
            assessment["threats"].append(f"Request from known malicious IP: {client_ip}")
            assessment["indicators"].append("malicious_ip")
            assessment["risk_increase"] += 0.5
        
        # Check for bot patterns
        user_agent = request_data.get("headers", {}).get("user-agent", "")
        bot_patterns = ["bot", "crawler", "spider", "scraper"]
        if any(pattern in user_agent.lower() for pattern in bot_patterns):
            assessment["indicators"].append("bot_traffic")
            assessment["warnings"].append("Bot traffic detected")
            assessment["risk_increase"] += 0.1
        
        # Check for rapid request patterns
        if validation_results.get("validation_summary", {}).get("origin_validation", {}).get("is_suspicious", False):
            assessment["indicators"].append("suspicious_origin")
            assessment["risk_increase"] += 0.2
        
        # Check for authentication anomalies
        auth_result = validation_results.get("validation_summary", {}).get("authentication_validation")
        if auth_result and len(auth_result.get("warnings", [])) > 2:
            assessment["indicators"].append("auth_anomaly")
            assessment["warnings"].append("Multiple authentication warnings")
            assessment["risk_increase"] += 0.1
        
    except Exception:
        assessment["warnings"].append("Error performing threat assessment")
    
    return assessment


async def _estimate_request_tokens(request_data: Dict[str, Any]) -> int:
    """Estimate token usage for a request."""
    token_estimate = 0
    
    try:
        # Rough estimation: ~4 characters per token
        char_to_token_ratio = 4
        
        # Count characters in messages
        messages = request_data.get("messages", [])
        for message in messages:
            content = message.get("content", "")
            if isinstance(content, str):
                token_estimate += len(content) // char_to_token_ratio
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        text = block.get("text", "")
                        token_estimate += len(text) // char_to_token_ratio
        
        # Count system message
        system = request_data.get("system", "")
        if system:
            token_estimate += len(system) // char_to_token_ratio
        
        # Add overhead for tools
        tools = request_data.get("tools", [])
        if tools:
            token_estimate += len(tools) * 50  # Rough estimate per tool
        
        # Add response token estimate
        max_tokens = request_data.get("max_tokens", 1000)
        token_estimate += max_tokens
        
    except Exception:
        token_estimate = 1000  # Default estimate
    
    return token_estimate


async def _calculate_adaptive_limits(
    client_history: Dict[str, Any],
    base_limits: Dict[str, Any],
    request_info: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate adaptive rate limits based on client behavior."""
    adaptive_result = {
        "apply_stricter_limits": False,
        "limits": base_limits.copy(),
        "adjustments": []
    }
    
    try:
        # Check for abuse patterns
        if client_history.get("violations_count", 0) > 5:
            adaptive_result["apply_stricter_limits"] = True
            # Reduce limits by 50%
            for key, value in adaptive_result["limits"].items():
                adaptive_result["limits"][key] = value // 2
            adaptive_result["adjustments"].append("Reduced limits due to violation history")
        
        # Check for new client (be more lenient)
        if client_history.get("first_request", True):
            # Increase limits by 20%
            for key, value in adaptive_result["limits"].items():
                adaptive_result["limits"][key] = int(value * 1.2)
            adaptive_result["adjustments"].append("Increased limits for new client")
        
    except Exception:
        pass
    
    return adaptive_result


async def _check_adaptive_limits(
    current_usage: Dict[str, Any],
    adaptive_limits: Dict[str, Any]
) -> Dict[str, Any]:
    """Check current usage against adaptive limits."""
    result = {
        "within_limits": True,
        "violations": []
    }
    
    try:
        # Check each limit
        for metric, limit in adaptive_limits.items():
            current_value = current_usage.get(metric.replace("_per_", "_last_"), 0)
            if current_value >= limit:
                result["within_limits"] = False
                result["violations"].append(f"Adaptive limit exceeded: {metric}")
    
    except Exception:
        result["violations"].append("Error checking adaptive limits")
        result["within_limits"] = False
    
    return result


async def _analyze_client_behavior(
    request_info: Dict[str, Any],
    client_history: Dict[str, Any],
    current_usage: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze client behavior patterns."""
    analysis = {
        "suspicious_behavior": False,
        "burst_detected": False,
        "flags": []
    }
    
    try:
        # Check for burst activity
        requests_per_minute = current_usage.get("requests_last_minute", 0)
        if requests_per_minute > 30:  # More than 30 requests per minute
            analysis["burst_detected"] = True
            analysis["flags"].append("high_frequency_requests")
        
        # Check for unusual patterns
        if client_history.get("avg_requests_per_minute", 0) > 0:
            current_rate = requests_per_minute
            avg_rate = client_history["avg_requests_per_minute"]
            if current_rate > avg_rate * 3:  # 3x normal rate
                analysis["suspicious_behavior"] = True
                analysis["flags"].append("unusual_activity_spike")
        
    except Exception:
        analysis["flags"].append("analysis_error")
    
    return analysis


async def _analyze_quota_usage(
    request_info: Dict[str, Any],
    current_usage: Dict[str, Any],
    rate_limit_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze quota and billing usage."""
    analysis = {
        "quota_exceeded": False,
        "approaching_quota": False,
        "quota_percentage": 0.0
    }
    
    try:
        # Check daily quota
        daily_requests = current_usage.get("requests_last_day", 0)
        daily_limit = rate_limit_config.get("requests_per_day", 10000)
        
        quota_percentage = (daily_requests / daily_limit) * 100
        analysis["quota_percentage"] = quota_percentage
        
        if quota_percentage >= 100:
            analysis["quota_exceeded"] = True
        elif quota_percentage >= 80:
            analysis["approaching_quota"] = True
        
    except Exception:
        pass
    
    return analysis


async def _calculate_projected_usage(
    current_usage: Dict[str, Any],
    client_history: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate projected usage based on current trends."""
    projection = {
        "will_exceed_limits": False,
        "warnings": [],
        "projected_daily_requests": 0
    }
    
    try:
        # Simple projection based on current hourly rate
        requests_last_hour = current_usage.get("requests_last_hour", 0)
        projected_daily = requests_last_hour * 24
        projection["projected_daily_requests"] = projected_daily
        
        # Check if projection exceeds typical daily limits
        if projected_daily > 10000:  # Default daily limit
            projection["will_exceed_limits"] = True
            projection["warnings"].append(f"Projected daily usage: {projected_daily} requests")
        
    except Exception:
        projection["warnings"].append("Unable to calculate usage projection")
    
    return projection


async def _generate_http_validation_recommendations(validation_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations for HTTP validation results."""
    recommendations = []
    
    try:
        if not validation_results.get("is_valid_request", True):
            recommendations.append("Review request format and headers")
        
        if len(validation_results.get("warnings", [])) > 3:
            recommendations.append("Multiple warnings detected - review request configuration")
        
        auth_validation = validation_results.get("validation_summary", {}).get("authentication_validation")
        if auth_validation and not auth_validation.get("is_authenticated", False):
            recommendations.append("Ensure proper authentication credentials are provided")
        
    except Exception:
        recommendations.append("Unable to generate specific recommendations")
    
    return recommendations


async def _generate_anthropic_validation_recommendations(validation_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations for Anthropic validation results."""
    recommendations = []
    
    try:
        request_analysis = validation_results.get("request_analysis", {})
        
        if request_analysis.get("estimated_tokens", 0) > 50000:
            recommendations.append("Consider reducing message length or using streaming")
        
        if not request_analysis.get("has_system", False):
            recommendations.append("Consider adding a system message for better results")
        
        if request_analysis.get("message_count", 0) > 20:
            recommendations.append("Long conversation detected - consider conversation summarization")
        
    except Exception:
        recommendations.append("Unable to generate specific recommendations")
    
    return recommendations


async def _generate_security_recommendations(validation_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations for security validation results."""
    recommendations = []
    
    try:
        if not validation_results.get("is_secure", True):
            recommendations.append("Security review required - violations detected")
        
        if validation_results.get("security_score", 1.0) < 0.8:
            recommendations.append("Low security score - enhance security measures")
        
        if validation_results.get("threat_indicators"):
            recommendations.append("Threat indicators detected - monitor request patterns")
        
    except Exception:
        recommendations.append("Unable to generate security recommendations")
    
    return recommendations


async def _generate_rate_limit_recommendations(validation_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations for rate limiting results."""
    recommendations = []
    
    try:
        if not validation_results.get("is_within_limits", True):
            recommendations.append("Rate limits exceeded - reduce request frequency")
        
        status = validation_results.get("rate_limit_status", "allowed")
        if status == "throttled":
            recommendations.append("Request throttling applied - optimize usage patterns")
        elif status == "quota_exceeded":
            recommendations.append("Usage quota exceeded - upgrade plan or wait for reset")
        
    except Exception:
        recommendations.append("Unable to generate rate limiting recommendations")
    
    return recommendations