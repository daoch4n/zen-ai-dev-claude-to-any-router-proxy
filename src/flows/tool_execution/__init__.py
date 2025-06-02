"""Tool execution flows package for OpenRouter Anthropic Server.

Orchestrates Prefect task execution across different tool categories with optimal
concurrency strategies and comprehensive error handling.

Part of Phase 6A comprehensive refactoring - Tool Execution Workflows.
"""

from .file_operations import (
    file_operations_flow,
    bulk_file_read_flow,
    safe_file_write_sequence_flow,
    file_edit_chain_flow,
    atomic_file_batch_flow
)

from .system_operations import (
    system_operations_flow,
    command_pipeline_flow,
    task_management_batch_flow,
    safe_command_execution_flow,
    interactive_command_session_flow
)

from .search_operations import (
    search_operations_flow,
    comprehensive_search_flow,
    directory_exploration_flow,
    file_pattern_search_flow,
    content_search_pipeline_flow
)

from .web_operations import (
    web_operations_flow,
    concurrent_web_search_flow,
    web_content_pipeline_flow,
    batch_url_fetch_flow,
    web_research_flow,
    url_validation_and_fetch_flow
)

from .notebook_operations import (
    notebook_operations_flow,
    batch_notebook_read_flow,
    notebook_cell_pipeline_flow,
    notebook_analysis_flow,
    notebook_batch_edit_flow,
    notebook_validation_flow
)

from .todo_operations import (
    todo_operations_flow,
    batch_todo_read_flow,
    todo_management_pipeline_flow,
    todo_aggregation_flow,
    batch_todo_update_flow,
    todo_synchronization_flow,
    todo_cleanup_flow
)

# Main orchestration flows
__all__ = [
    # Primary tool operation flows (one per tool category)
    "file_operations_flow",
    "system_operations_flow", 
    "search_operations_flow",
    "web_operations_flow",
    "notebook_operations_flow",
    "todo_operations_flow",
    
    # File operation specialized flows
    "bulk_file_read_flow",
    "safe_file_write_sequence_flow", 
    "file_edit_chain_flow",
    "atomic_file_batch_flow",
    
    # System operation specialized flows
    "command_pipeline_flow",
    "task_management_batch_flow",
    "safe_command_execution_flow",
    "interactive_command_session_flow",
    
    # Search operation specialized flows
    "comprehensive_search_flow",
    "directory_exploration_flow",
    "file_pattern_search_flow",
    "content_search_pipeline_flow",
    
    # Web operation specialized flows
    "concurrent_web_search_flow",
    "web_content_pipeline_flow",
    "batch_url_fetch_flow",
    "web_research_flow",
    "url_validation_and_fetch_flow",
    
    # Notebook operation specialized flows
    "batch_notebook_read_flow",
    "notebook_cell_pipeline_flow",
    "notebook_analysis_flow", 
    "notebook_batch_edit_flow",
    "notebook_validation_flow",
    
    # Todo operation specialized flows
    "batch_todo_read_flow",
    "todo_management_pipeline_flow",
    "todo_aggregation_flow",
    "batch_todo_update_flow",
    "todo_synchronization_flow",
    "todo_cleanup_flow"
]

# Flow category mapping for orchestration
TOOL_FLOW_MAPPING = {
    # File tools
    'write': file_operations_flow,
    'read': file_operations_flow,
    'edit': file_operations_flow,
    'multiedit': file_operations_flow,
    
    # System tools
    'bash': system_operations_flow,
    'task': system_operations_flow,
    
    # Search tools
    'glob': search_operations_flow,
    'grep': search_operations_flow,
    'ls': search_operations_flow,
    
    # Web tools
    'websearch': web_operations_flow,
    'webfetch': web_operations_flow,
    
    # Notebook tools
    'notebookread': notebook_operations_flow,
    'notebookedit': notebook_operations_flow,
    
    # Todo tools
    'todoread': todo_operations_flow,
    'todowrite': todo_operations_flow
}

# Concurrency strategy mapping
CONCURRENCY_STRATEGIES = {
    'file_operations': {
        'read_concurrent': True,
        'write_sequential': True,
        'max_concurrent_reads': 10,
        'max_concurrent_writes': 3
    },
    'system_operations': {
        'command_concurrent': False,  # Commands are sequential for safety
        'max_concurrent_commands': 1,
        'timeout_seconds': 30
    },
    'search_operations': {
        'search_concurrent': True,  # All searches are read-only
        'max_concurrent_searches': 5
    },
    'web_operations': {
        'web_concurrent': True,
        'max_concurrent_requests': 3,  # Respectful rate limiting
        'request_delay_seconds': 1
    },
    'notebook_operations': {
        'read_concurrent': True,
        'edit_sequential_per_notebook': True,
        'max_concurrent_notebooks': 3
    },
    'todo_operations': {
        'read_concurrent': True,
        'write_sequential_per_file': True,
        'max_concurrent_files': 5
    }
}

def get_flow_for_tool(tool_name: str):
    """
    Get the appropriate flow function for a given tool name.
    
    Args:
        tool_name: Name of the tool (case-insensitive)
    
    Returns:
        Flow function for the tool category
    """
    tool_key = tool_name.lower()
    return TOOL_FLOW_MAPPING.get(tool_key)

def get_concurrency_strategy(flow_category: str) -> dict:
    """
    Get concurrency strategy for a flow category.
    
    Args:
        flow_category: Category name (e.g., 'file_operations')
    
    Returns:
        Dictionary with concurrency configuration
    """
    return CONCURRENCY_STRATEGIES.get(flow_category, {})