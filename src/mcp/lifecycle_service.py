"""
MCP server lifecycle service with orchestration integration.

This service provides a clean interface for managing MCP server lifecycles
and integrates with the Prefect workflow orchestration system.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from prefect import task, flow
from prefect.logging import get_run_logger

from src.mcp.environment_manager import environment_manager, MCPServerProcess
from src.mcp.server_configs import config_manager
from src.core.logging_config import get_logger

logger = get_logger(__name__)


def _clean_log_extra(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean dictionary data for use in logger extra parameter.
    
    Removes keys that conflict with Python's LogRecord reserved fields
    to prevent KeyError: "Attempt to overwrite 'X' in LogRecord".
    """
    # LogRecord reserved fields that should not be in extra data
    reserved_fields = {
        'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
        'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
        'relativeCreated', 'thread', 'threadName', 'processName',
        'process', 'message', 'exc_info', 'exc_text', 'stack_info'
    }
    
    # Create a copy and remove conflicting keys
    cleaned = {}
    for key, value in data.items():
        if key not in reserved_fields:
            cleaned[key] = value
        else:
            # Prefix conflicting keys to make them safe
            cleaned[f"mcp_{key}"] = value
    
    return cleaned


@task(name="start_mcp_server")
async def start_mcp_server_task(server_name: str) -> Dict[str, Any]:
    """Prefect task to start an MCP server."""
    
    task_logger = get_run_logger()
    task_logger.info("Starting MCP server task", extra={"server_name": server_name})
    
    success = await environment_manager.start_server(server_name)
    
    result = {
        "server_name": server_name,
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    if success:
        status = environment_manager.get_server_status(server_name)
        result.update(status)
        task_logger.info("MCP server started successfully", extra=_clean_log_extra(result))
    else:
        task_logger.error("Failed to start MCP server", extra=_clean_log_extra(result))
    
    return result


@task(name="stop_mcp_server")
async def stop_mcp_server_task(server_name: str, force: bool = False) -> Dict[str, Any]:
    """Prefect task to stop an MCP server."""
    
    task_logger = get_run_logger()
    task_logger.info("Stopping MCP server task", 
                    extra={"server_name": server_name, "force": force})
    
    success = await environment_manager.stop_server(server_name, force=force)
    
    result = {
        "server_name": server_name,
        "success": success,
        "force": force,
        "timestamp": datetime.now().isoformat()
    }
    
    if success:
        task_logger.info("MCP server stopped successfully", extra=_clean_log_extra(result))
    else:
        task_logger.error("Failed to stop MCP server", extra=_clean_log_extra(result))
    
    return result


@task(name="restart_mcp_server")
async def restart_mcp_server_task(server_name: str) -> Dict[str, Any]:
    """Prefect task to restart an MCP server."""
    
    task_logger = get_run_logger()
    task_logger.info("Restarting MCP server task", extra={"server_name": server_name})
    
    success = await environment_manager.restart_server(server_name)
    
    result = {
        "server_name": server_name,
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    if success:
        status = environment_manager.get_server_status(server_name)
        result.update(status)
        task_logger.info("MCP server restarted successfully", extra=_clean_log_extra(result))
    else:
        task_logger.error("Failed to restart MCP server", extra=_clean_log_extra(result))
    
    return result


@task(name="health_check_mcp_server")
async def health_check_mcp_server_task(server_name: str) -> Dict[str, Any]:
    """Prefect task to perform health check on an MCP server."""
    
    task_logger = get_run_logger()
    task_logger.info("Health checking MCP server task", extra={"server_name": server_name})
    
    status = environment_manager.get_server_status(server_name)
    
    result = {
        "server_name": server_name,
        "health_check_timestamp": datetime.now().isoformat(),
        **status
    }
    
    task_logger.info("Health check completed", extra=_clean_log_extra(result))
    return result


@flow(name="start_multiple_mcp_servers")
async def start_multiple_servers_flow(server_names: List[str]) -> Dict[str, Any]:
    """Prefect flow to start multiple MCP servers concurrently."""
    
    flow_logger = get_run_logger()
    flow_logger.info("Starting multiple MCP servers flow", 
                    extra={"server_names": server_names})
    
    # Start all servers concurrently
    start_tasks = [
        start_mcp_server_task(server_name)
        for server_name in server_names
    ]
    
    # Wait for all tasks to complete
    results = []
    for task_future in start_tasks:
        result = await task_future
        results.append(result)
    
    # Summarize results
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    summary = {
        "total_servers": len(server_names),
        "successful_starts": len(successful),
        "failed_starts": len(failed),
        "success_rate": len(successful) / len(server_names) if server_names else 0,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
    
    flow_logger.info("Multiple server start flow completed", extra=_clean_log_extra(summary))
    return summary


@flow(name="stop_multiple_mcp_servers")
async def stop_multiple_servers_flow(server_names: List[str], force: bool = False) -> Dict[str, Any]:
    """Prefect flow to stop multiple MCP servers concurrently."""
    
    flow_logger = get_run_logger()
    flow_logger.info("Stopping multiple MCP servers flow", 
                    extra={"server_names": server_names, "force": force})
    
    # Stop all servers concurrently
    stop_tasks = [
        stop_mcp_server_task(server_name, force=force)
        for server_name in server_names
    ]
    
    # Wait for all tasks to complete
    results = []
    for task_future in stop_tasks:
        result = await task_future
        results.append(result)
    
    # Summarize results
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    summary = {
        "total_servers": len(server_names),
        "successful_stops": len(successful),
        "failed_stops": len(failed),
        "success_rate": len(successful) / len(server_names) if server_names else 0,
        "force": force,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
    
    flow_logger.info("Multiple server stop flow completed", extra=_clean_log_extra(summary))
    return summary


@flow(name="health_check_all_servers")
async def health_check_all_servers_flow() -> Dict[str, Any]:
    """Prefect flow to perform health checks on all configured servers."""
    
    flow_logger = get_run_logger()
    flow_logger.info("Health checking all MCP servers flow")
    
    # Get all configured server names
    all_servers = config_manager.list_server_names()
    
    if not all_servers:
        flow_logger.info("No MCP servers configured")
        return {
            "total_servers": 0,
            "results": [],
            "timestamp": datetime.now().isoformat()
        }
    
    # Health check all servers concurrently
    health_tasks = [
        health_check_mcp_server_task(server_name)
        for server_name in all_servers
    ]
    
    # Wait for all tasks to complete
    results = []
    for task_future in health_tasks:
        result = await task_future
        results.append(result)
    
    # Analyze health status
    running_servers = [r for r in results if r.get("running", False)]
    healthy_servers = [r for r in results if r.get("health_status") == "healthy"]
    unhealthy_servers = [r for r in results if r.get("health_status") in ["unhealthy", "dead"]]
    
    summary = {
        "total_servers": len(all_servers),
        "running_servers": len(running_servers),
        "healthy_servers": len(healthy_servers),
        "unhealthy_servers": len(unhealthy_servers),
        "overall_health": "healthy" if len(healthy_servers) == len(all_servers) else "degraded",
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
    
    flow_logger.info("Health check all servers flow completed", extra=_clean_log_extra(summary))
    return summary


class MCPLifecycleService:
    """Service for managing MCP server lifecycles with workflow orchestration."""
    
    def __init__(self):
        """Initialize the lifecycle service."""
        self.logger = logger.bind(component="mcp_lifecycle_service")
        self.logger.info("MCP lifecycle service initialized")
    
    async def start_server(self, server_name: str) -> Dict[str, Any]:
        """Start a single MCP server."""
        
        self.logger.info("Starting MCP server", server_name=server_name)
        
        # Run the Prefect task
        result = await start_mcp_server_task(server_name)
        
        self.logger.info("MCP server start operation completed",
                        server_name=server_name,
                        success=result["success"])
        
        return result
    
    async def stop_server(self, server_name: str, force: bool = False) -> Dict[str, Any]:
        """Stop a single MCP server."""
        
        self.logger.info("Stopping MCP server", 
                        server_name=server_name, 
                        force=force)
        
        # Run the Prefect task
        result = await stop_mcp_server_task(server_name, force=force)
        
        self.logger.info("MCP server stop operation completed",
                        server_name=server_name,
                        success=result["success"])
        
        return result
    
    async def restart_server(self, server_name: str) -> Dict[str, Any]:
        """Restart a single MCP server."""
        
        self.logger.info("Restarting MCP server", server_name=server_name)
        
        # Run the Prefect task
        result = await restart_mcp_server_task(server_name)
        
        self.logger.info("MCP server restart operation completed",
                        server_name=server_name,
                        success=result["success"])
        
        return result
    
    async def start_multiple_servers(self, server_names: List[str]) -> Dict[str, Any]:
        """Start multiple MCP servers concurrently."""
        
        self.logger.info("Starting multiple MCP servers", 
                        server_names=server_names,
                        count=len(server_names))
        
        # Run the Prefect flow
        result = await start_multiple_servers_flow(server_names)
        
        self.logger.info("Multiple server start operation completed",
                        total_servers=result["total_servers"],
                        successful_starts=result["successful_starts"],
                        success_rate=result["success_rate"])
        
        return result
    
    async def stop_multiple_servers(self, server_names: List[str], force: bool = False) -> Dict[str, Any]:
        """Stop multiple MCP servers concurrently."""
        
        self.logger.info("Stopping multiple MCP servers", 
                        server_names=server_names,
                        count=len(server_names),
                        force=force)
        
        # Run the Prefect flow
        result = await stop_multiple_servers_flow(server_names, force=force)
        
        self.logger.info("Multiple server stop operation completed",
                        total_servers=result["total_servers"],
                        successful_stops=result["successful_stops"],
                        success_rate=result["success_rate"])
        
        return result
    
    async def get_server_status(self, server_name: str) -> Dict[str, Any]:
        """Get status of a specific MCP server."""
        
        status = environment_manager.get_server_status(server_name)
        
        self.logger.debug("Retrieved server status",
                         server_name=server_name,
                         status=status.get("status", "unknown"))
        
        return status
    
    async def get_all_servers_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all configured MCP servers."""
        
        all_status = environment_manager.get_all_server_status()
        
        self.logger.debug("Retrieved all servers status",
                         total_servers=len(all_status))
        
        return all_status
    
    async def health_check_all_servers(self) -> Dict[str, Any]:
        """Perform health checks on all configured servers."""
        
        self.logger.info("Performing health checks on all servers")
        
        # Run the Prefect flow
        result = await health_check_all_servers_flow()
        
        self.logger.info("Health check operation completed",
                        total_servers=result["total_servers"],
                        running_servers=result["running_servers"],
                        overall_health=result["overall_health"])
        
        return result
    
    async def get_available_servers(self) -> List[str]:
        """Get list of all configured server names."""
        
        servers = config_manager.list_server_names()
        
        self.logger.debug("Retrieved available servers", 
                         servers=servers,
                         count=len(servers))
        
        return servers


# Global lifecycle service instance
lifecycle_service = MCPLifecycleService()