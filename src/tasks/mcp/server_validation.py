"""
MCP server validation tasks.

Atomic operations for validating MCP server configurations and existence.
"""

from typing import List, Optional
from fastapi import HTTPException

from src.mcp.server_configs import config_manager
from src.core.logging_config import get_logger

logger = get_logger(__name__)


def validate_server_exists(server_name: str) -> bool:
    """
    Validate that a server exists in configuration.
    
    Args:
        server_name: Name of the server to validate
        
    Returns:
        bool: True if server exists
        
    Raises:
        HTTPException: If server not found (404)
    """
    config = config_manager.get_server_config(server_name)
    if not config:
        logger.warning("Server not found in configuration", server_name=server_name)
        raise HTTPException(
            status_code=404,
            detail=f"MCP server '{server_name}' not found in configuration"
        )
    return True


def validate_servers_exist(server_names: List[str]) -> bool:
    """
    Validate that multiple servers exist in configuration.
    
    Args:
        server_names: List of server names to validate
        
    Returns:
        bool: True if all servers exist
        
    Raises:
        HTTPException: If any server not found (404)
    """
    for server_name in server_names:
        validate_server_exists(server_name)
    return True


def get_server_config_dict(server_name: str) -> Optional[dict]:
    """
    Get server configuration as dictionary.
    
    Args:
        server_name: Name of the server
        
    Returns:
        dict: Server configuration or None if not found
    """
    config = config_manager.get_server_config(server_name)
    if not config:
        return None
        
    return {
        "name": config.name,
        "type": config.type,
        "command": config.command,
        "environment": config.environment,
        "log_level": config.log_level,
        "restart_policy": config.restart_policy,
        "max_restarts": config.max_restarts,
        "python_version": config.python_version,
        "node_version": config.node_version,
        "health_check": {
            "enabled": config.health_check.enabled,
            "endpoint": config.health_check.endpoint,
            "interval": config.health_check.interval,
            "timeout": config.health_check.timeout
        }
    }


def get_all_server_configs() -> dict:
    """
    Get all server configurations as dictionary.
    
    Returns:
        dict: All server configurations
    """
    all_configs = {}
    server_names = config_manager.list_server_names()
    
    for server_name in server_names:
        config_dict = get_server_config_dict(server_name)
        if config_dict:
            all_configs[server_name] = config_dict
            
    return all_configs