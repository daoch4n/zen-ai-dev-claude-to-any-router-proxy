"""
Claude Code Advanced Streaming Cache Service.

This service provides intelligent caching for streaming responses with advanced
cache invalidation strategies, performance optimization, and comprehensive monitoring.

Phase 3A: Enhanced Streaming with Advanced LiteLLM
"""

import hashlib
import json
import time
import asyncio
from typing import Any, Dict, List, Optional, Tuple, AsyncIterator
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, asdict
import threading

from ..services.base import BaseService
from ..models.anthropic import MessagesRequest
from ..core.logging_config import get_logger
from ..utils.config import config

logger = get_logger("cache.claude_code_streaming")


@dataclass
class CacheEntry:
    """Represents a cached streaming response entry."""
    cache_key: str
    request_hash: str
    response_chunks: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: int
    size_bytes: int
    tags: List[str]
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.utcnow() > (self.created_at + timedelta(seconds=self.ttl_seconds))
    
    @property
    def age_seconds(self) -> float:
        """Get age of cache entry in seconds."""
        return (datetime.utcnow() - self.created_at).total_seconds()


@dataclass
class CacheStats:
    """Cache performance statistics."""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_invalidations: int = 0
    total_cached_entries: int = 0
    total_cache_size_bytes: int = 0
    average_hit_time_ms: float = 0.0
    average_miss_time_ms: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate percentage."""
        return 100.0 - self.hit_rate


class ClaudeCodeAdvancedCacheService(BaseService):
    """Advanced caching service for Claude Code streaming responses."""
    
    def __init__(self):
        """Initialize the advanced cache service."""
        super().__init__("ClaudeCodeAdvancedCache")
        
        # Cache storage (in-memory for now, can be extended to Redis/etc)
        self._cache_store: OrderedDict[str, CacheEntry] = OrderedDict()
        self._cache_lock = threading.RLock()
        
        # Cache configuration
        self.cache_config = {
            "max_entries": getattr(config, 'cache_max_entries', 1000),
            "max_size_mb": getattr(config, 'cache_max_size_mb', 500),
            "default_ttl_seconds": getattr(config, 'cache_default_ttl', 3600),  # 1 hour
            "cleanup_interval_seconds": getattr(config, 'cache_cleanup_interval', 300),  # 5 minutes
            "enable_compression": getattr(config, 'cache_enable_compression', True),
            "enable_metrics": getattr(config, 'cache_enable_metrics', True)
        }
        
        # Performance statistics
        self.stats = CacheStats()
        self._stats_lock = threading.RLock()
        
        # Cache invalidation patterns
        self.invalidation_patterns = {
            "model_change": r"model:.*",
            "tool_change": r"tools:.*", 
            "user_change": r"user:.*",
            "time_based": r"time:.*"
        }
        
        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_background_cleanup()
        
        logger.info("Advanced Cache Service initialized",
                   max_entries=self.cache_config["max_entries"],
                   max_size_mb=self.cache_config["max_size_mb"],
                   default_ttl=self.cache_config["default_ttl_seconds"])
    
    def generate_cache_key(
        self,
        request: MessagesRequest,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate intelligent cache key for streaming request.
        
        Args:
            request: The MessagesRequest to cache
            additional_context: Optional additional context for cache key
            
        Returns:
            str: Unique cache key
        """
        try:
            # Create comprehensive cache key components
            key_components = {
                "model": request.model,
                "messages": [
                    {
                        "role": msg.role,
                        "content": str(msg.content)[:1000]  # Limit content length for key
                    }
                    for msg in request.messages
                ],
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description[:200] if tool.description else ""
                    }
                    for tool in (request.tools or [])
                ],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": request.stream
            }
            
            # Add additional context if provided
            if additional_context:
                key_components["context"] = additional_context
            
            # Create stable JSON representation
            key_json = json.dumps(key_components, sort_keys=True, separators=(',', ':'))
            
            # Generate SHA-256 hash for consistent key length
            cache_key = hashlib.sha256(key_json.encode('utf-8')).hexdigest()
            
            logger.debug("Generated cache key",
                        cache_key=cache_key[:16] + "...",
                        model=request.model,
                        message_count=len(request.messages),
                        tools_count=len(request.tools) if request.tools else 0)
            
            return cache_key
            
        except Exception as e:
            logger.error("Failed to generate cache key",
                        error=str(e),
                        model=request.model)
            # Fallback to simple hash
            return hashlib.md5(str(request).encode()).hexdigest()
    
    async def get_cached_response(
        self,
        cache_key: str
    ) -> Optional[Tuple[List[Dict[str, Any]], Dict[str, Any]]]:
        """
        Retrieve cached streaming response.
        
        Args:
            cache_key: The cache key to look up
            
        Returns:
            Optional[Tuple[List[Dict], Dict]]: Cached chunks and metadata, or None
        """
        start_time = time.time()
        
        try:
            with self._cache_lock:
                cache_entry = self._cache_store.get(cache_key)
                
                if cache_entry is None:
                    await self._record_cache_miss(start_time)
                    return None
                
                # Check if entry has expired
                if cache_entry.is_expired:
                    logger.debug("Cache entry expired",
                               cache_key=cache_key[:16] + "...",
                               age_seconds=cache_entry.age_seconds)
                    
                    # Remove expired entry
                    del self._cache_store[cache_key]
                    await self._record_cache_miss(start_time)
                    return None
                
                # Update access information
                cache_entry.last_accessed = datetime.utcnow()
                cache_entry.access_count += 1
                
                # Move to end (LRU)
                self._cache_store.move_to_end(cache_key)
                
                await self._record_cache_hit(start_time)
                
                logger.info("Cache hit successful",
                           cache_key=cache_key[:16] + "...",
                           access_count=cache_entry.access_count,
                           age_seconds=cache_entry.age_seconds)
                
                return cache_entry.response_chunks, cache_entry.metadata
                
        except Exception as e:
            logger.error("Failed to retrieve cached response",
                        cache_key=cache_key[:16] + "...",
                        error=str(e))
            await self._record_cache_miss(start_time)
            return None
    
    async def store_streaming_response(
        self,
        cache_key: str,
        request: MessagesRequest,
        response_chunks: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Store streaming response in cache.
        
        Args:
            cache_key: The cache key to store under
            request: Original request for context
            response_chunks: List of streaming response chunks
            metadata: Optional metadata to store with response
            ttl_seconds: Optional custom TTL (uses default if None)
            tags: Optional tags for cache invalidation
            
        Returns:
            bool: True if stored successfully, False otherwise
        """
        try:
            # Calculate response size
            response_json = json.dumps(response_chunks)
            size_bytes = len(response_json.encode('utf-8'))
            
            # Check size limits
            max_size_bytes = self.cache_config["max_size_mb"] * 1024 * 1024
            if size_bytes > max_size_bytes * 0.1:  # Don't cache responses > 10% of max size
                logger.warning("Response too large to cache",
                             cache_key=cache_key[:16] + "...",
                             size_mb=size_bytes / (1024 * 1024),
                             max_size_mb=self.cache_config["max_size_mb"])
                return False
            
            # Create cache entry
            now = datetime.utcnow()
            cache_entry = CacheEntry(
                cache_key=cache_key,
                request_hash=hashlib.md5(str(request).encode()).hexdigest(),
                response_chunks=response_chunks,
                metadata=metadata or {},
                created_at=now,
                last_accessed=now,
                access_count=0,
                ttl_seconds=ttl_seconds or self.cache_config["default_ttl_seconds"],
                size_bytes=size_bytes,
                tags=tags or []
            )
            
            with self._cache_lock:
                # Ensure we don't exceed max entries
                await self._ensure_cache_capacity()
                
                # Store the entry
                self._cache_store[cache_key] = cache_entry
                
                # Update statistics
                with self._stats_lock:
                    self.stats.total_cached_entries = len(self._cache_store)
                    self.stats.total_cache_size_bytes += size_bytes
            
            logger.info("Streaming response cached successfully",
                       cache_key=cache_key[:16] + "...",
                       size_kb=size_bytes // 1024,
                       chunks_count=len(response_chunks),
                       ttl_seconds=cache_entry.ttl_seconds)
            
            return True
            
        except Exception as e:
            logger.error("Failed to store streaming response",
                        cache_key=cache_key[:16] + "...",
                        error=str(e))
            return False
    
    async def invalidate_cache(
        self,
        pattern: Optional[str] = None,
        tags: Optional[List[str]] = None,
        older_than: Optional[timedelta] = None
    ) -> int:
        """
        Invalidate cache entries based on criteria.
        
        Args:
            pattern: Optional regex pattern to match cache keys
            tags: Optional list of tags to match
            older_than: Optional age threshold for invalidation
            
        Returns:
            int: Number of entries invalidated
        """
        try:
            invalidated_count = 0
            
            with self._cache_lock:
                keys_to_remove = []
                
                for cache_key, entry in self._cache_store.items():
                    should_invalidate = False
                    
                    # Check pattern matching
                    if pattern:
                        import re
                        if re.match(pattern, cache_key):
                            should_invalidate = True
                    
                    # Check tag matching
                    if tags:
                        if any(tag in entry.tags for tag in tags):
                            should_invalidate = True
                    
                    # Check age threshold
                    if older_than:
                        if datetime.utcnow() - entry.created_at > older_than:
                            should_invalidate = True
                    
                    if should_invalidate:
                        keys_to_remove.append(cache_key)
                
                # Remove invalidated entries
                for key in keys_to_remove:
                    entry = self._cache_store[key]
                    with self._stats_lock:
                        self.stats.total_cache_size_bytes -= entry.size_bytes
                        self.stats.cache_invalidations += 1
                    del self._cache_store[key]
                    invalidated_count += 1
                
                # Update stats
                with self._stats_lock:
                    self.stats.total_cached_entries = len(self._cache_store)
            
            logger.info("Cache invalidation completed",
                       invalidated_count=invalidated_count,
                       pattern=pattern,
                       tags=tags)
            
            return invalidated_count
            
        except Exception as e:
            logger.error("Failed to invalidate cache",
                        pattern=pattern,
                        tags=tags,
                        error=str(e))
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        try:
            with self._stats_lock:
                stats_dict = asdict(self.stats)
            
            with self._cache_lock:
                # Add current cache state
                current_entries = len(self._cache_store)
                current_size_mb = sum(entry.size_bytes for entry in self._cache_store.values()) / (1024 * 1024)
                
                # Calculate age distribution
                now = datetime.utcnow()
                age_distribution = {
                    "< 1 minute": 0,
                    "1-5 minutes": 0,
                    "5-30 minutes": 0,
                    "30+ minutes": 0
                }
                
                for entry in self._cache_store.values():
                    age_minutes = (now - entry.created_at).total_seconds() / 60
                    if age_minutes < 1:
                        age_distribution["< 1 minute"] += 1
                    elif age_minutes < 5:
                        age_distribution["1-5 minutes"] += 1
                    elif age_minutes < 30:
                        age_distribution["5-30 minutes"] += 1
                    else:
                        age_distribution["30+ minutes"] += 1
            
            return {
                **stats_dict,
                "current_state": {
                    "entries_count": current_entries,
                    "size_mb": round(current_size_mb, 2),
                    "capacity_used_percent": round((current_entries / self.cache_config["max_entries"]) * 100, 1),
                    "size_used_percent": round((current_size_mb / self.cache_config["max_size_mb"]) * 100, 1)
                },
                "age_distribution": age_distribution,
                "configuration": self.cache_config,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get cache stats", error=str(e))
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
    
    async def _ensure_cache_capacity(self) -> None:
        """Ensure cache doesn't exceed capacity limits."""
        try:
            max_entries = self.cache_config["max_entries"]
            max_size_bytes = self.cache_config["max_size_mb"] * 1024 * 1024
            
            # Remove expired entries first
            now = datetime.utcnow()
            expired_keys = [
                key for key, entry in self._cache_store.items()
                if entry.is_expired
            ]
            
            for key in expired_keys:
                entry = self._cache_store[key]
                with self._stats_lock:
                    self.stats.total_cache_size_bytes -= entry.size_bytes
                del self._cache_store[key]
            
            # Check size limit
            current_size = sum(entry.size_bytes for entry in self._cache_store.values())
            while current_size > max_size_bytes and self._cache_store:
                # Remove least recently used
                oldest_key, oldest_entry = next(iter(self._cache_store.items()))
                current_size -= oldest_entry.size_bytes
                with self._stats_lock:
                    self.stats.total_cache_size_bytes -= oldest_entry.size_bytes
                del self._cache_store[oldest_key]
            
            # Check entry count limit
            while len(self._cache_store) >= max_entries:
                # Remove least recently used
                oldest_key, oldest_entry = next(iter(self._cache_store.items()))
                with self._stats_lock:
                    self.stats.total_cache_size_bytes -= oldest_entry.size_bytes
                del self._cache_store[oldest_key]
                
        except Exception as e:
            logger.error("Failed to ensure cache capacity", error=str(e))
    
    async def _record_cache_hit(self, start_time: float) -> None:
        """Record cache hit statistics."""
        with self._stats_lock:
            self.stats.total_requests += 1
            self.stats.cache_hits += 1
            
            hit_time_ms = (time.time() - start_time) * 1000
            # Update rolling average
            total_hits = self.stats.cache_hits
            current_avg = self.stats.average_hit_time_ms
            self.stats.average_hit_time_ms = ((current_avg * (total_hits - 1)) + hit_time_ms) / total_hits
    
    async def _record_cache_miss(self, start_time: float) -> None:
        """Record cache miss statistics."""
        with self._stats_lock:
            self.stats.total_requests += 1
            self.stats.cache_misses += 1
            
            miss_time_ms = (time.time() - start_time) * 1000
            # Update rolling average
            total_misses = self.stats.cache_misses
            current_avg = self.stats.average_miss_time_ms
            self.stats.average_miss_time_ms = ((current_avg * (total_misses - 1)) + miss_time_ms) / total_misses
    
    def _start_background_cleanup(self) -> None:
        """Start background cleanup task."""
        async def cleanup_task():
            while True:
                try:
                    await asyncio.sleep(self.cache_config["cleanup_interval_seconds"])
                    await self._cleanup_expired_entries()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error("Background cleanup error", error=str(e))
        
        # Start cleanup task
        try:
            loop = asyncio.get_event_loop()
            self._cleanup_task = loop.create_task(cleanup_task())
        except RuntimeError:
            # No event loop running, cleanup will happen on demand
            pass
    
    async def _cleanup_expired_entries(self) -> None:
        """Clean up expired cache entries."""
        try:
            with self._cache_lock:
                expired_keys = [
                    key for key, entry in self._cache_store.items()
                    if entry.is_expired
                ]
                
                for key in expired_keys:
                    entry = self._cache_store[key]
                    with self._stats_lock:
                        self.stats.total_cache_size_bytes -= entry.size_bytes
                    del self._cache_store[key]
                
                if expired_keys:
                    with self._stats_lock:
                        self.stats.total_cached_entries = len(self._cache_store)
                    
                    logger.debug("Cleaned up expired cache entries",
                               expired_count=len(expired_keys),
                               remaining_entries=len(self._cache_store))
                    
        except Exception as e:
            logger.error("Failed to cleanup expired entries", error=str(e))
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of the cache service."""
        try:
            with self._cache_lock:
                current_entries = len(self._cache_store)
                current_size_mb = sum(entry.size_bytes for entry in self._cache_store.values()) / (1024 * 1024)
                
                # Check capacity utilization
                capacity_used_percent = (current_entries / self.cache_config["max_entries"]) * 100
                size_used_percent = (current_size_mb / self.cache_config["max_size_mb"]) * 100
                
                # Determine health status
                is_healthy = (
                    capacity_used_percent < 90 and  # Not over 90% capacity
                    size_used_percent < 90 and      # Not over 90% size limit
                    current_entries >= 0            # Basic sanity check
                )
                
                # Check for expired entries
                now = datetime.utcnow()
                expired_count = sum(1 for entry in self._cache_store.values() if entry.is_expired)
                
                with self._stats_lock:
                    hit_rate = self.stats.hit_rate
                    total_requests = self.stats.total_requests
            
            return {
                "overall_healthy": is_healthy,
                "service_name": "ClaudeCodeAdvancedCacheService",
                "status": "healthy" if is_healthy else "degraded",
                "metrics": {
                    "current_entries": current_entries,
                    "current_size_mb": round(current_size_mb, 2),
                    "capacity_used_percent": round(capacity_used_percent, 1),
                    "size_used_percent": round(size_used_percent, 1),
                    "expired_entries": expired_count,
                    "hit_rate_percent": round(hit_rate, 1),
                    "total_requests": total_requests
                },
                "configuration": self.cache_config,
                "cleanup_task_running": self._cleanup_task is not None and not self._cleanup_task.done(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Cache service health check failed", error=str(e))
            return {
                "overall_healthy": False,
                "service_name": "ClaudeCodeAdvancedCacheService",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def shutdown(self) -> None:
        """Shutdown cache service and cleanup resources."""
        try:
            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
            
            with self._cache_lock:
                self._cache_store.clear()
            
            logger.info("Advanced Cache Service shutdown completed")
            
        except Exception as e:
            logger.error("Error during cache service shutdown", error=str(e)) 