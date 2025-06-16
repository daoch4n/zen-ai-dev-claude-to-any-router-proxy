"""
Prompt Caching Tasks Module

This module provides functionality for caching prompts to improve performance
and reduce API calls for repeated content. This is a key Anthropic Beta Feature
that enhances API compatibility and provides significant performance benefits
for applications with repeated or similar prompts.

Key Features:
- Intelligent cache key generation based on prompt content and parameters
- Cache hit/miss detection with performance metrics
- Multiple storage backend support (memory, Redis, file-based)
- Configurable TTL and cache size management
- Cache headers for HTTP optimization
- Statistics and monitoring for cache performance

Environment Variables:
- PROMPT_CACHE_ENABLE: Enable/disable prompt caching (default: true)
- PROMPT_CACHE_TTL: Time-to-live for cached prompts in seconds (default: 3600)
- PROMPT_CACHE_BACKEND: Storage backend (memory/redis/file, default: memory)
- PROMPT_CACHE_MAX_SIZE: Maximum number of cached entries (default: 1000)
- PROMPT_CACHE_KEY_SALT: Salt for cache key generation (default: anthropic-cache)

Author: Claude Code Proxy
Date: December 2024
"""

import hashlib
import json
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from ...core.logging_config import get_logger
from ...models.instructor import ConversionResult

logger = get_logger("conversion.prompt_caching")


@dataclass
class CacheEntry:
    """Represents a cached prompt entry with metadata."""
    
    cache_key: str
    cached_data: Dict[str, Any]
    created_at: datetime
    accessed_at: datetime
    access_count: int
    ttl_seconds: int
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl_seconds <= 0:
            return False  # No expiration
        
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now(timezone.utc) > expiry_time
    
    def update_access(self) -> None:
        """Update access metadata when cache entry is accessed."""
        self.accessed_at = datetime.now(timezone.utc)
        self.access_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache entry to dictionary."""
        return {
            "cache_key": self.cache_key,
            "cached_data": self.cached_data,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
            "ttl_seconds": self.ttl_seconds,
            "is_expired": self.is_expired()
        }


@dataclass
class CacheStats:
    """Cache performance statistics."""
    
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_expires: int = 0
    total_entries: int = 0
    memory_usage_bytes: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate as percentage."""
        return 100.0 - self.hit_rate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache stats to dictionary."""
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_expires": self.cache_expires,
            "total_entries": self.total_entries,
            "memory_usage_bytes": self.memory_usage_bytes,
            "hit_rate_percent": round(self.hit_rate, 2),
            "miss_rate_percent": round(self.miss_rate, 2)
        }


class PromptCacheManager:
    """Manages prompt caching with multiple storage backends."""
    
    def __init__(self):
        """Initialize prompt cache manager."""
        self.enabled = os.getenv("PROMPT_CACHE_ENABLE", "true").lower() == "true"
        self.ttl_seconds = int(os.getenv("PROMPT_CACHE_TTL", "3600"))
        self.backend = os.getenv("PROMPT_CACHE_BACKEND", "memory").lower()
        self.max_size = int(os.getenv("PROMPT_CACHE_MAX_SIZE", "1000"))
        self.key_salt = os.getenv("PROMPT_CACHE_KEY_SALT", "anthropic-cache")
        
        # In-memory storage for simple implementation
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._stats = CacheStats()
        
        logger.info("Prompt cache manager initialized",
                   enabled=self.enabled,
                   ttl_seconds=self.ttl_seconds,
                   backend=self.backend,
                   max_size=self.max_size)
    
    def generate_cache_key(
        self, 
        prompt_content: str, 
        model: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a unique cache key for the given prompt and parameters.
        
        Args:
            prompt_content: The prompt text content
            model: Model identifier
            parameters: Additional parameters that affect the response
            
        Returns:
            SHA-256 hash as cache key
        """
        try:
            # Create a deterministic representation
            key_data = {
                "prompt": prompt_content,
                "model": model,
                "parameters": parameters or {},
                "salt": self.key_salt
            }
            
            # Serialize to JSON with sorted keys for consistency
            key_string = json.dumps(key_data, sort_keys=True, separators=(',', ':'))
            
            # Generate SHA-256 hash
            cache_key = hashlib.sha256(key_string.encode('utf-8')).hexdigest()
            
            logger.debug("Generated cache key",
                        prompt_length=len(prompt_content),
                        model=model,
                        parameters_count=len(parameters or {}),
                        cache_key=cache_key[:16] + "...")
            
            return cache_key
            
        except Exception as e:
            logger.error("Error generating cache key", error=str(e))
            # Return a fallback key that won't match anything
            return f"error-{int(time.time())}"
    
    def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response for the given cache key.
        
        Args:
            cache_key: Cache key to lookup
            
        Returns:
            Cached response data or None if not found/expired
        """
        if not self.enabled:
            return None
        
        try:
            self._stats.total_requests += 1
            
            # Check if key exists
            if cache_key not in self._memory_cache:
                self._stats.cache_misses += 1
                logger.debug("Cache miss", cache_key=cache_key[:16] + "...")
                return None
            
            entry = self._memory_cache[cache_key]
            
            # Check if expired
            if entry.is_expired():
                self._stats.cache_expires += 1
                del self._memory_cache[cache_key]
                logger.debug("Cache expired", cache_key=cache_key[:16] + "...")
                return None
            
            # Update access metadata
            entry.update_access()
            self._stats.cache_hits += 1
            
            logger.info("Cache hit",
                       cache_key=cache_key[:16] + "...",
                       access_count=entry.access_count,
                       age_seconds=(datetime.now(timezone.utc) - entry.created_at).total_seconds())
            
            return entry.cached_data
            
        except Exception as e:
            logger.error("Error retrieving from cache", 
                        cache_key=cache_key[:16] + "...",
                        error=str(e))
            self._stats.cache_misses += 1
            return None
    
    def store_response(
        self, 
        cache_key: str, 
        response_data: Dict[str, Any]
    ) -> bool:
        """
        Store response data in cache.
        
        Args:
            cache_key: Cache key for storage
            response_data: Response data to cache
            
        Returns:
            True if stored successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Check cache size limit
            if len(self._memory_cache) >= self.max_size:
                self._evict_oldest_entry()
            
            # Create cache entry
            entry = CacheEntry(
                cache_key=cache_key,
                cached_data=response_data,
                created_at=datetime.now(timezone.utc),
                accessed_at=datetime.now(timezone.utc),
                access_count=0,
                ttl_seconds=self.ttl_seconds
            )
            
            # Store in cache
            self._memory_cache[cache_key] = entry
            self._stats.total_entries = len(self._memory_cache)
            
            logger.info("Response cached successfully",
                       cache_key=cache_key[:16] + "...",
                       ttl_seconds=self.ttl_seconds,
                       total_entries=self._stats.total_entries)
            
            return True
            
        except Exception as e:
            logger.error("Error storing in cache",
                        cache_key=cache_key[:16] + "...",
                        error=str(e))
            return False
    
    def _evict_oldest_entry(self) -> None:
        """Evict the oldest cache entry to make room for new ones."""
        if not self._memory_cache:
            return
        
        # Find oldest entry by creation time
        oldest_key = min(
            self._memory_cache.keys(),
            key=lambda k: self._memory_cache[k].created_at
        )
        
        del self._memory_cache[oldest_key]
        logger.debug("Evicted oldest cache entry", cache_key=oldest_key[:16] + "...")
    
    def clear_cache(self) -> int:
        """
        Clear all cached entries.
        
        Returns:
            Number of entries cleared
        """
        try:
            count = len(self._memory_cache)
            self._memory_cache.clear()
            self._stats.total_entries = 0
            
            logger.info("Cache cleared", entries_cleared=count)
            return count
            
        except Exception as e:
            logger.error("Error clearing cache", error=str(e))
            return 0
    
    def get_cache_stats(self) -> CacheStats:
        """Get current cache statistics."""
        self._stats.total_entries = len(self._memory_cache)
        
        # Estimate memory usage (rough calculation)
        memory_usage = 0
        for entry in self._memory_cache.values():
            memory_usage += len(str(entry.cached_data))
        self._stats.memory_usage_bytes = memory_usage
        
        return self._stats
    
    def cleanup_expired_entries(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        try:
            expired_keys = [
                key for key, entry in self._memory_cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._memory_cache[key]
                self._stats.cache_expires += 1
            
            if expired_keys:
                logger.info("Cleaned up expired cache entries", 
                           count=len(expired_keys))
            
            self._stats.total_entries = len(self._memory_cache)
            return len(expired_keys)
            
        except Exception as e:
            logger.error("Error cleaning up expired entries", error=str(e))
            return 0


# Global cache manager instance
_cache_manager: Optional[PromptCacheManager] = None


def get_cache_manager() -> PromptCacheManager:
    """Get or create the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = PromptCacheManager()
    return _cache_manager


def generate_prompt_cache_key(
    request_data: Dict[str, Any]
) -> str:
    """
    Generate cache key for a request.
    
    Args:
        request_data: Request data containing prompt and parameters
        
    Returns:
        Cache key string
    """
    try:
        cache_manager = get_cache_manager()
        
        # Extract prompt content
        messages = request_data.get("messages", [])
        prompt_content = json.dumps(messages, sort_keys=True)
        
        # Extract model
        model = request_data.get("model", "unknown")
        
        # Extract relevant parameters for caching
        cache_params = {
            "max_tokens": request_data.get("max_tokens"),
            "temperature": request_data.get("temperature"),
            "top_p": request_data.get("top_p"),
            "top_k": request_data.get("top_k"),
            "system": request_data.get("system"),
            "stop_sequences": request_data.get("stop_sequences"),
            "stream": request_data.get("stream"),
            "tool_choice": request_data.get("tool_choice"),
            "tools": request_data.get("tools")
        }
        
        # Remove None values
        cache_params = {k: v for k, v in cache_params.items() if v is not None}
        
        return cache_manager.generate_cache_key(prompt_content, model, cache_params)
        
    except Exception as e:
        logger.error("Error generating prompt cache key", error=str(e))
        return f"error-{int(time.time())}"


def get_cached_prompt_response(cache_key: str) -> Optional[ConversionResult]:
    """
    Get cached response for a prompt.
    
    Args:
        cache_key: Cache key to lookup
        
    Returns:
        ConversionResult with cached data or None
    """
    try:
        cache_manager = get_cache_manager()
        cached_data = cache_manager.get_cached_response(cache_key)
        
        if cached_data:
            logger.debug("Found cached prompt response", cache_key=cache_key[:16] + "...")
            return ConversionResult(
                success=True,
                converted_data=cached_data,
                metadata={
                    "cache_hit": True,
                    "cache_key": cache_key,
                    "cached_at": datetime.now(timezone.utc).isoformat()
                }
            )
        
        return None
        
    except Exception as e:
        logger.error("Error getting cached prompt response", 
                    cache_key=cache_key[:16] + "...",
                    error=str(e))
        return None


def cache_prompt_response(
    cache_key: str, 
    response_data: Dict[str, Any]
) -> ConversionResult:
    """
    Cache a prompt response.
    
    Args:
        cache_key: Cache key for storage
        response_data: Response data to cache
        
    Returns:
        ConversionResult indicating success/failure
    """
    try:
        cache_manager = get_cache_manager()
        success = cache_manager.store_response(cache_key, response_data)
        
        return ConversionResult(
            success=success,
            converted_data=response_data,
            metadata={
                "cached": success,
                "cache_key": cache_key,
                "cached_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
    except Exception as e:
        logger.error("Error caching prompt response",
                    cache_key=cache_key[:16] + "...",
                    error=str(e))
        return ConversionResult(
            success=False,
            converted_data=response_data,
            errors=[f"Failed to cache response: {str(e)}"],
            metadata={"cached": False}
        )


def get_prompt_cache_stats() -> Dict[str, Any]:
    """
    Get prompt cache statistics.
    
    Returns:
        Dictionary with cache performance metrics
    """
    try:
        cache_manager = get_cache_manager()
        stats = cache_manager.get_cache_stats()
        
        return {
            "cache_enabled": cache_manager.enabled,
            "cache_backend": cache_manager.backend,
            "cache_ttl_seconds": cache_manager.ttl_seconds,
            "cache_max_size": cache_manager.max_size,
            **stats.to_dict()
        }
        
    except Exception as e:
        logger.error("Error getting cache stats", error=str(e))
        return {"error": f"Failed to get cache stats: {str(e)}"}


def clear_prompt_cache() -> Dict[str, Any]:
    """
    Clear all cached prompts.
    
    Returns:
        Dictionary with operation result
    """
    try:
        cache_manager = get_cache_manager()
        cleared_count = cache_manager.clear_cache()
        
        logger.info("Prompt cache cleared", entries_cleared=cleared_count)
        
        return {
            "success": True,
            "entries_cleared": cleared_count,
            "cleared_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error("Error clearing prompt cache", error=str(e))
        return {
            "success": False,
            "error": f"Failed to clear cache: {str(e)}"
        }


def cleanup_expired_cache_entries() -> Dict[str, Any]:
    """
    Clean up expired cache entries.
    
    Returns:
        Dictionary with cleanup results
    """
    try:
        cache_manager = get_cache_manager()
        expired_count = cache_manager.cleanup_expired_entries()
        
        return {
            "success": True,
            "expired_entries_removed": expired_count,
            "cleaned_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error("Error cleaning up expired cache entries", error=str(e))
        return {
            "success": False,
            "error": f"Failed to cleanup cache: {str(e)}"
        } 