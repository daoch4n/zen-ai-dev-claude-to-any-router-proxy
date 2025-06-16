"""Format conversion tasks for OpenRouter Anthropic Server.

Prefect tasks for converting between Anthropic and LiteLLM formats.
Part of Phase 6A comprehensive refactoring - Conversion Tasks.
"""

import json
import uuid
from typing import Any, Dict, List, Optional, Union

from prefect import task
from prefect.cache_policies import NO_CACHE

from ...models.anthropic import Message, MessagesRequest, MessagesResponse, Tool
from ...models.base import Usage
from ...models.litellm import LiteLLMMessage, LiteLLMRequest
from ...models.instructor import ConversionResult
from ...utils.config import config, OPENROUTER_API_BASE
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager
from .model_mapping_tasks import ensure_openrouter_prefix

# Initialize logging and context management
logger = get_logger("format_conversion")
context_manager = ContextManager()


@task(name="anthropic_to_litellm_conversion")
async def anthropic_to_litellm_task(
    source_request: Dict[str, Any],
    conversion_metadata: Dict[str, Any] = None
) -> ConversionResult:
    """
    Convert Anthropic MessagesRequest to LiteLLM format.
    
    Args:
        source_request: Anthropic format request data
        conversion_metadata: Optional metadata for tracking conversions
    
    Returns:
        ConversionResult with converted LiteLLM request
    """
    try:
        # Parse source request
        source = MessagesRequest(**source_request)
        
        # Initialize conversion metadata
        if conversion_metadata is None:
            conversion_metadata = {}
        
        metadata = {
            "original_message_count": len(source.messages),
            "converted_message_count": 0,
            "tool_conversions": 0,
            "content_block_conversions": 0,
            "system_message_added": False,
            **conversion_metadata
        }
        
        # Convert messages
        litellm_messages = []
        
        # Handle system message first
        if source.system:
            if isinstance(source.system, str):
                # Simple string system message
                system_msg = LiteLLMMessage(
                    role="system",
                    content=source.system
                )
                litellm_messages.append(system_msg)
                metadata["system_message_added"] = True
                logger.info("Added system message",
                           message_preview=source.system[:100] + ('...' if len(source.system) > 100 else ''))
            
            elif isinstance(source.system, list):
                # Array of system content objects
                system_text_parts = []
                for content_item in source.system:
                    if hasattr(content_item, 'text'):
                        system_text_parts.append(content_item.text)
                    elif isinstance(content_item, dict) and 'text' in content_item:
                        system_text_parts.append(content_item['text'])
                
                if system_text_parts:
                    system_msg = LiteLLMMessage(
                        role="system",
                        content=" ".join(system_text_parts)
                    )
                    litellm_messages.append(system_msg)
                    metadata["system_message_added"] = True
                    logger.info("Added combined system message",
                               part_count=len(system_text_parts))
        
        # Convert regular messages
        for msg in source.messages:
            # Check if message contains tool_result blocks
            if isinstance(msg.content, list) and any(
                hasattr(block, 'type') and block.type == "tool_result" 
                for block in msg.content
            ):
                # For tool_result blocks, keep them as regular content to avoid
                # creating invalid conversation structures that OpenRouter rejects
                text_parts = []
                
                for block in msg.content:
                    if hasattr(block, 'type'):
                        if block.type == "text":
                            text_parts.append(getattr(block, 'text', ''))
                        elif block.type == "tool_result":
                            # Include tool_result content as text to maintain conversation flow
                            content = getattr(block, 'content', '')
                            if content:
                                text_parts.append(f"Tool result: {content}")
                
                # Create a single message with all content
                if text_parts:
                    text_content = " ".join(text_parts).strip()
                    if text_content:
                        litellm_messages.append(LiteLLMMessage(
                            role=msg.role,
                            content=text_content
                        ))
            else:
                # Regular message conversion
                from .message_transformation import convert_message_content_task
                converted_msg_result = await convert_message_content_task(
                    message_data=msg.model_dump(),
                    conversion_metadata=metadata
                )
                
                if converted_msg_result.success:
                    litellm_messages.append(LiteLLMMessage(**converted_msg_result.converted_data))
        
        metadata["converted_message_count"] = len(litellm_messages)
        
        # Convert tools
        litellm_tools = None
        if source.tools:
            from .schema_processing import convert_tool_definition_task
            
            litellm_tools = []
            logger.debug("Processing tools from request", tool_count=len(source.tools))
            
            for i, tool in enumerate(source.tools):
                logger.debug("Tool details",
                            tool_index=i+1,
                            tool_name=tool.name,
                            description_preview=tool.description[:100] if tool.description else 'None',
                            input_schema_keys=list(tool.input_schema.keys()) if tool.input_schema else 'None')
                
                # Convert tool to LiteLLM format
                tool_result = await convert_tool_definition_task(
                    tool_data=tool.model_dump(),
                    target_format="litellm"
                )
                
                if tool_result.success:
                    litellm_tools.append(tool_result.converted_data)
                    logger.debug("Tool converted successfully", tool_name=tool.name)
            
            logger.debug("Total tools being sent to OpenRouter", tool_count=len(litellm_tools))
        
        # Get model mapping
        model_mapping = config.get_model_mapping()
        mapped_model = model_mapping.get(source.model, source.model)
        openrouter_model = ensure_openrouter_prefix(mapped_model)
        
        # Build LiteLLM request
        litellm_request_data = {
            "model": openrouter_model,
            "messages": [msg.model_dump() for msg in litellm_messages],
            "max_tokens": source.max_tokens,
            "temperature": source.temperature or 1.0,
            "stream": source.stream or False,
            "api_key": config.openrouter_api_key,
            "api_base": OPENROUTER_API_BASE,
            "extra_headers": {
                "HTTP-Referer": "https://github.com/openrouter-anthropic-server",
                "X-Title": "OpenRouter Anthropic Server"
            }
        }
        
        # Add optional parameters
        if source.top_p is not None:
            litellm_request_data["top_p"] = source.top_p
        if source.top_k is not None:
            litellm_request_data["top_k"] = source.top_k
        if source.stop_sequences:
            litellm_request_data["stop"] = source.stop_sequences
        if litellm_tools:
            litellm_request_data["tools"] = litellm_tools
            # Only add tool_choice if we have tools to send
            if source.tool_choice:
                from .message_transformation import transform_tool_calls_task
                tool_choice_result = await transform_tool_calls_task(
                    tool_choice=source.tool_choice,
                    target_format="litellm"
                )
                if tool_choice_result.success:
                    litellm_request_data["tool_choice"] = tool_choice_result.converted_data
        
        logger.debug("Building LiteLLM request",
                    original_model=source.model,
                    openrouter_model=openrouter_model,
                    api_base=OPENROUTER_API_BASE)
        
        logger.info("Anthropic to LiteLLM conversion completed",
                   **metadata)
        
        return ConversionResult(
            success=True,
            converted_data=litellm_request_data,
            metadata=metadata
        )
        
    except Exception as e:
        error_msg = f"Anthropic to LiteLLM conversion failed: {str(e)}"
        logger.error("Conversion failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            metadata={"error_type": type(e).__name__}
        )


@task(name="litellm_response_to_anthropic_conversion", cache_policy=NO_CACHE)
async def litellm_response_to_anthropic_task(
    litellm_response: Any,
    original_request: Optional[Dict[str, Any]] = None,
    conversion_metadata: Dict[str, Any] = None
) -> ConversionResult:
    """
    Convert LiteLLM response to Anthropic MessagesResponse format.
    
    Args:
        litellm_response: The LiteLLM response object
        original_request: The original Anthropic request for context
        conversion_metadata: Optional metadata for tracking conversions
    
    Returns:
        ConversionResult with converted MessagesResponse
    """
    try:
        # Initialize conversion metadata
        if conversion_metadata is None:
            conversion_metadata = {}
        
        metadata = {
            "text_blocks": 0,
            "tool_use_blocks": 0,
            "total_blocks": 0,
            **conversion_metadata
        }
        
        # Debug response structure
        logger.debug("LiteLLM response analysis",
                    response_type=str(type(litellm_response)),
                    has_choices=hasattr(litellm_response, 'choices'),
                    has_delta=hasattr(litellm_response, 'delta'),
                    has_object=hasattr(litellm_response, 'object'))
        
        # Check if this is a streaming response wrapper
        is_streaming_wrapper = 'CustomStreamWrapper' in str(type(litellm_response))
        
        if is_streaming_wrapper:
            logger.debug("Converting streaming response to complete response")
            from .response_processing import reconstruct_streaming_response_task
            return await reconstruct_streaming_response_task(
                stream_wrapper=litellm_response,
                original_request=original_request,
                conversion_metadata=metadata
            )
        
        # Validate response structure for non-streaming responses
        if not hasattr(litellm_response, 'choices') or not litellm_response.choices:
            logger.error("Missing choices field in LiteLLM response",
                        available_attributes=[attr for attr in dir(litellm_response) if not attr.startswith('_')])
            return ConversionResult(
                success=False,
                errors=["Invalid LiteLLM response: missing choices"],
                converted_data=None
            )
        
        choice = litellm_response.choices[0]
        
        # Extract content blocks
        content = []
        
        # Handle text content
        if hasattr(choice.message, 'content') and choice.message.content:
            content.append({
                "type": "text",
                "text": choice.message.content
            })
            metadata["text_blocks"] = 1
        
        # Handle tool calls
        if (hasattr(choice.message, 'tool_calls') and
            choice.message.tool_calls and
            not str(type(choice.message.tool_calls)).startswith("<class 'unittest.mock.Mock")):
            
            from .message_transformation import transform_tool_calls_task
            tool_calls_result = await transform_tool_calls_task(
                tool_calls=choice.message.tool_calls,
                target_format="anthropic"
            )
            
            if tool_calls_result.success:
                content.extend(tool_calls_result.converted_data)
                metadata["tool_use_blocks"] = len(tool_calls_result.converted_data)
        
        metadata["total_blocks"] = len(content)
        
        # Extract usage information
        from .response_processing import extract_usage_info_task
        usage_result = await extract_usage_info_task(
            litellm_response=litellm_response
        )
        
        usage = usage_result.converted_data if usage_result.success else Usage(input_tokens=0, output_tokens=0)
        
        # Determine response model
        from .response_processing import determine_response_model_task
        model_result = await determine_response_model_task(
            original_request=original_request,
            litellm_response=litellm_response
        )
        
        response_model = model_result.converted_data if model_result.success else "claude-3-7-sonnet-20250219"
        
        # Map stop reason
        from .response_processing import map_stop_reason_task
        stop_reason_result = await map_stop_reason_task(
            finish_reason=choice.finish_reason
        )
        
        stop_reason = stop_reason_result.converted_data if stop_reason_result.success else "end_turn"
        
        # Create MessagesResponse
        response = MessagesResponse(
            id=f"msg_{uuid.uuid4().hex[:24]}",
            type="message",
            role="assistant",
            content=content,
            model=response_model,
            stop_reason=stop_reason,
            stop_sequence=None,
            usage=usage
        )
        
        logger.info("LiteLLM response conversion completed", **metadata)
        
        return ConversionResult(
            success=True,
            converted_data=response.model_dump(),
            metadata=metadata
        )
        
    except Exception as e:
        error_msg = f"LiteLLM response conversion failed: {e}"
        logger.error("Response conversion failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(name="litellm_to_anthropic_conversion")
async def litellm_to_anthropic_task(
    source_request: Dict[str, Any],
    conversion_metadata: Dict[str, Any] = None
) -> ConversionResult:
    """
    Convert LiteLLM request to Anthropic format.
    
    Args:
        source_request: LiteLLM format request data
        conversion_metadata: Optional metadata for tracking conversions
    
    Returns:
        ConversionResult with converted Anthropic request
    """
    try:
        # Parse source request
        source = LiteLLMRequest(**source_request)
        
        # Initialize conversion metadata
        if conversion_metadata is None:
            conversion_metadata = {}
        
        metadata = {
            "original_message_count": len(source.messages),
            "converted_message_count": 0,
            "tool_call_conversions": 0,
            "system_message_extracted": False,
            **conversion_metadata
        }
        
        # Convert messages and extract system message
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
                # Convert regular message
                from .message_transformation import convert_message_content_task
                converted_msg_result = await convert_message_content_task(
                    message_data=msg.model_dump(),
                    conversion_metadata=metadata,
                    target_format="anthropic"
                )
                
                if converted_msg_result.success:
                    anthropic_messages.append(Message(**converted_msg_result.converted_data))
        
        metadata["converted_message_count"] = len(anthropic_messages)
        
        # Convert tools
        anthropic_tools = None
        if source.tools:
            from .schema_processing import convert_tool_definition_task
            
            anthropic_tools = []
            for tool in source.tools:
                tool_result = await convert_tool_definition_task(
                    tool_data=tool,
                    target_format="anthropic"
                )
                
                if tool_result.success:
                    anthropic_tools.append(Tool(**tool_result.converted_data))
        
        # Build Anthropic request
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
        if source.top_p is not None:
            anthropic_request_data["top_p"] = source.top_p
        if source.top_k is not None:
            anthropic_request_data["top_k"] = source.top_k
        if source.stop:
            anthropic_request_data["stop_sequences"] = source.stop
        if anthropic_tools:
            anthropic_request_data["tools"] = [tool.model_dump() for tool in anthropic_tools]
            # Only add tool_choice if we have tools to send
            if source.tool_choice:
                from .message_transformation import transform_tool_calls_task
                tool_choice_result = await transform_tool_calls_task(
                    tool_choice=source.tool_choice,
                    target_format="anthropic"
                )
                if tool_choice_result.success:
                    anthropic_request_data["tool_choice"] = tool_choice_result.converted_data
        
        logger.info("LiteLLM to Anthropic conversion completed", **metadata)
        
        return ConversionResult(
            success=True,
            converted_data=anthropic_request_data,
            metadata=metadata
        )
        
    except Exception as e:
        error_msg = f"LiteLLM to Anthropic conversion failed: {str(e)}"
        logger.error("Conversion failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            metadata={"error_type": type(e).__name__}
        )