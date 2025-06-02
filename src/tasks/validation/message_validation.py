"""Message validation tasks for OpenRouter Anthropic Server.

Prefect tasks for validating message formats, content, and structure.
Part of Phase 6B comprehensive refactoring - Validation Tasks.
"""

from typing import Any, Dict, List, Optional

from prefect import task

from ...models.instructor import ConversionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager

# Initialize logging and context management
logger = get_logger("message_validation")
context_manager = ContextManager()


@task(name="validate_message_format")
async def validate_message_format_task(
    message_data: Dict[str, Any],
    expected_format: str = "anthropic"
) -> ConversionResult:
    """
    Validate message format for correctness and completeness.
    
    Args:
        message_data: Message data to validate
        expected_format: Expected format ("anthropic" or "litellm")
    
    Returns:
        ConversionResult with validation status
    """
    try:
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "format_info": {}
        }
        
        if expected_format == "anthropic":
            # Validate Anthropic message format
            required_fields = ["role", "content"]
            
            for field in required_fields:
                if field not in message_data:
                    validation_result["errors"].append(f"Missing required field: {field}")
                    validation_result["is_valid"] = False
            
            # Validate role
            if "role" in message_data:
                valid_roles = ["user", "assistant", "system"]
                if message_data["role"] not in valid_roles:
                    validation_result["errors"].append(f"Invalid role: {message_data['role']}")
                    validation_result["is_valid"] = False
            
            # Validate content structure
            if "content" in message_data:
                content = message_data["content"]
                
                if isinstance(content, str):
                    # Simple string content
                    if not content.strip():
                        validation_result["warnings"].append("Empty content string")
                    
                    validation_result["format_info"]["content_type"] = "string"
                    validation_result["format_info"]["content_length"] = len(content)
                
                elif isinstance(content, list):
                    # Block-based content
                    validation_result["format_info"]["content_type"] = "blocks"
                    validation_result["format_info"]["block_count"] = len(content)
                    
                    # Validate each block
                    for i, block in enumerate(content):
                        if not isinstance(block, dict):
                            validation_result["errors"].append(f"Content block {i} must be a dictionary")
                            validation_result["is_valid"] = False
                            continue
                        
                        if "type" not in block:
                            validation_result["errors"].append(f"Content block {i} missing type field")
                            validation_result["is_valid"] = False
                            continue
                        
                        block_type = block["type"]
                        if block_type == "text":
                            if "text" not in block:
                                validation_result["errors"].append(f"Text block {i} missing text field")
                                validation_result["is_valid"] = False
                        elif block_type == "tool_use":
                            required_tool_fields = ["id", "name", "input"]
                            for field in required_tool_fields:
                                if field not in block:
                                    validation_result["errors"].append(f"Tool use block {i} missing {field} field")
                                    validation_result["is_valid"] = False
                        elif block_type == "tool_result":
                            required_result_fields = ["tool_use_id", "content"]
                            for field in required_result_fields:
                                if field not in block:
                                    validation_result["errors"].append(f"Tool result block {i} missing {field} field")
                                    validation_result["is_valid"] = False
                        else:
                            validation_result["warnings"].append(f"Unknown block type in block {i}: {block_type}")
                
                else:
                    validation_result["errors"].append("Content must be string or list of blocks")
                    validation_result["is_valid"] = False
        
        elif expected_format == "litellm":
            # Validate LiteLLM message format
            required_fields = ["role", "content"]
            
            for field in required_fields:
                if field not in message_data:
                    validation_result["errors"].append(f"Missing required field: {field}")
                    validation_result["is_valid"] = False
            
            # Check for tool_calls if present
            if "tool_calls" in message_data:
                tool_calls = message_data["tool_calls"]
                if not isinstance(tool_calls, list):
                    validation_result["errors"].append("tool_calls must be a list")
                    validation_result["is_valid"] = False
                else:
                    for i, tool_call in enumerate(tool_calls):
                        if not isinstance(tool_call, dict):
                            validation_result["errors"].append(f"Tool call {i} must be a dictionary")
                            validation_result["is_valid"] = False
                            continue
                        
                        required_tool_fields = ["id", "type", "function"]
                        for field in required_tool_fields:
                            if field not in tool_call:
                                validation_result["errors"].append(f"Tool call {i} missing {field} field")
                                validation_result["is_valid"] = False
        
        else:
            validation_result["errors"].append(f"Unsupported validation format: {expected_format}")
            validation_result["is_valid"] = False
        
        # Add summary information
        validation_result["summary"] = {
            "total_errors": len(validation_result["errors"]),
            "total_warnings": len(validation_result["warnings"]),
            "is_valid": validation_result["is_valid"],
            "format": expected_format
        }
        
        logger.debug("Message format validation completed",
                    expected_format=expected_format,
                    is_valid=validation_result["is_valid"],
                    error_count=len(validation_result["errors"]),
                    warning_count=len(validation_result["warnings"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "validation_type": "message_format",
                "expected_format": expected_format,
                "is_valid": validation_result["is_valid"]
            }
        )
        
    except Exception as e:
        error_msg = f"Message format validation failed: {str(e)}"
        logger.error("Message format validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(name="validate_message_content")
async def validate_message_content_task(
    message_content: Any,
    content_rules: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate message content against specific rules.
    
    Args:
        message_content: Content to validate
        content_rules: Optional content validation rules
    
    Returns:
        ConversionResult with content validation status
    """
    try:
        if content_rules is None:
            content_rules = {}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "content_analysis": {}
        }
        
        # Analyze content structure
        if isinstance(message_content, str):
            content_length = len(message_content)
            word_count = len(message_content.split())
            
            validation_result["content_analysis"] = {
                "type": "string",
                "length": content_length,
                "word_count": word_count,
                "is_empty": not message_content.strip()
            }
            
            # Apply content rules
            max_length = content_rules.get("max_length", 100000)
            min_length = content_rules.get("min_length", 0)
            
            if content_length > max_length:
                validation_result["errors"].append(f"Content too long: {content_length} > {max_length}")
                validation_result["is_valid"] = False
            
            if content_length < min_length:
                validation_result["errors"].append(f"Content too short: {content_length} < {min_length}")
                validation_result["is_valid"] = False
            
            if not message_content.strip():
                validation_result["warnings"].append("Content is empty or whitespace only")
        
        elif isinstance(message_content, list):
            validation_result["content_analysis"] = {
                "type": "blocks",
                "block_count": len(message_content),
                "block_types": [block.get("type", "unknown") for block in message_content if isinstance(block, dict)]
            }
            
            # Validate block content
            total_text_length = 0
            for i, block in enumerate(message_content):
                if isinstance(block, dict):
                    block_type = block.get("type")
                    
                    if block_type == "text":
                        text = block.get("text", "")
                        total_text_length += len(text)
                        
                        if not text.strip():
                            validation_result["warnings"].append(f"Text block {i} is empty")
                    
                    elif block_type == "tool_use":
                        tool_name = block.get("name", "")
                        if not tool_name:
                            validation_result["errors"].append(f"Tool use block {i} missing tool name")
                            validation_result["is_valid"] = False
                    
                    elif block_type == "tool_result":
                        content = block.get("content", "")
                        if isinstance(content, str):
                            total_text_length += len(content)
            
            validation_result["content_analysis"]["total_text_length"] = total_text_length
            
            # Apply block-specific rules
            max_blocks = content_rules.get("max_blocks", 50)
            if len(message_content) > max_blocks:
                validation_result["errors"].append(f"Too many content blocks: {len(message_content)} > {max_blocks}")
                validation_result["is_valid"] = False
        
        else:
            validation_result["errors"].append(f"Invalid content type: {type(message_content)}")
            validation_result["is_valid"] = False
        
        # Check for potentially problematic content
        if content_rules.get("check_safety", False):
            safety_result = await _check_content_safety(message_content)
            if not safety_result["is_safe"]:
                validation_result["warnings"].extend(safety_result["warnings"])
        
        logger.debug("Message content validation completed",
                    content_type=validation_result["content_analysis"].get("type"),
                    is_valid=validation_result["is_valid"],
                    error_count=len(validation_result["errors"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "validation_type": "message_content",
                "content_type": validation_result["content_analysis"].get("type"),
                "is_valid": validation_result["is_valid"]
            }
        )
        
    except Exception as e:
        error_msg = f"Message content validation failed: {str(e)}"
        logger.error("Message content validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(name="validate_system_message")
async def validate_system_message_task(
    system_message: Any,
    validation_rules: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate system message format and content.
    
    Args:
        system_message: System message to validate
        validation_rules: Optional validation rules
    
    Returns:
        ConversionResult with system message validation status
    """
    try:
        if validation_rules is None:
            validation_rules = {}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "system_info": {}
        }
        
        if system_message is None:
            validation_result["system_info"]["has_system"] = False
            return ConversionResult(
                success=True,
                converted_data=validation_result,
                metadata={"validation_type": "system_message", "has_system": False}
            )
        
        validation_result["system_info"]["has_system"] = True
        
        if isinstance(system_message, str):
            validation_result["system_info"]["type"] = "string"
            validation_result["system_info"]["length"] = len(system_message)
            
            if not system_message.strip():
                validation_result["warnings"].append("System message is empty")
            
            # Check length limits
            max_length = validation_rules.get("max_system_length", 10000)
            if len(system_message) > max_length:
                validation_result["errors"].append(f"System message too long: {len(system_message)} > {max_length}")
                validation_result["is_valid"] = False
        
        elif isinstance(system_message, list):
            validation_result["system_info"]["type"] = "blocks"
            validation_result["system_info"]["block_count"] = len(system_message)
            
            # Validate system content blocks
            for i, block in enumerate(system_message):
                if not isinstance(block, dict):
                    validation_result["errors"].append(f"System block {i} must be a dictionary")
                    validation_result["is_valid"] = False
                    continue
                
                if "type" not in block:
                    validation_result["errors"].append(f"System block {i} missing type field")
                    validation_result["is_valid"] = False
                    continue
                
                if block["type"] == "text":
                    if "text" not in block:
                        validation_result["errors"].append(f"System text block {i} missing text field")
                        validation_result["is_valid"] = False
                else:
                    validation_result["warnings"].append(f"Unusual system block type: {block['type']}")
        
        else:
            validation_result["errors"].append(f"Invalid system message type: {type(system_message)}")
            validation_result["is_valid"] = False
        
        logger.debug("System message validation completed",
                    has_system=validation_result["system_info"]["has_system"],
                    system_type=validation_result["system_info"].get("type"),
                    is_valid=validation_result["is_valid"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "validation_type": "system_message",
                "has_system": validation_result["system_info"]["has_system"],
                "is_valid": validation_result["is_valid"]
            }
        )
        
    except Exception as e:
        error_msg = f"System message validation failed: {str(e)}"
        logger.error("System message validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(name="validate_tool_calls")
async def validate_tool_calls_task(
    tool_calls: List[Dict[str, Any]],
    available_tools: List[str] = None
) -> ConversionResult:
    """
    Validate tool calls in messages.
    
    Args:
        tool_calls: List of tool call dictionaries
        available_tools: Optional list of available tool names
    
    Returns:
        ConversionResult with tool calls validation status
    """
    try:
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "tool_call_info": {}
        }
        
        if not tool_calls:
            validation_result["tool_call_info"]["has_tool_calls"] = False
            return ConversionResult(
                success=True,
                converted_data=validation_result,
                metadata={"validation_type": "tool_calls", "has_tool_calls": False}
            )
        
        validation_result["tool_call_info"]["has_tool_calls"] = True
        validation_result["tool_call_info"]["call_count"] = len(tool_calls)
        
        tool_names = []
        tool_ids = []
        
        for i, tool_call in enumerate(tool_calls):
            if not isinstance(tool_call, dict):
                validation_result["errors"].append(f"Tool call {i} must be a dictionary")
                validation_result["is_valid"] = False
                continue
            
            # Validate required fields based on format
            if "type" in tool_call and tool_call["type"] == "tool_use":
                # Anthropic format
                required_fields = ["id", "name", "input"]
                for field in required_fields:
                    if field not in tool_call:
                        validation_result["errors"].append(f"Tool call {i} missing {field} field")
                        validation_result["is_valid"] = False
                
                if "name" in tool_call:
                    tool_names.append(tool_call["name"])
                if "id" in tool_call:
                    tool_ids.append(tool_call["id"])
            
            elif "function" in tool_call:
                # LiteLLM/OpenAI format
                required_fields = ["id", "type", "function"]
                for field in required_fields:
                    if field not in tool_call:
                        validation_result["errors"].append(f"Tool call {i} missing {field} field")
                        validation_result["is_valid"] = False
                
                if "function" in tool_call and isinstance(tool_call["function"], dict):
                    function = tool_call["function"]
                    if "name" not in function:
                        validation_result["errors"].append(f"Tool call {i} function missing name")
                        validation_result["is_valid"] = False
                    else:
                        tool_names.append(function["name"])
                
                if "id" in tool_call:
                    tool_ids.append(tool_call["id"])
            
            else:
                validation_result["errors"].append(f"Tool call {i} has unknown format")
                validation_result["is_valid"] = False
        
        # Check for duplicate tool call IDs
        if len(tool_ids) != len(set(tool_ids)):
            validation_result["errors"].append("Duplicate tool call IDs found")
            validation_result["is_valid"] = False
        
        # Validate tool names against available tools
        if available_tools:
            invalid_tools = [name for name in tool_names if name not in available_tools]
            if invalid_tools:
                validation_result["errors"].append(f"Unknown tools: {invalid_tools}")
                validation_result["is_valid"] = False
        
        validation_result["tool_call_info"]["tool_names"] = list(set(tool_names))
        validation_result["tool_call_info"]["unique_tools"] = len(set(tool_names))
        
        logger.debug("Tool calls validation completed",
                    call_count=len(tool_calls),
                    unique_tools=len(set(tool_names)),
                    is_valid=validation_result["is_valid"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "validation_type": "tool_calls",
                "call_count": len(tool_calls),
                "unique_tools": len(set(tool_names)),
                "is_valid": validation_result["is_valid"]
            }
        )
        
    except Exception as e:
        error_msg = f"Tool calls validation failed: {str(e)}"
        logger.error("Tool calls validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


async def _check_content_safety(content: Any) -> Dict[str, Any]:
    """Basic content safety check."""
    safety_result = {
        "is_safe": True,
        "warnings": []
    }
    
    # Convert content to string for analysis
    content_str = ""
    if isinstance(content, str):
        content_str = content
    elif isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        content_str = " ".join(text_parts)
    
    # Basic safety checks
    if len(content_str) > 100000:
        safety_result["warnings"].append("Content is very long")
    
    # Check for potential script content
    script_indicators = ["<script", "javascript:", "eval(", "exec("]
    for indicator in script_indicators:
        if indicator.lower() in content_str.lower():
            safety_result["warnings"].append(f"Potential script content detected: {indicator}")
    
    return safety_result