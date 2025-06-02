"""Tool conversion tasks for converting between Anthropic and LiteLLM tool formats."""

from typing import Any, Dict, List, Union

from ...models.anthropic import Tool, Message
from ...core.logging_config import get_logger

logger = get_logger("conversion.tool")


def convert_anthropic_tool_to_litellm(tool: Tool) -> Dict[str, Any]:
    """Convert Anthropic tool to LiteLLM format."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": clean_openrouter_tool_schema(tool.input_schema)
        }
    }


def convert_anthropic_tool_choice_to_litellm(tool_choice: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
    """Convert Anthropic tool_choice to LiteLLM format."""
    if isinstance(tool_choice, dict):
        if tool_choice.get("type") == "auto":
            return "auto"
        elif tool_choice.get("type") == "any":
            return "required"
        elif tool_choice.get("type") == "tool":
            return {
                "type": "function",
                "function": {"name": tool_choice.get("name", "")}
            }
    
    return tool_choice


def convert_litellm_tool_to_anthropic(tool: Dict[str, Any]) -> Tool:
    """Convert LiteLLM tool to Anthropic format."""
    function = tool.get("function", {})
    
    return Tool(
        name=function.get("name", ""),
        description=function.get("description", ""),
        input_schema=function.get("parameters", {})
    )


def convert_litellm_tool_choice_to_anthropic(tool_choice: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Convert LiteLLM tool_choice to Anthropic format."""
    if isinstance(tool_choice, str):
        if tool_choice == "auto":
            return {"type": "auto"}
        elif tool_choice == "required":
            return {"type": "any"}
        elif tool_choice == "none":
            return {"type": "auto"}  # Default fallback
    
    elif isinstance(tool_choice, dict):
        if tool_choice.get("type") == "function":
            function = tool_choice.get("function", {})
            return {
                "type": "tool",
                "name": function.get("name", "")
            }
    
    # Default fallback
    return {"type": "auto"}


def clean_openrouter_tool_schema(schema: Any) -> Any:
    """
    Recursively removes unsupported fields from a JSON schema for OpenRouter compatibility.
    Based on the reference implementation from openrouter_anthropic_server.py
    """
    if isinstance(schema, dict):
        # Remove specific keys that might be unsupported by OpenRouter
        schema = schema.copy()  # Don't modify the original
        schema.pop("additionalProperties", None)
        schema.pop("default", None)
        schema.pop("$schema", None)  # Remove JSON schema metadata
        
        # Check for unsupported 'format' in string types
        if schema.get("type") == "string" and "format" in schema:
            allowed_formats = {"enum", "date-time"}  # Safe subset
            if schema["format"] not in allowed_formats:
                logger.debug("Removing unsupported format for string type in OpenRouter schema",
                            format_removed=schema["format"])
                schema.pop("format")
        
        # Recursively clean nested schemas
        for key, value in list(schema.items()):
            schema[key] = clean_openrouter_tool_schema(value)
    elif isinstance(schema, list):
        # Recursively clean items in a list
        return [clean_openrouter_tool_schema(item) for item in schema]
    
    return schema


def find_tool_name_for_id(messages: List[Message], tool_use_id: str) -> str:
    """Find the tool name for a given tool_use_id from previous messages."""
    logger.debug("Looking for tool name for ID", tool_use_id=tool_use_id)

    for i, msg in enumerate(messages):
        logger.debug("Checking message", message_index=i+1, role=msg.role)
        if isinstance(msg.content, list):
            for j, block in enumerate(msg.content):
                logger.debug("Checking content block", block_index=j+1, 
                           block_type=getattr(block, 'type', 'unknown'))
                if hasattr(block, 'type') and block.type == "tool_use":
                    block_id = getattr(block, 'id', '')
                    block_name = getattr(block, 'name', '')
                    logger.debug("Found tool_use block", 
                               block_id=block_id, 
                               block_name=block_name)
                    if block_id == tool_use_id:
                        logger.info("Found matching tool name", 
                                   tool_use_id=tool_use_id, 
                                   tool_name=block_name)
                        return block_name

    logger.warning("Tool name not found for ID", tool_use_id=tool_use_id)
    return "unknown_tool"


def extract_tool_calls_from_content(content: List[Any]) -> List[Dict[str, Any]]:
    """Extract tool calls from message content blocks."""
    tool_calls = []
    
    for block in content:
        if hasattr(block, 'type') and block.type == "tool_use":
            tool_call = {
                "id": getattr(block, 'id', ''),
                "type": "function", 
                "function": {
                    "name": getattr(block, 'name', ''),
                    "arguments": getattr(block, 'input', {})
                }
            }
            tool_calls.append(tool_call)
    
    return tool_calls


def extract_text_from_content(content: List[Any]) -> str:
    """Extract text content from message content blocks."""
    text_parts = []
    
    for block in content:
        if hasattr(block, 'type') and block.type == "text":
            text_parts.append(getattr(block, 'text', ''))
    
    return " ".join(text_parts)