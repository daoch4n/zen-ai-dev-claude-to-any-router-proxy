"""Tool validation task functions."""

from typing import Any, Dict, List
from ...models.anthropic import Message, Tool
from ...models.instructor import ToolValidationResult
from ...core.logging_config import get_logger

logger = get_logger("validation.tool_tasks")


def validate_tool_data(data: Any) -> Dict[str, Any]:
    """Validate tool data structure.
    
    Args:
        data: Tool data to validate (dict or Tool object)
        
    Returns:
        Dict with validation results including errors, warnings, suggestions
    """
    try:
        if not isinstance(data, (dict, Tool)):
            return {
                "is_valid": False,
                "errors": ["Data must be a dictionary or Tool object"],
                "warnings": [],
                "suggestions": []
            }
        
        # Convert to dict if Tool object
        if isinstance(data, Tool):
            tool_dict = data.model_dump()
        else:
            tool_dict = data
        
        errors = []
        warnings = []
        suggestions = []
        
        # Validate required fields
        if "name" not in tool_dict:
            errors.append("Missing required field: name")
        elif not tool_dict["name"]:
            errors.append("Tool name cannot be empty")
        
        if "input_schema" not in tool_dict:
            errors.append("Missing required field: input_schema")
        else:
            schema_errors = validate_input_schema(tool_dict["input_schema"])
            errors.extend(schema_errors)
        
        # Check description
        if not tool_dict.get("description"):
            warnings.append("Tool missing description - recommended for better AI understanding")
            suggestions.append("Add a clear description of what the tool does")
        
        is_valid = len(errors) == 0
        
        logger.debug("Tool validation completed",
                    tool_name=tool_dict.get("name"),
                    has_description=bool(tool_dict.get("description")),
                    error_count=len(errors))
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error("Tool validation failed", error=str(e), exc_info=True)
        return {
            "is_valid": False,
            "errors": [f"Tool validation failed: {str(e)}"],
            "warnings": [],
            "suggestions": []
        }


def validate_input_schema(schema: Dict[str, Any]) -> List[str]:
    """Validate tool input schema.
    
    Args:
        schema: Tool input schema dictionary
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if not isinstance(schema, dict):
        errors.append("Input schema must be a dictionary")
        return errors
    
    # Check for required schema fields
    if "type" not in schema:
        errors.append("Input schema missing 'type' field")
    elif schema["type"] != "object":
        errors.append("Input schema type should be 'object' for tool parameters")
    
    # Validate properties if present
    if "properties" in schema:
        if not isinstance(schema["properties"], dict):
            errors.append("Schema 'properties' must be a dictionary")
        else:
            for prop_name, prop_def in schema["properties"].items():
                if not isinstance(prop_def, dict):
                    errors.append(f"Property '{prop_name}' definition must be a dictionary")
                elif "type" not in prop_def:
                    errors.append(f"Property '{prop_name}' missing 'type' field")
    
    return errors


def validate_tool_flow_data(messages: List[Message], available_tools: List[Tool]) -> ToolValidationResult:
    """Validate tool flow across messages to detect orphaned tools.
    
    Args:
        messages: List of conversation messages
        available_tools: List of available tools
        
    Returns:
        ToolValidationResult with orphaned tools and validation errors
    """
    try:
        tool_uses = {}
        tool_results = {}
        orphaned_tools = []
        missing_results = []
        validation_errors = []
        
        # Extract tool uses and results from messages
        for msg_idx, message in enumerate(messages):
            if isinstance(message.content, list):
                for block in message.content:
                    if hasattr(block, 'type'):
                        if block.type == "tool_use":
                            tool_id = getattr(block, 'id', None)
                            if tool_id:
                                tool_uses[tool_id] = {
                                    "message_index": msg_idx,
                                    "name": getattr(block, 'name', ''),
                                    "input": getattr(block, 'input', {})
                                }
                            else:
                                validation_errors.append(f"Tool use in message {msg_idx} missing ID")
                        
                        elif block.type == "tool_result":
                            tool_use_id = getattr(block, 'tool_use_id', None)
                            if tool_use_id:
                                tool_results[tool_use_id] = {
                                    "message_index": msg_idx,
                                    "content": getattr(block, 'content', '')
                                }
                            else:
                                validation_errors.append(f"Tool result in message {msg_idx} missing tool_use_id")
        
        # Find orphaned tools and missing results
        orphaned_tools = find_orphaned_tools(tool_uses, tool_results)
        missing_results = find_missing_results(tool_uses, tool_results)
        
        # Generate suggestions
        suggestions = []
        if orphaned_tools:
            suggestions.append("Add tool_result blocks for orphaned tool uses")
        if missing_results:
            suggestions.append("Remove tool_result blocks without corresponding tool_use")
        if validation_errors:
            suggestions.append("Fix tool ID and reference issues")
        
        is_valid = (
            len(orphaned_tools) == 0 and 
            len(missing_results) == 0 and 
            len(validation_errors) == 0
        )
        
        result = ToolValidationResult(
            is_valid=is_valid,
            orphaned_tools=orphaned_tools,
            missing_results=missing_results,
            validation_errors=validation_errors,
            suggestions=suggestions
        )
        
        logger.debug("Tool flow validation completed",
                    total_tool_uses=len(tool_uses),
                    total_tool_results=len(tool_results),
                    orphaned_count=len(orphaned_tools),
                    missing_results_count=len(missing_results))
        
        return result
        
    except Exception as e:
        logger.error("Tool flow validation failed", error=str(e), exc_info=True)
        from ...utils.errors import ToolValidationError
        raise ToolValidationError(f"Tool flow validation failed: {e}")


def find_orphaned_tools(tool_uses: Dict[str, Any], tool_results: Dict[str, Any]) -> List[str]:
    """Find tool uses without corresponding results.
    
    Args:
        tool_uses: Dictionary of tool uses by ID
        tool_results: Dictionary of tool results by tool_use_id
        
    Returns:
        List of orphaned tool IDs
    """
    orphaned = []
    for tool_id in tool_uses:
        if tool_id not in tool_results:
            orphaned.append(tool_id)
    return orphaned


def find_missing_results(tool_uses: Dict[str, Any], tool_results: Dict[str, Any]) -> List[str]:
    """Find tool results without corresponding uses.
    
    Args:
        tool_uses: Dictionary of tool uses by ID
        tool_results: Dictionary of tool results by tool_use_id
        
    Returns:
        List of tool result IDs without corresponding uses
    """
    missing = []
    for tool_id in tool_results:
        if tool_id not in tool_uses:
            missing.append(tool_id)
    return missing