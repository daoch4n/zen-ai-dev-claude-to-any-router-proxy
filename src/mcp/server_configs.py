"""
MCP server configuration models and management.

This module defines the data structures for MCP server configurations
and provides utilities for loading and validating server definitions.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
import yaml

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class HealthCheckConfig(BaseModel):
    """Health check configuration for MCP servers."""
    enabled: bool = True
    endpoint: Optional[str] = None
    timeout: int = Field(default=5, ge=1, le=60)
    interval: int = Field(default=30, ge=5, le=300)


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""
    name: str
    description: Optional[str] = None
    type: str = Field(..., pattern="^(python|nodejs)$")
    command: str
    python_version: Optional[str] = None
    node_version: Optional[str] = None
    environment: Dict[str, str] = Field(default_factory=dict)
    health_check: HealthCheckConfig = Field(default_factory=HealthCheckConfig)
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    restart_policy: str = Field(default="on-failure", pattern="^(never|on-failure|always)$")
    max_restarts: int = Field(default=3, ge=0, le=10)
    
    @field_validator('python_version')
    @classmethod
    def validate_python_version(cls, v, info):
        if info.data.get('type') == 'python' and not v:
            raise ValueError("python_version is required for Python servers")
        return v
    
    @field_validator('node_version')
    @classmethod
    def validate_node_version(cls, v, info):
        if info.data.get('type') == 'nodejs' and not v:
            raise ValueError("node_version is required for Node.js servers")
        return v


class GlobalMCPConfig(BaseModel):
    """Global MCP server management configuration."""
    startup_timeout: int = Field(default=30, ge=5, le=120)
    shutdown_timeout: int = Field(default=10, ge=1, le=60)
    log_directory: str = Field(default="logs/mcp", description="MCP logs directory")
    enable_monitoring: bool = True
    monitoring_interval: int = Field(default=60, ge=10, le=300)


class MCPConfigManager:
    """Manager for loading and validating MCP server configurations."""
    
    def __init__(self, config_path: str = "configs/mcp_servers.yaml"):
        """Initialize the configuration manager."""
        self.config_path = Path(config_path)
        self.logger = logger.bind(component="mcp_config_manager")
        self._servers: Dict[str, MCPServerConfig] = {}
        self._global_config: Optional[GlobalMCPConfig] = None
        
    def load_configuration(self) -> bool:
        """Load MCP server configurations from YAML file."""
        
        if not self.config_path.exists():
            self.logger.warning(
                "MCP configuration file not found",
                config_path=str(self.config_path)
            )
            self._global_config = GlobalMCPConfig()
            return False
        
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            self.logger.info(
                "Loading MCP server configurations",
                config_path=str(self.config_path)
            )
            
            # Load global configuration
            global_data = config_data.get('global', {})
            self._global_config = GlobalMCPConfig(**global_data)
            
            # Load server configurations
            servers_data = config_data.get('servers', {})
            self._servers = {}
            
            for server_name, server_config in servers_data.items():
                try:
                    # Ensure name matches key
                    server_config['name'] = server_name
                    
                    # Validate and create server config
                    server = MCPServerConfig(**server_config)
                    self._servers[server_name] = server
                    
                    self.logger.info(
                        "Loaded MCP server configuration",
                        server_name=server_name,
                        server_type=server.type,
                        command=server.command
                    )
                    
                except Exception as e:
                    self.logger.error(
                        "Failed to load server configuration",
                        server_name=server_name,
                        error=str(e),
                        error_type=type(e).__name__
                    )
            
            self.logger.info(
                "MCP configuration loading completed",
                total_servers=len(self._servers),
                loaded_servers=list(self._servers.keys())
            )
            return True
            
        except Exception as e:
            self.logger.error(
                "Failed to load MCP configuration file",
                config_path=str(self.config_path),
                error=str(e),
                error_type=type(e).__name__
            )
            # Fallback to default configuration
            self._global_config = GlobalMCPConfig()
            self._servers = {}
            return False
    
    def get_server_config(self, server_name: str) -> Optional[MCPServerConfig]:
        """Get configuration for a specific server."""
        return self._servers.get(server_name)
    
    def get_all_servers(self) -> Dict[str, MCPServerConfig]:
        """Get all server configurations."""
        return self._servers.copy()
    
    def get_global_config(self) -> GlobalMCPConfig:
        """Get global MCP configuration."""
        if self._global_config is None:
            self._global_config = GlobalMCPConfig()
        return self._global_config
    
    def list_server_names(self) -> List[str]:
        """Get list of all configured server names."""
        return list(self._servers.keys())
    
    def get_servers_by_type(self, server_type: str) -> Dict[str, MCPServerConfig]:
        """Get all servers of a specific type (python/nodejs)."""
        return {
            name: config 
            for name, config in self._servers.items() 
            if config.type == server_type
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the current configuration and return validation results."""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "server_count": len(self._servers)
        }
        
        # Check for duplicate commands
        commands = {}
        for name, config in self._servers.items():
            if config.command in commands:
                validation_result["errors"].append(
                    f"Duplicate command '{config.command}' found in servers: "
                    f"{commands[config.command]} and {name}"
                )
                validation_result["valid"] = False
            else:
                commands[config.command] = name
        
        # Check for conflicting health check endpoints
        endpoints = {}
        for name, config in self._servers.items():
            if config.health_check.enabled and config.health_check.endpoint:
                endpoint = config.health_check.endpoint
                if endpoint in endpoints:
                    validation_result["errors"].append(
                        f"Duplicate health check endpoint '{endpoint}' found in servers: "
                        f"{endpoints[endpoint]} and {name}"
                    )
                    validation_result["valid"] = False
                else:
                    endpoints[endpoint] = name
        
        # Check for missing version specifications
        for name, config in self._servers.items():
            if config.type == "python" and not config.python_version:
                validation_result["warnings"].append(
                    f"Server '{name}' (Python) missing python_version specification"
                )
            elif config.type == "nodejs" and not config.node_version:
                validation_result["warnings"].append(
                    f"Server '{name}' (Node.js) missing node_version specification"
                )
        
        self.logger.info(
            "MCP configuration validation completed",
            valid=validation_result["valid"],
            error_count=len(validation_result["errors"]),
            warning_count=len(validation_result["warnings"])
        )
        
        return validation_result


# Global configuration manager instance
config_manager = MCPConfigManager()