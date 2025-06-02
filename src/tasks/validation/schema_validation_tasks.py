"""Schema validation utility tasks."""

from typing import Any, List, Optional
from ...models.instructor import ValidationResult
from ...core.logging_config import get_logger

logger = get_logger("validation.schema_tasks")


def create_validation_result(
    is_valid: bool,
    errors: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
    suggestions: Optional[List[str]] = None
) -> ValidationResult:
    """Create a ValidationResult object.
    
    Args:
        is_valid: Whether the validation passed
        errors: List of validation errors
        warnings: List of validation warnings
        suggestions: List of improvement suggestions
        
    Returns:
        ValidationResult object
    """
    return ValidationResult(
        is_valid=is_valid,
        errors=errors or [],
        warnings=warnings or [],
        suggestions=suggestions or []
    )


# Custom exception classes for validation errors
class ValidationError(Exception):
    """Base validation error."""
    pass


class ToolValidationError(ValidationError):
    """Tool validation specific error."""
    pass


class ConversationFlowError(ValidationError):
    """Conversation flow validation specific error."""
    pass