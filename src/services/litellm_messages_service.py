"""
LiteLLM Messages Service for native Anthropic format support.

This service calls LiteLLM's /v1/messages endpoint which natively accepts
Anthropic format, eliminating the need for format conversion.
"""

import json
import httpx
from typing import Dict, Any, Optional, AsyncGenerator
from fastapi import HTTPException

from ..models.anthropic import MessagesRequest, MessagesResponse
from ..core.logging_config import get_logger
from ..utils.config import config
from .base import BaseService

logger = get_logger(__name__)


class LiteLLMMessagesService(BaseService):
    """Service for calling LiteLLM's /v1/messages endpoint with Anthropic format."""
    
    def __init__(self):
        """Initialize LiteLLM Messages service."""
        super().__init__("LiteLLMMessages")
        self.base_url = config.litellm_base_url or "http://localhost:4001"
        self.timeout = config.request_timeout
        
    async def create_message(
        self,
        request: MessagesRequest,
        api_key: Optional[str] = None
    ) -> MessagesResponse:
        """
        Create a message using LiteLLM's /v1/messages endpoint.
        
        This endpoint natively accepts Anthropic format, so no conversion needed!
        """
        url = f"{self.base_url}/v1/messages"
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        if api_key:
            headers["x-api-key"] = api_key
        
        # Prepare request body (already in Anthropic format)
        request_body = request.dict(exclude_unset=True)
        
        logger.info("Calling LiteLLM /v1/messages endpoint",
                   model=request.model,
                   messages_count=len(request.messages),
                   url=url)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=request_body,
                    headers=headers
                )
                
                response.raise_for_status()
                
                # Response is already in Anthropic format
                response_data = response.json()
                
                logger.info("LiteLLM /v1/messages call successful",
                           response_id=response_data.get("id"),
                           model=response_data.get("model"))
                
                return MessagesResponse(**response_data)
                
        except httpx.HTTPStatusError as e:
            logger.error("LiteLLM /v1/messages call failed",
                        status_code=e.response.status_code,
                        error=str(e))
            
            # Try to parse error response
            try:
                error_data = e.response.json()
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=error_data
                )
            except:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail={"error": str(e)}
                )
                
        except Exception as e:
            logger.error("Unexpected error calling LiteLLM /v1/messages",
                        error=str(e),
                        error_type=type(e).__name__)
            raise HTTPException(
                status_code=500,
                detail={"error": "LiteLLM messages call failed", "message": str(e)}
            )
    
    async def create_message_stream(
        self,
        request: MessagesRequest,
        api_key: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Create a streaming message using LiteLLM's /v1/messages endpoint.
        
        Yields Anthropic-format SSE chunks.
        """
        url = f"{self.base_url}/v1/messages"
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        if api_key:
            headers["x-api-key"] = api_key
        
        # Prepare request body with streaming enabled
        request_body = request.dict(exclude_unset=True)
        request_body["stream"] = True
        
        logger.info("Starting LiteLLM /v1/messages streaming call",
                   model=request.model,
                   messages_count=len(request.messages),
                   url=url)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    url,
                    json=request_body,
                    headers=headers
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            
                            if data == "[DONE]":
                                logger.info("LiteLLM streaming completed")
                                break
                                
                            try:
                                chunk = json.loads(data)
                                yield chunk
                            except json.JSONDecodeError:
                                logger.warning("Failed to parse streaming chunk", chunk=data)
                                continue
                                
        except httpx.HTTPStatusError as e:
            logger.error("LiteLLM streaming call failed",
                        status_code=e.response.status_code,
                        error=str(e))
            
            # Yield error as SSE chunk
            error_chunk = {
                "type": "error",
                "error": {
                    "type": "api_error",
                    "message": str(e)
                }
            }
            yield error_chunk
            
        except Exception as e:
            logger.error("Unexpected streaming error",
                        error=str(e),
                        error_type=type(e).__name__)
            
            # Yield error as SSE chunk
            error_chunk = {
                "type": "error",
                "error": {
                    "type": "streaming_error",
                    "message": str(e)
                }
            }
            yield error_chunk 