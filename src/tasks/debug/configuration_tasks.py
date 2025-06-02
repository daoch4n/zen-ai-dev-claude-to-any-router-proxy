"""Configuration tasks for debug utilities."""

from typing import Dict, Any
from ...utils.config import config
from ...core.logging_config import get_logger

logger = get_logger("debug.config_tasks")


def get_config_snapshot() -> Dict[str, Any]:
    """Get a snapshot of current configuration."""
    return {
        "debug_enabled": config.debug_enabled,
        "instructor_enabled": config.instructor_enabled,
        "log_level": config.log_level,
        "max_tokens_limit": config.max_tokens_limit,
        "environment": "development" if config.is_development() else "production"
    }


def get_token_usage_stats() -> Dict[str, Any]:
    """Get token usage statistics (placeholder for future implementation)."""
    return {
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "average_tokens_per_request": 0.0
    }


def get_model_usage_stats() -> Dict[str, int]:
    """Get model usage statistics (placeholder for future implementation)."""
    return {
        "claude-3-5-sonnet": 0,
        "claude-3-haiku": 0,
        "other": 0
    }