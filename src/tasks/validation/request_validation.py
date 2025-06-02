"""Request Validation Tasks for OpenRouter Anthropic Server.

Prefect tasks for validating HTTP requests, API parameters, and request security.
Part of Phase 6B comprehensive refactoring - Validation Tasks.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from prefect import task
from pydantic import ValidationError

from ...core.logging_config import get_logger
from ...models.instructor import ConversionResult
from ...models.anthropic import MessagesRequest

# Initialize logging
logger = get_logger("request_validation")


@task(
    name="validate_http_request",
    description="Validate HTTP request structure and headers",
    tags=["validation", "http", "requests"]
)
async def validate_http_request_task(
    request_data: Dict[str, Any],
    validation_rules: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate HTTP request structure, headers, and basic security.
    
    Args:
        request_data: HTTP request data to validate
        validation_rules: Optional validation configuration
    
    Returns:
        ConversionResult with validation status and details
    """
    logger.info("Validating HTTP request")
    
    try:
        if validation_rules is None:
            validation_rules = {}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "request_info": {
                "method": request_data.get("method"),
                "url": request_data.get("url"),
                "headers_count": 0,
                "body_size": 0,
                "content_type": None,
                "has_auth": False,
                "user_agent": None
            }
        }
        
        # Validate HTTP method
        method = request_data.get("method", "").upper()
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        
        if not method:
            validation_result["errors"].append("Missing HTTP method")
            validation_result["is_valid"] = False
        elif method not in valid_methods:
            validation_result["errors"].append(f"Invalid HTTP method: {method}")
            validation_result["is_valid"] = False
        
        validation_result["request_info"]["method"] = method
        
        # Validate URL
        url = request_data.get("url")
        if url:
            url_validation = await _validate_url_structure(url)
            if not url_validation["is_valid"]:
                validation_result["errors"].extend(url_validation["errors"])
                validation_result["is_valid"] = False
            validation_result["warnings"].extend(url_validation["warnings"])
            validation_result["request_info"]["url"] = url
        else:
            validation_result["errors"].append("Missing URL")
            validation_result["is_valid"] = False
        
        # Validate headers
        headers = request_data.get("headers", {})
        if headers:
            header_validation = await _validate_request_headers(headers, validation_rules)
            if not header_validation["is_valid"]:
                validation_result["errors"].extend(header_validation["errors"])
                validation_result["is_valid"] = False
            
            validation_result["warnings"].extend(header_validation["warnings"])
            validation_result["request_info"]["headers_count"] = len(headers)
            validation_result["request_info"]["content_type"] = headers.get("content-type") or headers.get("Content-Type")
            validation_result["request_info"]["user_agent"] = headers.get("user-agent") or headers.get("User-Agent")
            
            # Check for authentication
            auth_headers = ["authorization", "Authorization", "x-api-key", "X-Api-Key"]
            validation_result["request_info"]["has_auth"] = any(header in headers for header in auth_headers)
        
        # Validate request body
        body = request_data.get("body")
        if body:
            body_validation = await _validate_request_body(body, validation_result["request_info"]["content_type"])
            if not body_validation["is_valid"]:
                validation_result["errors"].extend(body_validation["errors"])
                validation_result["is_valid"] = False
            
            validation_result["warnings"].extend(body_validation["warnings"])
            validation_result["request_info"]["body_size"] = body_validation["body_size"]
        
        # Apply custom validation rules
        if validation_rules.get("require_https", False):
            if url and not url.startswith("https://"):
                validation_result["errors"].append("HTTPS required")
                validation_result["is_valid"] = False
        
        if validation_rules.get("require_auth", False):
            if not validation_result["request_info"]["has_auth"]:
                validation_result["errors"].append("Authentication required")
                validation_result["is_valid"] = False
        
        if validation_rules.get("max_body_size", 0) > 0:
            max_size = validation_rules["max_body_size"]
            if validation_result["request_info"]["body_size"] > max_size:
                validation_result["errors"].append(f"Request body too large: {validation_result['request_info']['body_size']} > {max_size}")
                validation_result["is_valid"] = False
        
        logger.info("HTTP request validation completed",
                   method=method,
                   is_valid=validation_result["is_valid"],
                   error_count=len(validation_result["errors"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "method": method,
                "validation_type": "http_request"
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


@task(
    name="validate_api_parameters",
    description="Validate API request parameters and values",
    tags=["validation", "api", "parameters"]
)
async def validate_api_parameters_task(
    parameters: Dict[str, Any],
    parameter_schema: Dict[str, Any] = None,
    validation_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate API request parameters against schema and rules.
    
    Args:
        parameters: API parameters to validate
        parameter_schema: Optional parameter schema definition
        validation_options: Optional validation configuration
    
    Returns:
        ConversionResult with validation status and details
    """
    logger.info("Validating API parameters", parameter_count=len(parameters))
    
    try:
        if validation_options is None:
            validation_options = {}
        if parameter_schema is None:
            parameter_schema = {}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "parameter_info": {
                "total_parameters": len(parameters),
                "valid_parameters": 0,
                "invalid_parameters": 0,
                "missing_required": [],
                "unexpected_parameters": [],
                "parameter_types": {}
            }
        }
        
        # Get schema information
        schema_properties = parameter_schema.get("properties", {})
        required_parameters = parameter_schema.get("required", [])
        
        # Check for required parameters
        for required_param in required_parameters:
            if required_param not in parameters:
                validation_result["parameter_info"]["missing_required"].append(required_param)
                validation_result["errors"].append(f"Missing required parameter: {required_param}")
                validation_result["is_valid"] = False
        
        # Validate each parameter
        for param_name, param_value in parameters.items():
            param_validation = await _validate_single_parameter(
                param_name, param_value, schema_properties.get(param_name), validation_options
            )
            
            if param_validation["is_valid"]:
                validation_result["parameter_info"]["valid_parameters"] += 1
            else:
                validation_result["parameter_info"]["invalid_parameters"] += 1
                validation_result["errors"].extend([f"Parameter '{param_name}': {error}" for error in param_validation["errors"]])
                validation_result["is_valid"] = False
            
            validation_result["warnings"].extend([f"Parameter '{param_name}': {warning}" for warning in param_validation["warnings"]])
            validation_result["parameter_info"]["parameter_types"][param_name] = type(param_value).__name__
            
            # Check for unexpected parameters
            if param_name not in schema_properties and schema_properties:
                validation_result["parameter_info"]["unexpected_parameters"].append(param_name)
                validation_result["warnings"].append(f"Unexpected parameter: {param_name}")
        
        # Additional parameter validation
        if validation_options.get("strict_schema", False) and validation_result["parameter_info"]["unexpected_parameters"]:
            validation_result["errors"].append("Unexpected parameters not allowed in strict mode")
            validation_result["is_valid"] = False
        
        # Check parameter count limits
        max_params = validation_options.get("max_parameters", 50)
        if len(parameters) > max_params:
            validation_result["warnings"].append(f"Many parameters provided ({len(parameters)} > {max_params})")
        
        logger.info("API parameters validation completed",
                   total_parameters=len(parameters),
                   valid_parameters=validation_result["parameter_info"]["valid_parameters"],
                   is_valid=validation_result["is_valid"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "total_parameters": len(parameters),
                "validation_type": "api_parameters"
            }
        )
        
    except Exception as e:
        error_msg = f"API parameters validation failed: {str(e)}"
        logger.error("API parameters validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(
    name="validate_anthropic_request",
    description="Validate Anthropic API request format and content",
    tags=["validation", "anthropic", "api"]
)
async def validate_anthropic_request_task(
    request_data: Dict[str, Any],
    validation_config: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate Anthropic API request format and content.
    
    Args:
        request_data: Anthropic request data to validate
        validation_config: Optional validation configuration
    
    Returns:
        ConversionResult with validation status and details
    """
    logger.info("Validating Anthropic request")
    
    try:
        if validation_config is None:
            validation_config = {}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "request_info": {
                "model": request_data.get("model"),
                "message_count": 0,
                "has_system_message": bool(request_data.get("system")),
                "has_tools": bool(request_data.get("tools")),
                "has_tool_choice": bool(request_data.get("tool_choice")),
                "stream": request_data.get("stream", False),
                "max_tokens": request_data.get("max_tokens"),
                "temperature": request_data.get("temperature")
            }
        }
        
        # Validate using Pydantic model
        try:
            anthropic_request = MessagesRequest(**request_data)
            validation_result["request_info"]["message_count"] = len(anthropic_request.messages)
        except ValidationError as ve:
            validation_result["is_valid"] = False
            for error in ve.errors():
                field_path = " -> ".join(str(loc) for loc in error["loc"])
                validation_result["errors"].append(f"Field '{field_path}': {error['msg']}")
        except Exception as pe:
            validation_result["errors"].append(f"Pydantic validation failed: {str(pe)}")
            validation_result["is_valid"] = False
        
        # Additional Anthropic-specific validation
        messages = request_data.get("messages", [])
        if messages:
            message_validation = await _validate_anthropic_messages(messages)
            if not message_validation["is_valid"]:
                validation_result["errors"].extend(message_validation["errors"])
                validation_result["is_valid"] = False
            validation_result["warnings"].extend(message_validation["warnings"])
        
        # Validate model parameter
        model = request_data.get("model")
        if model:
            model_validation = await _validate_model_parameter(model)
            if not model_validation["is_valid"]:
                validation_result["errors"].extend(model_validation["errors"])
                validation_result["is_valid"] = False
            validation_result["warnings"].extend(model_validation["warnings"])
        
        # Validate tools if present
        tools = request_data.get("tools")
        if tools:
            tools_validation = await _validate_anthropic_tools(tools)
            if not tools_validation["is_valid"]:
                validation_result["errors"].extend(tools_validation["errors"])
                validation_result["is_valid"] = False
            validation_result["warnings"].extend(tools_validation["warnings"])
        
        # Validate generation parameters
        gen_params_validation = await _validate_generation_parameters(request_data)
        if not gen_params_validation["is_valid"]:
            validation_result["errors"].extend(gen_params_validation["errors"])
            validation_result["is_valid"] = False
        validation_result["warnings"].extend(gen_params_validation["warnings"])
        
        # Apply custom validation rules
        if validation_config.get("require_system_message", False):
            if not validation_result["request_info"]["has_system_message"]:
                validation_result["warnings"].append("System message recommended for better results")
        
        if validation_config.get("max_message_count", 0) > 0:
            max_messages = validation_config["max_message_count"]
            if validation_result["request_info"]["message_count"] > max_messages:
                validation_result["errors"].append(f"Too many messages: {validation_result['request_info']['message_count']} > {max_messages}")
                validation_result["is_valid"] = False
        
        logger.info("Anthropic request validation completed",
                   model=model,
                   message_count=validation_result["request_info"]["message_count"],
                   is_valid=validation_result["is_valid"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "model": model,
                "validation_type": "anthropic_request"
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


@task(
    name="validate_request_rate_limit",
    description="Validate request against rate limiting rules",
    tags=["validation", "rate-limit", "security"]
)
async def validate_request_rate_limit_task(
    request_info: Dict[str, Any],
    rate_limit_config: Dict[str, Any] = None,
    current_usage: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate request against rate limiting rules.
    
    Args:
        request_info: Request information for rate limiting
        rate_limit_config: Rate limiting configuration
        current_usage: Current usage statistics
    
    Returns:
        ConversionResult with validation status and details
    """
    logger.info("Validating request rate limits")
    
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
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "rate_limit_info": {
                "client_id": request_info.get("client_id"),
                "user_id": request_info.get("user_id"),
                "request_tokens": request_info.get("estimated_tokens", 0),
                "current_usage": current_usage,
                "limits": rate_limit_config,
                "usage_percentages": {}
            }
        }
        
        # Check requests per minute
        if current_usage["requests_last_minute"] >= rate_limit_config["requests_per_minute"]:
            validation_result["errors"].append("Rate limit exceeded: requests per minute")
            validation_result["is_valid"] = False
        else:
            usage_pct = (current_usage["requests_last_minute"] / rate_limit_config["requests_per_minute"]) * 100
            validation_result["rate_limit_info"]["usage_percentages"]["requests_per_minute"] = usage_pct
            if usage_pct > 80:
                validation_result["warnings"].append(f"High request rate: {usage_pct:.1f}% of minute limit")
        
        # Check requests per hour
        if current_usage["requests_last_hour"] >= rate_limit_config["requests_per_hour"]:
            validation_result["errors"].append("Rate limit exceeded: requests per hour")
            validation_result["is_valid"] = False
        else:
            usage_pct = (current_usage["requests_last_hour"] / rate_limit_config["requests_per_hour"]) * 100
            validation_result["rate_limit_info"]["usage_percentages"]["requests_per_hour"] = usage_pct
            if usage_pct > 80:
                validation_result["warnings"].append(f"High hourly usage: {usage_pct:.1f}% of hour limit")
        
        # Check requests per day
        if current_usage["requests_last_day"] >= rate_limit_config["requests_per_day"]:
            validation_result["errors"].append("Rate limit exceeded: requests per day")
            validation_result["is_valid"] = False
        else:
            usage_pct = (current_usage["requests_last_day"] / rate_limit_config["requests_per_day"]) * 100
            validation_result["rate_limit_info"]["usage_percentages"]["requests_per_day"] = usage_pct
            if usage_pct > 90:
                validation_result["warnings"].append(f"High daily usage: {usage_pct:.1f}% of day limit")
        
        # Check tokens per minute
        estimated_tokens = request_info.get("estimated_tokens", 0)
        if current_usage["tokens_last_minute"] + estimated_tokens > rate_limit_config["tokens_per_minute"]:
            validation_result["errors"].append("Rate limit exceeded: tokens per minute")
            validation_result["is_valid"] = False
        else:
            total_tokens = current_usage["tokens_last_minute"] + estimated_tokens
            usage_pct = (total_tokens / rate_limit_config["tokens_per_minute"]) * 100
            validation_result["rate_limit_info"]["usage_percentages"]["tokens_per_minute"] = usage_pct
            if usage_pct > 80:
                validation_result["warnings"].append(f"High token usage: {usage_pct:.1f}% of minute limit")
        
        # Check concurrent requests
        if current_usage["active_requests"] >= rate_limit_config["concurrent_requests"]:
            validation_result["errors"].append("Rate limit exceeded: concurrent requests")
            validation_result["is_valid"] = False
        else:
            usage_pct = (current_usage["active_requests"] / rate_limit_config["concurrent_requests"]) * 100
            validation_result["rate_limit_info"]["usage_percentages"]["concurrent_requests"] = usage_pct
            if usage_pct > 80:
                validation_result["warnings"].append(f"High concurrency: {usage_pct:.1f}% of concurrent limit")
        
        logger.info("Request rate limit validation completed",
                   is_valid=validation_result["is_valid"],
                   client_id=request_info.get("client_id"),
                   estimated_tokens=estimated_tokens)
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "client_id": request_info.get("client_id"),
                "validation_type": "rate_limit"
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


# Helper functions for request validation

async def _validate_url_structure(url: str) -> Dict[str, Any]:
    """Validate URL structure and format."""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        parsed = urlparse(url)
        
        # Check basic URL structure
        if not parsed.scheme:
            validation_result["errors"].append("URL missing scheme")
            validation_result["is_valid"] = False
        elif parsed.scheme not in ["http", "https"]:
            validation_result["warnings"].append(f"Unusual URL scheme: {parsed.scheme}")
        
        if not parsed.netloc:
            validation_result["errors"].append("URL missing hostname")
            validation_result["is_valid"] = False
        
        # Check for suspicious patterns
        if any(char in url for char in ["<", ">", "\"", "'"]):
            validation_result["warnings"].append("URL contains potentially unsafe characters")
        
        # Check URL length
        if len(url) > 2000:
            validation_result["warnings"].append("URL is very long")
        
    except Exception as e:
        validation_result["errors"].append(f"URL parsing failed: {str(e)}")
        validation_result["is_valid"] = False
    
    return validation_result


async def _validate_request_headers(headers: Dict[str, str], validation_rules: Dict[str, Any]) -> Dict[str, Any]:
    """Validate HTTP request headers."""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Check for required headers
        required_headers = validation_rules.get("required_headers", [])
        for required_header in required_headers:
            if required_header.lower() not in [h.lower() for h in headers.keys()]:
                validation_result["errors"].append(f"Missing required header: {required_header}")
                validation_result["is_valid"] = False
        
        # Validate specific headers
        for header_name, header_value in headers.items():
            header_name_lower = header_name.lower()
            
            # Validate content-type
            if header_name_lower == "content-type":
                if "application/json" not in header_value and "text/plain" not in header_value:
                    validation_result["warnings"].append(f"Unusual content type: {header_value}")
            
            # Validate authorization
            elif header_name_lower == "authorization":
                if not header_value.startswith(("Bearer ", "Basic ")):
                    validation_result["warnings"].append("Unusual authorization format")
            
            # Check for suspicious headers
            elif header_name_lower in ["x-forwarded-for", "x-real-ip"]:
                validation_result["warnings"].append(f"Proxy header detected: {header_name}")
            
            # Check header value length
            if len(header_value) > 1000:
                validation_result["warnings"].append(f"Very long header value: {header_name}")
        
        # Check total header count
        if len(headers) > 50:
            validation_result["warnings"].append("Many headers in request")
        
    except Exception as e:
        validation_result["errors"].append(f"Header validation failed: {str(e)}")
        validation_result["is_valid"] = False
    
    return validation_result


async def _validate_request_body(body: Any, content_type: str = None) -> Dict[str, Any]:
    """Validate HTTP request body."""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "body_size": 0
    }
    
    try:
        # Calculate body size
        if isinstance(body, str):
            validation_result["body_size"] = len(body.encode('utf-8'))
        elif isinstance(body, bytes):
            validation_result["body_size"] = len(body)
        elif isinstance(body, dict):
            validation_result["body_size"] = len(json.dumps(body).encode('utf-8'))
        else:
            validation_result["body_size"] = len(str(body).encode('utf-8'))
        
        # Validate JSON body
        if content_type and "application/json" in content_type:
            try:
                if isinstance(body, str):
                    json.loads(body)
                elif not isinstance(body, dict):
                    validation_result["errors"].append("JSON content-type but body is not JSON")
                    validation_result["is_valid"] = False
            except json.JSONDecodeError as je:
                validation_result["errors"].append(f"Invalid JSON body: {str(je)}")
                validation_result["is_valid"] = False
        
        # Check body size limits
        if validation_result["body_size"] > 10 * 1024 * 1024:  # 10MB
            validation_result["warnings"].append(f"Very large request body: {validation_result['body_size']} bytes")
        
        # Check for suspicious content
        if isinstance(body, str):
            suspicious_patterns = ["<script", "javascript:", "eval(", "exec("]
            for pattern in suspicious_patterns:
                if pattern in body.lower():
                    validation_result["warnings"].append(f"Suspicious content pattern: {pattern}")
        
    except Exception as e:
        validation_result["errors"].append(f"Body validation failed: {str(e)}")
        validation_result["is_valid"] = False
    
    return validation_result


async def _validate_single_parameter(
    param_name: str, 
    param_value: Any, 
    param_schema: Dict[str, Any] = None,
    validation_options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Validate a single API parameter."""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        if param_schema is None:
            return validation_result
        
        # Type validation
        expected_type = param_schema.get("type")
        if expected_type:
            if expected_type == "string" and not isinstance(param_value, str):
                validation_result["errors"].append(f"Expected string, got {type(param_value).__name__}")
                validation_result["is_valid"] = False
            elif expected_type == "integer" and not isinstance(param_value, int):
                validation_result["errors"].append(f"Expected integer, got {type(param_value).__name__}")
                validation_result["is_valid"] = False
            elif expected_type == "number" and not isinstance(param_value, (int, float)):
                validation_result["errors"].append(f"Expected number, got {type(param_value).__name__}")
                validation_result["is_valid"] = False
            elif expected_type == "boolean" and not isinstance(param_value, bool):
                validation_result["errors"].append(f"Expected boolean, got {type(param_value).__name__}")
                validation_result["is_valid"] = False
        
        # Range validation
        if isinstance(param_value, (int, float)):
            minimum = param_schema.get("minimum")
            maximum = param_schema.get("maximum")
            
            if minimum is not None and param_value < minimum:
                validation_result["errors"].append(f"Value {param_value} below minimum {minimum}")
                validation_result["is_valid"] = False
            
            if maximum is not None and param_value > maximum:
                validation_result["errors"].append(f"Value {param_value} above maximum {maximum}")
                validation_result["is_valid"] = False
        
        # String length validation
        if isinstance(param_value, str):
            min_length = param_schema.get("minLength", 0)
            max_length = param_schema.get("maxLength")
            
            if len(param_value) < min_length:
                validation_result["errors"].append(f"String too short: {len(param_value)} < {min_length}")
                validation_result["is_valid"] = False
            
            if max_length and len(param_value) > max_length:
                validation_result["errors"].append(f"String too long: {len(param_value)} > {max_length}")
                validation_result["is_valid"] = False
            
            # Pattern validation
            pattern = param_schema.get("pattern")
            if pattern:
                try:
                    if not re.match(pattern, param_value):
                        validation_result["errors"].append(f"String does not match pattern: {pattern}")
                        validation_result["is_valid"] = False
                except re.error:
                    validation_result["warnings"].append(f"Invalid regex pattern: {pattern}")
        
        # Enum validation
        enum_values = param_schema.get("enum")
        if enum_values and param_value not in enum_values:
            validation_result["errors"].append(f"Value not in allowed enum: {enum_values}")
            validation_result["is_valid"] = False
        
    except Exception as e:
        validation_result["errors"].append(f"Parameter validation failed: {str(e)}")
        validation_result["is_valid"] = False
    
    return validation_result


async def _validate_anthropic_messages(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate Anthropic message format."""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        if not messages:
            validation_result["errors"].append("No messages provided")
            validation_result["is_valid"] = False
            return validation_result
        
        valid_roles = ["user", "assistant"]
        
        for i, message in enumerate(messages):
            # Check required fields
            if "role" not in message:
                validation_result["errors"].append(f"Message {i} missing role")
                validation_result["is_valid"] = False
            elif message["role"] not in valid_roles:
                validation_result["errors"].append(f"Message {i} invalid role: {message['role']}")
                validation_result["is_valid"] = False
            
            if "content" not in message:
                validation_result["errors"].append(f"Message {i} missing content")
                validation_result["is_valid"] = False
        
        # Check message alternation (user/assistant pattern)
        roles = [msg.get("role") for msg in messages]
        if len(roles) > 1:
            for i in range(len(roles) - 1):
                if roles[i] == roles[i + 1] and roles[i] == "user":
                    validation_result["warnings"].append(f"Consecutive user messages at positions {i}, {i+1}")
    
    except Exception as e:
        validation_result["errors"].append(f"Message validation failed: {str(e)}")
        validation_result["is_valid"] = False
    
    return validation_result


async def _validate_model_parameter(model: str) -> Dict[str, Any]:
    """Validate model parameter."""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Check model format
        if not model or not isinstance(model, str):
            validation_result["errors"].append("Model must be a non-empty string")
            validation_result["is_valid"] = False
            return validation_result
        
        # Check for known model patterns
        known_patterns = [
            "claude", "gpt", "anthropic", "openai", "gemini", "llama"
        ]
        
        if not any(pattern in model.lower() for pattern in known_patterns):
            validation_result["warnings"].append(f"Unknown model pattern: {model}")
        
        # Check model name length
        if len(model) > 100:
            validation_result["warnings"].append("Model name is very long")
        
    except Exception as e:
        validation_result["errors"].append(f"Model validation failed: {str(e)}")
        validation_result["is_valid"] = False
    
    return validation_result


async def _validate_anthropic_tools(tools: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate Anthropic tools format."""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        if len(tools) > 20:
            validation_result["warnings"].append("Many tools provided (>20)")
        
        tool_names = set()
        for i, tool in enumerate(tools):
            # Check required fields
            if "name" not in tool:
                validation_result["errors"].append(f"Tool {i} missing name")
                validation_result["is_valid"] = False
            elif tool["name"] in tool_names:
                validation_result["errors"].append(f"Duplicate tool name: {tool['name']}")
                validation_result["is_valid"] = False
            else:
                tool_names.add(tool["name"])
            
            if "description" not in tool:
                validation_result["errors"].append(f"Tool {i} missing description")
                validation_result["is_valid"] = False
            
            if "input_schema" not in tool:
                validation_result["errors"].append(f"Tool {i} missing input_schema")
                validation_result["is_valid"] = False
    
    except Exception as e:
        validation_result["errors"].append(f"Tools validation failed: {str(e)}")
        validation_result["is_valid"] = False
    
    return validation_result


async def _validate_generation_parameters(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate generation parameters."""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Validate max_tokens
        max_tokens = request_data.get("max_tokens")
        if max_tokens is not None:
            if not isinstance(max_tokens, int) or max_tokens <= 0:
                validation_result["errors"].append("max_tokens must be a positive integer")
                validation_result["is_valid"] = False
            elif max_tokens > 100000:
                validation_result["warnings"].append("max_tokens is very high (>100000)")
        
        # Validate temperature
        temperature = request_data.get("temperature")
        if temperature is not None:
            if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
                validation_result["errors"].append("temperature must be between 0 and 2")
                validation_result["is_valid"] = False
        
        # Validate top_p
        top_p = request_data.get("top_p")
        if top_p is not None:
            if not isinstance(top_p, (int, float)) or top_p <= 0 or top_p > 1:
                validation_result["errors"].append("top_p must be between 0 and 1")
                validation_result["is_valid"] = False
        
        # Validate top_k
        top_k = request_data.get("top_k")
        if top_k is not None:
            if not isinstance(top_k, int) or top_k <= 0:
                validation_result["errors"].append("top_k must be a positive integer")
                validation_result["is_valid"] = False
    
    except Exception as e:
        validation_result["errors"].append(f"Generation parameters validation failed: {str(e)}")
        validation_result["is_valid"] = False
    
    return validation_result