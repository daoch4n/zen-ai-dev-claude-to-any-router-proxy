"""Execution Coordinator for OpenRouter Anthropic Server.

High-level coordinator that orchestrates the complete tool execution workflow.
Replaces tool_execution.py with modular task-based architecture.

Part of Phase 6B comprehensive refactoring - Service Coordinators.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from ..core.logging_config import get_logger
from ..services.context_manager import ContextManager
from ..tasks.tool_execution.tool_result_formatting_tasks import ToolExecutionResult
from ..models.anthropic import Message, MessagesRequest, MessagesResponse
from .tool_coordinator import tool_coordinator

# Initialize logging and context management
logger = get_logger("execution_coordinator")
context_manager = ContextManager()


class ExecutionCoordinator:
    """
    Coordinates the complete tool execution workflow.
    
    Handles the full cycle from detecting tool use in responses,
    executing tools via the tool coordinator, formatting results,
    and continuing conversations.
    """
    
    def __init__(self):
        """Initialize the execution coordinator."""
        self.tool_coordinator = tool_coordinator
        # Lazy-load these to avoid circular imports
        self.result_formatter = None
        self.tool_detector = None
        
        # Execution configuration
        self.config = {
            "max_concurrent_tools": 5,
            "execution_timeout": 30,
            "max_execution_rounds": 3,
            "enable_tool_validation": True
        }
        
        logger.info("Execution coordinator initialized with task-based architecture")
    
    @property
    def _tool_detector(self):
        """Lazy-load tool detector to avoid circular imports"""
        if self.tool_detector is None:
            from ..services.tool_execution import ToolUseDetector
            self.tool_detector = ToolUseDetector()
        return self.tool_detector
    
    @property
    def _result_formatter(self):
        """Lazy-load result formatter to avoid circular imports"""
        if self.result_formatter is None:
            from ..services.tool_execution import ToolResultFormatter
            self.result_formatter = ToolResultFormatter()
        return self.result_formatter
    
    async def process_response_with_tools(
        self,
        litellm_response: Any,
        original_request: MessagesRequest,
        http_client: Any
    ) -> MessagesResponse:
        """
        Process a LiteLLM response that may contain tool use blocks.
        
        This is the main entry point for tool execution workflow.
        
        Args:
            litellm_response: Response from LiteLLM that may contain tool calls
            original_request: Original Anthropic request for context
            http_client: HTTP client for making API calls
        
        Returns:
            Final MessagesResponse after tool execution and conversation continuation
        """
        logger.info("Processing response with potential tool use",
                   has_tool_use=self._tool_detector.has_tool_use_blocks(litellm_response))
        
        try:
            # Check if response contains tool use
            if not self._tool_detector.has_tool_use_blocks(litellm_response):
                logger.debug("No tool use detected, converting response directly")
                # Convert response directly without tool execution
                from ..services.conversion import LiteLLMResponseToAnthropicConverter
                converter = LiteLLMResponseToAnthropicConverter()
                conversion_result = converter.convert(litellm_response, original_request)
                
                if conversion_result.success:
                    return MessagesResponse(**conversion_result.converted_data)
                else:
                    raise Exception(f"Response conversion failed: {conversion_result.errors}")
            
            # Execute tool use workflow
            return await self._execute_tool_workflow(
                litellm_response=litellm_response,
                original_request=original_request,
                http_client=http_client
            )
            
        except Exception as e:
            error_msg = f"Tool execution workflow failed: {str(e)}"
            logger.error("Tool execution workflow failed",
                        error=error_msg,
                        exc_info=True)
            
            # Return error response
            return self._create_error_response(error_msg, original_request)
    
    async def _execute_tool_workflow(
        self,
        litellm_response: Any,
        original_request: MessagesRequest,
        http_client: Any
    ) -> MessagesResponse:
        """Execute the complete tool workflow with conversation continuation."""
        logger.debug("Starting tool execution workflow")
        
        # Step 1: Extract tool use blocks
        tool_use_blocks = self.tool_detector.extract_tool_use_blocks(litellm_response)
        
        if not tool_use_blocks:
            logger.warning("Tool use detected but no blocks extracted")
            # Fallback to direct conversion
            from ..services.conversion import LiteLLMResponseToAnthropicConverter
            converter = LiteLLMResponseToAnthropicConverter()
            conversion_result = converter.convert(litellm_response, original_request)
            
            if conversion_result.success:
                return MessagesResponse(**conversion_result.converted_data)
            else:
                raise Exception(f"Fallback conversion failed: {conversion_result.errors}")
        
        logger.info("Executing tools",
                   tool_count=len(tool_use_blocks))
        
        # Step 2: Execute tools
        tool_results = await self._execute_tools(tool_use_blocks)
        
        # Step 3: Format tool results for conversation
        tool_result_blocks = self._format_tool_results(tool_results)
        
        # Step 4: Continue conversation with tool results
        final_response = await self._continue_conversation_with_results(
            tool_use_blocks=tool_use_blocks,
            tool_result_blocks=tool_result_blocks,
            original_request=original_request,
            http_client=http_client
        )
        
        return final_response
    
    async def _execute_tools(
        self,
        tool_use_blocks: List[Dict[str, Any]]
    ) -> List[ToolExecutionResult]:
        """Execute all tools using the tool coordinator."""
        logger.debug("Executing tools via coordinator",
                    tool_count=len(tool_use_blocks))
        
        # Convert tool use blocks to tool requests
        tool_requests = []
        for block in tool_use_blocks:
            tool_request = {
                'tool_call_id': block.get('id', ''),
                'name': block.get('name', ''),
                'input': block.get('input', {})
            }
            tool_requests.append(tool_request)
        
        # Execute tools via coordinator (handles optimal concurrency)
        tool_results = await self.tool_coordinator.execute_tools_batch(tool_requests)
        
        logger.info("Tool execution completed",
                   total_tools=len(tool_use_blocks),
                   successful_tools=sum(1 for r in tool_results if r.success))
        
        return tool_results
    
    def _format_tool_results(
        self,
        tool_results: List[ToolExecutionResult]
    ) -> List[Dict[str, Any]]:
        """Format tool execution results into tool_result blocks."""
        logger.debug("Formatting tool results",
                    result_count=len(tool_results))
        
        formatted_results = []
        for result in tool_results:
            formatted_block = self.result_formatter.create_tool_result_block(result)
            formatted_results.append(formatted_block)
        
        return formatted_results
    
    async def _continue_conversation_with_results(
        self,
        tool_use_blocks: List[Dict[str, Any]],
        tool_result_blocks: List[Dict[str, Any]],
        original_request: MessagesRequest,
        http_client: Any
    ) -> MessagesResponse:
        """Continue the conversation with tool results."""
        logger.debug("Continuing conversation with tool results",
                    tool_use_count=len(tool_use_blocks),
                    tool_result_count=len(tool_result_blocks))
        
        try:
            # Build continuation request
            continuation_request = self._build_continuation_request(
                tool_use_blocks=tool_use_blocks,
                tool_result_blocks=tool_result_blocks,
                original_request=original_request
            )
            
            # Make continuation API call
            from ..services.conversion import AnthropicToLiteLLMConverter, LiteLLMResponseToAnthropicConverter
            
            # Convert to LiteLLM format
            converter = AnthropicToLiteLLMConverter()
            conversion_result = converter.convert(continuation_request)
            
            if not conversion_result.success:
                raise Exception(f"Continuation request conversion failed: {conversion_result.errors}")
            
            litellm_request = conversion_result.converted_data
            
            # Make API call
            logger.debug("Making continuation API call")
            continuation_response = await http_client.make_litellm_request(
                litellm_request,
                stream=False  # Tool execution always non-streaming
            )
            
            # Convert response back to Anthropic format
            response_converter = LiteLLMResponseToAnthropicConverter()
            final_conversion = response_converter.convert(continuation_response, continuation_request)
            
            if not final_conversion.success:
                raise Exception(f"Final response conversion failed: {final_conversion.errors}")
            
            final_response = MessagesResponse(**final_conversion.converted_data)
            
            logger.info("Conversation continuation completed successfully")
            return final_response
            
        except Exception as e:
            error_msg = f"Conversation continuation failed: {str(e)}"
            logger.error("Conversation continuation failed",
                        error=error_msg,
                        exc_info=True)
            
            # Return a response with tool results but no further AI response
            return self._create_tool_results_response(
                tool_use_blocks=tool_use_blocks,
                tool_result_blocks=tool_result_blocks,
                original_request=original_request,
                error_message=error_msg
            )
    
    def _build_continuation_request(
        self,
        tool_use_blocks: List[Dict[str, Any]],
        tool_result_blocks: List[Dict[str, Any]],
        original_request: MessagesRequest
    ) -> MessagesRequest:
        """Build the continuation request with tool results."""
        logger.debug("Building continuation request")
        
        # Start with original messages
        continuation_messages = []
        for msg in original_request.messages:
            continuation_messages.append(msg)
        
        # Add assistant message with tool use
        assistant_content = []
        
        # Add any text content from the original response (if available)
        # For now, we'll just add the tool use blocks
        assistant_content.extend(tool_use_blocks)
        
        assistant_message = Message(
            role="assistant",
            content=assistant_content
        )
        continuation_messages.append(assistant_message)
        
        # Add user message with tool results
        user_message = Message(
            role="user",
            content=tool_result_blocks
        )
        continuation_messages.append(user_message)
        
        # Build continuation request
        continuation_request = MessagesRequest(
            model=original_request.model,
            messages=continuation_messages,
            max_tokens=original_request.max_tokens,
            temperature=original_request.temperature,
            system=original_request.system,
            tools=original_request.tools,
            tool_choice=original_request.tool_choice,
            stream=False  # Tool execution is always non-streaming
        )
        
        return continuation_request
    
    def _create_tool_results_response(
        self,
        tool_use_blocks: List[Dict[str, Any]],
        tool_result_blocks: List[Dict[str, Any]],
        original_request: MessagesRequest,
        error_message: Optional[str] = None
    ) -> MessagesResponse:
        """Create a response containing tool results."""
        logger.debug("Creating tool results response")
        
        # Build content with tool use and results
        content = []
        
        # Add tool use blocks
        content.extend(tool_use_blocks)
        
        # Add tool result blocks
        content.extend(tool_result_blocks)
        
        # Add error message if present
        if error_message:
            content.append({
                "type": "text",
                "text": f"Note: Conversation continuation failed: {error_message}"
            })
        
        response = MessagesResponse(
            id=f"msg_{int(asyncio.get_event_loop().time() * 1000)}",
            type="message",
            role="assistant",
            content=content,
            model=original_request.model,
            stop_reason="tool_use",
            stop_sequence=None,
            usage={"input_tokens": 0, "output_tokens": 0}  # Approximate
        )
        
        return response
    
    def _create_error_response(
        self,
        error_message: str,
        original_request: MessagesRequest
    ) -> MessagesResponse:
        """Create an error response."""
        logger.debug("Creating error response", error=error_message)
        
        content = [{
            "type": "text",
            "text": f"Tool execution error: {error_message}"
        }]
        
        response = MessagesResponse(
            id=f"msg_error_{int(asyncio.get_event_loop().time() * 1000)}",
            type="message",
            role="assistant",
            content=content,
            model=original_request.model,
            stop_reason="error",
            stop_sequence=None,
            usage={"input_tokens": 0, "output_tokens": 0}
        )
        
        return response
    
    async def validate_tool_execution_capability(self) -> Dict[str, Any]:
        """Validate that tool execution is working properly."""
        logger.info("Validating tool execution capability")
        
        validation_result = {
            "overall_status": "unknown",
            "tool_coordinator_status": "unknown",
            "tool_availability": {},
            "execution_test_results": [],
            "recommendations": []
        }
        
        try:
            # Test tool coordinator
            coordinator_stats = self.tool_coordinator.get_execution_statistics()
            validation_result["tool_coordinator_status"] = "healthy"
            
            # Test tool availability
            availability = await self.tool_coordinator.validate_tool_availability()
            validation_result["tool_availability"] = availability
            
            # Test execution with simple tools
            test_results = await self._run_execution_tests()
            validation_result["execution_test_results"] = test_results
            
            # Determine overall status
            available_tools = sum(1 for available in availability.values() if available)
            total_tools = len(availability)
            
            if available_tools >= total_tools * 0.8:
                validation_result["overall_status"] = "healthy"
            elif available_tools >= total_tools * 0.6:
                validation_result["overall_status"] = "degraded"
                validation_result["recommendations"].append(
                    "Some tools are unavailable. Check tool configurations."
                )
            else:
                validation_result["overall_status"] = "unhealthy"
                validation_result["recommendations"].append(
                    "Many tools are unavailable. Check system dependencies."
                )
            
            logger.info("Tool execution validation completed",
                       overall_status=validation_result["overall_status"],
                       available_tools=f"{available_tools}/{total_tools}")
            
        except Exception as e:
            validation_result["overall_status"] = "error"
            validation_result["error"] = str(e)
            logger.error("Tool execution validation failed",
                        error=str(e),
                        exc_info=True)
        
        return validation_result
    
    async def _run_execution_tests(self) -> List[Dict[str, Any]]:
        """Run basic execution tests."""
        test_cases = [
            {
                "name": "file_read_test",
                "tool_use_block": {
                    "type": "tool_use",
                    "id": "test_read_1",
                    "name": "Read",
                    "input": {"path": "/etc/hostname"}
                }
            },
            {
                "name": "bash_test",
                "tool_use_block": {
                    "type": "tool_use",
                    "id": "test_bash_1", 
                    "name": "Bash",
                    "input": {"command": "echo 'test'"}
                }
            }
        ]
        
        test_results = []
        
        for test_case in test_cases:
            try:
                tool_results = await self._execute_tools([test_case["tool_use_block"]])
                
                result = {
                    "test_name": test_case["name"],
                    "success": len(tool_results) > 0 and tool_results[0].success,
                    "execution_time": tool_results[0].execution_time if tool_results else 0,
                    "error": tool_results[0].error if tool_results and not tool_results[0].success else None
                }
                
                test_results.append(result)
                
            except Exception as e:
                test_results.append({
                    "test_name": test_case["name"],
                    "success": False,
                    "execution_time": 0,
                    "error": str(e)
                })
        
        return test_results
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """Get comprehensive execution metrics."""
        coordinator_stats = self.tool_coordinator.get_execution_statistics()
        coordinator_health = self.tool_coordinator.get_tool_health_status()
        
        return {
            "coordinator_statistics": coordinator_stats,
            "health_status": coordinator_health,
            "configuration": self.config,
            "capabilities": {
                "max_concurrent_tools": self.config["max_concurrent_tools"],
                "execution_timeout": self.config["execution_timeout"],
                "max_execution_rounds": self.config["max_execution_rounds"]
            }
        }


# Global execution coordinator instance
execution_coordinator = ExecutionCoordinator()