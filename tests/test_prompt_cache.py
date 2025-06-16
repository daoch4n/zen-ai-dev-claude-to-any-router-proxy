"""Tests for Prompt Caching functionality."""

import pytest
import os
import time
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta

from src.tasks.conversion.prompt_caching_tasks import (
    CacheEntry,
    CacheStats,
    PromptCacheManager,
    generate_prompt_cache_key,
    get_cached_prompt_response,
    cache_prompt_response,
    get_prompt_cache_stats
)
from src.models.instructor import ConversionResult


class TestCacheEntry:
    """Test CacheEntry functionality."""
    
    def test_cache_entry_not_expired(self):
        """Test cache entry that is not expired."""
        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            cache_key="test-key",
            cached_data={},
            created_at=now,
            accessed_at=now,
            access_count=0,
            ttl_seconds=3600
        )
        
        assert not entry.is_expired()
    
    def test_cache_entry_expired(self):
        """Test cache entry that is expired."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        entry = CacheEntry(
            cache_key="test-key",
            cached_data={},
            created_at=old_time,
            accessed_at=old_time,
            access_count=0,
            ttl_seconds=3600
        )
        
        assert entry.is_expired()


class TestPromptCacheManager:
    """Test PromptCacheManager class."""
    
    def test_cache_manager_initialization(self):
        """Test cache manager initialization."""
        manager = PromptCacheManager()
        
        assert manager.enabled is True
        assert manager.ttl_seconds == 3600
    
    def test_generate_cache_key_consistent(self):
        """Test cache key generation consistency."""
        manager = PromptCacheManager()
        
        key1 = manager.generate_cache_key("Hello", "gpt-4", {"temp": 0.5})
        key2 = manager.generate_cache_key("Hello", "gpt-4", {"temp": 0.5})
        
        assert key1 == key2
        assert len(key1) == 64
    
    def test_cache_store_and_retrieve(self):
        """Test storing and retrieving cached data."""
        manager = PromptCacheManager()
        cache_key = "test-key"
        test_data = {"response": "Hello"}
        
        # Store data
        success = manager.store_response(cache_key, test_data)
        assert success is True
        
        # Retrieve data
        result = manager.get_cached_response(cache_key)
        assert result == test_data


class TestPromptCachingFunctions:
    """Test high-level caching functions."""
    
    def setup_method(self):
        """Setup method run before each test."""
        # Clear global cache manager
        import src.tasks.conversion.prompt_caching_tasks as caching_module
        caching_module._cache_manager = None
    
    def test_cache_prompt_response(self):
        """Test caching a prompt response."""
        cache_key = "test-key"
        response_data = {"response": "Hello"}
        
        result = cache_prompt_response(cache_key, response_data)
        
        assert result.success is True
        assert result.converted_data == response_data
    
    def test_get_cached_response_hit(self):
        """Test getting cached response (hit)."""
        cache_key = "test-key"
        response_data = {"response": "Hello"}
        
        # Cache response
        cache_prompt_response(cache_key, response_data)
        
        # Retrieve it
        result = get_cached_prompt_response(cache_key)
        
        assert result is not None
        assert result.success is True
        assert result.converted_data == response_data
    
    def test_get_cached_response_miss(self):
        """Test getting cached response (miss)."""
        result = get_cached_prompt_response("nonexistent-key")
        assert result is None
    
    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        stats = get_prompt_cache_stats()
        
        assert "cache_enabled" in stats
        assert "total_requests" in stats 