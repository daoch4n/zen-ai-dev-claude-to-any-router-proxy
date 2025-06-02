"""Tool detection and validation task functions."""

import json
from typing import Any, Dict, List
from ...core.logging_config import get_logger

logger = get_logger("tool_execution.detection")


def detect_tool_use_blocks(response: Any) -> bool:
    """Check if LiteLLM response contains tool_use blocks"""
    try:
        # Handle different response formats
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            
            # Check message content for tool_use blocks
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                content = choice.message.content
                
                # Content can be string or list of blocks
                if isinstance(content, list):
                    return any(
                        isinstance(block, dict) and block.get('type') == 'tool_use'
                        for block in content
                    )
                
            # Check for tool_calls (OpenAI format)
            if hasattr(choice, 'message') and hasattr(choice.message, 'tool_calls'):
                return choice.message.tool_calls is not None and len(choice.message.tool_calls) > 0
            
            # Check stop reason
            if hasattr(choice, 'finish_reason') and choice.finish_reason == 'tool_calls':
                return True
            
        return False
        
    except Exception as e:
        logger.error("Error detecting tool use",
                    error=str(e),
                    exc_info=True)
        return False


def extract_tool_use_blocks(response: Any) -> List[Dict[str, Any]]:
    """Extract tool_use blocks from LiteLLM response"""
    tool_use_blocks = []
    
    try:
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                content = choice.message.content
                
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get('type') == 'tool_use':
                            tool_use_blocks.append(block)
            
            # Handle OpenAI-style tool_calls
            if hasattr(choice, 'message') and hasattr(choice.message, 'tool_calls'):
                if choice.message.tool_calls:
                    for tool_call in choice.message.tool_calls:
                        # Convert OpenAI format to Anthropic format
                        tool_use_block = {
                            "type": "tool_use",
                            "id": tool_call.id,
                            "name": tool_call.function.name,
                            "input": json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                        }
                        tool_use_blocks.append(tool_use_block)
        
        logger.debug("Extracted tool_use blocks", block_count=len(tool_use_blocks))
        return tool_use_blocks
        
    except Exception as e:
        logger.error("Error extracting tool use blocks",
                    error=str(e),
                    exc_info=True)
        return []


async def check_tools_need_confirmation(tool_use_blocks: List[Dict[str, Any]]) -> bool:
    """Check if any tools would require user confirmation before executing them"""
    for tool_block in tool_use_blocks:
        tool_name = tool_block.get('name', '')
        tool_input = tool_block.get('input', {})
        
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            user_confirmed = tool_input.get('user_confirmed', False)
            
            # Import the method from system_tools to check deletion confirmation
            from ...tasks.tools.system_tools import check_deletion_confirmation_task
            requires_confirmation = await check_deletion_confirmation_task(command)
            if requires_confirmation and not user_confirmed:
                return True
        
        # Add checks for other tools that might require confirmation here
        
    return False