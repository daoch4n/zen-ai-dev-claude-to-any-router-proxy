"""
MCP server environment management with proper isolation.

This module handles environment setup, process lifecycle management,
and proper isolation for different Python/Node.js versions.
"""

import asyncio
import os
import signal
import subprocess
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.mcp.server_configs import MCPServerConfig, config_manager
from src.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class MCPServerProcess:
    """Represents a running MCP server process."""
    name: str
    config: MCPServerConfig
    process: subprocess.Popen
    pid: int
    started_at: datetime
    restart_count: int = 0
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"  # unknown, healthy, unhealthy


class MCPEnvironmentManager:
    """Manages MCP server environments with proper isolation."""
    
    def __init__(self):
        """Initialize the environment manager."""
        self.logger = logger.bind(component="mcp_environment_manager")
        self.running_servers: Dict[str, MCPServerProcess] = {}
        self.global_config = config_manager.get_global_config()
        
        # Ensure log directory exists
        self.log_dir = Path(self.global_config.log_directory)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("MCP environment manager initialized",
                        log_directory=str(self.log_dir),
                        monitoring_enabled=self.global_config.enable_monitoring)
    
    async def start_server(self, server_name: str) -> bool:
        """Start an MCP server with proper environment isolation."""
        
        server_config = config_manager.get_server_config(server_name)
        if not server_config:
            self.logger.error("Server configuration not found", server_name=server_name)
            return False
        
        if server_name in self.running_servers:
            self.logger.warning("Server already running", server_name=server_name)
            return True
        
        server_logger = self.logger.bind(
            server_name=server_name,
            server_type=server_config.type,
            command=server_config.command
        )
        
        server_logger.info("Starting MCP server")
        
        try:
            # Prepare environment
            env = await self._prepare_server_environment(server_config)
            
            # Set up logging
            log_file = self.log_dir / f"{server_name}.log"
            
            # Start the process
            process = await self._spawn_server_process(
                server_config=server_config,
                env=env,
                log_file=log_file
            )
            
            # Create server process record
            server_process = MCPServerProcess(
                name=server_name,
                config=server_config,
                process=process,
                pid=process.pid,
                started_at=datetime.now()
            )
            
            self.running_servers[server_name] = server_process
            
            server_logger.info("MCP server started successfully",
                              pid=process.pid,
                              log_file=str(log_file))
            
            # Wait a moment and check if process is still running
            await asyncio.sleep(2)
            
            if process.poll() is not None:
                # Process died immediately
                server_logger.error("MCP server died immediately after startup",
                                   return_code=process.returncode)
                self.running_servers.pop(server_name, None)
                return False
            
            # Schedule health check if enabled
            if server_config.health_check.enabled:
                asyncio.create_task(self._monitor_server_health(server_name))
            
            return True
            
        except Exception as e:
            server_logger.error("Failed to start MCP server",
                               error=str(e),
                               error_type=type(e).__name__)
            return False
    
    async def stop_server(self, server_name: str, force: bool = False) -> bool:
        """Stop an MCP server gracefully or forcefully."""
        
        if server_name not in self.running_servers:
            self.logger.warning("Server not running", server_name=server_name)
            return True
        
        server_process = self.running_servers[server_name]
        server_logger = self.logger.bind(
            server_name=server_name,
            pid=server_process.pid
        )
        
        server_logger.info("Stopping MCP server", force=force)
        
        try:
            if force:
                # Force kill
                server_process.process.kill()
                server_logger.info("MCP server force killed")
            else:
                # Graceful shutdown
                server_process.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    await asyncio.wait_for(
                        asyncio.create_task(self._wait_for_process_exit(server_process.process)),
                        timeout=self.global_config.shutdown_timeout
                    )
                    server_logger.info("MCP server stopped gracefully")
                except asyncio.TimeoutError:
                    server_logger.warning("Graceful shutdown timed out, force killing")
                    server_process.process.kill()
            
            # Remove from running servers
            self.running_servers.pop(server_name, None)
            return True
            
        except Exception as e:
            server_logger.error("Failed to stop MCP server",
                               error=str(e),
                               error_type=type(e).__name__)
            return False
    
    async def restart_server(self, server_name: str) -> bool:
        """Restart an MCP server."""
        
        server_logger = self.logger.bind(server_name=server_name)
        server_logger.info("Restarting MCP server")
        
        # Check restart limits
        if server_name in self.running_servers:
            server_process = self.running_servers[server_name]
            if server_process.restart_count >= server_process.config.max_restarts:
                server_logger.error("Maximum restart attempts reached",
                                   restart_count=server_process.restart_count,
                                   max_restarts=server_process.config.max_restarts)
                return False
        
        # Stop the server
        await self.stop_server(server_name)
        
        # Wait a moment before restarting
        await asyncio.sleep(1)
        
        # Start the server
        success = await self.start_server(server_name)
        
        if success and server_name in self.running_servers:
            self.running_servers[server_name].restart_count += 1
            server_logger.info("MCP server restarted successfully",
                              restart_count=self.running_servers[server_name].restart_count)
        
        return success
    
    def get_server_status(self, server_name: str) -> Dict[str, Any]:
        """Get detailed status of an MCP server."""
        
        if server_name not in self.running_servers:
            return {
                "name": server_name,
                "status": "stopped",
                "running": False
            }
        
        server_process = self.running_servers[server_name]
        
        # Check if process is still running
        is_running = server_process.process.poll() is None
        uptime = datetime.now() - server_process.started_at if is_running else None
        
        return {
            "name": server_name,
            "status": "running" if is_running else "dead",
            "running": is_running,
            "pid": server_process.pid,
            "started_at": server_process.started_at.isoformat(),
            "uptime_seconds": uptime.total_seconds() if uptime else None,
            "restart_count": server_process.restart_count,
            "health_status": server_process.health_status,
            "last_health_check": server_process.last_health_check.isoformat() if server_process.last_health_check else None,
            "config": {
                "type": server_process.config.type,
                "command": server_process.config.command,
                "restart_policy": server_process.config.restart_policy
            }
        }
    
    def get_all_server_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all configured servers."""
        
        all_servers = config_manager.list_server_names()
        return {
            server_name: self.get_server_status(server_name)
            for server_name in all_servers
        }
    
    async def _prepare_server_environment(self, config: MCPServerConfig) -> Dict[str, str]:
        """Prepare environment variables for a server."""
        
        # Start with current environment
        env = os.environ.copy()
        
        # Add server-specific environment variables
        env.update(config.environment)
        
        # Set log level
        env["LOG_LEVEL"] = config.log_level
        
        # Add Python/Node.js version specific paths
        if config.type == "python" and config.python_version:
            # Add Python version specific paths
            python_path = f"/usr/bin/python{config.python_version}"
            if Path(python_path).exists():
                env["PYTHON"] = python_path
        
        elif config.type == "nodejs" and config.node_version:
            # Add Node.js version specific paths
            node_path = f"/home/luke/.nvm/versions/node/v{config.node_version}/bin"
            if Path(node_path).exists():
                env["PATH"] = f"{node_path}:{env.get('PATH', '')}"
        
        self.logger.debug("Prepared server environment",
                         server_name=config.name,
                         env_vars=list(config.environment.keys()))
        
        return env
    
    async def _spawn_server_process(
        self,
        server_config: MCPServerConfig,
        env: Dict[str, str],
        log_file: Path
    ) -> subprocess.Popen:
        """Spawn the actual server process."""
        
        # Open log file for writing
        log_handle = open(log_file, 'a')
        
        # Split command into parts
        cmd_parts = server_config.command.split()
        
        # Start the process
        process = subprocess.Popen(
            cmd_parts,
            env=env,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid  # Create new process group
        )
        
        self.logger.debug("Server process spawned",
                         server_name=server_config.name,
                         command=server_config.command,
                         pid=process.pid)
        
        return process
    
    async def _wait_for_process_exit(self, process: subprocess.Popen) -> None:
        """Wait for a process to exit (async)."""
        while process.poll() is None:
            await asyncio.sleep(0.1)
    
    async def _monitor_server_health(self, server_name: str) -> None:
        """Monitor server health continuously."""
        
        if server_name not in self.running_servers:
            return
        
        server_process = self.running_servers[server_name]
        config = server_process.config
        
        if not config.health_check.enabled or not config.health_check.endpoint:
            return
        
        monitor_logger = self.logger.bind(
            server_name=server_name,
            health_endpoint=config.health_check.endpoint
        )
        
        monitor_logger.info("Starting health monitoring")
        
        while server_name in self.running_servers:
            try:
                # Simple HTTP health check (could be enhanced with actual HTTP client)
                # For now, just check if process is running
                process = self.running_servers[server_name].process
                
                if process.poll() is None:
                    # Process is running
                    self.running_servers[server_name].health_status = "healthy"
                    self.running_servers[server_name].last_health_check = datetime.now()
                    monitor_logger.debug("Health check passed")
                else:
                    # Process died
                    self.running_servers[server_name].health_status = "dead"
                    monitor_logger.warning("Health check failed - process dead")
                    
                    # Handle restart policy
                    if config.restart_policy == "on-failure":
                        monitor_logger.info("Attempting automatic restart")
                        await self.restart_server(server_name)
                    
                    break
                
                # Wait for next check
                await asyncio.sleep(config.health_check.interval)
                
            except Exception as e:
                monitor_logger.error("Health check error",
                                   error=str(e),
                                   error_type=type(e).__name__)
                self.running_servers[server_name].health_status = "unhealthy"
                await asyncio.sleep(config.health_check.interval)
        
        monitor_logger.info("Health monitoring stopped")


# Global environment manager instance
environment_manager = MCPEnvironmentManager()