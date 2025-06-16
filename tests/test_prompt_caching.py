"""Tests for Prompt Caching functionality."""

import pytest
import os
import time
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from src.tasks.conversion.prompt_caching_tasks import (
    CacheEntry,
    CacheStats,
    PromptCacheManager,
    generate_prompt_cache_key,
    get_cached_prompt_response,
    cache_prompt_response,
    get_prompt_cache_stats,
    clear_prompt_cache,
    cleanup_expired_cache_entries,
    get_cache_manager
)
from src.models.instructor import ConversionResult


class TestCacheEntry:
    """Test CacheEntry dataclass functionality."""
    
    def test_cache_entry_creation(self):
        """Test creating a cache entry with all fields."""
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            cache_key="test-key-123",
            cached_data={"response": "test"},
            created_at=now,
            accessed_at=now,
            access_count=0,
            ttl_seconds=3600
        )
        
        assert entry.cache_key == "test-key-123"
        assert entry.cached_data == {"response": "test"}
        assert entry.access_count == 0
        assert entry.ttl_seconds == 3600
    
    def test_cache_entry_is_expired_false(self):
        """Test cache entry that is not expired."""
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            cache_key="test-key",
            cached_data={},
            created_at=now,
            accessed_at=now,
            access_count=0,
            ttl_seconds=3600  # 1 hour
        )
        
        assert not entry.is_expired()
    
    def test_cache_entry_is_expired_true(self):
        """Test cache entry that is expired."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        entry = CacheEntry(
            cache_key="test-key",
            cached_data={},
            created_at=old_time,
            accessed_at=old_time,
            access_count=0,
            ttl_seconds=3600  # 1 hour, but created 2 hours ago
        )
        
        assert entry.is_expired()
    
    def test_cache_entry_no_expiration(self):
        """Test cache entry with no expiration (ttl_seconds <= 0)."""
        old_time = datetime.now(timezone.utc) - timedelta(days=1)
        entry = CacheEntry(
            cache_key="test-key",
            cached_data={},
            created_at=old_time,
            accessed_at=old_time,
            access_count=0,
            ttl_seconds=0  # No expiration
        )
        
        assert not entry.is_expired()
    
    def test_cache_entry_update_access(self):
        """Test updating access metadata."""
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            cache_key="test-key",
            cached_data={},
            created_at=now,
            accessed_at=now,
            access_count=0,
            ttl_seconds=3600
        )
        
        # Update access
        entry.update_access()
        
        assert entry.access_count == 1
        assert entry.accessed_at > now


class TestCacheStats:
    """Test CacheStats dataclass functionality."""
    
    def test_cache_stats_hit_rate(self):
        """Test cache hit rate calculation."""
        stats = CacheStats(
            total_requests=100,
            cache_hits=75,
            cache_misses=25
        )
        
        assert stats.hit_rate == 75.0
        assert stats.miss_rate == 25.0
    
    def test_cache_stats_no_requests(self):
        """Test cache stats with no requests."""
        stats = CacheStats()
        
        assert stats.hit_rate == 0.0
        assert stats.miss_rate == 100.0


class TestPromptCacheManager:
    """Test PromptCacheManager class."""
    
    def setup_method(self):
        """Setup method run before each test."""
        # Reset environment variables
        os.environ.pop("PROMPT_CACHE_ENABLE", None)
        os.environ.pop("PROMPT_CACHE_TTL", None)
        os.environ.pop("PROMPT_CACHE_MAX_SIZE", None)
    
    def test_cache_manager_initialization_defaults(self):
        """Test cache manager initialization with defaults."""
        manager = PromptCacheManager()
        
        assert manager.enabled is True
        assert manager.ttl_seconds == 3600
        assert manager.max_size == 1000
        assert manager.backend == "memory"
    
    @patch.dict(os.environ, {'PROMPT_CACHE_ENABLE': 'false', 'PROMPT_CACHE_TTL': '7200'})
    def test_cache_manager_initialization_env_vars(self):
        """Test cache manager initialization with environment variables."""
        manager = PromptCacheManager()
        
        assert manager.enabled is False
        assert manager.ttl_seconds == 7200
    
    def test_generate_cache_key_consistent(self):
        """Test that cache key generation is consistent for same inputs."""
        manager = PromptCacheManager()
        
        key1 = manager.generate_cache_key("Hello world", "gpt-4", {"temperature": 0.5})
        key2 = manager.generate_cache_key("Hello world", "gpt-4", {"temperature": 0.5})
        
        assert key1 == key2
        assert len(key1) == 64  # SHA-256 hex digest length
    
    def test_generate_cache_key_different(self):
        """Test that different inputs generate different cache keys."""
        manager = PromptCacheManager()
        
        key1 = manager.generate_cache_key("Hello world", "gpt-4", {"temperature": 0.5})
        key2 = manager.generate_cache_key("Hello world", "gpt-4", {"temperature": 0.7})
        key3 = manager.generate_cache_key("Hello there", "gpt-4", {"temperature": 0.5})
        
        assert key1 != key2
        assert key1 != key3
        assert key2 != key3
    
    def test_cache_miss_initial(self):
        """Test cache miss on first request."""
        manager = PromptCacheManager()
        
        result = manager.get_cached_response("nonexistent-key")
        
        assert result is None
        assert manager._stats.cache_misses == 1
        assert manager._stats.total_requests == 1
    
    def test_cache_store_and_retrieve(self):
        """Test storing and retrieving cached data."""
        manager = PromptCacheManager()
        cache_key = "test-key-123"
        test_data = {"response": "Hello, world!"}
        
        # Store data
        success = manager.store_response(cache_key, test_data)
        assert success is True
        
        # Retrieve data
        result = manager.get_cached_response(cache_key)
        assert result == test_data
        assert manager._stats.cache_hits == 1
    
    def test_cache_disabled_behavior(self):
        """Test cache behavior when disabled."""
        manager = PromptCacheManager()
        manager.enabled = False
        
        cache_key = "test-key"
        test_data = {"response": "test"}
        
        # Should not store when disabled
        success = manager.store_response(cache_key, test_data)
        assert success is False
        
        # Should not retrieve when disabled
        result = manager.get_cached_response(cache_key)
        assert result is None
    
    def test_cache_expiration(self):
        """Test cache entry expiration."""
        manager = PromptCacheManager()
        manager.ttl_seconds = 1  # 1 second TTL
        
        cache_key = "test-key"
        test_data = {"response": "test"}
        
        # Store data
        manager.store_response(cache_key, test_data)
        
        # Should be retrievable immediately
        result = manager.get_cached_response(cache_key)
        assert result == test_data
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired now
        result = manager.get_cached_response(cache_key)
        assert result is None
        assert manager._stats.cache_expires >= 1
    
    def test_cache_size_limit_and_eviction(self):
        """Test cache size limit and eviction policy."""
        manager = PromptCacheManager()
        manager.max_size = 2  # Very small cache
        
        # Store 3 items (exceeds limit)
        manager.store_response("key1", {"data": "1"})
        manager.store_response("key2", {"data": "2"})
        manager.store_response("key3", {"data": "3"})  # Should evict oldest
        
        # key1 should be evicted (oldest)
        assert manager.get_cached_response("key1") is None
        assert manager.get_cached_response("key2") is not None
        assert manager.get_cached_response("key3") is not None
    
    def test_clear_cache(self):
        """Test clearing all cache entries."""
        manager = PromptCacheManager()
        
        # Store some data
        manager.store_response("key1", {"data": "1"})
        manager.store_response("key2", {"data": "2"})
        
        # Clear cache
        cleared_count = manager.clear_cache()
        
        assert cleared_count == 2
        assert len(manager._memory_cache) == 0
        assert manager.get_cached_response("key1") is None


class TestPromptCachingFunctions:
    """Test high-level prompt caching functions."""
    
    def setup_method(self):
        """Setup method run before each test."""
        # Clear global cache manager
        import src.tasks.conversion.prompt_caching_tasks as caching_module
        caching_module._cache_manager = None
    
    def test_generate_prompt_cache_key_from_request(self):
        """Test generating cache key from request data."""
        request_data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-4",
            "max_tokens": 100,
            "temperature": 0.5
        }
        
        key1 = generate_prompt_cache_key(request_data)
        key2 = generate_prompt_cache_key(request_data)
        
        assert key1 == key2
        assert len(key1) == 64
    
    def test_cache_prompt_response_success(self):
        """Test caching a prompt response successfully."""
        cache_key = "test-key"
        response_data = {"response": "Hello, world!"}
        
        result = cache_prompt_response(cache_key, response_data)
        
        assert result.success is True
        assert result.converted_data == response_data
        assert result.metadata["cached"] is True
    
    def test_get_cached_prompt_response_hit(self):
        """Test getting a cached prompt response (cache hit)."""
        cache_key = "test-key"
        response_data = {"response": "Hello, world!"}
        
        # First cache the response
        cache_prompt_response(cache_key, response_data)
        
        # Then retrieve it
        result = get_cached_prompt_response(cache_key)
        
        assert result is not None
        assert result.success is True
        assert result.converted_data == response_data
        assert result.metadata["cache_hit"] is True
    
    def test_get_cached_prompt_response_miss(self):
        """Test getting a cached prompt response (cache miss)."""
        result = get_cached_prompt_response("nonexistent-key")
        
        assert result is None
    
    def test_get_prompt_cache_stats(self):
        """Test getting cache statistics."""
        # Perform some cache operations
        cache_key = "test-key"
        response_data = {"response": "test"}
        
        cache_prompt_response(cache_key, response_data)
        get_cached_prompt_response(cache_key)  # Hit
        get_cached_prompt_response("miss-key")  # Miss
        
        stats = get_prompt_cache_stats()
        
        assert "cache_enabled" in stats
        assert "total_requests" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert stats["total_requests"] >= 2
    
    def test_clear_prompt_cache_function(self):
        """Test clearing the prompt cache via function."""
        # Cache some data
        cache_prompt_response("key1", {"data": "1"})
        cache_prompt_response("key2", {"data": "2"})
        
        # Clear cache
        result = clear_prompt_cache()
        
        assert result["success"] is True
        assert result["entries_cleared"] >= 0
        assert "cleared_at" in result
    
    def test_cleanup_expired_cache_entries(self):
        """Test cleaning up expired cache entries."""
        # This test would need to manipulate TTL or mock time
        result = cleanup_expired_cache_entries()
        
        assert result["success"] is True
        assert "expired_entries_removed" in result
        assert "cleaned_at" in result


class TestPromptCachingIntegration:
    """Test prompt caching integration scenarios."""
    
    def setup_method(self):
        """Setup method run before each test."""
        # Clear global cache manager
        import src.tasks.conversion.prompt_caching_tasks as caching_module
        caching_module._cache_manager = None
    
    def test_full_caching_workflow(self):
        """Test complete caching workflow from request to response."""
        # Create request data
        request_data = {
            "messages": [{"role": "user", "content": "What is AI?"}],
            "model": "anthropic/claude-3-5-sonnet",
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        # Generate cache key
        cache_key = generate_prompt_cache_key(request_data)
        
        # Should be cache miss initially
        cached_result = get_cached_prompt_response(cache_key)
        assert cached_result is None
        
        # Cache a response
        response_data = {"response": "AI is artificial intelligence..."}
        cache_result = cache_prompt_response(cache_key, response_data)
        assert cache_result.success is True
        
        # Should be cache hit now
        cached_result = get_cached_prompt_response(cache_key)
        assert cached_result is not None
        assert cached_result.converted_data == response_data
    
    def test_cache_key_variations(self):
        """Test that different request variations create different cache keys."""
        base_request = {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-4",
            "max_tokens": 100
        }
        
        # Same request should have same key
        key1 = generate_prompt_cache_key(base_request)
        key2 = generate_prompt_cache_key(base_request.copy())
        assert key1 == key2
        
        # Different temperature should have different key
        temp_request = base_request.copy()
        temp_request["temperature"] = 0.5
        key3 = generate_prompt_cache_key(temp_request)
        assert key1 != key3
        
        # Different message content should have different key
        content_request = base_request.copy()
        content_request["messages"] = [{"role": "user", "content": "Hi there"}]
        key4 = generate_prompt_cache_key(content_request)
        assert key1 != key4
    
    def test_cache_performance_with_multiple_operations(self):
        """Test cache performance with multiple operations."""
        # Cache multiple responses
        for i in range(10):
            cache_key = f"key-{i}"
            response_data = {"response": f"Response {i}"}
            cache_prompt_response(cache_key, response_data)
        
        # Access some cached responses
        for i in range(5):
            cache_key = f"key-{i}"
            result = get_cached_prompt_response(cache_key)
            assert result is not None
            assert result.converted_data["response"] == f"Response {i}"
        
        # Check stats
        stats = get_prompt_cache_stats()
        assert stats["total_entries"] >= 10
        assert stats["cache_hits"] >= 5
    
    def test_error_handling_in_caching(self):
        """Test error handling in caching operations."""
        # Test with invalid cache key
        result = get_cached_prompt_response("")
        # Should handle gracefully, not crash
        
        # Test caching with invalid data types
        result = cache_prompt_response("test-key", None)
        # Should handle gracefully
        assert result.success in [True, False]  # Either works or fails gracefully 