"""
Routers package for OpenRouter Anthropic Server.

This package contains FastAPI routers for:
- Messages endpoint (/v1/messages)
- Token counting endpoint (/v1/messages/count_tokens)
- Health check endpoints
- Debug endpoints (/debug/*)
- MCP server management endpoints (/v1/mcp/*)
"""

from .messages import router as messages_router
from .tokens import router as tokens_router
from .health import router as health_router
from .debug import router as debug_router
from .mcp import router as mcp_router

__all__ = [
    "messages_router",
    "tokens_router",
    "health_router",
    "debug_router",
    "mcp_router"
]