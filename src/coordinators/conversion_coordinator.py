"""Conversion coordinator for orchestrating conversion flows."""

from typing import Any, Dict, List, Optional

from ..services.base import ConversionService, InstructorService
from ..models.anthropic import MessagesRequest, MessagesResponse
from ..models.litellm import LiteLLMRequest
from ..models.instructor import ConversionResult, ModelMappingResult
from ..flows.conversion.anthropic_to_litellm_flow import AnthropicToLiteLLMFlow
from ..flows.conversion.litellm_response_to_anthropic_flow import LiteLLMResponseToAnthropicFlow
from ..flows.conversion.litellm_to_anthropic_flow import LiteLLMToAnthropicFlow
from ..tasks.conversion.model_mapping_tasks import map_model_name, update_request_with_model_mapping
from ..tasks.conversion.structured_output_tasks import create_structured_validation_summary
from ..core.logging_config import get_logger

logger = get_logger("conversion.coordinator")


class ConversionCoordinator:
    """Coordinates conversion operations between different formats."""
    
    def __init__(self):
        """Initialize conversion coordinator."""
        self.anthropic_to_litellm_flow = AnthropicToLiteLLMFlow()
        self.litellm_response_to_anthropic_flow = LiteLLMResponseToAnthropicFlow()
        self.litellm_to_anthropic_flow = LiteLLMToAnthropicFlow()
        logger.info("Conversion coordinator initialized")
    
    async def convert_anthropic_to_litellm(self, source: MessagesRequest, **kwargs) -> ConversionResult:
        """Convert Anthropic MessagesRequest to LiteLLM format."""
        logger.debug("Starting Anthropic to LiteLLM conversion",
                    model=source.model,
                    message_count=len(source.messages),
                    has_tools=bool(source.tools))
        
        result = self.anthropic_to_litellm_flow.convert(source, **kwargs)
        
        logger.info("Anthropic to LiteLLM conversion completed",
                   success=result.success,
                   error_count=len(result.errors) if result.errors else 0)
        
        return result
    
    async def convert_litellm_response_to_anthropic(
        self,
        litellm_response: Any,
        original_request: Optional[MessagesRequest] = None,
        **kwargs
    ) -> ConversionResult:
        """Convert LiteLLM response to Anthropic MessagesResponse format."""
        logger.debug("Starting LiteLLM response to Anthropic conversion",
                    response_type=str(type(litellm_response)),
                    has_original_request=original_request is not None)
        
        result = self.litellm_response_to_anthropic_flow.convert(
            litellm_response,
            original_request=original_request,
            **kwargs
        )
        
        logger.info("LiteLLM response to Anthropic conversion completed",
                   success=result.success,
                   error_count=len(result.errors) if result.errors else 0)
        
        return result
    
    async def convert_litellm_to_anthropic(self, source: LiteLLMRequest, **kwargs) -> ConversionResult:
        """Convert LiteLLM request to Anthropic format."""
        logger.debug("Starting LiteLLM to Anthropic conversion",
                    model=source.model,
                    message_count=len(source.messages),
                    has_tools=bool(source.tools))
        
        result = self.litellm_to_anthropic_flow.convert(source, **kwargs)
        
        logger.info("LiteLLM to Anthropic conversion completed",
                   success=result.success,
                   error_count=len(result.errors) if result.errors else 0)
        
        return result
    
    async def map_model(self, original_model: str) -> ModelMappingResult:
        """Map model name using configuration."""
        logger.debug("Starting model mapping", original_model=original_model)
        
        result = map_model_name(original_model)
        
        logger.info("Model mapping completed",
                   original_model=original_model,
                   mapped_model=result.mapped_model,
                   mapping_applied=result.mapping_applied)
        
        return result
    
    async def update_request_with_mapping(
        self,
        request_data: Dict[str, Any],
        mapping_result: ModelMappingResult
    ) -> Dict[str, Any]:
        """Update request data with mapped model."""
        logger.debug("Updating request with model mapping",
                    original_model=mapping_result.original_model,
                    mapped_model=mapping_result.mapped_model)
        
        updated_request = update_request_with_model_mapping(request_data, mapping_result)
        
        logger.info("Request updated with model mapping",
                   mapping_applied=mapping_result.mapping_applied)
        
        return updated_request
    
    async def create_validation_summary(
        self,
        validation_results: List[Dict[str, Any]],
        model: str = "anthropic/claude-3-5-sonnet-20241022"
    ) -> Dict[str, Any]:
        """Create a structured validation summary using Instructor."""
        logger.debug("Creating validation summary",
                    validation_count=len(validation_results),
                    model=model)
        
        # Use instructor service from one of the flows
        instructor_service = self.anthropic_to_litellm_flow
        
        result = create_structured_validation_summary(
            validation_results,
            instructor_service,
            model
        )
        
        logger.info("Validation summary created",
                   validation_count=len(validation_results))
        
        return result
    
    def get_conversion_metrics(self) -> Dict[str, Any]:
        """Get metrics from all conversion flows."""
        return {
            "anthropic_to_litellm": {
                "operations": getattr(self.anthropic_to_litellm_flow, 'operation_count', 0),
                "success_count": getattr(self.anthropic_to_litellm_flow, 'success_count', 0),
                "error_count": getattr(self.anthropic_to_litellm_flow, 'error_count', 0)
            },
            "litellm_response_to_anthropic": {
                "operations": getattr(self.litellm_response_to_anthropic_flow, 'operation_count', 0),
                "success_count": getattr(self.litellm_response_to_anthropic_flow, 'success_count', 0),
                "error_count": getattr(self.litellm_response_to_anthropic_flow, 'error_count', 0)
            },
            "litellm_to_anthropic": {
                "operations": getattr(self.litellm_to_anthropic_flow, 'operation_count', 0),
                "success_count": getattr(self.litellm_to_anthropic_flow, 'success_count', 0),
                "error_count": getattr(self.litellm_to_anthropic_flow, 'error_count', 0)
            }
        }
    
    def reset_metrics(self) -> None:
        """Reset metrics for all conversion flows."""
        for flow in [
            self.anthropic_to_litellm_flow,
            self.litellm_response_to_anthropic_flow,
            self.litellm_to_anthropic_flow
        ]:
            if hasattr(flow, 'operation_count'):
                flow.operation_count = 0
            if hasattr(flow, 'success_count'):
                flow.success_count = 0
            if hasattr(flow, 'error_count'):
                flow.error_count = 0
        
        logger.info("Conversion metrics reset")