"""
MCP (Model Context Protocol) Service for LiteLLM integration.
Provides standardized tool integration and management capabilities.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..core.logging_config import get_logger
from ..utils.config import config
from .base import BaseService

logger = get_logger("mcp_service")

class MCPService(BaseService):
    """Service for managing MCP servers and tools."""
    
    def __init__(self):
        """Initialize MCP service."""
        super().__init__("MCP")
        self.mcp_servers: Dict[str, Dict[str, Any]] = {}
        self.available_tools: List[Dict[str, Any]] = []
        self.mcp_enabled = self._check_mcp_requirements()
    
    def _check_mcp_requirements(self) -> bool:
        """Check if MCP requirements are met (python>=3.10)."""
        try:
            import sys
            python_version = sys.version_info
            
            if python_version >= (3, 10):
                logger.info("MCP requirements met", python_version=f"{python_version.major}.{python_version.minor}")
                return True
            else:
                logger.warning("MCP requires Python 3.10+", current_version=f"{python_version.major}.{python_version.minor}")
                return False
                
        except Exception as e:
            logger.error("Failed to check MCP requirements", error=str(e))
            return False
    
    async def is_mcp_enabled(self) -> Dict[str, Any]:
        """Check if MCP is enabled."""
        return {
            "enabled": self.mcp_enabled,
            "python_version_compatible": self.mcp_enabled,
            "server_count": len(self.mcp_servers),
            "tool_count": len(self.available_tools)
        }
    
    async def add_mcp_server(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new MCP server configuration.
        
        Args:
            server_config: MCP server configuration
            
        Returns:
            Server creation result
        """
        try:
            if not self.mcp_enabled:
                raise ValueError("MCP not enabled - Python 3.10+ required")
            
            # Validate required fields
            required_fields = ["name", "url"]
            missing_fields = [field for field in required_fields if field not in server_config]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            server_name = server_config["name"]
            
            # Check if server already exists
            if server_name in self.mcp_servers:
                raise ValueError(f"MCP server '{server_name}' already exists")
            
            # Create server configuration
            server_id = f"mcp_{server_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            mcp_server = {
                "id": server_id,
                "name": server_name,
                "url": server_config["url"],
                "type": server_config.get("type", "sse"),  # sse, stdio, streamable_http
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "tools_count": 0,
                "metadata": server_config.get("metadata", {})
            }
            
            # Store server configuration
            self.mcp_servers[server_id] = mcp_server
            
            # Attempt to connect and list tools
            try:
                tools = await self._list_server_tools(server_id)
                mcp_server["tools_count"] = len(tools)
                self.available_tools.extend(tools)
                logger.info("MCP server added successfully", server_id=server_id, tools_count=len(tools))
            except Exception as e:
                logger.warning("Failed to list tools for new server", server_id=server_id, error=str(e))
                mcp_server["status"] = "error"
                mcp_server["error"] = str(e)
            
            self.log_operation("add_mcp_server", success=True, server_id=server_id, server_name=server_name)
            
            return {
                "success": True,
                "server_id": server_id,
                "server": mcp_server
            }
            
        except Exception as e:
            error_msg = f"Failed to add MCP server: {e}"
            logger.error("MCP server addition failed", error=error_msg, server_config=server_config)
            self.log_operation("add_mcp_server", success=False, error=error_msg)
            
            return {
                "success": False,
                "error": error_msg
            }
    
    async def list_mcp_servers(self, user_access: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List all configured MCP servers.
        
        Args:
            user_access: User access permissions for filtering
            
        Returns:
            List of MCP servers
        """
        try:
            # Filter servers based on user access (placeholder for enterprise features)
            accessible_servers = list(self.mcp_servers.values())
            
            return {
                "success": True,
                "servers": accessible_servers,
                "total_count": len(accessible_servers),
                "enabled": self.mcp_enabled
            }
            
        except Exception as e:
            error_msg = f"Failed to list MCP servers: {e}"
            logger.error("MCP server listing failed", error=error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "servers": []
            }
    
    async def get_mcp_server(self, server_id: str) -> Dict[str, Any]:
        """
        Get specific MCP server details.
        
        Args:
            server_id: MCP server ID
            
        Returns:
            Server details
        """
        try:
            if server_id not in self.mcp_servers:
                return {
                    "success": False,
                    "error": f"MCP server '{server_id}' not found"
                }
            
            server = self.mcp_servers[server_id]
            
            # Get current tool list
            try:
                tools = await self._list_server_tools(server_id)
                server["current_tools"] = tools
                server["tools_count"] = len(tools)
            except Exception as e:
                logger.warning("Failed to refresh tool list", server_id=server_id, error=str(e))
                server["tool_list_error"] = str(e)
            
            return {
                "success": True,
                "server": server
            }
            
        except Exception as e:
            error_msg = f"Failed to get MCP server: {e}"
            logger.error("MCP server retrieval failed", error=error_msg, server_id=server_id)
            
            return {
                "success": False,
                "error": error_msg
            }
    
    async def delete_mcp_server(self, server_id: str) -> Dict[str, Any]:
        """
        Delete an MCP server.
        
        Args:
            server_id: MCP server ID
            
        Returns:
            Deletion result
        """
        try:
            if server_id not in self.mcp_servers:
                return {
                    "success": False,
                    "error": f"MCP server '{server_id}' not found"
                }
            
            # Remove server
            deleted_server = self.mcp_servers.pop(server_id)
            
            # Remove tools from this server
            self.available_tools = [
                tool for tool in self.available_tools 
                if tool.get("server_id") != server_id
            ]
            
            logger.info("MCP server deleted", server_id=server_id, server_name=deleted_server.get("name"))
            self.log_operation("delete_mcp_server", success=True, server_id=server_id)
            
            return {
                "success": True,
                "message": f"MCP server '{server_id}' deleted successfully",
                "deleted_server": deleted_server
            }
            
        except Exception as e:
            error_msg = f"Failed to delete MCP server: {e}"
            logger.error("MCP server deletion failed", error=error_msg, server_id=server_id)
            self.log_operation("delete_mcp_server", success=False, error=error_msg)
            
            return {
                "success": False,
                "error": error_msg
            }
    
    async def list_mcp_tools(self, server_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List available MCP tools.
        
        Args:
            server_id: Optional specific server ID to filter tools
            
        Returns:
            List of available tools
        """
        try:
            if server_id:
                # Filter tools for specific server
                tools = [tool for tool in self.available_tools if tool.get("server_id") == server_id]
            else:
                # Return all tools
                tools = self.available_tools
            
            return {
                "success": True,
                "tools": tools,
                "total_count": len(tools),
                "server_count": len(self.mcp_servers)
            }
            
        except Exception as e:
            error_msg = f"Failed to list MCP tools: {e}"
            logger.error("MCP tool listing failed", error=error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "tools": []
            }
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any], server_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            server_id: Optional specific server ID
            
        Returns:
            Tool execution result
        """
        try:
            # Find the tool
            target_tool = None
            target_server_id = None
            
            for tool in self.available_tools:
                if tool.get("name") == tool_name:
                    if server_id is None or tool.get("server_id") == server_id:
                        target_tool = tool
                        target_server_id = tool.get("server_id")
                        break
            
            if not target_tool:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }
            
            if target_server_id not in self.mcp_servers:
                return {
                    "success": False,
                    "error": f"Server for tool '{tool_name}' not available"
                }
            
            # Execute tool call (placeholder - would need actual MCP client implementation)
            result = await self._execute_tool_call(target_server_id, tool_name, arguments)
            
            logger.info("MCP tool executed", tool_name=tool_name, server_id=target_server_id)
            self.log_operation("call_mcp_tool", success=True, tool_name=tool_name, server_id=target_server_id)
            
            return {
                "success": True,
                "tool_name": tool_name,
                "server_id": target_server_id,
                "result": result
            }
            
        except Exception as e:
            error_msg = f"Failed to call MCP tool: {e}"
            logger.error("MCP tool call failed", error=error_msg, tool_name=tool_name)
            self.log_operation("call_mcp_tool", success=False, error=error_msg)
            
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _list_server_tools(self, server_id: str) -> List[Dict[str, Any]]:
        """
        List tools for a specific MCP server.
        
        Args:
            server_id: MCP server ID
            
        Returns:
            List of tools from the server
        """
        # Placeholder implementation - would need actual MCP client
        # This would connect to the MCP server and call list_tools()
        
        server = self.mcp_servers.get(server_id)
        if not server:
            return []
        
        # Mock tools for demonstration
        mock_tools = [
            {
                "name": f"tool_{server['name']}_1",
                "description": f"Example tool from {server['name']}",
                "server_id": server_id,
                "schema": {
                    "type": "function",
                    "function": {
                        "name": f"tool_{server['name']}_1",
                        "description": f"Example tool from {server['name']}",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "input": {"type": "string", "description": "Tool input"}
                            },
                            "required": ["input"]
                        }
                    }
                }
            }
        ]
        
        return mock_tools
    
    async def _execute_tool_call(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call on an MCP server.
        
        Args:
            server_id: MCP server ID
            tool_name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        # Placeholder implementation - would need actual MCP client
        # This would connect to the MCP server and call the tool
        
        return {
            "status": "success",
            "content": f"Mock result from {tool_name} with arguments: {arguments}",
            "execution_time": "0.1s"
        }
    
    def transform_mcp_tools_to_openai_format(self, mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform MCP tools to OpenAI-compatible format.
        
        Args:
            mcp_tools: List of MCP tools
            
        Returns:
            List of OpenAI-compatible tools
        """
        try:
            openai_tools = []
            
            for tool in mcp_tools:
                if "schema" in tool and isinstance(tool["schema"], dict):
                    # Use existing schema if it's already in OpenAI format
                    openai_tools.append(tool["schema"])
                else:
                    # Convert basic tool info to OpenAI format
                    openai_tool = {
                        "type": "function",
                        "function": {
                            "name": tool.get("name", "unknown_tool"),
                            "description": tool.get("description", "MCP tool"),
                            "parameters": tool.get("parameters", {
                                "type": "object",
                                "properties": {},
                                "required": []
                            })
                        }
                    }
                    openai_tools.append(openai_tool)
            
            return openai_tools
            
        except Exception as e:
            logger.error("Failed to transform MCP tools to OpenAI format", error=str(e))
            return [] 