"""Tests for OpenRouter extension functionality."""

import json
import os
import pytest
from unittest.mock import patch

from src.tasks.conversion.openrouter_extensions import (
    add_openrouter_extensions,
    get_openrouter_config_from_env,
    validate_openrouter_config,
    create_default_openrouter_config,
    get_openrouter_models_for_fallback,
    should_use_openrouter_extensions
)


class TestOpenRouterExtensions:
    """Test OpenRouter extension functionality."""
    
    def test_add_openrouter_extensions_basic(self):
        """Test basic OpenRouter extension addition."""
        base_request = {
            "model": "anthropic/claude-3-5-sonnet",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 100
        }
        
        config = {
            "fallback_models": ["anthropic/claude-3.7-sonnet", "anthropic/claude-3-haiku"],
            "routing_strategy": "fallback"
        }
        
        result = add_openrouter_extensions(base_request, config)
        
        # Should contain original parameters
        assert result["model"] == "anthropic/claude-3-5-sonnet"
        assert result["messages"] == [{"role": "user", "content": "Hello"}]
        assert result["max_tokens"] == 100
        
        # Should contain OpenRouter extensions
        assert result["models"] == ["anthropic/claude-3.7-sonnet", "anthropic/claude-3-haiku"]
        assert result["route"] == "fallback"
    
    def test_add_openrouter_extensions_provider_preferences(self):
        """Test OpenRouter provider preferences addition."""
        base_request = {"model": "anthropic/claude-3-5-sonnet"}
        
        config = {
            "provider_preferences": {
                "allow_fallbacks": True,
                "require_parameters": False,
                "data_collection": "allow"
            }
        }
        
        result = add_openrouter_extensions(base_request, config)
        
        assert result["provider"] == {
            "allow_fallbacks": True,
            "require_parameters": False,
            "data_collection": "allow"
        }
    
    def test_add_openrouter_extensions_advanced_sampling(self):
        """Test OpenRouter advanced sampling parameters."""
        base_request = {"model": "anthropic/claude-3-5-sonnet"}
        
        config = {
            "min_p": 0.1,
            "top_a": 0.5,
            "transforms": ["trim", "normalize"]
        }
        
        result = add_openrouter_extensions(base_request, config)
        
        assert result["min_p"] == 0.1
        assert result["top_a"] == 0.5
        assert result["transforms"] == ["trim", "normalize"]


class TestOpenRouterConfigFromEnv:
    """Test OpenRouter configuration from environment variables."""
    
    def test_get_openrouter_config_from_env_complete(self):
        """Test complete OpenRouter configuration from environment."""
        env_vars = {
            "OPENROUTER_FALLBACK_MODELS": "anthropic/claude-3.7-sonnet,anthropic/claude-3-haiku",
            "OPENROUTER_ROUTING_STRATEGY": "fallback",
            "OPENROUTER_PROVIDER_PREFERENCES": '{"allow_fallbacks": true, "data_collection": "allow"}',
            "OPENROUTER_TRANSFORMS": "trim,normalize,filter",
            "OPENROUTER_MIN_P": "0.1",
            "OPENROUTER_TOP_A": "0.5"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = get_openrouter_config_from_env()
            
            assert config["fallback_models"] == ["anthropic/claude-3.7-sonnet", "anthropic/claude-3-haiku"]
            assert config["routing_strategy"] == "fallback"
            assert config["provider_preferences"] == {"allow_fallbacks": True, "data_collection": "allow"}
            assert config["transforms"] == ["trim", "normalize", "filter"]
            assert config["min_p"] == 0.1
            assert config["top_a"] == 0.5


class TestOpenRouterUtilities:
    """Test OpenRouter utility functions."""
    
    def test_create_default_openrouter_config(self):
        """Test creation of default OpenRouter configuration."""
        config = create_default_openrouter_config()
        
        assert config["routing_strategy"] == "fallback"
        assert config["provider_preferences"]["allow_fallbacks"] is True
        assert config["provider_preferences"]["require_parameters"] is False
        assert config["provider_preferences"]["data_collection"] == "allow"
    
    def test_should_use_openrouter_extensions_with_env_vars(self):
        """Test detection of OpenRouter extensions based on environment variables."""
        # Test with one extension variable set
        with patch.dict(os.environ, {"OPENROUTER_FALLBACK_MODELS": "model1,model2"}, clear=True):
            assert should_use_openrouter_extensions() is True
        
        # Test with no extension variables set
        with patch.dict(os.environ, {}, clear=True):
            assert should_use_openrouter_extensions() is False
