"""Model mapping tasks for conversion operations."""

from typing import Dict, Any
from ...utils.config import config
from ...utils.errors import ModelMappingError
from ...core.logging_config import get_logger
from ...models.instructor import ModelMappingResult

logger = get_logger("conversion.model_mapping")


def ensure_openrouter_prefix(model: str) -> str:
    """
    Ensure model has openrouter/ prefix for LiteLLM routing.
    
    This is critical for LiteLLM to correctly route requests to OpenRouter.
    Based on openrouter_anthropic_server.py implementation.
    """
    if not model.startswith('openrouter/'):
        return f"openrouter/{model}"
    return model


def map_model_name(original_model: str) -> ModelMappingResult:
    """Map model name using configuration."""
    try:
        # Get model mappings from config
        model_mappings = config.get_model_mapping()
        
        # Map the model (alias mapping only)
        mapped_model = model_mappings.get(original_model, original_model)
        
        # Determine if alias mapping was applied
        alias_mapping_applied = original_model in model_mappings
        
        # Determine mapping type
        if alias_mapping_applied:
            # Check if it's one of the known aliases
            if original_model == "big":
                mapping_type = "big"
            elif original_model == "small":
                mapping_type = "small"
            else:
                mapping_type = "configured"
        else:
            mapping_type = "passthrough"
        
        # Ensure OpenRouter prefix for final result
        final_model = ensure_openrouter_prefix(mapped_model)
        
        logger.info("Model mapping completed",
                   original_model=original_model,
                   mapped_model=mapped_model,
                   final_model=final_model,
                   mapping_type=mapping_type)
        
        return ModelMappingResult(
            original_model=original_model,
            mapped_model=mapped_model,  # Only alias mapping, no openrouter prefix
            mapping_applied=alias_mapping_applied,  # Only True if alias mapping happened
            mapping_type=mapping_type
        )
    
    except Exception as e:
        logger.error("Model mapping failed",
                    original_model=original_model,
                    error=str(e))
        raise ModelMappingError(f"Failed to map model '{original_model}': {str(e)}")


def update_request_with_model_mapping(request_data: Dict[str, Any], mapping_result: ModelMappingResult) -> Dict[str, Any]:
    """Update request data with mapped model."""
    updated_request = request_data.copy()
    
    # Apply openrouter prefix to mapped model for the final request
    final_model = ensure_openrouter_prefix(mapping_result.mapped_model)
    updated_request['model'] = final_model
    
    # Preserve original model for tracking
    if mapping_result.mapping_applied:
        updated_request['original_model'] = mapping_result.original_model
        logger.info("Request updated with model mapping",
                   original_model=mapping_result.original_model,
                   final_model=final_model)
    
    return updated_request