"""
Streaming Cache Flow for Claude Code Advanced Streaming.

This flow orchestrates intelligent caching integration with streaming responses,
providing cache-aware streaming with performance optimization and cache warming.

Phase 3A: Enhanced Streaming with Advanced LiteLLM
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, AsyncIterator, Tuple
from datetime import datetime, timedelta

from ...services.base import ConversionService
from ...models.anthropic import MessagesRequest
from ...core.logging_config import get_logger
from ...services.claude_code_cache_service import ClaudeCodeAdvancedCacheService
from ...services.claude_code_streaming_service import StreamingChunk
from ...flows.streaming.claude_code_streaming_flow import ClaudeCodeStreamingFlow

logger = get_logger("flows.streaming_cache")


class StreamingCacheFlow(ConversionService):
    """Advanced streaming flow with intelligent caching integration."""
    
    def __init__(self):
        """Initialize the streaming cache flow."""
        super().__init__("StreamingCacheFlow")
        
        # Initialize services
        self.cache_service = ClaudeCodeAdvancedCacheService()
        self.streaming_flow = ClaudeCodeStreamingFlow()
        
        # Cache flow configuration
        self.cache_flow_config = {
            "enable_cache_warming": True,
            "cache_partial_responses": True,
            "max_cache_chunks": 1000,
            "cache_threshold_chunks": 5,  # Minimum chunks to cache
            "parallel_cache_storage": True,
            "cache_quality_threshold": 0.8  # Quality score threshold for caching
        }
        
        # Performance tracking
        self.cache_flow_metrics = {
            "total_streaming_requests": 0,
            "cache_enhanced_requests": 0,
            "cache_bypassed_requests": 0,
            "average_cache_save_time": 0.0,
            "cache_warming_hits": 0,
            "partial_cache_hits": 0
        }
        
        logger.info("Streaming Cache Flow initialized",
                   cache_warming_enabled=self.cache_flow_config["enable_cache_warming"],
                   cache_partial_responses=self.cache_flow_config["cache_partial_responses"])
    
    def convert(self, source: MessagesRequest, **kwargs) -> "ConversionResult":
        """
        Convert MessagesRequest for cache-aware streaming processing.
        
        This method provides compatibility with ConversionService interface.
        For actual streaming, use process_cached_streaming_request.
        """
        try:
            from ...models.instructor import ConversionResult
            
            # Generate cache key to verify caching capability
            cache_key = self.cache_service.generate_cache_key(source, kwargs.get('context'))
            
            return ConversionResult(
                success=True,
                converted_data={"stream": True, "model": source.model, "cache_key": cache_key},
                metadata={
                    "flow_type": "streaming_cache",
                    "cache_enabled": True,
                    "cache_warming": self.cache_flow_config["enable_cache_warming"],
                    "partial_caching": self.cache_flow_config["cache_partial_responses"],
                    "note": "Use process_cached_streaming_request for actual streaming"
                }
            )
            
        except Exception as e:
            from ...models.instructor import ConversionResult
            logger.error("Streaming cache flow conversion failed", error=str(e))
            return ConversionResult(
                success=False,
                errors=[f"Streaming cache flow validation failed: {str(e)}"]
            )
    
    async def process_cached_streaming_request(
        self,
        request: MessagesRequest,
        request_id: str,
        cache_options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Process streaming request with intelligent caching.
        
        Args:
            request: Anthropic MessagesRequest
            request_id: Unique request identifier
            cache_options: Optional caching configuration
            
        Yields:
            Dict[str, Any]: Anthropic-format streaming chunks with cache metadata
        """
        flow_start_time = time.time()
        cache_options = cache_options or {}
        
        try:
            # Update metrics
            self.cache_flow_metrics["total_streaming_requests"] += 1
            
            logger.info("Processing cache-aware streaming request",
                       request_id=request_id,
                       model=request.model,
                       cache_enabled=True)
            
            # Generate cache key
            cache_key = self.cache_service.generate_cache_key(
                request, 
                cache_options.get('context')
            )
            
            # Check for cached response
            cached_response = await self.cache_service.get_cached_response(cache_key)
            
            if cached_response and not cache_options.get('bypass_cache', False):
                # Serve from cache
                cached_chunks, cached_metadata = cached_response
                
                logger.info("Serving response from cache",
                           request_id=request_id,
                           cache_key=cache_key[:16] + "...",
                           chunks_count=len(cached_chunks))
                
                async for chunk in self._serve_cached_response(
                    cached_chunks, cached_metadata, request_id, cache_key
                ):
                    yield chunk
                
                self.cache_flow_metrics["cache_enhanced_requests"] += 1
                return
            
            # Cache miss - generate and cache response
            logger.info("Cache miss - generating new response",
                       request_id=request_id,
                       cache_key=cache_key[:16] + "...")
            
            response_chunks = []
            response_metadata = {}
            
            # Process through streaming flow and collect chunks for caching
            async for chunk in self.streaming_flow.process_streaming_request(request, request_id):
                # Add cache metadata to chunk
                chunk["cache_metadata"] = {
                    "cache_key": cache_key[:16] + "...",
                    "cache_status": "generating",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Collect for caching if enabled
                if self.cache_flow_config["cache_partial_responses"]:
                    response_chunks.append(chunk.copy())
                
                yield chunk
            
            # Store response in cache (if sufficient quality/length)
            if await self._should_cache_response(response_chunks, request):
                cache_success = await self.cache_service.store_streaming_response(
                    cache_key,
                    request,
                    response_chunks,
                    response_metadata,
                    ttl_seconds=cache_options.get('ttl_seconds'),
                    tags=cache_options.get('tags', [])
                )
                
                if cache_success:
                    logger.info("Response cached successfully",
                               request_id=request_id,
                               cache_key=cache_key[:16] + "...",
                               chunks_count=len(response_chunks))
                else:
                    logger.warning("Failed to cache response",
                                 request_id=request_id,
                                 cache_key=cache_key[:16] + "...")
            
            self.cache_flow_metrics["cache_bypassed_requests"] += 1
            
            flow_duration = time.time() - flow_start_time
            logger.info("Cache-aware streaming completed",
                       request_id=request_id,
                       duration=f"{flow_duration:.2f}s",
                       cached=len(response_chunks) > 0)
            
        except Exception as e:
            flow_duration = time.time() - flow_start_time
            
            logger.error("Cache-aware streaming failed",
                        request_id=request_id,
                        error=str(e),
                        duration=f"{flow_duration:.2f}s",
                        exc_info=True)
            
            # Yield error response
            yield {
                "type": "error",
                "error": {
                    "type": "streaming_cache_error",
                    "message": f"Cache-aware streaming failed: {str(e)}"
                },
                "cache_metadata": {
                    "cache_status": "error",
                    "error": str(e)
                },
                "metadata": {
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
    
    async def _serve_cached_response(
        self,
        cached_chunks: List[Dict[str, Any]],
        cached_metadata: Dict[str, Any],
        request_id: str,
        cache_key: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """Serve cached response with realistic streaming timing."""
        try:
            chunk_delay = 0.05  # 50ms delay between chunks for realistic streaming
            
            for i, chunk in enumerate(cached_chunks):
                # Add cache metadata
                chunk = chunk.copy()
                chunk["cache_metadata"] = {
                    "cache_key": cache_key[:16] + "...",
                    "cache_status": "hit",
                    "cached_at": cached_metadata.get("cached_at"),
                    "chunk_index": i,
                    "total_chunks": len(cached_chunks)
                }
                
                # Update request metadata
                chunk["request_id"] = request_id
                chunk["chunk_sequence"] = i + 1
                
                yield chunk
                
                # Add realistic streaming delay
                if i < len(cached_chunks) - 1:  # Don't delay after last chunk
                    await asyncio.sleep(chunk_delay)
            
            logger.debug("Cached response served completely",
                        request_id=request_id,
                        chunks_served=len(cached_chunks))
            
        except Exception as e:
            logger.error("Failed to serve cached response",
                        request_id=request_id,
                        error=str(e))
            
            # Yield error chunk
            yield {
                "type": "error",
                "error": {
                    "type": "cache_serving_error",
                    "message": f"Failed to serve cached response: {str(e)}"
                },
                "cache_metadata": {
                    "cache_status": "error",
                    "error": str(e)
                }
            }
    
    async def _should_cache_response(
        self,
        response_chunks: List[Dict[str, Any]],
        request: MessagesRequest
    ) -> bool:
        """Determine if response should be cached based on quality metrics."""
        try:
            # Check minimum chunk threshold
            if len(response_chunks) < self.cache_flow_config["cache_threshold_chunks"]:
                logger.debug("Response too short to cache",
                           chunks_count=len(response_chunks),
                           threshold=self.cache_flow_config["cache_threshold_chunks"])
                return False
            
            # Check maximum chunk limit
            if len(response_chunks) > self.cache_flow_config["max_cache_chunks"]:
                logger.debug("Response too long to cache",
                           chunks_count=len(response_chunks),
                           max_chunks=self.cache_flow_config["max_cache_chunks"])
                return False
            
            # Check for error chunks
            error_chunks = [chunk for chunk in response_chunks if chunk.get("type") == "error"]
            if error_chunks:
                logger.debug("Response contains errors - not caching",
                           error_chunks_count=len(error_chunks))
                return False
            
            # Check response quality (basic heuristics)
            content_chunks = [
                chunk for chunk in response_chunks 
                if chunk.get("type") == "message_delta" and chunk.get("delta", {}).get("text")
            ]
            
            if content_chunks:
                total_content_length = sum(
                    len(chunk.get("delta", {}).get("text", ""))
                    for chunk in content_chunks
                )
                
                # Don't cache very short responses
                if total_content_length < 50:
                    logger.debug("Content too short to cache",
                               content_length=total_content_length)
                    return False
            
            # Check for tool execution results (these are valuable to cache)
            tool_chunks = [
                chunk for chunk in response_chunks
                if chunk.get("type") in ["tool_call_delta", "tool_result_delta"]
            ]
            
            # Prefer caching responses with tool execution
            if tool_chunks:
                logger.debug("Response contains tool execution - good for caching",
                           tool_chunks_count=len(tool_chunks))
                return True
            
            # For content-only responses, use basic quality check
            return len(content_chunks) >= 3  # At least 3 content chunks
            
        except Exception as e:
            logger.error("Error evaluating cache worthiness", error=str(e))
            return False
    
    async def warm_cache_for_request(
        self,
        request: MessagesRequest,
        background: bool = True
    ) -> bool:
        """
        Warm cache by pre-generating response for request.
        
        Args:
            request: Request to warm cache for
            background: Whether to run in background
            
        Returns:
            bool: True if cache warming initiated, False otherwise
        """
        try:
            if not self.cache_flow_config["enable_cache_warming"]:
                return False
            
            cache_key = self.cache_service.generate_cache_key(request)
            
            # Check if already cached
            existing_response = await self.cache_service.get_cached_response(cache_key)
            if existing_response:
                logger.debug("Cache already warmed",
                           cache_key=cache_key[:16] + "...")
                return True
            
            if background:
                # Warm cache in background
                asyncio.create_task(self._background_cache_warming(request, cache_key))
                return True
            else:
                # Warm cache synchronously
                return await self._background_cache_warming(request, cache_key)
                
        except Exception as e:
            logger.error("Failed to warm cache", error=str(e))
            return False
    
    async def _background_cache_warming(
        self,
        request: MessagesRequest,
        cache_key: str
    ) -> bool:
        """Background task for cache warming."""
        try:
            logger.info("Starting background cache warming",
                       cache_key=cache_key[:16] + "...")
            
            # Generate response chunks
            response_chunks = []
            request_id = f"cache_warm_{int(time.time())}"
            
            async for chunk in self.streaming_flow.process_streaming_request(request, request_id):
                response_chunks.append(chunk)
            
            # Store in cache
            if await self._should_cache_response(response_chunks, request):
                success = await self.cache_service.store_streaming_response(
                    cache_key,
                    request,
                    response_chunks,
                    {"cache_warmed": True, "warmed_at": datetime.utcnow().isoformat()}
                )
                
                if success:
                    self.cache_flow_metrics["cache_warming_hits"] += 1
                    logger.info("Cache warming completed successfully",
                               cache_key=cache_key[:16] + "...",
                               chunks_count=len(response_chunks))
                    return True
            
            logger.info("Cache warming completed - response not cached",
                       cache_key=cache_key[:16] + "...")
            return False
            
        except Exception as e:
            logger.error("Background cache warming failed",
                        cache_key=cache_key[:16] + "...",
                        error=str(e))
            return False
    
    async def get_cache_flow_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cache flow metrics."""
        try:
            # Get cache service stats
            cache_stats = await self.cache_service.get_cache_stats()
            
            # Calculate flow-specific metrics
            total_requests = self.cache_flow_metrics["total_streaming_requests"]
            cache_enhancement_rate = 0.0
            if total_requests > 0:
                cache_enhancement_rate = (
                    self.cache_flow_metrics["cache_enhanced_requests"] / total_requests
                ) * 100
            
            return {
                "cache_flow_metrics": self.cache_flow_metrics,
                "cache_enhancement_rate": cache_enhancement_rate,
                "cache_service_stats": cache_stats,
                "configuration": self.cache_flow_config,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get cache flow metrics", error=str(e))
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of cache flow components."""
        try:
            # Check cache service health
            cache_stats = await self.cache_service.get_cache_stats()
            cache_healthy = "error" not in cache_stats
            
            # Check streaming flow health
            streaming_health = await self.streaming_flow.health_check()
            streaming_healthy = streaming_health.get("overall_healthy", False)
            
            overall_healthy = cache_healthy and streaming_healthy
            
            return {
                "overall_healthy": overall_healthy,
                "components": {
                    "cache_service": {
                        "healthy": cache_healthy,
                        "stats": cache_stats
                    },
                    "streaming_flow": streaming_health
                },
                "cache_flow_metrics": self.cache_flow_metrics,
                "configuration": self.cache_flow_config,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Cache flow health check failed", error=str(e))
            return {
                "overall_healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            } 