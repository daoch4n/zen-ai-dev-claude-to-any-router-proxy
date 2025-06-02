"""Tool result formatting task functions."""

import json
from typing import Any, Dict
from dataclasses import dataclass
from ...core.logging_config import get_logger

logger = get_logger("tool_execution.formatting")


@dataclass
class ToolExecutionResult:
    """Result of executing a single tool"""
    tool_call_id: str
    tool_name: str
    success: bool
    result: Any
    error: str = None
    execution_time: float = 0.0
    requires_user_input: bool = False


def format_tool_result_content(result: ToolExecutionResult) -> str:
    """Format the result content for tool_result block"""
    if not result.success:
        return f"Error: {result.error}"
    
    if result.result is None:
        return "Tool executed successfully (no output)"
    
    if isinstance(result.result, str):
        return result.result
    elif isinstance(result.result, dict):
        return json.dumps(result.result, indent=2)
    elif isinstance(result.result, (list, tuple)):
        return "\n".join(str(item) for item in result.result)
    else:
        return str(result.result)


def truncate_result_content(content: str, max_length: int = 10000) -> str:
    """Truncate content if it exceeds maximum length"""
    if len(content) <= max_length:
        return content
    
    original_length = len(content)
    truncated_content = content[:max_length]
    truncated_content += f"\n\n[Content truncated - {original_length} total characters, showing first {max_length}]"
    
    logger.warning("Tool result truncated",
                  original_length=original_length,
                  max_length=max_length,
                  truncated_length=len(truncated_content))
    
    return truncated_content


def create_tool_result_block(result: ToolExecutionResult) -> Dict[str, Any]:
    """Create tool_result block for API response"""
    # Special handling for user input requests
    if result.requires_user_input:
        # Don't create tool_result for user questions - return as text block instead
        return {
            "type": "text",
            "text": f"Tool '{result.tool_name}' requires user input:\n\n{result.result}"
        }
    
    content = format_tool_result_content(result)
    
    # Limit content size to prevent API errors
    MAX_RESULT_LENGTH = 10000  # Reasonable limit for tool results
    content = truncate_result_content(content, MAX_RESULT_LENGTH)
    
    return {
        "type": "tool_result",
        "tool_use_id": result.tool_call_id,
        "content": content
    }