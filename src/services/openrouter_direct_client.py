"""
Direct OpenRouter HTTP client for LiteLLM bypass implementation.

This module provides a direct HTTP client for communicating with OpenRouter API
without going through LiteLLM, enabling better performance and control.
"""

import json
import time
import uuid
import asyncio
from typing import Dict, Any, Optional, AsyncIterator
import httpx
from datetime import datetime

from ..services.base import BaseService
from ..models.openai import OpenAIChatRequest, OpenAIChatResponse, OpenAIStreamChunk, OpenAIError
from ..core.logging_config import get_logger
from ..utils.config import config

logger = get_logger(__name__)


class OpenRouterError(Exception):
    """Custom exception for OpenRouter API errors that preserves status codes."""
    
    def __init__(self, message: str, status_code: int, error_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data or {}
    
    def is_client_error(self) -> bool:
        """Check if this is a 4xx client error."""
        return 400 <= self.status_code < 500
    
    def is_server_error(self) -> bool:
        """Check if this is a 5xx server error."""
        return 500 <= self.status_code < 600


class OpenRouterDirectClient(BaseService):
    """Direct HTTP client for OpenRouter API without LiteLLM."""
    
    def __init__(self):
        """Initialize OpenRouter direct client."""
        super().__init__("OpenRouterDirect")
        
        self.api_base = config.openrouter_api_base
        self.api_key = config.openrouter_api_key
        self.timeout = config.openrouter_direct_timeout
        self.max_retries = config.openrouter_direct_retries
        
        # Create HTTP client with proper configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/claude-code-proxy",
                "X-Title": "Claude Code Proxy - LiteLLM Bypass"
            }
        )
        
        logger.info("OpenRouter direct client initialized",
                   api_base=self.api_base,
                   timeout=self.timeout,
                   max_retries=self.max_retries)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            logger.debug("OpenRouter direct client closed")
    
    def _prepare_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare headers for OpenRouter API request."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/claude-code-proxy",
            "X-Title": "Claude Code Proxy - LiteLLM Bypass"
        }
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _log_request_details(self, request_data: Dict[str, Any], request_id: str):
        """Log request details for debugging."""
        log_data = {
            "request_id": request_id,
            "model": request_data.get("model"),
            "message_count": len(request_data.get("messages", [])),
            "has_tools": bool(request_data.get("tools")),
            "stream": request_data.get("stream", False),
            "max_tokens": request_data.get("max_tokens"),
            "temperature": request_data.get("temperature")
        }
        
        if request_data.get("tools"):
            tool_names = [tool.get("function", {}).get("name", "unknown") 
                         for tool in request_data["tools"]]
            log_data["tool_names"] = tool_names
        
        logger.debug("OpenRouter direct request details", **log_data)
    
    async def _make_request_with_retry(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        stream: bool = False
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if stream:
                    # For streaming, don't retry - connection issues should fail fast
                    return await self.client.request(
                        method=method,
                        url=url,
                        json=data if data else None,
                        headers=headers
                    )
                else:
                    response = await self.client.request(
                        method=method,
                        url=url,
                        json=data if data else None,
                        headers=headers
                    )
                    
                    # Check for retryable status codes
                    if response.status_code in [429, 502, 503, 504]:
                        if attempt < self.max_retries:
                            wait_time = (2 ** attempt) + 1  # Exponential backoff
                            logger.warning("Retryable error, waiting before retry",
                                         attempt=attempt + 1,
                                         status_code=response.status_code,
                                         wait_time=wait_time)
                            await asyncio.sleep(wait_time)
                            continue
                    
                    return response
                    
            except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) + 1
                    logger.warning("Request failed, retrying",
                                 attempt=attempt + 1,
                                 error=str(e),
                                 wait_time=wait_time)
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error("All retry attempts failed",
                               total_attempts=attempt + 1,
                               final_error=str(e))
                    raise
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
    
    async def chat_completion(
        self,
        request: OpenAIChatRequest,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request directly to OpenRouter.
        
        Args:
            request: OpenAI format chat completion request
            request_id: Optional request ID for tracking
            
        Returns:
            OpenRouter response in OpenAI format
            
        Raises:
            Exception: If request fails after all retries
        """
        if not request_id:
            request_id = str(uuid.uuid4())
        
        start_time = time.time()
        
        try:
            # Convert request to dict
            request_data = request.model_dump(exclude_none=True)
            
            # Log request details
            self._log_request_details(request_data, request_id)
            
            # Prepare URL and headers
            url = f"{self.api_base}/chat/completions"
            headers = self._prepare_headers()
            
            logger.info("Sending direct OpenRouter request",
                       request_id=request_id,
                       model=request_data.get("model"),
                       url=url)
            
            # Make the request
            response = await self._make_request_with_retry(
                method="POST",
                url=url,
                data=request_data,
                headers=headers,
                stream=False
            )
            
            processing_time = time.time() - start_time
            
            # Handle response
            if response.status_code == 200:
                response_data = response.json()
                
                logger.info("OpenRouter direct request successful",
                           request_id=request_id,
                           processing_time=f"{processing_time:.2f}s",
                           response_id=response_data.get("id"),
                           model=response_data.get("model"))
                
                self.log_operation("openrouter_direct_request", success=True,
                                 request_id=request_id,
                                 processing_time=processing_time,
                                 model=request_data.get("model"))
                
                return response_data
            
            else:
                # Handle error response
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"error": {"message": response.text}}
                
                logger.error("OpenRouter direct request failed",
                           request_id=request_id,
                           status_code=response.status_code,
                           error_data=error_data,
                           processing_time=f"{processing_time:.2f}s")
                
                self.log_operation("openrouter_direct_request", success=False,
                                 request_id=request_id,
                                 processing_time=processing_time,
                                 error=error_data,
                                 status_code=response.status_code)
                
                # Raise appropriate exception
                raise OpenRouterError(f"OpenRouter API error {response.status_code}: {error_data}", response.status_code, error_data)
                
        except Exception as e:
            processing_time = time.time() - start_time
            
            logger.error("OpenRouter direct request exception",
                        request_id=request_id,
                        error=str(e),
                        error_type=type(e).__name__,
                        processing_time=f"{processing_time:.2f}s",
                        exc_info=True)
            
            self.log_operation("openrouter_direct_request", success=False,
                             request_id=request_id,
                             processing_time=processing_time,
                             error=str(e),
                             error_type=type(e).__name__)
            
            raise
    
    async def chat_completion_stream(
        self,
        request: OpenAIChatRequest,
        request_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Send streaming chat completion request directly to OpenRouter.
        
        Args:
            request: OpenAI format chat completion request with stream=True
            request_id: Optional request ID for tracking
            
        Yields:
            OpenRouter streaming chunks in OpenAI format
            
        Raises:
            Exception: If request fails
        """
        if not request_id:
            request_id = str(uuid.uuid4())
        
        start_time = time.time()
        
        try:
            # Convert request to dict and ensure streaming
            request_data = request.model_dump(exclude_none=True)
            request_data["stream"] = True
            
            # Log request details
            self._log_request_details(request_data, request_id)
            
            # Prepare URL and headers
            url = f"{self.api_base}/chat/completions"
            headers = self._prepare_headers()
            
            logger.info("Sending direct OpenRouter streaming request",
                       request_id=request_id,
                       model=request_data.get("model"),
                       url=url)
            
            # Make streaming request
            async with self.client.stream(
                method="POST",
                url=url,
                json=request_data,
                headers=headers
            ) as response:
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    error_data = json.loads(error_text) if error_text else {"error": {"message": "Unknown error"}}
                    
                    logger.error("OpenRouter streaming request failed",
                               request_id=request_id,
                               status_code=response.status_code,
                               error_data=error_data)
                    
                    raise OpenRouterError(f"OpenRouter streaming API error {response.status_code}: {error_data}", response.status_code, error_data)
                
                logger.info("OpenRouter streaming connection established",
                           request_id=request_id)
                
                chunk_count = 0
                
                # Process streaming chunks
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        if data_str.strip() == "[DONE]":
                            processing_time = time.time() - start_time
                            logger.info("OpenRouter streaming completed",
                                       request_id=request_id,
                                       chunk_count=chunk_count,
                                       processing_time=f"{processing_time:.2f}s")
                            break
                        
                        try:
                            chunk_data = json.loads(data_str)
                            chunk_count += 1
                            
                            logger.debug("Received streaming chunk",
                                        request_id=request_id,
                                        chunk_index=chunk_count,
                                        chunk_id=chunk_data.get("id"))
                            
                            yield chunk_data
                            
                        except json.JSONDecodeError as e:
                            logger.warning("Failed to parse streaming chunk",
                                         request_id=request_id,
                                         chunk_data=data_str,
                                         error=str(e))
                            continue
                
                processing_time = time.time() - start_time
                
                self.log_operation("openrouter_direct_stream", success=True,
                                 request_id=request_id,
                                 processing_time=processing_time,
                                 chunk_count=chunk_count,
                                 model=request_data.get("model"))
                
        except Exception as e:
            processing_time = time.time() - start_time
            
            logger.error("OpenRouter streaming request exception",
                        request_id=request_id,
                        error=str(e),
                        error_type=type(e).__name__,
                        processing_time=f"{processing_time:.2f}s",
                        exc_info=True)
            
            self.log_operation("openrouter_direct_stream", success=False,
                             request_id=request_id,
                             processing_time=processing_time,
                             error=str(e),
                             error_type=type(e).__name__)
            
            raise
    
    async def test_connection(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Test connection to OpenRouter API.
        
        Args:
            model: Optional model to test with
            
        Returns:
            Connection test result
        """
        test_model = model or config.openrouter_direct_model_format
        
        try:
            from ..models.openai import create_openai_message, create_openai_request
            
            # Create minimal test request
            test_messages = [create_openai_message("user", "test")]
            test_request = create_openai_request(
                model=test_model,
                messages=test_messages,
                max_tokens=1
            )
            
            logger.info("Testing OpenRouter direct connection", model=test_model)
            
            # Make test request
            response = await self.chat_completion(test_request)
            
            return {
                "status": "healthy",
                "model": test_model,
                "response_id": response.get("id"),
                "test_successful": True
            }
            
        except Exception as e:
            logger.error("OpenRouter connection test failed",
                        model=test_model,
                        error=str(e))
            
            return {
                "status": "unhealthy",
                "model": test_model,
                "error": str(e),
                "test_successful": False
            }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of OpenRouter direct client.
        
        Returns:
            Health status information
        """
        try:
            # Basic configuration check
            health_info = {
                "service": "OpenRouterDirect",
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "configuration": {
                    "api_base": self.api_base,
                    "timeout": self.timeout,
                    "max_retries": self.max_retries,
                    "api_key_configured": bool(self.api_key and len(self.api_key) > 10)
                }
            }
            
            # Test connection if requested
            if config.model_health_checks:
                connection_test = await self.test_connection()
                health_info["connection_test"] = connection_test
                
                if not connection_test["test_successful"]:
                    health_info["status"] = "degraded"
            
            return health_info
            
        except Exception as e:
            logger.error("Health status check failed", error=str(e))
            
            return {
                "service": "OpenRouterDirect",
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            } 