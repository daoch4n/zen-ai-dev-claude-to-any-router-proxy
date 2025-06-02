"""Tool mapping and flow selection for tool execution."""

from typing import Any, Callable, Dict, List, Optional
from ...core.logging_config import get_logger

logger = get_logger("tool_execution.mapping")


# Tool flow mapping - maps tool names to their execution flows
TOOL_FLOW_MAPPING: Dict[str, str] = {
    # File operations
    "Write": "file_operations_flow",
    "Read": "file_operations_flow", 
    "Edit": "file_operations_flow",
    "MultiEdit": "file_operations_flow",
    
    # Search operations
    "Glob": "search_operations_flow",
    "Grep": "search_operations_flow",
    "LS": "search_operations_flow",
    
    # System operations
    "Bash": "system_operations_flow",
    "Task": "system_operations_flow",
    
    # Web operations
    "WebSearch": "web_operations_flow",
    "WebFetch": "web_operations_flow",
    
    # Notebook operations
    "NotebookRead": "notebook_operations_flow",
    "NotebookEdit": "notebook_operations_flow",
    
    # Todo operations
    "TodoRead": "todo_operations_flow",
    "TodoWrite": "todo_operations_flow",
}


def get_flow_for_tool(tool_name: str) -> Optional[Callable]:
    """Get the appropriate flow function for a given tool name.
    
    Args:
        tool_name: Name of the tool to execute
        
    Returns:
        Flow function that can execute the tool, or None if not found
    """
    # Import flow functions dynamically to avoid circular imports
    try:
        from .file_operations import file_operations_flow
        from .search_operations import search_operations_flow
        from .system_operations import system_operations_flow
        from .web_operations import web_operations_flow
        from .notebook_operations import notebook_operations_flow
        from .todo_operations import todo_operations_flow
        
        flow_mapping = {
            "file_operations_flow": file_operations_flow,
            "search_operations_flow": search_operations_flow,
            "system_operations_flow": system_operations_flow,
            "web_operations_flow": web_operations_flow,
            "notebook_operations_flow": notebook_operations_flow,
            "todo_operations_flow": todo_operations_flow,
        }
        
        flow_name = TOOL_FLOW_MAPPING.get(tool_name)
        if flow_name:
            return flow_mapping.get(flow_name)
        
        logger.warning("No flow mapping found for tool", tool_name=tool_name)
        return None
        
    except ImportError as e:
        logger.error("Failed to import flow functions", error=str(e), tool_name=tool_name)
        return None


def get_concurrency_strategy(tool_name: str) -> Dict[str, Any]:
    """Get concurrency strategy for a tool.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Dictionary with concurrency configuration
    """
    # Define concurrency strategies based on tool type
    strategies = {
        # File operations - low concurrency to avoid conflicts
        "Write": {"max_concurrent": 2, "timeout": 30},
        "Read": {"max_concurrent": 5, "timeout": 15},
        "Edit": {"max_concurrent": 2, "timeout": 30},
        "MultiEdit": {"max_concurrent": 1, "timeout": 60},
        
        # Search operations - higher concurrency
        "Glob": {"max_concurrent": 3, "timeout": 20},
        "Grep": {"max_concurrent": 3, "timeout": 20},
        "LS": {"max_concurrent": 5, "timeout": 10},
        
        # System operations - moderate concurrency
        "Bash": {"max_concurrent": 3, "timeout": 60},
        "Task": {"max_concurrent": 2, "timeout": 120},
        
        # Web operations - limited concurrency
        "WebSearch": {"max_concurrent": 2, "timeout": 30},
        "WebFetch": {"max_concurrent": 3, "timeout": 45},
        
        # Notebook operations - low concurrency
        "NotebookRead": {"max_concurrent": 3, "timeout": 20},
        "NotebookEdit": {"max_concurrent": 1, "timeout": 60},
        
        # Todo operations - high concurrency
        "TodoRead": {"max_concurrent": 5, "timeout": 10},
        "TodoWrite": {"max_concurrent": 3, "timeout": 15},
    }
    
    # Default strategy
    default_strategy = {"max_concurrent": 3, "timeout": 30}
    
    return strategies.get(tool_name, default_strategy)


def get_available_tool_names() -> List[str]:
    """Get list of all available tool names.
    
    Returns:
        List of tool names that can be executed
    """
    return list(TOOL_FLOW_MAPPING.keys())


def validate_tool_name(tool_name: str) -> bool:
    """Validate if a tool name is supported.
    
    Args:
        tool_name: Tool name to validate
        
    Returns:
        True if tool is supported, False otherwise
    """
    return tool_name in TOOL_FLOW_MAPPING