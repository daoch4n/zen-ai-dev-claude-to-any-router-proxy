"""System operation flows for OpenRouter Anthropic Server.

Orchestrates system tool tasks with proper sequencing and safety checks.
Part of Phase 6A comprehensive refactoring - Tool Execution Workflows.
"""

import asyncio
from typing import Any, Dict, List

from prefect import flow

from ...services.tool_execution import ToolExecutionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager
from ...tasks.tools.system_tools import (
    execute_command_task,
    task_management_task
)

# Initialize logging and context management
logger = get_logger("system_operations")
context_manager = ContextManager()


@flow(name="system_operations")
async def system_operations_flow(
    tool_requests: List[Dict[str, Any]]
) -> List[ToolExecutionResult]:
    """
    Orchestrate system operations with proper safety and sequencing.
    
    Strategy:
    - Commands execute sequentially to avoid conflicts
    - Task management operations can run concurrently
    - Safety checks enforced at each step
    
    Args:
        tool_requests: List of tool request dictionaries
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting system operations flow", 
               request_count=len(tool_requests))
    
    # Categorize operations by type
    command_operations = []
    task_operations = []
    
    for request in tool_requests:
        tool_name = request.get('name', '').lower()
        if tool_name == 'bash':
            command_operations.append(request)
        elif tool_name == 'task':
            task_operations.append(request)
    
    results = []
    
    # Phase 1: Execute task management operations concurrently (safe)
    if task_operations:
        logger.info("Executing task management operations concurrently", 
                   count=len(task_operations))
        task_tasks = []
        for request in task_operations:
            task = task_management_task(
                tool_call_id=request.get('tool_call_id'),
                tool_name=request.get('name'),
                tool_input=request.get('input', {})
            )
            task_tasks.append(task)
        
        task_results = await asyncio.gather(*task_tasks, return_exceptions=True)
        results.extend(task_results)
    
    # Phase 2: Execute command operations sequentially (safety)
    if command_operations:
        logger.info("Executing command operations sequentially", 
                   count=len(command_operations))
        for request in command_operations:
            command = request.get('input', {}).get('command', '')
            logger.debug("Executing command", 
                        command=command[:100])  # Truncate for logging
            
            result = await execute_command_task(
                tool_call_id=request.get('tool_call_id'),
                tool_name=request.get('name'),
                tool_input=request.get('input', {})
            )
            results.append(result)
            
            # Log command execution status
            if isinstance(result, ToolExecutionResult):
                if result.success:
                    logger.info("Command executed successfully", 
                               command=command[:50])
                else:
                    logger.warning("Command execution failed", 
                                  command=command[:50],
                                  error=result.error)
    
    successful_operations = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("System operations flow completed", 
               total_operations=len(tool_requests),
               successful_operations=successful_operations)
    
    return results


@flow(name="command_pipeline")
async def command_pipeline_flow(
    commands: List[Dict[str, Any]],
    base_tool_call_id: str,
    fail_fast: bool = True
) -> List[ToolExecutionResult]:
    """
    Execute a pipeline of commands with dependency handling.
    
    Args:
        commands: List of command dictionaries with command, timeout, etc.
        base_tool_call_id: Base ID for generating unique tool call IDs
        fail_fast: Whether to stop on first failure
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting command pipeline", 
               command_count=len(commands),
               fail_fast=fail_fast)
    
    results = []
    
    for i, cmd_info in enumerate(commands):
        tool_call_id = f"{base_tool_call_id}_cmd_{i}"
        command = cmd_info.get('command', '')
        
        logger.info("Executing pipeline command", 
                   step=i+1,
                   total_steps=len(commands),
                   command=command[:100])
        
        result = await execute_command_task(
            tool_call_id=tool_call_id,
            tool_name="Bash",
            tool_input=cmd_info
        )
        results.append(result)
        
        # Check for failure
        if isinstance(result, ToolExecutionResult) and not result.success:
            logger.error("Command pipeline step failed", 
                        step=i+1,
                        command=command[:50],
                        error=result.error)
            
            if fail_fast:
                logger.warning("Stopping pipeline due to failure (fail_fast=True)")
                break
        else:
            logger.debug("Pipeline step completed successfully", 
                        step=i+1)
    
    successful_commands = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Command pipeline completed", 
               total_commands=len(commands),
               executed_commands=len(results),
               successful_commands=successful_commands)
    
    return results


@flow(name="task_management_batch")
async def task_management_batch_flow(
    task_operations: List[Dict[str, Any]]
) -> List[ToolExecutionResult]:
    """
    Execute multiple task management operations concurrently.
    
    Args:
        task_operations: List of task operation dictionaries
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting task management batch", 
               operation_count=len(task_operations))
    
    # Create concurrent task management operations
    task_tasks = []
    for operation in task_operations:
        task = task_management_task(
            tool_call_id=operation.get('tool_call_id'),
            tool_name=operation.get('name'),
            tool_input=operation.get('input', {})
        )
        task_tasks.append(task)
    
    # Execute all task operations concurrently
    results = await asyncio.gather(*task_tasks, return_exceptions=True)
    
    successful_operations = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Task management batch completed", 
               total_operations=len(task_operations),
               successful_operations=successful_operations)
    
    return results


@flow(name="safe_command_execution")
async def safe_command_execution_flow(
    command: str,
    tool_call_id: str,
    max_retries: int = 2,
    timeout: int = 30
) -> ToolExecutionResult:
    """
    Execute a single command with enhanced safety and retry logic.
    
    Args:
        command: Command to execute
        tool_call_id: Unique tool call identifier
        max_retries: Maximum number of retry attempts
        timeout: Command timeout in seconds
    
    Returns:
        ToolExecutionResult object
    """
    logger.info("Starting safe command execution", 
               command=command[:100],
               max_retries=max_retries,
               timeout=timeout)
    
    last_result = None
    
    for attempt in range(max_retries + 1):
        if attempt > 0:
            logger.info("Retrying command execution", 
                       attempt=attempt,
                       max_retries=max_retries)
        
        result = await execute_command_task(
            tool_call_id=f"{tool_call_id}_attempt_{attempt}",
            tool_name="Bash",
            tool_input={
                "command": command,
                "timeout": timeout,
                "description": f"Safe execution attempt {attempt + 1}"
            }
        )
        
        last_result = result
        
        # If successful, return immediately
        if isinstance(result, ToolExecutionResult) and result.success:
            logger.info("Command executed successfully", 
                       attempt=attempt,
                       command=command[:50])
            return result
        
        # Log failure and prepare for retry
        if isinstance(result, ToolExecutionResult):
            logger.warning("Command execution failed", 
                          attempt=attempt,
                          error=result.error,
                          will_retry=attempt < max_retries)
        
        # Don't sleep after the last attempt
        if attempt < max_retries:
            await asyncio.sleep(1)  # Brief delay before retry
    
    logger.error("Command execution failed after all retries", 
                command=command[:50],
                max_retries=max_retries)
    
    return last_result


@flow(name="interactive_command_session")
async def interactive_command_session_flow(
    commands_with_input: List[Dict[str, Any]],
    base_tool_call_id: str
) -> List[ToolExecutionResult]:
    """
    Execute commands that require interactive input.
    
    Args:
        commands_with_input: List of command dictionaries with stdin input
        base_tool_call_id: Base ID for generating unique tool call IDs
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting interactive command session", 
               command_count=len(commands_with_input))
    
    results = []
    
    for i, cmd_info in enumerate(commands_with_input):
        tool_call_id = f"{base_tool_call_id}_interactive_{i}"
        command = cmd_info.get('command', '')
        stdin_input = cmd_info.get('input', '')
        
        logger.info("Executing interactive command", 
                   step=i+1,
                   command=command[:100],
                   has_input=bool(stdin_input))
        
        result = await execute_command_task(
            tool_call_id=tool_call_id,
            tool_name="Bash",
            tool_input=cmd_info
        )
        results.append(result)
        
        if isinstance(result, ToolExecutionResult):
            if result.success:
                logger.debug("Interactive command completed", 
                           step=i+1)
            else:
                logger.warning("Interactive command failed", 
                              step=i+1,
                              error=result.error)
    
    successful_commands = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Interactive command session completed", 
               total_commands=len(commands_with_input),
               successful_commands=successful_commands)
    
    return results