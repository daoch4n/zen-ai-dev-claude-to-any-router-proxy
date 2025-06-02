"""Todo operation flows for OpenRouter Anthropic Server.

Orchestrates todo tool tasks with state management and atomic operations.
Part of Phase 6A comprehensive refactoring - Tool Execution Workflows.
"""

import asyncio
from typing import Any, Dict, List

from prefect import flow

from ...services.tool_execution import ToolExecutionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager
from ...tasks.tools.todo_tools import (
    read_todos_task,
    write_todos_task
)

# Initialize logging and context management
logger = get_logger("todo_operations")
context_manager = ContextManager()


@flow(name="todo_operations")
async def todo_operations_flow(
    tool_requests: List[Dict[str, Any]]
) -> List[ToolExecutionResult]:
    """
    Orchestrate todo operations with optimal concurrency and consistency.
    
    Strategy:
    - Read operations can run concurrently (read-only)
    - Write operations run sequentially per todo file (avoid conflicts)
    - Different todo files can be written concurrently
    
    Args:
        tool_requests: List of tool request dictionaries
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting todo operations flow", 
               request_count=len(tool_requests))
    
    # Categorize operations by type and todo file path
    read_operations = []
    write_operations = []
    
    for request in tool_requests:
        tool_name = request.get('name', '').lower()
        if tool_name == 'todoread':
            read_operations.append(request)
        elif tool_name == 'todowrite':
            write_operations.append(request)
    
    results = []
    
    # Execute all read operations concurrently (read-only, no conflicts)
    read_tasks = []
    for request in read_operations:
        task = read_todos_task(
            tool_call_id=request.get('tool_call_id'),
            tool_name=request.get('name'),
            tool_input=request.get('input', {})
        )
        read_tasks.append(task)
    
    if read_tasks:
        logger.info("Executing todo read operations concurrently", 
                   read_count=len(read_tasks))
        read_results = await asyncio.gather(*read_tasks, return_exceptions=True)
        results.extend(read_results)
    
    # Group write operations by todo file path for sequential execution
    write_by_path = {}
    for request in write_operations:
        path = request.get('input', {}).get('path', 'default.md')
        if path not in write_by_path:
            write_by_path[path] = []
        write_by_path[path].append(request)
    
    # Execute write operations: sequential per file, concurrent across files
    if write_by_path:
        logger.info("Executing todo write operations", 
                   file_count=len(write_by_path),
                   total_writes=len(write_operations))
        
        async def write_todo_sequence(path: str, requests: List[Dict[str, Any]]):
            """Execute write operations for a single todo file sequentially."""
            sequence_results = []
            for request in requests:
                result = await write_todos_task(
                    tool_call_id=request.get('tool_call_id'),
                    tool_name=request.get('name'),
                    tool_input=request.get('input', {})
                )
                sequence_results.append(result)
            return sequence_results
        
        # Create write sequence tasks (one per todo file)
        write_sequence_tasks = [
            write_todo_sequence(path, requests)
            for path, requests in write_by_path.items()
        ]
        
        # Execute write sequences concurrently across different files
        write_sequence_results = await asyncio.gather(*write_sequence_tasks, return_exceptions=True)
        
        # Flatten results
        for sequence_result in write_sequence_results:
            if isinstance(sequence_result, list):
                results.extend(sequence_result)
            else:
                results.append(sequence_result)
    
    successful_operations = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Todo operations flow completed", 
               total_operations=len(tool_requests),
               successful_operations=successful_operations)
    
    return results


@flow(name="batch_todo_read")
async def batch_todo_read_flow(
    todo_paths: List[str],
    base_tool_call_id: str,
    format_filter: str = None
) -> List[ToolExecutionResult]:
    """
    Read multiple todo files concurrently.
    
    Args:
        todo_paths: List of todo file paths
        base_tool_call_id: Base ID for generating unique tool call IDs
        format_filter: Optional format filter for todo items
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting batch todo read", 
               file_count=len(todo_paths),
               format_filter=format_filter)
    
    # Create read tasks for all todo files
    read_tasks = []
    for i, path in enumerate(todo_paths):
        tool_call_id = f"{base_tool_call_id}_read_{i}"
        
        tool_input = {"path": path}
        if format_filter:
            tool_input["format"] = format_filter
        
        task = read_todos_task(
            tool_call_id=tool_call_id,
            tool_name="TodoRead",
            tool_input=tool_input
        )
        read_tasks.append(task)
    
    # Execute all reads concurrently
    results = await asyncio.gather(*read_tasks, return_exceptions=True)
    
    successful_reads = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Batch todo read completed", 
               total_files=len(todo_paths),
               successful_reads=successful_reads)
    
    return results


@flow(name="todo_management_pipeline")
async def todo_management_pipeline_flow(
    todo_file_path: str,
    todo_operations: List[Dict[str, Any]],
    base_tool_call_id: str
) -> List[ToolExecutionResult]:
    """
    Execute a series of todo management operations on a single file.
    
    Args:
        todo_file_path: Path to the todo file
        todo_operations: List of todo operation dictionaries
        base_tool_call_id: Base ID for generating unique tool call IDs
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting todo management pipeline", 
               todo_file=todo_file_path,
               operation_count=len(todo_operations))
    
    results = []
    
    # Execute todo operations sequentially to maintain file consistency
    for i, operation in enumerate(todo_operations):
        tool_call_id = f"{base_tool_call_id}_op_{i}"
        
        # Determine operation type
        operation_type = operation.get('action', 'write')
        
        if operation_type == 'read':
            # Read operation
            tool_input = {
                "path": todo_file_path,
                **{k: v for k, v in operation.items() if k != 'action'}
            }
            
            result = await read_todos_task(
                tool_call_id=tool_call_id,
                tool_name="TodoRead",
                tool_input=tool_input
            )
        else:
            # Write operation (default)
            tool_input = {
                "path": todo_file_path,
                **{k: v for k, v in operation.items() if k != 'action'}
            }
            
            result = await write_todos_task(
                tool_call_id=tool_call_id,
                tool_name="TodoWrite",
                tool_input=tool_input
            )
        
        results.append(result)
        
        # Log operation result
        if result.success:
            logger.debug("Todo operation successful", 
                        operation_index=i,
                        operation_type=operation_type)
        else:
            logger.warning("Todo operation failed", 
                          operation_index=i,
                          operation_type=operation_type,
                          error=result.error)
            
            # Continue with remaining operations even on failure
            # (todo operations are generally independent)
    
    successful_operations = sum(1 for r in results if r.success)
    logger.info("Todo management pipeline completed", 
               total_operations=len(todo_operations),
               successful_operations=successful_operations)
    
    return results


@flow(name="todo_aggregation")
async def todo_aggregation_flow(
    todo_paths: List[str],
    base_tool_call_id: str,
    aggregation_format: str = "markdown"
) -> Dict[str, Any]:
    """
    Aggregate todos from multiple files and analyze them.
    
    Args:
        todo_paths: List of todo file paths
        base_tool_call_id: Base ID for generating unique tool call IDs
        aggregation_format: Format for aggregated output
    
    Returns:
        Dictionary with aggregated todo data and statistics
    """
    logger.info("Starting todo aggregation", 
               file_count=len(todo_paths),
               format=aggregation_format)
    
    # Read all todo files concurrently
    read_results = await batch_todo_read_flow(
        todo_paths=todo_paths,
        base_tool_call_id=f"{base_tool_call_id}_aggregation",
        format_filter=aggregation_format
    )
    
    # Aggregate and analyze todos
    aggregated_data = {
        "files_processed": len(todo_paths),
        "successful_reads": 0,
        "failed_reads": 0,
        "total_content_length": 0,
        "file_results": {},
        "aggregated_content": ""
    }
    
    for i, result in enumerate(read_results):
        if i >= len(todo_paths):
            continue
            
        path = todo_paths[i]
        
        if result.success:
            aggregated_data["successful_reads"] += 1
            content = str(result.content) if result.content else ""
            aggregated_data["total_content_length"] += len(content)
            aggregated_data["file_results"][path] = {
                "success": True,
                "content_length": len(content),
                "content": content
            }
            
            # Add to aggregated content
            if content:
                aggregated_data["aggregated_content"] += f"\n\n## {path}\n\n{content}"
        else:
            aggregated_data["failed_reads"] += 1
            aggregated_data["file_results"][path] = {
                "success": False,
                "error": result.error,
                "content": ""
            }
    
    logger.info("Todo aggregation completed", 
               files_processed=aggregated_data["files_processed"],
               successful_reads=aggregated_data["successful_reads"],
               total_content_length=aggregated_data["total_content_length"])
    
    return aggregated_data


@flow(name="batch_todo_update")
async def batch_todo_update_flow(
    update_specs: List[Dict[str, Any]],
    base_tool_call_id: str
) -> Dict[str, List[ToolExecutionResult]]:
    """
    Apply batch updates across multiple todo files.
    
    Args:
        update_specs: List of update specifications with path and operations
        base_tool_call_id: Base ID for generating unique tool call IDs
    
    Returns:
        Dictionary mapping todo file paths to their update results
    """
    logger.info("Starting batch todo update", 
               file_count=len(update_specs))
    
    # Group update specs by todo file path
    updates_by_path = {}
    for spec in update_specs:
        path = spec.get('path', 'default.md')
        if path not in updates_by_path:
            updates_by_path[path] = []
        updates_by_path[path].append(spec)
    
    async def update_todo_file(path: str, specs: List[Dict[str, Any]]):
        """Update a single todo file with multiple operations."""
        file_tool_call_id = f"{base_tool_call_id}_{path.replace('/', '_').replace('.', '_')}"
        
        # Extract operations from specs
        operations = []
        for spec in specs:
            operation = dict(spec)
            operation.pop('path', None)  # Remove path as it's handled separately
            operations.append(operation)
        
        # Use management pipeline for sequential operations on this file
        return await todo_management_pipeline_flow(
            todo_file_path=path,
            todo_operations=operations,
            base_tool_call_id=file_tool_call_id
        )
    
    # Create update tasks (one per todo file)
    update_tasks = [
        update_todo_file(path, specs)
        for path, specs in updates_by_path.items()
    ]
    
    # Execute updates concurrently across different files
    update_results = await asyncio.gather(*update_tasks, return_exceptions=True)
    
    # Map results back to paths
    file_update_results = {}
    path_list = list(updates_by_path.keys())
    
    for i, result in enumerate(update_results):
        if i < len(path_list):
            path = path_list[i]
            if isinstance(result, list):
                file_update_results[path] = result
                successful_updates = sum(1 for r in result if isinstance(r, ToolExecutionResult) and r.success)
                logger.debug("Todo file update completed", 
                           file_path=path,
                           total_operations=len(result),
                           successful_operations=successful_updates)
            else:
                logger.error("Todo file update failed", 
                           file_path=path,
                           error=str(result))
                file_update_results[path] = []
    
    total_operations = sum(len(results) for results in file_update_results.values())
    successful_operations = sum(
        sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
        for results in file_update_results.values()
    )
    
    logger.info("Batch todo update flow completed", 
               files_processed=len(file_update_results),
               total_operations=total_operations,
               successful_operations=successful_operations)
    
    return file_update_results


@flow(name="todo_synchronization")
async def todo_synchronization_flow(
    source_paths: List[str],
    target_path: str,
    base_tool_call_id: str,
    merge_strategy: str = "append"
) -> ToolExecutionResult:
    """
    Synchronize todos from multiple source files into a target file.
    
    Args:
        source_paths: List of source todo file paths
        target_path: Target todo file path
        base_tool_call_id: Base ID for generating unique tool call IDs
        merge_strategy: Strategy for merging todos (append, replace, merge)
    
    Returns:
        ToolExecutionResult for the synchronization operation
    """
    logger.info("Starting todo synchronization", 
               source_count=len(source_paths),
               target_path=target_path,
               merge_strategy=merge_strategy)
    
    # Read all source files
    source_results = await batch_todo_read_flow(
        todo_paths=source_paths,
        base_tool_call_id=f"{base_tool_call_id}_sync_read"
    )
    
    # Collect content from successful reads
    collected_content = []
    successful_sources = 0
    
    for i, result in enumerate(source_results):
        if i >= len(source_paths):
            continue
            
        source_path = source_paths[i]
        
        if result.success and result.content:
            collected_content.append(f"# From {source_path}\n\n{result.content}")
            successful_sources += 1
            logger.debug("Source todo file read successfully", 
                        source_path=source_path)
        else:
            logger.warning("Failed to read source todo file", 
                          source_path=source_path,
                          error=result.error if hasattr(result, 'error') else 'Unknown error')
    
    # Read target file if merge strategy requires it
    target_content = ""
    if merge_strategy in ["merge", "append"]:
        target_read_result = await read_todos_task(
            tool_call_id=f"{base_tool_call_id}_sync_target_read",
            tool_name="TodoRead",
            tool_input={"path": target_path}
        )
        
        if target_read_result.success and target_read_result.content:
            target_content = str(target_read_result.content)
    
    # Prepare synchronized content based on merge strategy
    if merge_strategy == "replace":
        synchronized_content = "\n\n".join(collected_content)
    elif merge_strategy == "append":
        all_content = [target_content] + collected_content if target_content else collected_content
        synchronized_content = "\n\n".join(all_content)
    elif merge_strategy == "merge":
        # Simple merge - could be enhanced with smart merging
        all_content = [target_content] + collected_content if target_content else collected_content
        synchronized_content = "\n\n".join(all_content)
    else:
        synchronized_content = "\n\n".join(collected_content)
    
    # Write synchronized content to target file
    sync_result = await write_todos_task(
        tool_call_id=f"{base_tool_call_id}_sync_write",
        tool_name="TodoWrite",
        tool_input={
            "path": target_path,
            "content": synchronized_content,
            "action": "write"
        }
    )
    
    logger.info("Todo synchronization completed", 
               successful_sources=successful_sources,
               target_path=target_path,
               sync_success=sync_result.success,
               merge_strategy=merge_strategy)
    
    return sync_result


@flow(name="todo_cleanup")
async def todo_cleanup_flow(
    todo_paths: List[str],
    base_tool_call_id: str,
    cleanup_rules: Dict[str, Any] = None
) -> Dict[str, ToolExecutionResult]:
    """
    Clean up todo files by removing completed items, duplicates, etc.
    
    Args:
        todo_paths: List of todo file paths to clean up
        base_tool_call_id: Base ID for generating unique tool call IDs
        cleanup_rules: Optional cleanup rules to apply
    
    Returns:
        Dictionary mapping file paths to cleanup results
    """
    logger.info("Starting todo cleanup", 
               file_count=len(todo_paths),
               has_rules=cleanup_rules is not None)
    
    # Default cleanup rules
    default_rules = {
        "remove_completed": True,
        "remove_duplicates": False,
        "sort_by_priority": False
    }
    
    rules = {**default_rules, **(cleanup_rules or {})}
    
    # Read all todo files first
    read_results = await batch_todo_read_flow(
        todo_paths=todo_paths,
        base_tool_call_id=f"{base_tool_call_id}_cleanup_read"
    )
    
    cleanup_results = {}
    
    # Process each file for cleanup
    for i, read_result in enumerate(read_results):
        if i >= len(todo_paths):
            continue
            
        path = todo_paths[i]
        
        if not read_result.success:
            cleanup_results[path] = read_result
            continue
        
        # Apply cleanup rules (simplified implementation)
        original_content = str(read_result.content) if read_result.content else ""
        cleaned_content = original_content
        
        try:
            # Simple cleanup logic - could be enhanced
            lines = cleaned_content.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Remove completed items (lines starting with - [x])
                if rules.get("remove_completed") and line.strip().startswith('- [x]'):
                    continue
                cleaned_lines.append(line)
            
            cleaned_content = '\n'.join(cleaned_lines)
            
            # Write cleaned content back
            cleanup_result = await write_todos_task(
                tool_call_id=f"{base_tool_call_id}_cleanup_write_{i}",
                tool_name="TodoWrite",
                tool_input={
                    "path": path,
                    "content": cleaned_content,
                    "action": "write"
                }
            )
            
            cleanup_results[path] = cleanup_result
            
            if cleanup_result.success:
                logger.debug("Todo cleanup successful", 
                           file_path=path,
                           original_length=len(original_content),
                           cleaned_length=len(cleaned_content))
            else:
                logger.warning("Todo cleanup failed", 
                             file_path=path,
                             error=cleanup_result.error)
        
        except Exception as e:
            logger.error("Todo cleanup error", 
                        file_path=path,
                        error=str(e))
            # Create error result
            cleanup_results[path] = ToolExecutionResult(
                success=False,
                content=None,
                error=f"Cleanup error: {str(e)}",
                tool_call_id=f"{base_tool_call_id}_cleanup_error_{i}",
                tool_name="TodoWrite"
            )
    
    successful_cleanups = sum(1 for r in cleanup_results.values() if r.success)
    logger.info("Todo cleanup flow completed", 
               total_files=len(todo_paths),
               successful_cleanups=successful_cleanups)
    
    return cleanup_results