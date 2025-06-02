"""Message validation flow for orchestrating message validation operations."""

from typing import Any, List
from ...models.anthropic import Message, MessagesRequest
from ...models.instructor import ValidationResult
from ...tasks.validation.message_validation_tasks import (
    validate_message_data,
    validate_messages_request_data
)
from ...tasks.validation.schema_validation_tasks import create_validation_result
from ...core.logging_config import get_logger

logger = get_logger("validation.message_flow")


class MessageValidationFlow:
    """Orchestrates message validation operations using task-based architecture."""
    
    def __init__(self):
        """Initialize message validation flow."""
        logger.info("MessageValidationFlow initialized")
    
    async def validate_message(self, data: Any, **kwargs) -> ValidationResult:
        """Validate message data with comprehensive checks.
        
        Args:
            data: Message data to validate
            **kwargs: Additional validation parameters
            
        Returns:
            ValidationResult with validation details
        """
        try:
            logger.debug("Starting message validation", data_type=type(data).__name__)
            
            # Use task function for validation
            result_data = validate_message_data(data)
            
            # Convert to ValidationResult
            result = create_validation_result(
                is_valid=result_data["is_valid"],
                errors=result_data["errors"],
                warnings=result_data["warnings"],
                suggestions=result_data["suggestions"]
            )
            
            logger.debug("Message validation completed",
                        is_valid=result.is_valid,
                        error_count=len(result.errors),
                        warning_count=len(result.warnings))
            
            return result
            
        except Exception as e:
            logger.error("Message validation flow failed", error=str(e), exc_info=True)
            return create_validation_result(
                False,
                errors=[f"Validation failed: {str(e)}"],
                suggestions=["Check message format and try again"]
            )
    
    async def validate_messages_request(self, request: MessagesRequest) -> MessagesRequest:
        """Validate a MessagesRequest and return it if valid.
        
        Args:
            request: MessagesRequest to validate
            
        Returns:
            Validated MessagesRequest object
            
        Raises:
            ValueError: If validation fails
        """
        try:
            logger.debug("Starting messages request validation",
                        message_count=len(request.messages) if request and request.messages else 0)
            
            # Use task function for validation
            validated_request = validate_messages_request_data(request)
            
            logger.info("Messages request validation flow completed successfully",
                       message_count=len(validated_request.messages))
            
            # Return ValidationResult instead of MessagesRequest
            from ...tasks.validation.schema_validation_tasks import create_validation_result
            return create_validation_result(
                is_valid=True,
                errors=[],
                warnings=[],
                suggestions=[]
            )
            
        except Exception as e:
            logger.error("Messages request validation flow failed", error=str(e), exc_info=True)
            raise
    
    async def batch_validate_messages(self, messages: List[Message]) -> List[ValidationResult]:
        """Validate multiple messages in batch.
        
        Args:
            messages: List of messages to validate
            
        Returns:
            List of ValidationResult objects
        """
        try:
            logger.debug("Starting batch message validation", message_count=len(messages))
            
            results = []
            for i, message in enumerate(messages):
                try:
                    result = await self.validate_message(message)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to validate message {i}", error=str(e))
                    results.append(create_validation_result(
                        False,
                        errors=[f"Message {i} validation failed: {str(e)}"]
                    ))
            
            valid_count = sum(1 for r in results if r.is_valid)
            logger.info("Batch message validation completed",
                       total_messages=len(messages),
                       valid_messages=valid_count,
                       invalid_messages=len(messages) - valid_count)
            
            return results
            
        except Exception as e:
            logger.error("Batch message validation flow failed", error=str(e), exc_info=True)
            return [create_validation_result(
                False,
                errors=[f"Batch validation failed: {str(e)}"]
            ) for _ in messages]