"""
MCP server management API endpoints.

This router provides REST API endpoints for managing MCP servers,
integrating with the lifecycle service and workflow orchestration.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.mcp.lifecycle_service import lifecycle_service
from src.mcp.server_configs import config_manager
from src.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/v1/mcp", tags=["MCP Management"])


class ServerStartRequest(BaseModel):
    """Request model for starting MCP servers."""
    server_names: List[str] = Field(..., description="List of server names to start")


class ServerStopRequest(BaseModel):
    """Request model for stopping MCP servers."""
    server_names: List[str] = Field(..., description="List of server names to stop")
    force: bool = Field(default=False, description="Force stop servers")


class MCPServerStatusResponse(BaseModel):
    """Response model for MCP server status."""
    name: str
    status: str
    running: bool
    pid: Optional[int] = None
    started_at: Optional[str] = None
    uptime_seconds: Optional[float] = None
    restart_count: int = 0
    health_status: str = "unknown"
    last_health_check: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class MultiServerOperationResponse(BaseModel):
    """Response model for multi-server operations."""
    total_servers: int
    successful_operations: int
    failed_operations: int
    success_rate: float
    results: List[Dict[str, Any]]
    timestamp: str


class HealthCheckResponse(BaseModel):
    """Response model for health check operations."""
    total_servers: int
    running_servers: int
    healthy_servers: int
    unhealthy_servers: int
    overall_health: str
    results: List[Dict[str, Any]]
    timestamp: str


@router.get("/servers", response_model=List[str])
async def list_available_servers():
    """List all available MCP servers from configuration."""
    
    request_logger = logger.bind(endpoint="list_available_servers")
    request_logger.info("Listing available MCP servers")
    
    try:
        servers = await lifecycle_service.get_available_servers()
        
        request_logger.info("Successfully retrieved available servers",
                           count=len(servers))
        
        return servers
        
    except Exception as e:
        request_logger.error("Failed to list available servers",
                           error=str(e),
                           error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list available servers: {str(e)}"
        )


@router.get("/servers/{server_name}/status", response_model=MCPServerStatusResponse)
async def get_server_status(server_name: str):
    """Get detailed status of a specific MCP server."""
    
    request_logger = logger.bind(
        endpoint="get_server_status",
        server_name=server_name
    )
    request_logger.info("Getting MCP server status")
    
    try:
        # Check if server is configured
        if not config_manager.get_server_config(server_name):
            request_logger.warning("Server not found in configuration")
            raise HTTPException(
                status_code=404,
                detail=f"MCP server '{server_name}' not found in configuration"
            )
        
        status = await lifecycle_service.get_server_status(server_name)
        
        request_logger.info("Successfully retrieved server status",
                           status=status.get("status", "unknown"))
        
        return MCPServerStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        request_logger.error("Failed to get server status",
                           error=str(e),
                           error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get server status: {str(e)}"
        )


@router.get("/servers/status", response_model=Dict[str, MCPServerStatusResponse])
async def get_all_servers_status():
    """Get status of all configured MCP servers."""
    
    request_logger = logger.bind(endpoint="get_all_servers_status")
    request_logger.info("Getting all MCP servers status")
    
    try:
        all_status = await lifecycle_service.get_all_servers_status()
        
        # Convert to response models
        response = {}
        for server_name, status in all_status.items():
            response[server_name] = MCPServerStatusResponse(**status)
        
        request_logger.info("Successfully retrieved all servers status",
                           total_servers=len(response))
        
        return response
        
    except Exception as e:
        request_logger.error("Failed to get all servers status",
                           error=str(e),
                           error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get all servers status: {str(e)}"
        )


@router.post("/servers/{server_name}/start")
async def start_server(server_name: str):
    """Start a specific MCP server."""
    
    request_logger = logger.bind(
        endpoint="start_server",
        server_name=server_name
    )
    request_logger.info("Starting MCP server")
    
    try:
        # Check if server is configured
        if not config_manager.get_server_config(server_name):
            request_logger.warning("Server not found in configuration")
            raise HTTPException(
                status_code=404,
                detail=f"MCP server '{server_name}' not found in configuration"
            )
        
        result = await lifecycle_service.start_server(server_name)
        
        if result["success"]:
            request_logger.info("Successfully started MCP server")
            return {
                "message": f"MCP server '{server_name}' started successfully",
                "server_name": server_name,
                "status": result
            }
        else:
            request_logger.error("Failed to start MCP server")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start MCP server '{server_name}'"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        request_logger.error("Error starting MCP server",
                           error=str(e),
                           error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error starting MCP server: {str(e)}"
        )


@router.post("/servers/{server_name}/stop")
async def stop_server(server_name: str, force: bool = Query(default=False)):
    """Stop a specific MCP server."""
    
    request_logger = logger.bind(
        endpoint="stop_server",
        server_name=server_name,
        force=force
    )
    request_logger.info("Stopping MCP server")
    
    try:
        # Check if server is configured
        if not config_manager.get_server_config(server_name):
            request_logger.warning("Server not found in configuration")
            raise HTTPException(
                status_code=404,
                detail=f"MCP server '{server_name}' not found in configuration"
            )
        
        result = await lifecycle_service.stop_server(server_name, force=force)
        
        if result["success"]:
            request_logger.info("Successfully stopped MCP server")
            return {
                "message": f"MCP server '{server_name}' stopped successfully",
                "server_name": server_name,
                "force": force,
                "status": result
            }
        else:
            request_logger.error("Failed to stop MCP server")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to stop MCP server '{server_name}'"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        request_logger.error("Error stopping MCP server",
                           error=str(e),
                           error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error stopping MCP server: {str(e)}"
        )


@router.post("/servers/{server_name}/restart")
async def restart_server(server_name: str):
    """Restart a specific MCP server."""
    
    request_logger = logger.bind(
        endpoint="restart_server",
        server_name=server_name
    )
    request_logger.info("Restarting MCP server")
    
    try:
        # Check if server is configured
        if not config_manager.get_server_config(server_name):
            request_logger.warning("Server not found in configuration")
            raise HTTPException(
                status_code=404,
                detail=f"MCP server '{server_name}' not found in configuration"
            )
        
        result = await lifecycle_service.restart_server(server_name)
        
        if result["success"]:
            request_logger.info("Successfully restarted MCP server")
            return {
                "message": f"MCP server '{server_name}' restarted successfully",
                "server_name": server_name,
                "status": result
            }
        else:
            request_logger.error("Failed to restart MCP server")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to restart MCP server '{server_name}'"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        request_logger.error("Error restarting MCP server",
                           error=str(e),
                           error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error restarting MCP server: {str(e)}"
        )


@router.post("/servers/start", response_model=MultiServerOperationResponse)
async def start_multiple_servers(request: ServerStartRequest):
    """Start multiple MCP servers concurrently."""
    
    request_logger = logger.bind(
        endpoint="start_multiple_servers",
        server_names=request.server_names,
        count=len(request.server_names)
    )
    request_logger.info("Starting multiple MCP servers")
    
    try:
        # Validate all servers exist in configuration
        for server_name in request.server_names:
            if not config_manager.get_server_config(server_name):
                request_logger.warning("Server not found in configuration",
                                     server_name=server_name)
                raise HTTPException(
                    status_code=404,
                    detail=f"MCP server '{server_name}' not found in configuration"
                )
        
        result = await lifecycle_service.start_multiple_servers(request.server_names)
        
        request_logger.info("Multiple server start operation completed",
                           success_rate=result["success_rate"])
        
        return MultiServerOperationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        request_logger.error("Error starting multiple MCP servers",
                           error=str(e),
                           error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error starting multiple MCP servers: {str(e)}"
        )


@router.post("/servers/stop", response_model=MultiServerOperationResponse)
async def stop_multiple_servers(request: ServerStopRequest):
    """Stop multiple MCP servers concurrently."""
    
    request_logger = logger.bind(
        endpoint="stop_multiple_servers",
        server_names=request.server_names,
        count=len(request.server_names),
        force=request.force
    )
    request_logger.info("Stopping multiple MCP servers")
    
    try:
        # Validate all servers exist in configuration
        for server_name in request.server_names:
            if not config_manager.get_server_config(server_name):
                request_logger.warning("Server not found in configuration",
                                     server_name=server_name)
                raise HTTPException(
                    status_code=404,
                    detail=f"MCP server '{server_name}' not found in configuration"
                )
        
        result = await lifecycle_service.stop_multiple_servers(
            request.server_names, 
            force=request.force
        )
        
        request_logger.info("Multiple server stop operation completed",
                           success_rate=result["success_rate"])
        
        return MultiServerOperationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        request_logger.error("Error stopping multiple MCP servers",
                           error=str(e),
                           error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error stopping multiple MCP servers: {str(e)}"
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check_all_servers():
    """Perform health checks on all configured MCP servers."""
    
    request_logger = logger.bind(endpoint="health_check_all_servers")
    request_logger.info("Performing health checks on all MCP servers")
    
    try:
        result = await lifecycle_service.health_check_all_servers()
        
        request_logger.info("Health check operation completed",
                           overall_health=result["overall_health"])
        
        return HealthCheckResponse(**result)
        
    except Exception as e:
        request_logger.error("Error performing health checks",
                           error=str(e),
                           error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error performing health checks: {str(e)}"
        )


@router.get("/config/{server_name}")
async def get_server_config(server_name: str):
    """Get configuration for a specific MCP server."""
    
    request_logger = logger.bind(
        endpoint="get_server_config",
        server_name=server_name
    )
    request_logger.info("Getting MCP server configuration")
    
    try:
        config = config_manager.get_server_config(server_name)
        
        if not config:
            request_logger.warning("Server not found in configuration")
            raise HTTPException(
                status_code=404,
                detail=f"MCP server '{server_name}' not found in configuration"
            )
        
        # Convert to dict for JSON response
        config_dict = {
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
        
        request_logger.info("Successfully retrieved server configuration")
        
        return {
            "server_name": server_name,
            "config": config_dict
        }
        
    except HTTPException:
        raise
    except Exception as e:
        request_logger.error("Error getting server configuration",
                           error=str(e),
                           error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting server configuration: {str(e)}"
        )


@router.get("/config")
async def get_all_server_configs():
    """Get configurations for all MCP servers."""
    
    request_logger = logger.bind(endpoint="get_all_server_configs")
    request_logger.info("Getting all MCP server configurations")
    
    try:
        all_configs = {}
        server_names = config_manager.list_server_names()
        
        for server_name in server_names:
            config = config_manager.get_server_config(server_name)
            if config:
                all_configs[server_name] = {
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
        
        request_logger.info("Successfully retrieved all server configurations",
                           total_servers=len(all_configs))
        
        return {
            "total_servers": len(all_configs),
            "configurations": all_configs
        }
        
    except Exception as e:
        request_logger.error("Error getting all server configurations",
                           error=str(e),
                           error_type=type(e).__name__)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting all server configurations: {str(e)}"
        )