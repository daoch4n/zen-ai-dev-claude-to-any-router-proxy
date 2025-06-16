"""
HTTP Client service for OpenRouter Anthropic Server.
Provides proper HTTP client configuration for LiteLLM with proxy support.
"""

import os
import asyncio
from typing import Dict, Any, Optional
import litellm
from litellm import acompletion
from datetime import datetime

from ..core.logging_config import get_logger
from ..services.context_manager import ContextManager
from ..utils.config import config

# Import LiteLLM exception types for better error handling
from litellm import (
    BadRequestError, 
    ContextWindowExceededError,
    ContentPolicyViolationError,
    AuthenticationError,
    RateLimitError,
    Timeout,
    NotFoundError,
    ServiceUnavailableError,
    APIConnectionError,
    BudgetExceededError
)

# Initialize logging and context management
logger = get_logger("http_client")
context_manager = ContextManager()
from ..utils.error_logger import log_error
from .base import BaseService


class HTTPClientService(BaseService):
    """Service for managing HTTP client configuration and LiteLLM calls."""
    
    def __init__(self):
        """Initialize HTTP client service."""
        super().__init__("HTTPClient")
        self._configure_litellm()
    
    def _configure_litellm(self):
        """Configure LiteLLM with proper HTTP client settings."""
        try:
            # Configure LiteLLM settings
            litellm.set_verbose = config.debug_enabled
            
            # Set timeout configuration
            litellm.request_timeout = config.request_timeout
            
            # Enhanced LiteLLM configuration based on API documentation
            # Add retry configuration
            litellm.num_retries = int(os.getenv("LITELLM_NUM_RETRIES", "3"))
            litellm.retry_delay = float(os.getenv("LITELLM_RETRY_DELAY", "1.0"))
            
            # Add rate limiting configuration
            litellm.rpm = int(os.getenv("LITELLM_RPM", "10000"))  # Requests per minute
            litellm.tpm = int(os.getenv("LITELLM_TPM", "200000"))  # Tokens per minute
            
            # Configure caching if enabled
            if config.enable_caching:
                # Enable LiteLLM's built-in caching
                litellm.cache = litellm.Cache(
                    type="redis" if os.getenv("REDIS_URL") else "local",
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", "6379")),
                    password=os.getenv("REDIS_PASSWORD"),
                    ttl=config.cache_ttl
                )
            
            # Configure proxy settings if needed
            self._configure_proxy_settings()
            
            self.log_operation("litellm_configuration", success=True, 
                             timeout=config.request_timeout, 
                             debug_enabled=config.debug_enabled,
                             caching_enabled=config.enable_caching,
                             retries=litellm.num_retries)
            
        except Exception as e:
            error_msg = f"LiteLLM configuration failed: {e}"
            self.log_operation("litellm_configuration", success=False, error=error_msg)
            raise
    
    def _configure_proxy_settings(self):
        """Configure proxy settings for LiteLLM."""
        # Check if proxy configuration is needed
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
        proxy_settings = {}
        
        for var in proxy_vars:
            if var in os.environ:
                proxy_settings[var] = os.environ[var]
        
        if proxy_settings:
            logger.info("Detected proxy settings", proxy_keys=list(proxy_settings.keys()))
            
            # For OpenRouter, we typically want to bypass proxy
            # This is a cleaner approach than manipulating environment variables
            self._setup_openrouter_proxy_bypass()
        else:
            logger.info("No proxy settings detected")
    
    def _setup_openrouter_proxy_bypass(self):
        """Setup proxy bypass for OpenRouter API calls."""
        # LiteLLM uses httpx internally, which respects proxy settings
        # For OpenRouter, we want to bypass proxy to avoid connection issues
        
        # Option 1: Configure httpx client with no proxy for OpenRouter domains
        openrouter_domains = [
            "openrouter.ai",
            "*.openrouter.ai"
        ]
        
        # Store proxy bypass configuration
        self._proxy_bypass_domains = openrouter_domains
        
        logger.info("Configured proxy bypass for OpenRouter domains", domains=openrouter_domains)
    
    async def make_litellm_request(self, request_data: Dict[str, Any], request_id: str) -> Any:
        """
        Make a LiteLLM API request with proper HTTP client configuration.
        
        Args:
            request_data: The LiteLLM request data
            request_id: Unique request ID for tracking
            
        Returns:
            LiteLLM response object
        """
        try:
            import time
            start_time = time.time()
            
            logger.info("Making LiteLLM API call", request_id=request_id)
            
            # Log request details (excluding sensitive data)
            self._log_request_details(request_data)
            
            # Configure request-specific settings
            request_config = self._prepare_request_config(request_data)
            
            # Make the API call with proper configuration
            response = await self._execute_litellm_request(request_config)
            
            processing_time = time.time() - start_time
            
            # DEBUG: Log response details for diagnosis
            logger.debug("LiteLLM response received",
                        response_type=str(type(response)),
                        response_attributes=[attr for attr in dir(response) if not attr.startswith('_')],
                        request_id=request_id)
            if hasattr(response, 'choices'):
                logger.debug("Response choices info",
                           choices_count=len(response.choices) if response.choices else 0,
                           request_id=request_id)
            if hasattr(response, 'object'):
                logger.debug("Response object type",
                           object_type=response.object,
                           request_id=request_id)
            
            self.log_operation("litellm_api_call", success=True,
                             request_id=request_id,
                             processing_time=processing_time,
                             model=request_data.get('model', 'unknown'))
            
            logger.info("LiteLLM API call completed",
                       processing_time=f"{processing_time:.2f}s",
                       request_id=request_id)
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Use enhanced exception handling
            self._handle_litellm_exception(e, request_data, processing_time)
            
            # Log operation failure
            self.log_operation("litellm_api_call", success=False,
                             request_id=request_id,
                             processing_time=processing_time,
                             error=str(e),
                             error_type=type(e).__name__)
            
            logger.error("LiteLLM API call failed",
                        error=str(e),
                        error_type=type(e).__name__,
                        processing_time=f"{processing_time:.2f}s",
                        request_id=request_id,
                        error_log_file=f"{config.unified_logs_dir}/errors/errors_{datetime.now().strftime('%Y-%m-%d')}.jsonl",
                        exc_info=True)
            raise
    
    def _log_request_details(self, request_data: Dict[str, Any]):
        """Log request details for debugging."""
        # Extract request details for structured logging
        request_details = {}
        for key, value in request_data.items():
            if key == "api_key":
                request_details[key] = "*" * 8
            elif key == "messages" and isinstance(value, list):
                request_details[key] = f"[{len(value)} messages]"
            elif key == "tools" and isinstance(value, list):
                request_details[key] = f"[{len(value)} tools]"
                # Log tool names for debugging
                tool_names = []
                for tool in value:
                    if isinstance(tool, dict) and 'function' in tool:
                        func_name = tool['function'].get('name', 'unknown')
                        tool_names.append(func_name)
                request_details["tool_names"] = tool_names
            elif key == "stream":
                request_details[key] = f"{value} (streaming mode)"
            else:
                request_details[key] = value
        
        logger.debug("LiteLLM request details", **request_details)
    
    def _prepare_request_config(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare request configuration - simplified for OpenRouter compatibility."""
        # Use minimal configuration like the working simple server
        request_config = {
            **request_data,
            # Only add essential parameters, remove problematic LiteLLM configs
            # "drop_params": True,  # ← Removed - this might cause OpenRouter issues
            # "timeout": ...,       # ← Removed - let LiteLLM use defaults  
            # "num_retries": ...,   # ← Removed - let LiteLLM use defaults
            # "rpm": ...,           # ← Removed - not needed for OpenRouter
            # "tpm": ...,           # ← Removed - not needed for OpenRouter
        }
        
        # Only add basic timeout to prevent infinite hangs
        request_config["timeout"] = 300  # 5 minutes max
        
        # Remove None values and keep it clean
        request_config = {k: v for k, v in request_config.items() if v is not None}
        
        logger.debug("Prepared simplified request config for OpenRouter compatibility",
                    keys=list(request_config.keys()),
                    model=request_config.get("model"))
        
        return request_config
    
    def _handle_litellm_exception(self, e: Exception, request_data: Dict[str, Any], processing_time: float) -> None:
        """
        Enhanced exception handling using LiteLLM's exception mapping.
        
        Args:
            e: The exception to handle
            request_data: Original request data
            processing_time: Request processing time
        """
        # Extract error details
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "model": request_data.get('model', 'unknown'),
            "processing_time": processing_time,
            "llm_provider": getattr(e, 'llm_provider', 'unknown'),
            "status_code": getattr(e, 'status_code', None)
        }
        
        # Log different error types with appropriate severity
        if isinstance(e, ContextWindowExceededError):
            logger.warning("Context window exceeded - consider fallback", **error_details)
        elif isinstance(e, ContentPolicyViolationError):
            logger.warning("Content policy violation - review content", **error_details)
        elif isinstance(e, RateLimitError):
            logger.warning("Rate limit exceeded - implement backoff", **error_details)
        elif isinstance(e, BudgetExceededError):
            logger.error("Budget exceeded - check cost limits", **error_details)
        elif isinstance(e, AuthenticationError):
            logger.error("Authentication failed - check API keys", **error_details)
        elif isinstance(e, NotFoundError):
            logger.error("Model not found - check model name", **error_details)
        elif isinstance(e, Timeout):
            logger.warning("Request timeout - consider retry", **error_details)
        elif isinstance(e, ServiceUnavailableError):
            logger.warning("Service unavailable - try again later", **error_details)
        else:
            logger.error("Unexpected LiteLLM error", **error_details)
        
        # Check if error should be retried
        if hasattr(e, 'status_code'):
            should_retry = litellm._should_retry(e.status_code)
            logger.info("Retry recommendation", should_retry=should_retry, status_code=e.status_code)
        
        # Log comprehensive error information to disk
        error_context = {
            "service": "HTTPClient",
            "method": "make_litellm_request",
            "processing_time": processing_time,
            "error_classification": error_details,
            "retry_eligible": should_retry if hasattr(e, 'status_code') else False
        }
        
        log_error(
            error=e,
            correlation_id=request_data.get("request_id", "unknown"),
            request_data=request_data,
            context=error_context
        )
    
    def _add_reasoning_parameters(self, request_config: Dict[str, Any], source_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add reasoning content parameters to LiteLLM request if supported.
        
        Args:
            request_config: Base request configuration
            source_request: Original request with potential reasoning parameters
            
        Returns:
            Enhanced request configuration
        """
        try:
            # Check if reasoning is requested
            reasoning_effort = source_request.get("reasoning_effort")
            thinking_param = source_request.get("thinking")
            
            if reasoning_effort:
                # Validate reasoning effort
                valid_efforts = ["low", "medium", "high"]
                if reasoning_effort in valid_efforts:
                    request_config["reasoning_effort"] = reasoning_effort
                    logger.debug("Added reasoning effort", effort=reasoning_effort)
                else:
                    logger.warning("Invalid reasoning effort", effort=reasoning_effort, valid=valid_efforts)
            
            if thinking_param:
                # Add thinking parameter for Anthropic models
                request_config["thinking"] = thinking_param
                logger.debug("Added thinking parameter", thinking=thinking_param)
            
            # Add drop_params for provider switching
            if source_request.get("drop_params"):
                request_config["drop_params"] = True
                logger.debug("Enabled parameter dropping for provider switching")
            
            return request_config
            
        except Exception as e:
            logger.error("Failed to add reasoning parameters", error=str(e))
            return request_config
    
    async def _execute_litellm_request(self, request_config: Dict[str, Any]) -> Any:
        """Execute LiteLLM request with error handling and timeout."""
        try:
            logger.debug("Executing LiteLLM request", 
                        model=request_config.get("model"),
                        has_tools=bool(request_config.get("tools")),
                        request_id=request_config.get("request_id", "unknown"))
            
            response = await acompletion(**request_config)
            
            logger.debug("LiteLLM request successful",
                        response_type=str(type(response)),
                        model=getattr(response, 'model', 'unknown') if hasattr(response, 'model') else 'unknown')
            
            return response
            
        except Exception as e:
            # Check if this is an OpenRouter tool response parsing error
            if self._is_openrouter_tool_parsing_error(e, request_config):
                logger.warning("OpenRouter tool response parsing failed, retrying without tools",
                             error=str(e),
                             model=request_config.get("model"),
                             original_tool_count=len(request_config.get("tools", [])))
                
                # Retry without tools to get a basic response
                retry_config = request_config.copy()
                retry_config.pop("tools", None)
                retry_config.pop("tool_choice", None)
                
                try:
                    response = await acompletion(**retry_config)
                    logger.info("OpenRouter retry without tools successful",
                              model=request_config.get("model"))
                    return response
                    
                except Exception as retry_error:
                    logger.error("OpenRouter retry without tools failed",
                               retry_error=str(retry_error),
                               original_error=str(e))
                    raise retry_error
            
            # For other errors, re-raise as-is
            raise e
    
    def _is_openrouter_tool_parsing_error(self, error: Exception, request_config: Dict[str, Any]) -> bool:
        """Check if this is an OpenRouter tool response parsing error."""
        error_str = str(error).lower()
        
        # Check for specific error patterns that indicate OpenRouter tool parsing issues
        parsing_error_indicators = [
            "openrouterexception - provider returned error",
            "convert_to_model_response_object",
            "provider returned error"
        ]
        
        # Check if request has tools and model is OpenRouter
        has_tools = bool(request_config.get("tools"))
        is_openrouter = request_config.get("model", "").startswith("openrouter/")
        
        # Check for parsing error patterns
        is_parsing_error = any(indicator in error_str for indicator in parsing_error_indicators)
        
        return has_tools and is_openrouter and is_parsing_error

    async def test_model_connection(self, model: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Test connection to a specific model using LiteLLM's health check capabilities.
        
        Args:
            model: Model name to test
            provider: Optional provider specification
            
        Returns:
            Health check result
        """
        try:
            # Prepare test request similar to LiteLLM's test_connection endpoint
            test_config = {
                "model": model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1,
                "timeout": 10
            }
            
            if provider:
                test_config["custom_llm_provider"] = provider
                
            logger.info("Testing model connection", model=model, provider=provider)
            
            # Test the connection with a minimal request
            response = await self._execute_litellm_request(test_config)
            
            return {
                "model": model,
                "provider": provider,
                "status": "healthy",
                "response_time": getattr(response, '_response_time', None),
                "model_info": {
                    "model": getattr(response, 'model', model),
                    "usage": getattr(response, 'usage', {})
                }
            }
            
        except Exception as e:
            logger.error("Model connection test failed", model=model, provider=provider, error=str(e))
            return {
                "model": model,
                "provider": provider,
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def get_litellm_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status including LiteLLM-specific metrics.
        
        Returns:
            Health status information
        """
        try:
            health_info = {
                "service": "HTTPClient",
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "litellm_config": {
                    "timeout": litellm.request_timeout,
                    "retries": getattr(litellm, 'num_retries', 0),
                    "verbose": litellm.set_verbose,
                    "cache_enabled": hasattr(litellm, 'cache') and litellm.cache is not None
                }
            }
            
            # Add cache status if available
            if hasattr(litellm, 'cache') and litellm.cache:
                try:
                    # Test cache connectivity
                    cache_status = {
                        "type": getattr(litellm.cache, 'type', 'unknown'),
                        "status": "connected"
                    }
                    health_info["cache"] = cache_status
                except Exception as e:
                    health_info["cache"] = {"status": "error", "error": str(e)}
            
            # Test basic LiteLLM functionality
            try:
                # This is similar to what LiteLLM's health endpoints do
                await self.test_model_connection(config.small_model)
                health_info["model_connectivity"] = "healthy"
            except Exception as e:
                health_info["model_connectivity"] = "degraded"
                health_info["model_error"] = str(e)
            
            return health_info
            
        except Exception as e:
            logger.error("Health status check failed", error=str(e))
            return {
                "service": "HTTPClient",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def check_reasoning_support(self, model: str) -> Dict[str, Any]:
        """
        Check if a model supports reasoning content using LiteLLM's supports_reasoning function.
        
        Args:
            model: Model name to check
            
        Returns:
            Reasoning support information
        """
        try:
            # Use LiteLLM's built-in reasoning support detection
            supports_reasoning = litellm.supports_reasoning(model=model)
            
            # Determine supported reasoning efforts based on provider
            supported_efforts = []
            provider = None
            
            if "anthropic/" in model or "claude" in model:
                provider = "anthropic"
                supported_efforts = ["low", "medium", "high"]
            elif "deepseek/" in model:
                provider = "deepseek"
                supported_efforts = ["low", "medium", "high"]
            elif "openrouter/" in model:
                provider = "openrouter"
                supported_efforts = ["low", "medium", "high"]
            
            return {
                "model": model,
                "supports_reasoning": supports_reasoning,
                "supported_efforts": supported_efforts,
                "provider": provider,
                "reasoning_available": supports_reasoning and bool(supported_efforts)
            }
            
        except Exception as e:
            logger.warning("Failed to check reasoning support", model=model, error=str(e))
            return {
                "model": model,
                "supports_reasoning": False,
                "supported_efforts": [],
                "provider": None,
                "reasoning_available": False,
                "error": str(e)
            }


class ProxyConfigurationService(BaseService):
    """Service for managing proxy configuration and bypass rules."""
    
    def __init__(self):
        """Initialize proxy configuration service."""
        super().__init__("ProxyConfiguration")
        self.bypass_rules = self._load_bypass_rules()
    
    def _load_bypass_rules(self) -> Dict[str, Any]:
        """Load proxy bypass rules from configuration."""
        return {
            "domains": [
                "openrouter.ai",
                "api.openrouter.ai",
                "*.openrouter.ai"
            ],
            "providers": [
                "openrouter/",
                "anthropic/",
                "openai/"
            ],
            "patterns": [
                "*openrouter*",
                "*anthropic*"
            ]
        }
    
    def should_bypass_proxy(self, url: str = None, model: str = None) -> bool:
        """
        Determine if proxy should be bypassed for a given URL or model.
        
        Args:
            url: The target URL
            model: The model name
            
        Returns:
            True if proxy should be bypassed
        """
        if url:
            # Check domain-based rules
            for domain in self.bypass_rules["domains"]:
                if domain.replace("*", "") in url:
                    return True
        
        if model:
            # Check provider-based rules
            for provider in self.bypass_rules["providers"]:
                if model.startswith(provider):
                    return True
            
            # Check pattern-based rules
            for pattern in self.bypass_rules["patterns"]:
                pattern_clean = pattern.replace("*", "")
                if pattern_clean in model.lower():
                    return True
        
        return False
    
    def get_proxy_config(self, bypass: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get proxy configuration for HTTP requests.
        
        Args:
            bypass: Whether to bypass proxy
            
        Returns:
            Proxy configuration or None
        """
        if bypass:
            return None
        
        # Get proxy settings from environment
        proxy_config = {}
        
        if os.environ.get('HTTP_PROXY'):
            proxy_config['http'] = os.environ['HTTP_PROXY']
        
        if os.environ.get('HTTPS_PROXY'):
            proxy_config['https'] = os.environ['HTTPS_PROXY']
        
        return proxy_config if proxy_config else None