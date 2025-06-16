"""
LiteLLM bypass flow service for direct OpenRouter integration.

This module orchestrates the complete bypass flow: Anthropic → OpenAI → OpenRouter → OpenAI → Anthropic,
providing direct communication with OpenRouter while maintaining Anthropic API compatibility.
"""

import time
import uuid
import asyncio
from typing import Dict, Any, Optional, AsyncIterator, Union
from datetime import datetime

from ..services.base import ConversionService
from ..services.openrouter_direct_client import OpenRouterDirectClient
from ..services.anthropic_openai_converter import AnthropicOpenAIConverter
from ..services.http_client import HTTPClientService  # Fallback
from ..models.anthropic import MessagesRequest, MessagesResponse
from ..models.instructor import ConversionResult
from ..core.logging_config import get_logger
from ..utils.config import config

logger = get_logger(__name__)


class LiteLLMBypassFlow(ConversionService):
    """Orchestrates the complete LiteLLM bypass flow."""
    
    def __init__(self):
        """Initialize the bypass flow service."""
        super().__init__("LiteLLMBypass")
        
        # Initialize components
        self.converter = AnthropicOpenAIConverter()
        self.openrouter_client = OpenRouterDirectClient()
        self.fallback_enabled = config.bypass_fallback_enabled
        
        # Initialize fallback client if needed
        self._fallback_client = None
        if self.fallback_enabled:
            self._fallback_client = HTTPClientService()
        
        logger.info("LiteLLM bypass flow initialized",
                   fallback_enabled=self.fallback_enabled,
                   openrouter_base=config.openrouter_api_base,
                   bypass_default=True)
    
    async def close(self):
        """Close the bypass flow and cleanup resources."""
        if self.openrouter_client:
            await self.openrouter_client.close()
        logger.debug("LiteLLM bypass flow closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    def convert(self, source: MessagesRequest, **kwargs) -> ConversionResult:
        """
        Synchronous wrapper for async convert method.
        
        Args:
            source: Anthropic MessagesRequest
            **kwargs: Additional parameters
            
        Returns:
            ConversionResult with bypass flow result
        """
        # Handle both sync and async contexts
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.convert_async(source, **kwargs)
                    )
                    return future.result()
            else:
                # We're in a sync context
                return asyncio.run(self.convert_async(source, **kwargs))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(self.convert_async(source, **kwargs))
    
    async def convert_async(self, source: MessagesRequest, **kwargs) -> ConversionResult:
        """
        Complete bypass flow: Anthropic → OpenAI → OpenRouter → OpenAI → Anthropic.
        
        Args:
            source: Anthropic MessagesRequest
            **kwargs: Additional parameters
            
        Returns:
            ConversionResult with converted Anthropic response
        """
        request_id = kwargs.get("request_id", str(uuid.uuid4()))
        start_time = time.time()
        
        try:
            logger.info("Starting LiteLLM bypass flow",
                       request_id=request_id,
                       model=source.model,
                       bypass_enabled=config.is_openrouter_backend())
            
            # Step 1: Validate input request
            self._validate_request(source)
            
            # Step 2: Preserve original model name and convert for bypass mode  
            original_model = source.model  # Save the truly original model name
            bypass_model = self._convert_model_for_bypass(source.model)
            if bypass_model != source.model:
                # Create a copy of the request with the converted model
                source_dict = source.model_dump()
                source_dict["model"] = bypass_model
                source = MessagesRequest(**source_dict)
                logger.debug("Model converted for bypass",
                           original_model=original_model,
                           bypass_model=bypass_model,
                           request_id=request_id)
            
            # Step 3: Convert Anthropic → OpenAI format
            logger.debug("Converting Anthropic request to OpenAI format", request_id=request_id)
            openai_request = self.converter.anthropic_to_openai(source)
            
            # Step 4: Call OpenRouter directly
            logger.debug("Calling OpenRouter directly", request_id=request_id)
            openai_response = await self.openrouter_client.chat_completion(
                openai_request,
                request_id=request_id
            )
            
            # Step 5: Convert OpenAI response → Anthropic format
            logger.debug("Converting OpenAI response to Anthropic format", request_id=request_id)
            
            # Create a copy of the source with the original model name for response conversion
            original_source_dict = source.model_dump()
            original_source_dict["model"] = original_model  
            original_source = MessagesRequest(**original_source_dict)
            
            anthropic_response = self.converter.openai_to_anthropic_response(
                openai_response,
                original_source  # Use source with original model name
            )
            
            processing_time = time.time() - start_time
            
            logger.info("LiteLLM bypass flow completed successfully",
                       request_id=request_id,
                       processing_time=f"{processing_time:.2f}s",
                       response_id=anthropic_response.id,
                       bypass_model=bypass_model)
            
            self.log_operation("litellm_bypass_flow", success=True,
                             request_id=request_id,
                             processing_time=processing_time,
                             model=source.model,
                             bypass_model=bypass_model)
            
            # Return successful conversion result
            return ConversionResult(
                success=True,
                converted_data=anthropic_response.model_dump(),
                metadata={
                    "processing_time": processing_time,
                    "bypass_used": True,
                    "model": source.model,
                    "bypass_model": bypass_model,
                    "request_id": request_id
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Import here to avoid circular imports
            from .openrouter_direct_client import OpenRouterError
            
            # Handle OpenRouter client errors (4xx) differently from server errors
            if isinstance(e, OpenRouterError) and e.is_client_error():
                # For 4xx client errors, convert to Anthropic error format and return
                logger.warning("OpenRouter client error, returning error response",
                             request_id=request_id,
                             status_code=e.status_code,
                             error=str(e))
                
                # Convert OpenRouter error to Anthropic error format  
                error_response = self._convert_openrouter_error_to_anthropic(e, request_id)
                
                return ConversionResult(
                    success=False,
                    converted_data=error_response,
                    metadata={
                        "processing_time": processing_time,
                        "bypass_used": True,
                        "client_error": True,
                        "status_code": e.status_code,
                        "request_id": request_id
                    },
                    errors=[f"Client error {e.status_code}: {str(e)}"]
                )
            
            logger.error("LiteLLM bypass flow failed",
                        request_id=request_id,
                        error=str(e),
                        error_type=type(e).__name__,
                        processing_time=f"{processing_time:.2f}s",
                        exc_info=True)
            
            self.log_operation("litellm_bypass_flow", success=False,
                             request_id=request_id,
                             processing_time=processing_time,
                             error=str(e),
                             error_type=type(e).__name__)
            
            # Try fallback to LiteLLM if enabled (only for server errors, not client errors)
            if self.fallback_enabled and self._fallback_client:
                logger.info("Attempting fallback to LiteLLM",
                           request_id=request_id,
                           original_error=str(e))
                
                try:
                    # Remove request_id from kwargs to avoid duplicate parameter
                    fallback_kwargs = {k: v for k, v in kwargs.items() if k != "request_id"}
                    return await self._fallback_to_litellm(source, e, request_id, **fallback_kwargs)
                    
                except Exception as fallback_error:
                    logger.error("Fallback to LiteLLM also failed",
                               request_id=request_id,
                               fallback_error=str(fallback_error),
                               original_error=str(e))
                    
                    # Return error result with both errors
                    return ConversionResult(
                        success=False,
                        errors=[
                            f"Bypass failed: {str(e)}",
                            f"Fallback failed: {str(fallback_error)}"
                        ],
                        metadata={
                            "processing_time": processing_time,
                            "bypass_attempted": True,
                            "fallback_attempted": True,
                            "request_id": request_id
                        }
                    )
            
            # Return error result without fallback
            return ConversionResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "processing_time": processing_time,
                    "bypass_attempted": True,
                    "fallback_enabled": self.fallback_enabled,
                    "request_id": request_id
                }
            )
    
    async def convert_streaming(
        self,
        source: MessagesRequest,
        **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Handle streaming bypass flow.
        
        Args:
            source: Anthropic MessagesRequest with stream=True
            **kwargs: Additional parameters
            
        Yields:
            Anthropic format streaming chunks
        """
        request_id = kwargs.get("request_id", str(uuid.uuid4()))
        start_time = time.time()
        
        try:
            logger.info("Starting LiteLLM bypass streaming flow",
                       request_id=request_id,
                       model=source.model)
            
            # Step 1: Validate input request
            self._validate_request(source)
            
            # Step 2: Preserve original model name and convert for bypass mode
            original_model = source.model  # Save the truly original model name
            bypass_model = self._convert_model_for_bypass(source.model)
            if bypass_model != source.model:
                # Create a copy of the request with the converted model
                source_dict = source.model_dump()
                source_dict["model"] = bypass_model
                source = MessagesRequest(**source_dict)
            
            # Step 3: Convert Anthropic → OpenAI format (with streaming enabled)
            openai_request = self.converter.anthropic_to_openai(source)
            openai_request.stream = True
            
            logger.debug("Starting OpenRouter streaming request", request_id=request_id)
            
            # Step 4: Stream from OpenRouter and convert chunks
            chunk_count = 0
            
            # Create source with original model name for chunk conversion
            original_source_dict = source.model_dump()
            original_source_dict["model"] = original_model
            original_source = MessagesRequest(**original_source_dict)
            
            async for openai_chunk in self.openrouter_client.chat_completion_stream(
                openai_request,
                request_id=request_id
            ):
                # Step 5: Convert each OpenAI chunk → Anthropic format
                anthropic_chunk = self.converter.convert_streaming_chunk(
                    openai_chunk,
                    original_source  # Use source with original model name
                )
                
                chunk_count += 1
                logger.debug("Converted streaming chunk",
                           request_id=request_id,
                           chunk_index=chunk_count,
                           chunk_type=anthropic_chunk.get("type"))
                
                yield anthropic_chunk
            
            processing_time = time.time() - start_time
            
            logger.info("LiteLLM bypass streaming completed",
                       request_id=request_id,
                       chunk_count=chunk_count,
                       processing_time=f"{processing_time:.2f}s")
            
            self.log_operation("litellm_bypass_streaming", success=True,
                             request_id=request_id,
                             processing_time=processing_time,
                             chunk_count=chunk_count,
                             model=source.model,
                             bypass_model=bypass_model)
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            logger.error("LiteLLM bypass streaming failed",
                        request_id=request_id,
                        error=str(e),
                        error_type=type(e).__name__,
                        processing_time=f"{processing_time:.2f}s",
                        exc_info=True)
            
            self.log_operation("litellm_bypass_streaming", success=False,
                             request_id=request_id,
                             processing_time=processing_time,
                             error=str(e),
                             error_type=type(e).__name__)
            
            # Try fallback streaming if enabled
            if self.fallback_enabled and self._fallback_client:
                logger.info("Attempting streaming fallback to LiteLLM",
                           request_id=request_id)
                
                try:
                    # Remove request_id from kwargs to avoid duplicate parameter
                    fallback_kwargs = {k: v for k, v in kwargs.items() if k != "request_id"}
                    async for chunk in self._fallback_streaming_to_litellm(source, e, request_id, **fallback_kwargs):
                        yield chunk
                        
                except Exception as fallback_error:
                    logger.error("Streaming fallback to LiteLLM failed",
                               request_id=request_id,
                               fallback_error=str(fallback_error))
                    
                    # Yield error chunk
                    yield {
                        "type": "error",
                        "error": {
                            "type": "bypass_and_fallback_failed",
                            "message": f"Both bypass and fallback failed",
                            "bypass_error": str(e),
                            "fallback_error": str(fallback_error)
                        }
                    }
            else:
                # Yield error chunk
                yield {
                    "type": "error",
                    "error": {
                        "type": "bypass_failed",
                        "message": str(e)
                    }
                }
    
    def _validate_request(self, request: MessagesRequest) -> None:
        """Validate the request before processing."""
        if not request.model:
            raise ValueError("Model is required")
        
        if not request.messages:
            raise ValueError("Messages are required")
        
        if len(request.messages) == 0:
            raise ValueError("At least one message is required")
    
    def _convert_model_for_bypass(self, model: str) -> str:
        """Convert model name for bypass mode (remove openrouter/ prefix if present)."""
        bypass_mapping = config.get_bypass_model_mapping()
        return bypass_mapping.get(model, model)
    
    def _convert_openrouter_error_to_anthropic(self, error: 'OpenRouterError', request_id: str) -> Dict[str, Any]:
        """Convert OpenRouter error to Anthropic error format."""
        # Extract error details from OpenRouter error
        error_message = "Request failed"
        error_type = "invalid_request_error"
        
        if error.error_data and "error" in error.error_data:
            error_info = error.error_data["error"]
            error_message = error_info.get("message", str(error))
            
            # Map error types based on status code
            if error.status_code == 400:
                error_type = "invalid_request_error"
            elif error.status_code == 401:
                error_type = "authentication_error"
            elif error.status_code == 403:
                error_type = "permission_error"
            elif error.status_code == 404:
                error_type = "not_found_error"
            elif error.status_code == 429:
                error_type = "rate_limit_error"
            else:
                error_type = "api_error"
        
        # Return Anthropic-compatible error response
        return {
            "type": "error",
            "error": {
                "type": error_type,
                "message": error_message
            }
        }
    
    async def _fallback_to_litellm(
        self,
        source: MessagesRequest,
        original_error: Exception,
        request_id: str,
        **kwargs
    ) -> ConversionResult:
        """Fallback to LiteLLM when bypass fails."""
        try:
            logger.info("Executing fallback to LiteLLM",
                       request_id=request_id,
                       original_error=str(original_error))
            
            # Use the existing LiteLLM flow
            from ..services.conversion import AnthropicToLiteLLMConverter, LiteLLMResponseToAnthropicConverter
            
            # Convert to LiteLLM format
            litellm_converter = AnthropicToLiteLLMConverter()
            litellm_request_result = litellm_converter.convert(source)
            
            if not litellm_request_result.success:
                raise ValueError(f"LiteLLM conversion failed: {litellm_request_result.errors}")
            
            # Make LiteLLM request
            litellm_response = await self._fallback_client.make_litellm_request(
                litellm_request_result.converted_data,
                request_id
            )
            
            # Convert response back to Anthropic format
            response_converter = LiteLLMResponseToAnthropicConverter()
            anthropic_result = response_converter.convert(litellm_response, source)
            
            if not anthropic_result.success:
                raise ValueError(f"Response conversion failed: {anthropic_result.errors}")
            
            logger.info("Fallback to LiteLLM successful", request_id=request_id)
            
            # Mark as fallback result
            fallback_result = ConversionResult(
                success=True,
                converted_data=anthropic_result.converted_data,
                metadata={
                    "bypass_attempted": True,
                    "fallback_used": True,
                    "original_error": str(original_error),
                    "request_id": request_id
                }
            )
            
            return fallback_result
            
        except Exception as e:
            logger.error("Fallback to LiteLLM failed",
                        request_id=request_id,
                        error=str(e),
                        exc_info=True)
            raise
    
    async def _fallback_streaming_to_litellm(
        self,
        source: MessagesRequest,
        original_error: Exception,
        request_id: str,
        **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Fallback streaming to LiteLLM when bypass fails."""
        try:
            logger.info("Executing streaming fallback to LiteLLM", request_id=request_id)
            
            # This would need to be implemented to stream from the existing LiteLLM flow
            # For now, we'll yield an error indicating fallback streaming is not implemented
            yield {
                "type": "error",
                "error": {
                    "type": "fallback_streaming_not_implemented",
                    "message": "Streaming fallback to LiteLLM not yet implemented",
                    "original_error": str(original_error)
                }
            }
            
        except Exception as e:
            logger.error("Streaming fallback to LiteLLM failed",
                        request_id=request_id,
                        error=str(e))
            raise 