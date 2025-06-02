"""Message validation task functions."""

from typing import Any, Dict, List, Union
from ...models.anthropic import Message, MessagesRequest
from ...models.instructor import ValidationResult
from ...core.logging_config import get_logger

logger = get_logger("validation.message_tasks")


def validate_message_data(data: Any) -> Dict[str, Any]:
    """Validate message data structure.
    
    Args:
        data: Message data to validate (dict or Message object)
        
    Returns:
        Dict with validation results including errors, warnings, suggestions
    """
    try:
        # Basic validation
        if not isinstance(data, (dict, Message)):
            return {
                "is_valid": False,
                "errors": ["Data must be a dictionary or Message object"],
                "warnings": [],
                "suggestions": ["Provide valid message data with role and content"]
            }
        
        # Convert to dict if Message object
        if isinstance(data, Message):
            message_dict = data.model_dump()
        else:
            message_dict = data
        
        errors = []
        warnings = []
        suggestions = []
        
        # Validate required fields
        if "role" not in message_dict:
            errors.append("Missing required field: role")
        elif message_dict["role"] not in ["user", "assistant"]:
            errors.append(f"Invalid role: {message_dict['role']}. Must be 'user' or 'assistant'")
        
        if "content" not in message_dict:
            errors.append("Missing required field: content")
        elif not message_dict["content"]:
            errors.append("Content cannot be empty")
        
        # Validate content structure
        content = message_dict.get("content")
        if isinstance(content, list):
            content_errors = validate_content_blocks(content)
            errors.extend(content_errors)
        
        # Check for tool-related issues
        if isinstance(content, list):
            tool_warnings = check_tool_usage_patterns(content)
            warnings.extend(tool_warnings)
        
        # Generate suggestions
        if errors:
            suggestions.append("Fix validation errors before proceeding")
        if warnings:
            suggestions.append("Review warnings for potential improvements")
        
        is_valid = len(errors) == 0
        
        logger.debug("Message validation completed",
                    role=message_dict.get("role"),
                    content_type="list" if isinstance(content, list) else "string",
                    error_count=len(errors),
                    warning_count=len(warnings))
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error("Message validation failed", error=str(e), exc_info=True)
        return {
            "is_valid": False,
            "errors": [f"Validation failed: {str(e)}"],
            "warnings": [],
            "suggestions": ["Check message format and try again"]
        }


def validate_content_blocks(content_blocks: List[Dict[str, Any]]) -> List[str]:
    """Validate content blocks structure.
    
    Args:
        content_blocks: List of content block dictionaries
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    for i, block in enumerate(content_blocks):
        if not isinstance(block, dict):
            errors.append(f"Content block {i} must be a dictionary")
            continue
        
        block_type = block.get("type")
        if not block_type:
            errors.append(f"Content block {i} missing 'type' field")
            continue
        
        # Validate specific block types
        if block_type == "text":
            if "text" not in block:
                errors.append(f"Text block {i} missing 'text' field")
            elif not block["text"]:
                errors.append(f"Text block {i} has empty text")
        
        elif block_type == "tool_use":
            if "name" not in block:
                errors.append(f"Tool use block {i} missing 'name' field")
            if "input" not in block:
                errors.append(f"Tool use block {i} missing 'input' field")
            if "id" not in block:
                errors.append(f"Tool use block {i} missing 'id' field")
        
        elif block_type == "tool_result":
            if "tool_use_id" not in block:
                errors.append(f"Tool result block {i} missing 'tool_use_id' field")
            if "content" not in block:
                errors.append(f"Tool result block {i} missing 'content' field")
        
        else:
            errors.append(f"Unknown content block type: {block_type}")
    
    return errors


def check_tool_usage_patterns(content_blocks: List[Dict[str, Any]]) -> List[str]:
    """Check for common tool usage pattern issues.
    
    Args:
        content_blocks: List of content block dictionaries
        
    Returns:
        List of warning messages about tool usage patterns
    """
    warnings = []
    
    tool_uses = [block for block in content_blocks if block.get("type") == "tool_use"]
    tool_results = [block for block in content_blocks if block.get("type") == "tool_result"]
    
    # Check for tool uses without IDs
    for tool_use in tool_uses:
        if not tool_use.get("id"):
            warnings.append("Tool use block missing ID - may cause orphaned tool issues")
    
    # Check for empty tool inputs
    for tool_use in tool_uses:
        if not tool_use.get("input"):
            warnings.append(f"Tool '{tool_use.get('name')}' has empty input")
    
    return warnings


def validate_messages_request_data(request: MessagesRequest) -> MessagesRequest:
    """Validate a MessagesRequest and return it if valid.
    
    Args:
        request: MessagesRequest to validate
        
    Returns:
        Validated MessagesRequest object
        
    Raises:
        ValueError: If validation fails
    """
    try:
        # Validate the request structure
        if not request:
            raise ValueError("Request cannot be None")
        
        if not request.messages:
            raise ValueError("Request must contain at least one message")
        
        # Validate each message
        validation_errors = []
        for i, message in enumerate(request.messages):
            validation_result = validate_message_data(message)
            if not validation_result["is_valid"]:
                validation_errors.extend([
                    f"Message {i}: {error}" for error in validation_result["errors"]
                ])
        
        # Check for validation errors
        if validation_errors:
            error_message = f"Request validation failed: {'; '.join(validation_errors)}"
            logger.error("Messages request validation failed",
                        error=error_message,
                        message_count=len(request.messages))
            raise ValueError(error_message)
        
        logger.info("Messages request validation completed successfully",
                   message_count=len(request.messages),
                   model=getattr(request, 'model', 'unknown'))
        
        return request
        
    except Exception as e:
        logger.error("Messages request validation failed", error=str(e), exc_info=True)
        raise ValueError(f"Request validation failed: {str(e)}")