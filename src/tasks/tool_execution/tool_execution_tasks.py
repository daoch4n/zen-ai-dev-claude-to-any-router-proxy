"""Tool execution core task functions."""

import asyncio
from typing import Any, Dict
from .tool_result_formatting_tasks import ToolExecutionResult
from ...core.logging_config import get_logger

logger = get_logger("tool_execution.execution")


# Exception classes for tool execution
class ToolExecutionError(Exception):
    """Base exception for tool execution errors"""
    pass


class ToolTimeoutError(ToolExecutionError):
    """Tool execution timed out"""
    pass


class ToolValidationError(ToolExecutionError):
    """Tool input validation failed"""
    pass


class ToolPermissionError(ToolExecutionError):
    """Tool execution permission denied"""
    pass


def validate_tool_input(tool_name: str, tool_input: Dict[str, Any]) -> bool:
    """Validate tool input parameters"""
    # Basic validation - can be extended per tool type
    if not isinstance(tool_input, dict):
        raise ToolValidationError(f"Tool input must be a dictionary, got {type(tool_input)}")
    
    # Add specific validation rules per tool type
    if tool_name == 'Write':
        if 'file_path' not in tool_input or 'content' not in tool_input:
            raise ToolValidationError("Write tool requires 'file_path' and 'content' parameters")
    elif tool_name == 'Read':
        if 'file_path' not in tool_input:
            raise ToolValidationError("Read tool requires 'file_path' parameter")
    elif tool_name == 'Bash':
        if 'command' not in tool_input:
            raise ToolValidationError("Bash tool requires 'command' parameter")
    
    return True


def check_tool_permissions(tool_name: str, tool_input: Dict[str, Any]) -> bool:
    """Check if tool execution is permitted"""
    # Basic permission checks
    if tool_name == 'Bash':
        command = tool_input.get('command', '')
        # Add security checks for dangerous commands
        dangerous_patterns = ['rm -rf /', 'format', 'del /q']
        for pattern in dangerous_patterns:
            if pattern in command.lower():
                raise ToolPermissionError(f"Command contains dangerous pattern: {pattern}")
    
    return True


async def execute_single_tool_with_timeout(
    tool_call_id: str,
    tool_name: str, 
    tool_input: Dict[str, Any],
    timeout: float = 30.0
) -> ToolExecutionResult:
    """Execute a single tool with timeout protection"""
    logger.info("Executing tool",
               tool_name=tool_name,
               tool_call_id=tool_call_id)
    
    try:
        # Validate input
        validate_tool_input(tool_name, tool_input)
        
        # Check permissions
        check_tool_permissions(tool_name, tool_input)
        
        # Import tool coordinator for actual execution
        from ...coordinators.tool_coordinator import tool_coordinator
        
        # Add timeout wrapper
        result = await asyncio.wait_for(
            tool_coordinator.execute_tool(tool_name, tool_call_id, tool_input),
            timeout=timeout
        )
        
        if result.success:
            logger.info("Tool completed successfully",
                       tool_name=tool_name,
                       execution_time=f"{result.execution_time:.2f}s")
        else:
            logger.warning("Tool execution failed",
                          tool_name=tool_name,
                          error=result.error)
        
        return result
        
    except asyncio.TimeoutError:
        error_msg = f"Tool execution timed out after {timeout}s"
        logger.error("Tool execution timed out",
                    tool_name=tool_name,
                    timeout=timeout,
                    error_msg=error_msg)
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=False,
            result=None,
            error=error_msg
        )
    except (ToolValidationError, ToolPermissionError) as e:
        logger.error("Tool validation/permission error",
                    tool_name=tool_name,
                    error=str(e))
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=False,
            result=None,
            error=str(e)
        )
    except Exception as e:
        error_msg = f"Tool execution error: {e}"
        logger.error("Tool execution error",
                    tool_name=tool_name,
                    error=str(e),
                    error_msg=error_msg,
                    exc_info=True)
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=False,
            result=None,
            error=error_msg
        )