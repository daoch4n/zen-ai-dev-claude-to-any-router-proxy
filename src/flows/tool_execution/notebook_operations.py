"""Notebook operation flows for OpenRouter Anthropic Server.

Orchestrates notebook tool tasks with cell-level operations and validation.
Part of Phase 6A comprehensive refactoring - Tool Execution Workflows.
"""

import asyncio
from typing import Any, Dict, List

from prefect import flow

from ...services.tool_execution import ToolExecutionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager
from ...tasks.tools.notebook_tools import (
    read_notebook_task,
    edit_notebook_task
)

# Initialize logging and context management
logger = get_logger("notebook_operations")
context_manager = ContextManager()


@flow(name="notebook_operations")
async def notebook_operations_flow(
    tool_requests: List[Dict[str, Any]]
) -> List[ToolExecutionResult]:
    """
    Orchestrate notebook operations with optimal concurrency.
    
    Strategy:
    - Read operations can run concurrently (read-only)
    - Edit operations run sequentially per notebook (avoid conflicts)
    - Different notebooks can be edited concurrently
    
    Args:
        tool_requests: List of tool request dictionaries
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting notebook operations flow", 
               request_count=len(tool_requests))
    
    # Categorize operations by type and notebook path
    read_operations = []
    edit_operations = []
    
    for request in tool_requests:
        tool_name = request.get('name', '').lower()
        if tool_name == 'notebookread':
            read_operations.append(request)
        elif tool_name == 'notebookedit':
            edit_operations.append(request)
    
    results = []
    
    # Execute all read operations concurrently (read-only, no conflicts)
    read_tasks = []
    for request in read_operations:
        task = read_notebook_task(
            tool_call_id=request.get('tool_call_id'),
            tool_name=request.get('name'),
            tool_input=request.get('input', {})
        )
        read_tasks.append(task)
    
    if read_tasks:
        logger.info("Executing notebook read operations concurrently", 
                   read_count=len(read_tasks))
        read_results = await asyncio.gather(*read_tasks, return_exceptions=True)
        results.extend(read_results)
    
    # Group edit operations by notebook path for sequential execution
    edit_by_path = {}
    for request in edit_operations:
        path = request.get('input', {}).get('path', 'unknown')
        if path not in edit_by_path:
            edit_by_path[path] = []
        edit_by_path[path].append(request)
    
    # Execute edit operations: sequential per notebook, concurrent across notebooks
    if edit_by_path:
        logger.info("Executing notebook edit operations", 
                   notebook_count=len(edit_by_path),
                   total_edits=len(edit_operations))
        
        async def edit_notebook_sequence(path: str, requests: List[Dict[str, Any]]):
            """Execute edit operations for a single notebook sequentially."""
            sequence_results = []
            for request in requests:
                result = await edit_notebook_task(
                    tool_call_id=request.get('tool_call_id'),
                    tool_name=request.get('name'),
                    tool_input=request.get('input', {})
                )
                sequence_results.append(result)
            return sequence_results
        
        # Create edit sequence tasks (one per notebook)
        edit_sequence_tasks = [
            edit_notebook_sequence(path, requests)
            for path, requests in edit_by_path.items()
        ]
        
        # Execute edit sequences concurrently across different notebooks
        edit_sequence_results = await asyncio.gather(*edit_sequence_tasks, return_exceptions=True)
        
        # Flatten results
        for sequence_result in edit_sequence_results:
            if isinstance(sequence_result, list):
                results.extend(sequence_result)
            else:
                results.append(sequence_result)
    
    successful_operations = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Notebook operations flow completed", 
               total_operations=len(tool_requests),
               successful_operations=successful_operations)
    
    return results


@flow(name="batch_notebook_read")
async def batch_notebook_read_flow(
    notebook_paths: List[str],
    base_tool_call_id: str,
    include_outputs: bool = True
) -> List[ToolExecutionResult]:
    """
    Read multiple notebooks concurrently.
    
    Args:
        notebook_paths: List of notebook file paths
        base_tool_call_id: Base ID for generating unique tool call IDs
        include_outputs: Whether to include cell outputs in read
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting batch notebook read", 
               notebook_count=len(notebook_paths),
               include_outputs=include_outputs)
    
    # Create read tasks for all notebooks
    read_tasks = []
    for i, path in enumerate(notebook_paths):
        tool_call_id = f"{base_tool_call_id}_read_{i}"
        task = read_notebook_task(
            tool_call_id=tool_call_id,
            tool_name="NotebookRead",
            tool_input={
                "path": path,
                "include_outputs": include_outputs
            }
        )
        read_tasks.append(task)
    
    # Execute all reads concurrently
    results = await asyncio.gather(*read_tasks, return_exceptions=True)
    
    successful_reads = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Batch notebook read completed", 
               total_notebooks=len(notebook_paths),
               successful_reads=successful_reads)
    
    return results


@flow(name="notebook_cell_pipeline")
async def notebook_cell_pipeline_flow(
    notebook_path: str,
    cell_operations: List[Dict[str, Any]],
    base_tool_call_id: str
) -> List[ToolExecutionResult]:
    """
    Execute a series of cell operations on a single notebook.
    
    Args:
        notebook_path: Path to the notebook file
        cell_operations: List of cell operation dictionaries
        base_tool_call_id: Base ID for generating unique tool call IDs
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting notebook cell pipeline", 
               notebook_path=notebook_path,
               operation_count=len(cell_operations))
    
    results = []
    
    # Execute cell operations sequentially to maintain consistency
    for i, operation in enumerate(cell_operations):
        tool_call_id = f"{base_tool_call_id}_cell_{i}"
        
        # Prepare tool input
        tool_input = {
            "path": notebook_path,
            **operation
        }
        
        # Execute the cell operation
        result = await edit_notebook_task(
            tool_call_id=tool_call_id,
            tool_name="NotebookEdit",
            tool_input=tool_input
        )
        
        results.append(result)
        
        # Log operation result
        if result.success:
            logger.debug("Cell operation successful", 
                        operation_index=i,
                        operation_type=operation.get('action', 'unknown'))
        else:
            logger.warning("Cell operation failed", 
                          operation_index=i,
                          operation_type=operation.get('action', 'unknown'),
                          error=result.error)
            
            # Stop pipeline on first failure to maintain notebook consistency
            logger.error("Stopping cell pipeline due to failure", 
                        failed_operation=i,
                        remaining_operations=len(cell_operations) - i - 1)
            break
    
    successful_operations = sum(1 for r in results if r.success)
    logger.info("Notebook cell pipeline completed", 
               total_operations=len(cell_operations),
               successful_operations=successful_operations,
               completed_operations=len(results))
    
    return results


@flow(name="notebook_analysis")
async def notebook_analysis_flow(
    notebook_paths: List[str],
    base_tool_call_id: str,
    analysis_type: str = "structure"
) -> Dict[str, ToolExecutionResult]:
    """
    Analyze multiple notebooks to extract structure and metadata.
    
    Args:
        notebook_paths: List of notebook file paths
        base_tool_call_id: Base ID for generating unique tool call IDs
        analysis_type: Type of analysis to perform
    
    Returns:
        Dictionary mapping notebook paths to analysis results
    """
    logger.info("Starting notebook analysis", 
               notebook_count=len(notebook_paths),
               analysis_type=analysis_type)
    
    # Read all notebooks concurrently for analysis
    read_results = await batch_notebook_read_flow(
        notebook_paths=notebook_paths,
        base_tool_call_id=f"{base_tool_call_id}_analysis",
        include_outputs=(analysis_type == "full")
    )
    
    # Map results back to paths
    analysis_results = {}
    for i, result in enumerate(read_results):
        if i < len(notebook_paths):
            path = notebook_paths[i]
            analysis_results[path] = result
            
            if result.success:
                logger.debug("Notebook analysis successful", 
                           notebook_path=path,
                           analysis_type=analysis_type)
            else:
                logger.warning("Notebook analysis failed", 
                             notebook_path=path,
                             error=result.error)
    
    successful_analyses = sum(1 for r in analysis_results.values() if r.success)
    logger.info("Notebook analysis completed", 
               total_notebooks=len(notebook_paths),
               successful_analyses=successful_analyses)
    
    return analysis_results


@flow(name="notebook_batch_edit")
async def notebook_batch_edit_flow(
    edit_specs: List[Dict[str, Any]],
    base_tool_call_id: str
) -> Dict[str, List[ToolExecutionResult]]:
    """
    Apply batch edits across multiple notebooks.
    
    Args:
        edit_specs: List of edit specifications with path and operations
        base_tool_call_id: Base ID for generating unique tool call IDs
    
    Returns:
        Dictionary mapping notebook paths to their edit results
    """
    logger.info("Starting notebook batch edit", 
               notebook_count=len(edit_specs))
    
    # Group edit specs by notebook path
    edit_by_path = {}
    for spec in edit_specs:
        path = spec.get('path')
        if not path:
            logger.warning("Edit spec missing path", spec=spec)
            continue
            
        if path not in edit_by_path:
            edit_by_path[path] = []
        edit_by_path[path].append(spec)
    
    async def edit_notebook_batch(path: str, specs: List[Dict[str, Any]]):
        """Edit a single notebook with multiple operations."""
        notebook_tool_call_id = f"{base_tool_call_id}_{path.replace('/', '_')}"
        
        # Extract operations from specs
        operations = []
        for spec in specs:
            operation = dict(spec)
            operation.pop('path', None)  # Remove path as it's handled separately
            operations.append(operation)
        
        # Use cell pipeline for sequential operations on this notebook
        return await notebook_cell_pipeline_flow(
            notebook_path=path,
            cell_operations=operations,
            base_tool_call_id=notebook_tool_call_id
        )
    
    # Create batch edit tasks (one per notebook)
    batch_edit_tasks = [
        edit_notebook_batch(path, specs)
        for path, specs in edit_by_path.items()
    ]
    
    # Execute batch edits concurrently across different notebooks
    batch_results = await asyncio.gather(*batch_edit_tasks, return_exceptions=True)
    
    # Map results back to paths
    edit_results = {}
    path_list = list(edit_by_path.keys())
    
    for i, result in enumerate(batch_results):
        if i < len(path_list):
            path = path_list[i]
            if isinstance(result, list):
                edit_results[path] = result
                successful_edits = sum(1 for r in result if isinstance(r, ToolExecutionResult) and r.success)
                logger.debug("Notebook batch edit completed", 
                           notebook_path=path,
                           total_operations=len(result),
                           successful_operations=successful_edits)
            else:
                logger.error("Notebook batch edit failed", 
                           notebook_path=path,
                           error=str(result))
                edit_results[path] = []
    
    total_operations = sum(len(results) for results in edit_results.values())
    successful_operations = sum(
        sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
        for results in edit_results.values()
    )
    
    logger.info("Notebook batch edit flow completed", 
               notebooks_processed=len(edit_results),
               total_operations=total_operations,
               successful_operations=successful_operations)
    
    return edit_results


@flow(name="notebook_validation")
async def notebook_validation_flow(
    notebook_paths: List[str],
    base_tool_call_id: str,
    validation_rules: Dict[str, Any] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Validate notebook structure and content.
    
    Args:
        notebook_paths: List of notebook file paths
        base_tool_call_id: Base ID for generating unique tool call IDs
        validation_rules: Optional validation rules to apply
    
    Returns:
        Dictionary mapping notebook paths to validation results
    """
    logger.info("Starting notebook validation", 
               notebook_count=len(notebook_paths),
               has_rules=validation_rules is not None)
    
    # Read all notebooks for validation
    read_results = await batch_notebook_read_flow(
        notebook_paths=notebook_paths,
        base_tool_call_id=f"{base_tool_call_id}_validation",
        include_outputs=True
    )
    
    validation_results = {}
    
    for i, result in enumerate(read_results):
        if i >= len(notebook_paths):
            continue
            
        path = notebook_paths[i]
        
        if not result.success:
            validation_results[path] = {
                "valid": False,
                "errors": [f"Failed to read notebook: {result.error}"],
                "warnings": []
            }
            continue
        
        # Basic validation - check if notebook content is valid
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "stats": {}
        }
        
        try:
            # Basic structure validation
            if not result.content:
                validation["valid"] = False
                validation["errors"].append("Empty notebook content")
            else:
                # Count cells, validate structure, etc.
                # This is a simplified validation - could be enhanced
                validation["stats"]["content_length"] = len(str(result.content))
                
                # Apply custom validation rules if provided
                if validation_rules:
                    # Custom validation logic would go here
                    logger.debug("Applying custom validation rules", 
                               notebook_path=path,
                               rules=list(validation_rules.keys()))
        
        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"Validation error: {str(e)}")
        
        validation_results[path] = validation
        
        logger.debug("Notebook validation completed", 
                   notebook_path=path,
                   valid=validation["valid"],
                   error_count=len(validation["errors"]),
                   warning_count=len(validation["warnings"]))
    
    valid_notebooks = sum(1 for v in validation_results.values() if v.get("valid", False))
    logger.info("Notebook validation flow completed", 
               total_notebooks=len(notebook_paths),
               valid_notebooks=valid_notebooks)
    
    return validation_results