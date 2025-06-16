"""
MCP server management API endpoints - Refactored.

This router provides REST API endpoints for managing MCP servers,
using the modular task-flow-coordinator architecture.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field

try:
    from src.coordinators.mcp_coordinator import mcp_coordinator
except ImportError:
    mcp_coordinator = None
    
from ..services.mcp_service import MCPService
from ..core.logging_config import get_logger

logger = get_logger("mcp_router")
router = APIRouter(prefix="/v1/mcp", tags=["MCP Management"])

# MCP service instance
mcp_service = MCPService()

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
    pid: int | None = None
    started_at: str | None = None
    uptime_seconds: float | None = None
    restart_count: int = 0
    health_status: str = "unknown"
    last_health_check: str | None = None
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


class MCPServerCreate(BaseModel):
    """MCP server creation request."""
    name: str
    url: str
    type: str = "sse"  # sse, stdio, streamable_http
    metadata: Optional[Dict[str, Any]] = None


class MCPServerUpdate(BaseModel):
    """MCP server update request."""
    name: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MCPToolCall(BaseModel):
    """MCP tool call request."""
    tool_name: str
    arguments: Dict[str, Any]
    server_id: Optional[str] = None


@router.get("/servers", response_model=List[str])
async def list_available_servers():
    """List all available MCP servers from configuration."""
    return await mcp_coordinator.list_servers()


@router.get("/servers/{server_name}/status", response_model=MCPServerStatusResponse)
async def get_server_status(server_name: str):
    """Get detailed status of a specific MCP server."""
    result = await mcp_coordinator.get_server_status(server_name)
    return MCPServerStatusResponse(**result)


@router.get("/servers/status")
async def get_all_servers_status():
    """Get status of all MCP servers."""
    return await mcp_coordinator.get_all_servers_status()


@router.post("/servers/{server_name}/start")
async def start_server(server_name: str):
    """Start a specific MCP server."""
    return await mcp_coordinator.start_server(server_name)


@router.post("/servers/{server_name}/stop")
async def stop_server(server_name: str, force: bool = Query(default=False)):
    """Stop a specific MCP server."""
    return await mcp_coordinator.stop_server(server_name, force=force)


@router.post("/servers/{server_name}/restart")
async def restart_server(server_name: str, force: bool = Query(default=False)):
    """Restart a specific MCP server."""
    return await mcp_coordinator.restart_server(server_name, force=force)


@router.post("/servers/start", response_model=MultiServerOperationResponse)
async def start_multiple_servers(request: ServerStartRequest):
    """Start multiple MCP servers."""
    result = await mcp_coordinator.start_multiple_servers(request.server_names)
    return MultiServerOperationResponse(**result)


@router.post("/servers/stop", response_model=MultiServerOperationResponse)
async def stop_multiple_servers(request: ServerStopRequest):
    """Stop multiple MCP servers."""
    result = await mcp_coordinator.stop_multiple_servers(
        request.server_names,
        force=request.force
    )
    return MultiServerOperationResponse(**result)


@router.get("/health", response_model=HealthCheckResponse)
async def health_check_all_servers():
    """Perform health checks on all configured MCP servers."""
    result = await mcp_coordinator.health_check_all_servers()
    return HealthCheckResponse(**result)


@router.get("/config/{server_name}")
async def get_server_config(server_name: str):
    """Get configuration for a specific MCP server."""
    return mcp_coordinator.get_server_config(server_name)


@router.get("/config")
async def get_all_server_configs():
    """Get configurations for all MCP servers."""
    return mcp_coordinator.get_all_server_configs()


@router.get("/mcp/enabled")
async def get_mcp_enabled():
    """Check if MCP is enabled (python>=3.10 requirements are met)."""
    try:
        status = await mcp_service.is_mcp_enabled()
        return status
    except Exception as e:
        logger.error("Failed to check MCP status", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to check MCP status", "message": str(e)}
        )


@router.get("/mcp/tools/list")
async def list_mcp_tools(
    server_id: Optional[str] = Query(None, description="Optional server ID filter")
):
    """List all available tools."""
    try:
        result = await mcp_service.list_mcp_tools(server_id=server_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail={"error": "Failed to list MCP tools", "message": result.get("error")}
            )
        
        return {
            "tools": result["tools"],
            "total_count": result["total_count"],
            "server_count": result["server_count"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list MCP tools", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to list MCP tools", "message": str(e)}
        )


@router.post("/mcp/tools/call")
async def call_mcp_tool(tool_call: MCPToolCall):
    """Call a specific tool with the provided arguments."""
    try:
        result = await mcp_service.call_mcp_tool(
            tool_name=tool_call.tool_name,
            arguments=tool_call.arguments,
            server_id=tool_call.server_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail={"error": "Tool call failed", "message": result.get("error")}
            )
        
        return {
            "tool_name": result["tool_name"],
            "server_id": result["server_id"],
            "result": result["result"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to call MCP tool", tool_name=tool_call.tool_name, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to call MCP tool", "message": str(e)}
        )


@router.get("/v1/mcp/server")
async def list_mcp_servers():
    """Returns all of the configured mcp servers in the db filtered by requestor's access."""
    try:
        result = await mcp_service.list_mcp_servers()
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail={"error": "Failed to list MCP servers", "message": result.get("error")}
            )
        
        return {
            "servers": result["servers"],
            "total_count": result["total_count"],
            "enabled": result["enabled"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list MCP servers", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to list MCP servers", "message": str(e)}
        )


@router.get("/v1/mcp/server/{server_id}")
async def get_mcp_server(server_id: str):
    """Returns the specific mcp server in the db given server_id filtered by requestor's access."""
    try:
        result = await mcp_service.get_mcp_server(server_id)
        
        if not result["success"]:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(
                    status_code=404,
                    detail={"error": "MCP server not found", "server_id": server_id}
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail={"error": "Failed to get MCP server", "message": result.get("error")}
                )
        
        return result["server"]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get MCP server", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to get MCP server", "message": str(e)}
        )


@router.post("/v1/mcp/server")
async def add_mcp_server(server_config: MCPServerCreate):
    """Add a new external mcp server."""
    try:
        result = await mcp_service.add_mcp_server(server_config.dict())
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail={"error": "Failed to add MCP server", "message": result.get("error")}
            )
        
        return {
            "server_id": result["server_id"],
            "server": result["server"],
            "message": "MCP server added successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to add MCP server", server_config=server_config.dict(), error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to add MCP server", "message": str(e)}
        )


@router.put("/v1/mcp/server")
async def update_mcp_server(
    server_id: str = Query(..., description="MCP server ID to update"),
    update_data: MCPServerUpdate = Body(...)
):
    """Updates an existing external mcp server."""
    try:
        # Get existing server
        existing_result = await mcp_service.get_mcp_server(server_id)
        if not existing_result["success"]:
            raise HTTPException(
                status_code=404,
                detail={"error": "MCP server not found", "server_id": server_id}
            )
        
        # Update server configuration
        existing_server = existing_result["server"]
        update_dict = update_data.dict(exclude_unset=True)
        
        for key, value in update_dict.items():
            if value is not None:
                existing_server[key] = value
        
        # For this implementation, we'll delete and recreate
        # In a real implementation, you'd update the existing server
        await mcp_service.delete_mcp_server(server_id)
        result = await mcp_service.add_mcp_server(existing_server)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail={"error": "Failed to update MCP server", "message": result.get("error")}
            )
        
        return {
            "server_id": result["server_id"],
            "server": result["server"],
            "message": "MCP server updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update MCP server", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to update MCP server", "message": str(e)}
        )


@router.delete("/v1/mcp/server/{server_id}")
async def delete_mcp_server(server_id: str):
    """Deletes the mcp server given server_id."""
    try:
        result = await mcp_service.delete_mcp_server(server_id)
        
        if not result["success"]:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(
                    status_code=404,
                    detail={"error": "MCP server not found", "server_id": server_id}
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail={"error": "Failed to delete MCP server", "message": result.get("error")}
                )
        
        return {
            "message": result["message"],
            "deleted_server": result["deleted_server"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete MCP server", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to delete MCP server", "message": str(e)}
        )