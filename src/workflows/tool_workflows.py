"""
Tool execution workflows using Prefect orchestration.

This module contains tool-specific workflows that handle complex
tool execution sequences with proper context management.
"""

from typing import Dict, Any, List, Optional
from prefect import flow, task
from dataclasses import dataclass

from src.core.logging_config import get_logger
from src.services.tool_execution import ToolExecutionService
from src.tasks.tool_execution.tool_result_formatting_tasks import ToolExecutionResult
from src.services.context_manager import ContextManager

logger = get_logger(__name__)


@dataclass
class ToolSequenceResult:
    """Result of a tool execution sequence."""
    results: List[ToolExecutionResult]
    context: Any
    success: bool
    total_execution_time: float


@flow(name="execute_tool_sequence")
async def execute_tool_sequence(
    tool_blocks: List[Dict[str, Any]],
    conversation_context: Any,
    request_id: str
) -> ToolSequenceResult:
    """
    Execute a sequence of tools with proper context management and logging.
    
    This flow replaces the complex tool execution logic that was embedded
    in the monolithic router functions.
    """
    
    # Create flow-scoped logger with context
    flow_logger = logger.bind(
        flow_name="execute_tool_sequence",
        request_id=request_id,
        tool_count=len(tool_blocks)
    )
    
    flow_logger.info("Tool sequence execution started")
    
    results = []
    total_execution_time = 0.0
    
    try:
        for i, tool_block in enumerate(tool_blocks):
            # Create tool-specific context
            tool_logger = flow_logger.bind(
                tool_step=i + 1,
                tool_name=tool_block.get('name'),
                tool_call_id=tool_block.get('id')
            )
            
            tool_logger.info("Executing tool", tool_input=tool_block.get('input'))
            
            # Execute individual tool
            result = await execute_single_tool.submit(
                tool_block=tool_block,
                conversation_context=conversation_context,
                tool_step=i + 1
            )
            
            # Log result
            if result.success:
                tool_logger.info(
                    "Tool execution successful",
                    execution_time=result.execution_time,
                    result_preview=str(result.result)[:200] if result.result else None
                )
            else:
                tool_logger.error(
                    "Tool execution failed",
                    error=result.error,
                    execution_time=result.execution_time
                )
            
            results.append(result)
            total_execution_time += result.execution_time
            
            # Update conversation context with result
            await update_context_with_tool_result.submit(
                conversation_context, result
            )
        
        # Determine overall success
        successful_tools = sum(1 for r in results if r.success)
        overall_success = successful_tools == len(results)
        
        flow_logger.info(
            "Tool sequence execution completed",
            successful_tools=successful_tools,
            total_tools=len(results),
            total_execution_time=total_execution_time,
            overall_success=overall_success
        )
        
        return ToolSequenceResult(
            results=results,
            context=conversation_context,
            success=overall_success,
            total_execution_time=total_execution_time
        )
        
    except Exception as e:
        flow_logger.error(
            "Tool sequence execution failed",
            error=str(e),
            error_type=type(e).__name__,
            completed_tools=len(results)
        )
        
        return ToolSequenceResult(
            results=results,
            context=conversation_context,
            success=False,
            total_execution_time=total_execution_time
        )


@task(name="execute_single_tool")
async def execute_single_tool(
    tool_block: Dict[str, Any],
    conversation_context: Any,
    tool_step: int
) -> ToolExecutionResult:
    """Execute a single tool with proper context and error handling."""
    
    task_logger = logger.bind(
        task_name="execute_single_tool",
        tool_name=tool_block.get('name'),
        tool_call_id=tool_block.get('id'),
        tool_step=tool_step
    )
    
    task_logger.info("Single tool execution started")
    
    try:
        # Create tool execution context
        context_manager = ContextManager()
        tool_context = context_manager.create_tool_context(
            tool_name=tool_block.get('name'),
            tool_call_id=tool_block.get('id'),
            conversation_context=conversation_context
        )
        
        # Execute tool using the service
        tool_service = ToolExecutionService()
        result = await tool_service.execute_tool(
            tool_name=tool_block.get('name'),
            tool_input=tool_block.get('input', {}),
            tool_call_id=tool_block.get('id'),
            context=tool_context
        )
        
        task_logger.info(
            "Single tool execution completed",
            success=result.success,
            execution_time=result.execution_time
        )
        
        return result
        
    except Exception as e:
        task_logger.error(
            "Single tool execution failed",
            error=str(e),
            error_type=type(e).__name__
        )
        
        # Return error result
        from src.tasks.tool_execution.tool_result_formatting_tasks import ToolExecutionResult
        return ToolExecutionResult(
            tool_name=tool_block.get('name'),
            tool_call_id=tool_block.get('id'),
            success=False,
            result=None,
            error=str(e),
            execution_time=0.0
        )


@task(name="update_context_with_tool_result")
async def update_context_with_tool_result(
    conversation_context: Any,
    tool_result: ToolExecutionResult
) -> None:
    """Update conversation context with tool execution result."""
    
    task_logger = logger.bind(
        task_name="update_context_with_tool_result",
        tool_name=tool_result.tool_name,
        tool_success=tool_result.success
    )
    
    task_logger.debug("Updating context with tool result")
    
    # Add tool result to conversation context
    if hasattr(conversation_context, 'add_tool_result'):
        conversation_context.add_tool_result(tool_result)
    
    task_logger.debug("Context updated with tool result")


@flow(name="handle_tool_continuation")
async def handle_tool_continuation(
    initial_response: Any,
    conversation_context: Any,
    original_request: Any,
    request_id: str
) -> Any:
    """
    Handle tool continuation after initial tool execution.
    
    This flow manages the process of sending tool results back to the API
    and handling any follow-up tool executions.
    """
    
    flow_logger = logger.bind(
        flow_name="handle_tool_continuation",
        request_id=request_id
    )
    
    flow_logger.info("Tool continuation workflow started")
    
    current_response = initial_response
    max_iterations = 5  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        flow_logger.info(f"Tool continuation iteration {iteration}")
        
        # Check if current response needs tool execution
        has_tools = await detect_tools_in_response.submit(current_response)
        
        if not has_tools:
            flow_logger.info("No more tools detected, continuation complete")
            break
        
        # Extract tools and execute them
        tool_blocks = await extract_tool_blocks.submit(current_response)
        
        tool_result = await execute_tool_sequence.submit(
            tool_blocks=tool_blocks,
            conversation_context=conversation_context,
            request_id=request_id
        )
        
        # Send tool results back to API for next response
        next_response = await continue_conversation_with_tools.submit(
            tool_results=tool_result.results,
            conversation_context=conversation_context,
            original_request=original_request
        )
        
        current_response = next_response
    
    if iteration >= max_iterations:
        flow_logger.warning("Tool continuation reached maximum iterations")
    
    flow_logger.info("Tool continuation workflow completed")
    return current_response


@task(name="detect_tools_in_response")
async def detect_tools_in_response(response: Any) -> bool:
    """Detect if response contains tool use blocks."""
    
    task_logger = logger.bind(task_name="detect_tools_in_response")
    task_logger.debug("Detecting tools in response")
    
    # Tool detection logic would go here
    # TODO: Implement actual tool detection from response
    
    has_tools = False
    task_logger.debug("Tool detection completed", has_tools=has_tools)
    return has_tools


@task(name="extract_tool_blocks")
async def extract_tool_blocks(response: Any) -> List[Dict[str, Any]]:
    """Extract tool blocks from response."""
    
    task_logger = logger.bind(task_name="extract_tool_blocks")
    task_logger.debug("Extracting tool blocks from response")
    
    # Tool extraction logic would go here
    # TODO: Implement actual tool block extraction
    
    tool_blocks = []
    task_logger.debug("Tool block extraction completed", tool_count=len(tool_blocks))
    return tool_blocks


@task(name="continue_conversation_with_tools")
async def continue_conversation_with_tools(
    tool_results: List[ToolExecutionResult],
    conversation_context: Any,
    original_request: Any
) -> Any:
    """Continue conversation by sending tool results back to API."""
    
    task_logger = logger.bind(
        task_name="continue_conversation_with_tools",
        tool_result_count=len(tool_results)
    )
    
    task_logger.info("Continuing conversation with tool results")
    
    # Build continuation request with tool results
    # TODO: Implement conversation continuation logic
    
    task_logger.info("Conversation continuation completed")
    return None  # TODO: Return actual API response