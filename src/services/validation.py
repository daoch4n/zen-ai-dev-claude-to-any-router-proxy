"""Validation services with Instructor integration."""

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

class MessageValidationService(ValidationService[Message], InstructorService):
    """Service for validating Anthropic messages with Instructor enhancement."""
    
    def __init__(self):
        """Initialize message validation service."""
        ValidationService.__init__(self, "MessageValidation")
        InstructorService.__init__(self, "MessageValidation")
        self.logger = get_logger("validation.message")
        self.context_manager = ContextManager()
    
    def validate(self, data: Any, **kwargs) -> ValidationResult:
        """Validate message data with comprehensive checks."""
        try:
            # Basic validation
            if not isinstance(data, (dict, Message)):
                return self.create_validation_result(
                    False,
                    errors=["Data must be a dictionary or Message object"],
                    suggestions=["Provide valid message data with role and content"]
                )
            
            # Convert to dict if Message object
            if isinstance(data, Message):
                message_dict = data.model_dump()
            else:
                message_dict = data
            
            errors = []
            warnings = []
            suggestions = []
            
            # Validate required fields
            if "role" not in message_dict:
                errors.append("Missing required field: role")
            elif message_dict["role"] not in ["user", "assistant"]:
                errors.append(f"Invalid role: {message_dict['role']}. Must be 'user' or 'assistant'")
            
            if "content" not in message_dict:
                errors.append("Missing required field: content")
            elif not message_dict["content"]:
                errors.append("Content cannot be empty")
            
            # Validate content structure
            content = message_dict.get("content")
            if isinstance(content, list):
                content_errors = self._validate_content_blocks(content)
                errors.extend(content_errors)
            
            # Check for tool-related issues
            if isinstance(content, list):
                tool_warnings = self._check_tool_usage_patterns(content)
                warnings.extend(tool_warnings)
            
            # Generate suggestions
            if errors:
                suggestions.append("Fix validation errors before proceeding")
            if warnings:
                suggestions.append("Review warnings for potential improvements")
            
            is_valid = len(errors) == 0
            
            self.log_operation(
                "message_validation",
                is_valid,
                role=message_dict.get("role"),
                content_type="list" if isinstance(content, list) else "string",
                error_count=len(errors),
                warning_count=len(warnings)
            )
            
            return self.create_validation_result(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error("Message validation failed",
                             error=str(e),
                             operation="message_validation",
                             exc_info=True)
            return self.create_validation_result(
                False,
                errors=[f"Validation failed: {str(e)}"],
                suggestions=["Check message format and try again"]
            )
    
    def validate_messages_request(self, request: MessagesRequest) -> MessagesRequest:
        """Validate a MessagesRequest and return it if valid."""
        try:
            # Validate the request structure
            if not request:
                raise ValueError("Request cannot be None")
            
            if not request.messages:
                raise ValueError("Request must contain at least one message")
            
            # Validate each message
            validation_errors = []
            for i, message in enumerate(request.messages):
                validation_result = self.validate(message)
                if not validation_result.is_valid:
                    validation_errors.extend([
                        f"Message {i}: {error}" for error in validation_result.errors
                    ])
            
            # Check for validation errors
            if validation_errors:
                error_message = f"Request validation failed: {'; '.join(validation_errors)}"
                self.logger.error("Messages request validation failed",
                                error=error_message,
                                message_count=len(request.messages))
                raise ValueError(error_message)
            
            # Validate conversation flow if multiple messages
            if len(request.messages) > 1:
                flow_validator = ConversationFlowValidationService()
                flow_result = flow_validator.validate_conversation_flow(request.messages)
                if not flow_result.is_valid:
                    error_message = f"Conversation flow validation failed: {'; '.join(flow_result.flow_errors)}"
                    self.logger.error("Conversation flow validation failed",
                                    error=error_message,
                                    message_count=len(request.messages))
                    raise ValueError(error_message)
            
            self.logger.info("Messages request validation completed successfully",
                           message_count=len(request.messages),
                           model=getattr(request, 'model', 'unknown'))
            
            return request
            
        except Exception as e:
            self.logger.error("Messages request validation failed",
                            error=str(e),
                            operation="validate_messages_request",
                            exc_info=True)
            raise ValueError(f"Request validation failed: {str(e)}")
    
    def _validate_content_blocks(self, content_blocks: List[Dict[str, Any]]) -> List[str]:
        """Validate content blocks structure."""
        errors = []
        
        for i, block in enumerate(content_blocks):
            if not isinstance(block, dict):
                errors.append(f"Content block {i} must be a dictionary")
                continue
            
            block_type = block.get("type")
            if not block_type:
                errors.append(f"Content block {i} missing 'type' field")
                continue
            
            # Validate specific block types
            if block_type == "text":
                if "text" not in block:
                    errors.append(f"Text block {i} missing 'text' field")
                elif not block["text"]:
                    errors.append(f"Text block {i} has empty text")
            
            elif block_type == "tool_use":
                if "name" not in block:
                    errors.append(f"Tool use block {i} missing 'name' field")
                if "input" not in block:
                    errors.append(f"Tool use block {i} missing 'input' field")
                if "id" not in block:
                    errors.append(f"Tool use block {i} missing 'id' field")
            
            elif block_type == "tool_result":
                if "tool_use_id" not in block:
                    errors.append(f"Tool result block {i} missing 'tool_use_id' field")
                if "content" not in block:
                    errors.append(f"Tool result block {i} missing 'content' field")
            
            else:
                errors.append(f"Unknown content block type: {block_type}")
        
        return errors
    
    def _check_tool_usage_patterns(self, content_blocks: List[Dict[str, Any]]) -> List[str]:
        """Check for common tool usage pattern issues."""
        warnings = []
        
        tool_uses = [block for block in content_blocks if block.get("type") == "tool_use"]
        tool_results = [block for block in content_blocks if block.get("type") == "tool_result"]
        
        # Check for tool uses without IDs
        for tool_use in tool_uses:
            if not tool_use.get("id"):
                warnings.append("Tool use block missing ID - may cause orphaned tool issues")
        
        # Check for empty tool inputs
        for tool_use in tool_uses:
            if not tool_use.get("input"):
                warnings.append(f"Tool '{tool_use.get('name')}' has empty input")
        
        return warnings

class ToolValidationService(ValidationService[Tool], InstructorService):
    """Service for validating tools and detecting orphaned tools."""
    
    def __init__(self):
        """Initialize tool validation service."""
        ValidationService.__init__(self, "ToolValidation")
        InstructorService.__init__(self, "ToolValidation")
        self.logger = get_logger("validation.tool")
        self.context_manager = ContextManager()
    
    def validate(self, data: Any, **kwargs) -> ValidationResult:
        """Validate tool data."""
        try:
            if not isinstance(data, (dict, Tool)):
                return self.create_validation_result(
                    False,
                    errors=["Data must be a dictionary or Tool object"]
                )
            
            # Convert to dict if Tool object
            if isinstance(data, Tool):
                tool_dict = data.model_dump()
            else:
                tool_dict = data
            
            errors = []
            warnings = []
            suggestions = []
            
            # Validate required fields
            if "name" not in tool_dict:
                errors.append("Missing required field: name")
            elif not tool_dict["name"]:
                errors.append("Tool name cannot be empty")
            
            if "input_schema" not in tool_dict:
                errors.append("Missing required field: input_schema")
            else:
                schema_errors = self._validate_input_schema(tool_dict["input_schema"])
                errors.extend(schema_errors)
            
            # Check description
            if not tool_dict.get("description"):
                warnings.append("Tool missing description - recommended for better AI understanding")
                suggestions.append("Add a clear description of what the tool does")
            
            is_valid = len(errors) == 0
            
            self.log_operation(
                "tool_validation",
                is_valid,
                tool_name=tool_dict.get("name"),
                has_description=bool(tool_dict.get("description")),
                error_count=len(errors)
            )
            
            return self.create_validation_result(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error("Tool validation failed",
                             error=str(e),
                             operation="tool_validation",
                             exc_info=True)
            return self.create_validation_result(
                False,
                errors=[f"Tool validation failed: {str(e)}"]
            )
    
    def validate_tool_flow(
        self,
        messages: List[Message],
        available_tools: List[Tool]
    ) -> ToolValidationResult:
        """Validate tool flow across messages to detect orphaned tools."""
        try:
            tool_uses = {}
            tool_results = {}
            orphaned_tools = []
            missing_results = []
            validation_errors = []
            
            # Extract tool uses and results from messages
            for msg_idx, message in enumerate(messages):
                if isinstance(message.content, list):
                    for block in message.content:
                        if hasattr(block, 'type'):
                            if block.type == "tool_use":
                                tool_id = getattr(block, 'id', None)
                                if tool_id:
                                    tool_uses[tool_id] = {
                                        "message_index": msg_idx,
                                        "name": getattr(block, 'name', ''),
                                        "input": getattr(block, 'input', {})
                                    }
                                else:
                                    validation_errors.append(f"Tool use in message {msg_idx} missing ID")
                            
                            elif block.type == "tool_result":
                                tool_use_id = getattr(block, 'tool_use_id', None)
                                if tool_use_id:
                                    tool_results[tool_use_id] = {
                                        "message_index": msg_idx,
                                        "content": getattr(block, 'content', '')
                                    }
                                else:
                                    validation_errors.append(f"Tool result in message {msg_idx} missing tool_use_id")
            
            # Find orphaned tools (tool uses without results)
            for tool_id, tool_use in tool_uses.items():
                if tool_id not in tool_results:
                    orphaned_tools.append(tool_id)
            
            # Find missing results (tool results without corresponding uses)
            for tool_id in tool_results:
                if tool_id not in tool_uses:
                    missing_results.append(tool_id)
            
            # Generate suggestions
            suggestions = []
            if orphaned_tools:
                suggestions.append("Add tool_result blocks for orphaned tool uses")
            if missing_results:
                suggestions.append("Remove tool_result blocks without corresponding tool_use")
            if validation_errors:
                suggestions.append("Fix tool ID and reference issues")
            
            is_valid = (
                len(orphaned_tools) == 0 and 
                len(missing_results) == 0 and 
                len(validation_errors) == 0
            )
            
            result = ToolValidationResult(
                is_valid=is_valid,
                orphaned_tools=orphaned_tools,
                missing_results=missing_results,
                validation_errors=validation_errors,
                suggestions=suggestions
            )
            
            self.log_operation(
                "tool_flow_validation",
                is_valid,
                total_tool_uses=len(tool_uses),
                total_tool_results=len(tool_results),
                orphaned_count=len(orphaned_tools),
                missing_results_count=len(missing_results)
            )
            
            return result
            
        except Exception as e:
            self.logger.error("Tool flow validation failed",
                             error=str(e),
                             operation="tool_flow_validation",
                             exc_info=True)
            raise ToolValidationError(f"Tool flow validation failed: {e}")
    
    def _validate_input_schema(self, schema: Dict[str, Any]) -> List[str]:
        """Validate tool input schema."""
        errors = []
        
        if not isinstance(schema, dict):
            errors.append("Input schema must be a dictionary")
            return errors
        
        # Check for required schema fields
        if "type" not in schema:
            errors.append("Input schema missing 'type' field")
        elif schema["type"] != "object":
            errors.append("Input schema type should be 'object' for tool parameters")
        
        # Validate properties if present
        if "properties" in schema:
            if not isinstance(schema["properties"], dict):
                errors.append("Schema 'properties' must be a dictionary")
            else:
                for prop_name, prop_def in schema["properties"].items():
                    if not isinstance(prop_def, dict):
                        errors.append(f"Property '{prop_name}' definition must be a dictionary")
                    elif "type" not in prop_def:
                        errors.append(f"Property '{prop_name}' missing 'type' field")
        
        return errors

class ConversationFlowValidationService(ValidationService[List[Message]], InstructorService):
    """Service for validating conversation flow patterns."""
    
    def __init__(self):
        """Initialize conversation flow validation service."""
        ValidationService.__init__(self, "ConversationFlowValidation")
        InstructorService.__init__(self, "ConversationFlowValidation")
        self.logger = get_logger("validation.conversation_flow")
        self.context_manager = ContextManager()
    
    def validate(self, data: Any, **kwargs) -> ValidationResult:
        """Validate conversation flow."""
        try:
            if not isinstance(data, list):
                return self.create_validation_result(
                    False,
                    errors=["Data must be a list of messages"]
                )
            
            messages = data
            flow_result = self.validate_conversation_flow(messages)
            
            return self.create_validation_result(
                is_valid=flow_result.is_valid,
                errors=flow_result.flow_errors,
                suggestions=flow_result.suggestions
            )
            
        except Exception as e:
            self.logger.error("Conversation flow validation failed",
                             error=str(e),
                             operation="conversation_flow_validation",
                             exc_info=True)
            return self.create_validation_result(
                False,
                errors=[f"Conversation flow validation failed: {str(e)}"]
            )
    
    def validate_conversation_flow(self, messages: List[Message]) -> ConversationFlowResult:
        """Validate conversation flow patterns."""
        try:
            flow_errors = []
            suggestions = []
            
            if not messages:
                flow_errors.append("Conversation cannot be empty")
                return ConversationFlowResult(
                    is_valid=False,
                    flow_errors=flow_errors,
                    role_sequence_valid=False,
                    tool_flow_valid=False
                )
            
            # Validate role sequence
            role_sequence_valid = self._validate_role_sequence(messages, flow_errors)
            
            # Validate tool flow
            tool_flow_valid = self._validate_tool_flow_in_conversation(messages, flow_errors)
            
            # Generate suggestions
            if not role_sequence_valid:
                suggestions.append("Ensure proper alternating user/assistant roles")
            if not tool_flow_valid:
                suggestions.append("Check tool use and result pairing")
            
            is_valid = role_sequence_valid and tool_flow_valid and len(flow_errors) == 0
            
            result = ConversationFlowResult(
                is_valid=is_valid,
                flow_errors=flow_errors,
                role_sequence_valid=role_sequence_valid,
                tool_flow_valid=tool_flow_valid,
                suggestions=suggestions
            )
            
            self.log_operation(
                "conversation_flow_validation",
                is_valid,
                message_count=len(messages),
                role_sequence_valid=role_sequence_valid,
                tool_flow_valid=tool_flow_valid
            )
            
            return result
            
        except Exception as e:
            self.logger.error("Conversation flow validation execution failed",
                             error=str(e),
                             operation="conversation_flow_validation",
                             exc_info=True)
            raise ConversationFlowError(f"Conversation flow validation failed: {e}")
    
    def _validate_role_sequence(self, messages: List[Message], errors: List[str]) -> bool:
        """Validate role sequence in conversation."""
        if not messages:
            return True
        
        # First message should be user
        if messages[0].role != "user":
            errors.append("Conversation should start with a user message")
            return False
        
        # Check alternating pattern
        for i in range(1, len(messages)):
            current_role = messages[i].role
            previous_role = messages[i-1].role
            
            # Allow same role in some cases (e.g., tool results)
            if current_role == previous_role:
                # Check if this is a valid same-role sequence
                if not self._is_valid_same_role_sequence(messages[i-1], messages[i]):
                    errors.append(f"Invalid role sequence at message {i}: {previous_role} -> {current_role}")
                    return False
        
        return True
    
    def _is_valid_same_role_sequence(self, prev_msg: Message, curr_msg: Message) -> bool:
        """Check if same-role sequence is valid."""
        # User can send multiple messages (e.g., tool results)
        if curr_msg.role == "user":
            # Check if current message contains tool results
            if isinstance(curr_msg.content, list):
                return any(
                    hasattr(block, 'type') and block.type == "tool_result" 
                    for block in curr_msg.content
                )
        
        # Assistant can send multiple messages in some cases
        if curr_msg.role == "assistant":
            # Generally not recommended, but not invalid
            return True
        
        return False
    
    def _validate_tool_flow_in_conversation(self, messages: List[Message], errors: List[str]) -> bool:
        """Validate tool flow within conversation."""
        tool_uses = set()
        tool_results = set()
        
        for msg in messages:
            if isinstance(msg.content, list):
                for block in msg.content:
                    if hasattr(block, 'type'):
                        if block.type == "tool_use":
                            tool_id = getattr(block, 'id', None)
                            if tool_id:
                                tool_uses.add(tool_id)
                        elif block.type == "tool_result":
                            tool_use_id = getattr(block, 'tool_use_id', None)
                            if tool_use_id:
                                tool_results.add(tool_use_id)
        
        # Check for orphaned tools
        orphaned = tool_uses - tool_results
        if orphaned:
            errors.append(f"Orphaned tool uses found: {list(orphaned)}")
            return False
        
        # Check for results without uses
        missing_uses = tool_results - tool_uses
        if missing_uses:
            errors.append(f"Tool results without corresponding uses: {list(missing_uses)}")
            return False
        
        return True