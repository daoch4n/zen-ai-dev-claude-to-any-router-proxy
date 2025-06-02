"""Services package for OpenRouter Anthropic Server.

This package contains business logic services including:
- Validation services with Instructor integration
- Conversion services for data transformation
- Model mapping and structured output services
"""

from .base import BaseService, ValidationService, ConversionService, InstructorService
from .validation import (
    MessageValidationService,
    ToolValidationService,
    ConversationFlowValidationService
)
from .conversion import (
    AnthropicToLiteLLMConverter,
    LiteLLMToAnthropicConverter,
    LiteLLMResponseToAnthropicConverter,
    ModelMappingService,
    StructuredOutputService
)
from .http_client import HTTPClientService, ProxyConfigurationService

# Service instances for global use
message_validator = MessageValidationService()
tool_validator = ToolValidationService()
conversation_flow_validator = ConversationFlowValidationService()

anthropic_to_litellm_converter = AnthropicToLiteLLMConverter()
litellm_to_anthropic_converter = LiteLLMToAnthropicConverter()
litellm_response_to_anthropic_converter = LiteLLMResponseToAnthropicConverter()
model_mapper = ModelMappingService()
structured_output_service = StructuredOutputService()
http_client_service = HTTPClientService()
proxy_configuration_service = ProxyConfigurationService()

__all__ = [
    # Base classes
    "BaseService",
    "ValidationService", 
    "ConversionService",
    "InstructorService",
    
    # Validation services
    "MessageValidationService",
    "ToolValidationService", 
    "ConversationFlowValidationService",
    
    # Conversion services
    "AnthropicToLiteLLMConverter",
    "LiteLLMToAnthropicConverter",
    "LiteLLMResponseToAnthropicConverter",
    "ModelMappingService",
    "StructuredOutputService",
    
    # HTTP client services
    "HTTPClientService",
    "ProxyConfigurationService",
    
    # Service instances
    "message_validator",
    "tool_validator",
    "conversation_flow_validator",
    "anthropic_to_litellm_converter",
    "litellm_to_anthropic_converter",
    "litellm_response_to_anthropic_converter",
    "model_mapper",
    "structured_output_service",
    "http_client_service",
    "proxy_configuration_service",
]