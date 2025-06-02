"""
MCP Server Management Coordinator.

Centralized coordinator for all MCP server management operations,
providing a single point of access for server lifecycle management.
"""

from typing import List, Dict, Any, Optional
from functools import wraps

from src.flows.mcp.server_management import (
    get_servers_list_flow,
    get_server_status_flow,
    get_all_servers_status_flow,
    start_server_flow,
    stop_server_flow,
    restart_server_flow,
    start_multiple_servers_flow,
    stop_multiple_servers_flow,
    health_check_flow,
    get_server_config_flow,
    get_all_configs_flow
)
from src.core.logging_config import get_logger

logger = get_logger(__name__)


def log_operation(operation_name: str):
    """
    Decorator for logging MCP operations.
    
    Args:
        operation_name: Name of the operation for logging
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract relevant parameters for logging
            log_context = {"operation": operation_name}
            
            if args and len(args) > 1:  # First arg is self, second might be server_name
                if isinstance(args[1], str):
                    log_context["server_name"] = args[1]
            if "server_names" in kwargs:
                log_context["server_count"] = len(kwargs["server_names"])
            elif len(args) > 1 and isinstance(args[1], list):
                log_context["server_count"] = len(args[1])
                
            request_logger = logger.bind(**log_context)
            request_logger.info(f"Starting {operation_name}")
            
            try:
                result = await func(*args, **kwargs)
                request_logger.info(f"Completed {operation_name}")
                return result
            except Exception as e:
                request_logger.error(f"Failed {operation_name}",
                                   error=str(e), error_type=type(e).__name__)
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Extract relevant parameters for logging
            log_context = {"operation": operation_name}
            
            if args and len(args) > 1:  # First arg is self, second might be server_name
                if isinstance(args[1], str):
                    log_context["server_name"] = args[1]
                    
            request_logger = logger.bind(**log_context)
            request_logger.info(f"Starting {operation_name}")
            
            try:
                result = func(*args, **kwargs)
                request_logger.info(f"Completed {operation_name}")
                return result
            except Exception as e:
                request_logger.error(f"Failed {operation_name}",
                                   error=str(e), error_type=type(e).__name__)
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator


class MCPCoordinator:
    """
    Singleton coordinator for MCP server management operations.
    
    Provides centralized access to all MCP server lifecycle operations
    with consistent logging and error handling.
    """
    
    _instance: Optional['MCPCoordinator'] = None
    
    def __new__(cls) -> 'MCPCoordinator':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @log_operation("list_servers")
    async def list_servers(self) -> List[str]:
        """
        List all available MCP servers.
        
        Returns:
            List[str]: Available server names
        """
        return await get_servers_list_flow()
    
    @log_operation("get_server_status")
    async def get_server_status(self, server_name: str) -> Dict[str, Any]:
        """
        Get detailed status of a specific MCP server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            dict: Server status information
        """
        return await get_server_status_flow(server_name)
    
    @log_operation("get_all_servers_status")
    async def get_all_servers_status(self) -> Dict[str, Any]:
        """
        Get status of all MCP servers.
        
        Returns:
            dict: Status information for all servers
        """
        return await get_all_servers_status_flow()
    
    @log_operation("start_server")
    async def start_server(self, server_name: str) -> Dict[str, Any]:
        """
        Start a specific MCP server.
        
        Args:
            server_name: Name of the server to start
            
        Returns:
            dict: Operation result
        """
        return await start_server_flow(server_name)
    
    @log_operation("stop_server")
    async def stop_server(self, server_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Stop a specific MCP server.
        
        Args:
            server_name: Name of the server to stop
            force: Whether to force stop
            
        Returns:
            dict: Operation result
        """
        return await stop_server_flow(server_name, force=force)
    
    @log_operation("restart_server")
    async def restart_server(self, server_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Restart a specific MCP server.
        
        Args:
            server_name: Name of the server to restart
            force: Whether to force restart
            
        Returns:
            dict: Operation result
        """
        return await restart_server_flow(server_name, force=force)
    
    @log_operation("start_multiple_servers")
    async def start_multiple_servers(self, server_names: List[str]) -> Dict[str, Any]:
        """
        Start multiple MCP servers.
        
        Args:
            server_names: List of server names to start
            
        Returns:
            dict: Operation results
        """
        return await start_multiple_servers_flow(server_names)
    
    @log_operation("stop_multiple_servers")
    async def stop_multiple_servers(self, server_names: List[str], force: bool = False) -> Dict[str, Any]:
        """
        Stop multiple MCP servers.
        
        Args:
            server_names: List of server names to stop
            force: Whether to force stop
            
        Returns:
            dict: Operation results
        """
        return await stop_multiple_servers_flow(server_names, force=force)
    
    @log_operation("health_check_all")
    async def health_check_all_servers(self) -> Dict[str, Any]:
        """
        Perform health checks on all configured MCP servers.
        
        Returns:
            dict: Health check results
        """
        return await health_check_flow()
    
    @log_operation("get_server_config")
    def get_server_config(self, server_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific MCP server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            dict: Server configuration response
        """
        return get_server_config_flow(server_name)
    
    @log_operation("get_all_configs")
    def get_all_server_configs(self) -> Dict[str, Any]:
        """
        Get configurations for all MCP servers.
        
        Returns:
            dict: All server configurations response
        """
        return get_all_configs_flow()


# Global coordinator instance
mcp_coordinator = MCPCoordinator()