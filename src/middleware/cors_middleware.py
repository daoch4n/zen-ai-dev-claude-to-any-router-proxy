"""
CORS middleware for OpenRouter Anthropic Server.
Handles Cross-Origin Resource Sharing with configurable policies.
"""

from typing import List, Optional
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse

from src.core.logging_config import get_logger
from src.utils.config import config

logger = get_logger(__name__)


class CORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware with enhanced logging and configuration.
    
    Features:
    - Configurable allowed origins, methods, and headers
    - Preflight request handling
    - Request logging for CORS debugging
    - Environment-aware CORS policies
    """
    
    def __init__(
        self,
        app,
        allow_origins: Optional[List[str]] = None,
        allow_methods: Optional[List[str]] = None,
        allow_headers: Optional[List[str]] = None,
        allow_credentials: bool = False,
        expose_headers: Optional[List[str]] = None,
        max_age: int = 600
    ):
        super().__init__(app)
        
        # Set defaults based on environment
        if allow_origins is None:
            if config.environment in ["development", "testing"]:
                allow_origins = ["*"]
            else:
                allow_origins = ["https://claude.ai", "https://console.anthropic.com"]
        
        if allow_methods is None:
            allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
        
        if allow_headers is None:
            allow_headers = [
                "Accept",
                "Accept-Language",
                "Content-Language",
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "X-Request-ID",
                "anthropic-version",
                "anthropic-beta"
            ]
        
        if expose_headers is None:
            expose_headers = ["X-Request-ID", "X-Processing-Time"]
        
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers
        self.max_age = max_age
        
        logger.info("🌐 CORS middleware configured",
                   origins_count=len(allow_origins),
                   methods_count=len(allow_methods),
                   allow_credentials=allow_credentials,
                   max_age=max_age)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Handle CORS for all requests."""
        
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            return await self._handle_preflight(request, origin)
        
        # Process normal request
        response = await call_next(request)
        
        # Add CORS headers to response
        self._add_cors_headers(response, origin)
        
        return response
    
    async def _handle_preflight(self, request: Request, origin: Optional[str]) -> Response:
        """Handle CORS preflight requests."""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.debug("🔍 CORS preflight request received",
                    request_id=request_id,
                    origin=origin)
        
        # Check if origin is allowed
        if not self._is_origin_allowed(origin):
            logger.warning("⚠️ CORS preflight rejected - origin not allowed",
                          origin=origin,
                          request_id=request_id)
            return PlainTextResponse(
                "CORS preflight rejected",
                status_code=403
            )
        
        # Check requested method
        requested_method = request.headers.get("access-control-request-method")
        if requested_method and requested_method not in self.allow_methods:
            logger.warning("⚠️ CORS preflight rejected - method not allowed",
                          requested_method=requested_method,
                          allowed_methods=self.allow_methods,
                          request_id=request_id)
            return PlainTextResponse(
                "Method not allowed",
                status_code=405
            )
        
        # Check requested headers
        requested_headers = request.headers.get("access-control-request-headers")
        if requested_headers:
            requested_header_list = [h.strip().lower() for h in requested_headers.split(",")]
            allowed_header_list = [h.lower() for h in self.allow_headers]
            
            for header in requested_header_list:
                if header not in allowed_header_list:
                    logger.warning("⚠️ CORS preflight rejected - header not allowed",
                                  requested_header=header,
                                  allowed_headers=self.allow_headers,
                                  request_id=request_id)
                    return PlainTextResponse(
                        "Header not allowed",
                        status_code=403
                    )
        
        # Create preflight response
        response = PlainTextResponse("OK", status_code=200)
        self._add_cors_headers(response, origin, is_preflight=True)
        
        logger.debug("✅ CORS preflight approved",
                    request_id=request_id,
                    origin=origin)
        return response
    
    def _add_cors_headers(self, response: Response, origin: Optional[str], is_preflight: bool = False):
        """Add CORS headers to response."""
        
        # Add origin header if allowed
        if self._is_origin_allowed(origin):
            if "*" in self.allow_origins:
                response.headers["Access-Control-Allow-Origin"] = "*"
            elif origin:  # Only set if origin is not None
                response.headers["Access-Control-Allow-Origin"] = origin
        elif not origin:  # For requests without origin (same-origin, testing)
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        # Add credentials header if enabled
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        # Add exposed headers
        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        # Add preflight-specific headers
        if is_preflight:
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
            response.headers["Access-Control-Max-Age"] = str(self.max_age)
        
        # Add Vary header for proper caching
        vary_headers = []
        if "Vary" in response.headers:
            vary_headers = [h.strip() for h in response.headers["Vary"].split(",")]
        
        if "Origin" not in vary_headers:
            vary_headers.append("Origin")
        
        if is_preflight and "Access-Control-Request-Method" not in vary_headers:
            vary_headers.append("Access-Control-Request-Method")
            vary_headers.append("Access-Control-Request-Headers")
        
        response.headers["Vary"] = ", ".join(vary_headers)
    
    def _is_origin_allowed(self, origin: Optional[str]) -> bool:
        """Check if origin is allowed."""
        if not origin:
            return True  # Allow requests without origin (e.g., same-origin, mobile apps)
        
        if "*" in self.allow_origins:
            return True
        
        return origin in self.allow_origins