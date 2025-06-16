"""
Claude Code Tool Execution Service optimized for Claude Code CLI workflows.

This module implements the comprehensive tool execution framework as outlined in the
Master Implementation Plan Phase 1.2 - Tool Execution Framework.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

from src.core.logging_config import get_logger
from src.utils.config import config

logger = get_logger(__name__)


class ClaudeCodeToolService:
    """Tool execution service optimized for Claude Code CLI."""
    
    def __init__(self):
        """Initialize the Claude Code tool service."""
        # Tools identified from Claude Code CLI API analysis
        self.claude_code_tools = {
            # Core Claude Code Tools
            "str_replace_editor": {
                "timeout": 15, 
                "category": "file_ops",
                "description": "String replacement based file editor",
                "requires_content": True
            },
            "bash": {
                "timeout": 30, 
                "category": "system", 
                "security": "sandboxed",
                "description": "Execute bash commands",
                "requires_permission": True
            },
            "computer": {
                "timeout": 45, 
                "category": "system", 
                "requires_permission": True,
                "description": "Computer control and screen interaction",
                "security": "restricted"
            },
            
            # Enhanced File Operations
            "read_file": {
                "timeout": 10, 
                "max_size": "10MB",
                "category": "file_ops",
                "description": "Read file contents"
            },
            "write_file": {
                "timeout": 10, 
                "max_size": "10MB",
                "category": "file_ops", 
                "description": "Write content to file"
            },
            "edit_file": {
                "timeout": 20, 
                "max_size": "10MB",
                "category": "file_ops",
                "description": "Edit existing file content"
            },
            "list_dir": {
                "timeout": 5,
                "category": "file_ops",
                "description": "List directory contents"
            },
            "file_search": {
                "timeout": 15,
                "category": "search",
                "description": "Search for files by name pattern"
            },
            "grep_search": {
                "timeout": 20,
                "category": "search", 
                "description": "Search file contents using grep"
            },
            "codebase_search": {
                "timeout": 30,
                "category": "search",
                "description": "Semantic search across codebase"
            },
            
            # Development Tools
            "run_terminal_cmd": {
                "timeout": 60, 
                "security": "restricted",
                "category": "system",
                "description": "Execute terminal commands"
            },
            "create_diagram": {
                "timeout": 10,
                "category": "generation",
                "description": "Create diagrams and visualizations"
            },
            "web_search": {
                "timeout": 25,
                "category": "web",
                "description": "Search the web for information"
            },
            
            # Notebook Operations
            "edit_notebook": {
                "timeout": 15,
                "category": "notebook",
                "description": "Edit Jupyter notebook cells"
            },
            "run_notebook_cell": {
                "timeout": 45,
                "category": "notebook",
                "description": "Execute notebook cell"
            }
        }
        
        # Performance tracking
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_response_time": 0.0,
            "tool_usage": {},
            "error_types": {}
        }
        
        # Security settings
        self.security_settings = {
            "allow_file_operations": True,
            "allow_system_commands": True,
            "allow_web_access": True,
            "max_file_size_mb": 10,
            "restricted_paths": ["/etc", "/var", "/sys", "/proc"],
            "allowed_commands": ["ls", "cat", "echo", "grep", "find", "pwd", "which", "uv"]
        }
    
    def _has_permission(self, tool_name: str) -> bool:
        """Check if tool has required permissions."""
        tool_config = self.claude_code_tools.get(tool_name, {})
        
        if not tool_config.get("requires_permission", False):
            return True
        
        # Check specific permissions based on tool category
        category = tool_config.get("category", "")
        
        if category == "system":
            return self.security_settings.get("allow_system_commands", False)
        elif category == "file_ops":
            return self.security_settings.get("allow_file_operations", True)
        elif category == "web":
            return self.security_settings.get("allow_web_access", True)
        
        # Default to allowed for other categories
        return True
    
    def _validate_tool_arguments(self, tool_call: Dict, tool_config: Dict) -> Dict:
        """Validate and sanitize tool arguments."""
        function_data = tool_call.get("function", {})
        tool_name = function_data.get("name", "")
        
        try:
            arguments = json.loads(function_data.get("arguments", "{}"))
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON arguments: {e}", "tool": tool_name}
        
        # Category-specific validation
        category = tool_config.get("category", "")
        
        if category == "file_ops":
            # Validate file paths
            file_path = arguments.get("file_path") or arguments.get("path") or arguments.get("filename")
            if file_path:
                # Check for restricted paths
                for restricted in self.security_settings["restricted_paths"]:
                    if str(file_path).startswith(restricted):
                        return {"error": f"Access denied to restricted path: {file_path}", "tool": tool_name}
        
        elif category == "system":
            # Validate system commands
            command = arguments.get("command", "")
            if command:
                # Extract base command
                base_cmd = command.split()[0] if command.split() else ""
                allowed_commands = self.security_settings["allowed_commands"]
                
                if base_cmd not in allowed_commands:
                    return {"error": f"Command not allowed: {base_cmd}", "tool": tool_name}
        
        return {"valid": True, "arguments": arguments}
    
    async def _execute_with_claude_code_optimizations(
        self, 
        tool_call: Dict, 
        tool_config: Dict,
        context: Dict = None
    ) -> Dict:
        """Execute tool with Claude Code CLI optimizations."""
        
        function_data = tool_call.get("function", {})
        tool_name = function_data.get("name", "")
        
        # Validate arguments
        validation_result = self._validate_tool_arguments(tool_call, tool_config)
        if "error" in validation_result:
            return validation_result
        
        arguments = validation_result["arguments"]
        timeout = tool_config.get("timeout", 30)
        
        start_time = time.time()
        
        try:
            # Route to specific tool execution based on tool name
            result = await self._route_tool_execution(tool_name, arguments, timeout, context)
            
            execution_time = time.time() - start_time
            
            # Update statistics
            self._update_execution_stats(tool_name, execution_time, success=True)
            
            # Format result for Claude Code CLI
            return self._format_claude_code_result(result, tool_name, execution_time)
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            self._update_execution_stats(tool_name, execution_time, success=False, error_type="timeout")
            
            return {
                "error": f"Tool execution timed out after {timeout}s",
                "tool": tool_name,
                "execution_time": execution_time
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_type = type(e).__name__
            self._update_execution_stats(tool_name, execution_time, success=False, error_type=error_type)
            
            logger.error("Tool execution failed", 
                        tool=tool_name, 
                        error=str(e), 
                        error_type=error_type,
                        execution_time=execution_time)
            
            return {
                "error": f"Tool execution failed: {str(e)}", 
                "tool": tool_name,
                "error_type": error_type,
                "execution_time": execution_time
            }
    
    async def _route_tool_execution(
        self, 
        tool_name: str, 
        arguments: Dict, 
        timeout: int,
        context: Dict = None
    ) -> Dict:
        """Route tool execution to appropriate handler."""
        
        # Import tool execution service
        from src.services.tool_execution import ToolExecutionService
        tool_service = ToolExecutionService()
        
        # Execute with timeout
        result = await asyncio.wait_for(
            tool_service.execute_tool(tool_name, arguments, context or {}),
            timeout=timeout
        )
        
        return result
    
    def _format_claude_code_result(self, result: Dict, tool_name: str, execution_time: float) -> Dict:
        """Format tool execution result for Claude Code CLI."""
        
        # Base formatted result
        formatted_result = {
            "tool": tool_name,
            "execution_time": round(execution_time, 3),
            "timestamp": datetime.utcnow().isoformat(),
            "success": True
        }
        
        # Add tool-specific formatting
        tool_config = self.claude_code_tools.get(tool_name, {})
        category = tool_config.get("category", "")
        
        if category == "file_ops":
            # File operation specific formatting
            if "content" in result:
                formatted_result["content"] = result["content"]
            if "file_path" in result:
                formatted_result["file_path"] = result["file_path"]
            if "files" in result:
                formatted_result["files"] = result["files"]
        
        elif category == "system":
            # System command specific formatting
            if "output" in result:
                formatted_result["output"] = result["output"]
            if "exit_code" in result:
                formatted_result["exit_code"] = result["exit_code"]
            if "stderr" in result:
                formatted_result["stderr"] = result["stderr"]
        
        elif category == "search":
            # Search specific formatting
            if "results" in result:
                formatted_result["results"] = result["results"]
            if "matches" in result:
                formatted_result["matches"] = result["matches"]
            if "total_results" in result:
                formatted_result["total_results"] = result["total_results"]
        
        elif category == "web":
            # Web specific formatting
            if "content" in result:
                formatted_result["content"] = result["content"]
            if "url" in result:
                formatted_result["url"] = result["url"]
            if "title" in result:
                formatted_result["title"] = result["title"]
        
        # Include original result data
        formatted_result["data"] = result
        
        return formatted_result
    
    async def _handle_claude_code_tool_error(
        self, 
        error: Exception, 
        tool_name: str, 
        context: Dict
    ) -> Dict:
        """Handle errors with Claude Code CLI specific recovery strategies."""
        
        error_type = type(error).__name__
        
        # Claude Code specific error handling strategies
        recovery_strategies = {
            "TimeoutError": self._handle_timeout_error,
            "PermissionError": self._handle_permission_error,
            "FileNotFoundError": self._handle_file_not_found_error,
            "ConnectionError": self._handle_connection_error,
            "JSONDecodeError": self._handle_json_decode_error
        }
        
        recovery_handler = recovery_strategies.get(error_type)
        
        if recovery_handler:
            try:
                recovery_result = await recovery_handler(error, tool_name, context)
                if recovery_result:
                    return recovery_result
            except Exception as recovery_error:
                logger.warning("Error recovery failed", 
                             original_error=str(error),
                             recovery_error=str(recovery_error),
                             tool=tool_name)
        
        # Return standard error format
        return {
            "error": str(error),
            "error_type": error_type,
            "tool": tool_name,
            "recovery_attempted": recovery_handler is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_timeout_error(self, error: Exception, tool_name: str, context: Dict) -> Optional[Dict]:
        """Handle timeout errors with retry strategy."""
        tool_config = self.claude_code_tools.get(tool_name, {})
        
        # Suggest shorter timeout for retry
        suggested_timeout = max(5, tool_config.get("timeout", 30) // 2)
        
        return {
            "error": "Tool execution timed out",
            "tool": tool_name,
            "recovery_suggestion": f"Consider reducing complexity or retry with timeout={suggested_timeout}s",
            "can_retry": True
        }
    
    async def _handle_permission_error(self, error: Exception, tool_name: str, context: Dict) -> Optional[Dict]:
        """Handle permission errors."""
        return {
            "error": "Permission denied",
            "tool": tool_name,
            "recovery_suggestion": "Check file permissions or run with elevated privileges",
            "can_retry": False
        }
    
    async def _handle_file_not_found_error(self, error: Exception, tool_name: str, context: Dict) -> Optional[Dict]:
        """Handle file not found errors."""
        return {
            "error": "File or directory not found",
            "tool": tool_name,
            "recovery_suggestion": "Verify the file path exists or create the required directory",
            "can_retry": True
        }
    
    async def _handle_connection_error(self, error: Exception, tool_name: str, context: Dict) -> Optional[Dict]:
        """Handle connection errors for web tools."""
        return {
            "error": "Network connection failed",
            "tool": tool_name,
            "recovery_suggestion": "Check internet connection and retry",
            "can_retry": True
        }
    
    async def _handle_json_decode_error(self, error: Exception, tool_name: str, context: Dict) -> Optional[Dict]:
        """Handle JSON decode errors."""
        return {
            "error": "Invalid JSON format in tool arguments",
            "tool": tool_name,
            "recovery_suggestion": "Verify argument format and retry",
            "can_retry": True
        }
    
    def _update_execution_stats(
        self, 
        tool_name: str, 
        execution_time: float, 
        success: bool = True,
        error_type: str = None
    ):
        """Update execution statistics."""
        self.execution_stats["total_executions"] += 1
        
        if success:
            self.execution_stats["successful_executions"] += 1
        else:
            self.execution_stats["failed_executions"] += 1
            
            if error_type:
                if error_type not in self.execution_stats["error_types"]:
                    self.execution_stats["error_types"][error_type] = 0
                self.execution_stats["error_types"][error_type] += 1
        
        # Update tool usage statistics
        if tool_name not in self.execution_stats["tool_usage"]:
            self.execution_stats["tool_usage"][tool_name] = {
                "count": 0,
                "total_time": 0,
                "success_count": 0,
                "failure_count": 0
            }
        
        tool_stats = self.execution_stats["tool_usage"][tool_name]
        tool_stats["count"] += 1
        tool_stats["total_time"] += execution_time
        
        if success:
            tool_stats["success_count"] += 1
        else:
            tool_stats["failure_count"] += 1
        
        # Update average response time
        total_time = sum(
            stats["total_time"] for stats in self.execution_stats["tool_usage"].values()
        )
        self.execution_stats["average_response_time"] = total_time / self.execution_stats["total_executions"]
    
    async def execute_claude_code_tool(
        self, 
        tool_call: Dict, 
        context: Dict = None
    ) -> Dict:
        """Execute tool with Claude Code CLI optimizations."""
        
        function_data = tool_call.get("function", {})
        tool_name = function_data.get("name", "")
        
        if tool_name not in self.claude_code_tools:
            return {
                "error": f"Unknown tool: {tool_name}",
                "tool": tool_name,
                "available_tools": list(self.claude_code_tools.keys())
            }
        
        tool_config = self.claude_code_tools[tool_name]
        
        # Security validation
        if tool_config.get("requires_permission") and not self._has_permission(tool_name):
            return {
                "error": "Tool requires explicit permission", 
                "tool": tool_name,
                "required_permission": tool_config.get("category", "unknown")
            }
        
        # Execute with timeout and error handling
        try:
            result = await self._execute_with_claude_code_optimizations(
                tool_call, 
                tool_config,
                context
            )
            return result
            
        except Exception as e:
            return await self._handle_claude_code_tool_error(e, tool_name, context or {})
    
    def get_claude_code_tool_stats(self) -> Dict:
        """Get comprehensive Claude Code tool execution statistics."""
        stats = self.execution_stats.copy()
        
        # Calculate success rate
        total = stats["total_executions"]
        if total > 0:
            stats["success_rate"] = stats["successful_executions"] / total
            stats["failure_rate"] = stats["failed_executions"] / total
        else:
            stats["success_rate"] = 0.0
            stats["failure_rate"] = 0.0
        
        # Add tool-specific metrics
        for tool_name, tool_stats in stats["tool_usage"].items():
            if tool_stats["count"] > 0:
                tool_stats["average_time"] = tool_stats["total_time"] / tool_stats["count"]
                tool_stats["success_rate"] = tool_stats["success_count"] / tool_stats["count"]
            else:
                tool_stats["average_time"] = 0.0
                tool_stats["success_rate"] = 0.0
        
        # Add configuration info
        stats["configured_tools"] = len(self.claude_code_tools)
        stats["security_settings"] = self.security_settings.copy()
        
        return stats
    
    def get_available_claude_code_tools(self) -> Dict:
        """Get list of available Claude Code tools with descriptions."""
        return {
            tool_name: {
                "description": config.get("description", ""),
                "category": config.get("category", ""),
                "timeout": config.get("timeout", 30),
                "requires_permission": config.get("requires_permission", False)
            }
            for tool_name, config in self.claude_code_tools.items()
        } 