"""Flow for converting LiteLLM format to Anthropic format."""

from typing import Any, Dict, List, Union
import json

from ...services.base import ConversionService, InstructorService
from ...models.anthropic import Message, MessagesRequest, Tool
from ...models.litellm import LiteLLMMessage, LiteLLMRequest
from ...models.instructor import ConversionResult
from ...tasks.conversion.message_conversion_tasks import convert_litellm_message_to_anthropic
from ...tasks.conversion.tool_conversion_tasks import (
    convert_litellm_tool_to_anthropic,
    convert_litellm_tool_choice_to_anthropic
)
from ...core.logging_config import get_logger

logger = get_logger("conversion.litellm_to_anthropic")


class LiteLLMToAnthropicFlow(ConversionService[LiteLLMRequest, MessagesRequest], InstructorService):
    """Flow for converting LiteLLM format to Anthropic format."""
    
    def __init__(self):
        """Initialize LiteLLM to Anthropic flow."""
        ConversionService.__init__(self, "LiteLLMToAnthropic")
        InstructorService.__init__(self, "LiteLLMToAnthropic")
    
    def convert(self, source: LiteLLMRequest, **kwargs) -> ConversionResult:
        """Convert LiteLLM request to Anthropic format."""
        try:
            # Initialize conversion metadata
            conversion_metadata = self._initialize_metadata(source)
            
            # Convert messages and extract system message
            anthropic_messages, system_message = self._convert_messages(source, conversion_metadata)
            
            # Convert tools
            anthropic_tools = self._convert_tools(source)
            
            # Build Anthropic request
            anthropic_request_data = self._build_anthropic_request(
                source, anthropic_messages, system_message, anthropic_tools
            )
            
            # Log success
            self.log_operation(
                "litellm_to_anthropic_conversion",
                True,
                **conversion_metadata
            )
            
            return self.create_conversion_result(
                success=True,
                converted_data=anthropic_request_data,
                metadata=conversion_metadata
            )
            
        except Exception as e:
            logger.error("LiteLLM to Anthropic conversion failed",
                        error=str(e),
                        operation="litellm_to_anthropic_conversion",
                        exc_info=True)
            return self.create_conversion_result(
                success=False,
                errors=[f"Conversion failed: {str(e)}"],
                metadata={"error_type": type(e).__name__}
            )
    
    def _initialize_metadata(self, source: LiteLLMRequest) -> Dict[str, Any]:
        """Initialize conversion metadata."""
        return {
            "original_message_count": len(source.messages),
            "converted_message_count": 0,
            "tool_call_conversions": 0,
            "system_message_extracted": False
        }
    
    def _convert_messages(self, source: LiteLLMRequest, metadata: Dict[str, Any]) -> tuple[List[Message], str]:
        """Convert messages and extract system message."""
        anthropic_messages = []
        system_message = None
        
        for msg in source.messages:
            if msg.role == "system":
                # Extract system message
                system_message = msg.content
                metadata["system_message_extracted"] = True
                logger.info("Extracted system message",
                           message_preview=msg.content[:100] if msg.content else '' + ('...' if msg.content and len(msg.content) > 100 else ''))
            else:
                # Convert regular message using task module
                converted_msg = convert_litellm_message_to_anthropic(msg, metadata)
                anthropic_messages.append(converted_msg)
        
        metadata["converted_message_count"] = len(anthropic_messages)
        return anthropic_messages, system_message
    
    def _convert_tools(self, source: LiteLLMRequest) -> List[Tool]:
        """Convert tools to Anthropic format."""
        if not source.tools:
            return None
        
        anthropic_tools = []
        for tool in source.tools:
            converted_tool = convert_litellm_tool_to_anthropic(tool)
            anthropic_tools.append(converted_tool)
        
        return anthropic_tools
    
    def _build_anthropic_request(
        self,
        source: LiteLLMRequest,
        anthropic_messages: List[Message],
        system_message: str,
        anthropic_tools: List[Tool]
    ) -> Dict[str, Any]:
        """Build the final Anthropic request data."""
        # Build base request
        anthropic_request_data = {
            "model": source.model,
            "messages": [msg.model_dump() for msg in anthropic_messages],
            "max_tokens": source.max_tokens,
            "temperature": source.temperature,
            "stream": source.stream
        }
        
        # Add system message if present
        if system_message:
            anthropic_request_data["system"] = system_message
        
        # Add optional parameters
        self._add_optional_parameters(source, anthropic_request_data, anthropic_tools)
        
        return anthropic_request_data
    
    def _add_optional_parameters(
        self,
        source: LiteLLMRequest,
        request_data: Dict[str, Any],
        anthropic_tools: List[Tool]
    ) -> None:
        """Add optional parameters to the request."""
        if source.top_p is not None:
            request_data["top_p"] = source.top_p
        if source.top_k is not None:
            request_data["top_k"] = source.top_k
        if source.stop:
            request_data["stop_sequences"] = source.stop
        if anthropic_tools:
            request_data["tools"] = [tool.model_dump() for tool in anthropic_tools]
            # Only add tool_choice if we have tools to send
            if source.tool_choice:
                request_data["tool_choice"] = convert_litellm_tool_choice_to_anthropic(source.tool_choice)