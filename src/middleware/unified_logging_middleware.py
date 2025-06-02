"""
Unified logging middleware using Structlog and Context Manager.
Replaces the legacy logging middleware with unified context-aware logging.
"""

import time
import uuid
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging_config import get_logger
from src.services.context_manager import ContextManager
from src.utils.config import config


class UnifiedLoggingMiddleware(BaseHTTPMiddleware):
    """
    Unified logging middleware with automatic context management.
    
    Features:
    - Request/response timing with structured logging
    - Automatic context creation and propagation
    - Context cleanup after request completion
    - Enhanced debugging with full context chain
    - Thread-safe context management via contextvars
    """
    
    def __init__(self, app, log_requests: bool = True, log_responses: bool = True):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.context_manager = ContextManager()
        self.logger = get_logger("middleware.logging")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and response with unified logging and context management."""
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Create request context - this automatically binds to contextvars
        request_context = self.context_manager.create_request_context(
            endpoint=str(request.url.path),
            method=request.method,
            user_agent=request.headers.get("user-agent"),
            request_id=request_id
        )
        
        # Add request ID to request state for backwards compatibility
        request.state.request_id = request_id
        request.state.request_context = request_context
        
        # Log incoming request with automatic context
        if self.log_requests:
            await self._log_request(request, request_context)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log response with context
            if self.log_responses:
                await self._log_response(request, response, processing_time)
            
            # Add request ID and timing headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"
            
            self.logger.info("Request completed successfully",
                           status_code=response.status_code,
                           processing_time=round(processing_time, 4))
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Log error with full context
            self.logger.error("Request failed",
                            error=str(e),
                            error_type=type(e).__name__,
                            processing_time=round(processing_time, 4))
            
            raise
            
        finally:
            # Always cleanup context at end of request
            self.context_manager.cleanup_context()
    
    async def _log_request(self, request: Request, request_context):
        """Log incoming request with unified context."""
        try:
            # Get request body for logging (if appropriate)
            body_data = None
            if request.method in ["POST", "PUT", "PATCH"]:
                body_data = await self._get_request_body(request)
            
            # Log structured request with automatic context enrichment
            self.logger.info("Request received",
                           path=request.url.path,
                           method=request.method,
                           query_params=dict(request.query_params),
                           client_host=request.client.host if request.client else "unknown",
                           content_length=request.headers.get("content-length"),
                           content_type=request.headers.get("content-type"))
            
            # Enhanced debug logging if enabled
            if config.debug_enabled:
                self.logger.debug("Request details",
                                 headers=dict(request.headers),
                                 path_params=dict(request.path_params),
                                 client_port=request.client.port if request.client else None,
                                 body_preview=body_data[:500] if isinstance(body_data, str) else str(type(body_data).__name__))
                
        except Exception as e:
            self.logger.warning("Failed to log request details", error=str(e))
    
    async def _log_response(self, request: Request, response: Response, processing_time: float):
        """Log response with unified context."""
        try:
            # Determine success status
            success = 200 <= response.status_code < 400
            
            # Log response with context (request context automatically included)
            log_method = self.logger.info if success else self.logger.warning
            log_method("Response prepared",
                      status_code=response.status_code,
                      success=success,
                      processing_time=round(processing_time, 4),
                      response_type=type(response).__name__)
            
            # Enhanced debug logging
            if config.debug_enabled:
                response_info = {
                    "headers": dict(response.headers),
                    "is_streaming": isinstance(response, StreamingResponse)
                }
                
                # Add media type if available
                if hasattr(response, 'media_type'):
                    response_info["media_type"] = response.media_type
                
                self.logger.debug("Response details", **response_info)
                
        except Exception as e:
            self.logger.warning("Failed to log response details", error=str(e))
    
    async def _get_request_body(self, request: Request):
        """Safely get request body for logging."""
        try:
            body_bytes = await request.body()
            
            # Only log reasonable sized bodies
            if len(body_bytes) > 10000:  # 10KB limit
                return f"<large_body_size_{len(body_bytes)}_bytes>"
            
            if len(body_bytes) == 0:
                return None
            
            # Try to decode and parse
            body_str = body_bytes.decode('utf-8')
            
            # Try to parse as JSON for structured logging
            try:
                body_json = json.loads(body_str)
                # For messages requests, we might want to limit message content
                if isinstance(body_json, dict) and "messages" in body_json:
                    # Create a copy with truncated message content for logging
                    log_body = body_json.copy()
                    if len(str(log_body)) > 1000:  # Truncate large message bodies
                        log_body["messages"] = f"<{len(body_json.get('messages', []))} messages>"
                    return log_body
                return body_json
            except json.JSONDecodeError:
                # Return string if not valid JSON
                return body_str[:500] + "..." if len(body_str) > 500 else body_str
                
        except Exception as e:
            return f"<body_read_error: {str(e)}>"