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
            
            # Configure proxy settings if needed
            self._configure_proxy_settings()
            
            self.log_operation("litellm_configuration", success=True, 
                             timeout=config.request_timeout, 
                             debug_enabled=config.debug_enabled)
            
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
            error_msg = f"LiteLLM API call failed: {e}"
            
            # Log comprehensive error information to disk
            error_context = {
                "service": "HTTPClient",
                "method": "make_litellm_request",
                "processing_time": processing_time,
                "model": request_data.get('model', 'unknown'),
                "request_id": request_id,
                "api_base": request_data.get('api_base', 'unknown'),
                "stream": request_data.get('stream', False)
            }
            
            # Extract response details if available
            response_data = None
            if hasattr(e, 'response') and e.response:
                try:
                    response_data = {
                        "status_code": getattr(e.response, 'status_code', None),
                        "headers": dict(getattr(e.response, 'headers', {})),
                        "body": getattr(e.response, 'text', None) or str(e.response)
                    }
                except Exception:
                    response_data = {"error": "Failed to extract response details"}
            
            # Log to disk with full details
            log_error(
                error=e,
                correlation_id=request_id,
                request_data=request_data,
                response_data=response_data,
                context=error_context
            )
            
            self.log_operation("litellm_api_call", success=False,
                             request_id=request_id,
                             processing_time=processing_time,
                             error=error_msg)
            
            logger.error("LiteLLM API call failed",
                        error=str(e),
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
        """Prepare request configuration with proper HTTP client settings."""
        config_data = request_data.copy()
        
        # Add timeout configuration
        config_data['timeout'] = config.request_timeout
        
        # Add custom headers if needed
        if 'headers' not in config_data:
            config_data['headers'] = {}
        
        # Add user agent
        config_data['headers']['User-Agent'] = 'OpenRouter-Anthropic-Server/2.0'
        
        # Configure proxy bypass for OpenRouter
        if self._should_bypass_proxy(config_data.get('model', '')):
            config_data['proxy'] = None  # Explicitly disable proxy for this request
        
        return config_data
    
    def _should_bypass_proxy(self, model: str) -> bool:
        """Determine if proxy should be bypassed for this model/provider."""
        # OpenRouter models should bypass proxy (must start with openrouter/)
        if model.startswith('openrouter/'):
            return True
        
        # Add other providers that need proxy bypass
        bypass_providers = ['anthropic/', 'openai/', 'google/']
        return any(model.startswith(provider) for provider in bypass_providers)
    
    async def _execute_litellm_request(self, request_config: Dict[str, Any]) -> Any:
        """Execute the LiteLLM request with proper error handling."""
        try:
            # Use LiteLLM's async completion with our configuration
            response = await acompletion(**request_config)
            return response
            
        except Exception as e:
            # Enhanced error handling for common issues
            if "proxy" in str(e).lower():
                logger.warning("Proxy-related error detected, retrying without proxy",
                             error=str(e),
                             retry_attempt=True)
                # Retry without proxy
                retry_config = request_config.copy()
                retry_config['proxy'] = None
                return await acompletion(**retry_config)
            else:
                raise


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