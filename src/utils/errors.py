"""Custom exception classes for the OpenRouter Anthropic Server."""

class OpenRouterProxyError(Exception):
    """Base exception for OpenRouter proxy errors."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class ToolValidationError(OpenRouterProxyError):
    """Raised when tool validation fails."""
    pass

class ConversationFlowError(OpenRouterProxyError):
    """Raised when conversation flow is invalid."""
    pass

class OrphanedToolError(ToolValidationError):
    """Raised when orphaned tools are detected."""
    pass

class ModelMappingError(OpenRouterProxyError):
    """Raised when model mapping fails."""
    pass

class SchemaValidationError(OpenRouterProxyError):
    """Raised when schema validation fails."""
    pass

class InstructorError(OpenRouterProxyError):
    """Raised when Instructor operations fail."""
    pass

class StructuredOutputError(InstructorError):
    """Raised when structured output generation fails."""
    pass

class ValidationExtractionError(InstructorError):
    """Raised when validation or extraction using Instructor fails."""
    pass

class LiteLLMError(OpenRouterProxyError):
    """Raised when LiteLLM operations fail."""
    pass

class AnthropicConversionError(OpenRouterProxyError):
    """Raised when Anthropic format conversion fails."""
    pass

class StreamingError(OpenRouterProxyError):
    """Raised when streaming operations fail."""
    pass

class ConfigurationError(OpenRouterProxyError):
    """Raised when configuration is invalid."""
    pass