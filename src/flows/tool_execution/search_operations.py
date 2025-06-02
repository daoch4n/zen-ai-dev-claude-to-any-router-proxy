"""Search operation flows for OpenRouter Anthropic Server.

Orchestrates search tool tasks with optimal concurrency and result aggregation.
Part of Phase 6A comprehensive refactoring - Tool Execution Workflows.
"""

import asyncio
from typing import Any, Dict, List

from prefect import flow

from ...services.tool_execution import ToolExecutionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager
from ...tasks.tools.search_tools import (
    glob_search_task,
    grep_search_task,
    list_directory_task
)

# Initialize logging and context management
logger = get_logger("search_operations")
context_manager = ContextManager()


@flow(name="search_operations")
async def search_operations_flow(
    tool_requests: List[Dict[str, Any]]
) -> List[ToolExecutionResult]:
    """
    Orchestrate search operations with optimal concurrency.
    
    Strategy:
    - All search operations are read-only and can run concurrently
    - Directory listings execute first (fastest)
    - Glob and grep searches run in parallel
    
    Args:
        tool_requests: List of tool request dictionaries
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting search operations flow", 
               request_count=len(tool_requests))
    
    # Categorize operations by type
    glob_operations = []
    grep_operations = []
    ls_operations = []
    
    for request in tool_requests:
        tool_name = request.get('name', '').lower()
        if tool_name == 'glob':
            glob_operations.append(request)
        elif tool_name == 'grep':
            grep_operations.append(request)
        elif tool_name == 'ls':
            ls_operations.append(request)
    
    results = []
    
    # Execute all search operations concurrently (all read-only)
    all_tasks = []
    
    # Add directory listing tasks
    for request in ls_operations:
        task = list_directory_task(
            tool_call_id=request.get('tool_call_id'),
            tool_name=request.get('name'),
            tool_input=request.get('input', {})
        )
        all_tasks.append(task)
    
    # Add glob search tasks
    for request in glob_operations:
        task = glob_search_task(
            tool_call_id=request.get('tool_call_id'),
            tool_name=request.get('name'),
            tool_input=request.get('input', {})
        )
        all_tasks.append(task)
    
    # Add grep search tasks
    for request in grep_operations:
        task = grep_search_task(
            tool_call_id=request.get('tool_call_id'),
            tool_name=request.get('name'),
            tool_input=request.get('input', {})
        )
        all_tasks.append(task)
    
    # Execute all search operations concurrently
    if all_tasks:
        logger.info("Executing all search operations concurrently", 
                   total_tasks=len(all_tasks),
                   glob_count=len(glob_operations),
                   grep_count=len(grep_operations),
                   ls_count=len(ls_operations))
        
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
    
    successful_operations = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Search operations flow completed", 
               total_operations=len(tool_requests),
               successful_operations=successful_operations)
    
    return results


@flow(name="comprehensive_search")
async def comprehensive_search_flow(
    search_pattern: str,
    search_paths: List[str],
    base_tool_call_id: str,
    case_sensitive: bool = True,
    max_matches: int = 100
) -> Dict[str, List[ToolExecutionResult]]:
    """
    Perform comprehensive search using multiple search methods.
    
    Args:
        search_pattern: Pattern to search for
        search_paths: List of paths to search in
        base_tool_call_id: Base ID for generating unique tool call IDs
        case_sensitive: Whether search should be case sensitive
        max_matches: Maximum matches per grep operation
    
    Returns:
        Dictionary with glob and grep results
    """
    logger.info("Starting comprehensive search", 
               pattern=search_pattern,
               path_count=len(search_paths),
               case_sensitive=case_sensitive)
    
    all_tasks = []
    task_types = []
    
    # Create glob search tasks for each path
    for i, path in enumerate(search_paths):
        tool_call_id = f"{base_tool_call_id}_glob_{i}"
        task = glob_search_task(
            tool_call_id=tool_call_id,
            tool_name="Glob",
            tool_input={
                "pattern": search_pattern,
                "directory": path
            }
        )
        all_tasks.append(task)
        task_types.append("glob")
    
    # Create grep search tasks for each path
    for i, path in enumerate(search_paths):
        tool_call_id = f"{base_tool_call_id}_grep_{i}"
        task = grep_search_task(
            tool_call_id=tool_call_id,
            tool_name="Grep",
            tool_input={
                "pattern": search_pattern,
                "path": path,
                "case_sensitive": case_sensitive,
                "max_matches": max_matches
            }
        )
        all_tasks.append(task)
        task_types.append("grep")
    
    # Execute all searches concurrently
    results = await asyncio.gather(*all_tasks, return_exceptions=True)
    
    # Categorize results
    glob_results = []
    grep_results = []
    
    for i, result in enumerate(results):
        if task_types[i] == "glob":
            glob_results.append(result)
        else:
            grep_results.append(result)
    
    successful_globs = sum(1 for r in glob_results if isinstance(r, ToolExecutionResult) and r.success)
    successful_greps = sum(1 for r in grep_results if isinstance(r, ToolExecutionResult) and r.success)
    
    logger.info("Comprehensive search completed", 
               pattern=search_pattern,
               successful_globs=successful_globs,
               successful_greps=successful_greps)
    
    return {
        "glob_results": glob_results,
        "grep_results": grep_results
    }


@flow(name="directory_exploration")
async def directory_exploration_flow(
    root_paths: List[str],
    base_tool_call_id: str,
    show_hidden: bool = False,
    detailed: bool = False
) -> List[ToolExecutionResult]:
    """
    Explore multiple directories concurrently.
    
    Args:
        root_paths: List of directory paths to explore
        base_tool_call_id: Base ID for generating unique tool call IDs
        show_hidden: Whether to show hidden files
        detailed: Whether to show detailed file information
    
    Returns:
        List of ToolExecutionResult objects
    """
    logger.info("Starting directory exploration", 
               directory_count=len(root_paths),
               show_hidden=show_hidden,
               detailed=detailed)
    
    # Create directory listing tasks
    ls_tasks = []
    for i, path in enumerate(root_paths):
        tool_call_id = f"{base_tool_call_id}_ls_{i}"
        task = list_directory_task(
            tool_call_id=tool_call_id,
            tool_name="LS",
            tool_input={
                "path": path,
                "all": show_hidden,
                "long": detailed
            }
        )
        ls_tasks.append(task)
    
    # Execute all directory listings concurrently
    results = await asyncio.gather(*ls_tasks, return_exceptions=True)
    
    successful_listings = sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
    logger.info("Directory exploration completed", 
               total_directories=len(root_paths),
               successful_listings=successful_listings)
    
    return results


@flow(name="file_pattern_search")
async def file_pattern_search_flow(
    file_patterns: List[str],
    search_directories: List[str],
    base_tool_call_id: str
) -> Dict[str, List[ToolExecutionResult]]:
    """
    Search for multiple file patterns across multiple directories.
    
    Args:
        file_patterns: List of glob patterns to search for
        search_directories: List of directories to search in
        base_tool_call_id: Base ID for generating unique tool call IDs
    
    Returns:
        Dictionary mapping patterns to their results
    """
    logger.info("Starting file pattern search", 
               pattern_count=len(file_patterns),
               directory_count=len(search_directories))
    
    all_tasks = []
    task_patterns = []
    
    # Create glob search tasks for each pattern in each directory
    for pattern in file_patterns:
        for i, directory in enumerate(search_directories):
            tool_call_id = f"{base_tool_call_id}_{pattern.replace('*', 'star')}_{i}"
            task = glob_search_task(
                tool_call_id=tool_call_id,
                tool_name="Glob",
                tool_input={
                    "pattern": pattern,
                    "directory": directory
                }
            )
            all_tasks.append(task)
            task_patterns.append(pattern)
    
    # Execute all searches concurrently
    results = await asyncio.gather(*all_tasks, return_exceptions=True)
    
    # Group results by pattern
    pattern_results = {pattern: [] for pattern in file_patterns}
    for i, result in enumerate(results):
        pattern = task_patterns[i]
        pattern_results[pattern].append(result)
    
    # Log summary
    for pattern, pattern_result_list in pattern_results.items():
        successful_searches = sum(1 for r in pattern_result_list if isinstance(r, ToolExecutionResult) and r.success)
        logger.debug("Pattern search summary", 
                    pattern=pattern,
                    successful_searches=successful_searches,
                    total_searches=len(pattern_result_list))
    
    total_successful = sum(
        sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
        for results in pattern_results.values()
    )
    
    logger.info("File pattern search completed", 
               total_searches=len(all_tasks),
               successful_searches=total_successful)
    
    return pattern_results


@flow(name="content_search_pipeline")
async def content_search_pipeline_flow(
    search_terms: List[str],
    target_paths: List[str],
    base_tool_call_id: str,
    case_sensitive: bool = True,
    max_matches_per_term: int = 50
) -> Dict[str, List[ToolExecutionResult]]:
    """
    Search for multiple terms across multiple paths.
    
    Args:
        search_terms: List of search terms/patterns
        target_paths: List of paths to search in
        base_tool_call_id: Base ID for generating unique tool call IDs
        case_sensitive: Whether searches should be case sensitive
        max_matches_per_term: Maximum matches per search term
    
    Returns:
        Dictionary mapping search terms to their results
    """
    logger.info("Starting content search pipeline", 
               term_count=len(search_terms),
               path_count=len(target_paths),
               case_sensitive=case_sensitive)
    
    all_tasks = []
    task_terms = []
    
    # Create grep search tasks for each term in each path
    for term in search_terms:
        for i, path in enumerate(target_paths):
            tool_call_id = f"{base_tool_call_id}_{term.replace(' ', '_')[:20]}_{i}"
            task = grep_search_task(
                tool_call_id=tool_call_id,
                tool_name="Grep",
                tool_input={
                    "pattern": term,
                    "path": path,
                    "case_sensitive": case_sensitive,
                    "max_matches": max_matches_per_term
                }
            )
            all_tasks.append(task)
            task_terms.append(term)
    
    # Execute all searches concurrently
    results = await asyncio.gather(*all_tasks, return_exceptions=True)
    
    # Group results by search term
    term_results = {term: [] for term in search_terms}
    for i, result in enumerate(results):
        term = task_terms[i]
        term_results[term].append(result)
    
    # Log summary for each term
    for term, term_result_list in term_results.items():
        successful_searches = sum(1 for r in term_result_list if isinstance(r, ToolExecutionResult) and r.success)
        logger.debug("Content search term summary", 
                    term=term[:50],
                    successful_searches=successful_searches,
                    total_searches=len(term_result_list))
    
    total_successful = sum(
        sum(1 for r in results if isinstance(r, ToolExecutionResult) and r.success)
        for results in term_results.values()
    )
    
    logger.info("Content search pipeline completed", 
               total_searches=len(all_tasks),
               successful_searches=total_successful)
    
    return term_results