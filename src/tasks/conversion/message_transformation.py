"""Message transformation tasks for OpenRouter Anthropic Server.

Prefect tasks for converting message content, tool calls, and system messages.
Part of Phase 6A comprehensive refactoring - Conversion Tasks.
"""

import json
from typing import Any, Dict, List, Optional, Union

from prefect import task

from ...models.anthropic import Message
from ...models.litellm import LiteLLMMessage
from ...models.instructor import ConversionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager

# Initialize logging and context management
logger = get_logger("message_transformation")
context_manager = ContextManager()


@task(name="convert_message_content")
async def convert_message_content_task(
    message_data: Dict[str, Any],
    conversion_metadata: Dict[str, Any] = None,
    target_format: str = "litellm"
) -> ConversionResult:
    """
    Convert message content between Anthropic and LiteLLM formats.
    
    Args:
        message_data: Message data to convert
        conversion_metadata: Metadata for tracking conversions
        target_format: Target format ("litellm" or "anthropic")
    
    Returns:
        ConversionResult with converted message
    """
    try:
        if conversion_metadata is None:
            conversion_metadata = {}
        
        if target_format == "litellm":
            return await _convert_anthropic_to_litellm_message(message_data, conversion_metadata)
        elif target_format == "anthropic":
            return await _convert_litellm_to_anthropic_message(message_data, conversion_metadata)
        else:
            raise ValueError(f"Unsupported target format: {target_format}")
            
    except Exception as e:
        error_msg = f"Message content conversion failed: {str(e)}"
        logger.error("Message conversion failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


async def _convert_anthropic_to_litellm_message(
    message_data: Dict[str, Any],
    metadata: Dict[str, Any]
) -> ConversionResult:
    """Convert Anthropic message to LiteLLM format."""
    message = Message(**message_data)
    
    if isinstance(message.content, str):
        # Simple text message
        converted_message = {
            "role": message.role,
            "content": message.content
        }
        
        return ConversionResult(
            success=True,
            converted_data=converted_message,
            metadata={"conversion_type": "simple_text"}
        )
    
    elif isinstance(message.content, list):
        # Complex message with content blocks
        text_parts = []
        tool_calls = []
        
        for block in message.content:
            if hasattr(block, 'type'):
                if block.type == "text":
                    text_parts.append(getattr(block, 'text', ''))
                
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
                    metadata["content_block_conversions"] += 1
        
        # Create LiteLLM message
        if message.role == "assistant" and tool_calls:
            converted_message = {
                "role": "assistant",
                "content": " ".join(text_parts) if text_parts else None,
                "tool_calls": tool_calls
            }
        else:
            content = " ".join(text_parts) if text_parts else ""
            converted_message = {
                "role": message.role,
                "content": content
            }
        
        return ConversionResult(
            success=True,
            converted_data=converted_message,
            metadata={
                "conversion_type": "complex_content",
                "text_parts": len(text_parts),
                "tool_calls": len(tool_calls)
            }
        )
    
    else:
        # Fallback for unknown content types
        converted_message = {
            "role": message.role,
            "content": str(message.content)
        }
        
        return ConversionResult(
            success=True,
            converted_data=converted_message,
            metadata={"conversion_type": "fallback"}
        )


async def _convert_litellm_to_anthropic_message(
    message_data: Dict[str, Any],
    metadata: Dict[str, Any]
) -> ConversionResult:
    """Convert LiteLLM message to Anthropic format."""
    message = LiteLLMMessage(**message_data)
    content_blocks = []
    
    # Add text content if present
    if message.content:
        content_blocks.append({
            "type": "text",
            "text": message.content
        })
    
    # Add tool calls if present
    if message.tool_calls:
        for tool_call in message.tool_calls:
            try:
                arguments = json.loads(tool_call["function"]["arguments"])
            except (json.JSONDecodeError, KeyError):
                arguments = {}
            
            content_blocks.append({
                "type": "tool_use",
                "id": tool_call.get("id", ""),
                "name": tool_call["function"]["name"],
                "input": arguments
            })
            metadata["tool_call_conversions"] += 1
    
    # Return appropriate content format
    if len(content_blocks) == 1 and content_blocks[0]["type"] == "text":
        # Simple text message
        converted_message = {
            "role": message.role,
            "content": content_blocks[0]["text"]
        }
    else:
        # Complex message with blocks
        converted_message = {
            "role": message.role,
            "content": content_blocks
        }
    
    return ConversionResult(
        success=True,
        converted_data=converted_message,
        metadata={
            "conversion_type": "litellm_to_anthropic",
            "content_blocks": len(content_blocks)
        }
    )


@task(name="extract_system_message")
async def extract_system_message_task(
    messages: List[Dict[str, Any]]
) -> ConversionResult:
    """
    Extract system messages from a list of messages.
    
    Args:
        messages: List of message dictionaries
    
    Returns:
        ConversionResult with system message content and filtered messages
    """
    try:
        system_messages = []
        regular_messages = []
        
        for msg in messages:
            if msg.get("role") == "system":
                system_messages.append(msg.get("content", ""))
            else:
                regular_messages.append(msg)
        
        # Combine system messages if multiple
        system_content = None
        if system_messages:
            system_content = " ".join(filter(None, system_messages))
        
        logger.info("System message extraction completed",
                   system_message_count=len(system_messages),
                   regular_message_count=len(regular_messages),
                   has_system_content=bool(system_content))
        
        return ConversionResult(
            success=True,
            converted_data={
                "system_message": system_content,
                "regular_messages": regular_messages
            },
            metadata={
                "system_message_count": len(system_messages),
                "regular_message_count": len(regular_messages)
            }
        )
        
    except Exception as e:
        error_msg = f"System message extraction failed: {str(e)}"
        logger.error("System message extraction failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(name="transform_tool_calls")
async def transform_tool_calls_task(
    tool_calls: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    target_format: str = "litellm"
) -> ConversionResult:
    """
    Transform tool calls between Anthropic and LiteLLM formats.
    
    Args:
        tool_calls: Tool calls to transform
        tool_choice: Tool choice to transform
        target_format: Target format ("litellm" or "anthropic")
    
    Returns:
        ConversionResult with transformed tool calls/choice
    """
    try:
        if tool_calls is not None:
            return await _transform_tool_calls(tool_calls, target_format)
        elif tool_choice is not None:
            return await _transform_tool_choice(tool_choice, target_format)
        else:
            return ConversionResult(
                success=False,
                errors=["No tool calls or tool choice provided"],
                converted_data=None
            )
            
    except Exception as e:
        error_msg = f"Tool transformation failed: {str(e)}"
        logger.error("Tool transformation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


async def _transform_tool_calls(
    tool_calls: List[Dict[str, Any]],
    target_format: str
) -> ConversionResult:
    """Transform tool calls between formats."""
    if target_format == "anthropic":
        # Convert LiteLLM tool calls to Anthropic tool_use blocks
        anthropic_blocks = []
        
        for tool_call in tool_calls:
            # Validate tool call structure
            if not tool_call.get('id') or not tool_call.get('function'):
                continue
            
            tool_content = {
                "type": "tool_use",
                "id": tool_call['id'],
                "name": tool_call['function']['name'],
            }
            
            # Parse tool arguments safely
            try:
                if 'arguments' in tool_call['function']:
                    tool_content["input"] = json.loads(tool_call['function']['arguments'])
                else:
                    tool_content["input"] = {}
            except (json.JSONDecodeError, TypeError):
                tool_content["input"] = {}
            
            anthropic_blocks.append(tool_content)
        
        return ConversionResult(
            success=True,
            converted_data=anthropic_blocks,
            metadata={"tool_calls_converted": len(anthropic_blocks)}
        )
    
    elif target_format == "litellm":
        # Convert Anthropic tool_use blocks to LiteLLM tool calls
        litellm_tool_calls = []
        
        for block in tool_calls:
            if block.get('type') == 'tool_use':
                tool_call = {
                    "id": block.get('id', ''),
                    "type": "function",
                    "function": {
                        "name": block.get('name', ''),
                        "arguments": json.dumps(block.get('input', {}))
                    }
                }
                litellm_tool_calls.append(tool_call)
        
        return ConversionResult(
            success=True,
            converted_data=litellm_tool_calls,
            metadata={"tool_calls_converted": len(litellm_tool_calls)}
        )
    
    else:
        raise ValueError(f"Unsupported target format: {target_format}")


async def _transform_tool_choice(
    tool_choice: Union[str, Dict[str, Any]],
    target_format: str
) -> ConversionResult:
    """Transform tool choice between formats."""
    if target_format == "litellm":
        # Convert Anthropic tool_choice to LiteLLM format
        if isinstance(tool_choice, dict):
            if tool_choice.get("type") == "auto":
                converted_choice = "auto"
            elif tool_choice.get("type") == "any":
                converted_choice = "required"
            elif tool_choice.get("type") == "tool":
                converted_choice = {
                    "type": "function",
                    "function": {"name": tool_choice.get("name", "")}
                }
            else:
                converted_choice = tool_choice
        else:
            converted_choice = tool_choice
    
    elif target_format == "anthropic":
        # Convert LiteLLM tool_choice to Anthropic format
        if isinstance(tool_choice, str):
            if tool_choice == "auto":
                converted_choice = {"type": "auto"}
            elif tool_choice == "required":
                converted_choice = {"type": "any"}
            else:
                converted_choice = {"type": "auto"}
        elif isinstance(tool_choice, dict):
            if tool_choice.get("type") == "function":
                converted_choice = {
                    "type": "tool",
                    "name": tool_choice.get("function", {}).get("name", "")
                }
            else:
                converted_choice = {"type": "auto"}
        else:
            converted_choice = {"type": "auto"}
    
    else:
        raise ValueError(f"Unsupported target format: {target_format}")
    
    return ConversionResult(
        success=True,
        converted_data=converted_choice,
        metadata={"tool_choice_transformed": True}
    )


@task(name="format_tool_results")
async def format_tool_results_task(
    tool_results: List[Dict[str, Any]],
    target_format: str = "anthropic"
) -> ConversionResult:
    """
    Format tool results for inclusion in messages.
    
    Args:
        tool_results: List of tool result dictionaries
        target_format: Target format for results
    
    Returns:
        ConversionResult with formatted tool results
    """
    try:
        if target_format == "anthropic":
            # Format as Anthropic tool_result blocks
            formatted_results = []
            
            for result in tool_results:
                tool_result_block = {
                    "type": "tool_result",
                    "tool_use_id": result.get("tool_call_id", ""),
                    "content": result.get("content", ""),
                }
                
                # Add error information if present
                if result.get("error"):
                    tool_result_block["is_error"] = True
                
                formatted_results.append(tool_result_block)
            
            return ConversionResult(
                success=True,
                converted_data=formatted_results,
                metadata={"results_formatted": len(formatted_results)}
            )
        
        elif target_format == "text":
            # Format as text for LiteLLM compatibility
            text_parts = []
            
            for result in tool_results:
                tool_name = result.get("tool_name", "unknown")
                content = result.get("content", "")
                error = result.get("error")
                
                if error:
                    text_parts.append(f"Tool {tool_name} error: {error}")
                else:
                    text_parts.append(f"Tool {tool_name} result: {content}")
            
            formatted_text = "\n\n".join(text_parts)
            
            return ConversionResult(
                success=True,
                converted_data=formatted_text,
                metadata={"results_formatted": len(tool_results)}
            )
        
        else:
            raise ValueError(f"Unsupported target format: {target_format}")
            
    except Exception as e:
        error_msg = f"Tool results formatting failed: {str(e)}"
        logger.error("Tool results formatting failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(name="find_tool_name_for_id")
async def find_tool_name_for_id_task(
    messages: List[Dict[str, Any]],
    tool_use_id: str
) -> ConversionResult:
    """
    Find the tool name for a given tool_use_id from previous messages.
    
    Args:
        messages: List of message dictionaries to search
        tool_use_id: Tool use ID to find
    
    Returns:
        ConversionResult with tool name
    """
    try:
        logger.debug("Looking for tool name for ID", tool_use_id=tool_use_id)
        
        for i, msg in enumerate(messages):
            logger.debug("Checking message", message_index=i+1, role=msg.get("role"))
            
            content = msg.get("content")
            if isinstance(content, list):
                for j, block in enumerate(content):
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        block_id = block.get("id")
                        block_name = block.get("name")
                        logger.debug("Found tool_use block", block_id=block_id, block_name=block_name)
                        
                        if block_id == tool_use_id:
                            logger.debug("Found matching tool name", tool_name=block_name)
                            return ConversionResult(
                                success=True,
                                converted_data=block_name,
                                metadata={"tool_name": block_name}
                            )
        
        # Fallback if not found
        logger.warning("Could not find tool name for ID", tool_use_id=tool_use_id)
        return ConversionResult(
            success=True,
            converted_data="unknown_tool",
            metadata={"tool_name": "unknown_tool", "fallback": True}
        )
        
    except Exception as e:
        error_msg = f"Tool name lookup failed: {str(e)}"
        logger.error("Tool name lookup failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )