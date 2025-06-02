"""Validation services with Instructor integration - Refactored Facade."""

import asyncio
import uuid
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .base import ValidationService, InstructorService
from ..models.anthropic import Message, MessagesRequest, Tool
from ..models.instructor import (
    ValidationResult, ToolValidationResult, ConversationFlowResult,
    StructuredToolCall
)
from ..utils.errors import ToolValidationError, ConversationFlowError
from ..core.logging_config import get_logger
from ..services.context_manager import ContextManager
from ..coordinators.validation_coordinator import get_validation_coordinator

class MessageValidationService(ValidationService[Message], InstructorService):
    """Service for validating Anthropic messages with Instructor enhancement - Refactored."""
    
    def __init__(self):
        """Initialize message validation service."""
        ValidationService.__init__(self, "MessageValidation")
        InstructorService.__init__(self, "MessageValidation")
        self.logger = get_logger("validation.message")
        self.context_manager = ContextManager()
        self._coordinator = get_validation_coordinator()
    
    def _run_async(self, coro):
        """Run async coroutine in sync context."""
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                # If no loop is running, run directly
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop exists, create new one
            return asyncio.run(coro)
    
    def validate(self, data: Any, **kwargs) -> ValidationResult:
        """Validate message data using coordinator."""
        try:
            # Use coordinator for validation
            return self._run_async(self._coordinator.validate_message(data, **kwargs))
        except Exception as e:
            self.logger.error("Message validation failed", error=str(e), exc_info=True)
            return self.create_validation_result(
                False,
                errors=[f"Validation failed: {str(e)}"],
                suggestions=["Check message format and try again"]
            )
    
    def validate_messages_request(self, request: MessagesRequest) -> MessagesRequest:
        """Validate a MessagesRequest using coordinator."""
        try:
            # Use coordinator for validation
            result = self._run_async(self._coordinator.validate_messages_request(request))
            
            if not result.is_valid:
                error_message = f"Request validation failed: {'; '.join(result.errors)}"
                self.logger.error("Messages request validation failed", error=error_message)
                raise ValueError(error_message)
            
            # If validation passes, get the actual validated request from the task
            from ..tasks.validation.message_validation_tasks import validate_messages_request_data
            validated_request = validate_messages_request_data(request)
            return validated_request
            
        except Exception as e:
            self.logger.error("Messages request validation failed", error=str(e), exc_info=True)
            raise ValueError(f"Request validation failed: {str(e)}")


class ToolValidationService(ValidationService[Tool], InstructorService):
    """Service for validating tools with enhanced functionality - Refactored."""
    
    def __init__(self):
        """Initialize tool validation service."""
        ValidationService.__init__(self, "ToolValidation")
        InstructorService.__init__(self, "ToolValidation")
        self.logger = get_logger("validation.tool")
        self.context_manager = ContextManager()
        self._coordinator = get_validation_coordinator()
    
    def _run_async(self, coro):
        """Run async coroutine in sync context."""
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                # If no loop is running, run directly
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop exists, create new one
            return asyncio.run(coro)
    
    def validate(self, data: Any, **kwargs) -> ValidationResult:
        """Validate tool data using coordinator."""
        try:
            return self._run_async(self._coordinator.validate_tool(data, **kwargs))
        except Exception as e:
            self.logger.error("Tool validation failed", error=str(e), exc_info=True)
            return self.create_validation_result(
                False,
                errors=[f"Tool validation failed: {str(e)}"]
            )
    
    def validate_tool_flow(
        self,
        messages: List[Message],
        available_tools: List[Tool]
    ) -> ToolValidationResult:
        """Validate tool flow using coordinator."""
        try:
            return self._run_async(self._coordinator.validate_tool_flow(messages, available_tools))
        except Exception as e:
            self.logger.error("Tool flow validation failed", error=str(e), exc_info=True)
            raise ToolValidationError(f"Tool flow validation failed: {str(e)}")


class ConversationFlowValidationService(ValidationService[List[Message]], InstructorService):
    """Service for validating conversation flows - Refactored."""
    
    def __init__(self):
        """Initialize conversation flow validation service."""
        ValidationService.__init__(self, "ConversationFlowValidation")
        InstructorService.__init__(self, "ConversationFlowValidation")
        self.logger = get_logger("validation.conversation_flow")
        self.context_manager = ContextManager()
        self._coordinator = get_validation_coordinator()
    
    def _run_async(self, coro):
        """Run async coroutine in sync context."""
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                # If no loop is running, run directly
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop exists, create new one
            return asyncio.run(coro)
    
    def validate(self, data: Any, **kwargs) -> ValidationResult:
        """Validate conversation flow using coordinator."""
        try:
            return self._run_async(self._coordinator.validate_conversation_flow(data, **kwargs))
        except Exception as e:
            self.logger.error("Conversation flow validation failed", error=str(e), exc_info=True)
            return self.create_validation_result(
                False,
                errors=[f"Conversation flow validation failed: {str(e)}"]
            )
    
    def validate_conversation_flow(self, messages: List[Message]) -> ConversationFlowResult:
        """Validate conversation flow and return detailed results."""
        try:
            # Validate role sequence
            role_result = self._run_async(self._coordinator.validate_message_role_sequence(messages))
            
            # Validate tool flow in conversation
            tool_result = self._run_async(self._coordinator.conversation_flow.validate_tool_flow_in_messages(messages))
            
            # Create conversation flow result
            return ConversationFlowResult(
                is_valid=role_result.is_valid and tool_result.is_valid,
                flow_errors=role_result.errors + tool_result.errors,
                flow_warnings=role_result.warnings + tool_result.warnings,
                role_transitions=[],  # Legacy field
                tool_call_patterns=[],  # Legacy field
                message_count=len(messages),
                validation_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error("Conversation flow validation failed", error=str(e), exc_info=True)
            raise ConversationFlowError(f"Conversation flow validation failed: {str(e)}")