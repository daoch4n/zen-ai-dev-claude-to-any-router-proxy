"""
Logging middleware for OpenRouter Anthropic Server.
Provides comprehensive request/response logging with structured output.
"""

import time
import uuid
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging_config import get_logger
from src.utils.debug import debug_logger

logger = get_logger(__name__)
from src.utils.config import config


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all HTTP requests and responses.
    
    Features:
    - Request/response timing
    - Structured logging with request IDs
    - Debug logging for development
    - Error tracking and correlation
    """
    
    def __init__(self, app, log_requests: bool = True, log_responses: bool = True):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and response with logging."""
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Add request ID to request state for use in other components
        request.state.request_id = request_id
        
        # Log incoming request
        if self.log_requests:
            await self._log_request(request, request_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log response
            if self.log_responses:
                await self._log_response(request, response, request_id, processing_time)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Log error
            logger.error("❌ Request failed in middleware",
                        request_id=request_id,
                        method=request.method,
                        path=request.url.path,
                        processing_time_s=round(processing_time, 3),
                        error_type=type(e).__name__,
                        error_message=str(e))
            
            # Log to debug logger
            debug_logger.log_request_response(
                request_id=request_id,
                request_data={
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "error": str(e)
                },
                response_data=None,
                processing_time=processing_time,
                success=False,
                error=str(e)
            )
            
            raise
    
    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request details."""
        try:
            # Get request body for POST requests (if not too large)
            body = None
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body_bytes = await request.body()
                    if len(body_bytes) < 10000:  # Only log if less than 10KB
                        body = body_bytes.decode('utf-8')
                        # Try to parse as JSON for better formatting
                        try:
                            body = json.loads(body)
                        except json.JSONDecodeError:
                            pass
                except Exception:
                    body = "<body_read_error>"
            
            # Log structured request info
            logger.info("📨 Incoming request",
                       request_id=request_id,
                       method=request.method,
                       path=request.url.path,
                       client_host=request.client.host if request.client else 'unknown')
            
            # Debug logging with full details
            if config.debug_enabled:
                debug_data = {
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "query_params": dict(request.query_params),
                    "path_params": dict(request.path_params),
                    "client": {
                        "host": request.client.host if request.client else None,
                        "port": request.client.port if request.client else None
                    }
                }
                
                if body is not None:
                    debug_data["body"] = body
                
                debug_logger.log_request_response(
                    request_id=request_id,
                    request_data=debug_data,
                    response_data=None,
                    processing_time=0,
                    success=True
                )
                
        except Exception as e:
            logger.warning("⚠️ Failed to log request details",
                          request_id=request_id,
                          error_type=type(e).__name__,
                          error_message=str(e))
    
    async def _log_response(self, request: Request, response: Response, request_id: str, processing_time: float):
        """Log response details."""
        try:
            # Determine if request was successful
            success = 200 <= response.status_code < 400
            status_emoji = "✅" if success else "❌"
            
            # Log basic response info
            logger.info(f"{status_emoji} Response sent",
                       request_id=request_id,
                       status_code=response.status_code,
                       processing_time_s=round(processing_time, 3),
                       success=success)
            
            # Debug logging with response details
            if config.debug_enabled:
                response_data = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "processing_time": processing_time
                }
                
                # Try to capture response body for non-streaming responses
                if not isinstance(response, StreamingResponse):
                    try:
                        # This is tricky with FastAPI - we can't easily read the response body
                        # without affecting the response. For now, we'll just log metadata.
                        response_data["type"] = type(response).__name__
                    except Exception:
                        pass
                
                debug_logger.log_request_response(
                    request_id=request_id,
                    request_data=None,
                    response_data=response_data,
                    processing_time=processing_time,
                    success=success
                )
                
        except Exception as e:
            logger.warning("⚠️ Failed to log response details",
                          request_id=request_id,
                          error_type=type(e).__name__,
                          error_message=str(e))