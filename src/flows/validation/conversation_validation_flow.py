"""Conversation validation flow for orchestrating conversation validation operations."""

from typing import Any, List
from ...models.anthropic import Message
from ...models.instructor import ValidationResult
from ...tasks.validation.conversation_validation_tasks import (
    validate_conversation_flow_data,
    validate_role_sequence,
    is_valid_same_role_sequence,
    validate_tool_flow_in_conversation
)
from ...tasks.validation.schema_validation_tasks import create_validation_result
from ...core.logging_config import get_logger

logger = get_logger("validation.conversation_flow")


class ConversationValidationFlow:
    """Orchestrates conversation validation operations using task-based architecture."""
    
    def __init__(self):
        """Initialize conversation validation flow."""
        logger.info("ConversationValidationFlow initialized")
    
    async def validate_conversation_flow(self, data: Any, **kwargs) -> ValidationResult:
        """Validate conversation flow data.
        
        Args:
            data: Conversation flow data to validate
            **kwargs: Additional validation parameters
            
        Returns:
            ValidationResult with validation details
        """
        try:
            logger.debug("Starting conversation flow validation", data_type=type(data).__name__)
            
            # Use task function for validation
            result_data = validate_conversation_flow_data(data)
            
            # Convert ConversationFlowResult to ValidationResult
            result = create_validation_result(
                is_valid=result_data.is_valid,
                errors=result_data.flow_errors,
                warnings=[],  # ConversationFlowResult doesn't have warnings
                suggestions=result_data.suggestions
            )
            
            logger.debug("Conversation flow validation completed",
                        is_valid=result.is_valid,
                        error_count=len(result.errors),
                        warning_count=len(result.warnings))
            
            return result
            
        except Exception as e:
            logger.error("Conversation flow validation failed", error=str(e), exc_info=True)
            return create_validation_result(
                False,
                errors=[f"Conversation flow validation failed: {str(e)}"]
            )
    
    async def validate_message_role_sequence(self, messages: List[Message]) -> ValidationResult:
        """Validate the role sequence in a conversation.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            ValidationResult with role sequence validation details
        """
        try:
            logger.debug("Starting role sequence validation", message_count=len(messages))
            
            # Use task function for validation with errors list
            errors = []
            result_data = validate_role_sequence(messages, errors)
            
            # Convert boolean result to ValidationResult
            result = create_validation_result(
                is_valid=result_data,
                errors=errors,
                warnings=[],
                suggestions=["Ensure proper alternating user/assistant roles"] if not result_data else []
            )
            
            logger.debug("Role sequence validation completed",
                        is_valid=result.is_valid,
                        error_count=len(result.errors))
            
            return result
            
        except Exception as e:
            logger.error("Role sequence validation failed", error=str(e), exc_info=True)
            return create_validation_result(
                False,
                errors=[f"Role sequence validation failed: {str(e)}"]
            )
    
    async def validate_tool_flow_in_messages(self, messages: List[Message]) -> ValidationResult:
        """Validate tool flow within conversation messages.
        
        Args:
            messages: List of conversation messages to validate
            
        Returns:
            ValidationResult with tool flow validation details
        """
        try:
            logger.debug("Starting tool flow validation in conversation", 
                        message_count=len(messages))
            
            # Use task function for validation with errors list
            errors = []
            result_data = validate_tool_flow_in_conversation(messages, errors)
            
            # Convert boolean result to ValidationResult
            result = create_validation_result(
                is_valid=result_data,
                errors=errors,
                warnings=[],
                suggestions=["Check tool use and result pairing"] if not result_data else []
            )
            
            logger.debug("Tool flow validation in conversation completed",
                        is_valid=result.is_valid,
                        error_count=len(result.errors))
            
            return result
            
        except Exception as e:
            logger.error("Tool flow validation in conversation failed", error=str(e), exc_info=True)
            return create_validation_result(
                False,
                errors=[f"Tool flow validation failed: {str(e)}"]
            )
    
    async def check_same_role_sequence_validity(self, messages: List[Message]) -> bool:
        """Check if same role sequences are valid in conversation.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            True if same role sequences are valid, False otherwise
        """
        try:
            logger.debug("Checking same role sequence validity", message_count=len(messages))
            
            # Use task function for validation
            is_valid = is_valid_same_role_sequence(messages)
            
            logger.debug("Same role sequence validity check completed", is_valid=is_valid)
            
            return is_valid
            
        except Exception as e:
            logger.error("Same role sequence validity check failed", error=str(e), exc_info=True)
            return False
    
    async def comprehensive_conversation_validation(self, messages: List[Message]) -> ValidationResult:
        """Perform comprehensive validation of conversation including roles and tool flow.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            ValidationResult with comprehensive validation details
        """
        try:
            logger.debug("Starting comprehensive conversation validation", 
                        message_count=len(messages))
            
            all_errors = []
            all_warnings = []
            all_suggestions = []
            
            # Validate role sequence
            role_result = await self.validate_message_role_sequence(messages)
            all_errors.extend(role_result.errors)
            all_warnings.extend(role_result.warnings)
            all_suggestions.extend(role_result.suggestions)
            
            # Validate tool flow in conversation
            tool_result = await self.validate_tool_flow_in_messages(messages)
            all_errors.extend(tool_result.errors)
            all_warnings.extend(tool_result.warnings)
            all_suggestions.extend(tool_result.suggestions)
            
            # Overall validation
            is_valid = len(all_errors) == 0
            
            result = create_validation_result(
                is_valid=is_valid,
                errors=all_errors,
                warnings=all_warnings,
                suggestions=all_suggestions
            )
            
            logger.info("Comprehensive conversation validation completed",
                       is_valid=result.is_valid,
                       total_errors=len(all_errors),
                       total_warnings=len(all_warnings))
            
            return result
            
        except Exception as e:
            logger.error("Comprehensive conversation validation failed", error=str(e), exc_info=True)
            return create_validation_result(
                False,
                errors=[f"Comprehensive conversation validation failed: {str(e)}"]
            )
    
    async def validate_conversation_structure(self, messages: List[Message]) -> ValidationResult:
        """Validate the overall structure of a conversation.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            ValidationResult with structure validation details
        """
        try:
            logger.debug("Starting conversation structure validation", 
                        message_count=len(messages))
            
            errors = []
            warnings = []
            suggestions = []
            
            # Basic structure checks
            if not messages:
                errors.append("Conversation cannot be empty")
            elif len(messages) == 1:
                warnings.append("Single message conversation may not be meaningful")
            
            # Check for alternating patterns if messages exist
            if messages and len(messages) > 1:
                same_role_valid = await self.check_same_role_sequence_validity(messages)
                if not same_role_valid:
                    suggestions.append("Consider improving role alternation for better conversation flow")
            
            # Create result
            is_valid = len(errors) == 0
            result = create_validation_result(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions
            )
            
            logger.debug("Conversation structure validation completed", is_valid=result.is_valid)
            
            return result
            
        except Exception as e:
            logger.error("Conversation structure validation failed", error=str(e), exc_info=True)
            return create_validation_result(
                False,
                errors=[f"Conversation structure validation failed: {str(e)}"]
            )