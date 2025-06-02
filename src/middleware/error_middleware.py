"""
Error handling middleware for OpenRouter Anthropic Server.
Provides comprehensive error handling with structured responses.
"""

import traceback
import json
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError

from src.core.logging_config import get_logger
from src.utils.errors import (
    OpenRouterProxyError, ToolValidationError, ConversationFlowError,
    ModelMappingError, SchemaValidationError, InstructorError
)
from src.utils.config import config

logger = get_logger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling all application errors with structured responses.
    
    Features:
    - Structured error responses in Anthropic format
    - Error logging with context
    - Development vs production error details
    - Error correlation with request IDs
    """
    
    def __init__(self, app, include_debug_info: bool = None):
        super().__init__(app)
        # Use config debug setting if not explicitly provided
        self.include_debug_info = include_debug_info if include_debug_info is not None else config.debug_enabled
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with comprehensive error handling."""
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            # Handle FastAPI HTTP exceptions
            return await self._handle_http_exception(request, e)
            
        except ValidationError as e:
            # Handle Pydantic validation errors
            return await self._handle_validation_error(request, e)
            
        except OpenRouterProxyError as e:
            # Handle our custom application errors
            return await self._handle_proxy_error(request, e)
            
        except Exception as e:
            # Handle unexpected errors
            return await self._handle_unexpected_error(request, e)
    
    async def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Handle FastAPI HTTP exceptions."""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.warning("⚠️ HTTP exception handled",
                      request_id=request_id,
                      status_code=exc.status_code,
                      detail=str(exc.detail),
                      headers=exc.headers)
        
        # Structure error response in Anthropic format
        error_response = {
            "type": "error",
            "error": {
                "type": self._get_anthropic_error_type(exc.status_code),
                "message": str(exc.detail) if isinstance(exc.detail, str) else json.dumps(exc.detail)
            }
        }
        
        # Add debug info if enabled
        if self.include_debug_info:
            error_response["debug"] = {
                "request_id": request_id,
                "status_code": exc.status_code,
                "headers": exc.headers
            }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers=exc.headers
        )
    
    async def _handle_validation_error(self, request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors."""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.error("❌ Request validation failed",
                    request_id=request_id,
                    error_count=len(exc.errors()),
                    validation_errors=exc.errors())
        
        # Format validation errors for user
        formatted_errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            formatted_errors.append(f"{field_path}: {error['msg']}")
        
        error_response = {
            "type": "error",
            "error": {
                "type": "invalid_request_error",
                "message": f"Request validation failed: {'; '.join(formatted_errors)}"
            }
        }
        
        # Add debug info if enabled
        if self.include_debug_info:
            error_response["debug"] = {
                "request_id": request_id,
                "validation_errors": exc.errors(),
                "error_count": len(exc.errors())
            }
        
        return JSONResponse(
            status_code=400,
            content=error_response
        )
    
    async def _handle_proxy_error(self, request: Request, exc: OpenRouterProxyError) -> JSONResponse:
        """Handle custom proxy errors."""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Map custom errors to appropriate HTTP status codes and types
        error_mapping = {
            ToolValidationError: (400, "invalid_request_error"),
            ConversationFlowError: (400, "invalid_request_error"),
            ModelMappingError: (400, "invalid_request_error"),
            SchemaValidationError: (400, "invalid_request_error"),
            InstructorError: (500, "api_error")
        }
        
        status_code, error_type = error_mapping.get(type(exc), (500, "api_error"))
        
        logger.error("❌ Proxy error handled",
                    request_id=request_id,
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                    status_code=status_code,
                    anthropic_error_type=error_type)
        
        error_response = {
            "type": "error",
            "error": {
                "type": error_type,
                "message": str(exc)
            }
        }
        
        # Add debug info if enabled
        if self.include_debug_info:
            error_response["debug"] = {
                "request_id": request_id,
                "error_class": type(exc).__name__,
                "traceback": traceback.format_exc()
            }
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )
    
    async def _handle_unexpected_error(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected errors."""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.error("🔥 Unexpected error occurred",
                    request_id=request_id,
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                    traceback=traceback.format_exc())
        
        # Generic error response
        error_response = {
            "type": "error",
            "error": {
                "type": "api_error",
                "message": "An unexpected error occurred. Please try again later."
            }
        }
        
        # Add debug info if enabled (be careful not to leak sensitive info)
        if self.include_debug_info:
            error_response["debug"] = {
                "request_id": request_id,
                "error_class": type(exc).__name__,
                "error_message": str(exc),
                "traceback": traceback.format_exc()
            }
        else:
            # In production, just include the request ID for correlation
            error_response["debug"] = {
                "request_id": request_id
            }
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )
    
    def _get_anthropic_error_type(self, status_code: int) -> str:
        """Map HTTP status codes to Anthropic error types."""
        mapping = {
            400: "invalid_request_error",
            401: "authentication_error",
            403: "permission_error",
            404: "not_found_error",
            422: "invalid_request_error",
            429: "rate_limit_error",
            500: "api_error",
            502: "api_error",
            503: "overloaded_error",
            529: "overloaded_error"
        }
        return mapping.get(status_code, "api_error")