"""
MCP (Model Context Protocol) server management for OpenRouter Anthropic Server.

This module provides proper lifecycle management, environment isolation,
and health monitoring for MCP servers with different runtime requirements.
"""

# Core MCP components
from .server_configs import MCPServerConfig, HealthCheckConfig, GlobalMCPConfig, MCPConfigManager, config_manager
from .environment_manager import environment_manager, MCPServerProcess
from .lifecycle_service import lifecycle_service

__all__ = [
    "config_manager",
    "MCPServerConfig",
    "HealthCheckConfig",
    "GlobalMCPConfig",
    "MCPConfigManager",
    "environment_manager",
    "MCPServerProcess",
    "lifecycle_service"
]