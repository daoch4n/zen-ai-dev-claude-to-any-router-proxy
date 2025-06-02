"""Tool execution coordinator for orchestrating all tool execution flows."""

from typing import Any, List
from ..flows.tool_execution.tool_execution_flow import ToolExecutionFlow
from ..flows.tool_execution.conversation_continuation_flow import ConversationContinuationFlow
from ..flows.tool_execution.tool_registry_flow import ToolRegistryFlow
from ..tasks.tool_execution.tool_result_formatting_tasks import ToolExecutionResult
from ..models.anthropic import MessagesRequest
from ..services.http_client import HTTPClientService
from ..utils.config import config
from ..core.logging_config import get_logger

logger = get_logger("tool_execution.coordinator")


class ToolExecutionCoordinator:
    """Coordinates all tool execution operations using flow modules"""
    
    def __init__(self):
        """Initialize tool execution coordinator"""
        # Initialize HTTP client
        self.http_client = HTTPClientService()
        
        # Initialize flow modules
        self.execution_flow = ToolExecutionFlow(
            max_concurrent_tools=getattr(config, 'tool_max_concurrent_tools', 5),
            execution_timeout=getattr(config, 'tool_execution_timeout', 30),
            rate_limit_window=getattr(config, 'tool_rate_limit_window', 60),
            rate_limit_max_requests=getattr(config, 'tool_rate_limit_max_requests', 100)
        )
        
        self.continuation_flow = ConversationContinuationFlow(self.http_client)
        self.registry_flow = ToolRegistryFlow()
        
        logger.info("ToolExecutionCoordinator initialized")
    
    async def handle_tool_use_response(
        self,
        response: Any,
        original_request: MessagesRequest,
        request_id: str
    ) -> Any:
        """
        Main orchestrator for tool execution flow:
        1. Check if tools should be executed
        2. Execute tools if appropriate
        3. Continue conversation with results
        4. Return final response
        """
        try:
            logger.info("Starting tool execution coordination", request_id=request_id)
            
            # Step 1: Check if we should execute tools
            should_execute = await self.execution_flow.should_execute_tools(response)
            if not should_execute:
                logger.info("Tools should not be executed, returning original response")
                return response
            
            # Step 2: Execute tools
            tool_results = await self.execution_flow.execute_tools_from_response(response, request_id)
            
            # Step 3: Check for security errors that should return original response
            if self.execution_flow.check_security_errors(tool_results):
                logger.warning("Security errors detected, returning original response")
                return response
            
            # Step 4: Continue conversation with tool results
            final_response = await self.continuation_flow.continue_conversation_with_tool_results(
                original_request,
                response,
                tool_results,
                request_id
            )
            
            logger.info("Tool execution coordination completed successfully",
                       request_id=request_id,
                       tools_executed=len(tool_results),
                       successful_tools=sum(1 for r in tool_results if r.success))
            
            return final_response
            
        except Exception as e:
            logger.error("Tool execution coordination failed",
                        error=str(e),
                        request_id=request_id,
                        exc_info=True)
            raise
    
    def has_tool_use_blocks(self, response: Any) -> bool:
        """Check if response contains tool_use blocks"""
        return self.execution_flow.has_tool_use_blocks(response)
    
    async def execute_single_tool(self, tool_call_id: str, tool_name: str, tool_input: dict) -> ToolExecutionResult:
        """Execute a single tool via registry"""
        return await self.registry_flow.execute_tool(tool_call_id, tool_name, tool_input)
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return self.registry_flow.get_available_tools()
    
    def get_metrics(self) -> dict:
        """Get tool execution metrics"""
        return self.execution_flow.get_metrics()


# Global coordinator instance
tool_execution_coordinator = ToolExecutionCoordinator()