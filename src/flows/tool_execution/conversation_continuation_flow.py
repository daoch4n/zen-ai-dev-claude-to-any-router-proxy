"""Conversation continuation flow for tool results."""

from typing import Any, List
from ...tasks.tool_execution.conversation_continuation_tasks import (
    create_tool_result_messages
)
from ...tasks.tool_execution.tool_result_formatting_tasks import ToolExecutionResult
from ...models.anthropic import Message, MessagesRequest
from ...services.http_client import HTTPClientService
from ...utils.config import config, OPENROUTER_API_BASE
from ...utils.error_logger import log_error
from ...core.logging_config import get_logger

logger = get_logger("tool_execution.continuation")


class ConversationContinuationFlow:
    """Handles continuing conversation after tool execution"""
    
    def __init__(self, http_client: HTTPClientService):
        """Initialize conversation continuation with HTTP client"""
        self.http_client = http_client
    
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
            continuation_messages = await create_tool_result_messages(
                original_request.messages,
                tool_use_response,
                tool_results
            )
            
            # Convert to LiteLLM format and make API call
            return await self._make_continuation_request(
                original_request,
                continuation_messages,
                tool_results,
                request_id
            )
            
        except Exception as e:
            logger.error("Continuation API call failed",
                        error=str(e),
                        exc_info=True)
            
            # Log comprehensive error details
            await self._log_continuation_error(e, original_request, tool_results, request_id)
            raise
    
    async def _make_continuation_request(
        self,
        original_request: MessagesRequest,
        continuation_messages: List[dict],
        tool_results: List[ToolExecutionResult],
        request_id: str
    ) -> Any:
        """Make the actual continuation API request"""
        # Convert messages from Anthropic format to LiteLLM format
        from ...services.conversion import AnthropicToLiteLLMConverter
        
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
            "api_base": OPENROUTER_API_BASE,
            "extra_headers": {
                "HTTP-Referer": "https://github.com/openrouter-anthropic-server",
                "X-Title": "OpenRouter Anthropic Server - Tool Results"
            }
        }
        
        # Add tools if present
        if litellm_request.get("tools"):
            continuation_request["tools"] = litellm_request["tools"]
        
        # Log request details for debugging
        self._log_continuation_request(litellm_request, tool_results)
        
        # Make API call
        logger.info(f"🔄 Making continuation API call with {len(tool_results)} tool results")
        continuation_response = await self.http_client.make_litellm_request(
            continuation_request,
            f"{request_id}_continuation"
        )
        
        return continuation_response
    
    def _log_continuation_request(self, litellm_request: dict, tool_results: List[ToolExecutionResult]):
        """Log continuation request details for debugging"""
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
    
    async def _log_continuation_error(
        self,
        error: Exception,
        original_request: MessagesRequest,
        tool_results: List[ToolExecutionResult],
        request_id: str
    ):
        """Log comprehensive error details for continuation failures"""
        error_context = {
            "service": "ConversationContinuationFlow",
            "method": "continue_conversation_with_tool_results",
            "original_request_id": request_id,
            "tool_count": len(tool_results),
            "tool_names": [r.tool_name for r in tool_results],
            "tool_success": [r.success for r in tool_results],
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
        
        log_error(
            error=error,
            correlation_id=f"{request_id}_continuation",
            request_data=None,
            response_data=None,
            context=error_context
        )