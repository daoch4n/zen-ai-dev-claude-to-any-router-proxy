"""Conversation continuation task functions."""

import json
from typing import Any, Dict, List
from .tool_result_formatting_tasks import ToolExecutionResult, create_tool_result_block
from ...models.anthropic import Message
from ...core.logging_config import get_logger

logger = get_logger("tool_execution.continuation")


def create_assistant_tool_use_message(tool_use_response: Any) -> Dict[str, Any]:
    """Create assistant message from tool_use response"""
    try:
        content = []
        
        if hasattr(tool_use_response, 'choices') and tool_use_response.choices:
            choice = tool_use_response.choices[0]
            
            # Extract text content
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                msg_content = choice.message.content
                
                if isinstance(msg_content, str):
                    if msg_content.strip():
                        content.append({"type": "text", "text": msg_content})
                elif isinstance(msg_content, list):
                    # If content is already a list of blocks, use as-is
                    for block in msg_content:
                        if isinstance(block, dict):
                            content.append(block)
            
            # Add tool_calls if present (from OpenAI format)
            if hasattr(choice, 'message') and hasattr(choice.message, 'tool_calls'):
                if choice.message.tool_calls:
                    for tool_call in choice.message.tool_calls:
                        content.append({
                            "type": "tool_use",
                            "id": tool_call.id,
                            "name": tool_call.function.name,
                            "input": json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                        })
        
        return {
            "role": "assistant",
            "content": content
        }
        
    except Exception as e:
        logger.error("Error creating assistant message",
                    error=str(e),
                    exc_info=True)
        return {
            "role": "assistant", 
            "content": [{"type": "text", "text": "Tool execution initiated"}]
        }


def create_user_tool_result_message(tool_results: List[ToolExecutionResult]) -> Dict[str, Any]:
    """Create user message with tool_result blocks"""
    content = []
    
    # Only process completed tools, skip user input requests
    completed_results = [result for result in tool_results if not result.requires_user_input]
    
    for result in completed_results:
        tool_result_block = create_tool_result_block(result)
        content.append(tool_result_block)
    
    # Ensure we have at least one tool result
    if not content:
        logger.warning("No tool results to send in continuation")
        # Add a dummy error result to prevent empty content
        content.append({
            "type": "tool_result",
            "tool_use_id": "error",
            "content": "No tool results available"
        })
    
    return {
        "role": "user",
        "content": content
    }


async def create_tool_result_messages(
    original_messages: List[Message],
    tool_use_response: Any,
    tool_results: List[ToolExecutionResult]
) -> List[Dict[str, Any]]:
    """
    Create the message sequence for continuing conversation:
    1. Current conversation messages (not original if cleaned)
    2. Assistant message with tool_use blocks
    3. User message with tool_result blocks
    """
    messages = []
    
    # Add current messages (which may have been cleaned)
    for msg in original_messages:
        messages.append(msg.model_dump())
    
    # Add assistant response with tool_use
    assistant_message = create_assistant_tool_use_message(tool_use_response)
    messages.append(assistant_message)
    
    # Add user response with tool_result
    user_message = create_user_tool_result_message(tool_results)
    messages.append(user_message)
    
    return messages