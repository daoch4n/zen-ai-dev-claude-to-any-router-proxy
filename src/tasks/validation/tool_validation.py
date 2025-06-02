"""Tool Validation Tasks for OpenRouter Anthropic Server.

Prefect tasks for validating tool configurations, executions, and results.
Part of Phase 6B comprehensive refactoring - Validation Tasks.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union

from prefect import task
from pydantic import ValidationError

from ...core.logging_config import get_logger
from ...models.instructor import ConversionResult
from ...services.tool_execution import ToolExecutionResult

# Initialize logging
logger = get_logger("tool_validation")


@task(
    name="validate_tool_definition",
    description="Validate tool definition structure and schema",
    tags=["validation", "tools", "schema"]
)
async def validate_tool_definition_task(
    tool_definition: Dict[str, Any],
    validation_rules: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate a tool definition for correct structure and schema.
    
    Args:
        tool_definition: Tool definition to validate
        validation_rules: Optional validation configuration
    
    Returns:
        ConversionResult with validation status and details
    """
    logger.info("Validating tool definition", tool_name=tool_definition.get("name", "unknown"))
    
    try:
        if validation_rules is None:
            validation_rules = {}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "tool_info": {
                "name": tool_definition.get("name"),
                "has_description": bool(tool_definition.get("description")),
                "has_input_schema": bool(tool_definition.get("input_schema")),
                "schema_properties_count": 0,
                "required_parameters": []
            }
        }
        
        # Check required fields
        required_fields = ["name", "description", "input_schema"]
        for field in required_fields:
            if field not in tool_definition:
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False
        
        # Validate name
        tool_name = tool_definition.get("name")
        if tool_name:
            if not isinstance(tool_name, str):
                validation_result["errors"].append("Tool name must be a string")
                validation_result["is_valid"] = False
            elif not tool_name.strip():
                validation_result["errors"].append("Tool name cannot be empty")
                validation_result["is_valid"] = False
            elif len(tool_name) > 100:
                validation_result["warnings"].append("Tool name is very long (>100 characters)")
            
            # Check for valid characters
            if not tool_name.replace("_", "").replace("-", "").isalnum():
                validation_result["warnings"].append("Tool name contains special characters")
        
        # Validate description
        description = tool_definition.get("description")
        if description:
            if not isinstance(description, str):
                validation_result["errors"].append("Description must be a string")
                validation_result["is_valid"] = False
            elif len(description) < 10:
                validation_result["warnings"].append("Description is very short (<10 characters)")
            elif len(description) > 1000:
                validation_result["warnings"].append("Description is very long (>1000 characters)")
        
        # Validate input schema
        input_schema = tool_definition.get("input_schema")
        if input_schema:
            schema_validation = await _validate_tool_input_schema(input_schema)
            
            if not schema_validation["is_valid"]:
                validation_result["errors"].extend(schema_validation["errors"])
                validation_result["is_valid"] = False
            
            validation_result["warnings"].extend(schema_validation["warnings"])
            validation_result["tool_info"]["schema_properties_count"] = schema_validation["properties_count"]
            validation_result["tool_info"]["required_parameters"] = schema_validation["required_parameters"]
        
        # Apply custom validation rules
        if validation_rules.get("enforce_strict_naming", False):
            if tool_name and not tool_name.islower():
                validation_result["warnings"].append("Tool name should be lowercase")
        
        if validation_rules.get("require_examples", False):
            if "examples" not in tool_definition:
                validation_result["warnings"].append("Tool definition should include examples")
        
        logger.info("Tool definition validation completed",
                   tool_name=tool_name,
                   is_valid=validation_result["is_valid"],
                   error_count=len(validation_result["errors"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "tool_name": tool_name,
                "validation_type": "tool_definition"
            }
        )
        
    except Exception as e:
        error_msg = f"Tool definition validation failed: {str(e)}"
        logger.error("Tool definition validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(
    name="validate_tool_execution_request",
    description="Validate tool execution request parameters",
    tags=["validation", "tools", "execution"]
)
async def validate_tool_execution_request_task(
    tool_name: str,
    tool_input: Dict[str, Any],
    tool_definition: Dict[str, Any] = None,
    validation_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate a tool execution request against the tool's schema.
    
    Args:
        tool_name: Name of the tool to execute
        tool_input: Input parameters for the tool
        tool_definition: Optional tool definition for validation
        validation_options: Optional validation configuration
    
    Returns:
        ConversionResult with validation status and details
    """
    logger.info("Validating tool execution request", tool_name=tool_name)
    
    try:
        if validation_options is None:
            validation_options = {}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "request_info": {
                "tool_name": tool_name,
                "input_type": type(tool_input).__name__,
                "input_size": len(str(tool_input)),
                "parameter_count": len(tool_input) if isinstance(tool_input, dict) else 0,
                "provided_parameters": list(tool_input.keys()) if isinstance(tool_input, dict) else []
            }
        }
        
        # Basic tool name validation
        if not tool_name or not isinstance(tool_name, str):
            validation_result["errors"].append("Tool name must be a non-empty string")
            validation_result["is_valid"] = False
        
        # Basic input validation
        if not isinstance(tool_input, dict):
            validation_result["errors"].append("Tool input must be a dictionary")
            validation_result["is_valid"] = False
        
        # If we have a tool definition, validate against its schema
        if tool_definition and isinstance(tool_input, dict):
            schema_validation = await _validate_against_tool_schema(
                tool_input, tool_definition.get("input_schema", {})
            )
            
            if not schema_validation["is_valid"]:
                validation_result["errors"].extend(schema_validation["errors"])
                validation_result["is_valid"] = False
            
            validation_result["warnings"].extend(schema_validation["warnings"])
            validation_result["request_info"]["schema_validation"] = schema_validation
        
        # Check for potentially dangerous parameters
        if isinstance(tool_input, dict):
            dangerous_patterns = validation_options.get("dangerous_patterns", [
                "eval", "exec", "import", "__", "system", "shell"
            ])
            
            for param_name, param_value in tool_input.items():
                if isinstance(param_value, str):
                    for pattern in dangerous_patterns:
                        if pattern in param_value.lower():
                            validation_result["warnings"].append(
                                f"Parameter '{param_name}' contains potentially dangerous pattern: {pattern}"
                            )
        
        # Check input size limits
        max_input_size = validation_options.get("max_input_size", 100000)  # 100KB default
        if validation_result["request_info"]["input_size"] > max_input_size:
            validation_result["warnings"].append(
                f"Tool input is very large ({validation_result['request_info']['input_size']} bytes)"
            )
        
        logger.info("Tool execution request validation completed",
                   tool_name=tool_name,
                   is_valid=validation_result["is_valid"],
                   parameter_count=validation_result["request_info"]["parameter_count"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "tool_name": tool_name,
                "validation_type": "execution_request"
            }
        )
        
    except Exception as e:
        error_msg = f"Tool execution request validation failed: {str(e)}"
        logger.error("Tool execution request validation failed", 
                    tool_name=tool_name, error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(
    name="validate_tool_execution_result",
    description="Validate tool execution result structure and content",
    tags=["validation", "tools", "results"]
)
async def validate_tool_execution_result_task(
    execution_result: Union[ToolExecutionResult, Dict[str, Any]],
    expected_format: str = "standard",
    validation_rules: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate a tool execution result for correct structure and content.
    
    Args:
        execution_result: Tool execution result to validate
        expected_format: Expected result format ("standard", "anthropic", "openai")
        validation_rules: Optional validation configuration
    
    Returns:
        ConversionResult with validation status and details
    """
    logger.info("Validating tool execution result", expected_format=expected_format)
    
    try:
        if validation_rules is None:
            validation_rules = {}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "result_info": {
                "format": expected_format,
                "has_success_indicator": False,
                "has_result_data": False,
                "has_error_info": False,
                "result_type": None,
                "result_size": 0
            }
        }
        
        # Convert to dict if it's a ToolExecutionResult
        if isinstance(execution_result, ToolExecutionResult):
            result_dict = {
                "success": execution_result.success,
                "result": execution_result.result,
                "error": execution_result.error,
                "metadata": execution_result.metadata
            }
            validation_result["result_info"]["result_type"] = "ToolExecutionResult"
        elif isinstance(execution_result, dict):
            result_dict = execution_result
            validation_result["result_info"]["result_type"] = "dict"
        else:
            validation_result["errors"].append("Execution result must be ToolExecutionResult or dict")
            validation_result["is_valid"] = False
            result_dict = {}
        
        # Validate based on expected format
        if expected_format == "standard":
            # Check for required fields
            if "success" in result_dict:
                validation_result["result_info"]["has_success_indicator"] = True
                if not isinstance(result_dict["success"], bool):
                    validation_result["errors"].append("Success field must be boolean")
                    validation_result["is_valid"] = False
            else:
                validation_result["errors"].append("Missing required field: success")
                validation_result["is_valid"] = False
            
            # Check result/error consistency
            success = result_dict.get("success", False)
            has_result = "result" in result_dict and result_dict["result"] is not None
            has_error = "error" in result_dict and result_dict["error"] is not None
            
            validation_result["result_info"]["has_result_data"] = has_result
            validation_result["result_info"]["has_error_info"] = has_error
            
            if success and not has_result:
                validation_result["warnings"].append("Success=True but no result data provided")
            
            if not success and not has_error:
                validation_result["warnings"].append("Success=False but no error information provided")
            
            if success and has_error:
                validation_result["warnings"].append("Success=True but error information is present")
        
        elif expected_format == "anthropic":
            # Validate Anthropic tool result format
            if "type" not in result_dict:
                validation_result["errors"].append("Missing required field: type")
                validation_result["is_valid"] = False
            elif result_dict["type"] != "tool_result":
                validation_result["errors"].append("Type must be 'tool_result' for Anthropic format")
                validation_result["is_valid"] = False
            
            if "tool_use_id" not in result_dict:
                validation_result["errors"].append("Missing required field: tool_use_id")
                validation_result["is_valid"] = False
            
            if "content" not in result_dict:
                validation_result["errors"].append("Missing required field: content")
                validation_result["is_valid"] = False
        
        elif expected_format == "openai":
            # Validate OpenAI tool result format
            if "tool_call_id" not in result_dict:
                validation_result["errors"].append("Missing required field: tool_call_id")
                validation_result["is_valid"] = False
            
            if "role" not in result_dict:
                validation_result["errors"].append("Missing required field: role")
                validation_result["is_valid"] = False
            elif result_dict["role"] != "tool":
                validation_result["errors"].append("Role must be 'tool' for OpenAI format")
                validation_result["is_valid"] = False
        
        # Calculate result size
        if result_dict:
            try:
                validation_result["result_info"]["result_size"] = len(json.dumps(result_dict))
            except (TypeError, ValueError):
                validation_result["result_info"]["result_size"] = len(str(result_dict))
        
        # Check result size limits
        max_result_size = validation_rules.get("max_result_size", 1000000)  # 1MB default
        if validation_result["result_info"]["result_size"] > max_result_size:
            validation_result["warnings"].append(
                f"Tool result is very large ({validation_result['result_info']['result_size']} bytes)"
            )
        
        # Validate content safety if requested
        if validation_rules.get("check_content_safety", False):
            content_validation = await _validate_result_content_safety(result_dict)
            validation_result["warnings"].extend(content_validation.get("warnings", []))
        
        logger.info("Tool execution result validation completed",
                   is_valid=validation_result["is_valid"],
                   format=expected_format,
                   result_size=validation_result["result_info"]["result_size"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "expected_format": expected_format,
                "validation_type": "execution_result"
            }
        )
        
    except Exception as e:
        error_msg = f"Tool execution result validation failed: {str(e)}"
        logger.error("Tool execution result validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(
    name="validate_tool_registry",
    description="Validate tool registry for completeness and consistency",
    tags=["validation", "tools", "registry"]
)
async def validate_tool_registry_task(
    tool_registry: Dict[str, Any],
    expected_tools: List[str] = None,
    validation_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate a tool registry for completeness and consistency.
    
    Args:
        tool_registry: Tool registry to validate
        expected_tools: Optional list of expected tool names
        validation_options: Optional validation configuration
    
    Returns:
        ConversionResult with validation status and details
    """
    logger.info("Validating tool registry", registry_size=len(tool_registry))
    
    try:
        if validation_options is None:
            validation_options = {}
        if expected_tools is None:
            expected_tools = []
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "registry_info": {
                "total_tools": len(tool_registry),
                "tool_names": list(tool_registry.keys()),
                "missing_tools": [],
                "unexpected_tools": [],
                "duplicate_tools": [],
                "invalid_tools": []
            }
        }
        
        # Check for expected tools
        if expected_tools:
            missing_tools = set(expected_tools) - set(tool_registry.keys())
            if missing_tools:
                validation_result["registry_info"]["missing_tools"] = list(missing_tools)
                validation_result["errors"].append(f"Missing expected tools: {list(missing_tools)}")
                validation_result["is_valid"] = False
            
            unexpected_tools = set(tool_registry.keys()) - set(expected_tools)
            if unexpected_tools:
                validation_result["registry_info"]["unexpected_tools"] = list(unexpected_tools)
                validation_result["warnings"].append(f"Unexpected tools found: {list(unexpected_tools)}")
        
        # Check for duplicate tool names (case-insensitive)
        tool_names_lower = {}
        for tool_name in tool_registry.keys():
            lower_name = tool_name.lower()
            if lower_name in tool_names_lower:
                validation_result["registry_info"]["duplicate_tools"].append((tool_name, tool_names_lower[lower_name]))
                validation_result["errors"].append(f"Duplicate tool names (case-insensitive): {tool_name}, {tool_names_lower[lower_name]}")
                validation_result["is_valid"] = False
            tool_names_lower[lower_name] = tool_name
        
        # Validate each tool in the registry
        for tool_name, tool_callable in tool_registry.items():
            tool_validation = await _validate_registry_tool_entry(tool_name, tool_callable)
            
            if not tool_validation["is_valid"]:
                validation_result["registry_info"]["invalid_tools"].append(tool_name)
                validation_result["errors"].extend([f"Tool '{tool_name}': {error}" for error in tool_validation["errors"]])
                validation_result["is_valid"] = False
            
            validation_result["warnings"].extend([f"Tool '{tool_name}': {warning}" for warning in tool_validation["warnings"]])
        
        # Check registry size limits
        max_tools = validation_options.get("max_tools", 100)
        if len(tool_registry) > max_tools:
            validation_result["warnings"].append(f"Tool registry is very large ({len(tool_registry)} tools)")
        
        logger.info("Tool registry validation completed",
                   total_tools=len(tool_registry),
                   is_valid=validation_result["is_valid"],
                   invalid_tools=len(validation_result["registry_info"]["invalid_tools"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "total_tools": len(tool_registry),
                "validation_type": "tool_registry"
            }
        )
        
    except Exception as e:
        error_msg = f"Tool registry validation failed: {str(e)}"
        logger.error("Tool registry validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


# Helper functions for validation tasks

async def _validate_tool_input_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a tool's input schema structure."""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "properties_count": 0,
        "required_parameters": []
    }
    
    try:
        # Check schema type
        if schema.get("type") != "object":
            validation_result["warnings"].append("Schema type should be 'object'")
        
        # Check for properties
        properties = schema.get("properties", {})
        if not properties:
            validation_result["warnings"].append("Schema has no properties defined")
        else:
            validation_result["properties_count"] = len(properties)
            
            # Validate each property
            for prop_name, prop_schema in properties.items():
                if not isinstance(prop_schema, dict):
                    validation_result["errors"].append(f"Property '{prop_name}' schema must be a dict")
                    validation_result["is_valid"] = False
                    continue
                
                if "type" not in prop_schema:
                    validation_result["warnings"].append(f"Property '{prop_name}' missing type")
                
                if "description" not in prop_schema:
                    validation_result["warnings"].append(f"Property '{prop_name}' missing description")
        
        # Check required parameters
        required = schema.get("required", [])
        if required:
            validation_result["required_parameters"] = required
            
            # Validate required parameters exist in properties
            for req_param in required:
                if req_param not in properties:
                    validation_result["errors"].append(f"Required parameter '{req_param}' not in properties")
                    validation_result["is_valid"] = False
        
        # Check for additional properties
        if "additionalProperties" in schema:
            if schema["additionalProperties"] is True:
                validation_result["warnings"].append("Schema allows additional properties")
        
    except Exception as e:
        validation_result["errors"].append(f"Schema validation failed: {str(e)}")
        validation_result["is_valid"] = False
    
    return validation_result


async def _validate_against_tool_schema(
    tool_input: Dict[str, Any], 
    input_schema: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate tool input against its schema."""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])
        
        # Check required parameters
        for req_param in required:
            if req_param not in tool_input:
                validation_result["errors"].append(f"Missing required parameter: {req_param}")
                validation_result["is_valid"] = False
        
        # Check provided parameters
        for param_name, param_value in tool_input.items():
            if param_name not in properties:
                validation_result["warnings"].append(f"Unexpected parameter: {param_name}")
                continue
            
            prop_schema = properties[param_name]
            expected_type = prop_schema.get("type")
            
            # Basic type checking
            if expected_type:
                if expected_type == "string" and not isinstance(param_value, str):
                    validation_result["errors"].append(f"Parameter '{param_name}' should be string")
                    validation_result["is_valid"] = False
                elif expected_type == "integer" and not isinstance(param_value, int):
                    validation_result["errors"].append(f"Parameter '{param_name}' should be integer")
                    validation_result["is_valid"] = False
                elif expected_type == "number" and not isinstance(param_value, (int, float)):
                    validation_result["errors"].append(f"Parameter '{param_name}' should be number")
                    validation_result["is_valid"] = False
                elif expected_type == "boolean" and not isinstance(param_value, bool):
                    validation_result["errors"].append(f"Parameter '{param_name}' should be boolean")
                    validation_result["is_valid"] = False
                elif expected_type == "array" and not isinstance(param_value, list):
                    validation_result["errors"].append(f"Parameter '{param_name}' should be array")
                    validation_result["is_valid"] = False
                elif expected_type == "object" and not isinstance(param_value, dict):
                    validation_result["errors"].append(f"Parameter '{param_name}' should be object")
                    validation_result["is_valid"] = False
        
    except Exception as e:
        validation_result["errors"].append(f"Schema validation failed: {str(e)}")
        validation_result["is_valid"] = False
    
    return validation_result


async def _validate_result_content_safety(result_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Validate result content for safety concerns."""
    validation_result = {
        "warnings": []
    }
    
    try:
        # Convert result to string for analysis
        result_str = json.dumps(result_dict).lower()
        
        # Check for potentially sensitive patterns
        sensitive_patterns = [
            "password", "secret", "token", "key", "credential",
            "private", "confidential", "internal", "admin"
        ]
        
        for pattern in sensitive_patterns:
            if pattern in result_str:
                validation_result["warnings"].append(f"Result contains potentially sensitive content: {pattern}")
        
        # Check for very long content
        if len(result_str) > 50000:  # 50KB
            validation_result["warnings"].append("Result contains very long content")
        
    except Exception:
        # If we can't analyze the content, just warn
        validation_result["warnings"].append("Could not analyze result content safety")
    
    return validation_result


async def _validate_registry_tool_entry(tool_name: str, tool_callable: Any) -> Dict[str, Any]:
    """Validate a single tool entry in the registry."""
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Check if tool_callable is callable
        if not callable(tool_callable):
            validation_result["errors"].append("Tool entry is not callable")
            validation_result["is_valid"] = False
        
        # Check for async function
        if callable(tool_callable):
            if asyncio.iscoroutinefunction(tool_callable):
                validation_result["warnings"].append("Tool is async function")
            
            # Try to get function signature if possible
            try:
                import inspect
                sig = inspect.signature(tool_callable)
                param_count = len(sig.parameters)
                
                if param_count == 0:
                    validation_result["warnings"].append("Tool function has no parameters")
                elif param_count > 10:
                    validation_result["warnings"].append(f"Tool function has many parameters ({param_count})")
                
            except Exception:
                # Can't inspect signature, that's ok
                pass
        
    except Exception as e:
        validation_result["errors"].append(f"Tool entry validation failed: {str(e)}")
        validation_result["is_valid"] = False
    
    return validation_result