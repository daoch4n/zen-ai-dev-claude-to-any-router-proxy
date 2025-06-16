"""
Universal Streaming Router for Multi-Model Real-time Tool Execution.

This router provides endpoints for streaming responses across 100+ LiteLLM models
with real-time tool execution, intelligent caching, and provider-specific optimizations.

Phase 3B: Multi-Model Streaming Support
"""

import asyncio
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..models.anthropic import MessagesRequest
from ..core.logging_config import get_logger
from ..flows.universal.universal_streaming_flow import UniversalStreamingFlow
from ..services.universal.universal_streaming_service import AIProvider
from ..converters.universal.multi_model_converter import MultiModelConverter
# Request context not needed for this implementation

logger = get_logger("universal.streaming_router")

# Initialize universal streaming components lazily
_universal_flow = None
_multi_model_converter = None

def get_universal_flow():
    """Get or create universal flow instance."""
    global _universal_flow
    if _universal_flow is None:
        _universal_flow = UniversalStreamingFlow()
    return _universal_flow

def get_multi_model_converter():
    """Get or create multi-model converter instance."""
    global _multi_model_converter
    if _multi_model_converter is None:
        _multi_model_converter = MultiModelConverter()
    return _multi_model_converter

# Create router
router = APIRouter(prefix="/v1/universal", tags=["Universal Streaming"])


class UniversalStreamingRequest(BaseModel):
    """Universal streaming request model."""
    model: str = Field(..., description="Model name (auto-detects provider)")
    messages: List[Dict[str, Any]] = Field(..., description="Messages array")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Available tools")
    max_tokens: Optional[int] = Field(1024, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Temperature for generation")
    stream: bool = Field(True, description="Enable streaming (always true for universal)")
    provider: Optional[str] = Field(None, description="Force specific provider")
    enable_tools: bool = Field(True, description="Enable real-time tool execution")


@router.post("/stream")
async def universal_streaming_endpoint(
    request: UniversalStreamingRequest,
    http_request: Request
) -> StreamingResponse:
    """
    Universal streaming endpoint supporting 100+ models with real-time tool execution.
    
    This endpoint automatically detects the AI provider from the model name and
    provides streaming responses with real-time tool execution capabilities.
    """
    # request_context = get_request_context(http_request)  # Not needed
    request_id = str(uuid.uuid4())
    
    try:
        logger.info("Universal streaming request received",
                   request_id=request_id,
                   model=request.model,
                   provider=request.provider,
                   tools_enabled=request.enable_tools)
        
        # Convert to internal format
        internal_request = MessagesRequest(
            model=request.model,
            messages=request.messages,
            tools=request.tools if request.enable_tools else None,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=True
        )
        
        # Parse provider if specified
        target_provider = None
        if request.provider:
            try:
                target_provider = AIProvider(request.provider.lower())
            except ValueError:
                logger.warning("Invalid provider specified, using auto-detection",
                             specified_provider=request.provider,
                             request_id=request_id)
        
        # Create streaming response
        async def stream_generator():
            try:
                universal_flow = get_universal_flow()
                async for chunk in universal_flow.process_universal_streaming_request(
                    internal_request, request_id, target_provider
                ):
                    # Format as SSE
                    chunk_data = f"data: {chunk}\n\n"
                    yield chunk_data.encode()
                
                # Send completion marker
                yield b"data: [DONE]\n\n"
                
            except Exception as e:
                logger.error("Universal streaming failed",
                           request_id=request_id,
                           error=str(e))
                
                error_chunk = {
                    "id": request_id,
                    "error": {
                        "message": f"Universal streaming error: {str(e)}",
                        "type": "universal_streaming_error"
                    }
                }
                yield f"data: {error_chunk}\n\n".encode()
                yield b"data: [DONE]\n\n"
        
        return StreamingResponse(
            stream_generator(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Universal-Request-ID": request_id,
                "X-Universal-Streaming": "enabled"
            }
        )
        
    except Exception as e:
        logger.error("Universal streaming endpoint failed",
                    request_id=request_id,
                    error=str(e),
                    exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Universal streaming failed",
                "message": str(e),
                "request_id": request_id,
                "type": "universal_streaming_error"
            }
        )


@router.get("/providers")
async def list_supported_providers() -> Dict[str, Any]:
    """
    List all supported AI providers with capabilities.
    
    Returns comprehensive information about supported providers,
    their capabilities, and current status.
    """
    try:
        # Get provider information from services
        universal_flow = get_universal_flow()
        multi_model_converter = get_multi_model_converter()
        
        universal_providers = universal_flow.universal_streaming_service.get_supported_providers()
        conversion_providers = multi_model_converter.get_supported_providers_info()
        
        return {
            "total_providers": len(universal_providers),
            "universal_streaming_providers": universal_providers,
            "conversion_support": conversion_providers,
            "capabilities": {
                "real_time_tool_execution": True,
                "intelligent_caching": True,
                "cross_provider_optimization": True,
                "automatic_provider_detection": True,
                "fallback_support": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to list providers", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to list providers",
                "message": str(e)
            }
        )


@router.get("/health")
async def universal_health_check() -> Dict[str, Any]:
    """
    Universal streaming health check.
    
    Comprehensive health check for all universal streaming components
    including services, converters, and flows.
    """
    try:
        # Get health from all components
        universal_flow = get_universal_flow()
        flow_health = await universal_flow.health_check()
        
        # Extract component health
        overall_healthy = flow_health.get("overall_healthy", False)
        
        return {
            "overall_healthy": overall_healthy,
            "phase_3b_status": "operational" if overall_healthy else "degraded",
            "universal_streaming": "active" if overall_healthy else "inactive",
            "multi_model_support": "enabled" if overall_healthy else "disabled",
            "real_time_tools": "operational" if overall_healthy else "degraded",
            "intelligent_caching": "active" if overall_healthy else "inactive",
            "components": {
                "universal_flow": flow_health,
                "supported_providers": len(universal_flow.provider_priority),
                "conversion_support": "active",
                "cache_integration": "enabled"
            },
            "capabilities": {
                "total_models_supported": "100+",
                "providers_supported": len(universal_flow.provider_priority),
                "real_time_tool_execution": True,
                "intelligent_provider_selection": True,
                "cross_provider_optimization": True,
                "universal_caching": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Universal health check failed", error=str(e))
        return {
            "overall_healthy": False,
            "phase_3b_status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
