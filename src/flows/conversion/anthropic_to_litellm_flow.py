"""Flow for converting Anthropic format to LiteLLM format."""

from typing import Any, Dict, List

from ...services.base import ConversionService, InstructorService
from ...models.anthropic import MessagesRequest
from ...models.litellm import LiteLLMMessage, LiteLLMRequest
from ...models.instructor import ConversionResult
from ...tasks.conversion.model_mapping_tasks import (
    ensure_openrouter_prefix,
    map_model_name,
    update_request_with_model_mapping
)
from ...tasks.conversion.message_conversion_tasks import (
    extract_system_message_content,
    convert_anthropic_message_to_litellm,
    handle_tool_result_blocks,
    create_system_message
)
from ...tasks.conversion.tool_conversion_tasks import (
    convert_anthropic_tool_to_litellm,
    convert_anthropic_tool_choice_to_litellm
)
from ...utils.config import config
from ...core.logging_config import get_logger

logger = get_logger("conversion.anthropic_to_litellm")


class AnthropicToLiteLLMFlow(ConversionService[MessagesRequest, LiteLLMRequest], InstructorService):
    """Flow for converting Anthropic format to LiteLLM format."""
    
    def __init__(self):
        """Initialize Anthropic to LiteLLM flow."""
        ConversionService.__init__(self, "AnthropicToLiteLLM")
        InstructorService.__init__(self, "AnthropicToLiteLLM")
    
    def convert(self, source: MessagesRequest, **kwargs) -> ConversionResult:
        """Convert Anthropic MessagesRequest to LiteLLM format."""
        try:
            # Initialize conversion metadata
            conversion_metadata = self._initialize_metadata(source)
            
            # Convert messages
            litellm_messages = self._convert_messages(source, conversion_metadata)
            
            # Convert tools
            litellm_tools = self._convert_tools(source, conversion_metadata)
            
            # Build LiteLLM request
            litellm_request_data = self._build_litellm_request(
                source, litellm_messages, litellm_tools, conversion_metadata
            )
            
            # Log success
            self.log_operation(
                "anthropic_to_litellm_conversion",
                True,
                **conversion_metadata
            )
            
            return self.create_conversion_result(
                success=True,
                converted_data=litellm_request_data,
                metadata=conversion_metadata
            )
            
        except Exception as e:
            logger.error("Anthropic to LiteLLM conversion failed",
                        error=str(e),
                        operation="anthropic_to_litellm_conversion",
                        exc_info=True)
            return self.create_conversion_result(
                success=False,
                errors=[f"Conversion failed: {str(e)}"],
                metadata={"error_type": type(e).__name__}
            )
    
    def _initialize_metadata(self, source: MessagesRequest) -> Dict[str, Any]:
        """Initialize conversion metadata."""
        return {
            "original_message_count": len(source.messages),
            "converted_message_count": 0,
            "tool_conversions": 0,
            "content_block_conversions": 0,
            "system_message_added": False
        }
    
    def _convert_messages(self, source: MessagesRequest, metadata: Dict[str, Any]) -> List[LiteLLMMessage]:
        """Convert all messages including system message."""
        litellm_messages = []
        
        # Handle system message first
        if source.system:
            system_content = extract_system_message_content(source.system)
            if system_content:
                system_msg = create_system_message(system_content)
                litellm_messages.append(system_msg)
                metadata["system_message_added"] = True
                logger.info("Added system message",
                           message_preview=system_content[:100] + ('...' if len(system_content) > 100 else ''))
        
        # Convert regular messages
        for msg in source.messages:
            # Check if message contains tool_result blocks
            if isinstance(msg.content, list) and any(
                hasattr(block, 'type') and block.type == "tool_result" 
                for block in msg.content
            ):
                # Handle tool_result blocks specially
                text_parts = handle_tool_result_blocks(msg)
                if text_parts:
                    text_content = " ".join(text_parts).strip()
                    if text_content:
                        litellm_messages.append(LiteLLMMessage(
                            role=msg.role,
                            content=text_content
                        ))
            else:
                # Regular message conversion
                converted_msg = convert_anthropic_message_to_litellm(msg, metadata)
                litellm_messages.append(converted_msg)
        
        metadata["converted_message_count"] = len(litellm_messages)
        return litellm_messages
    
    def _convert_tools(self, source: MessagesRequest, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert tools to LiteLLM format."""
        if not source.tools:
            return None
        
        litellm_tools = []
        logger.debug("Processing tools from request", tool_count=len(source.tools))
        
        for i, tool in enumerate(source.tools):
            logger.debug("Tool details",
                        tool_index=i+1,
                        tool_name=tool.name,
                        description_preview=tool.description[:100] if tool.description else 'None',
                        input_schema_keys=list(tool.input_schema.keys()) if tool.input_schema else 'None')
            
            # Convert tool using task module
            converted_tool = convert_anthropic_tool_to_litellm(tool)
            litellm_tools.append(converted_tool)
            metadata["tool_conversions"] += 1
            logger.debug("Tool converted successfully", tool_name=tool.name)
        
        logger.debug("Total tools being sent to OpenRouter", tool_count=len(litellm_tools))
        return litellm_tools
    
    def _build_litellm_request(
        self, 
        source: MessagesRequest, 
        litellm_messages: List[LiteLLMMessage],
        litellm_tools: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build the final LiteLLM request data."""
        # Map model using task module
        mapping_result = map_model_name(source.model)
        
        # Build base request
        litellm_request_data = {
            "model": mapping_result.mapped_model,
            "messages": [msg.model_dump() for msg in litellm_messages],
            "max_tokens": source.max_tokens,
            "temperature": source.temperature or 1.0,
            "stream": source.stream or False,
            "api_key": config.openrouter_api_key,
            "api_base": "https://openrouter.ai/api/v1",
            "extra_headers": {
                "HTTP-Referer": "https://github.com/openrouter-anthropic-server",
                "X-Title": "OpenRouter Anthropic Server"
            }
        }
        
        # Log request details
        logger.debug("Building LiteLLM request",
                    original_model=source.model,
                    mapped_model=mapping_result.mapped_model,
                    api_base="https://openrouter.ai/api/v1")
        
        # Add optional parameters
        self._add_optional_parameters(source, litellm_request_data, litellm_tools)
        
        return litellm_request_data
    
    def _add_optional_parameters(
        self, 
        source: MessagesRequest, 
        request_data: Dict[str, Any],
        litellm_tools: List[Dict[str, Any]]
    ) -> None:
        """Add optional parameters to the request."""
        if source.top_p is not None:
            request_data["top_p"] = source.top_p
        if source.top_k is not None:
            request_data["top_k"] = source.top_k
        if source.stop_sequences:
            request_data["stop"] = source.stop_sequences
        if litellm_tools:
            request_data["tools"] = litellm_tools
        if source.tool_choice:
            request_data["tool_choice"] = convert_anthropic_tool_choice_to_litellm(source.tool_choice)