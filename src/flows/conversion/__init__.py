"""Conversion pipeline flows for OpenRouter Anthropic Server.

Orchestrates conversion task execution with optimal flow design and error handling.
Part of Phase 6A comprehensive refactoring - Conversion Pipelines.
"""

# TODO: Create these missing modules in Phase 6D
# from .request_conversion import (
#     anthropic_to_litellm_pipeline_flow,
#     litellm_to_anthropic_pipeline_flow,
#     model_mapping_pipeline_flow
# )

# from .response_conversion import (
#     litellm_response_to_anthropic_pipeline_flow,
#     response_validation_pipeline_flow,
#     streaming_response_pipeline_flow
# )

# from .schema_validation import (
#     tool_schema_validation_pipeline_flow,
#     batch_schema_cleaning_pipeline_flow,
#     schema_compatibility_pipeline_flow
# )

from .conversion_orchestration import (
    complete_request_conversion_flow,
    complete_response_conversion_flow,
    bidirectional_conversion_flow,
    conversion_health_check_flow
)

# Main conversion pipeline flows
__all__ = [
    # Complete orchestration flows (from existing conversion_orchestration module)
    "complete_request_conversion_flow",
    "complete_response_conversion_flow",
    "bidirectional_conversion_flow",
    "conversion_health_check_flow"
    
    # TODO: Add these when modules are created in Phase 6D:
    # Request conversion pipelines
    # "anthropic_to_litellm_pipeline_flow",
    # "litellm_to_anthropic_pipeline_flow",
    # "model_mapping_pipeline_flow",
    
    # Response conversion pipelines
    # "litellm_response_to_anthropic_pipeline_flow",
    # "response_validation_pipeline_flow",
    # "streaming_response_pipeline_flow",
    
    # Schema validation pipelines
    # "tool_schema_validation_pipeline_flow",
    # "batch_schema_cleaning_pipeline_flow",
    # "schema_compatibility_pipeline_flow",
]

# Pipeline configuration
CONVERSION_PIPELINE_CONFIG = {
    "request_conversion": {
        "retry_limit": 3,
        "timeout_seconds": 30,
        "enable_validation": True
    },
    "response_conversion": {
        "retry_limit": 2,
        "timeout_seconds": 20,
        "enable_metrics": True
    },
    "schema_processing": {
        "batch_size": 10,
        "parallel_processing": True,
        "cleanup_aggressive": False
    },
    "model_mapping": {
        "cache_mappings": True,
        "validate_models": True,
        "fallback_enabled": True
    }
}

def get_pipeline_config(pipeline_type: str) -> dict:
    """
    Get configuration for a specific pipeline type.
    
    Args:
        pipeline_type: Type of pipeline configuration to retrieve
    
    Returns:
        Configuration dictionary for the pipeline
    """
    return CONVERSION_PIPELINE_CONFIG.get(pipeline_type, {})