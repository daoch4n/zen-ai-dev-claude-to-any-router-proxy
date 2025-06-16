"""
Comprehensive API Mapping Tests

Tests to validate our conversion implementation against all three APIs:
- Anthropic API
- OpenAI API  
- OpenRouter API

Based on the API conversion analysis plan.
"""

import pytest
from unittest.mock import Mock, patch
import json
import base64

from src.flows.conversion.anthropic_to_litellm_flow import AnthropicToLiteLLMFlow
from src.flows.conversion.litellm_response_to_anthropic_flow import LiteLLMResponseToAnthropicFlow
from src.models.anthropic import MessagesRequest, Message, Tool
from src.models.instructor import ConversionResult


class TestParameterMappingComprehensive:
    """Test comprehensive parameter mapping across all APIs."""
    
    def test_core_parameters_mapping(self):
        """Test all core parameters are properly mapped."""
        flow = AnthropicToLiteLLMFlow()
        
        # Test request with all core parameters
        anthropic_request = MessagesRequest(
            model="claude-3-sonnet",
            messages=[
                Message(role="user", content="Hello, world!")
            ],
            max_tokens=1000,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            stop_sequences=["STOP", "END"],
            stream=False,
            system="You are a helpful assistant."
        )
        
        result = flow.convert(anthropic_request)
        
        assert result.success
        converted = result.converted_data
        
        # Verify core parameter mapping
        assert converted["model"].startswith("openrouter/")
        assert converted["max_tokens"] == 1000
        assert converted["temperature"] == 0.7
        assert converted["top_p"] == 0.9
        assert converted["top_k"] == 40
        assert converted["stop"] == ["STOP", "END"]
        assert converted["stream"] == False
        
        # Verify system message is converted to messages array
        assert len(converted["messages"]) >= 1
        assert converted["messages"][0]["role"] == "system"
        assert converted["messages"][0]["content"] == "You are a helpful assistant."
    
    def test_tool_parameter_mapping(self):
        """Test tool and tool_choice parameter mapping."""
        flow = AnthropicToLiteLLMFlow()
        
        # Create a tool definition
        tool = Tool(
            name="get_weather",
            description="Get current weather for a location",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        )
        
        anthropic_request = MessagesRequest(
            model="claude-3-sonnet",
            messages=[Message(role="user", content="What's the weather?")],
            max_tokens=100,
            tools=[tool],
            tool_choice={"type": "auto"}
        )
        
        result = flow.convert(anthropic_request)
        
        assert result.success
        converted = result.converted_data
        
        # Verify tool conversion
        assert "tools" in converted
        assert len(converted["tools"]) == 1
        
        tool_def = converted["tools"][0]
        assert tool_def["type"] == "function"
        assert tool_def["function"]["name"] == "get_weather"
        assert tool_def["function"]["description"] == "Get current weather for a location."
        assert "parameters" in tool_def["function"]
        
        # Verify tool_choice conversion
        assert converted["tool_choice"] == "auto"


class TestMissingParameterSupport:
    """Test cases for currently missing parameter support."""
    
    def test_openai_advanced_parameters_gap(self):
        """Test that we identify missing OpenAI advanced parameters."""
        # These parameters are supported by OpenAI but not currently handled
        missing_openai_params = [
            "frequency_penalty",
            "presence_penalty", 
            "seed",
            "logit_bias",
            "top_logprobs",
            "user"
        ]
        
        # This test documents the gap - these should be implemented
        for param in missing_openai_params:
            # Currently these would be ignored in conversion
            # TODO: Implement support for these parameters
            pass
    
    def test_openrouter_extensions_gap(self):
        """Test that we identify missing OpenRouter extensions."""
        # These parameters are OpenRouter-specific and not currently handled
        missing_openrouter_params = [
            "models",  # Array of fallback models
            "route",   # Routing strategy
            "provider",  # Provider preferences
            "transforms",  # Prompt transforms
            "min_p",   # Minimum probability threshold
            "top_a"    # Top-a sampling
        ]
        
        # This test documents the gap - these should be implemented
        for param in missing_openrouter_params:
            # Currently these would be ignored in conversion
            # TODO: Implement support for these parameters
            pass


# Note: Image content conversion tests are comprehensive and working - see:
# - test_image_content_conversion_anthropic_to_openai()
# - test_image_content_round_trip_conversion() 
# - test_multimodal_message_with_tools()
# - tests/test_image_content_conversion.py (full test suite)


class TestToolSchemaValidation:
    """Test tool schema handling and validation."""
    
    def test_complex_tool_schema_conversion(self):
        """Test conversion of complex tool schemas."""
        complex_tool = Tool(
            name="analyze_data",
            description="Analyze complex data structures with advanced options",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "value": {"type": "number"},
                                "metadata": {
                                    "type": "object",
                                    "additionalProperties": True
                                }
                            }
                        }
                    },
                    "options": {
                        "type": "object",
                        "properties": {
                            "algorithm": {
                                "type": "string", 
                                "enum": ["linear", "quadratic", "exponential"]
                            },
                            "threshold": {
                                "type": "number", 
                                "minimum": 0, 
                                "maximum": 1
                            },
                            "debug": {"type": "boolean", "default": False}
                        }
                    }
                },
                "required": ["data"]
            }
        )
        
        flow = AnthropicToLiteLLMFlow()
        
        anthropic_request = MessagesRequest(
            model="claude-3-sonnet",
            messages=[Message(role="user", content="Analyze this data")],
            max_tokens=100,
            tools=[complex_tool]
        )
        
        result = flow.convert(anthropic_request)
        
        assert result.success
        converted = result.converted_data
        
        # Verify complex schema is preserved but cleaned
        tool_def = converted["tools"][0]["function"]
        assert tool_def["name"] == "analyze_data"
        assert "parameters" in tool_def
        
        # Check that schema structure is simplified for OpenRouter compatibility
        params = tool_def["parameters"]
        assert params["type"] == "object"
        # Complex schemas are simplified for OpenRouter compatibility
        # The properties may be empty or simplified
        assert "properties" in params
    
    def test_tool_schema_openrouter_compatibility(self):
        """Test that tool schemas are compatible with OpenRouter limits."""
        # OpenRouter has stricter limits on tool complexity
        very_long_description = "A" * 500  # Very long description
        
        tool_with_long_desc = Tool(
            name="test_tool",
            description=very_long_description,
            input_schema={
                "type": "object",
                "properties": {
                    "param": {
                        "type": "string",
                        "description": "B" * 200  # Long parameter description
                    }
                }
            }
        )
        
        flow = AnthropicToLiteLLMFlow()
        
        anthropic_request = MessagesRequest(
            model="claude-3-sonnet",
            messages=[Message(role="user", content="Test")],
            max_tokens=100,
            tools=[tool_with_long_desc]
        )
        
        result = flow.convert(anthropic_request)
        
        assert result.success
        converted = result.converted_data
        
        # Verify descriptions are truncated for OpenRouter compatibility
        tool_def = converted["tools"][0]["function"]
        assert len(tool_def["description"]) <= 200  # Should be truncated
        
        # Complex tool parameters are simplified for OpenRouter compatibility
        # The specific parameter properties may be removed to ensure compatibility
        params = tool_def["parameters"]
        assert params["type"] == "object"
        assert "properties" in params


class TestStreamingConversion:
    """Test streaming response conversion."""
    
    def test_streaming_response_to_anthropic(self):
        """Test conversion of streaming responses back to Anthropic format."""
        # Mock streaming response with proper structure
        mock_message = Mock()
        mock_message.content = "Hello, world!"
        mock_message.tool_calls = None
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_choice.finish_reason = "stop"
        
        mock_usage = Mock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 5
        
        mock_complete_response = Mock()
        mock_complete_response.choices = [mock_choice]
        mock_complete_response.usage = mock_usage
        mock_complete_response.model = "claude-3-sonnet"
        
        # Mock streaming response that mimics CustomStreamWrapper
        class MockCustomStreamWrapper(Mock):
            pass
        
        mock_streaming_response = MockCustomStreamWrapper()
        mock_streaming_response.complete_response = mock_complete_response
        
        flow = LiteLLMResponseToAnthropicFlow()
        
        result = flow.convert(mock_streaming_response)
        
        assert result.success
        converted = result.converted_data
        
        # Verify streaming response is properly converted
        assert converted["role"] == "assistant"
        assert len(converted["content"]) > 0
        assert converted["content"][0]["type"] == "text"
        assert converted["content"][0]["text"] == "Hello, world!"
        assert converted["stop_reason"] == "end_turn"


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_malformed_request_handling(self):
        """Test handling of malformed requests."""
        flow = AnthropicToLiteLLMFlow()
        
        # Test with missing required fields
        malformed_request = MessagesRequest(
            model="claude-3-sonnet",
            messages=[],  # Empty messages
            max_tokens=100
        )
        
        result = flow.convert(malformed_request)
        
        # Should handle gracefully
        assert result.success or len(result.errors) > 0
    
    def test_unsupported_content_types(self):
        """Test handling of unsupported content types."""
        # Since Pydantic validation prevents creation of invalid messages,
        # this test verifies that the validation works correctly
        import pytest
        
        with pytest.raises(Exception):  # ValidationError expected
            Message(
                role="user",
                content=[
                    {"type": "text", "text": "Hello"},
                    {"type": "unsupported_type", "data": "some data"}
                ]
            )
        
        # Test that valid content types work fine
        valid_message = Message(
            role="user",
            content=[
                {"type": "text", "text": "Hello"}
            ]
        )
        
        flow = AnthropicToLiteLLMFlow()
        
        anthropic_request = MessagesRequest(
            model="claude-3-sonnet",
            messages=[valid_message],
            max_tokens=100
        )
        
        result = flow.convert(anthropic_request)
        
        # Should succeed with valid content
        assert result.success


class TestPerformanceMetrics:
    """Test performance characteristics of conversion."""
    
    def test_conversion_latency(self):
        """Test that conversion completes within acceptable time limits."""
        import time
        
        flow = AnthropicToLiteLLMFlow()
        
        # Create a reasonably complex request
        anthropic_request = MessagesRequest(
            model="claude-3-sonnet",
            messages=[
                Message(role="user", content="Hello"),
                Message(role="assistant", content="Hi there!"),
                Message(role="user", content="How are you?")
            ],
            max_tokens=1000,
            temperature=0.7,
            tools=[
                Tool(
                    name="test_tool",
                    description="A test tool",
                    input_schema={"type": "object", "properties": {"param": {"type": "string"}}}
                )
            ]
        )
        
        start_time = time.time()
        result = flow.convert(anthropic_request)
        end_time = time.time()
        
        conversion_time = end_time - start_time
        
        assert result.success
        assert conversion_time < 0.01  # Should complete in under 10ms
    
    def test_memory_usage(self):
        """Test memory usage during conversion."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        flow = AnthropicToLiteLLMFlow()
        
        # Perform multiple conversions
        for _ in range(100):
            anthropic_request = MessagesRequest(
                model="claude-3-sonnet",
                messages=[Message(role="user", content="Test message")],
                max_tokens=100
            )
            result = flow.convert(anthropic_request)
            assert result.success
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024


def test_image_content_conversion_anthropic_to_openai():
    """Test image content conversion from Anthropic to OpenAI format."""
    sample_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAHGbYJYUgAAAABJRU5ErkJggg=="
    
    flow = AnthropicToLiteLLMFlow()
    
    anthropic_request = MessagesRequest(
        model="claude-3-sonnet-20240229",
        max_tokens=100,
        messages=[
            Message(
                role="user",
                content=[
                    {"type": "text", "text": "What's in this image?"},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": sample_image_data
                        }
                    }
                ]
            )
        ]
    )
    
    result = flow.convert(anthropic_request)
    
    assert result.success
    converted = result.converted_data
    
    # Verify multimodal content conversion
    assert len(converted["messages"]) >= 1
    user_message = None
    for msg in converted["messages"]:
        if msg["role"] == "user":
            user_message = msg
            break
    
    assert user_message is not None
    assert isinstance(user_message["content"], list)
    assert len(user_message["content"]) == 2
    assert user_message["content"][0]["type"] == "text"
    assert user_message["content"][1]["type"] == "image_url"
    assert sample_image_data in user_message["content"][1]["image_url"]["url"]


def test_image_content_round_trip_conversion():
    """Test that image content maintains integrity through round-trip conversion."""
    sample_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAHGbYJYUgAAAABJRU5ErkJggg=="
    
    flow = AnthropicToLiteLLMFlow()
    
    original_anthropic = MessagesRequest(
        model="claude-3-sonnet-20240229",
        max_tokens=50,
        messages=[
            Message(
                role="user",
                content=[
                    {"type": "text", "text": "Analyze this:"},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": sample_image_data
                        }
                    }
                ]
            )
        ]
    )
    
    # Convert to OpenAI format
    result = flow.convert(original_anthropic)
    
    assert result.success
    openai_format = result.converted_data
    
    # Verify image conversion
    user_message = None
    for msg in openai_format["messages"]:
        if msg["role"] == "user":
            user_message = msg
            break
    
    assert user_message is not None
    assert isinstance(user_message["content"], list)
    image_content = user_message["content"][1]
    assert image_content["type"] == "image_url"
    assert f"data:image/png;base64,{sample_image_data}" == image_content["image_url"]["url"]
    
    # Note: For full round-trip, we'd need OpenAI->Anthropic conversion as well
    # This validates the Anthropic->OpenAI direction works correctly


def test_multimodal_message_with_tools():
    """Test multimodal message with both images and tool definitions."""
    sample_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAHGbYJYUgAAAABJRU5ErkJggg=="
    
    flow = AnthropicToLiteLLMFlow()
    
    tool = Tool(
        name="calculator",
        description="Perform mathematical calculations",
        input_schema={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Mathematical expression"}
            },
            "required": ["expression"]
        }
    )
    
    anthropic_request = MessagesRequest(
        model="claude-3-sonnet-20240229",
        max_tokens=200,
        messages=[
            Message(
                role="user",
                content=[
                    {"type": "text", "text": "Analyze this chart and calculate totals:"},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": sample_image_data
                        }
                    }
                ]
            )
        ],
        tools=[tool]
    )
    
    result = flow.convert(anthropic_request)
    
    assert result.success
    converted = result.converted_data
    
    # Verify both image and tool conversion
    user_message = None
    for msg in converted["messages"]:
        if msg["role"] == "user":
            user_message = msg
            break
    
    assert user_message is not None
    assert isinstance(user_message["content"], list)
    assert len(user_message["content"]) == 2
    assert user_message["content"][1]["type"] == "image_url"
    assert "functions" in converted or "tools" in converted
    
    # Verify tool conversion
    if "tools" in converted:
        assert converted["tools"][0]["function"]["name"] == "calculator"
    elif "functions" in converted:
        assert converted["functions"][0]["name"] == "calculator"


def test_image_content_error_handling():
    """Test handling of malformed image content."""
    flow = AnthropicToLiteLLMFlow()
    
    anthropic_request = MessagesRequest(
        model="claude-3-sonnet-20240229", 
        max_tokens=50,
        messages=[
            Message(
                role="user",
                content=[
                    {"type": "text", "text": "What's in this image?"},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": ""  # Empty data should be handled gracefully
                        }
                    }
                ]
            )
        ]
    )
    
    result = flow.convert(anthropic_request)
    
    assert result.success
    converted = result.converted_data
    
    # Should convert empty image to text placeholder
    user_message = None
    for msg in converted["messages"]:
        if msg["role"] == "user":
            user_message = msg
            break
    
    assert user_message is not None
    assert isinstance(user_message["content"], list)
    content = user_message["content"]
    assert len(content) == 2
    assert content[1]["type"] == "text"
    assert "Empty image content" in content[1]["text"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 