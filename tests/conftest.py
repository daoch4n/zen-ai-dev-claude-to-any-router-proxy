"""Pytest configuration and shared fixtures for the OpenRouter Anthropic Server tests."""

import pytest
import os
import tempfile
import json
from typing import Dict, Any, List
from unittest.mock import Mock, patch
from pathlib import Path

# Add src to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.config import ServerConfig
from src.core.logging_config import setup_logging
from src.models.anthropic import Message, MessagesRequest, Tool


@pytest.fixture(scope="session")
def test_config(tmp_path_factory):
    """Create a test configuration."""
    # Create a session-scoped temporary directory for debug logs
    temp_debug_dir = tmp_path_factory.mktemp("test_debug_logs")
    
    return ServerConfig(
        openrouter_api_key="test-key-123",
        host="127.0.0.1",
        port=4000,
        big_model="anthropic/claude-sonnet-4",
        small_model="anthropic/claude-3.7-sonnet",
        log_level="DEBUG",
        debug_enabled=True,
        debug_logs_dir=str(temp_debug_dir),
        environment="testing",
        max_tokens_limit=8192,
        request_timeout=300,
        instructor_enabled=True,
        instructor_temperature=0.1,
        instructor_max_retries=3,
        enable_caching=True,
        cache_ttl=3600,
        max_concurrent_requests=10
    )


@pytest.fixture
def temp_debug_dir():
    """Create a temporary directory for debug logs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_message():
    """Create a sample message for testing."""
    return Message(
        role="user",
        content="Hello, how are you?"
    )


@pytest.fixture
def sample_assistant_message():
    """Create a sample assistant message for testing."""
    return Message(
        role="assistant",
        content="I'm doing well, thank you for asking!"
    )


@pytest.fixture
def sample_tool():
    """Create a sample tool for testing."""
    return Tool(
        name="get_weather",
        description="Get weather information for a location",
        input_schema={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location to get weather for"
                },
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "default": "celsius"
                }
            },
            "required": ["location"]
        }
    )


@pytest.fixture
def sample_messages_request(sample_message, sample_tool):
    """Create a sample messages request for testing."""
    return MessagesRequest(
        model="anthropic/claude-3.7-sonnet",
        max_tokens=4096,
        messages=[sample_message],
        tools=[sample_tool],
        stream=False,
        temperature=0.7
    )


@pytest.fixture
def sample_tool_use_message():
    """Create a sample message with tool use."""
    return Message(
        role="assistant",
        content=[
            {
                "type": "text",
                "text": "I'll get the weather for you."
            },
            {
                "type": "tool_use",
                "id": "tool_123",
                "name": "get_weather",
                "input": {"location": "San Francisco", "units": "celsius"}
            }
        ]
    )


@pytest.fixture
def sample_tool_result_message():
    """Create a sample message with tool result."""
    return Message(
        role="user",
        content=[
            {
                "type": "tool_result",
                "tool_use_id": "tool_123",
                "content": "The weather in San Francisco is 22°C and sunny."
            }
        ]
    )


@pytest.fixture
def sample_conversation(sample_message, sample_tool_use_message, sample_tool_result_message):
    """Create a sample multi-turn conversation."""
    return [
        sample_message,
        sample_tool_use_message,
        sample_tool_result_message
    ]


@pytest.fixture
def mock_openrouter_response():
    """Mock OpenRouter API response."""
    return {
        "id": "msg_123456",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "Hello! I'm doing well, thank you for asking."
            }
        ],
        "model": "anthropic/claude-3.7-sonnet",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": 10,
            "output_tokens": 15,
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0
        }
    }


@pytest.fixture
def mock_streaming_response():
    """Mock streaming response chunks."""
    return [
        {
            "type": "message_start",
            "message": {
                "id": "msg_123",
                "type": "message",
                "role": "assistant",
                "content": [],
                "model": "anthropic/claude-3.7-sonnet",
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 10, "output_tokens": 0}
            }
        },
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {"type": "text", "text": ""}
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "Hello"}
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "!"}
        },
        {
            "type": "content_block_stop",
            "index": 0
        },
        {
            "type": "message_delta",
            "delta": {"stop_reason": "end_turn", "stop_sequence": None},
            "usage": {"output_tokens": 15}
        },
        {
            "type": "message_stop"
        }
    ]


@pytest.fixture
def mock_litellm_client():
    """Mock LiteLLM client."""
    with patch('litellm.completion') as mock_completion:
        mock_completion.return_value = Mock()
        yield mock_completion


@pytest.fixture
def mock_instructor_client():
    """Mock Instructor client."""
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = Mock()
    return mock_client


@pytest.fixture(autouse=True)
def setup_test_environment(test_config, temp_debug_dir):
    """Set up test environment for each test."""
    # Set test environment variables
    os.environ["OPENROUTER_API_KEY"] = test_config.openrouter_api_key
    os.environ["DEBUG"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    # Setup logging for tests
    setup_logging("DEBUG")
    
    yield
    
    # Cleanup
    for key in ["OPENROUTER_API_KEY", "DEBUG", "LOG_LEVEL"]:
        os.environ.pop(key, None)


@pytest.fixture
def sample_request_data():
    """Sample request data for testing."""
    return {
        "model": "anthropic/claude-3.7-sonnet",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you?"
            }
        ],
        "tools": [
            {
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
        ],
        "stream": False,
        "temperature": 0.7
    }


@pytest.fixture
def sample_litellm_request():
    """Sample LiteLLM request for testing."""
    return {
        "model": "anthropic/claude-3.7-sonnet",
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you?"
            }
        ],
        "max_tokens": 4096,
        "temperature": 0.7,
        "stream": False,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"}
                        },
                        "required": ["location"]
                    }
                }
            }
        ],
        "api_key": "test-key-123",
        "extra_headers": {
            "HTTP-Referer": "https://github.com/your-repo",
            "X-Title": "OpenRouter Anthropic Server"
        }
    }


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
pytest.mark.slow = pytest.mark.slow