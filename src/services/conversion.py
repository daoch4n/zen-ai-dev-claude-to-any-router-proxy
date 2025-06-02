"""Lightweight conversion service facade for backward compatibility."""

from typing import Any, Dict, List, Optional, Union

from .base import ConversionService, InstructorService
from ..models.anthropic import Message, MessagesRequest, MessagesResponse, Tool
from ..models.base import Usage
from ..models.litellm import LiteLLMMessage, LiteLLMRequest
from ..models.instructor import ConversionResult, ModelMappingResult
from ..coordinators.conversion_coordinator import ConversionCoordinator
from ..tasks.conversion.model_mapping_tasks import ensure_openrouter_prefix
from ..core.logging_config import get_logger

logger = get_logger("conversion")

# Global coordinator instance for backward compatibility
_coordinator = ConversionCoordinator()


class AnthropicToLiteLLMConverter(ConversionService[MessagesRequest, LiteLLMRequest], InstructorService):
    """Backward-compatible converter that delegates to the conversion coordinator."""
    
    def __init__(self):
        """Initialize Anthropic to LiteLLM converter."""
        ConversionService.__init__(self, "AnthropicToLiteLLM")
        InstructorService.__init__(self, "AnthropicToLiteLLM")
    
    def convert(self, source: MessagesRequest, **kwargs) -> ConversionResult:
        """Convert Anthropic MessagesRequest to LiteLLM format."""
        import asyncio
        
        # Handle both sync and async contexts
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, but this is a sync call
                # Create a new task to run the async conversion
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        _coordinator.convert_anthropic_to_litellm(source, **kwargs)
                    )
                    return future.result()
            else:
                # We're in a sync context
                return asyncio.run(_coordinator.convert_anthropic_to_litellm(source, **kwargs))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(_coordinator.convert_anthropic_to_litellm(source, **kwargs))


class LiteLLMResponseToAnthropicConverter(ConversionService[Any, MessagesResponse]):
    """Backward-compatible converter that delegates to the conversion coordinator."""
    
    def __init__(self):
        """Initialize LiteLLM response to Anthropic converter."""
        super().__init__("LiteLLMResponseToAnthropic")
    
    def convert(self, litellm_response: Any, original_request: Optional[MessagesRequest] = None, **kwargs) -> ConversionResult:
        """Convert LiteLLM response to Anthropic MessagesResponse format."""
        import asyncio
        
        # Handle both sync and async contexts
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, but this is a sync call
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        _coordinator.convert_litellm_response_to_anthropic(
                            litellm_response, original_request, **kwargs
                        )
                    )
                    return future.result()
            else:
                # We're in a sync context
                return asyncio.run(_coordinator.convert_litellm_response_to_anthropic(
                    litellm_response, original_request, **kwargs
                ))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(_coordinator.convert_litellm_response_to_anthropic(
                litellm_response, original_request, **kwargs
            ))


class LiteLLMToAnthropicConverter(ConversionService[LiteLLMRequest, MessagesRequest], InstructorService):
    """Backward-compatible converter that delegates to the conversion coordinator."""
    
    def __init__(self):
        """Initialize LiteLLM to Anthropic converter."""
        ConversionService.__init__(self, "LiteLLMToAnthropic")
        InstructorService.__init__(self, "LiteLLMToAnthropic")
    
    def convert(self, source: LiteLLMRequest, **kwargs) -> ConversionResult:
        """Convert LiteLLM request to Anthropic format."""
        import asyncio
        
        # Handle both sync and async contexts
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, but this is a sync call
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        _coordinator.convert_litellm_to_anthropic(source, **kwargs)
                    )
                    return future.result()
            else:
                # We're in a sync context
                return asyncio.run(_coordinator.convert_litellm_to_anthropic(source, **kwargs))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(_coordinator.convert_litellm_to_anthropic(source, **kwargs))


class ModelMappingService(InstructorService):
    """Backward-compatible service that delegates to the conversion coordinator."""
    
    def __init__(self):
        """Initialize model mapping service."""
        super().__init__("ModelMapping")
    
    def map_model(self, original_model: str) -> ModelMappingResult:
        """Map model name using configuration."""
        import asyncio
        
        # Handle both sync and async contexts
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, but this is a sync call
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        _coordinator.map_model(original_model)
                    )
                    return future.result()
            else:
                # We're in a sync context
                return asyncio.run(_coordinator.map_model(original_model))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(_coordinator.map_model(original_model))
    
    def update_request_with_mapping(
        self,
        request_data: Dict[str, Any],
        mapping_result: ModelMappingResult
    ) -> Dict[str, Any]:
        """Update request data with mapped model."""
        import asyncio
        
        # Handle both sync and async contexts
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, but this is a sync call
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        _coordinator.update_request_with_mapping(request_data, mapping_result)
                    )
                    return future.result()
            else:
                # We're in a sync context
                return asyncio.run(_coordinator.update_request_with_mapping(request_data, mapping_result))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(_coordinator.update_request_with_mapping(request_data, mapping_result))


class StructuredOutputService(InstructorService):
    """Backward-compatible service that delegates to the conversion coordinator."""
    
    def __init__(self):
        """Initialize structured output service."""
        super().__init__("StructuredOutput")
    
    def create_validation_summary(
        self,
        validation_results: List[Dict[str, Any]],
        model: str = "anthropic/claude-3-5-sonnet-20241022"
    ) -> Dict[str, Any]:
        """Create a structured validation summary using Instructor."""
        import asyncio
        
        # Handle both sync and async contexts
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, but this is a sync call
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        _coordinator.create_validation_summary(validation_results, model)
                    )
                    return future.result()
            else:
                # We're in a sync context
                return asyncio.run(_coordinator.create_validation_summary(validation_results, model))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(_coordinator.create_validation_summary(validation_results, model))