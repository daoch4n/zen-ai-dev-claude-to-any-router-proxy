"""Message conversion tasks for converting between Anthropic and LiteLLM formats."""

from typing import Any, Dict, List, Union
import json

from ...models.anthropic import Message
from ...models.litellm import LiteLLMMessage
from ...core.logging_config import get_logger
from .content_conversion_tasks import (
    convert_image_content_anthropic_to_openai,
    convert_content_blocks_anthropic_to_openai,
    convert_content_blocks_openai_to_anthropic
)

logger = get_logger("conversion.message")


def extract_system_message_content(system: Union[str, List[Any]]) -> str:
    """Extract system message content from various formats."""
    if isinstance(system, str):
        return system
    
    elif isinstance(system, list):
        # Array of system content objects
        system_text_parts = []
        for content_item in system:
            if hasattr(content_item, 'text'):
                system_text_parts.append(content_item.text)
            elif isinstance(content_item, dict) and 'text' in content_item:
                system_text_parts.append(content_item['text'])
        
        return " ".join(system_text_parts)
    
    return str(system)


def convert_anthropic_message_to_litellm(message: Message, metadata: Dict[str, Any]) -> LiteLLMMessage:
    """Convert Anthropic message to LiteLLM format with enhanced multi-modal support."""
    if isinstance(message.content, str):
        # Simple text message
        return LiteLLMMessage(
            role=message.role,
            content=message.content
        )
    
    elif isinstance(message.content, list):
        # Complex message with content blocks (including images)
        text_parts = []
        tool_calls = []
        converted_content = []
        has_multimodal_content = False
        
        for block in message.content:
            if hasattr(block, 'type'):
                if block.type == "text":
                    text_content = getattr(block, 'text', '')
                    text_parts.append(text_content)
                    converted_content.append({
                        "type": "text",
                        "text": text_content
                    })
                
                elif block.type == "image":
                    # Convert image block to OpenAI format
                    image_content = convert_image_content_anthropic_to_openai(block.model_dump())
                    converted_content.append(image_content)
                    has_multimodal_content = True
                    metadata["image_conversions"] = metadata.get("image_conversions", 0) + 1
                    logger.debug("Converted image content block",
                               media_type=block.model_dump().get("source", {}).get("media_type", "unknown"))
                
                elif block.type == "tool_use":
                    tool_call = {
                        "id": getattr(block, 'id', ''),
                        "type": "function",
                        "function": {
                            "name": getattr(block, 'name', ''),
                            "arguments": json.dumps(getattr(block, 'input', {}))
                        }
                    }
                    tool_calls.append(tool_call)
                    metadata["content_block_conversions"] = metadata.get("content_block_conversions", 0) + 1
                
                elif block.type == "tool_result":
                    # Tool result blocks handled at higher level - convert to text for now
                    tool_id = getattr(block, 'tool_use_id', 'unknown')
                    content = getattr(block, 'content', '')
                    text_parts.append(f"Tool {tool_id} result: {content}")
                    converted_content.append({
                        "type": "text",
                        "text": f"Tool {tool_id} result: {content}"
                    })
        
        # Create LiteLLM message based on content type
        if has_multimodal_content or (len(converted_content) > 1 and not tool_calls):
            # Multi-modal content - use content array format
            return LiteLLMMessage(
                role=message.role,
                content=converted_content
            )
        
        elif message.role == "assistant" and tool_calls:
            # Assistant message with tool calls
            return LiteLLMMessage(
                role="assistant",
                content=" ".join(text_parts) if text_parts else None,
                tool_calls=tool_calls
            )
        
        else:
            # Regular text message
            content = " ".join(text_parts) if text_parts else ""
            return LiteLLMMessage(
                role=message.role,
                content=content
            )
    
    else:
        # Fallback for unknown content types
        return LiteLLMMessage(
            role=message.role,
            content=str(message.content)
        )


def convert_litellm_message_to_anthropic(litellm_message: LiteLLMMessage, metadata: Dict[str, Any]) -> Message:
    """Convert LiteLLM message to Anthropic format with enhanced multi-modal support."""
    # Extract role, ensuring it's valid for Anthropic
    role = litellm_message.role
    if role == "system":
        # System messages are handled separately in Anthropic format
        role = "assistant"
    
    # Convert content
    if hasattr(litellm_message, 'tool_calls') and litellm_message.tool_calls:
        # Message with tool calls
        content_blocks = []
        
        # Add text content if present
        if litellm_message.content:
            content_blocks.append({
                "type": "text",
                "text": litellm_message.content
            })
        
        # Add tool use blocks
        for tool_call in litellm_message.tool_calls:
            if hasattr(tool_call, 'function'):
                function = tool_call.function
                try:
                    # Parse arguments from JSON string
                    arguments = json.loads(function.arguments) if isinstance(function.arguments, str) else function.arguments
                except json.JSONDecodeError:
                    arguments = {}
                
                content_blocks.append({
                    "type": "tool_use",
                    "id": tool_call.id,
                    "name": function.name,
                    "input": arguments
                })
                metadata["tool_call_conversions"] = metadata.get("tool_call_conversions", 0) + 1
        
        return Message(role=role, content=content_blocks)
    
    elif isinstance(litellm_message.content, list):
        # Multi-modal content from OpenAI - convert back to Anthropic format
        converted_blocks = convert_content_blocks_openai_to_anthropic(litellm_message.content)
        metadata["multimodal_conversions"] = metadata.get("multimodal_conversions", 0) + 1
        return Message(role=role, content=converted_blocks)
    
    else:
        # Simple text message
        return Message(role=role, content=litellm_message.content or "")


def handle_tool_result_blocks(message: Message) -> List[str]:
    """Handle tool_result blocks in messages, converting them to text."""
    if not isinstance(message.content, list):
        return []
    
    text_parts = []
    for block in message.content:
        if hasattr(block, 'type'):
            if block.type == "text":
                text_parts.append(getattr(block, 'text', ''))
            elif block.type == "tool_result":
                # Convert tool_result to text representation
                tool_id = getattr(block, 'tool_use_id', 'unknown')
                content = getattr(block, 'content', '')
                
                if isinstance(content, list):
                    # Extract text from content blocks
                    result_text = []
                    for content_block in content:
                        if isinstance(content_block, dict) and content_block.get('type') == 'text':
                            result_text.append(content_block.get('text', ''))
                        elif hasattr(content_block, 'text'):
                            result_text.append(content_block.text)
                    content = " ".join(result_text)
                
                text_parts.append(f"Tool {tool_id} result: {content}")
    
    return text_parts


def create_system_message(system_content: str) -> LiteLLMMessage:
    """Create a system message in LiteLLM format."""
    return LiteLLMMessage(
        role="system",
        content=system_content
    )