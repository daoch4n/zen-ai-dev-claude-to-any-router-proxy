"""Tests for OpenAI advanced parameters functionality."""

import json
import os
import pytest
from unittest.mock import patch
from typing import Dict, Any

from src.tasks.conversion.openai_advanced_parameters import (
    add_openai_advanced_parameters,
    get_openai_advanced_config_from_env,
    validate_openai_advanced_config,
    create_default_openai_advanced_config,
    should_use_openai_advanced_parameters,
    get_openai_parameter_usage_stats
)


class TestOpenAIAdvancedParameters:
    """Test OpenAI advanced parameters functionality."""
    
    def test_add_openai_advanced_parameters_basic(self):
        """Test basic OpenAI advanced parameter addition."""
        base_request = {
            "model": "openrouter/anthropic/claude-3-5-sonnet",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 100
        }
        
        config = {
            "frequency_penalty": 0.5,
            "presence_penalty": 0.3,
            "seed": 12345
        }
        
        result = add_openai_advanced_parameters(base_request, config)
        
        assert result.success is True
        assert result.converted_data["model"] == "openrouter/anthropic/claude-3-5-sonnet"
        assert result.converted_data["messages"] == [{"role": "user", "content": "Hello"}]
        assert result.converted_data["max_tokens"] == 100
        
        # Should contain OpenAI advanced parameters
        assert result.converted_data["frequency_penalty"] == 0.5
        assert result.converted_data["presence_penalty"] == 0.3
        assert result.converted_data["seed"] == 12345
    
    def test_add_openai_advanced_parameters_user_and_logit_bias(self):
        """Test OpenAI user identifier and logit bias parameters."""
        base_request = {"model": "openrouter/anthropic/claude-3-5-sonnet"}
        
        config = {
            "user": "test-user-123",
            "logit_bias": {"50256": -100, "198": 2.5}
        }
        
        result = add_openai_advanced_parameters(base_request, config)
        
        assert result.success is True
        assert result.converted_data["user"] == "test-user-123"
        assert result.converted_data["logit_bias"] == {"50256": -100, "198": 2.5}
    
    def test_add_openai_advanced_parameters_all_parameters(self):
        """Test all OpenAI advanced parameters together."""
        base_request = {"model": "openrouter/anthropic/claude-3-5-sonnet"}
        
        config = {
            "frequency_penalty": 1.0,
            "presence_penalty": -0.5,
            "seed": 42,
            "user": "comprehensive-test",
            "logit_bias": {"100": 10, "200": -5}
        }
        
        result = add_openai_advanced_parameters(base_request, config)
        
        assert result.success is True
        assert result.converted_data["frequency_penalty"] == 1.0
        assert result.converted_data["presence_penalty"] == -0.5
        assert result.converted_data["seed"] == 42
        assert result.converted_data["user"] == "comprehensive-test"
        assert result.converted_data["logit_bias"] == {"100": 10, "200": -5}
    
    def test_add_openai_advanced_parameters_empty_config(self):
        """Test parameter addition with empty config."""
        base_request = {"model": "openrouter/anthropic/claude-3-5-sonnet"}
        
        result = add_openai_advanced_parameters(base_request, {})
        
        # Should return success with warning about no config
        assert result.success is True
        assert result.converted_data == base_request
        assert "No OpenAI advanced parameters configured" in result.warnings
    
    def test_add_openai_advanced_parameters_validation_failure(self):
        """Test parameter addition with invalid config."""
        base_request = {"model": "openrouter/anthropic/claude-3-5-sonnet"}
        
        # Invalid frequency penalty (out of range)
        config = {"frequency_penalty": 5.0}
        
        result = add_openai_advanced_parameters(base_request, config)
        
        assert result.success is False
        assert "frequency_penalty must be between -2.0 and 2.0" in result.errors


class TestOpenAIAdvancedConfigFromEnv:
    """Test OpenAI advanced parameters configuration from environment variables."""
    
    def test_get_openai_advanced_config_from_env_complete(self):
        """Test complete OpenAI advanced configuration from environment."""
        env_vars = {
            "OPENAI_FREQUENCY_PENALTY": "0.5",
            "OPENAI_PRESENCE_PENALTY": "-0.3",
            "OPENAI_SEED": "12345",
            "OPENAI_USER": "test-user",
            "OPENAI_LOGIT_BIAS": '{"50256": -100, "198": 2.5}'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = get_openai_advanced_config_from_env()
            
            assert config["frequency_penalty"] == 0.5
            assert config["presence_penalty"] == -0.3
            assert config["seed"] == 12345
            assert config["user"] == "test-user"
            assert config["logit_bias"] == {"50256": -100, "198": 2.5}
    
    def test_get_openai_advanced_config_from_env_partial(self):
        """Test partial OpenAI advanced configuration from environment."""
        env_vars = {
            "OPENAI_FREQUENCY_PENALTY": "1.0",
            "OPENAI_USER": "partial-user"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = get_openai_advanced_config_from_env()
            
            assert config["frequency_penalty"] == 1.0
            assert config["user"] == "partial-user"
            assert "presence_penalty" not in config
            assert "seed" not in config
            assert "logit_bias" not in config
    
    def test_get_openai_advanced_config_from_env_empty(self):
        """Test OpenAI advanced configuration with no environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_openai_advanced_config_from_env()
            assert config == {}
    
    def test_get_openai_advanced_config_invalid_values(self):
        """Test handling of invalid values in environment variables."""
        env_vars = {
            "OPENAI_FREQUENCY_PENALTY": "not_a_number",
            "OPENAI_SEED": "not_an_integer",
            "OPENAI_LOGIT_BIAS": "invalid json"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = get_openai_advanced_config_from_env()
            # Should not include invalid fields
            assert "frequency_penalty" not in config
            assert "seed" not in config
            assert "logit_bias" not in config


class TestOpenAIAdvancedConfigValidation:
    """Test OpenAI advanced parameters configuration validation."""
    
    def test_validate_openai_advanced_config_valid(self):
        """Test validation of valid OpenAI advanced configuration."""
        valid_config = {
            "frequency_penalty": 0.5,
            "presence_penalty": -0.3,
            "seed": 12345,
            "user": "test-user",
            "logit_bias": {"50256": -100, "198": 2.5}
        }
        
        result = validate_openai_advanced_config(valid_config)
        
        assert result.success is True
        assert result.converted_data == valid_config
        assert len(result.errors) == 0
    
    def test_validate_openai_advanced_config_invalid_penalties(self):
        """Test validation with invalid penalty values."""
        invalid_configs = [
            {"frequency_penalty": -3.0},  # Below -2.0
            {"frequency_penalty": 3.0},   # Above 2.0
            {"presence_penalty": -2.5},   # Below -2.0
            {"presence_penalty": 2.5},    # Above 2.0
            {"frequency_penalty": "not_a_number"}  # Not a number
        ]
        
        for invalid_config in invalid_configs:
            result = validate_openai_advanced_config(invalid_config)
            assert result.success is False
            assert len(result.errors) > 0
    
    def test_validate_openai_advanced_config_invalid_seed(self):
        """Test validation with invalid seed values."""
        invalid_configs = [
            {"seed": "not_an_integer"},
            {"seed": 3.14},  # Float instead of int
        ]
        
        for invalid_config in invalid_configs:
            result = validate_openai_advanced_config(invalid_config)
            assert result.success is False
            assert "seed must be an integer" in result.errors
    
    def test_validate_openai_advanced_config_invalid_user(self):
        """Test validation with invalid user values."""
        invalid_configs = [
            {"user": 123},  # Not a string
            {"user": ""},   # Empty string (warning)
            {"user": "x" * 300}  # Very long string (warning)
        ]
        
        # Non-string user should fail
        result = validate_openai_advanced_config({"user": 123})
        assert result.success is False
        assert "user must be a string" in result.errors
        
        # Empty user should succeed with warning
        result = validate_openai_advanced_config({"user": ""})
        assert result.success is True
        assert any("empty" in warning for warning in result.warnings)
        
        # Long user should succeed with warning
        result = validate_openai_advanced_config({"user": "x" * 300})
        assert result.success is True
        assert any("very long" in warning for warning in result.warnings)
    
    def test_validate_openai_advanced_config_invalid_logit_bias(self):
        """Test validation with invalid logit bias values."""
        invalid_configs = [
            {"logit_bias": "not_a_dict"},
            {"logit_bias": {"invalid_token": 1.0}},  # Non-numeric token ID
            {"logit_bias": {"123": "not_a_number"}},  # Non-numeric bias value
        ]
        
        for invalid_config in invalid_configs:
            result = validate_openai_advanced_config(invalid_config)
            assert result.success is False
            assert len(result.errors) > 0


class TestOpenAIAdvancedUtilities:
    """Test OpenAI advanced parameters utility functions."""
    
    def test_create_default_openai_advanced_config(self):
        """Test creation of default OpenAI advanced configuration."""
        config = create_default_openai_advanced_config()
        
        assert config["frequency_penalty"] == 0.0
        assert config["presence_penalty"] == 0.0
        assert config["seed"] is None
        assert config["user"] == "claude-code-proxy-user"
        assert config["logit_bias"] == {}
    
    def test_should_use_openai_advanced_parameters_with_config(self):
        """Test decision logic for using OpenAI advanced parameters."""
        # Test with OpenAI-compatible model and config
        request_data = {"model": "openrouter/anthropic/claude-3-5-sonnet"}
        config = {"frequency_penalty": 0.5}
        
        result = should_use_openai_advanced_parameters(request_data, config)
        assert result is True
        
        # Test with Anthropic model (should not apply)
        request_data = {"model": "anthropic/claude-3-5-sonnet"}
        result = should_use_openai_advanced_parameters(request_data, config)
        assert result is False
        
        # Test with no config
        result = should_use_openai_advanced_parameters(request_data, {})
        assert result is False
    
    def test_get_openai_parameter_usage_stats(self):
        """Test usage statistics calculation."""
        config = {
            "frequency_penalty": 0.5,
            "presence_penalty": 0.3,
            "seed": 12345,
            "user": "test-user",
            "logit_bias": {"100": 1.0, "200": -1.0}
        }
        
        stats = get_openai_parameter_usage_stats(config)
        
        assert stats["total_parameters"] == 5
        assert stats["penalty_parameters"] == 2
        assert stats["sampling_parameters"] == 1
        assert stats["tracking_parameters"] == 1
        assert stats["logit_bias_tokens"] == 2


class TestOpenAIAdvancedIntegration:
    """Test OpenAI advanced parameters in integration scenarios."""
    
    def test_full_integration_scenario(self):
        """Test complete integration scenario with all OpenAI advanced parameters."""
        base_request = {
            "model": "openrouter/anthropic/claude-3-5-sonnet",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        # Complete configuration
        config = {
            "frequency_penalty": 0.5,
            "presence_penalty": 0.3,
            "seed": 42,
            "user": "integration-test",
            "logit_bias": {"50256": -100, "198": 2.5}
        }
        
        # Validate configuration first
        validation_result = validate_openai_advanced_config(config)
        assert validation_result.success is True
        
        # Apply advanced parameters
        result = add_openai_advanced_parameters(base_request, config)
        
        # Verify all original parameters preserved
        assert result.converted_data["model"] == "openrouter/anthropic/claude-3-5-sonnet"
        assert result.converted_data["messages"] == [{"role": "user", "content": "Hello"}]
        assert result.converted_data["max_tokens"] == 100
        assert result.converted_data["temperature"] == 0.7
        
        # Verify all OpenAI advanced parameters added
        assert result.converted_data["frequency_penalty"] == 0.5
        assert result.converted_data["presence_penalty"] == 0.3
        assert result.converted_data["seed"] == 42
        assert result.converted_data["user"] == "integration-test"
        assert result.converted_data["logit_bias"] == {"50256": -100, "198": 2.5}
    
    def test_environment_based_integration(self):
        """Test integration using environment variables."""
        base_request = {
            "model": "openrouter/anthropic/claude-3-5-sonnet",
            "messages": [{"role": "user", "content": "Test"}]
        }
        
        env_vars = {
            "OPENAI_FREQUENCY_PENALTY": "0.8",
            "OPENAI_SEED": "999",
            "OPENAI_USER": "env-test-user"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            # Get config from environment
            config = get_openai_advanced_config_from_env()
            
            # Apply advanced parameters
            result = add_openai_advanced_parameters(base_request, config)
            
            assert result.success is True
            assert result.converted_data["frequency_penalty"] == 0.8
            assert result.converted_data["seed"] == 999
            assert result.converted_data["user"] == "env-test-user"
    
    def test_graceful_degradation(self):
        """Test graceful degradation when OpenAI advanced parameters fail."""
        base_request = {"model": "openrouter/anthropic/claude-3-5-sonnet"}
        
        # Test with None config (should succeed with no changes)
        result = add_openai_advanced_parameters(base_request, None)
        assert result.success is True
        assert result.converted_data == base_request 