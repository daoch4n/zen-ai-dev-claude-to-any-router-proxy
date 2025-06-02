"""Tool execution service for OpenRouter Anthropic Server.

This is the new modular implementation that replaces the monolithic tool_execution.py.
It maintains full backward compatibility while using the new task-based architecture.
"""

from typing import Any, Dict, List
from .base import BaseService
from ..coordinators.tool_execution_coordinator import tool_execution_coordinator
from ..tasks.tool_execution.tool_result_formatting_tasks import ToolExecutionResult
from ..models.anthropic import MessagesRequest
from ..core.logging_config import get_logger

logger = get_logger("tool_execution")


# Export the classes and exceptions for backward compatibility
from ..tasks.tool_execution.tool_execution_tasks import (
    ToolExecutionError,
    ToolTimeoutError,
    ToolValidationError,
    ToolPermissionError
)

# Export the result formatting classes
from ..tasks.tool_execution.tool_result_formatting_tasks import (
    ToolExecutionResult
)


class ToolResultFormatter:
    """Formats tool execution results into Anthropic tool_result format
    
    This class is maintained for backward compatibility.
    """
    
    def create_tool_result_block(self, result: ToolExecutionResult) -> Dict[str, Any]:
        """Create tool_result block for API response"""
        from ..tasks.tool_execution.tool_result_formatting_tasks import create_tool_result_block
        return create_tool_result_block(result)
    
    def _format_result_content(self, result: ToolExecutionResult) -> str:
        """Format result content for backward compatibility"""
        if hasattr(result, 'result'):
            if result.result is None:
                return "Tool executed successfully"
            elif isinstance(result.result, dict):
                import json
                return json.dumps(result.result, indent=2)
            return str(result.result)
        return str(result)


class ToolRegistry:
    """Maps Claude Code tool names to the new task-based execution functions
    
    This class is maintained for backward compatibility.
    """
    
    def __init__(self):
        """Initialize tool registry"""
        # Delegate to the coordinator's registry
        self._registry = tool_execution_coordinator.registry_flow
        logger.info("ToolRegistry initialized (legacy compatibility layer)")
    
    async def execute_tool(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute a tool using the task-based coordinator"""
        return await self._registry.execute_tool(tool_call_id, tool_name, tool_input)
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return self._registry.get_available_tools()


class ToolUseDetector:
    """Detects tool_use blocks in LiteLLM responses
    
    This class is maintained for backward compatibility.
    """
    
    @staticmethod
    def has_tool_use_blocks(response: Any) -> bool:
        """Check if LiteLLM response contains tool_use blocks"""
        from ..tasks.tool_execution.tool_detection_tasks import detect_tool_use_blocks
        return detect_tool_use_blocks(response)
    
    @staticmethod
    def extract_tool_use_blocks(response: Any) -> List[Dict[str, Any]]:
        """Extract tool_use blocks from LiteLLM response"""
        from ..tasks.tool_execution.tool_detection_tasks import extract_tool_use_blocks
        return extract_tool_use_blocks(response)


class ConversationContinuation:
    """Handles continuing conversation after tool execution
    
    This class is maintained for backward compatibility.
    """
    
    def __init__(self, http_client):
        """Initialize conversation continuation with HTTP client"""
        # Delegate to the coordinator's continuation flow
        self._continuation = tool_execution_coordinator.continuation_flow
        logger.info("ConversationContinuation initialized (legacy compatibility layer)")
    
    async def create_tool_result_messages(
        self,
        original_messages: List,
        tool_use_response: Any,
        tool_results: List[ToolExecutionResult]
    ) -> List[Dict[str, Any]]:
        """Create the message sequence for continuing conversation"""
        from ..tasks.tool_execution.conversation_continuation_tasks import create_tool_result_messages
        return await create_tool_result_messages(original_messages, tool_use_response, tool_results)
    
    async def continue_conversation_with_tool_results(
        self,
        original_request: MessagesRequest,
        tool_use_response: Any,
        tool_results: List[ToolExecutionResult],
        request_id: str
    ) -> Any:
        """Make follow-up API call with tool results"""
        return await self._continuation.continue_conversation_with_tool_results(
            original_request,
            tool_use_response,
            tool_results,
            request_id
        )


class ToolExecutionService(BaseService):
    """Handles client tool execution and tool_use/tool_result flow
    
    This is the main service class that maintains backward compatibility
    while using the new modular architecture internally.
    """
    
    def __init__(self):
        """Initialize tool execution service"""
        super().__init__("ToolExecution")
        
        # Create compatibility instances
        self.registry = ToolRegistry()
        self.detector = ToolUseDetector()
        
        # Initialize http_client for backward compatibility
        from ..services.http_client import HTTPClientService
        self.http_client = HTTPClientService()
        
        # Initialize continuation immediately for backward compatibility
        self.continuation = ConversationContinuation(self.http_client)
        
        # Configuration attributes for backward compatibility
        self.max_concurrent_tools = 5
        self.execution_timeout = 30
        
        # Initialize metrics tracking for compatibility
        self._metrics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'success_rate': 0.0,
            'tool_usage_count': {},
            'error_breakdown': {},
            'execution_times': {},  # Changed to dict to track by tool name
            'max_concurrent_executions': 0,
            'concurrent_executions': 0,
            'rate_limit_requests': {}
        }
        
        # Initialize rate limiting attributes
        self.rate_limit_max_requests = 100
        self.rate_limit_window = 60
        self.rate_limit_tracker = {}
        
        logger.info("ToolExecutionService initialized (new modular architecture)")
    
    async def _execute_tools(self, tool_use_blocks: List[Dict[str, Any]], request_id: str) -> List[ToolExecutionResult]:
        """Execute tools for backward compatibility"""
        results = []
        
        # Track concurrent execution for metrics
        self._metrics['concurrent_executions'] += len(tool_use_blocks)
        if self._metrics['concurrent_executions'] > self._metrics['max_concurrent_executions']:
            self._metrics['max_concurrent_executions'] = self._metrics['concurrent_executions']
        
        for tool_block in tool_use_blocks:
            try:
                result = await self.registry.execute_tool(
                    tool_block.get('id', ''),
                    tool_block.get('name', ''),
                    tool_block.get('input', {})
                )
                results.append(result)
                self._update_metrics(result)
            except Exception as e:
                error_result = ToolExecutionResult(
                    tool_call_id=tool_block.get('id', ''),
                    tool_name=tool_block.get('name', ''),
                    success=False,
                    result=f"Error executing tool: {str(e)}",
                    error=str(e),
                    execution_time=0.0
                )
                results.append(error_result)
                self._update_metrics(error_result)
        
        # Reset concurrent count after execution
        self._metrics['concurrent_executions'] = max(0, self._metrics['concurrent_executions'] - len(tool_use_blocks))
        
        return results
    
    def _update_metrics(self, result: ToolExecutionResult):
        """Update metrics for backward compatibility"""
        self._metrics['total_executions'] += 1
        if result.success:
            self._metrics['successful_executions'] += 1
        else:
            self._metrics['failed_executions'] += 1
            # Track error breakdown
            if result.error:
                # Extract error type (part before colon if present)
                error_key = result.error.split(':')[0].strip()
                self._metrics['error_breakdown'][error_key] = (
                    self._metrics['error_breakdown'].get(error_key, 0) + 1
                )
        
        # Update success rate
        total = self._metrics['total_executions']
        if total > 0:
            self._metrics['success_rate'] = (
                self._metrics['successful_executions'] / total
            )
        
        # Update tool usage count
        tool_name = result.tool_name
        self._metrics['tool_usage_count'][tool_name] = (
            self._metrics['tool_usage_count'].get(tool_name, 0) + 1
        )
        
        # Track execution times by tool name (keep last 100 per tool)
        if tool_name not in self._metrics['execution_times']:
            self._metrics['execution_times'][tool_name] = []
        
        times_list = self._metrics['execution_times'][tool_name]
        times_list.append(result.execution_time)
        
        # Keep only last 100 entries per tool
        if len(times_list) > 100:
            times_list[:] = times_list[-100:]
        
        # Track concurrent executions (simple increment/decrement)
        self._metrics['concurrent_executions'] = max(0, self._metrics['concurrent_executions'])
        if self._metrics['concurrent_executions'] > self._metrics['max_concurrent_executions']:
            self._metrics['max_concurrent_executions'] = self._metrics['concurrent_executions']
    
    def _check_rate_limit(self, request_id: str) -> bool:
        """Check rate limit for backward compatibility"""
        import time
        current_time = time.time()
        
        # Use configurable rate limits
        max_requests = getattr(self, 'rate_limit_max_requests', 100)
        window = getattr(self, 'rate_limit_window', 60)
        
        window_start = current_time - window
        
        # Initialize rate_limit_tracker if not exists
        if not hasattr(self, 'rate_limit_tracker'):
            self.rate_limit_tracker = {}
        
        # Clean old requests
        self.rate_limit_tracker = {
            rid: timestamp for rid, timestamp in self.rate_limit_tracker.items()
            if timestamp > window_start
        }
        
        # Check if under limit
        if len(self.rate_limit_tracker) < max_requests:
            self.rate_limit_tracker[request_id] = current_time
            return True
        return False
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Backward compatibility property for metrics"""
        return self._metrics
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current tool execution metrics"""
        return self._metrics.copy()
    
    async def handle_tool_use_response(
        self,
        response: Any,
        original_request: MessagesRequest,
        request_id: str
    ) -> Any:
        """
        Main orchestrator for tool execution flow.
        
        This method delegates to the new coordinator while maintaining
        the same interface for backward compatibility.
        """
        try:
            # Delegate to the new coordinator
            return await tool_execution_coordinator.handle_tool_use_response(
                response,
                original_request,
                request_id
            )
        except Exception as e:
            # Maintain compatibility with original error logging
            self.log_operation(
                "tool_execution_flow",
                False,
                request_id=request_id,
                error=str(e)
            )
            logger.error("Tool execution flow failed",
                        error=str(e),
                        request_id=request_id,
                        exc_info=True)
            raise