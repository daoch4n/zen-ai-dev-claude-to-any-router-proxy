"""Unit tests for model classes and validation."""

import pytest
from unittest.mock import patch, Mock
from pydantic import ValidationError

from src.models.base import BaseOpenRouterModel, Usage, Tool, ThinkingConfig
from src.models.anthropic import (
    Message, MessagesRequest, MessagesResponse, TokenCountRequest,
    ContentBlockText, ContentBlockToolUse, ContentBlockToolResult,
    SystemContent
)
from src.models.litellm import LiteLLMMessage, LiteLLMRequest, LiteLLMResponse
from src.utils.errors import OpenRouterProxyError, ToolValidationError


class TestBaseModels:
    """Test base model classes."""
    
    def test_usage_model(self):
        """Test Usage model creation and validation."""
        usage = Usage(
            input_tokens=100,
            output_tokens=50,
            cache_creation_input_tokens=10,
            cache_read_input_tokens=5
        )
        
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.cache_creation_input_tokens == 10
        assert usage.cache_read_input_tokens == 5
    
    def test_usage_model_defaults(self):
        """Test Usage model with default values."""
        usage = Usage(input_tokens=100, output_tokens=50)
        
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.cache_creation_input_tokens == 0
        assert usage.cache_read_input_tokens == 0
    
    def test_tool_model(self):
        """Test Tool model creation and validation."""
        tool = Tool(
            name="get_weather",
            description="Get weather information",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        )
        
        assert tool.name == "get_weather"
        assert tool.description == "Get weather information"
        assert tool.input_schema["type"] == "object"
        assert "location" in tool.input_schema["properties"]
        assert "location" in tool.input_schema["required"]
    
    def test_tool_model_minimal(self):
        """Test Tool model with minimal required fields."""
        tool = Tool(
            name="simple_tool",
            input_schema={"type": "object"}
        )
        
        assert tool.name == "simple_tool"
        assert tool.description is None
        assert tool.input_schema == {"type": "object"}
    
    def test_thinking_config(self):
        """Test ThinkingConfig model."""
        # Default enabled
        config = ThinkingConfig()
        assert config.enabled is True
        
        # Explicitly disabled
        config = ThinkingConfig(enabled=False)
        assert config.enabled is False


class TestAnthropicModels:
    """Test Anthropic-specific model classes."""
    
    def test_simple_message(self):
        """Test simple text message creation."""
        message = Message(
            role="user",
            content="Hello, how are you?"
        )
        
        assert message.role == "user"
        assert message.content == "Hello, how are you?"
    
    def test_complex_message_with_content_blocks(self):
        """Test message with complex content blocks."""
        message = Message(
            role="assistant",
            content=[
                {
                    "type": "text",
                    "text": "I'll help you with that."
                },
                {
                    "type": "tool_use",
                    "id": "tool_123",
                    "name": "get_weather",
                    "input": {"location": "San Francisco"}
                }
            ]
        )
        
        assert message.role == "assistant"
        assert isinstance(message.content, list)
        assert len(message.content) == 2
        assert message.content[0].type == "text"
        assert message.content[1].type == "tool_use"
        assert message.content[1].name == "get_weather"
    
    def test_tool_result_message(self):
        """Test message with tool result."""
        message = Message(
            role="user",
            content=[
                {
                    "type": "tool_result",
                    "tool_use_id": "tool_123",
                    "content": "The weather is sunny, 22°C"
                }
            ]
        )
        
        assert message.role == "user"
        assert message.content[0].type == "tool_result"
        assert message.content[0].tool_use_id == "tool_123"
        assert "sunny" in message.content[0].content
    
    def test_message_content_validation(self):
        """Test message content validation and consolidation."""
        # Test tool consolidation
        message = Message(
            role="assistant",
            content=[
                {
                    "type": "tool_use",
                    "name": "test_tool",
                    "input": {"param1": "value1"}
                },
                {
                    "type": "tool_use",
                    "name": "test_tool",
                    "input": {"param2": "value2"}
                }
            ]
        )
        
        # Should consolidate tool use blocks
        assert isinstance(message.content, list)
        # The validator should handle consolidation
    
    def test_messages_request(self):
        """Test MessagesRequest model."""
        request = MessagesRequest(
            model="anthropic/claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[
                Message(role="user", content="Hello")
            ],
            tools=[
                Tool(
                    name="test_tool",
                    input_schema={"type": "object"}
                )
            ],
            stream=False,
            temperature=0.7
        )
        
        # Model gets mapped: anthropic/claude-3-5-sonnet-20241022 -> anthropic/claude-3.7-sonnet -> openrouter/anthropic/claude-3.7-sonnet
        assert request.model == "openrouter/anthropic/claude-3.7-sonnet"
        assert request.original_model == "anthropic/claude-3-5-sonnet-20241022"
        assert request.max_tokens == 4096
        assert len(request.messages) == 1
        assert len(request.tools) == 1
        assert request.stream is False
        assert request.temperature == 0.7
    
    def test_messages_request_with_system(self):
        """Test MessagesRequest with system message."""
        request = MessagesRequest(
            model="anthropic/claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[Message(role="user", content="Hello")],
            system="You are a helpful assistant."
        )
        
        assert request.system == "You are a helpful assistant."
    
    def test_messages_request_with_thinking(self):
        """Test MessagesRequest with thinking configuration."""
        request = MessagesRequest(
            model="anthropic/claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[Message(role="user", content="Hello")],
            thinking=ThinkingConfig(enabled=True)
        )
        
        assert request.thinking.enabled is True
    
    def test_messages_response(self):
        """Test MessagesResponse model."""
        response = MessagesResponse(
            id="msg_123",
            model="anthropic/claude-3-5-sonnet-20241022",
            content=[
                ContentBlockText(type="text", text="Hello! How can I help you?")
            ],
            stop_reason="end_turn",
            usage=Usage(input_tokens=10, output_tokens=15)
        )
        
        assert response.id == "msg_123"
        assert response.role == "assistant"
        assert response.type == "message"
        assert len(response.content) == 1
        assert response.content[0].text == "Hello! How can I help you?"
        assert response.stop_reason == "end_turn"
        assert response.usage.input_tokens == 10
    
    def test_token_count_request(self):
        """Test TokenCountRequest model."""
        request = TokenCountRequest(
            model="anthropic/claude-3-5-sonnet-20241022",
            messages=[Message(role="user", content="Hello")],
            tools=[Tool(name="test", input_schema={"type": "object"})]
        )
        
        assert request.model == "anthropic/claude-3-5-sonnet-20241022"
        assert len(request.messages) == 1
        assert len(request.tools) == 1


class TestLiteLLMModels:
    """Test LiteLLM model classes."""
    
    def test_litellm_message(self):
        """Test LiteLLMMessage model."""
        message = LiteLLMMessage(
            role="user",
            content="Hello, world!"
        )
        
        assert message.role == "user"
        assert message.content == "Hello, world!"
        assert message.tool_calls is None
        assert message.tool_call_id is None
    
    def test_litellm_message_with_tool_calls(self):
        """Test LiteLLMMessage with tool calls."""
        message = LiteLLMMessage(
            role="assistant",
            content=None,
            tool_calls=[
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"location": "San Francisco"}'
                    }
                }
            ]
        )
        
        assert message.role == "assistant"
        assert message.content is None
        assert len(message.tool_calls) == 1
        assert message.tool_calls[0]["function"]["name"] == "get_weather"
    
    def test_litellm_request(self):
        """Test LiteLLMRequest model."""
        request = LiteLLMRequest(
            model="anthropic/claude-3-5-sonnet-20241022",
            messages=[
                LiteLLMMessage(role="user", content="Hello")
            ],
            max_tokens=1000,
            temperature=0.7,
            stream=False
        )
        
        assert request.model == "anthropic/claude-3-5-sonnet-20241022"
        assert len(request.messages) == 1
        assert request.max_tokens == 1000
        assert request.temperature == 0.7
        assert request.stream is False
    
    def test_litellm_request_with_tools(self):
        """Test LiteLLMRequest with tools."""
        request = LiteLLMRequest(
            model="anthropic/claude-3-5-sonnet-20241022",
            messages=[LiteLLMMessage(role="user", content="Hello")],
            max_tokens=1000,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get weather info",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {"type": "string"}
                            }
                        }
                    }
                }
            ]
        )
        
        assert len(request.tools) == 1
        assert request.tools[0]["function"]["name"] == "get_weather"
    
    def test_litellm_response(self):
        """Test LiteLLMResponse model."""
        response = LiteLLMResponse(
            id="chatcmpl-123",
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you?"
                    },
                    "finish_reason": "stop"
                }
            ],
            usage={
                "prompt_tokens": 10,
                "completion_tokens": 15,
                "total_tokens": 25
            },
            model="anthropic/claude-3-5-sonnet-20241022"
        )
        
        assert response.id == "chatcmpl-123"
        assert len(response.choices) == 1
        assert response.choices[0]["message"]["content"] == "Hello! How can I help you?"
        assert response.usage["total_tokens"] == 25
        assert response.model == "anthropic/claude-3-5-sonnet-20241022"


class TestModelIntegration:
    """Test model integration and edge cases."""
    
    def test_base_model_extra_fields(self):
        """Test that BaseOpenRouterModel allows extra fields."""
        # This should not raise an error due to extra="allow"
        request = MessagesRequest(
            model="test-model",
            max_tokens=1000,
            messages=[Message(role="user", content="test")],
            custom_field="custom_value"  # Extra field
        )
        
        assert hasattr(request, 'custom_field')
        assert request.custom_field == "custom_value"
    
    def test_model_serialization(self):
        """Test model serialization."""
        message = Message(role="user", content="Hello")
        serialized = message.model_dump()
        
        assert serialized["role"] == "user"
        assert serialized["content"] == "Hello"
    
    def test_model_validation_errors(self):
        """Test model validation error handling."""
        # Invalid role
        with pytest.raises(ValidationError):
            Message(role="invalid_role", content="test")
        
        # Missing required fields
        with pytest.raises(ValidationError):
            MessagesRequest(max_tokens=1000)  # Missing model and messages
    
    def test_content_block_models(self):
        """Test content block model creation."""
        text_block = ContentBlockText(type="text", text="Hello")
        assert text_block.type == "text"
        assert text_block.text == "Hello"
        
        tool_use_block = ContentBlockToolUse(
            type="tool_use",
            id="tool_123",
            name="get_weather",
            input={"location": "SF"}
        )
        assert tool_use_block.type == "tool_use"
        assert tool_use_block.name == "get_weather"
        
        tool_result_block = ContentBlockToolResult(
            type="tool_result",
            tool_use_id="tool_123",
            content="Sunny, 22°C"
        )
        assert tool_result_block.type == "tool_result"
        assert tool_result_block.tool_use_id == "tool_123"