"""
Multi-Model Converter for Universal AI Provider Support.

This converter handles request/response transformation between our internal format
and the various formats used by 100+ LiteLLM models across all AI providers.

Phase 3B: Multi-Model Streaming Support
"""

import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from ...services.base import BaseService
from ...models.anthropic import MessagesRequest, MessagesResponse
from ...core.logging_config import get_logger
from ...services.universal.universal_streaming_service import AIProvider, UniversalStreamingChunk

logger = get_logger("universal.multi_model_converter")


class MultiModelConverter(BaseService):
    """Converter for handling requests/responses across all AI providers."""
    
    def __init__(self):
        """Initialize the multi-model converter."""
        super().__init__("MultiModelConverter")
        
        # Provider-specific conversion configurations
        self.conversion_configs = {
            AIProvider.ANTHROPIC: {
                "request_format": "anthropic_messages",
                "response_format": "anthropic_streaming",
                "tool_format": "anthropic_tools",
                "supports_system_message": True,
                "supports_reasoning": True,
                "max_tokens_field": "max_tokens"
            },
            AIProvider.OPENAI: {
                "request_format": "openai_chat",
                "response_format": "openai_streaming",
                "tool_format": "openai_functions",
                "supports_system_message": True,
                "supports_reasoning": False,
                "max_tokens_field": "max_tokens"
            },
            AIProvider.GOOGLE: {
                "request_format": "google_gemini",
                "response_format": "google_streaming",
                "tool_format": "google_functions",
                "supports_system_message": True,
                "supports_reasoning": False,
                "max_tokens_field": "max_output_tokens"
            }
        }
        
        # Universal conversion metrics
        self.conversion_metrics = {
            "total_conversions": 0,
            "conversions_by_provider": {},
            "conversion_errors": 0,
            "successful_conversions": 0,
            "average_conversion_time": 0.0
        }
        
        logger.info("Multi-Model Converter initialized",
                   supported_providers=len(self.conversion_configs))
    
    def convert_request_to_provider_format(
        self,
        request: MessagesRequest,
        provider: AIProvider,
        model: str
    ) -> Dict[str, Any]:
        """
        Convert internal request format to provider-specific format.
        
        Args:
            request: Internal MessagesRequest
            provider: Target AI provider
            model: Target model name
            
        Returns:
            Dict: Provider-specific request format
        """
        try:
            conversion_start = datetime.utcnow()
            
            # Get provider configuration
            config = self.conversion_configs.get(provider, self.conversion_configs[AIProvider.ANTHROPIC])
            
            logger.debug("Converting request to provider format",
                        provider=provider.value,
                        model=model,
                        request_format=config["request_format"])
            
            # Base conversion
            converted_request = {
                "model": model,
                "stream": True,  # Always enable streaming for universal support
                "messages": self._convert_messages_to_provider_format(request.messages, provider, config)
            }
            
            # Add provider-specific fields
            if hasattr(request, 'max_tokens') and request.max_tokens:
                max_tokens_field = config["max_tokens_field"]
                converted_request[max_tokens_field] = request.max_tokens
            
            if hasattr(request, 'temperature') and request.temperature is not None:
                converted_request["temperature"] = request.temperature
            
            # Convert tools if supported
            if hasattr(request, 'tools') and request.tools and config["supports_system_message"]:
                converted_request["tools"] = self._convert_tools_to_provider_format(
                    request.tools, provider, config
                )
            
            # Update metrics
            self._update_conversion_metrics(provider, conversion_start, True)
            
            logger.debug("Request conversion completed",
                        provider=provider.value,
                        model=model,
                        converted_fields=list(converted_request.keys()))
            
            return converted_request
            
        except Exception as e:
            logger.error("Request conversion failed",
                        provider=provider.value,
                        model=model,
                        error=str(e),
                        exc_info=True)
            
            self._update_conversion_metrics(provider, conversion_start, False)
            
            # Return fallback format
            return {
                "model": model,
                "stream": True,
                "messages": [{"role": "user", "content": "Conversion error occurred"}]
            }
    
    def _convert_messages_to_provider_format(
        self,
        messages: List[Any],
        provider: AIProvider,
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Convert messages to provider-specific format."""
        converted_messages = []
        
        for message in messages:
            # Handle both dict and object formats
            if hasattr(message, 'role') and hasattr(message, 'content'):
                # Pydantic model or object with attributes
                role = getattr(message, 'role', 'user')
                content = getattr(message, 'content', '')
            elif isinstance(message, dict):
                # Dictionary format
                role = message.get("role", "user")
                content = message.get("content", "")
            else:
                # Fallback
                role = "user"
                content = str(message)
            
            if provider == AIProvider.ANTHROPIC:
                # Anthropic format
                converted_message = {
                    "role": role,
                    "content": content
                }
            
            elif provider in [AIProvider.OPENAI, AIProvider.GOOGLE]:
                # OpenAI-compatible format
                converted_message = {
                    "role": role,
                    "content": content
                }
            
            else:
                # Generic format
                converted_message = {
                    "role": role,
                    "content": content
                }
            
            converted_messages.append(converted_message)
        
        return converted_messages
    
    def _convert_tools_to_provider_format(
        self,
        tools: List[Dict[str, Any]],
        provider: AIProvider,
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Convert tools to provider-specific format."""
        converted_tools = []
        
        for tool in tools:
            if provider == AIProvider.ANTHROPIC:
                # Anthropic tool format
                converted_tool = {
                    "name": tool.get("name", ""),
                    "description": tool.get("description", ""),
                    "input_schema": tool.get("input_schema", {})
                }
            
            elif provider in [AIProvider.OPENAI, AIProvider.GOOGLE]:
                # OpenAI function format
                converted_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.get("name", ""),
                        "description": tool.get("description", ""),
                        "parameters": tool.get("input_schema", {})
                    }
                }
            
            else:
                # Generic tool format
                converted_tool = tool
            
            converted_tools.append(converted_tool)
        
        return converted_tools
    
    def convert_universal_chunk_to_response_format(
        self,
        chunk: UniversalStreamingChunk,
        provider: AIProvider,
        request_id: str
    ) -> Dict[str, Any]:
        """
        Convert universal streaming chunk to provider-specific response format.
        
        Args:
            chunk: Universal streaming chunk
            provider: Source AI provider
            request_id: Request identifier
            
        Returns:
            Dict: Provider-specific response chunk
        """
        try:
            # Get provider configuration
            config = self.conversion_configs.get(provider, self.conversion_configs[AIProvider.ANTHROPIC])
            
            # Base response structure
            response_chunk = {
                "id": request_id,
                "object": "chat.completion.chunk",
                "created": int(datetime.utcnow().timestamp()),
                "model": "universal-model",
                "provider": provider.value
            }
            
            # Convert based on chunk type
            if chunk.normalized_type == "content":
                if provider == AIProvider.ANTHROPIC:
                    response_chunk.update({
                        "type": "message_delta",
                        "delta": {
                            "type": "text_delta",
                            "text": chunk.content
                        }
                    })
                else:
                    # OpenAI-compatible format
                    response_chunk.update({
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "content": chunk.content
                            },
                            "finish_reason": None
                        }]
                    })
            
            elif chunk.normalized_type == "thinking":
                if provider == AIProvider.ANTHROPIC:
                    response_chunk.update({
                        "type": "thinking_delta",
                        "delta": {
                            "thinking": chunk.thinking_content
                        }
                    })
                else:
                    # Convert thinking to content for non-Anthropic providers
                    response_chunk.update({
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "content": f"[Thinking: {chunk.thinking_content}]"
                            },
                            "finish_reason": None
                        }]
                    })
            
            elif chunk.normalized_type == "tool_result":
                # Tool results are handled as content
                tool_result_content = f"Tool execution completed: {chunk.content}"
                if provider == AIProvider.ANTHROPIC:
                    response_chunk.update({
                        "type": "message_delta",
                        "delta": {
                            "type": "text_delta",
                            "text": tool_result_content
                        }
                    })
                else:
                    response_chunk.update({
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "content": tool_result_content
                            },
                            "finish_reason": None
                        }]
                    })
            
            elif chunk.normalized_type == "error":
                # Error handling
                response_chunk.update({
                    "error": {
                        "message": chunk.content,
                        "type": "universal_streaming_error",
                        "provider": provider.value
                    }
                })
            
            # Add universal metadata
            response_chunk["universal_metadata"] = {
                "original_provider": chunk.provider.value,
                "chunk_type": chunk.normalized_type,
                "timestamp": chunk.timestamp,
                "metadata": chunk.metadata
            }
            
            return response_chunk
            
        except Exception as e:
            logger.error("Universal chunk conversion failed",
                        provider=provider.value,
                        chunk_type=chunk.normalized_type,
                        error=str(e))
            
            # Return error chunk
            return {
                "id": request_id,
                "error": {
                    "message": f"Chunk conversion error: {str(e)}",
                    "type": "conversion_error",
                    "provider": provider.value
                }
            }
    
    def _update_conversion_metrics(
        self,
        provider: AIProvider,
        start_time: datetime,
        success: bool
    ) -> None:
        """Update conversion metrics."""
        # Update total conversions
        self.conversion_metrics["total_conversions"] += 1
        
        # Update by provider
        provider_key = provider.value
        if provider_key not in self.conversion_metrics["conversions_by_provider"]:
            self.conversion_metrics["conversions_by_provider"][provider_key] = 0
        self.conversion_metrics["conversions_by_provider"][provider_key] += 1
        
        # Update success/error counts
        if success:
            self.conversion_metrics["successful_conversions"] += 1
        else:
            self.conversion_metrics["conversion_errors"] += 1
    
    def get_conversion_metrics(self) -> Dict[str, Any]:
        """Get conversion metrics."""
        return {
            **self.conversion_metrics,
            "supported_providers": [p.value for p in self.conversion_configs.keys()],
            "conversion_success_rate": (
                self.conversion_metrics["successful_conversions"] / 
                max(self.conversion_metrics["total_conversions"], 1)
            ),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_supported_providers_info(self) -> Dict[str, Any]:
        """Get detailed information about supported providers."""
        return {
            provider.value: {
                "request_format": config["request_format"],
                "response_format": config["response_format"],
                "tool_format": config["tool_format"],
                "supports_system_message": config["supports_system_message"],
                "supports_reasoning": config["supports_reasoning"],
                "max_tokens_field": config["max_tokens_field"]
            }
            for provider, config in self.conversion_configs.items()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for multi-model converter."""
        try:
            return {
                "overall_healthy": True,
                "supported_providers": len(self.conversion_configs),
                "conversion_metrics": self.conversion_metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Multi-model converter health check failed", error=str(e))
            return {
                "overall_healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
