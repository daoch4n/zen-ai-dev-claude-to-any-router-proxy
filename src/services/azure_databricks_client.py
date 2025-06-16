"""
Azure Databricks Claude client service.

This module provides a production-ready client for Azure Databricks Claude endpoints,
handling authentication, retries, error handling, and request formatting.
"""

import httpx
import base64
import json
from typing import Dict, Any, Optional, List, AsyncGenerator
from contextlib import asynccontextmanager

from src.core.logging_config import get_logger
from src.utils.config import config

logger = get_logger(__name__)


class AzureDatabricksClaudeClient:
    """
    Production-ready Azure Databricks Claude client.
    
    Handles authentication, retries, error handling, and maintains
    Anthropic API compatibility while communicating with Azure Databricks.
    """
    
    def __init__(self, workspace_instance: str, databricks_token: str):
        """
        Initialize the Azure Databricks Claude client.
        
        Args:
            workspace_instance: Azure Databricks workspace instance (e.g., "adb-1234567890123456.7")
            databricks_token: Azure Databricks Personal Access Token
        """
        self.workspace_instance = workspace_instance
        self.base_url = f"https://{workspace_instance}.azuredatabricks.net/serving-endpoints"
        self.logger = get_logger(f"{__name__}.AzureDatabricksClaudeClient")
        
        # Create Basic auth header for Azure Databricks PAT authentication
        auth_header = base64.b64encode(f"token:{databricks_token}".encode()).decode()
        
        # HTTP client with proper configuration
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/json",
                "User-Agent": "Claude-Code-Proxy/1.0",
                "Accept": "application/json"
            },
            timeout=httpx.Timeout(config.databricks_timeout),
            follow_redirects=True,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
        
        self.logger.info("Azure Databricks client initialized",
                        workspace=workspace_instance,
                        base_url=self.base_url)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def create_message(self, 
                           endpoint_name: str,
                           messages: List[Dict[str, Any]], 
                           max_tokens: int = 1000,
                           temperature: float = 0.7,
                           stream: bool = False,
                           **kwargs) -> Dict[str, Any]:
        """
        Create a message using Azure Databricks Claude endpoint.
        
        Maintains Anthropic API compatibility while handling Azure Databricks specifics.
        
        Args:
            endpoint_name: Azure Databricks endpoint name (e.g., "databricks-claude-sonnet-4")
            messages: List of messages in Anthropic format
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dict containing the API response
            
        Raises:
            httpx.HTTPStatusError: For HTTP errors
            Exception: For other request failures
        """
        url = f"{self.base_url}/{endpoint_name}/invocations"
        
        # Prepare request payload
        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        # Remove None values to keep payload clean
        payload = {k: v for k, v in payload.items() if v is not None}
        
        self.logger.info("Sending request to Azure Databricks", 
                        endpoint=endpoint_name, 
                        message_count=len(messages),
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stream=stream)
        
        try:
            # Make the request with retries
            response = await self._make_request_with_retries(url, payload)
            
            data = response.json()
            
            # Log successful response
            usage = data.get('usage', {})
            self.logger.info("Received response from Azure Databricks",
                           endpoint=endpoint_name,
                           total_tokens=usage.get('total_tokens', 0),
                           prompt_tokens=usage.get('prompt_tokens', 0),
                           completion_tokens=usage.get('completion_tokens', 0),
                           model=data.get('model', 'unknown'))
            
            return data
            
        except httpx.HTTPStatusError as e:
            self.logger.error("Azure Databricks HTTP error",
                            endpoint=endpoint_name,
                            status_code=e.response.status_code,
                            response_text=e.response.text,
                            url=url)
            raise
        except Exception as e:
            self.logger.error("Azure Databricks request failed", 
                            endpoint=endpoint_name,
                            error=str(e),
                            error_type=type(e).__name__,
                            url=url)
            raise
    
    async def create_streaming_message(self,
                                     endpoint_name: str,
                                     messages: List[Dict[str, Any]], 
                                     max_tokens: int = 1000,
                                     temperature: float = 0.7,
                                     **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Create a streaming message using Azure Databricks Claude endpoint.
        
        Args:
            endpoint_name: Azure Databricks endpoint name
            messages: List of messages in Anthropic format
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Yields:
            Dict containing streaming response chunks
        """
        url = f"{self.base_url}/{endpoint_name}/invocations"
        
        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        self.logger.info("Starting streaming request to Azure Databricks", 
                        endpoint=endpoint_name, 
                        message_count=len(messages))
        
        try:
            async with self.client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line:
                        # Handle Server-Sent Events format
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            
                            if data_str.strip() == "[DONE]":
                                self.logger.info("Streaming completed", endpoint=endpoint_name)
                                break
                                
                            try:
                                chunk_data = json.loads(data_str)
                                yield chunk_data
                            except json.JSONDecodeError:
                                self.logger.warning("Failed to parse streaming chunk", 
                                                  chunk=data_str[:100])
                                continue
                        
        except httpx.HTTPStatusError as e:
            self.logger.error("Azure Databricks streaming HTTP error",
                            endpoint=endpoint_name,
                            status_code=e.response.status_code,
                            response_text=e.response.text)
            raise
        except Exception as e:
            self.logger.error("Azure Databricks streaming failed", 
                            endpoint=endpoint_name,
                            error=str(e),
                            error_type=type(e).__name__)
            raise
    
    async def health_check(self, endpoint_name: str) -> Dict[str, Any]:
        """
        Perform a health check on an Azure Databricks endpoint.
        
        Args:
            endpoint_name: Endpoint to check
            
        Returns:
            Dict containing health check results
        """
        try:
            import time
            start_time = time.time()
            
            # Minimal test request
            response = await self.create_message(
                endpoint_name=endpoint_name,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "model": response.get("model", "unknown"),
                "endpoint": endpoint_name
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
                "endpoint": endpoint_name
            }
    
    async def _make_request_with_retries(self, url: str, payload: Dict[str, Any]) -> httpx.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            url: Request URL
            payload: Request payload
            
        Returns:
            httpx.Response object
            
        Raises:
            httpx.HTTPStatusError: For HTTP errors after all retries
            Exception: For other request failures
        """
        max_retries = config.databricks_max_retries
        
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.post(url, json=payload)
                response.raise_for_status()
                return response
                
            except httpx.HTTPStatusError as e:
                if attempt == max_retries:
                    # Last attempt, re-raise the error
                    raise
                    
                # Check if error is retryable
                if e.response.status_code in [429, 500, 502, 503, 504]:
                    # Retryable error
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning("Retryable error, waiting before retry",
                                      attempt=attempt + 1,
                                      max_retries=max_retries,
                                      status_code=e.response.status_code,
                                      wait_time=wait_time)
                    
                    import asyncio
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # Non-retryable error, raise immediately
                    raise
                    
            except Exception as e:
                if attempt == max_retries:
                    raise
                    
                # Retry on network errors
                wait_time = 2 ** attempt
                self.logger.warning("Network error, retrying",
                                  attempt=attempt + 1,
                                  max_retries=max_retries,
                                  error=str(e),
                                  wait_time=wait_time)
                
                import asyncio
                await asyncio.sleep(wait_time)
                continue
    
    async def close(self):
        """Close the HTTP client and clean up resources."""
        if hasattr(self, 'client') and self.client is not None:
            await self.client.aclose()
            self.logger.info("Azure Databricks client closed")


@asynccontextmanager
async def get_databricks_client() -> AzureDatabricksClaudeClient:
    """
    Async context manager for Azure Databricks client.
    
    Returns:
        Configured AzureDatabricksClaudeClient instance
        
    Raises:
        ValueError: If Azure Databricks is not enabled or not configured
    """
    if not config.is_azure_databricks_backend():
        raise ValueError("Azure Databricks integration is not enabled")
    
    if not config.databricks_host or not config.databricks_token:
        raise ValueError("Azure Databricks host and token must be configured")
    
    client = AzureDatabricksClaudeClient(
        workspace_instance=config.databricks_host,
        databricks_token=config.databricks_token
    )
    
    try:
        yield client
    finally:
        await client.close()


def get_endpoint_for_model(model: str) -> str:
    """
    Get the appropriate Azure Databricks endpoint for a given model.
    
    Args:
        model: Model name or identifier
        
    Returns:
        Azure Databricks endpoint name
    """
    model_mapping = config.get_databricks_model_mapping()
    
    # Try direct lookup first
    if model in model_mapping:
        return model_mapping[model]
    
    # Fallback logic based on model name
    model_lower = model.lower()
    
    if "sonnet-4" in model_lower or "4" in model_lower:
        return config.databricks_claude_sonnet_4_endpoint
    elif "3.7" in model_lower or "3-7" in model_lower:
        return config.databricks_claude_3_7_sonnet_endpoint
    else:
        # Default to Claude 3.7 Sonnet
        logger.warning("Unknown model, defaulting to Claude 3.7 Sonnet", 
                      model=model, 
                      default_endpoint=config.databricks_claude_3_7_sonnet_endpoint)
        return config.databricks_claude_3_7_sonnet_endpoint