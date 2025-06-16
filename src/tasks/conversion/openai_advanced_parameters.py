"""
OpenAI Advanced Parameters Module

This module provides functionality to add OpenAI-specific advanced parameters
to API requests during conversion. These parameters enhance the API compatibility
and provide advanced features like frequency/presence penalties, deterministic
sampling, user tracking, and token probability adjustments.

Supported Parameters:
- frequency_penalty: Penalize frequent tokens (range: -2.0 to 2.0)
- presence_penalty: Penalize new tokens (range: -2.0 to 2.0)
- seed: Deterministic sampling (integer)
- user: User identifier for tracking (string)
- logit_bias: Token probability adjustments (dict)

Environment Variables:
- OPENAI_FREQUENCY_PENALTY: Float value for frequency penalty
- OPENAI_PRESENCE_PENALTY: Float value for presence penalty
- OPENAI_SEED: Integer value for deterministic sampling
- OPENAI_USER: String value for user identification
- OPENAI_LOGIT_BIAS: JSON string for logit bias mapping

Author: Claude Code Proxy
Date: December 2024
"""

import json
import os
from typing import Any, Dict, List, Optional, Union
from ...core.logging_config import get_logger
from ...models.instructor import ConversionResult

logger = get_logger("conversion.openai_advanced")


def add_openai_advanced_parameters(
    request_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> ConversionResult:
    """
    Add OpenAI advanced parameters to the request data.
    
    Args:
        request_data: The request data to enhance
        config: Optional configuration dict. If None, loads from environment.
        
    Returns:
        ConversionResult with success status and any warnings/errors
    """
    try:
        if config is None:
            config = get_openai_advanced_config_from_env()
        
        if not config:
            logger.debug("No OpenAI advanced parameters configured")
            return ConversionResult(
                success=True,
                converted_data=request_data,
                warnings=["No OpenAI advanced parameters configured"]
            )
        
        # Validate configuration
        validation_result = validate_openai_advanced_config(config)
        if not validation_result.success:
            logger.warning("OpenAI advanced config validation failed", 
                         errors=validation_result.errors)
            return validation_result
        
        # Add parameters to request
        enhanced_data = request_data.copy()
        
        # Add frequency penalty
        if "frequency_penalty" in config:
            enhanced_data["frequency_penalty"] = config["frequency_penalty"]
            logger.debug("Added frequency_penalty", value=config["frequency_penalty"])
        
        # Add presence penalty
        if "presence_penalty" in config:
            enhanced_data["presence_penalty"] = config["presence_penalty"]
            logger.debug("Added presence_penalty", value=config["presence_penalty"])
        
        # Add seed for deterministic sampling
        if "seed" in config:
            enhanced_data["seed"] = config["seed"]
            logger.debug("Added seed", value=config["seed"])
        
        # Add user identifier
        if "user" in config:
            enhanced_data["user"] = config["user"]
            logger.debug("Added user", value=config["user"])
        
        # Add logit bias
        if "logit_bias" in config:
            enhanced_data["logit_bias"] = config["logit_bias"]
            logger.debug("Added logit_bias", 
                        token_count=len(config["logit_bias"]))
        
        logger.info("Successfully added OpenAI advanced parameters",
                   parameters_added=len([k for k in config.keys() if k in enhanced_data]))
        
        return ConversionResult(
            success=True,
            converted_data=enhanced_data,
            warnings=validation_result.warnings
        )
        
    except Exception as e:
        logger.error("Failed to add OpenAI advanced parameters", error=str(e))
        return ConversionResult(
            success=False,
            converted_data=request_data,
            errors=[f"Failed to add OpenAI advanced parameters: {str(e)}"]
        )


def get_openai_advanced_config_from_env() -> Dict[str, Any]:
    """
    Get OpenAI advanced parameters configuration from environment variables.
    
    Environment Variables:
    - OPENAI_FREQUENCY_PENALTY: Float (-2.0 to 2.0)
    - OPENAI_PRESENCE_PENALTY: Float (-2.0 to 2.0)
    - OPENAI_SEED: Integer for deterministic sampling
    - OPENAI_USER: String for user identification
    - OPENAI_LOGIT_BIAS: JSON string for token bias mapping
    
    Returns:
        Dictionary with configured parameters
    """
    config = {}
    
    try:
        # Frequency penalty
        if freq_penalty := os.getenv("OPENAI_FREQUENCY_PENALTY"):
            try:
                config["frequency_penalty"] = float(freq_penalty)
            except ValueError:
                logger.warning("Invalid OPENAI_FREQUENCY_PENALTY value", 
                             value=freq_penalty)
        
        # Presence penalty
        if pres_penalty := os.getenv("OPENAI_PRESENCE_PENALTY"):
            try:
                config["presence_penalty"] = float(pres_penalty)
            except ValueError:
                logger.warning("Invalid OPENAI_PRESENCE_PENALTY value", 
                             value=pres_penalty)
        
        # Seed
        if seed := os.getenv("OPENAI_SEED"):
            try:
                config["seed"] = int(seed)
            except ValueError:
                logger.warning("Invalid OPENAI_SEED value", value=seed)
        
        # User identifier
        if user := os.getenv("OPENAI_USER"):
            config["user"] = user.strip()
        
        # Logit bias
        if logit_bias := os.getenv("OPENAI_LOGIT_BIAS"):
            try:
                config["logit_bias"] = json.loads(logit_bias)
            except json.JSONDecodeError:
                logger.warning("Invalid OPENAI_LOGIT_BIAS JSON", value=logit_bias)
        
        logger.debug("Loaded OpenAI advanced config from environment",
                    parameters=list(config.keys()))
        
    except Exception as e:
        logger.error("Error loading OpenAI advanced config from environment", 
                    error=str(e))
    
    return config


def validate_openai_advanced_config(config: Dict[str, Any]) -> ConversionResult:
    """
    Validate OpenAI advanced parameters configuration.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        ConversionResult with validation status and any errors/warnings
    """
    errors = []
    warnings = []
    
    try:
        # Validate frequency penalty
        if "frequency_penalty" in config:
            freq_penalty = config["frequency_penalty"]
            if not isinstance(freq_penalty, (int, float)):
                errors.append("frequency_penalty must be a number")
            elif not -2.0 <= freq_penalty <= 2.0:
                errors.append("frequency_penalty must be between -2.0 and 2.0")
        
        # Validate presence penalty
        if "presence_penalty" in config:
            pres_penalty = config["presence_penalty"]
            if not isinstance(pres_penalty, (int, float)):
                errors.append("presence_penalty must be a number")
            elif not -2.0 <= pres_penalty <= 2.0:
                errors.append("presence_penalty must be between -2.0 and 2.0")
        
        # Validate seed
        if "seed" in config:
            seed = config["seed"]
            if not isinstance(seed, int):
                errors.append("seed must be an integer")
            elif seed < 0:
                warnings.append("seed should typically be a positive integer")
        
        # Validate user
        if "user" in config:
            user = config["user"]
            if not isinstance(user, str):
                errors.append("user must be a string")
            elif not user.strip():
                warnings.append("user identifier is empty")
            elif len(user) > 256:
                warnings.append("user identifier is very long (>256 chars)")
        
        # Validate logit bias
        if "logit_bias" in config:
            logit_bias = config["logit_bias"]
            if not isinstance(logit_bias, dict):
                errors.append("logit_bias must be a dictionary")
            else:
                for token_id, bias in logit_bias.items():
                    # Token IDs should be strings (representing integers)
                    try:
                        int(token_id)
                    except ValueError:
                        errors.append(f"logit_bias key '{token_id}' must be a valid token ID")
                    
                    # Bias values should be numbers
                    if not isinstance(bias, (int, float)):
                        errors.append(f"logit_bias value for token '{token_id}' must be a number")
                    elif not -100 <= bias <= 100:
                        warnings.append(f"logit_bias value {bias} for token '{token_id}' is extreme")
                
                if len(logit_bias) > 300:
                    warnings.append(f"logit_bias has many entries ({len(logit_bias)}), may impact performance")
        
        success = len(errors) == 0
        
        if success:
            logger.debug("OpenAI advanced config validation passed",
                        parameters=list(config.keys()),
                        warnings_count=len(warnings))
        else:
            logger.warning("OpenAI advanced config validation failed",
                         errors=errors, warnings=warnings)
        
        return ConversionResult(
            success=success,
            converted_data=config if success else None,
            errors=errors,
            warnings=warnings
        )
        
    except Exception as e:
        logger.error("Error validating OpenAI advanced config", error=str(e))
        return ConversionResult(
            success=False,
            converted_data=None,
            errors=[f"Validation error: {str(e)}"]
        )


def create_default_openai_advanced_config() -> Dict[str, Any]:
    """
    Create a default OpenAI advanced parameters configuration for development.
    
    Returns:
        Dictionary with sensible default values
    """
    return {
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "seed": None,  # No seed by default for non-deterministic sampling
        "user": "claude-code-proxy-user",
        "logit_bias": {}  # Empty logit bias by default
    }


def should_use_openai_advanced_parameters(
    request_data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Determine if OpenAI advanced parameters should be applied to the request.
    
    Args:
        request_data: The request data to analyze
        config: Optional configuration. If None, loads from environment.
        
    Returns:
        True if advanced parameters should be applied
    """
    try:
        if config is None:
            config = get_openai_advanced_config_from_env()
        
        # Apply if we have any configuration
        has_config = bool(config)
        
        # Check if request is going to OpenAI/LiteLLM (not back to Anthropic)
        model = request_data.get("model", "")
        is_openai_compatible = not model.startswith("anthropic/")
        
        should_apply = has_config and is_openai_compatible
        
        logger.debug("Checking if should use OpenAI advanced parameters",
                    has_config=has_config,
                    is_openai_compatible=is_openai_compatible,
                    should_apply=should_apply,
                    model=model)
        
        return should_apply
        
    except Exception as e:
        logger.error("Error checking if should use OpenAI advanced parameters", 
                    error=str(e))
        return False


def get_openai_parameter_usage_stats(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get usage statistics for OpenAI advanced parameters.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary with usage statistics
    """
    stats = {
        "total_parameters": len(config),
        "penalty_parameters": 0,
        "sampling_parameters": 0,
        "tracking_parameters": 0,
        "logit_bias_tokens": 0
    }
    
    # Count penalty parameters
    if "frequency_penalty" in config or "presence_penalty" in config:
        stats["penalty_parameters"] = sum([
            "frequency_penalty" in config,
            "presence_penalty" in config
        ])
    
    # Count sampling parameters
    if "seed" in config:
        stats["sampling_parameters"] = 1
    
    # Count tracking parameters
    if "user" in config:
        stats["tracking_parameters"] = 1
    
    # Count logit bias tokens
    if "logit_bias" in config:
        stats["logit_bias_tokens"] = len(config["logit_bias"])
    
    return stats 