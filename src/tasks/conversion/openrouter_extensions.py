"""OpenRouter extension tasks for advanced routing and provider features."""

import os
import json
from typing import Dict, Any, List, Optional
from ...core.logging_config import get_logger
from ...models.instructor import ConversionResult

logger = get_logger("conversion.openrouter_extensions")


def add_openrouter_extensions(
    request_data: Dict[str, Any], 
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add OpenRouter-specific parameters when configured.
    
    OpenRouter extends the OpenAI API with additional routing and provider features:
    - models: Array of fallback models for routing
    - route: Routing strategy (e.g., "fallback")
    - provider: Provider preferences and settings
    - transforms: Array of prompt transforms to apply
    - min_p: Minimum probability threshold (advanced sampling)
    - top_a: Top-a sampling parameter (advanced sampling)
    
    Args:
        request_data: Base request data to enhance
        config: OpenRouter extension configuration
        
    Returns:
        Enhanced request data with OpenRouter parameters
    """
    if not config:
        config = get_openrouter_config_from_env()
    
    enhanced_request = request_data.copy()
    extensions_added = []
    
    # Add fallback models for routing
    if config.get("fallback_models"):
        enhanced_request["models"] = config["fallback_models"]
        extensions_added.append("models")
        logger.debug("Added fallback models", models=config["fallback_models"])
    
    # Add routing strategy
    if config.get("routing_strategy"):
        enhanced_request["route"] = config["routing_strategy"]
        extensions_added.append("route")
        logger.debug("Added routing strategy", route=config["routing_strategy"])
    
    # Add provider preferences
    if config.get("provider_preferences"):
        enhanced_request["provider"] = config["provider_preferences"]
        extensions_added.append("provider")
        logger.debug("Added provider preferences", provider=config["provider_preferences"])
    
    # Add prompt transforms
    if config.get("transforms"):
        enhanced_request["transforms"] = config["transforms"]
        extensions_added.append("transforms")
        logger.debug("Added prompt transforms", transforms=config["transforms"])
    
    # Add advanced sampling parameters
    if config.get("min_p") is not None:
        enhanced_request["min_p"] = config["min_p"]
        extensions_added.append("min_p")
        logger.debug("Added min_p sampling", min_p=config["min_p"])
    
    if config.get("top_a") is not None:
        enhanced_request["top_a"] = config["top_a"]
        extensions_added.append("top_a")
        logger.debug("Added top_a sampling", top_a=config["top_a"])
    
    # Log summary of extensions added
    if extensions_added:
        logger.info("OpenRouter extensions added", 
                   extensions=extensions_added,
                   total_extensions=len(extensions_added))
    else:
        logger.debug("No OpenRouter extensions configured")
    
    return enhanced_request


def get_openrouter_config_from_env() -> Dict[str, Any]:
    """
    Get OpenRouter extension configuration from environment variables.
    
    Environment variables supported:
    - OPENROUTER_FALLBACK_MODELS: Comma-separated list of fallback models
    - OPENROUTER_ROUTING_STRATEGY: Routing strategy (e.g., "fallback")
    - OPENROUTER_PROVIDER_PREFERENCES: JSON string with provider preferences
    - OPENROUTER_TRANSFORMS: Comma-separated list of prompt transforms
    - OPENROUTER_MIN_P: Minimum probability threshold (float)
    - OPENROUTER_TOP_A: Top-a sampling parameter (float)
    
    Returns:
        Dictionary with OpenRouter configuration
    """
    config = {}
    
    # Parse fallback models
    fallback_models_str = os.getenv("OPENROUTER_FALLBACK_MODELS", "").strip()
    if fallback_models_str:
        config["fallback_models"] = [
            model.strip() for model in fallback_models_str.split(",") 
            if model.strip()
        ]
    
    # Parse routing strategy
    routing_strategy = os.getenv("OPENROUTER_ROUTING_STRATEGY", "").strip()
    if routing_strategy:
        config["routing_strategy"] = routing_strategy
    
    # Parse provider preferences (JSON format)
    provider_prefs_str = os.getenv("OPENROUTER_PROVIDER_PREFERENCES", "").strip()
    if provider_prefs_str:
        try:
            config["provider_preferences"] = json.loads(provider_prefs_str)
        except json.JSONDecodeError as e:
            logger.warning("Invalid JSON in OPENROUTER_PROVIDER_PREFERENCES", 
                          error=str(e), value=provider_prefs_str)
    
    # Parse transforms
    transforms_str = os.getenv("OPENROUTER_TRANSFORMS", "").strip()
    if transforms_str:
        config["transforms"] = [
            transform.strip() for transform in transforms_str.split(",") 
            if transform.strip()
        ]
    
    # Parse advanced sampling parameters
    min_p_str = os.getenv("OPENROUTER_MIN_P", "").strip()
    if min_p_str:
        try:
            config["min_p"] = float(min_p_str)
        except ValueError as e:
            logger.warning("Invalid float in OPENROUTER_MIN_P", 
                          error=str(e), value=min_p_str)
    
    top_a_str = os.getenv("OPENROUTER_TOP_A", "").strip()
    if top_a_str:
        try:
            config["top_a"] = float(top_a_str)
        except ValueError as e:
            logger.warning("Invalid float in OPENROUTER_TOP_A", 
                          error=str(e), value=top_a_str)
    
    return config


def validate_openrouter_config(config: Dict[str, Any]) -> ConversionResult:
    """
    Validate OpenRouter extension configuration.
    
    Args:
        config: OpenRouter configuration to validate
        
    Returns:
        ConversionResult indicating validation success/failure
    """
    errors = []
    warnings = []
    
    # Validate fallback models
    if "fallback_models" in config:
        fallback_models = config["fallback_models"]
        if not isinstance(fallback_models, list):
            errors.append("fallback_models must be a list")
        elif len(fallback_models) == 0:
            warnings.append("fallback_models is empty")
        else:
            for i, model in enumerate(fallback_models):
                if not isinstance(model, str) or not model.strip():
                    errors.append(f"fallback_models[{i}] must be a non-empty string")
    
    # Validate routing strategy
    if "routing_strategy" in config:
        route = config["routing_strategy"]
        valid_routes = ["fallback"]  # OpenRouter currently supports "fallback"
        if route not in valid_routes:
            errors.append(f"routing_strategy must be one of: {valid_routes}")
    
    # Validate provider preferences
    if "provider_preferences" in config:
        provider = config["provider_preferences"]
        if not isinstance(provider, dict):
            errors.append("provider_preferences must be a dictionary")
        else:
            # Validate known provider preference fields
            valid_fields = ["allow_fallbacks", "require_parameters", "data_collection"]
            for field in provider:
                if field not in valid_fields:
                    warnings.append(f"Unknown provider preference field: {field}")
    
    # Validate transforms
    if "transforms" in config:
        transforms = config["transforms"]
        if not isinstance(transforms, list):
            errors.append("transforms must be a list")
        else:
            for i, transform in enumerate(transforms):
                if not isinstance(transform, str) or not transform.strip():
                    errors.append(f"transforms[{i}] must be a non-empty string")
    
    # Validate sampling parameters
    if "min_p" in config:
        min_p = config["min_p"]
        if not isinstance(min_p, (int, float)) or not (0.0 <= min_p <= 1.0):
            errors.append("min_p must be a float between 0.0 and 1.0")
    
    if "top_a" in config:
        top_a = config["top_a"]
        if not isinstance(top_a, (int, float)) or not (0.0 <= top_a <= 1.0):
            errors.append("top_a must be a float between 0.0 and 1.0")
    
    # Create result
    success = len(errors) == 0
    metadata = {
        "validation_errors": errors,
        "validation_warnings": warnings,
        "config_fields_validated": list(config.keys())
    }
    
    if success:
        logger.info("OpenRouter config validation passed", **metadata)
        return ConversionResult(
            success=True,
            converted_data=config,
            metadata=metadata
        )
    else:
        logger.error("OpenRouter config validation failed", **metadata)
        return ConversionResult(
            success=False,
            errors=errors,
            metadata=metadata
        )


def create_default_openrouter_config() -> Dict[str, Any]:
    """
    Create a default OpenRouter configuration for development/testing.
    
    Returns:
        Default configuration with common OpenRouter settings
    """
    return {
        "routing_strategy": "fallback",
        "provider_preferences": {
            "allow_fallbacks": True,
            "require_parameters": False,
            "data_collection": "allow"
        }
    }


def get_openrouter_models_for_fallback(primary_model: str) -> List[str]:
    """
    Get a list of recommended fallback models for a given primary model.
    
    Args:
        primary_model: The primary model being used
        
    Returns:
        List of recommended fallback models
    """
    # Common fallback mappings based on model capabilities
    # Updated to prioritize claude-sonnet-4-20250514 as primary and claude-3-7-sonnet-20250219 as fallback
    fallback_mappings = {
        "anthropic/claude-sonnet-4": [
            "claude-sonnet-4-20250514",
            "anthropic/claude-3.7-sonnet",
            "claude-3-7-sonnet-20250219",
            "anthropic/claude-3-sonnet"
        ],
        "anthropic/claude-3.7-sonnet": [
            "claude-3-7-sonnet-20250219",
            "anthropic/claude-sonnet-4",
            "claude-sonnet-4-20250514",
            "anthropic/claude-3-sonnet"
        ],
        "anthropic/claude-3-5-sonnet": [
            "claude-sonnet-4-20250514",
            "anthropic/claude-sonnet-4",
            "claude-3-7-sonnet-20250219",
            "anthropic/claude-3.7-sonnet",
            "anthropic/claude-3-sonnet"
        ],
        "anthropic/claude-3-sonnet": [
            "claude-3-7-sonnet-20250219",
            "anthropic/claude-3.7-sonnet",
            "claude-sonnet-4-20250514",
            "anthropic/claude-sonnet-4"
        ],
        "anthropic/claude-3-haiku": [
            "claude-3-7-sonnet-20250219",
            "anthropic/claude-3.7-sonnet",
            "anthropic/claude-3-sonnet"
        ]
    }
    
    # Remove openrouter/ prefix for lookup if present
    lookup_model = primary_model.replace("openrouter/", "")
    
    return fallback_mappings.get(lookup_model, [])


def should_use_openrouter_extensions() -> bool:
    """
    Check if OpenRouter extensions should be used based on environment.
    
    Returns:
        True if OpenRouter extensions should be applied
    """
    # Check if any OpenRouter extension environment variables are set
    extension_vars = [
        "OPENROUTER_FALLBACK_MODELS",
        "OPENROUTER_ROUTING_STRATEGY", 
        "OPENROUTER_PROVIDER_PREFERENCES",
        "OPENROUTER_TRANSFORMS",
        "OPENROUTER_MIN_P",
        "OPENROUTER_TOP_A"
    ]
    
    return any(os.getenv(var) for var in extension_vars) 