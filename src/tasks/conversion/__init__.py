"""Conversion task modules for OpenRouter Anthropic Server.

Modular Prefect tasks for data transformation between different formats.
Part of Phase 6A comprehensive refactoring - Conversion Tasks.
"""

from .format_conversion import (
    anthropic_to_litellm_task,
    litellm_response_to_anthropic_task,
    litellm_to_anthropic_task
)

from .model_mapping import (
    map_model_task,
    update_request_model_task,
    validate_model_mapping_task
)

from .schema_processing import (
    clean_openrouter_schema_task,
    validate_tool_schema_task,
    convert_tool_definition_task
)

from .message_transformation import (
    convert_message_content_task,
    extract_system_message_task,
    transform_tool_calls_task,
    format_tool_results_task
)

from .response_processing import (
    extract_usage_info_task,
    determine_response_model_task,
    map_stop_reason_task,
    reconstruct_streaming_response_task
)

from .structured_output import (
    create_validation_summary_task,
    format_validation_results_task,
    extract_structured_data_task
)

# Main conversion tasks
__all__ = [
    # Format conversion tasks
    "anthropic_to_litellm_task",
    "litellm_response_to_anthropic_task", 
    "litellm_to_anthropic_task",
    
    # Model mapping tasks
    "map_model_task",
    "update_request_model_task",
    "validate_model_mapping_task",
    
    # Schema processing tasks
    "clean_openrouter_schema_task",
    "validate_tool_schema_task",
    "convert_tool_definition_task",
    
    # Message transformation tasks
    "convert_message_content_task",
    "extract_system_message_task",
    "transform_tool_calls_task",
    "format_tool_results_task",
    
    # Response processing tasks
    "extract_usage_info_task",
    "determine_response_model_task",
    "map_stop_reason_task",
    "reconstruct_streaming_response_task",
    
    # Structured output tasks
    "create_validation_summary_task",
    "format_validation_results_task",
    "extract_structured_data_task"
]