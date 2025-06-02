"""
MCP server management flows.

Orchestration logic for MCP server operations, combining validation,
operations, and error handling.
"""

from typing import List, Dict, Any, Optional
from fastapi import HTTPException

from src.tasks.mcp.server_validation import (
    validate_server_exists,
    validate_servers_exist,
    get_server_config_dict,
    get_all_server_configs
)
from src.tasks.mcp.server_operations import (
    get_available_servers,
    get_server_status,
    get_all_servers_status,
    start_server,
    stop_server,
    restart_server,
    start_multiple_servers,
    stop_multiple_servers,
    health_check_all_servers
)
from src.core.logging_config import get_logger

logger = get_logger(__name__)


async def get_servers_list_flow() -> List[str]:
    """
    Flow for getting list of available servers.
    
    Returns:
        List[str]: Available server names
        
    Raises:
        HTTPException: On operation failure (500)
    """
    try:
        return await get_available_servers()
    except Exception as e:
        logger.error("Failed to list available servers", 
                    error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list available servers: {str(e)}"
        )


async def get_server_status_flow(server_name: str) -> Dict[str, Any]:
    """
    Flow for getting server status with validation.
    
    Args:
        server_name: Name of the server
        
    Returns:
        dict: Server status information
        
    Raises:
        HTTPException: On validation failure (404) or operation failure (500)
    """
    try:
        # Validate server exists
        validate_server_exists(server_name)
        
        # Get status
        return await get_server_status(server_name)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting server status",
                    server_name=server_name,
                    error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting server status: {str(e)}"
        )


async def get_all_servers_status_flow() -> Dict[str, Any]:
    """
    Flow for getting all servers status.
    
    Returns:
        dict: All servers status information
        
    Raises:
        HTTPException: On operation failure (500)
    """
    try:
        return await get_all_servers_status()
    except Exception as e:
        logger.error("Error getting all servers status",
                    error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting all servers status: {str(e)}"
        )


async def start_server_flow(server_name: str) -> Dict[str, Any]:
    """
    Flow for starting a server with validation.
    
    Args:
        server_name: Name of the server to start
        
    Returns:
        dict: Operation result
        
    Raises:
        HTTPException: On validation failure (404) or operation failure (500)
    """
    try:
        # Validate server exists
        validate_server_exists(server_name)
        
        # Start server
        return await start_server(server_name)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error starting server",
                    server_name=server_name,
                    error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error starting server: {str(e)}"
        )


async def stop_server_flow(server_name: str, force: bool = False) -> Dict[str, Any]:
    """
    Flow for stopping a server with validation.
    
    Args:
        server_name: Name of the server to stop
        force: Whether to force stop
        
    Returns:
        dict: Operation result
        
    Raises:
        HTTPException: On validation failure (404) or operation failure (500)
    """
    try:
        # Validate server exists
        validate_server_exists(server_name)
        
        # Stop server
        return await stop_server(server_name, force=force)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error stopping server",
                    server_name=server_name,
                    error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error stopping server: {str(e)}"
        )


async def restart_server_flow(server_name: str, force: bool = False) -> Dict[str, Any]:
    """
    Flow for restarting a server with validation.
    
    Args:
        server_name: Name of the server to restart
        force: Whether to force restart
        
    Returns:
        dict: Operation result
        
    Raises:
        HTTPException: On validation failure (404) or operation failure (500)
    """
    try:
        # Validate server exists
        validate_server_exists(server_name)
        
        # Restart server
        return await restart_server(server_name, force=force)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error restarting server",
                    server_name=server_name,
                    error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error restarting server: {str(e)}"
        )


async def start_multiple_servers_flow(server_names: List[str]) -> Dict[str, Any]:
    """
    Flow for starting multiple servers with validation.
    
    Args:
        server_names: List of server names to start
        
    Returns:
        dict: Operation results
        
    Raises:
        HTTPException: On validation failure (404) or operation failure (500)
    """
    try:
        # Validate all servers exist
        validate_servers_exist(server_names)
        
        # Start servers
        return await start_multiple_servers(server_names)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error starting multiple servers",
                    count=len(server_names),
                    error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error starting multiple servers: {str(e)}"
        )


async def stop_multiple_servers_flow(server_names: List[str], force: bool = False) -> Dict[str, Any]:
    """
    Flow for stopping multiple servers with validation.
    
    Args:
        server_names: List of server names to stop
        force: Whether to force stop
        
    Returns:
        dict: Operation results
        
    Raises:
        HTTPException: On validation failure (404) or operation failure (500)
    """
    try:
        # Validate all servers exist
        validate_servers_exist(server_names)
        
        # Stop servers
        return await stop_multiple_servers(server_names, force=force)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error stopping multiple servers",
                    count=len(server_names),
                    error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error stopping multiple servers: {str(e)}"
        )


async def health_check_flow() -> Dict[str, Any]:
    """
    Flow for performing health checks on all servers.
    
    Returns:
        dict: Health check results
        
    Raises:
        HTTPException: On operation failure (500)
    """
    try:
        return await health_check_all_servers()
    except Exception as e:
        logger.error("Error performing health checks",
                    error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error performing health checks: {str(e)}"
        )


def get_server_config_flow(server_name: str) -> Dict[str, Any]:
    """
    Flow for getting server configuration with validation.
    
    Args:
        server_name: Name of the server
        
    Returns:
        dict: Server configuration response
        
    Raises:
        HTTPException: On validation failure (404) or operation failure (500)
    """
    try:
        # Validate and get config
        config_dict = get_server_config_dict(server_name)
        if not config_dict:
            logger.warning("Server not found in configuration", server_name=server_name)
            raise HTTPException(
                status_code=404,
                detail=f"MCP server '{server_name}' not found in configuration"
            )
        
        return {
            "server_name": server_name,
            "config": config_dict
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting server configuration",
                    server_name=server_name,
                    error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting server configuration: {str(e)}"
        )


def get_all_configs_flow() -> Dict[str, Any]:
    """
    Flow for getting all server configurations.
    
    Returns:
        dict: All server configurations response
        
    Raises:
        HTTPException: On operation failure (500)
    """
    try:
        all_configs = get_all_server_configs()
        
        return {
            "total_servers": len(all_configs),
            "configurations": all_configs
        }
        
    except Exception as e:
        logger.error("Error getting all server configurations",
                    error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting all server configurations: {str(e)}"
        )