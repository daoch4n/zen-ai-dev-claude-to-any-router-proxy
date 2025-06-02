"""Unit tests for service layer components."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.services.base import BaseService, ValidationService, ConversionService, InstructorService
from src.services.validation import (
    MessageValidationService, ToolValidationService, ConversationFlowValidationService
)
from src.services.conversion import (
    AnthropicToLiteLLMConverter, LiteLLMToAnthropicConverter,
    ModelMappingService, StructuredOutputService
)
from src.models.anthropic import Message, MessagesRequest, Tool
from src.models.litellm import LiteLLMMessage, LiteLLMRequest
from src.models.instructor import ValidationResult, ConversionResult, ToolValidationResult, StructuredResponse
from src.utils.instructor_client import InstructorClient


class TestBaseService:
    """Test BaseService class."""
    
    def test_base_service_initialization(self):
        """Test base service initialization."""
        service = BaseService("TestService")
        assert service.name == "TestService"
        assert service.logger is not None
    
    def test_log_operation(self):
        """Test operation logging."""
        service = BaseService("TestService")
        
        # Should not raise an exception
        service.log_operation("test_operation", True, param1="value1")
        service.log_operation("failed_operation", False, error="test error")


class TestValidationService:
    """Test ValidationService base class."""
    
    def test_create_validation_result(self):
        """Test validation result creation."""
        service = MessageValidationService()
        
        result = service.create_validation_result(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
            suggestions=["Suggestion 1"]
        )
        
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
        assert len(result.suggestions) == 1


class TestMessageValidationService:
    """Test MessageValidationService."""
    
    def setup_method(self):
        """Set up test method."""
        self.service = MessageValidationService()
    
    def test_validate_valid_message_dict(self):
        """Test validation of valid message dictionary."""
        message_data = {
            "role": "user",
            "content": "Hello, how are you?"
        }
        
        result = self.service.validate(message_data)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_valid_message_object(self):
        """Test validation of valid Message object."""
        message = Message(role="user", content="Hello, how are you?")
        
        result = self.service.validate(message)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_invalid_message_missing_role(self):
        """Test validation of message missing role."""
        message_data = {
            "content": "Hello, how are you?"
        }
        
        result = self.service.validate(message_data)
        
        assert not result.is_valid
        assert "Missing required field: role" in result.errors
    
    def test_validate_invalid_message_missing_content(self):
        """Test validation of message missing content."""
        message_data = {
            "role": "user"
        }
        
        result = self.service.validate(message_data)
        
        assert not result.is_valid
        assert "Missing required field: content" in result.errors
    
    def test_validate_invalid_role(self):
        """Test validation of invalid role."""
        message_data = {
            "role": "invalid_role",
            "content": "Hello"
        }
        
        result = self.service.validate(message_data)
        
        assert not result.is_valid
        assert any("Invalid role" in error for error in result.errors)
    
    def test_validate_empty_content(self):
        """Test validation of empty content."""
        message_data = {
            "role": "user",
            "content": ""
        }
        
        result = self.service.validate(message_data)
        
        assert not result.is_valid
        assert "Content cannot be empty" in result.errors
    
    def test_validate_complex_content_blocks(self):
        """Test validation of complex content blocks."""
        message_data = {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "I'll help you with that."},
                {"type": "tool_use", "id": "tool_123", "name": "get_weather", "input": {"location": "SF"}}
            ]
        }
        
        result = self.service.validate(message_data)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_invalid_content_blocks(self):
        """Test validation of invalid content blocks."""
        message_data = {
            "role": "assistant",
            "content": [
                {"type": "text"},  # Missing text field
                {"type": "tool_use", "name": "get_weather"}  # Missing id and input
            ]
        }
        
        result = self.service.validate(message_data)
        
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_validate_non_dict_data(self):
        """Test validation of non-dictionary data."""
        result = self.service.validate("invalid_data")
        
        assert not result.is_valid
        assert "Data must be a dictionary or Message object" in result.errors


class TestToolValidationService:
    """Test ToolValidationService."""
    
    def setup_method(self):
        """Set up test method."""
        self.service = ToolValidationService()
    
    def test_validate_valid_tool_dict(self):
        """Test validation of valid tool dictionary."""
        tool_data = {
            "name": "get_weather",
            "description": "Get weather information",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
        
        result = self.service.validate(tool_data)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_valid_tool_object(self):
        """Test validation of valid Tool object."""
        tool = Tool(
            name="get_weather",
            description="Get weather information",
            input_schema={
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"]
            }
        )
        
        result = self.service.validate(tool)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_tool_missing_name(self):
        """Test validation of tool missing name."""
        tool_data = {
            "input_schema": {"type": "object"}
        }
        
        result = self.service.validate(tool_data)
        
        assert not result.is_valid
        assert "Missing required field: name" in result.errors
    
    def test_validate_tool_missing_schema(self):
        """Test validation of tool missing input schema."""
        tool_data = {
            "name": "get_weather"
        }
        
        result = self.service.validate(tool_data)
        
        assert not result.is_valid
        assert "Missing required field: input_schema" in result.errors
    
    def test_validate_tool_missing_description(self):
        """Test validation of tool missing description (warning)."""
        tool_data = {
            "name": "get_weather",
            "input_schema": {"type": "object"}
        }
        
        result = self.service.validate(tool_data)
        
        assert result.is_valid  # Still valid, just a warning
        assert len(result.warnings) > 0
        assert any("missing description" in warning for warning in result.warnings)
    
    def test_validate_tool_flow_valid(self):
        """Test validation of valid tool flow."""
        messages = [
            Message(role="user", content="Get weather for SF"),
            Message(role="assistant", content=[
                {"type": "text", "text": "I'll get the weather for you."},
                {"type": "tool_use", "id": "tool_123", "name": "get_weather", "input": {"location": "SF"}}
            ]),
            Message(role="user", content=[
                {"type": "tool_result", "tool_use_id": "tool_123", "content": "Sunny, 22°C"}
            ])
        ]
        
        tools = [Tool(name="get_weather", input_schema={"type": "object"})]
        
        result = self.service.validate_tool_flow(messages, tools)
        
        assert isinstance(result, ToolValidationResult)
        assert result.is_valid
        assert len(result.orphaned_tools) == 0
        assert len(result.missing_results) == 0
    
    def test_validate_tool_flow_orphaned_tools(self):
        """Test validation of tool flow with orphaned tools."""
        messages = [
            Message(role="user", content="Get weather for SF"),
            Message(role="assistant", content=[
                {"type": "tool_use", "id": "tool_123", "name": "get_weather", "input": {"location": "SF"}}
            ])
            # Missing tool result
        ]
        
        tools = [Tool(name="get_weather", input_schema={"type": "object"})]
        
        result = self.service.validate_tool_flow(messages, tools)
        
        assert not result.is_valid
        assert len(result.orphaned_tools) == 1
        assert "tool_123" in result.orphaned_tools


class TestConversationFlowValidationService:
    """Test ConversationFlowValidationService."""
    
    def setup_method(self):
        """Set up test method."""
        self.service = ConversationFlowValidationService()
    
    def test_validate_valid_conversation(self):
        """Test validation of valid conversation flow."""
        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!"),
            Message(role="user", content="How are you?"),
            Message(role="assistant", content="I'm doing well, thanks!")
        ]
        
        result = self.service.validate(messages)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_empty_conversation(self):
        """Test validation of empty conversation."""
        result = self.service.validate([])
        
        assert not result.is_valid
        assert "Conversation cannot be empty" in result.errors
    
    def test_validate_conversation_not_starting_with_user(self):
        """Test validation of conversation not starting with user."""
        messages = [
            Message(role="assistant", content="Hello"),
            Message(role="user", content="Hi")
        ]
        
        result = self.service.validate(messages)
        
        assert not result.is_valid
        assert any("should start with a user message" in error for error in result.errors)
    
    def test_validate_conversation_flow_detailed(self):
        """Test detailed conversation flow validation."""
        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!")
        ]
        
        flow_result = self.service.validate_conversation_flow(messages)
        
        assert flow_result.is_valid
        assert flow_result.role_sequence_valid
        assert flow_result.tool_flow_valid


class TestAnthropicToLiteLLMConverter:
    """Test AnthropicToLiteLLMConverter."""
    
    def setup_method(self):
        """Set up test method."""
        self.converter = AnthropicToLiteLLMConverter()
    
    def test_convert_simple_request(self):
        """Test conversion of simple Anthropic request."""
        request = MessagesRequest(
            model="anthropic/claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[Message(role="user", content="Hello")]
        )
        
        result = self.converter.convert(request)
        
        assert isinstance(result, ConversionResult)
        assert result.success
        assert result.converted_data is not None
        # Model gets mapped: anthropic/claude-3-5-sonnet-20241022 -> anthropic/claude-3.7-sonnet -> openrouter/anthropic/claude-3.7-sonnet
        assert result.converted_data["model"] == "openrouter/anthropic/claude-3.7-sonnet"
        assert len(result.converted_data["messages"]) == 1
    
    def test_convert_request_with_tools(self):
        """Test conversion of request with tools."""
        tool = Tool(
            name="get_weather",
            description="Get weather info",
            input_schema={"type": "object", "properties": {"location": {"type": "string"}}}
        )
        
        request = MessagesRequest(
            model="anthropic/claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[Message(role="user", content="Get weather for SF")],
            tools=[tool]
        )
        
        result = self.converter.convert(request)
        
        assert result.success
        assert "tools" in result.converted_data
        assert len(result.converted_data["tools"]) == 1
        assert result.converted_data["tools"][0]["type"] == "function"
    
    def test_convert_complex_message(self):
        """Test conversion of complex message with tool use."""
        message = Message(
            role="assistant",
            content=[
                {"type": "text", "text": "I'll get the weather for you."},
                {"type": "tool_use", "id": "tool_123", "name": "get_weather", "input": {"location": "SF"}}
            ]
        )
        
        request = MessagesRequest(
            model="anthropic/claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[message]
        )
        
        result = self.converter.convert(request)
        
        assert result.success
        litellm_message = result.converted_data["messages"][0]
        assert "tool_calls" in litellm_message
        assert len(litellm_message["tool_calls"]) == 1


class TestModelMappingService:
    """Test ModelMappingService."""
    
    def setup_method(self):
        """Set up test method."""
        self.service = ModelMappingService()
    
    def test_map_big_model(self):
        """Test mapping of 'big' model."""
        result = self.service.map_model("big")
        
        assert result.original_model == "big"
        assert result.mapping_applied
        assert result.mapping_type == "big"
    
    def test_map_small_model(self):
        """Test mapping of 'small' model."""
        result = self.service.map_model("small")
        
        assert result.original_model == "small"
        assert result.mapping_applied
        assert result.mapping_type == "small"
    
    def test_map_passthrough_model(self):
        """Test passthrough of unmapped model."""
        model_name = "some-unknown-model-that-has-no-mapping"
        result = self.service.map_model(model_name)
        
        assert result.original_model == model_name
        assert result.mapped_model == model_name
        assert not result.mapping_applied
        assert result.mapping_type == "passthrough"
    
    def test_update_request_with_mapping(self):
        """Test updating request with model mapping."""
        request_data = {"model": "big", "max_tokens": 1000}
        mapping_result = self.service.map_model("big")
        
        updated_request = self.service.update_request_with_mapping(request_data, mapping_result)
        
        assert updated_request["model"] != "big"
        assert updated_request["original_model"] == "big"
        assert updated_request["max_tokens"] == 1000


class TestStructuredOutputService:
    """Test StructuredOutputService."""
    
    def setup_method(self):
        """Set up test method."""
        self.service = StructuredOutputService()
    
    @patch('src.services.conversion._coordinator.create_validation_summary')
    def test_create_validation_summary(self, mock_create_summary):
        """Test creation of validation summary."""
        # Mock the coordinator method - setup async coroutine
        from unittest.mock import AsyncMock
        mock_create_summary.return_value = {
            "is_valid": False,
            "errors": ["Test error"],
            "warnings": [],
            "suggestions": ["Fix the error"]
        }
        
        validation_results = [
            {"is_valid": False, "errors": ["Test error"]},
            {"is_valid": True, "errors": []}
        ]
        
        summary = self.service.create_validation_summary(validation_results)
        
        assert isinstance(summary, dict)
        # Note: The method is called through asyncio.run(), so we can't easily verify call count
        assert summary["is_valid"] == False
        assert "Test error" in summary["errors"]


class TestInstructorService:
    """Test InstructorService base functionality."""
    
    def setup_method(self):
        """Set up test method."""
        # We'll mock the instructor client in each test method
        pass
    
    @patch('src.utils.instructor_client.instructor_client')
    def test_create_structured_output(self, mock_client):
        """Test structured output creation."""
        # Create service with mocked client
        service = InstructorService("TestInstructor")
        
        # Mock the instructor client methods
        expected_response = StructuredResponse(
            content="Test response",
            confidence=0.95
        )
        mock_client.create_structured_completion.return_value = expected_response
        
        result = service.create_structured_output(
            model="anthropic/claude-3.7-sonnet",
            messages=[{"role": "user", "content": "test"}],
            response_model=StructuredResponse
        )
        
        assert isinstance(result, StructuredResponse)
        assert result.content == "Test response"
        mock_client.create_structured_completion.assert_called()
    
    @patch('src.utils.instructor_client.instructor_client')
    def test_validate_with_instructor(self, mock_client):
        """Test validation with Instructor."""
        # Create service with mocked client
        service = InstructorService("TestInstructor")
        
        # Mock validation response
        expected_result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            suggestions=[]
        )
        mock_client.validate_with_instructor.return_value = expected_result
        
        result = service.validate_with_instructor(
            data={"test": "data"},
            validation_model=StructuredResponse
        )
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid
        mock_client.validate_with_instructor.assert_called()
    
    @patch('src.utils.instructor_client.instructor_client')
    def test_extract_structured_data(self, mock_client):
        """Test structured data extraction."""
        # Create service with mocked client
        service = InstructorService("TestInstructor")
        
        # Mock extraction response
        expected_response = StructuredResponse(
            content="Extracted data",
            confidence=0.85
        )
        mock_client.extract_structured_data.return_value = expected_response
        
        result = service.extract_structured_data(
            text="Some text to extract from",
            extraction_model=StructuredResponse
        )
        
        assert isinstance(result, StructuredResponse)
        assert result.content == "Extracted data"
        mock_client.extract_structured_data.assert_called()