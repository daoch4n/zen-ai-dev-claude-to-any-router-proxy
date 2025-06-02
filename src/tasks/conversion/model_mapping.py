"""Model mapping tasks for OpenRouter Anthropic Server.

Prefect tasks for mapping model names and updating requests.
Part of Phase 6A comprehensive refactoring - Conversion Tasks.
"""

from typing import Any, Dict, List

from prefect import task

from ...models.instructor import ConversionResult, ModelMappingResult
from ...utils.config import config
from ...utils.errors import ModelMappingError
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager

# Initialize logging and context management
logger = get_logger("model_mapping")
context_manager = ContextManager()


@task(name="map_model")
async def map_model_task(
    original_model: str,
    custom_mapping: Dict[str, str] = None
) -> ConversionResult:
    """
    Map model name using configuration or custom mapping.
    
    Args:
        original_model: Original model name to map
        custom_mapping: Optional custom mapping to use instead of config
    
    Returns:
        ConversionResult with ModelMappingResult
    """
    try:
        # Use custom mapping if provided, otherwise use config
        if custom_mapping:
            model_mapping = custom_mapping
        else:
            model_mapping = config.get_model_mapping()
        
        mapped_model = model_mapping.get(original_model, original_model)
        mapping_applied = mapped_model != original_model
        
        # Determine mapping type
        if original_model == "big":
            mapping_type = "big"
        elif original_model == "small":
            mapping_type = "small"
        elif mapping_applied:
            mapping_type = "configured"
        else:
            mapping_type = "passthrough"
        
        result = ModelMappingResult(
            original_model=original_model,
            mapped_model=mapped_model,
            mapping_applied=mapping_applied,
            mapping_type=mapping_type
        )
        
        logger.info("Model mapping completed",
                   original_model=original_model,
                   mapped_model=mapped_model,
                   mapping_type=mapping_type,
                   mapping_applied=mapping_applied)
        
        return ConversionResult(
            success=True,
            converted_data=result.model_dump(),
            metadata={
                "original_model": original_model,
                "mapped_model": mapped_model,
                "mapping_type": mapping_type
            }
        )
        
    except Exception as e:
        error_msg = f"Model mapping failed: {str(e)}"
        logger.error("Model mapping failed", 
                    original_model=original_model,
                    error=error_msg, 
                    exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(name="update_request_model")
async def update_request_model_task(
    request_data: Dict[str, Any],
    mapping_result: Dict[str, Any]
) -> ConversionResult:
    """
    Update request data with mapped model.
    
    Args:
        request_data: Original request data
        mapping_result: Model mapping result from map_model_task
    
    Returns:
        ConversionResult with updated request data
    """
    try:
        # Parse mapping result
        mapping = ModelMappingResult(**mapping_result)
        
        # Create updated request
        updated_request = request_data.copy()
        
        # Store original model for reference if mapping was applied
        if mapping.mapping_applied:
            updated_request["original_model"] = mapping.original_model
        
        # Update model
        updated_request["model"] = mapping.mapped_model
        
        logger.info("Request model updated",
                   original_model=mapping.original_model,
                   mapped_model=mapping.mapped_model,
                   mapping_applied=mapping.mapping_applied)
        
        return ConversionResult(
            success=True,
            converted_data=updated_request,
            metadata={
                "original_model": mapping.original_model,
                "mapped_model": mapping.mapped_model,
                "mapping_applied": mapping.mapping_applied
            }
        )
        
    except Exception as e:
        error_msg = f"Request model update failed: {str(e)}"
        logger.error("Request model update failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(name="validate_model_mapping")
async def validate_model_mapping_task(
    model_name: str,
    allowed_models: List[str] = None
) -> ConversionResult:
    """
    Validate that a model mapping is allowed and supported.
    
    Args:
        model_name: Model name to validate
        allowed_models: Optional list of allowed models
    
    Returns:
        ConversionResult with validation status
    """
    try:
        # Default allowed models if not provided
        if allowed_models is None:
            allowed_models = [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022", 
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
                "anthropic/claude-3-5-sonnet-20241022",
                "anthropic/claude-3-5-haiku-20241022",
                "anthropic/claude-3-opus-20240229",
                "anthropic/claude-3-sonnet-20240229",
                "anthropic/claude-3-haiku-20240307",
                "big",
                "small"
            ]
        
        # Check if model is in allowed list
        is_valid = model_name in allowed_models
        
        # Additional validation for OpenRouter format
        has_openrouter_prefix = model_name.startswith("openrouter/")
        
        # Check for common model patterns
        is_anthropic_model = (
            "claude" in model_name.lower() or
            "anthropic" in model_name.lower() or
            model_name in ["big", "small"]
        )
        
        validation_result = {
            "is_valid": is_valid,
            "model_name": model_name,
            "has_openrouter_prefix": has_openrouter_prefix,
            "is_anthropic_model": is_anthropic_model,
            "validation_details": {
                "in_allowed_list": is_valid,
                "format_valid": True,  # Basic format validation
                "supported": is_anthropic_model
            }
        }
        
        # Add warnings for suspicious models
        warnings = []
        if not is_anthropic_model:
            warnings.append(f"Model '{model_name}' does not appear to be an Anthropic model")
        
        if not is_valid and is_anthropic_model:
            warnings.append(f"Model '{model_name}' is not in the allowed models list but appears valid")
        
        validation_result["warnings"] = warnings
        
        logger.info("Model validation completed",
                   model_name=model_name,
                   is_valid=is_valid,
                   is_anthropic_model=is_anthropic_model,
                   warning_count=len(warnings))
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "model_name": model_name,
                "is_valid": is_valid,
                "warning_count": len(warnings)
            }
        )
        
    except Exception as e:
        error_msg = f"Model validation failed: {str(e)}"
        logger.error("Model validation failed", 
                    model_name=model_name,
                    error=error_msg, 
                    exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(name="get_model_aliases")
async def get_model_aliases_task() -> ConversionResult:
    """
    Get available model aliases and their mappings.
    
    Returns:
        ConversionResult with model aliases information
    """
    try:
        model_mapping = config.get_model_mapping()
        
        # Categorize mappings
        aliases = {
            "convenience_aliases": {},
            "full_mappings": {},
            "passthrough_models": []
        }
        
        # Known convenience aliases
        convenience_aliases = ["big", "small"]
        
        for original, mapped in model_mapping.items():
            if original in convenience_aliases:
                aliases["convenience_aliases"][original] = mapped
            elif original != mapped:
                aliases["full_mappings"][original] = mapped
            else:
                aliases["passthrough_models"].append(original)
        
        # Add metadata about available models
        metadata = {
            "total_mappings": len(model_mapping),
            "convenience_aliases": len(aliases["convenience_aliases"]),
            "full_mappings": len(aliases["full_mappings"]),
            "passthrough_models": len(aliases["passthrough_models"])
        }
        
        logger.info("Model aliases retrieved", **metadata)
        
        return ConversionResult(
            success=True,
            converted_data=aliases,
            metadata=metadata
        )
        
    except Exception as e:
        error_msg = f"Failed to get model aliases: {str(e)}"
        logger.error("Model aliases retrieval failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(name="ensure_openrouter_prefix")
async def ensure_openrouter_prefix_task(
    model_name: str,
    force_prefix: bool = True
) -> ConversionResult:
    """
    Ensure model has openrouter/ prefix for LiteLLM routing.
    
    Args:
        model_name: Model name to process
        force_prefix: Whether to force the prefix even if already present
    
    Returns:
        ConversionResult with prefixed model name
    """
    try:
        original_model = model_name
        
        if not model_name.startswith('openrouter/'):
            prefixed_model = f"openrouter/{model_name}"
            prefix_added = True
        else:
            prefixed_model = model_name
            prefix_added = False
        
        logger.debug("OpenRouter prefix processing",
                    original_model=original_model,
                    prefixed_model=prefixed_model,
                    prefix_added=prefix_added)
        
        return ConversionResult(
            success=True,
            converted_data=prefixed_model,
            metadata={
                "original_model": original_model,
                "prefixed_model": prefixed_model,
                "prefix_added": prefix_added
            }
        )
        
    except Exception as e:
        error_msg = f"OpenRouter prefix processing failed: {str(e)}"
        logger.error("OpenRouter prefix processing failed", 
                    model_name=model_name,
                    error=error_msg, 
                    exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(name="remove_openrouter_prefix")
async def remove_openrouter_prefix_task(
    model_name: str
) -> ConversionResult:
    """
    Remove openrouter/ prefix from model name for response consistency.
    
    Args:
        model_name: Model name to process
    
    Returns:
        ConversionResult with unprefixed model name
    """
    try:
        original_model = model_name
        
        if model_name.startswith('openrouter/'):
            unprefixed_model = model_name[11:]  # Remove 'openrouter/' prefix
            prefix_removed = True
        else:
            unprefixed_model = model_name
            prefix_removed = False
        
        logger.debug("OpenRouter prefix removal",
                    original_model=original_model,
                    unprefixed_model=unprefixed_model,
                    prefix_removed=prefix_removed)
        
        return ConversionResult(
            success=True,
            converted_data=unprefixed_model,
            metadata={
                "original_model": original_model,
                "unprefixed_model": unprefixed_model,
                "prefix_removed": prefix_removed
            }
        )
        
    except Exception as e:
        error_msg = f"OpenRouter prefix removal failed: {str(e)}"
        logger.error("OpenRouter prefix removal failed", 
                    model_name=model_name,
                    error=error_msg, 
                    exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )