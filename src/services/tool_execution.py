"""Tool execution service for OpenRouter Anthropic Server.

Handles client tool execution and tool_use/tool_result conversation flow
according to Anthropic's tool use protocol.
"""

import asyncio
import json
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from copy import deepcopy

from .base import BaseService
from .http_client import HTTPClientService
from ..models.anthropic import Message, MessagesRequest, MessagesResponse
from ..core.logging_config import get_logger
from ..services.context_manager import ContextManager
from ..utils.config import config

# Initialize logging and context management
logger = get_logger("tool_execution")
context_manager = ContextManager()
from ..utils.error_logger import log_error


class ToolExecutionError(Exception):
    """Base exception for tool execution errors"""
    pass


class ToolTimeoutError(ToolExecutionError):
    """Tool execution timed out"""
    pass


class ToolValidationError(ToolExecutionError):
    """Tool input validation failed"""
    pass


class ToolPermissionError(ToolExecutionError):
    """Tool execution permission denied"""
    pass


@dataclass
class ToolExecutionResult:
    """Result of executing a single tool"""
    tool_call_id: str
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    requires_user_input: bool = False


class ToolResultFormatter:
    """Formats tool execution results into Anthropic tool_result format"""
    
    def create_tool_result_block(self, result: ToolExecutionResult) -> Dict[str, Any]:
        """Create tool_result block for API response"""
        # Special handling for user input requests
        if result.requires_user_input:
            # Don't create tool_result for user questions - return as text block instead
            return {
                "type": "text",
                "text": f"Tool '{result.tool_name}' requires user input:\n\n{result.result}"
            }
        
        content = self._format_result_content(result)
        
        # Limit content size to prevent API errors
        MAX_RESULT_LENGTH = 10000  # Reasonable limit for tool results
        if len(content) > MAX_RESULT_LENGTH:
            original_length = len(content)
            truncated_content = content[:MAX_RESULT_LENGTH]
            truncated_content += f"\n\n[Content truncated - {original_length} total characters, showing first {MAX_RESULT_LENGTH}]"
            content = truncated_content
            logger.warning("Tool result truncated",
                          original_length=original_length,
                          max_length=MAX_RESULT_LENGTH,
                          truncated_length=len(truncated_content))
        
        return {
            "type": "tool_result",
            "tool_use_id": result.tool_call_id,
            "content": content
        }
    
    def _format_result_content(self, result: ToolExecutionResult) -> str:
        """Format the result content for tool_result block"""
        if not result.success:
            return f"Error: {result.error}"
        
        if result.result is None:
            return "Tool executed successfully (no output)"
        
        if isinstance(result.result, str):
            return result.result
        elif isinstance(result.result, dict):
            return json.dumps(result.result, indent=2)
        elif isinstance(result.result, (list, tuple)):
            return "\n".join(str(item) for item in result.result)
        else:
            return str(result.result)


class ToolRegistry:
    """Maps Claude Code tool names to the new task-based execution functions"""
    
    def __init__(self):
        """Initialize tool registry with task-based coordinator"""
        # Import the new tool coordinator
        from ..coordinators.tool_coordinator import tool_coordinator
        self.coordinator = tool_coordinator
        
        # Available tools mapping (for compatibility)
        self.tools = {
            "Write": self._execute_write,
            "Read": self._execute_read,
            "Edit": self._execute_edit,
            "MultiEdit": self._execute_multi_edit,
            "Glob": self._execute_glob,
            "Grep": self._execute_grep,
            "LS": self._execute_ls,
            "Bash": self._execute_bash,
            "Task": self._execute_task,
            "WebSearch": self._execute_web_search,
            "WebFetch": self._execute_web_fetch,
            "NotebookRead": self._execute_notebook_read,
            "NotebookEdit": self._execute_notebook_edit,
            "TodoRead": self._execute_todo_read,
            "TodoWrite": self._execute_todo_write,
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
    
    # Individual tool execution methods for backward compatibility
    async def _execute_write(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute write tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_read(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute read tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_edit(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute edit tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_multi_edit(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute multi-edit tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_glob(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute glob tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_grep(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute grep tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_ls(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute ls tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_bash(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute bash tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_task(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute task tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_web_search(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute web search tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_web_fetch(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute web fetch tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_notebook_read(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute notebook read tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_notebook_edit(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute notebook edit tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_todo_read(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute todo read tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)
    
    async def _execute_todo_write(self, tool_call_id: str, tool_name: str, tool_input: Dict[str, Any]) -> ToolExecutionResult:
        """Execute todo write tool via coordinator"""
        return await self.coordinator.execute_tool(tool_name, tool_call_id, tool_input)


class ToolUseDetector:
    """Detects tool_use blocks in LiteLLM responses"""
    
    @staticmethod
    def has_tool_use_blocks(response: Any) -> bool:
        """Check if LiteLLM response contains tool_use blocks"""
        try:
            # Handle different response formats
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                
                # Check message content for tool_use blocks
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    content = choice.message.content
                    
                    # Content can be string or list of blocks
                    if isinstance(content, list):
                        return any(
                            isinstance(block, dict) and block.get('type') == 'tool_use'
                            for block in content
                        )
                    
                # Check for tool_calls (OpenAI format)
                if hasattr(choice, 'message') and hasattr(choice.message, 'tool_calls'):
                    return choice.message.tool_calls is not None and len(choice.message.tool_calls) > 0
                
                # Check stop reason
                if hasattr(choice, 'finish_reason') and choice.finish_reason == 'tool_calls':
                    return True
                
            return False
            
        except Exception as e:
            logger.error("Error detecting tool use",
                        error=str(e),
                        exc_info=True)
            return False
    
    @staticmethod
    def extract_tool_use_blocks(response: Any) -> List[Dict[str, Any]]:
        """Extract tool_use blocks from LiteLLM response"""
        tool_use_blocks = []
        
        try:
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    content = choice.message.content
                    
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'tool_use':
                                tool_use_blocks.append(block)
                
                # Handle OpenAI-style tool_calls
                if hasattr(choice, 'message') and hasattr(choice.message, 'tool_calls'):
                    if choice.message.tool_calls:
                        for tool_call in choice.message.tool_calls:
                            # Convert OpenAI format to Anthropic format
                            tool_use_block = {
                                "type": "tool_use",
                                "id": tool_call.id,
                                "name": tool_call.function.name,
                                "input": json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                            }
                            tool_use_blocks.append(tool_use_block)
            
            logger.debug("Extracted tool_use blocks", block_count=len(tool_use_blocks))
            return tool_use_blocks
            
        except Exception as e:
            logger.error("Error extracting tool use blocks",
                        error=str(e),
                        exc_info=True)
            return []


class ConversationContinuation:
    """Handles continuing conversation after tool execution"""
    
    def __init__(self, http_client: HTTPClientService):
        """Initialize conversation continuation with HTTP client"""
        self.http_client = http_client
    
    async def create_tool_result_messages(
        self,
        original_messages: List[Message],
        tool_use_response: Any,
        tool_results: List[ToolExecutionResult]
    ) -> List[Dict[str, Any]]:
        """
        Create the message sequence for continuing conversation:
        1. Current conversation messages (not original if cleaned)
        2. Assistant message with tool_use blocks
        3. User message with tool_result blocks
        """
        messages = []
        
        # Add current messages (which may have been cleaned)
        for msg in original_messages:
            messages.append(msg.model_dump())
        
        # Add assistant response with tool_use
        assistant_message = self._create_assistant_tool_use_message(tool_use_response)
        messages.append(assistant_message)
        
        # Add user response with tool_result
        user_message = self._create_user_tool_result_message(tool_results)
        messages.append(user_message)
        
        return messages
    
    def _create_assistant_tool_use_message(self, tool_use_response: Any) -> Dict[str, Any]:
        """Create assistant message from tool_use response"""
        try:
            content = []
            
            if hasattr(tool_use_response, 'choices') and tool_use_response.choices:
                choice = tool_use_response.choices[0]
                
                # Extract text content
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    msg_content = choice.message.content
                    
                    if isinstance(msg_content, str):
                        if msg_content.strip():
                            content.append({"type": "text", "text": msg_content})
                    elif isinstance(msg_content, list):
                        # If content is already a list of blocks, use as-is
                        for block in msg_content:
                            if isinstance(block, dict):
                                content.append(block)
                
                # Add tool_calls if present (from OpenAI format)
                if hasattr(choice, 'message') and hasattr(choice.message, 'tool_calls'):
                    if choice.message.tool_calls:
                        for tool_call in choice.message.tool_calls:
                            content.append({
                                "type": "tool_use",
                                "id": tool_call.id,
                                "name": tool_call.function.name,
                                "input": json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                            })
            
            return {
                "role": "assistant",
                "content": content
            }
            
        except Exception as e:
            logger.error("Error creating assistant message",
                        error=str(e),
                        exc_info=True)
            return {
                "role": "assistant", 
                "content": [{"type": "text", "text": "Tool execution initiated"}]
            }
    
    def _create_user_tool_result_message(self, tool_results: List[ToolExecutionResult]) -> Dict[str, Any]:
        """Create user message with tool_result blocks"""
        formatter = ToolResultFormatter()
        content = []
        
        # Only process completed tools, skip user input requests
        completed_results = [result for result in tool_results if not result.requires_user_input]
        
        for result in completed_results:
            tool_result_block = formatter.create_tool_result_block(result)
            content.append(tool_result_block)
        
        # Ensure we have at least one tool result
        if not content:
            logger.warning("No tool results to send in continuation")
            # Add a dummy error result to prevent empty content
            content.append({
                "type": "tool_result",
                "tool_use_id": "error",
                "content": "No tool results available"
            })
        
        return {
            "role": "user",
            "content": content
        }
    
    async def continue_conversation_with_tool_results(
        self,
        original_request: MessagesRequest,
        tool_use_response: Any,
        tool_results: List[ToolExecutionResult],
        request_id: str
    ) -> Any:
        """Make follow-up API call with tool results"""
        try:
            # Create continuation request
            continuation_messages = await self.create_tool_result_messages(
                original_request.messages,
                tool_use_response,
                tool_results
            )
            
            # Convert messages from Anthropic format to LiteLLM format
            from .conversion import AnthropicToLiteLLMConverter
            from ..models.anthropic import Message
            
            # Convert dict messages back to Message objects for conversion
            anthropic_messages = []
            for msg_dict in continuation_messages:
                anthropic_messages.append(Message(**msg_dict))
            
            # Create a temporary MessagesRequest for conversion
            temp_request = MessagesRequest(
                model=original_request.model,
                messages=anthropic_messages,
                max_tokens=original_request.max_tokens,
                temperature=original_request.temperature,
                stream=original_request.stream,
                tools=original_request.tools,
                tool_choice=original_request.tool_choice,
                system=original_request.system
            )
            
            # Convert to LiteLLM format
            converter = AnthropicToLiteLLMConverter()
            conversion_result = converter.convert(temp_request)
            
            if not conversion_result.success:
                raise Exception(f"Message conversion failed: {conversion_result.errors}")
            
            litellm_request = conversion_result.converted_data
            
            # Build continuation request data with converted messages
            continuation_request = {
                "model": litellm_request["model"],
                "messages": litellm_request["messages"],
                "max_tokens": litellm_request.get("max_tokens", original_request.max_tokens),
                "temperature": litellm_request.get("temperature", original_request.temperature or 1.0),
                "stream": litellm_request.get("stream", original_request.stream or False),
                "api_key": config.openrouter_api_key,
                "api_base": "https://openrouter.ai/api/v1",
                "extra_headers": {
                    "HTTP-Referer": "https://github.com/openrouter-anthropic-server",
                    "X-Title": "OpenRouter Anthropic Server - Tool Results"
                }
            }
            
            # Add tools if present
            if litellm_request.get("tools"):
                continuation_request["tools"] = litellm_request["tools"]
            
            # DEBUG: Log the messages being sent
            logger.info(f"🔍 DEBUG: Continuation request message count: {len(litellm_request['messages'])}")
            for i, msg in enumerate(litellm_request['messages']):
                role = msg.get('role', 'unknown')
                content_type = type(msg.get('content', '')).__name__
                if isinstance(msg.get('content'), list):
                    content_info = f"list[{len(msg['content'])}]"
                    block_types = []
                    for block in msg['content']:
                        if isinstance(block, dict):
                            block_types.append(block.get('type', 'unknown'))
                    content_info += f" types: {block_types}"
                else:
                    content_info = content_type
                logger.info(f"  Message {i+1}: role={role}, content={content_info}")
            
            # Make API call
            logger.info(f"🔄 Making continuation API call with {len(tool_results)} tool results")
            continuation_response = await self.http_client.make_litellm_request(
                continuation_request,
                f"{request_id}_continuation"
            )
            
            return continuation_response
            
        except Exception as e:
            logger.error("Continuation API call failed",
                        error=str(e),
                        exc_info=True)
            
            # Log comprehensive error details
            error_context = {
                "service": "ConversationContinuation",
                "method": "continue_conversation_with_tool_results",
                "original_request_id": request_id,
                "tool_count": len(tool_results),
                "tool_names": [r.tool_name for r in tool_results],
                "tool_success": [r.success for r in tool_results],
                "message_count": len(continuation_messages) if 'continuation_messages' in locals() else 0
            }
            
            # Include tool results details
            tool_details = []
            for result in tool_results:
                tool_details.append({
                    "tool_name": result.tool_name,
                    "tool_call_id": result.tool_call_id,
                    "success": result.success,
                    "error": result.error,
                    "result_preview": str(result.result)[:200] if result.result else None
                })
            error_context["tool_details"] = tool_details
            
            # Include continuation request if available
            request_data = None
            if 'continuation_request' in locals():
                request_data = continuation_request
            
            log_error(
                error=e,
                correlation_id=f"{request_id}_continuation",
                request_data=request_data,
                response_data=None,
                context=error_context
            )
            
            raise


class ToolExecutionService(BaseService):
    """Handles client tool execution and tool_use/tool_result flow"""
    
    def __init__(self):
        """Initialize tool execution service"""
        super().__init__("ToolExecution")
        
        self.registry = ToolRegistry()
        self.detector = ToolUseDetector()
        self.http_client = HTTPClientService()
        self.continuation = ConversationContinuation(self.http_client)
        
        # Execution settings
        self.max_concurrent_tools = getattr(config, 'tool_max_concurrent_tools', 5)
        self.execution_timeout = getattr(config, 'tool_execution_timeout', 30)
        self.debug_enabled = getattr(config, 'tool_debug_enabled', False)
        
        # Metrics tracking
        self.metrics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'execution_times': {},
            'tool_usage_count': {},
            'error_count_by_type': {},
            'concurrent_executions': 0,
            'max_concurrent_executions': 0
        }
        
        # Rate limiting
        self.rate_limit_window = getattr(config, 'tool_rate_limit_window', 60)  # seconds
        self.rate_limit_max_requests = getattr(config, 'tool_rate_limit_max_requests', 100)
        self.rate_limit_tracker = {}
        
        logger.info("ToolExecutionService initialized")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current tool execution metrics"""
        avg_execution_times = {}
        for tool_name, times in self.metrics['execution_times'].items():
            if times:
                avg_execution_times[tool_name] = sum(times) / len(times)
        
        return {
            'total_executions': self.metrics['total_executions'],
            'successful_executions': self.metrics['successful_executions'],
            'failed_executions': self.metrics['failed_executions'],
            'success_rate': self.metrics['successful_executions'] / max(1, self.metrics['total_executions']),
            'average_execution_times': avg_execution_times,
            'tool_usage_count': self.metrics['tool_usage_count'],
            'error_breakdown': self.metrics['error_count_by_type'],
            'max_concurrent_executions': self.metrics['max_concurrent_executions']
        }
    
    def _update_metrics(self, result: ToolExecutionResult):
        """Update metrics based on tool execution result"""
        self.metrics['total_executions'] += 1
        
        if result.success:
            self.metrics['successful_executions'] += 1
        else:
            self.metrics['failed_executions'] += 1
            error_type = result.error.split(':')[0] if result.error else 'unknown'
            self.metrics['error_count_by_type'][error_type] = self.metrics['error_count_by_type'].get(error_type, 0) + 1
        
        # Track execution times
        if result.tool_name not in self.metrics['execution_times']:
            self.metrics['execution_times'][result.tool_name] = []
        self.metrics['execution_times'][result.tool_name].append(result.execution_time)
        
        # Keep only last 100 execution times per tool
        if len(self.metrics['execution_times'][result.tool_name]) > 100:
            self.metrics['execution_times'][result.tool_name] = self.metrics['execution_times'][result.tool_name][-100:]
        
        # Track tool usage
        self.metrics['tool_usage_count'][result.tool_name] = self.metrics['tool_usage_count'].get(result.tool_name, 0) + 1
    
    def _check_rate_limit(self, request_id: str) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        # Clean old entries
        cutoff_time = current_time - self.rate_limit_window
        self.rate_limit_tracker = {
            req_id: timestamp 
            for req_id, timestamp in self.rate_limit_tracker.items() 
            if timestamp > cutoff_time
        }
        
        # Check if over limit
        if len(self.rate_limit_tracker) >= self.rate_limit_max_requests:
            logger.warning("Rate limit exceeded",
                          request_id=request_id,
                          current_requests=len(self.rate_limit_tracker),
                          max_requests=self.rate_limit_max_requests)
            return False
        
        # Track this request
        self.rate_limit_tracker[request_id] = current_time
        return True
    
    async def _check_tools_need_confirmation(self, tool_use_blocks: List[Dict[str, Any]]) -> bool:
        """Check if any tools would require user confirmation before executing them"""
        for tool_block in tool_use_blocks:
            tool_name = tool_block.get('name', '')
            tool_input = tool_block.get('input', {})
            
            if tool_name == 'Bash':
                command = tool_input.get('command', '')
                user_confirmed = tool_input.get('user_confirmed', False)
                
                # Import the method from system_tools to check deletion confirmation
                from ..tasks.tools.system_tools import check_deletion_confirmation_task
                requires_confirmation = await check_deletion_confirmation_task(command)
                if requires_confirmation and not user_confirmed:
                    return True
            
            # Add checks for other tools that might require confirmation here
            
        return False
    
    async def handle_tool_use_response(
        self,
        response: Any,
        original_request: MessagesRequest,
        request_id: str
    ) -> Any:
        """
        Main orchestrator for tool execution flow:
        1. Extract tool_use blocks from response
        2. Execute each tool locally
        3. Create tool_result messages
        4. Continue conversation with Anthropic
        5. Return final response
        """
        try:
            logger.info("Starting tool execution flow", request_id=request_id)
            
            # Check rate limit
            if not self._check_rate_limit(request_id):
                raise ToolExecutionError("Rate limit exceeded for tool execution")
            
            # Step 1: Extract tool_use blocks
            tool_use_blocks = self.detector.extract_tool_use_blocks(response)
            if not tool_use_blocks:
                logger.warning("No tool_use blocks found in response")
                return response

            logger.info("Found tools to execute", tool_count=len(tool_use_blocks))
            
            # Step 1.5: Check if any tools would require user confirmation BEFORE executing
            requires_user_confirmation = await self._check_tools_need_confirmation(tool_use_blocks)
            if requires_user_confirmation:
                logger.info("Tools require user confirmation, letting Claude CLI handle interaction")
                return response
            
            # Step 2: Execute tools
            tool_results = await self._execute_tools(tool_use_blocks, request_id)
            
            # Step 2.5: Check if any tool failed with security/permission errors
            # In such cases, return original response to let Claude CLI handle it
            security_errors = [
                r for r in tool_results 
                if not r.success and r.error and (
                    "not allowed for security reasons" in r.error or
                    "permission denied" in r.error.lower() or
                    "access denied" in r.error.lower()
                )
            ]
            
            if security_errors:
                logger.warning("Tool execution blocked by security policy, returning original response",
                              security_error_count=len(security_errors))
                # Return the original response so Claude CLI can handle the tool execution
                # and show appropriate error messages to the user
                return response
            
            # Step 3: Continue conversation with tool results
            final_response = await self.continuation.continue_conversation_with_tool_results(
                original_request,
                response,
                tool_results,
                request_id
            )
            
            self.log_operation(
                "tool_execution_flow",
                True,
                request_id=request_id,
                tools_executed=len(tool_results),
                successful_tools=sum(1 for r in tool_results if r.success)
            )
            
            logger.info("Tool execution flow completed", request_id=request_id)
            return final_response
            
        except Exception as e:
            error_msg = f"Tool execution flow failed: {e}"
            self.log_operation(
                "tool_execution_flow",
                False,
                request_id=request_id,
                error=error_msg
            )
            logger.error("Tool execution flow failed",
                        error_msg=error_msg,
                        request_id=request_id,
                        exc_info=True)
            raise
    
    async def _execute_tools(self, tool_use_blocks: List[Dict[str, Any]], request_id: str) -> List[ToolExecutionResult]:
        """Execute all tools from tool_use blocks"""
        results = []
        
        # Limit concurrent executions
        semaphore = asyncio.Semaphore(self.max_concurrent_tools)
        
        # Track concurrent executions
        self.metrics['concurrent_executions'] = 0
        
        async def execute_single_tool(tool_block: Dict[str, Any]) -> ToolExecutionResult:
            async with semaphore:
                # Update concurrent execution metrics
                self.metrics['concurrent_executions'] += 1
                self.metrics['max_concurrent_executions'] = max(
                    self.metrics['max_concurrent_executions'],
                    self.metrics['concurrent_executions']
                )
                
                try:
                    result = await self._execute_single_tool(tool_block, request_id)
                    return result
                finally:
                    self.metrics['concurrent_executions'] -= 1
        
        # Execute tools concurrently
        tasks = [execute_single_tool(block) for block in tool_use_blocks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                tool_block = tool_use_blocks[i]
                error_result = ToolExecutionResult(
                    tool_call_id=tool_block.get('id', f'error_{i}'),
                    tool_name=tool_block.get('name', 'unknown'),
                    success=False,
                    result=None,
                    error=f"Execution exception: {result}"
                )
                self._update_metrics(error_result)
                processed_results.append(error_result)
            else:
                self._update_metrics(result)
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_single_tool(self, tool_block: Dict[str, Any], request_id: str) -> ToolExecutionResult:
        """Execute a single tool from tool_use block"""
        tool_call_id = tool_block.get('id', '')
        tool_name = tool_block.get('name', '')
        tool_input = tool_block.get('input', {})
        
        logger.info("Executing tool",
                   tool_name=tool_name,
                   tool_call_id=tool_call_id)
        
        try:
            # Add timeout wrapper
            result = await asyncio.wait_for(
                self.registry.execute_tool(tool_call_id, tool_name, tool_input),
                timeout=self.execution_timeout
            )
            
            if result.success:
                logger.info("Tool completed successfully",
                           tool_name=tool_name,
                           execution_time=f"{result.execution_time:.2f}s")
            else:
                logger.warning("Tool execution failed",
                              tool_name=tool_name,
                              error=result.error)
            
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Tool execution timed out after {self.execution_timeout}s"
            logger.error("Tool execution timed out",
                        tool_name=tool_name,
                        timeout=self.execution_timeout,
                        error_msg=error_msg)
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Tool execution error: {e}"
            logger.error("Tool execution error",
                        tool_name=tool_name,
                        error=str(e),
                        error_msg=error_msg,
                        exc_info=True)
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=error_msg
            ) 