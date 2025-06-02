"""
MCP server operations tasks.

Atomic operations for MCP server lifecycle management including start, stop, 
restart, status, and health checks.
"""

from typing import List, Dict, Any
from src.mcp.lifecycle_service import lifecycle_service
from src.core.logging_config import get_logger

logger = get_logger(__name__)


async def get_available_servers() -> List[str]:
    """
    Get list of available MCP servers.
    
    Returns:
        List[str]: List of server names
    """
    return await lifecycle_service.get_available_servers()


async def get_server_status(server_name: str) -> Dict[str, Any]:
    """
    Get detailed status of a specific MCP server.
    
    Args:
        server_name: Name of the server
        
    Returns:
        dict: Server status information
    """
    return await lifecycle_service.get_server_status(server_name)


async def get_all_servers_status() -> Dict[str, Any]:
    """
    Get status of all MCP servers.
    
    Returns:
        dict: Status information for all servers
    """
    return await lifecycle_service.get_all_servers_status()


async def start_server(server_name: str) -> Dict[str, Any]:
    """
    Start a specific MCP server.
    
    Args:
        server_name: Name of the server to start
        
    Returns:
        dict: Operation result
    """
    return await lifecycle_service.start_server(server_name)


async def stop_server(server_name: str, force: bool = False) -> Dict[str, Any]:
    """
    Stop a specific MCP server.
    
    Args:
        server_name: Name of the server to stop
        force: Whether to force stop
        
    Returns:
        dict: Operation result
    """
    return await lifecycle_service.stop_server(server_name, force=force)


async def restart_server(server_name: str, force: bool = False) -> Dict[str, Any]:
    """
    Restart a specific MCP server.
    
    Args:
        server_name: Name of the server to restart
        force: Whether to force restart
        
    Returns:
        dict: Operation result
    """
    return await lifecycle_service.restart_server(server_name, force=force)


async def start_multiple_servers(server_names: List[str]) -> Dict[str, Any]:
    """
    Start multiple MCP servers.
    
    Args:
        server_names: List of server names to start
        
    Returns:
        dict: Operation results
    """
    return await lifecycle_service.start_multiple_servers(server_names)


async def stop_multiple_servers(server_names: List[str], force: bool = False) -> Dict[str, Any]:
    """
    Stop multiple MCP servers.
    
    Args:
        server_names: List of server names to stop
        force: Whether to force stop
        
    Returns:
        dict: Operation results
    """
    return await lifecycle_service.stop_multiple_servers(server_names, force=force)


async def health_check_all_servers() -> Dict[str, Any]:
    """
    Perform health checks on all configured MCP servers.
    
    Returns:
        dict: Health check results
    """
    return await lifecycle_service.health_check_all_servers()