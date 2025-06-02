"""File operation flows for OpenRouter Anthropic Server.

Orchestrates file tool tasks with optimal concurrency and sequencing.
Part of Phase 6A comprehensive refactoring - Tool Execution Workflows.
"""

import asyncio
from typing import Any, Dict, List

from prefect import flow

from ...services.tool_execution import ToolExecutionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager
from ...tasks.tools.file_tools import (
    write_file_task,
    read_file_task,
    edit_file_task,
    multi_edit_file_task
)

# Initialize logging and context management
logger = get_logger("file_operations")
context_manager = ContextManager()


@flow(name="file_operations")
async def file_operations_flow(
    tool_requests: List[Dict[str, Any]]
) -> List[ToolExecutionResult]:
    """
    Orchestrate file operations with optimal concurrency.
    
    Strategy:
    - Concurrent reads (safe to parallelize)
    - Sequential writes to avoid conflicts
    - Edits run after writes complete
    
    Args:
        tool_requests: List of tool request dictionaries
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting file operations flow", 
               request_count=len(tool_requests))
    
    # Categorize operations by type for optimal execution strategy
    read_operations = []
    write_operations = []
    edit_operations = []
    multi_edit_operations = []
    
    for request in tool_requests:
        tool_name = request.get('name', '').lower()
        if tool_name == 'read':
            read_operations.append(request)
        elif tool_name == 'write':
            write_operations.append(request)
        elif tool_name == 'edit':
            edit_operations.append(request)
        elif tool_name == 'multiedit':
            multi_edit_operations.append(request)
    
    results = []
    
    # Phase 1: Execute all read operations concurrently (safe)
    if read_operations:
        logger.info("Executing read operations concurrently", 
                   count=len(read_operations))
        read_tasks = []
        for request in read_operations:
            task = read_file_task(
                tool_call_id=request.get('tool_call_id'),
                tool_name=request.get('name'),
                tool_input=request.get('input', {})
            )
            read_tasks.append(task)
        
        read_results = await asyncio.gather(*read_tasks, return_exceptions=True)
        results.extend(read_results)
    
    # Phase 2: Execute write operations sequentially (avoid file conflicts)
    if write_operations:
        logger.info("Executing write operations sequentially", 
                   count=len(write_operations))
        for request in write_operations:
            result = await write_file_task(
                tool_call_id=request.get('tool_call_id'),
                tool_name=request.get('name'),
                tool_input=request.get('input', {})
            )
            results.append(result)
    
    # Phase 3: Execute edit operations sequentially (after writes complete)
    if edit_operations:
        logger.info("Executing edit operations sequentially", 
                   count=len(edit_operations))
        for request in edit_operations:
            result = await edit_file_task(
                tool_call_id=request.get('tool_call_id'),
                tool_name=request.get('name'),
                tool_input=request.get('input', {})
            )
            results.append(result)
    
    # Phase 4: Execute multi-edit operations sequentially (complex edits)
    if multi_edit_operations:
        logger.info("Executing multi-edit operations sequentially", 
                   count=len(multi_edit_operations))
        for request in multi_edit_operations:
            result = await multi_edit_file_task(
                tool_call_id=request.get('tool_call_id'),
                tool_name=request.get('name'),
                tool_input=request.get('input', {})
            )
            results.append(result)
    
    logger.info("File operations flow completed", 
               total_operations=len(tool_requests),
               successful_operations=sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success))
    
    return results


@flow(name="bulk_file_read")
async def bulk_file_read_flow(
    file_paths: List[str],
    base_tool_call_id: str
) -> List[ToolExecutionResult]:
    """
    Optimized bulk file reading with concurrent execution.
    
    Args:
        file_paths: List of file paths to read
        base_tool_call_id: Base ID for generating unique tool call IDs
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting bulk file read flow", 
               file_count=len(file_paths))
    
    # Create concurrent read tasks
    read_tasks = []
    for i, file_path in enumerate(file_paths):
        tool_call_id = f"{base_tool_call_id}_{i}"
        task = read_file_task(
            tool_call_id=tool_call_id,
            tool_name="Read",
            tool_input={"file_path": file_path}
        )
        read_tasks.append(task)
    
    # Execute all reads concurrently
    results = await asyncio.gather(*read_tasks, return_exceptions=True)
    
    successful_reads = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Bulk file read flow completed", 
               total_files=len(file_paths),
               successful_reads=successful_reads)
    
    return results


@flow(name="safe_file_write_sequence")
async def safe_file_write_sequence_flow(
    write_operations: List[Dict[str, Any]]
) -> List[ToolExecutionResult]:
    """
    Safe sequential file writing to prevent conflicts.
    
    Args:
        write_operations: List of write operation dictionaries
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting safe file write sequence", 
               operation_count=len(write_operations))
    
    results = []
    
    # Execute writes one at a time to prevent conflicts
    for i, operation in enumerate(write_operations):
        logger.debug("Executing write operation", 
                    operation_index=i,
                    file_path=operation.get('input', {}).get('file_path'))
        
        result = await write_file_task(
            tool_call_id=operation.get('tool_call_id'),
            tool_name=operation.get('name'),
            tool_input=operation.get('input', {})
        )
        results.append(result)
        
        # If write failed, log but continue with remaining operations
        if not (isinstance(result, ToolExecutionResult) and result.success):
            logger.warning("Write operation failed, continuing with remaining operations",
                          operation_index=i,
                          error=getattr(result, 'error', 'Unknown error'))
    
    successful_writes = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Safe file write sequence completed", 
               total_operations=len(write_operations),
               successful_writes=successful_writes)
    
    return results


@flow(name="file_edit_chain")
async def file_edit_chain_flow(
    file_path: str,
    edit_operations: List[Dict[str, Any]],
    base_tool_call_id: str
) -> List[ToolExecutionResult]:
    """
    Chain multiple edit operations on a single file.
    
    Args:
        file_path: Path to the file to edit
        edit_operations: List of edit operations to apply
        base_tool_call_id: Base ID for generating unique tool call IDs
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting file edit chain", 
               file_path=file_path,
               edit_count=len(edit_operations))
    
    results = []
    
    # Apply edits sequentially to maintain order
    for i, edit_op in enumerate(edit_operations):
        tool_call_id = f"{base_tool_call_id}_edit_{i}"
        
        # Prepare edit input with file path
        edit_input = edit_op.copy()
        edit_input['file_path'] = file_path
        
        logger.debug("Applying edit operation", 
                    edit_index=i,
                    old_string=edit_input.get('old_string', '')[:50])
        
        result = await edit_file_task(
            tool_call_id=tool_call_id,
            tool_name="Edit",
            tool_input=edit_input
        )
        results.append(result)
        
        # If edit failed, stop the chain to prevent corruption
        if not (isinstance(result, ToolExecutionResult) and result.success):
            logger.error("Edit operation failed, stopping edit chain",
                        edit_index=i,
                        error=getattr(result, 'error', 'Unknown error'))
            break
    
    successful_edits = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("File edit chain completed", 
               total_edits=len(edit_operations),
               successful_edits=successful_edits)
    
    return results


@flow(name="atomic_file_batch")
async def atomic_file_batch_flow(
    batch_operations: List[Dict[str, Any]]
) -> List[ToolExecutionResult]:
    """
    Atomic batch file operations with rollback on failure.
    
    Executes a batch of file operations and rolls back all changes
    if any operation fails, ensuring data consistency.
    
    Args:
        batch_operations: List of file operation dictionaries
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting atomic file batch operation", 
               operation_count=len(batch_operations))
    
    results = []
    backup_info = []
    
    try:
        # Phase 1: Create backups for all files that will be modified
        for operation in batch_operations:
            tool_name = operation.get('name', '').lower()
            if tool_name in ['write', 'edit', 'multiedit']:
                file_path = operation.get('input', {}).get('file_path')
                if file_path:
                    # Create backup by reading current content
                    backup_result = await read_file_task(
                        tool_call_id=f"backup_{operation.get('tool_call_id')}",
                        tool_name="Read",
                        tool_input={"file_path": file_path}
                    )
                    backup_info.append({
                        'file_path': file_path,
                        'backup_result': backup_result,
                        'operation': operation
                    })
        
        # Phase 2: Execute all operations
        for operation in batch_operations:
            tool_name = operation.get('name', '').lower()
            
            if tool_name == 'read':
                result = await read_file_task(
                    tool_call_id=operation.get('tool_call_id'),
                    tool_name=operation.get('name'),
                    tool_input=operation.get('input', {})
                )
            elif tool_name == 'write':
                result = await write_file_task(
                    tool_call_id=operation.get('tool_call_id'),
                    tool_name=operation.get('name'),
                    tool_input=operation.get('input', {})
                )
            elif tool_name == 'edit':
                result = await edit_file_task(
                    tool_call_id=operation.get('tool_call_id'),
                    tool_name=operation.get('name'),
                    tool_input=operation.get('input', {})
                )
            elif tool_name == 'multiedit':
                result = await multi_edit_file_task(
                    tool_call_id=operation.get('tool_call_id'),
                    tool_name=operation.get('name'),
                    tool_input=operation.get('input', {})
                )
            else:
                result = ToolExecutionResult(
                    tool_call_id=operation.get('tool_call_id'),
                    tool_name=operation.get('name'),
                    success=False,
                    content="",
                    error=f"Unknown file operation: {tool_name}"
                )
            
            results.append(result)
            
            # If any operation fails, initiate rollback
            if not (isinstance(result, ToolExecutionResult) and result.success):
                logger.error("Operation failed in atomic batch, initiating rollback",
                           failed_operation=tool_name,
                           error=getattr(result, 'error', 'Unknown error'))
                
                # Rollback all modified files
                for backup in backup_info:
                    if isinstance(backup['backup_result'], ToolExecutionResult) and backup['backup_result'].success:
                        logger.info("Rolling back file", file_path=backup['file_path'])
                        await write_file_task(
                            tool_call_id=f"rollback_{backup['operation'].get('tool_call_id')}",
                            tool_name="Write",
                            tool_input={
                                "file_path": backup['file_path'],
                                "content": backup['backup_result'].content
                            }
                        )
                
                # Mark all operations as failed due to rollback
                for i in range(len(results)):
                    if isinstance(results[i], ToolExecutionResult) and results[i].success:
                        results[i] = ToolExecutionResult(
                            tool_call_id=results[i].tool_call_id,
                            tool_name=results[i].tool_name,
                            success=False,
                            content="",
                            error="Operation rolled back due to batch failure"
                        )
                
                break
        
        successful_operations = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
        logger.info("Atomic file batch operation completed", 
                   total_operations=len(batch_operations),
                   successful_operations=successful_operations)
        
        return results
        
    except Exception as e:
        logger.error("Unexpected error in atomic batch operation", 
                    error=str(e), exc_info=True)
        
        # Emergency rollback
        for backup in backup_info:
            if isinstance(backup['backup_result'], ToolExecutionResult) and backup['backup_result'].success:
                try:
                    await write_file_task(
                        tool_call_id=f"emergency_rollback_{backup['operation'].get('tool_call_id')}",
                        tool_name="Write",
                        tool_input={
                            "file_path": backup['file_path'],
                            "content": backup['backup_result'].content
                        }
                    )
                except Exception as rollback_error:
                    logger.error("Emergency rollback failed", 
                                file_path=backup['file_path'],
                                error=str(rollback_error))
        
        # Return error results for all operations
        error_results = []
        for operation in batch_operations:
            error_results.append(ToolExecutionResult(
                tool_call_id=operation.get('tool_call_id'),
                tool_name=operation.get('name'),
                success=False,
                content="",
                error=f"Atomic batch failed: {str(e)}"
            ))
        
        return error_results