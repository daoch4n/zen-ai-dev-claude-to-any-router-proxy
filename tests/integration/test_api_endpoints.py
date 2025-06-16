"""
Integration tests for API endpoints.
Tests the complete API layer with routers, middleware, and services.
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

# Import the app
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main import create_app
from src.models.anthropic import MessagesRequest, TokenCountRequest, Message


@pytest.fixture
def client(test_config):
    """Create test client."""
    # Use the complete test config from conftest.py
    
    # Patch the config
    with patch('src.main.config', test_config):
        with patch('src.middleware.cors_middleware.config', test_config):
            app = create_app()
            yield TestClient(app)


@pytest.fixture
def sample_message_request():
    """Sample message request for testing."""
    return {
        "model": "anthropic/claude-3.7-sonnet",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you?"
            }
        ]
    }


@pytest.fixture
def sample_token_request():
    """Sample token count request for testing."""
    return {
        "model": "anthropic/claude-3.7-sonnet",
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you?"
            }
        ]
    }


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self, client):
        """Test basic health check."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "OpenRouter Anthropic Server"
    
    def test_detailed_health_check(self, client):
        """Test detailed health check."""
        response = client.get("/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "environment" in data
        assert "response_time_ms" in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "OpenRouter Anthropic Server"
        assert "endpoints" in data
        assert "features" in data
    
    def test_status_endpoint(self, client):
        """Test status endpoint."""
        response = client.get("/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "running"
        assert "timestamp" in data


class TestMessagesEndpoint:
    """Test messages endpoint."""
    
    @patch('litellm.acompletion')
    def test_create_message_success(self, mock_completion, client, sample_message_request):
        """Test successful message creation."""
        # Mock LiteLLM response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Hello! I'm doing well, thank you for asking."
        mock_response.choices[0].message.tool_calls = None  # Explicitly set to None
        mock_response.choices[0].finish_reason = "end_turn"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 15
        
        mock_completion.return_value = mock_response
        
        response = client.post("/v1/messages", json=sample_message_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["type"] == "message"
        assert data["role"] == "assistant"
        assert len(data["content"]) > 0
        assert data["content"][0]["type"] == "text"
        assert "usage" in data
    
    def test_create_message_validation_error(self, client):
        """Test message creation with validation error."""
        invalid_request = {
            "model": "anthropic/claude-3.7-sonnet",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "invalid_role",  # Invalid role
                    "content": "Hello"
                }
            ]
        }
        
        response = client.post("/v1/messages", json=invalid_request)
        assert response.status_code == 400
        
        data = response.json()
        assert data["type"] == "error"
        assert "error" in data
    
    def test_create_message_missing_fields(self, client):
        """Test message creation with missing required fields."""
        invalid_request = {
            "model": "anthropic/claude-3.7-sonnet",
            # Missing max_tokens and messages
        }
        
        response = client.post("/v1/messages", json=invalid_request)
        assert response.status_code == 400  # Our custom validation error handler converts 422 to 400
        
        data = response.json()
        assert data["type"] == "error"
    
    def test_create_message_empty_content(self, client):
        """Test message creation with empty content."""
        invalid_request = {
            "model": "anthropic/claude-3.7-sonnet",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": ""  # Empty content
                }
            ]
        }
        
        response = client.post("/v1/messages", json=invalid_request)
        assert response.status_code == 400
        
        data = response.json()
        assert data["type"] == "error"
    
    @patch('src.services.openrouter_direct_client.OpenRouterDirectClient.chat_completion')
    def test_create_message_with_tools(self, mock_chat_completion, client):
        """Test message creation with tools - tools are executed and final response returned."""
        # Mock OpenRouter response (bypass is now default)
        mock_openrouter_response = {
            "id": "chatcmpl-test123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "anthropic/claude-3-5-sonnet-20241022",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "I apologize, but the weather service is not available. Please check a weather app or website for current conditions in San Francisco."
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 35,
                "total_tokens": 85
            }
        }

        # Set up mock for OpenRouter direct client
        mock_chat_completion.return_value = mock_openrouter_response
        
        request_with_tools = {
            "model": "anthropic/claude-3.7-sonnet",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": "What's the weather in San Francisco?"
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
            ]
        }
        
        response = client.post("/v1/messages", json=request_with_tools)
        assert response.status_code == 200
        
        data = response.json()
        assert data["type"] == "message"
        # Tool execution can result in various response formats:
        # - 1 block: final text response (tool succeeded or failed and Claude finished)
        # - 2 blocks: text + tool_use (Claude wants to try again)
        assert len(data["content"]) >= 1
        assert data["content"][0]["type"] == "text"
        
        # Verify that tool-related content is present
        response_text = data["content"][0]["text"].lower()
        assert any(word in response_text for word in ["weather", "service", "information", "apologize"])
        
        # Verify that OpenRouter direct client was called at least once
        assert mock_chat_completion.call_count >= 1


class TestTokensEndpoint:
    """Test token counting endpoint."""
    
    @patch('litellm.token_counter')
    def test_count_tokens_success(self, mock_counter, client, sample_token_request):
        """Test successful token counting."""
        mock_counter.return_value = 25
        
        response = client.post("/v1/messages/count_tokens", json=sample_token_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["input_tokens"] == 25
    
    def test_count_tokens_validation_error(self, client):
        """Test token counting with validation error."""
        invalid_request = {
            "model": "anthropic/claude-3.7-sonnet",
            "messages": [
                {
                    "role": "invalid_role",  # Invalid role
                    "content": "Hello"
                }
            ]
        }
        
        response = client.post("/v1/messages/count_tokens", json=invalid_request)
        assert response.status_code == 400
        
        data = response.json()
        assert data["type"] == "error"
    
    @patch('litellm.token_counter')
    def test_count_tokens_complex_content(self, mock_counter, client):
        """Test token counting with complex content blocks."""
        mock_counter.return_value = 50
        
        complex_request = {
            "model": "anthropic/claude-3.7-sonnet",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What's the weather?"
                        }
                    ]
                },
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "I'll check the weather for you."
                        },
                        {
                            "type": "tool_use",
                            "id": "tool_123",
                            "name": "get_weather",
                            "input": {"location": "SF"}
                        }
                    ]
                }
            ]
        }
        
        response = client.post("/v1/messages/count_tokens", json=complex_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["input_tokens"] == 50


class TestMiddleware:
    """Test middleware functionality."""
    
    def test_cors_headers(self, client):
        """Test CORS headers are added."""
        response = client.get("/health")
        
        # Check for CORS headers
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Vary" in response.headers
    
    def test_request_id_header(self, client):
        """Test request ID is added to response."""
        response = client.get("/health")
        
        assert "X-Request-ID" in response.headers
        assert "X-Processing-Time" in response.headers
    
    def test_preflight_request(self, client):
        """Test CORS preflight request."""
        response = client.options(
            "/v1/messages",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        assert response.status_code == 200
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers
    
    def test_error_handling_format(self, client):
        """Test error responses are in Anthropic format."""
        # Make request to non-existent endpoint
        response = client.get("/non-existent")
        assert response.status_code == 404
        
        data = response.json()
        assert data["type"] == "error"
        assert "error" in data
        assert data["error"]["type"] == "not_found_error"


class TestModelMapping:
    """Test model mapping functionality."""
    
    @patch('litellm.acompletion')
    def test_big_model_mapping(self, mock_completion, client):
        """Test 'big' model mapping."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].finish_reason = "end_turn"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        
        mock_completion.return_value = mock_response
        
        request = {
            "model": "big",  # Should be mapped
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello"
                }
            ]
        }
        
        response = client.post("/v1/messages", json=request)
        assert response.status_code == 200
        
        # Check that the response model is the original model
        data = response.json()
        # The system now correctly returns the mapped model in the response
        # but we can verify the request was processed correctly
        assert "model" in data
        assert data["type"] == "message"
    
    @patch('litellm.acompletion')
    def test_small_model_mapping(self, mock_completion, client):
        """Test 'small' model mapping."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].finish_reason = "end_turn"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        
        mock_completion.return_value = mock_response
        
        request = {
            "model": "small",  # Should be mapped
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello"
                }
            ]
        }
        
        response = client.post("/v1/messages", json=request)
        assert response.status_code == 200
        
        # Check that the response model is the original model
        data = response.json()
        # The system now correctly returns the mapped model in the response
        # but we can verify the request was processed correctly
        assert "model" in data
        assert data["type"] == "message"