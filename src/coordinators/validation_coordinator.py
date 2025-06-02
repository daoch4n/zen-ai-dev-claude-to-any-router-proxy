"""Validation coordinator for managing all validation operations."""

from typing import Any, List, Optional, Dict
from ..models.anthropic import Message, Tool
from ..models.instructor import ValidationResult, ToolValidationResult
from ..flows.validation.message_validation_flow import MessageValidationFlow
from ..flows.validation.tool_validation_flow import ToolValidationFlow
from ..flows.validation.conversation_validation_flow import ConversationValidationFlow
from ..core.logging_config import get_logger

logger = get_logger("coordinators.validation")


class ValidationCoordinator:
    """Coordinates all validation operations using flow-based architecture."""
    
    _instance: Optional["ValidationCoordinator"] = None
    
    def __init__(self):
        """Initialize validation coordinator."""
        if ValidationCoordinator._instance is not None:
            raise RuntimeError("ValidationCoordinator is a singleton")
        
        self.message_flow = MessageValidationFlow()
        self.tool_flow = ToolValidationFlow()
        self.conversation_flow = ConversationValidationFlow()
        
        logger.info("ValidationCoordinator initialized")
    
    @classmethod
    def get_instance(cls) -> "ValidationCoordinator":
        """Get the singleton instance of ValidationCoordinator."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    # Message Validation Methods
    async def validate_message(self, data: Any, **kwargs) -> ValidationResult:
        """Validate message data using message validation flow.
        
        Args:
            data: Message data to validate
            **kwargs: Additional validation parameters
            
        Returns:
            ValidationResult with validation details
        """
        try:
            logger.debug("Coordinating message validation")
            return await self.message_flow.validate_message(data, **kwargs)
        except Exception as e:
            logger.error("Message validation coordination failed", error=str(e), exc_info=True)
            raise
    
    async def validate_messages_request(self, data: Any, **kwargs) -> ValidationResult:
        """Validate messages request data using message validation flow.
        
        Args:
            data: Messages request data to validate
            **kwargs: Additional validation parameters
            
        Returns:
            ValidationResult with validation details
        """
        try:
            logger.debug("Coordinating messages request validation")
            return await self.message_flow.validate_messages_request(data, **kwargs)
        except Exception as e:
            logger.error("Messages request validation coordination failed", error=str(e), exc_info=True)
            raise
    
    async def validate_content_blocks(self, content_blocks: List[dict]) -> ValidationResult:
        """Validate content blocks using message validation flow.
        
        Args:
            content_blocks: List of content blocks to validate
            
        Returns:
            ValidationResult with validation details
        """
        try:
            logger.debug("Coordinating content blocks validation", block_count=len(content_blocks))
            return await self.message_flow.validate_content_blocks(content_blocks)
        except Exception as e:
            logger.error("Content blocks validation coordination failed", error=str(e), exc_info=True)
            raise
    
    # Tool Validation Methods
    async def validate_tool(self, data: Any, **kwargs) -> ValidationResult:
        """Validate tool data using tool validation flow.
        
        Args:
            data: Tool data to validate
            **kwargs: Additional validation parameters
            
        Returns:
            ValidationResult with validation details
        """
        try:
            logger.debug("Coordinating tool validation")
            return await self.tool_flow.validate_tool(data, **kwargs)
        except Exception as e:
            logger.error("Tool validation coordination failed", error=str(e), exc_info=True)
            raise
    
    async def validate_tool_flow(
        self,
        messages: List[Message],
        available_tools: List[Tool]
    ) -> ToolValidationResult:
        """Validate tool flow using tool validation flow.
        
        Args:
            messages: List of conversation messages
            available_tools: List of available tools
            
        Returns:
            ToolValidationResult with orphaned tools and validation errors
        """
        try:
            logger.debug("Coordinating tool flow validation")
            return await self.tool_flow.validate_tool_flow(messages, available_tools)
        except Exception as e:
            logger.error("Tool flow validation coordination failed", error=str(e), exc_info=True)
            raise
    
    async def batch_validate_tools(self, tools: List[Tool]) -> List[ValidationResult]:
        """Validate multiple tools in batch using tool validation flow.
        
        Args:
            tools: List of tools to validate
            
        Returns:
            List of ValidationResult objects
        """
        try:
            logger.debug("Coordinating batch tool validation", tool_count=len(tools))
            return await self.tool_flow.batch_validate_tools(tools)
        except Exception as e:
            logger.error("Batch tool validation coordination failed", error=str(e), exc_info=True)
            raise
    
    # Conversation Validation Methods
    async def validate_conversation_flow(self, data: Any, **kwargs) -> ValidationResult:
        """Validate conversation flow using conversation validation flow.
        
        Args:
            data: Conversation flow data to validate
            **kwargs: Additional validation parameters
            
        Returns:
            ValidationResult with validation details
        """
        try:
            logger.debug("Coordinating conversation flow validation")
            return await self.conversation_flow.validate_conversation_flow(data, **kwargs)
        except Exception as e:
            logger.error("Conversation flow validation coordination failed", error=str(e), exc_info=True)
            raise
    
    async def validate_message_role_sequence(self, messages: List[Message]) -> ValidationResult:
        """Validate message role sequence using conversation validation flow.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            ValidationResult with role sequence validation details
        """
        try:
            logger.debug("Coordinating role sequence validation", message_count=len(messages))
            return await self.conversation_flow.validate_message_role_sequence(messages)
        except Exception as e:
            logger.error("Role sequence validation coordination failed", error=str(e), exc_info=True)
            raise
    
    # Comprehensive Validation Methods
    async def comprehensive_message_validation(
        self,
        messages: List[Message],
        available_tools: Optional[List[Tool]] = None
    ) -> Dict[str, ValidationResult]:
        """Perform comprehensive validation across all validation domains.
        
        Args:
            messages: List of conversation messages
            available_tools: Optional list of available tools
            
        Returns:
            Dictionary with validation results for each domain
        """
        try:
            logger.info("Starting comprehensive message validation",
                       message_count=len(messages),
                       has_tools=available_tools is not None)
            
            results = {}
            
            # Validate conversation structure and flow
            results["conversation"] = await self.conversation_flow.comprehensive_conversation_validation(messages)
            
            # Validate individual messages
            message_results = []
            for i, message in enumerate(messages):
                try:
                    result = await self.validate_message(message)
                    message_results.append(result)
                except Exception as e:
                    logger.error(f"Failed to validate message {i}", error=str(e))
                    from ..tasks.validation.schema_validation_tasks import create_validation_result
                    message_results.append(create_validation_result(
                        False,
                        errors=[f"Message {i} validation failed: {str(e)}"]
                    ))
            
            # Combine message validation results
            all_message_errors = []
            all_message_warnings = []
            for i, result in enumerate(message_results):
                all_message_errors.extend([f"Message {i}: {error}" for error in result.errors])
                all_message_warnings.extend([f"Message {i}: {warning}" for warning in result.warnings])
            
            from ..tasks.validation.schema_validation_tasks import create_validation_result
            results["messages"] = create_validation_result(
                is_valid=len(all_message_errors) == 0,
                errors=all_message_errors,
                warnings=all_message_warnings
            )
            
            # Validate tool flow if tools are provided
            if available_tools:
                try:
                    results["tools"] = await self.tool_flow.validate_tool_flow(messages, available_tools)
                except Exception as e:
                    logger.error("Tool flow validation failed in comprehensive validation", error=str(e))
                    results["tools"] = create_validation_result(
                        False,
                        errors=[f"Tool flow validation failed: {str(e)}"]
                    )
            
            # Log summary
            total_errors = sum(len(getattr(r, 'errors', [])) for r in results.values())
            total_warnings = sum(len(getattr(r, 'warnings', [])) for r in results.values())
            
            logger.info("Comprehensive message validation completed",
                       domains_validated=len(results),
                       total_errors=total_errors,
                       total_warnings=total_warnings)
            
            return results
            
        except Exception as e:
            logger.error("Comprehensive message validation coordination failed", error=str(e), exc_info=True)
            raise
    
    async def validate_api_request(
        self,
        request_data: dict,
        available_tools: Optional[List[Tool]] = None
    ) -> ValidationResult:
        """Validate a complete API request including messages and tools.
        
        Args:
            request_data: Complete API request data
            available_tools: Optional list of available tools
            
        Returns:
            ValidationResult with overall validation status
        """
        try:
            logger.debug("Coordinating API request validation")
            
            # Validate the request structure first
            request_result = await self.validate_messages_request(request_data)
            
            if not request_result.is_valid:
                return request_result
            
            # Extract messages for further validation
            messages = request_data.get("messages", [])
            if not messages:
                from ..tasks.validation.schema_validation_tasks import create_validation_result
                return create_validation_result(
                    False,
                    errors=["No messages found in request"]
                )
            
            # Perform comprehensive validation
            comprehensive_results = await self.comprehensive_message_validation(messages, available_tools)
            
            # Combine all errors and warnings
            all_errors = request_result.errors.copy()
            all_warnings = request_result.warnings.copy()
            
            for domain, result in comprehensive_results.items():
                if hasattr(result, 'errors'):
                    all_errors.extend([f"{domain}: {error}" for error in result.errors])
                if hasattr(result, 'warnings'):
                    all_warnings.extend([f"{domain}: {warning}" for warning in result.warnings])
            
            # Create final result
            from ..tasks.validation.schema_validation_tasks import create_validation_result
            final_result = create_validation_result(
                is_valid=len(all_errors) == 0,
                errors=all_errors,
                warnings=all_warnings
            )
            
            logger.info("API request validation completed",
                       is_valid=final_result.is_valid,
                       total_errors=len(all_errors),
                       total_warnings=len(all_warnings))
            
            return final_result
            
        except Exception as e:
            logger.error("API request validation coordination failed", error=str(e), exc_info=True)
            raise


# Global instance for backward compatibility
_validation_coordinator_instance: Optional[ValidationCoordinator] = None


def get_validation_coordinator() -> ValidationCoordinator:
    """Get the global validation coordinator instance."""
    global _validation_coordinator_instance
    if _validation_coordinator_instance is None:
        _validation_coordinator_instance = ValidationCoordinator.get_instance()
    return _validation_coordinator_instance