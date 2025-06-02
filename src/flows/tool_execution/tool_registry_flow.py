"""Tool registry flow for mapping and executing tools."""

from typing import Any, Dict, List
from ...tasks.tool_execution.tool_result_formatting_tasks import ToolExecutionResult
from ...core.logging_config import get_logger

logger = get_logger("tool_execution.registry")


class ToolRegistryFlow:
    """Maps Claude Code tool names to the new task-based execution functions"""
    
    def __init__(self):
        """Initialize tool registry with task-based coordinator"""
        # Import the new tool coordinator
        from ...coordinators.tool_coordinator import tool_coordinator
        self.coordinator = tool_coordinator
        
        # Available tools mapping (for compatibility)
        self.tools = {
            "Write": self._execute_via_coordinator,
            "Read": self._execute_via_coordinator,
            "Edit": self._execute_via_coordinator,
            "MultiEdit": self._execute_via_coordinator,
            "Glob": self._execute_via_coordinator,
            "Grep": self._execute_via_coordinator,
            "LS": self._execute_via_coordinator,
            "Bash": self._execute_via_coordinator,
            "Task": self._execute_via_coordinator,
            "WebSearch": self._execute_via_coordinator,
            "WebFetch": self._execute_via_coordinator,
            "NotebookRead": self._execute_via_coordinator,
            "NotebookEdit": self._execute_via_coordinator,
            "TodoRead": self._execute_via_coordinator,
            "TodoWrite": self._execute_via_coordinator,
        }
        
        logger.info("Initialized task-based tool registry", tool_count=len(self.tools))
    
    async def execute_tool(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute a tool using the task-based coordinator"""
        try:
            # Use the coordinator for execution
            result = await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
            return result
        except Exception as e:
            logger.error("Tool execution failed in registry",
                        tool_name=tool_name,
                        error=str(e),
                        exc_info=True)
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=str(e),
                execution_time=0.0
            )
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())
    
    def is_tool_available(self, tool_name: str) -> bool:
        """Check if a tool is available"""
        return tool_name in self.tools
    
    async def _execute_via_coordinator(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute tool via coordinator (unified method for all tools)"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)