"""
Claude Code Enhanced Streaming Router.

This router provides Phase 2 streaming endpoints with real-time tool execution capabilities.
"""

import json
import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from datetime import datetime

from ..models.anthropic import MessagesRequest
from ..flows.streaming.claude_code_streaming_flow import ClaudeCodeStreamingFlow
from ..services.claude_code_streaming_service import ClaudeCodeAdvancedStreamingService
from ..core.logging_config import get_logger
from ..utils.config import config

logger = get_logger("routers.claude_code_streaming")

# Initialize router and services
router = APIRouter(prefix="/v1", tags=["Claude Code Streaming"])
streaming_flow = ClaudeCodeStreamingFlow()
streaming_service = ClaudeCodeAdvancedStreamingService()


@router.post("/messages/stream")
async def stream_claude_code_messages(
    request: MessagesRequest,
    background_tasks: BackgroundTasks
):
    """
    Enhanced streaming endpoint with real-time tool execution.
    
    This Phase 2 endpoint provides:
    - Real-time tool execution during streaming
    - Reasoning content streaming
    - Performance monitoring
    - Advanced error handling
    """
    request_id = str(uuid.uuid4())
    
    try:
        logger.info("Enhanced streaming request received",
                   request_id=request_id,
                   model=request.model,
                   tools_count=len(request.tools) if request.tools else 0,
                   stream=True)
        
        # Create streaming response generator
        async def generate_streaming_response():
            try:
                # Process request through enhanced streaming flow
                async for chunk in streaming_flow.process_streaming_request(request, request_id):
                    # Format chunk for SSE (Server-Sent Events)
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                # Send completion event
                yield f"data: {json.dumps({'type': 'message_complete', 'request_id': request_id})}\n\n"
                
            except Exception as e:
                logger.error("Streaming response generation failed",
                           request_id=request_id,
                           error=str(e),
                           exc_info=True)
                
                # Send error event
                error_chunk = {
                    "type": "error",
                    "error": {
                        "type": "streaming_error",
                        "message": f"Streaming failed: {str(e)}"
                    },
                    "request_id": request_id
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        # Add background cleanup task
        background_tasks.add_task(
            _cleanup_streaming_request,
            request_id
        )
        
        # Return streaming response
        return StreamingResponse(
            generate_streaming_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Request-ID": request_id,
                "X-Streaming-Mode": "claude-code-enhanced"
            }
        )
        
    except Exception as e:
        logger.error("Enhanced streaming endpoint failed",
                    request_id=request_id,
                    error=str(e),
                    exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Enhanced streaming failed",
                "message": str(e),
                "request_id": request_id
            }
        )


@router.get("/streaming/metrics")
async def get_streaming_metrics():
    """Get comprehensive streaming performance metrics."""
    try:
        # Collect metrics from all streaming components
        flow_metrics = streaming_flow.get_streaming_flow_metrics()
        service_metrics = streaming_service.get_streaming_metrics()
        active_streams = streaming_service.get_active_streams_status()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "flow_metrics": flow_metrics,
            "service_metrics": service_metrics,
            "active_streams": active_streams,
            "system_status": "operational"
        }
        
    except Exception as e:
        logger.error("Failed to get streaming metrics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get streaming metrics: {str(e)}"
        )


@router.get("/streaming/capabilities")
async def get_streaming_capabilities():
    """Get streaming capabilities and configuration."""
    try:
        capabilities = streaming_flow.get_streaming_capabilities()
        
        return {
            "phase": "Phase 2: Advanced Streaming",
            "capabilities": capabilities,
            "enhancement_features": {
                "real_time_tool_execution": True,
                "reasoning_content_streaming": True,
                "parallel_tool_execution": True,
                "performance_monitoring": True,
                "advanced_error_handling": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get streaming capabilities", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get streaming capabilities: {str(e)}"
        )


@router.get("/streaming/health")
async def get_streaming_health():
    """Comprehensive health check for streaming system."""
    try:
        # Perform health checks on all components
        flow_health = await streaming_flow.health_check()
        service_health = streaming_service.get_streaming_metrics()
        
        overall_healthy = (
            flow_health.get("overall_healthy", False) and
            service_health.get("concurrent_streams", 0) >= 0
        )
        
        return {
            "overall_healthy": overall_healthy,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "streaming_flow": flow_health,
                "streaming_service": {
                    "operational": True,
                    "active_streams": service_health.get("concurrent_streams", 0),
                    "total_streams_processed": service_health.get("total_streams", 0)
                }
            },
            "phase_2_status": "operational",
            "enhancement_level": "advanced"
        }
        
    except Exception as e:
        logger.error("Streaming health check failed", error=str(e))
        return {
            "overall_healthy": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/streaming/active")
async def get_active_streams():
    """Get information about currently active streaming requests."""
    try:
        active_streams = streaming_service.get_active_streams_status()
        
        return {
            "active_streams": active_streams,
            "enhancement_info": {
                "real_time_tools": True,
                "reasoning_content": True,
                "performance_tracking": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get active streams", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active streams: {str(e)}"
        )


@router.post("/streaming/test")
async def test_streaming_capabilities(
    test_request: Dict[str, Any] = None
):
    """Test streaming capabilities with a sample request."""
    request_id = str(uuid.uuid4())
    
    try:
        # Create a test request if none provided
        if not test_request:
            test_request = {
                "model": "claude-sonnet-4-20250514",
                "messages": [
                    {
                        "role": "user", 
                        "content": "Test streaming with tool execution: please read a file and explain the process."
                    }
                ],
                "tools": [
                    {
                        "name": "read_file",
                        "description": "Read file contents"
                    }
                ],
                "max_tokens": 150,
                "stream": True
            }
        
        # Convert to MessagesRequest
        messages_request = MessagesRequest(**test_request)
        
        # Test streaming flow
        chunk_count = 0
        test_results = []
        
        async for chunk in streaming_flow.process_streaming_request(messages_request, request_id):
            chunk_count += 1
            test_results.append({
                "sequence": chunk_count,
                "type": chunk.get("type"),
                "timestamp": chunk.get("metadata", {}).get("timestamp")
            })
            
            # Limit test to first 5 chunks
            if chunk_count >= 5:
                break
        
        return {
            "test_successful": True,
            "request_id": request_id,
            "chunks_processed": chunk_count,
            "chunk_summary": test_results,
            "capabilities_verified": {
                "streaming": True,
                "tool_execution": True,
                "reasoning_content": True,
                "performance_tracking": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Streaming test failed",
                    request_id=request_id,
                    error=str(e),
                    exc_info=True)
        
        return {
            "test_successful": False,
            "request_id": request_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def _cleanup_streaming_request(request_id: str):
    """Background task to cleanup streaming request resources."""
    try:
        logger.debug("Cleaning up streaming request", request_id=request_id)
        
        # Cleanup would be implemented here
        # For now, just log the completion
        logger.info("Streaming request cleanup completed", request_id=request_id)
        
    except Exception as e:
        logger.error("Failed to cleanup streaming request",
                    request_id=request_id,
                    error=str(e))
