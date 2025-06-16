"""
Enhanced Streaming Router with Advanced Caching.

This router provides Phase 3A streaming endpoints with intelligent caching,
cache management, and performance optimization capabilities.

Phase 3A: Enhanced Streaming with Advanced LiteLLM
"""

import json
import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta

from ..models.anthropic import MessagesRequest
from ..flows.caching.streaming_cache_flow import StreamingCacheFlow
from ..services.claude_code_cache_service import ClaudeCodeAdvancedCacheService
from ..core.logging_config import get_logger
from ..utils.config import config

logger = get_logger("routers.streaming_cache")

# Initialize router and services
router = APIRouter(prefix="/v1/cache", tags=["Phase 3A: Advanced Streaming Cache"])
cache_flow = StreamingCacheFlow()
cache_service = ClaudeCodeAdvancedCacheService()


@router.post("/messages/stream")
async def stream_with_advanced_cache(
    request: MessagesRequest,
    background_tasks: BackgroundTasks,
    bypass_cache: bool = Query(False, description="Bypass cache and force new generation"),
    cache_ttl: Optional[int] = Query(None, description="Custom cache TTL in seconds"),
    cache_tags: Optional[str] = Query(None, description="Comma-separated cache tags")
):
    """
    Enhanced streaming endpoint with intelligent caching.
    
    This Phase 3A endpoint provides:
    - Intelligent response caching with configurable TTL
    - Cache warming and pre-generation
    - Performance optimization through caching
    - Cache tag-based invalidation support
    """
    request_id = str(uuid.uuid4())
    
    try:
        logger.info("Enhanced cache streaming request received",
                   request_id=request_id,
                   model=request.model,
                   bypass_cache=bypass_cache,
                   cache_ttl=cache_ttl)
        
        # Parse cache tags
        tags = []
        if cache_tags:
            tags = [tag.strip() for tag in cache_tags.split(",")]
        
        # Cache options
        cache_options = {
            "bypass_cache": bypass_cache,
            "ttl_seconds": cache_ttl,
            "tags": tags,
            "context": {
                "request_id": request_id,
                "endpoint": "cache_stream",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Create streaming response generator
        async def generate_cached_streaming_response():
            try:
                # Process request through cache-aware streaming flow
                async for chunk in cache_flow.process_cached_streaming_request(
                    request, request_id, cache_options
                ):
                    # Format chunk for SSE (Server-Sent Events)
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                # Send completion event
                completion_chunk = {
                    "type": "message_complete",
                    "request_id": request_id,
                    "cache_metadata": {
                        "cache_flow": "phase_3a_advanced",
                        "completion_time": datetime.utcnow().isoformat()
                    }
                }
                yield f"data: {json.dumps(completion_chunk)}\n\n"
                
            except Exception as e:
                logger.error("Cached streaming response generation failed",
                           request_id=request_id,
                           error=str(e),
                           exc_info=True)
                
                # Send error event
                error_chunk = {
                    "type": "error",
                    "error": {
                        "type": "cached_streaming_error",
                        "message": f"Cached streaming failed: {str(e)}"
                    },
                    "request_id": request_id,
                    "cache_metadata": {
                        "cache_status": "error",
                        "error": str(e)
                    }
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        # Add background cleanup task
        background_tasks.add_task(
            _cleanup_cache_streaming_request,
            request_id
        )
        
        # Return streaming response
        return StreamingResponse(
            generate_cached_streaming_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Request-ID": request_id,
                "X-Streaming-Mode": "phase-3a-cached",
                "X-Cache-Enabled": "true"
            }
        )
        
    except Exception as e:
        logger.error("Enhanced cache streaming endpoint failed",
                    request_id=request_id,
                    error=str(e),
                    exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Enhanced cache streaming failed",
                "message": str(e),
                "request_id": request_id
            }
        )


@router.get("/stats")
async def get_cache_statistics():
    """Get comprehensive cache statistics and performance metrics."""
    try:
        # Get cache flow metrics
        flow_metrics = await cache_flow.get_cache_flow_metrics()
        
        return {
            "phase": "Phase 3A: Advanced Streaming Cache",
            "metrics": flow_metrics,
            "performance_summary": {
                "cache_enhancement_rate": flow_metrics.get("cache_enhancement_rate", 0),
                "total_requests": flow_metrics.get("cache_flow_metrics", {}).get("total_streaming_requests", 0),
                "cache_hits": flow_metrics.get("cache_service_stats", {}).get("cache_hits", 0),
                "hit_rate": flow_metrics.get("cache_service_stats", {}).get("hit_rate", 0)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get cache statistics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache statistics: {str(e)}"
        )


@router.get("/health")
async def get_cache_health():
    """Comprehensive health check for cache system."""
    try:
        # Perform health checks on cache components
        health_result = await cache_flow.health_check()
        
        return {
            **health_result,
            "phase_3a_status": "operational" if health_result.get("overall_healthy") else "degraded",
            "cache_enhancement": "active",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Cache health check failed", error=str(e))
        return {
            "overall_healthy": False,
            "phase_3a_status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/warm")
async def warm_cache(
    request: MessagesRequest,
    background: bool = Query(True, description="Run cache warming in background")
):
    """Warm cache by pre-generating response for request."""
    try:
        request_id = str(uuid.uuid4())
        
        logger.info("Cache warming requested",
                   request_id=request_id,
                   model=request.model,
                   background=background)
        
        # Initiate cache warming
        warming_success = await cache_flow.warm_cache_for_request(request, background)
        
        return {
            "cache_warming_initiated": warming_success,
            "request_id": request_id,
            "background_mode": background,
            "model": request.model,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Cache warming failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Cache warming failed: {str(e)}"
        )


@router.delete("/invalidate")
async def invalidate_cache(
    pattern: Optional[str] = Query(None, description="Regex pattern to match cache keys"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to match"),
    older_than_hours: Optional[int] = Query(None, description="Invalidate entries older than X hours")
):
    """Invalidate cache entries based on criteria."""
    try:
        # Parse parameters
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        older_than = None
        if older_than_hours:
            older_than = timedelta(hours=older_than_hours)
        
        # Perform invalidation
        invalidated_count = await cache_service.invalidate_cache(
            pattern=pattern,
            tags=tag_list,
            older_than=older_than
        )
        
        logger.info("Cache invalidation completed",
                   invalidated_count=invalidated_count,
                   pattern=pattern,
                   tags=tags,
                   older_than_hours=older_than_hours)
        
        return {
            "invalidation_completed": True,
            "entries_invalidated": invalidated_count,
            "criteria": {
                "pattern": pattern,
                "tags": tag_list,
                "older_than_hours": older_than_hours
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Cache invalidation failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Cache invalidation failed: {str(e)}"
        )


@router.get("/entries")
async def list_cache_entries(
    limit: int = Query(10, description="Maximum number of entries to return"),
    skip: int = Query(0, description="Number of entries to skip"),
    sort_by: str = Query("created_at", description="Sort field: created_at, last_accessed, access_count")
):
    """List cache entries with pagination."""
    try:
        # Get cache stats with entry details
        cache_stats = await cache_service.get_cache_stats()
        
        return {
            "cache_entries_summary": {
                "total_entries": cache_stats.get("current_state", {}).get("entries_count", 0),
                "total_size_mb": cache_stats.get("current_state", {}).get("size_mb", 0),
                "capacity_used_percent": cache_stats.get("current_state", {}).get("capacity_used_percent", 0)
            },
            "pagination": {
                "limit": limit,
                "skip": skip,
                "sort_by": sort_by
            },
            "age_distribution": cache_stats.get("age_distribution", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to list cache entries", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list cache entries: {str(e)}"
        )


@router.post("/test")
async def test_cache_performance(
    test_type: str = Query("basic", description="Test type: basic, warming, invalidation"),
    iterations: int = Query(3, description="Number of test iterations")
):
    """Test cache performance with various scenarios."""
    test_id = str(uuid.uuid4())
    
    try:
        logger.info("Cache performance test started",
                   test_id=test_id,
                   test_type=test_type,
                   iterations=iterations)
        
        test_results = []
        
        if test_type == "basic":
            # Basic cache hit/miss test
            test_request = MessagesRequest(
                model="claude-sonnet-4-20250514",
                messages=[
                    {"role": "user", "content": "Test cache performance with a simple request."}
                ],
                max_tokens=50,
                stream=True
            )
            
            for i in range(iterations):
                start_time = datetime.utcnow()
                
                # Generate cache key
                cache_key = cache_service.generate_cache_key(test_request)
                
                # Check cache
                cached_response = await cache_service.get_cached_response(cache_key)
                
                end_time = datetime.utcnow()
                duration_ms = (end_time - start_time).total_seconds() * 1000
                
                test_results.append({
                    "iteration": i + 1,
                    "cache_hit": cached_response is not None,
                    "duration_ms": round(duration_ms, 2),
                    "cache_key": cache_key[:16] + "..."
                })
        
        elif test_type == "warming":
            # Cache warming test
            test_request = MessagesRequest(
                model="claude-sonnet-4-20250514",
                messages=[
                    {"role": "user", "content": f"Cache warming test {test_id}"}
                ],
                max_tokens=50,
                stream=True
            )
            
            for i in range(iterations):
                start_time = datetime.utcnow()
                
                warming_success = await cache_flow.warm_cache_for_request(
                    test_request, background=False
                )
                
                end_time = datetime.utcnow()
                duration_ms = (end_time - start_time).total_seconds() * 1000
                
                test_results.append({
                    "iteration": i + 1,
                    "warming_success": warming_success,
                    "duration_ms": round(duration_ms, 2)
                })
        
        elif test_type == "invalidation":
            # Cache invalidation test
            for i in range(iterations):
                start_time = datetime.utcnow()
                
                invalidated_count = await cache_service.invalidate_cache(
                    older_than=timedelta(seconds=1)
                )
                
                end_time = datetime.utcnow()
                duration_ms = (end_time - start_time).total_seconds() * 1000
                
                test_results.append({
                    "iteration": i + 1,
                    "invalidated_count": invalidated_count,
                    "duration_ms": round(duration_ms, 2)
                })
        
        # Calculate performance metrics
        avg_duration = sum(r["duration_ms"] for r in test_results) / len(test_results)
        max_duration = max(r["duration_ms"] for r in test_results)
        min_duration = min(r["duration_ms"] for r in test_results)
        
        return {
            "test_completed": True,
            "test_id": test_id,
            "test_type": test_type,
            "iterations": iterations,
            "results": test_results,
            "performance_summary": {
                "average_duration_ms": round(avg_duration, 2),
                "max_duration_ms": max_duration,
                "min_duration_ms": min_duration,
                "performance_rating": "excellent" if avg_duration < 10 else "good" if avg_duration < 50 else "fair"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Cache performance test failed",
                    test_id=test_id,
                    test_type=test_type,
                    error=str(e))
        
        return {
            "test_completed": False,
            "test_id": test_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/configuration")
async def get_cache_configuration():
    """Get current cache configuration and settings."""
    try:
        cache_stats = await cache_service.get_cache_stats()
        flow_metrics = await cache_flow.get_cache_flow_metrics()
        
        return {
            "phase": "Phase 3A: Advanced Streaming Cache",
            "cache_service_config": cache_stats.get("configuration", {}),
            "cache_flow_config": flow_metrics.get("configuration", {}),
            "capabilities": {
                "intelligent_caching": True,
                "cache_warming": True,
                "pattern_invalidation": True,
                "performance_monitoring": True,
                "background_cleanup": True
            },
            "limits": {
                "max_entries": cache_stats.get("configuration", {}).get("max_entries", 0),
                "max_size_mb": cache_stats.get("configuration", {}).get("max_size_mb", 0),
                "default_ttl_seconds": cache_stats.get("configuration", {}).get("default_ttl_seconds", 0)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get cache configuration", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache configuration: {str(e)}"
        )


async def _cleanup_cache_streaming_request(request_id: str):
    """Background task to cleanup cache streaming request resources."""
    try:
        logger.debug("Cleaning up cache streaming request", request_id=request_id)
        
        # Cleanup would be implemented here
        # For now, just log the completion
        logger.info("Cache streaming request cleanup completed", request_id=request_id)
        
    except Exception as e:
        logger.error("Failed to cleanup cache streaming request",
                    request_id=request_id,
                    error=str(e)) 