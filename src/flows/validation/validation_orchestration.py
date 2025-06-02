"""Validation Orchestration Flows for OpenRouter Anthropic Server.

Top-level Prefect flows that orchestrate comprehensive validation pipelines
by coordinating message, request, and system validation flows.

Part of Phase 6C comprehensive refactoring - Validation Orchestration.
"""

import asyncio
from typing import Any, Dict, List, Optional

from prefect import flow
from prefect.task_runners import ConcurrentTaskRunner

from ...core.logging_config import get_logger
from ...models.instructor import ConversionResult
from .message_validation_flows import (
    comprehensive_message_validation_flow,
    conversation_validation_flow,
    content_safety_validation_flow
)
from .request_validation_flows import (
    http_request_validation_flow,
    anthropic_request_validation_flow,
    api_security_validation_flow,
    rate_limit_validation_flow
)
from .system_validation_flows import (
    tool_system_validation_flow,
    flow_system_validation_flow,
    security_validation_flow,
    compliance_validation_flow
)

# Initialize logging
logger = get_logger("validation_orchestration")


@flow(
    name="complete_request_validation",
    description="Complete end-to-end request validation pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "orchestration", "complete"]
)
async def complete_request_validation_flow(
    request_data: Dict[str, Any],
    validation_config: Dict[str, Any] = None,
    system_context: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform complete end-to-end request validation including HTTP, API, security, and content validation.
    
    Args:
        request_data: Complete request data to validate
        validation_config: Comprehensive validation configuration
        system_context: System context for validation
    
    Returns:
        ConversionResult with complete validation results
    """
    logger.info("Starting complete request validation pipeline")
    
    try:
        if validation_config is None:
            validation_config = {}
        if system_context is None:
            system_context = {}
        
        validation_results = {
            "is_valid_request": True,
            "overall_validation_score": 1.0,
            "validation_pipeline": {
                "http_validation": None,
                "anthropic_validation": None,
                "security_validation": None,
                "content_validation": None,
                "rate_limit_validation": None
            },
            "errors": [],
            "warnings": [],
            "validation_metrics": {
                "http_score": 1.0,
                "api_score": 1.0,
                "security_score": 1.0,
                "content_score": 1.0,
                "rate_limit_score": 1.0,
                "processing_time": 0.0
            },
            "security_assessment": {
                "threat_level": "low",
                "risk_factors": [],
                "security_recommendations": []
            }
        }
        
        import time
        start_time = time.time()
        
        # Step 1: HTTP Request Validation
        logger.info("Executing HTTP request validation")
        http_result = await http_request_validation_flow(
            request_data=request_data,
            validation_config=validation_config.get("http_config", {}),
            security_config=validation_config.get("security_config", {})
        )
        
        validation_results["validation_pipeline"]["http_validation"] = http_result.converted_data
        
        if not http_result.success or not http_result.converted_data.get("is_valid_request", True):
            validation_results["is_valid_request"] = False
            if http_result.errors:
                validation_results["errors"].extend([f"HTTP: {error}" for error in http_result.errors])
            
            if http_result.converted_data:
                validation_results["errors"].extend([f"HTTP: {error}" for error in http_result.converted_data.get("errors", [])])
                validation_results["warnings"].extend([f"HTTP: {warning}" for warning in http_result.converted_data.get("warnings", [])])
                validation_results["validation_metrics"]["http_score"] = 0.0
        
        # Step 2: Anthropic API Validation (if applicable)
        if request_data.get("body") and isinstance(request_data["body"], dict):
            logger.info("Executing Anthropic API validation")
            anthropic_result = await anthropic_request_validation_flow(
                request_data=request_data["body"],
                validation_config=validation_config.get("anthropic_config", {}),
                tool_definitions=system_context.get("tool_definitions", [])
            )
            
            validation_results["validation_pipeline"]["anthropic_validation"] = anthropic_result.converted_data
            
            if not anthropic_result.success or not anthropic_result.converted_data.get("is_valid_anthropic_request", True):
                validation_results["is_valid_request"] = False
                if anthropic_result.errors:
                    validation_results["errors"].extend([f"Anthropic: {error}" for error in anthropic_result.errors])
                
                if anthropic_result.converted_data:
                    validation_results["errors"].extend([f"Anthropic: {error}" for error in anthropic_result.converted_data.get("errors", [])])
                    validation_results["warnings"].extend([f"Anthropic: {warning}" for warning in anthropic_result.converted_data.get("warnings", [])])
                    validation_results["validation_metrics"]["api_score"] = 0.0
        
        # Step 3: Security Validation
        logger.info("Executing security validation")
        security_result = await api_security_validation_flow(
            request_data=request_data,
            security_config=validation_config.get("security_config", {}),
            threat_intelligence=system_context.get("threat_intelligence", {})
        )
        
        validation_results["validation_pipeline"]["security_validation"] = security_result.converted_data
        
        if not security_result.success or not security_result.converted_data.get("is_secure", True):
            validation_results["is_valid_request"] = False
            if security_result.errors:
                validation_results["errors"].extend([f"Security: {error}" for error in security_result.errors])
            
            if security_result.converted_data:
                security_data = security_result.converted_data
                validation_results["errors"].extend([f"Security: {violation}" for violation in security_data.get("security_violations", [])])
                validation_results["warnings"].extend([f"Security: {warning}" for warning in security_data.get("security_warnings", [])])
                validation_results["validation_metrics"]["security_score"] = security_data.get("security_score", 0.0)
                
                # Extract security assessment
                validation_results["security_assessment"]["threat_level"] = "high" if not security_data.get("is_secure", True) else "low"
                validation_results["security_assessment"]["risk_factors"] = security_data.get("threat_indicators", [])
                validation_results["security_assessment"]["security_recommendations"] = security_data.get("recommendations", [])
        
        # Step 4: Content Safety Validation
        content_items = []
        if request_data.get("body") and isinstance(request_data["body"], dict):
            messages = request_data["body"].get("messages", [])
            for message in messages:
                content = message.get("content")
                if isinstance(content, str):
                    content_items.append(content)
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            content_items.append(block.get("text", ""))
            
            # Add system message
            if request_data["body"].get("system"):
                content_items.append(request_data["body"]["system"])
        
        if content_items:
            logger.info("Executing content safety validation")
            content_result = await content_safety_validation_flow(
                content_items=content_items,
                safety_config=validation_config.get("safety_config", {}),
                sanitization_config=validation_config.get("sanitization_config", {})
            )
            
            validation_results["validation_pipeline"]["content_validation"] = content_result.converted_data
            
            if not content_result.success or not content_result.converted_data.get("overall_safe", True):
                validation_results["is_valid_request"] = False
                if content_result.errors:
                    validation_results["errors"].extend([f"Content: {error}" for error in content_result.errors])
                
                if content_result.converted_data:
                    content_data = content_result.converted_data
                    validation_results["errors"].extend([f"Content: {error}" for error in content_data.get("errors", [])])
                    validation_results["warnings"].extend([f"Content: {warning}" for warning in content_data.get("warnings", [])])
                    
                    # Calculate content score
                    safe_content = content_data.get("safety_summary", {}).get("safe_content", 0)
                    total_content = safe_content + content_data.get("safety_summary", {}).get("unsafe_content", 0)
                    validation_results["validation_metrics"]["content_score"] = safe_content / max(1, total_content)
        
        # Step 5: Rate Limiting Validation
        if system_context.get("enable_rate_limiting", True):
            logger.info("Executing rate limit validation")
            request_info = {
                "client_id": request_data.get("client_id") or request_data.get("headers", {}).get("x-client-id"),
                "user_id": request_data.get("user_id") or request_data.get("headers", {}).get("x-user-id"),
                "estimated_tokens": system_context.get("estimated_tokens", 1000)
            }
            
            rate_limit_result = await rate_limit_validation_flow(
                request_info=request_info,
                rate_limit_config=validation_config.get("rate_limit_config", {}),
                current_usage=system_context.get("current_usage", {}),
                client_history=system_context.get("client_history", {})
            )
            
            validation_results["validation_pipeline"]["rate_limit_validation"] = rate_limit_result.converted_data
            
            if not rate_limit_result.success or not rate_limit_result.converted_data.get("is_within_limits", True):
                validation_results["is_valid_request"] = False
                if rate_limit_result.errors:
                    validation_results["errors"].extend([f"Rate Limit: {error}" for error in rate_limit_result.errors])
                
                if rate_limit_result.converted_data:
                    rate_data = rate_limit_result.converted_data
                    validation_results["errors"].extend([f"Rate Limit: {violation}" for violation in rate_data.get("violations", [])])
                    validation_results["warnings"].extend([f"Rate Limit: {warning}" for warning in rate_data.get("warnings", [])])
                    validation_results["validation_metrics"]["rate_limit_score"] = 0.0 if not rate_data.get("is_within_limits", True) else 1.0
        
        # Calculate overall validation score
        scores = [
            validation_results["validation_metrics"]["http_score"],
            validation_results["validation_metrics"]["api_score"],
            validation_results["validation_metrics"]["security_score"],
            validation_results["validation_metrics"]["content_score"],
            validation_results["validation_metrics"]["rate_limit_score"]
        ]
        
        validation_results["overall_validation_score"] = sum(scores) / len(scores)
        validation_results["validation_metrics"]["processing_time"] = time.time() - start_time
        
        # Generate comprehensive recommendations
        recommendations = await _generate_complete_validation_recommendations(validation_results)
        validation_results["recommendations"] = recommendations
        
        logger.info("Complete request validation pipeline completed",
                   is_valid=validation_results["is_valid_request"],
                   overall_score=validation_results["overall_validation_score"],
                   processing_time=validation_results["validation_metrics"]["processing_time"],
                   error_count=len(validation_results["errors"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "validation_type": "complete_request",
                "overall_score": validation_results["overall_validation_score"],
                "is_valid": validation_results["is_valid_request"],
                "processing_time": validation_results["validation_metrics"]["processing_time"]
            }
        )
        
    except Exception as e:
        error_msg = f"Complete request validation failed: {str(e)}"
        logger.error("Complete request validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(
    name="security_assessment",
    description="Comprehensive security assessment pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "security", "assessment"]
)
async def security_assessment_flow(
    security_context: Dict[str, Any],
    request_samples: List[Dict[str, Any]] = None,
    content_samples: List[str] = None,
    system_data: Dict[str, Any] = None,
    assessment_config: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform comprehensive security assessment across all system components.
    
    Args:
        security_context: Security context and configuration
        request_samples: Sample requests for security analysis
        content_samples: Sample content for safety analysis
        system_data: System data for security evaluation
        assessment_config: Security assessment configuration
    
    Returns:
        ConversionResult with comprehensive security assessment results
    """
    logger.info("Starting comprehensive security assessment")
    
    try:
        if assessment_config is None:
            assessment_config = {}
        if request_samples is None:
            request_samples = []
        if content_samples is None:
            content_samples = []
        if system_data is None:
            system_data = {}
        
        assessment_results = {
            "is_secure_environment": True,
            "overall_security_score": 1.0,
            "security_assessment": {
                "api_security": None,
                "system_security": None,
                "content_security": None,
                "compliance_security": None
            },
            "security_violations": [],
            "security_warnings": [],
            "threat_analysis": {
                "threat_level": "low",
                "risk_factors": [],
                "vulnerability_count": 0,
                "mitigation_recommendations": []
            },
            "security_metrics": {
                "api_security_score": 1.0,
                "system_security_score": 1.0,
                "content_security_score": 1.0,
                "compliance_score": 1.0,
                "vulnerability_density": 0.0
            }
        }
        
        # Step 1: API Security Assessment
        if request_samples:
            logger.info("Executing API security assessment")
            api_security_result = await api_security_validation_flow(
                request_data=request_samples[0] if request_samples else {},
                security_config=assessment_config.get("api_security_config", {}),
                threat_intelligence=system_data.get("threat_intelligence", {})
            )
            
            assessment_results["security_assessment"]["api_security"] = api_security_result.converted_data
            
            if not api_security_result.success or not api_security_result.converted_data.get("is_secure", True):
                assessment_results["is_secure_environment"] = False
                if api_security_result.errors:
                    assessment_results["security_violations"].extend(api_security_result.errors)
                
                if api_security_result.converted_data:
                    api_data = api_security_result.converted_data
                    assessment_results["security_violations"].extend(api_data.get("security_violations", []))
                    assessment_results["security_warnings"].extend(api_data.get("security_warnings", []))
                    assessment_results["security_metrics"]["api_security_score"] = api_data.get("security_score", 0.0)
                    assessment_results["threat_analysis"]["risk_factors"].extend(api_data.get("threat_indicators", []))
        
        # Step 2: System Security Assessment
        logger.info("Executing system security assessment")
        system_security_result = await security_validation_flow(
            security_context=security_context,
            content_samples=content_samples,
            request_samples=request_samples,
            validation_config=assessment_config.get("system_security_config", {})
        )
        
        assessment_results["security_assessment"]["system_security"] = system_security_result.converted_data
        
        if not system_security_result.success or not system_security_result.converted_data.get("is_secure_system", True):
            assessment_results["is_secure_environment"] = False
            if system_security_result.errors:
                assessment_results["security_violations"].extend(system_security_result.errors)
            
            if system_security_result.converted_data:
                system_data_result = system_security_result.converted_data
                assessment_results["security_violations"].extend(system_data_result.get("security_violations", []))
                assessment_results["security_warnings"].extend(system_data_result.get("security_warnings", []))
                assessment_results["security_metrics"]["system_security_score"] = system_data_result.get("security_score", 0.0)
        
        # Step 3: Content Security Assessment
        if content_samples:
            logger.info("Executing content security assessment")
            content_security_result = await content_safety_validation_flow(
                content_items=content_samples,
                safety_config=assessment_config.get("content_security_config", {}),
                sanitization_config=assessment_config.get("sanitization_config", {})
            )
            
            assessment_results["security_assessment"]["content_security"] = content_security_result.converted_data
            
            if not content_security_result.success or not content_security_result.converted_data.get("overall_safe", True):
                assessment_results["is_secure_environment"] = False
                if content_security_result.errors:
                    assessment_results["security_violations"].extend(content_security_result.errors)
                
                if content_security_result.converted_data:
                    content_data = content_security_result.converted_data
                    assessment_results["security_violations"].extend(content_data.get("errors", []))
                    assessment_results["security_warnings"].extend(content_data.get("warnings", []))
                    
                    # Calculate content security score
                    safe_content = content_data.get("safety_summary", {}).get("safe_content", 0)
                    total_content = safe_content + content_data.get("safety_summary", {}).get("unsafe_content", 0)
                    assessment_results["security_metrics"]["content_security_score"] = safe_content / max(1, total_content)
        
        # Step 4: Compliance Security Assessment
        logger.info("Executing compliance security assessment")
        compliance_result = await compliance_validation_flow(
            compliance_context=security_context,
            audit_data=system_data.get("audit_data", {}),
            policy_rules=assessment_config.get("policy_rules", {}),
            validation_config=assessment_config.get("compliance_config", {})
        )
        
        assessment_results["security_assessment"]["compliance_security"] = compliance_result.converted_data
        
        if not compliance_result.success or not compliance_result.converted_data.get("is_compliant", True):
            assessment_results["is_secure_environment"] = False
            if compliance_result.errors:
                assessment_results["security_violations"].extend(compliance_result.errors)
            
            if compliance_result.converted_data:
                compliance_data = compliance_result.converted_data
                assessment_results["security_violations"].extend(compliance_data.get("compliance_violations", []))
                assessment_results["security_warnings"].extend(compliance_data.get("compliance_warnings", []))
                assessment_results["security_metrics"]["compliance_score"] = compliance_data.get("compliance_score", 0.0)
        
        # Calculate overall security score
        scores = [
            assessment_results["security_metrics"]["api_security_score"],
            assessment_results["security_metrics"]["system_security_score"],
            assessment_results["security_metrics"]["content_security_score"],
            assessment_results["security_metrics"]["compliance_score"]
        ]
        
        assessment_results["overall_security_score"] = sum(scores) / len(scores)
        
        # Threat analysis
        vulnerability_count = len(assessment_results["security_violations"])
        assessment_results["threat_analysis"]["vulnerability_count"] = vulnerability_count
        
        total_components = len(scores)
        assessment_results["security_metrics"]["vulnerability_density"] = vulnerability_count / max(1, total_components)
        
        # Determine threat level
        if assessment_results["overall_security_score"] >= 0.9 and vulnerability_count == 0:
            assessment_results["threat_analysis"]["threat_level"] = "low"
        elif assessment_results["overall_security_score"] >= 0.7 and vulnerability_count <= 2:
            assessment_results["threat_analysis"]["threat_level"] = "medium"
        elif assessment_results["overall_security_score"] >= 0.5 and vulnerability_count <= 5:
            assessment_results["threat_analysis"]["threat_level"] = "high"
        else:
            assessment_results["threat_analysis"]["threat_level"] = "critical"
        
        # Generate mitigation recommendations
        mitigation_recommendations = await _generate_security_mitigation_recommendations(assessment_results)
        assessment_results["threat_analysis"]["mitigation_recommendations"] = mitigation_recommendations
        
        logger.info("Security assessment completed",
                   is_secure=assessment_results["is_secure_environment"],
                   security_score=assessment_results["overall_security_score"],
                   threat_level=assessment_results["threat_analysis"]["threat_level"],
                   vulnerability_count=vulnerability_count)
        
        return ConversionResult(
            success=True,
            converted_data=assessment_results,
            metadata={
                "validation_type": "security_assessment",
                "security_score": assessment_results["overall_security_score"],
                "threat_level": assessment_results["threat_analysis"]["threat_level"],
                "vulnerability_count": vulnerability_count
            }
        )
        
    except Exception as e:
        error_msg = f"Security assessment failed: {str(e)}"
        logger.error("Security assessment failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(
    name="system_health_validation",
    description="Comprehensive system health validation pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "health", "system"]
)
async def system_health_validation_flow(
    system_context: Dict[str, Any],
    health_config: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform comprehensive system health validation across all components.
    
    Args:
        system_context: Complete system context and data
        health_config: System health validation configuration
    
    Returns:
        ConversionResult with comprehensive system health results
    """
    logger.info("Starting system health validation")
    
    try:
        if health_config is None:
            health_config = {}
        
        health_results = {
            "is_healthy_system": True,
            "overall_health_score": 1.0,
            "health_assessment": {
                "tool_system_health": None,
                "flow_system_health": None,
                "security_health": None,
                "performance_health": None
            },
            "health_issues": [],
            "health_warnings": [],
            "system_metrics": {
                "tool_health_score": 1.0,
                "flow_health_score": 1.0,
                "security_health_score": 1.0,
                "performance_score": 1.0,
                "availability": 1.0,
                "reliability": 1.0
            },
            "recommendations": []
        }
        
        # Step 1: Tool System Health
        tool_registry = system_context.get("tool_registry", {})
        tool_definitions = system_context.get("tool_definitions", [])
        execution_history = system_context.get("execution_history", [])
        
        if tool_registry:
            logger.info("Executing tool system health validation")
            tool_health_result = await tool_system_validation_flow(
                tool_registry=tool_registry,
                tool_definitions=tool_definitions,
                execution_history=execution_history,
                validation_config=health_config.get("tool_config", {})
            )
            
            health_results["health_assessment"]["tool_system_health"] = tool_health_result.converted_data
            
            if not tool_health_result.success or not tool_health_result.converted_data.get("is_valid_system", True):
                health_results["is_healthy_system"] = False
                if tool_health_result.errors:
                    health_results["health_issues"].extend([f"Tool System: {error}" for error in tool_health_result.errors])
                
                if tool_health_result.converted_data:
                    tool_data = tool_health_result.converted_data
                    health_results["health_issues"].extend([f"Tool System: {error}" for error in tool_data.get("errors", [])])
                    health_results["health_warnings"].extend([f"Tool System: {warning}" for warning in tool_data.get("warnings", [])])
                    health_results["system_metrics"]["tool_health_score"] = tool_data.get("system_health_score", 0.0)
        
        # Step 2: Flow System Health
        flow_definitions = system_context.get("flow_definitions", [])
        flow_executions = system_context.get("flow_executions", [])
        flow_dependencies = system_context.get("flow_dependencies", {})
        
        if flow_definitions:
            logger.info("Executing flow system health validation")
            flow_health_result = await flow_system_validation_flow(
                flow_definitions=flow_definitions,
                flow_executions=flow_executions,
                flow_dependencies=flow_dependencies,
                validation_config=health_config.get("flow_config", {})
            )
            
            health_results["health_assessment"]["flow_system_health"] = flow_health_result.converted_data
            
            if not flow_health_result.success or not flow_health_result.converted_data.get("is_valid_flow_system", True):
                health_results["is_healthy_system"] = False
                if flow_health_result.errors:
                    health_results["health_issues"].extend([f"Flow System: {error}" for error in flow_health_result.errors])
                
                if flow_health_result.converted_data:
                    flow_data = flow_health_result.converted_data
                    health_results["health_issues"].extend([f"Flow System: {error}" for error in flow_data.get("errors", [])])
                    health_results["health_warnings"].extend([f"Flow System: {warning}" for warning in flow_data.get("warnings", [])])
                    health_results["system_metrics"]["flow_health_score"] = flow_data.get("flow_health_score", 0.0)
        
        # Step 3: Security Health
        security_context = system_context.get("security_context", {})
        content_samples = system_context.get("content_samples", [])
        request_samples = system_context.get("request_samples", [])
        
        logger.info("Executing security health validation")
        security_health_result = await security_validation_flow(
            security_context=security_context,
            content_samples=content_samples,
            request_samples=request_samples,
            validation_config=health_config.get("security_config", {})
        )
        
        health_results["health_assessment"]["security_health"] = security_health_result.converted_data
        
        if not security_health_result.success or not security_health_result.converted_data.get("is_secure_system", True):
            health_results["is_healthy_system"] = False
            if security_health_result.errors:
                health_results["health_issues"].extend([f"Security: {error}" for error in security_health_result.errors])
            
            if security_health_result.converted_data:
                security_data = security_health_result.converted_data
                health_results["health_issues"].extend([f"Security: {violation}" for violation in security_data.get("security_violations", [])])
                health_results["health_warnings"].extend([f"Security: {warning}" for warning in security_data.get("security_warnings", [])])
                health_results["system_metrics"]["security_health_score"] = security_data.get("security_score", 0.0)
        
        # Step 4: Performance Health Assessment
        performance_metrics = system_context.get("performance_metrics", {})
        performance_health = await _assess_performance_health(performance_metrics, health_config.get("performance_config", {}))
        
        health_results["health_assessment"]["performance_health"] = performance_health
        
        if not performance_health.get("is_healthy", True):
            health_results["is_healthy_system"] = False
            health_results["health_issues"].extend(performance_health.get("issues", []))
        
        health_results["health_warnings"].extend(performance_health.get("warnings", []))
        health_results["system_metrics"]["performance_score"] = performance_health.get("performance_score", 1.0)
        
        # Calculate system availability and reliability
        availability_metrics = system_context.get("availability_metrics", {})
        reliability_metrics = system_context.get("reliability_metrics", {})
        
        health_results["system_metrics"]["availability"] = availability_metrics.get("uptime_percentage", 1.0)
        health_results["system_metrics"]["reliability"] = reliability_metrics.get("success_rate", 1.0)
        
        # Calculate overall health score
        health_scores = [
            health_results["system_metrics"]["tool_health_score"],
            health_results["system_metrics"]["flow_health_score"],
            health_results["system_metrics"]["security_health_score"],
            health_results["system_metrics"]["performance_score"],
            health_results["system_metrics"]["availability"],
            health_results["system_metrics"]["reliability"]
        ]
        
        health_results["overall_health_score"] = sum(health_scores) / len(health_scores)
        
        # Apply health thresholds
        min_health_score = health_config.get("min_health_score", 0.8)
        if health_results["overall_health_score"] < min_health_score:
            health_results["is_healthy_system"] = False
            health_results["health_issues"].append(f"Overall health score {health_results['overall_health_score']:.2f} below threshold {min_health_score}")
        
        # Generate health recommendations
        recommendations = await _generate_system_health_recommendations(health_results)
        health_results["recommendations"] = recommendations
        
        logger.info("System health validation completed",
                   is_healthy=health_results["is_healthy_system"],
                   health_score=health_results["overall_health_score"],
                   issue_count=len(health_results["health_issues"]),
                   warning_count=len(health_results["health_warnings"]))
        
        return ConversionResult(
            success=True,
            converted_data=health_results,
            metadata={
                "validation_type": "system_health",
                "health_score": health_results["overall_health_score"],
                "is_healthy": health_results["is_healthy_system"]
            }
        )
        
    except Exception as e:
        error_msg = f"System health validation failed: {str(e)}"
        logger.error("System health validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(
    name="validation_pipeline",
    description="Master validation pipeline orchestrating all validation flows",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "pipeline", "master"]
)
async def validation_pipeline_flow(
    pipeline_context: Dict[str, Any],
    pipeline_config: Dict[str, Any] = None
) -> ConversionResult:
    """
    Execute the master validation pipeline that orchestrates all validation flows.
    
    Args:
        pipeline_context: Complete pipeline context with all required data
        pipeline_config: Master pipeline configuration
    
    Returns:
        ConversionResult with master validation pipeline results
    """
    logger.info("Starting master validation pipeline")
    
    try:
        if pipeline_config is None:
            pipeline_config = {}
        
        pipeline_results = {
            "pipeline_success": True,
            "master_validation_score": 1.0,
            "pipeline_execution": {
                "request_validation": None,
                "security_assessment": None,
                "system_health": None,
                "compliance_check": None
            },
            "pipeline_errors": [],
            "pipeline_warnings": [],
            "pipeline_metrics": {
                "total_execution_time": 0.0,
                "validation_coverage": 1.0,
                "success_rate": 1.0,
                "performance_score": 1.0
            },
            "executive_summary": {
                "overall_status": "healthy",
                "critical_issues": [],
                "recommendations": []
            }
        }
        
        import time
        pipeline_start_time = time.time()
        
        # Step 1: Complete Request Validation
        if pipeline_context.get("request_data"):
            logger.info("Executing complete request validation")
            request_validation_result = await complete_request_validation_flow(
                request_data=pipeline_context["request_data"],
                validation_config=pipeline_config.get("request_config", {}),
                system_context=pipeline_context.get("system_context", {})
            )
            
            pipeline_results["pipeline_execution"]["request_validation"] = request_validation_result.converted_data
            
            if not request_validation_result.success or not request_validation_result.converted_data.get("is_valid_request", True):
                pipeline_results["pipeline_success"] = False
                if request_validation_result.errors:
                    pipeline_results["pipeline_errors"].extend([f"Request Validation: {error}" for error in request_validation_result.errors])
                
                if request_validation_result.converted_data:
                    request_data = request_validation_result.converted_data
                    pipeline_results["pipeline_errors"].extend([f"Request: {error}" for error in request_data.get("errors", [])])
                    pipeline_results["pipeline_warnings"].extend([f"Request: {warning}" for warning in request_data.get("warnings", [])])
        
        # Step 2: Security Assessment
        logger.info("Executing security assessment")
        security_assessment_result = await security_assessment_flow(
            security_context=pipeline_context.get("security_context", {}),
            request_samples=pipeline_context.get("request_samples", []),
            content_samples=pipeline_context.get("content_samples", []),
            system_data=pipeline_context.get("system_data", {}),
            assessment_config=pipeline_config.get("security_config", {})
        )
        
        pipeline_results["pipeline_execution"]["security_assessment"] = security_assessment_result.converted_data
        
        if not security_assessment_result.success or not security_assessment_result.converted_data.get("is_secure_environment", True):
            pipeline_results["pipeline_success"] = False
            if security_assessment_result.errors:
                pipeline_results["pipeline_errors"].extend([f"Security Assessment: {error}" for error in security_assessment_result.errors])
            
            if security_assessment_result.converted_data:
                security_data = security_assessment_result.converted_data
                pipeline_results["pipeline_errors"].extend([f"Security: {violation}" for violation in security_data.get("security_violations", [])])
                pipeline_results["pipeline_warnings"].extend([f"Security: {warning}" for warning in security_data.get("security_warnings", [])])
                
                # Check for critical security issues
                threat_level = security_data.get("threat_analysis", {}).get("threat_level", "low")
                if threat_level in ["high", "critical"]:
                    pipeline_results["executive_summary"]["critical_issues"].append(f"Critical security threat level: {threat_level}")
        
        # Step 3: System Health Validation
        logger.info("Executing system health validation")
        system_health_result = await system_health_validation_flow(
            system_context=pipeline_context.get("system_context", {}),
            health_config=pipeline_config.get("health_config", {})
        )
        
        pipeline_results["pipeline_execution"]["system_health"] = system_health_result.converted_data
        
        if not system_health_result.success or not system_health_result.converted_data.get("is_healthy_system", True):
            pipeline_results["pipeline_success"] = False
            if system_health_result.errors:
                pipeline_results["pipeline_errors"].extend([f"System Health: {error}" for error in system_health_result.errors])
            
            if system_health_result.converted_data:
                health_data = system_health_result.converted_data
                pipeline_results["pipeline_errors"].extend([f"Health: {issue}" for issue in health_data.get("health_issues", [])])
                pipeline_results["pipeline_warnings"].extend([f"Health: {warning}" for warning in health_data.get("health_warnings", [])])
                
                # Check for critical health issues
                health_score = health_data.get("overall_health_score", 1.0)
                if health_score < 0.5:
                    pipeline_results["executive_summary"]["critical_issues"].append(f"Critical system health score: {health_score:.2f}")
        
        # Step 4: Compliance Check
        if pipeline_context.get("compliance_context"):
            logger.info("Executing compliance validation")
            compliance_result = await compliance_validation_flow(
                compliance_context=pipeline_context["compliance_context"],
                audit_data=pipeline_context.get("audit_data", {}),
                policy_rules=pipeline_context.get("policy_rules", {}),
                validation_config=pipeline_config.get("compliance_config", {})
            )
            
            pipeline_results["pipeline_execution"]["compliance_check"] = compliance_result.converted_data
            
            if not compliance_result.success or not compliance_result.converted_data.get("is_compliant", True):
                pipeline_results["pipeline_success"] = False
                if compliance_result.errors:
                    pipeline_results["pipeline_errors"].extend([f"Compliance: {error}" for error in compliance_result.errors])
                
                if compliance_result.converted_data:
                    compliance_data = compliance_result.converted_data
                    pipeline_results["pipeline_errors"].extend([f"Compliance: {violation}" for violation in compliance_data.get("compliance_violations", [])])
                    pipeline_results["pipeline_warnings"].extend([f"Compliance: {warning}" for warning in compliance_data.get("compliance_warnings", [])])
                    
                    # Check for critical compliance issues
                    compliance_level = compliance_data.get("compliance_metrics", {}).get("overall_compliance_level", "compliant")
                    if compliance_level == "non_compliant":
                        pipeline_results["executive_summary"]["critical_issues"].append(f"Non-compliant system: {compliance_level}")
        
        # Calculate pipeline metrics
        pipeline_results["pipeline_metrics"]["total_execution_time"] = time.time() - pipeline_start_time
        
        # Calculate success rate
        total_validations = sum(1 for v in pipeline_results["pipeline_execution"].values() if v is not None)
        successful_validations = sum(
            1 for v in pipeline_results["pipeline_execution"].values() 
            if v is not None and (
                v.get("is_valid_request", True) or 
                v.get("is_secure_environment", True) or 
                v.get("is_healthy_system", True) or 
                v.get("is_compliant", True)
            )
        )
        
        if total_validations > 0:
            pipeline_results["pipeline_metrics"]["success_rate"] = successful_validations / total_validations
        
        # Calculate master validation score
        validation_scores = []
        
        for validation_result in pipeline_results["pipeline_execution"].values():
            if validation_result:
                if "overall_validation_score" in validation_result:
                    validation_scores.append(validation_result["overall_validation_score"])
                elif "overall_security_score" in validation_result:
                    validation_scores.append(validation_result["overall_security_score"])
                elif "overall_health_score" in validation_result:
                    validation_scores.append(validation_result["overall_health_score"])
                elif "compliance_score" in validation_result:
                    validation_scores.append(validation_result["compliance_score"])
        
        if validation_scores:
            pipeline_results["master_validation_score"] = sum(validation_scores) / len(validation_scores)
        
        # Determine overall status
        if pipeline_results["pipeline_success"] and not pipeline_results["executive_summary"]["critical_issues"]:
            pipeline_results["executive_summary"]["overall_status"] = "healthy"
        elif pipeline_results["pipeline_success"] and pipeline_results["executive_summary"]["critical_issues"]:
            pipeline_results["executive_summary"]["overall_status"] = "warning"
        else:
            pipeline_results["executive_summary"]["overall_status"] = "critical"
        
        # Generate executive recommendations
        executive_recommendations = await _generate_executive_recommendations(pipeline_results)
        pipeline_results["executive_summary"]["recommendations"] = executive_recommendations
        
        logger.info("Master validation pipeline completed",
                   pipeline_success=pipeline_results["pipeline_success"],
                   master_score=pipeline_results["master_validation_score"],
                   overall_status=pipeline_results["executive_summary"]["overall_status"],
                   execution_time=pipeline_results["pipeline_metrics"]["total_execution_time"],
                   critical_issues=len(pipeline_results["executive_summary"]["critical_issues"]))
        
        return ConversionResult(
            success=True,
            converted_data=pipeline_results,
            metadata={
                "validation_type": "master_pipeline",
                "master_score": pipeline_results["master_validation_score"],
                "overall_status": pipeline_results["executive_summary"]["overall_status"],
                "execution_time": pipeline_results["pipeline_metrics"]["total_execution_time"]
            }
        )
        
    except Exception as e:
        error_msg = f"Master validation pipeline failed: {str(e)}"
        logger.error("Master validation pipeline failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


# Helper functions for validation orchestration flows

async def _generate_complete_validation_recommendations(validation_results: Dict[str, Any]) -> List[str]:
    """Generate comprehensive recommendations for complete validation results."""
    recommendations = []
    
    try:
        overall_score = validation_results.get("overall_validation_score", 1.0)
        metrics = validation_results.get("validation_metrics", {})
        
        if overall_score < 0.8:
            recommendations.append("Overall validation score is low - comprehensive review required")
        
        if metrics.get("http_score", 1.0) < 0.9:
            recommendations.append("HTTP validation issues detected - review request format and headers")
        
        if metrics.get("api_score", 1.0) < 0.9:
            recommendations.append("API validation issues detected - review Anthropic request structure")
        
        if metrics.get("security_score", 1.0) < 0.9:
            recommendations.append("Security validation issues detected - enhance security measures")
        
        if metrics.get("content_score", 1.0) < 0.9:
            recommendations.append("Content safety issues detected - review content filtering")
        
        if metrics.get("rate_limit_score", 1.0) < 1.0:
            recommendations.append("Rate limiting issues detected - review usage patterns")
        
        # Performance recommendations
        processing_time = metrics.get("processing_time", 0.0)
        if processing_time > 5.0:  # 5 seconds
            recommendations.append("Validation processing time is high - optimize validation pipeline")
        
    except Exception:
        recommendations.append("Unable to generate comprehensive validation recommendations")
    
    return recommendations


async def _generate_security_mitigation_recommendations(assessment_results: Dict[str, Any]) -> List[str]:
    """Generate security mitigation recommendations."""
    recommendations = []
    
    try:
        threat_level = assessment_results.get("threat_analysis", {}).get("threat_level", "low")
        security_score = assessment_results.get("overall_security_score", 1.0)
        vulnerability_count = assessment_results.get("threat_analysis", {}).get("vulnerability_count", 0)
        
        if threat_level == "critical":
            recommendations.append("CRITICAL: Immediate security review and remediation required")
            recommendations.append("Implement emergency security protocols")
            recommendations.append("Consider temporarily restricting system access")
        elif threat_level == "high":
            recommendations.append("HIGH: Urgent security remediation required within 24 hours")
            recommendations.append("Implement additional monitoring and alerting")
        elif threat_level == "medium":
            recommendations.append("MEDIUM: Security improvements recommended within 1 week")
            recommendations.append("Review and update security policies")
        
        if security_score < 0.7:
            recommendations.append("Low security score - comprehensive security audit recommended")
        
        if vulnerability_count > 5:
            recommendations.append(f"High vulnerability count ({vulnerability_count}) - systematic remediation plan needed")
        
        # Specific security recommendations
        metrics = assessment_results.get("security_metrics", {})
        
        if metrics.get("api_security_score", 1.0) < 0.8:
            recommendations.append("Strengthen API security controls and authentication")
        
        if metrics.get("content_security_score", 1.0) < 0.8:
            recommendations.append("Enhance content safety filters and monitoring")
        
        if metrics.get("compliance_score", 1.0) < 0.8:
            recommendations.append("Address compliance gaps and policy violations")
        
    except Exception:
        recommendations.append("Unable to generate security mitigation recommendations")
    
    return recommendations


async def _assess_performance_health(
    performance_metrics: Dict[str, Any],
    performance_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Assess system performance health."""
    assessment = {
        "is_healthy": True,
        "performance_score": 1.0,
        "issues": [],
        "warnings": []
    }
    
    try:
        # Check response time
        avg_response_time = performance_metrics.get("average_response_time", 0.0)
        max_response_time = performance_config.get("max_response_time", 5.0)
        
        if avg_response_time > max_response_time:
            assessment["is_healthy"] = False
            assessment["issues"].append(f"High average response time: {avg_response_time:.2f}s > {max_response_time}s")
        elif avg_response_time > max_response_time * 0.8:
            assessment["warnings"].append(f"Response time approaching limit: {avg_response_time:.2f}s")
        
        # Check throughput
        requests_per_second = performance_metrics.get("requests_per_second", 0.0)
        min_throughput = performance_config.get("min_throughput", 10.0)
        
        if requests_per_second < min_throughput:
            assessment["warnings"].append(f"Low throughput: {requests_per_second:.1f} req/s < {min_throughput} req/s")
        
        # Check error rate
        error_rate = performance_metrics.get("error_rate", 0.0)
        max_error_rate = performance_config.get("max_error_rate", 0.05)  # 5%
        
        if error_rate > max_error_rate:
            assessment["is_healthy"] = False
            assessment["issues"].append(f"High error rate: {error_rate:.2%} > {max_error_rate:.2%}")
        elif error_rate > max_error_rate * 0.8:
            assessment["warnings"].append(f"Error rate approaching limit: {error_rate:.2%}")
        
        # Check resource utilization
        cpu_usage = performance_metrics.get("cpu_usage", 0.0)
        memory_usage = performance_metrics.get("memory_usage", 0.0)
        
        if cpu_usage > 0.9:  # 90%
            assessment["warnings"].append(f"High CPU usage: {cpu_usage:.1%}")
        
        if memory_usage > 0.9:  # 90%
            assessment["warnings"].append(f"High memory usage: {memory_usage:.1%}")
        
        # Calculate performance score
        score_factors = []
        
        # Response time factor
        if avg_response_time <= max_response_time:
            response_factor = max(0.0, 1.0 - (avg_response_time / max_response_time))
            score_factors.append(response_factor)
        else:
            score_factors.append(0.0)
        
        # Error rate factor
        error_factor = max(0.0, 1.0 - (error_rate / max_error_rate))
        score_factors.append(error_factor)
        
        # Resource utilization factor
        resource_factor = max(0.0, 1.0 - max(cpu_usage, memory_usage))
        score_factors.append(resource_factor)
        
        assessment["performance_score"] = sum(score_factors) / len(score_factors)
        
    except Exception:
        assessment["warnings"].append("Error assessing performance health")
    
    return assessment


async def _generate_system_health_recommendations(health_results: Dict[str, Any]) -> List[str]:
    """Generate system health recommendations."""
    recommendations = []
    
    try:
        health_score = health_results.get("overall_health_score", 1.0)
        metrics = health_results.get("system_metrics", {})
        
        if health_score < 0.8:
            recommendations.append("System health is low - comprehensive system review required")
        
        if metrics.get("tool_health_score", 1.0) < 0.8:
            recommendations.append("Tool system health issues - review and fix tool implementations")
        
        if metrics.get("flow_health_score", 1.0) < 0.8:
            recommendations.append("Flow system health issues - optimize flow executions")
        
        if metrics.get("security_health_score", 1.0) < 0.8:
            recommendations.append("Security health issues - strengthen security measures")
        
        if metrics.get("performance_score", 1.0) < 0.8:
            recommendations.append("Performance health issues - optimize system performance")
        
        if metrics.get("availability", 1.0) < 0.99:
            recommendations.append("Availability concerns - improve system reliability")
        
        if metrics.get("reliability", 1.0) < 0.95:
            recommendations.append("Reliability issues - enhance error handling and recovery")
        
    except Exception:
        recommendations.append("Unable to generate system health recommendations")
    
    return recommendations


async def _generate_executive_recommendations(pipeline_results: Dict[str, Any]) -> List[str]:
    """Generate executive-level recommendations."""
    recommendations = []
    
    try:
        overall_status = pipeline_results.get("executive_summary", {}).get("overall_status", "healthy")
        master_score = pipeline_results.get("master_validation_score", 1.0)
        critical_issues = pipeline_results.get("executive_summary", {}).get("critical_issues", [])
        
        if overall_status == "critical":
            recommendations.append("EXECUTIVE ACTION REQUIRED: Critical system issues detected")
            recommendations.append("Immediate incident response and remediation plan activation")
            recommendations.append("Consider business continuity measures if necessary")
        elif overall_status == "warning":
            recommendations.append("Management attention required: System warnings detected")
            recommendations.append("Schedule comprehensive system review within 48 hours")
        
        if master_score < 0.8:
            recommendations.append("System validation score below acceptable threshold")
            recommendations.append("Implement systematic improvement plan with defined milestones")
        
        if len(critical_issues) > 0:
            recommendations.append(f"Address {len(critical_issues)} critical issue(s) immediately")
            recommendations.append("Establish monitoring and alerting for critical system components")
        
        # Performance recommendations
        execution_time = pipeline_results.get("pipeline_metrics", {}).get("total_execution_time", 0.0)
        if execution_time > 30.0:  # 30 seconds
            recommendations.append("Validation pipeline performance needs optimization")
            recommendations.append("Consider infrastructure scaling or process optimization")
        
        success_rate = pipeline_results.get("pipeline_metrics", {}).get("success_rate", 1.0)
        if success_rate < 0.9:
            recommendations.append("Low validation success rate indicates systemic issues")
            recommendations.append("Comprehensive system architecture review recommended")
        
    except Exception:
        recommendations.append("Unable to generate executive recommendations")
    
    return recommendations