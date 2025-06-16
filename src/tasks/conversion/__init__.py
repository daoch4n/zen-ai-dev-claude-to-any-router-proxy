"""Conversion task modules for atomic conversion operations."""

from .model_mapping_tasks import ensure_openrouter_prefix
from .message_conversion_tasks import (
    convert_anthropic_message_to_litellm,
    convert_litellm_message_to_anthropic,
    extract_system_message_content
)
from .tool_conversion_tasks import (
    convert_anthropic_tool_to_litellm,
    convert_litellm_tool_to_anthropic,
    clean_openrouter_tool_schema
)
from .structured_output_tasks import (
    format_validation_results,
    create_structured_validation_summary
)
from .openrouter_extensions import (
    add_openrouter_extensions,
    get_openrouter_config_from_env,
    validate_openrouter_config,
    create_default_openrouter_config,
    get_openrouter_models_for_fallback,
    should_use_openrouter_extensions
)
from .openai_advanced_parameters import (
    add_openai_advanced_parameters,
    get_openai_advanced_config_from_env,
    validate_openai_advanced_config,
    create_default_openai_advanced_config,
    should_use_openai_advanced_parameters,
    get_openai_parameter_usage_stats
)

__all__ = [
    "ensure_openrouter_prefix",
    "convert_anthropic_message_to_litellm", 
    "convert_litellm_message_to_anthropic",
    "extract_system_message_content",
    "convert_anthropic_tool_to_litellm",
    "convert_litellm_tool_to_anthropic", 
    "clean_openrouter_tool_schema",
    "format_validation_results",
    "create_structured_validation_summary",
    # OpenRouter extensions
    "add_openrouter_extensions",
    "get_openrouter_config_from_env",
    "validate_openrouter_config",
    "create_default_openrouter_config",
    "get_openrouter_models_for_fallback",
    "should_use_openrouter_extensions",
    # OpenAI advanced parameters
    "add_openai_advanced_parameters",
    "get_openai_advanced_config_from_env",
    "validate_openai_advanced_config",
    "create_default_openai_advanced_config",
    "should_use_openai_advanced_parameters",
    "get_openai_parameter_usage_stats"
]