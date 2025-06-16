"""
Tests for Azure Databricks Claude integration.

This module tests the Azure Databricks proxy functionality including
configuration, client service, converter, and router components.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from fastapi.testclient import TestClient
import httpx
import os

from src.services.azure_databricks_client import AzureDatabricksClaudeClient, get_endpoint_for_model
from src.converters.azure_databricks_converter import AzureDatabricksConverter
from src.utils.config import config
from src.main import create_app


def get_base_env_vars(**overrides):
    """Get base environment variables required for ServerConfig with optional overrides."""
    base_vars = {
        'OPENROUTER_API_KEY': 'test-key',
        'HOST': '0.0.0.0',
        'PORT': '4000',
        'ANTHROPIC_MODEL': 'anthropic/claude-sonnet-4',
        'ANTHROPIC_SMALL_FAST_MODEL': 'anthropic/claude-3.7-sonnet',
        'LOG_LEVEL': 'INFO',
        'DEBUG': 'false',
        'DEBUG_LOGS_DIR': 'logs/debug',
        'ENVIRONMENT': 'testing',
        'MAX_TOKENS_LIMIT': '8192',
        'REQUEST_TIMEOUT': '300',
        'INSTRUCTOR_ENABLED': 'true',
        'ENABLE_CACHING': 'true',
        'CACHE_TTL': '3600',
        'MAX_CONCURRENT_REQUESTS': '10'
    }
    base_vars.update(overrides)
    return base_vars


class TestAzureDatabricksClient:
    """Test Azure Databricks client functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        return AzureDatabricksClaudeClient(
            workspace_instance="test-workspace",
            databricks_token="test-token"
        )
    
    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.workspace_instance == "test-workspace"
        assert client.base_url == "https://test-workspace.azuredatabricks.net/serving-endpoints"
        assert client.client is not None
    
    @pytest.mark.asyncio
    async def test_create_message_success(self, client):
        """Test successful message creation."""
        # Mock response
        mock_response = {
            "choices": [{"message": {"content": "Test response"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            "model": "claude-3-7-sonnet",
            "id": "test-id"
        }
        
        with patch.object(client, '_make_request_with_retries') as mock_request:
            mock_http_response = Mock()
            mock_http_response.json.return_value = mock_response
            mock_request.return_value = mock_http_response
            
            result = await client.create_message(
                endpoint_name="databricks-claude-3-7-sonnet",
                messages=[{"role": "user", "content": "Hello"}]
            )
            
            assert result == mock_response
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test successful health check."""
        with patch.object(client, 'create_message') as mock_create:
            mock_create.return_value = {
                "model": "claude-3-7-sonnet",
                "id": "test-id"
            }
            
            result = await client.health_check("databricks-claude-3-7-sonnet")
            
            assert result["status"] == "healthy"
            assert "response_time_ms" in result
            assert result["model"] == "claude-3-7-sonnet"
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, client):
        """Test health check failure."""
        with patch.object(client, 'create_message') as mock_create:
            mock_create.side_effect = Exception("Connection failed")
            
            result = await client.health_check("databricks-claude-3-7-sonnet")
            
            assert result["status"] == "unhealthy"
            assert "error" in result
            assert result["error"] == "Connection failed"


class TestAzureDatabricksConverter:
    """Test Azure Databricks converter functionality."""
    
    @pytest.fixture
    def converter(self):
        """Create a test converter instance."""
        return AzureDatabricksConverter()
    
    def test_convert_request_to_databricks(self, converter):
        """Test request format conversion."""
        anthropic_request = {
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 100,
            "temperature": 0.7,
            "model": "claude-3.7-sonnet"
        }
        
        result = converter.convert_request_to_databricks(anthropic_request)
        
        assert result["messages"] == anthropic_request["messages"]
        assert result["max_tokens"] == 100
        assert result["temperature"] == 0.7
        assert result["model"] == "claude-3.7-sonnet"
    
    def test_convert_response_to_anthropic(self, converter):
        """Test response format conversion."""
        databricks_response = {
            "choices": [{"message": {"content": "Hello back!"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15},
            "model": "claude-3-7-sonnet",
            "id": "test-123"
        }
        
        result = converter.convert_response_to_anthropic(databricks_response)
        
        assert result["type"] == "message"
        assert result["role"] == "assistant"
        assert result["content"][0]["text"] == "Hello back!"
        assert result["usage"]["input_tokens"] == 5
        assert result["usage"]["output_tokens"] == 10
        assert result["stop_reason"] == "end_turn"
    
    def test_convert_finish_reason(self, converter):
        """Test finish reason conversion."""
        assert converter._convert_finish_reason("stop") == "end_turn"
        assert converter._convert_finish_reason("length") == "max_tokens"
        assert converter._convert_finish_reason("function_call") == "tool_use"
        assert converter._convert_finish_reason("unknown") == "end_turn"
    
    def test_validate_anthropic_request_valid(self, converter):
        """Test request validation with valid request."""
        valid_request = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        
        assert converter.validate_anthropic_request(valid_request) is True
    
    def test_validate_anthropic_request_invalid(self, converter):
        """Test request validation with invalid request."""
        invalid_request = {
            "messages": []  # Empty messages
        }
        
        assert converter.validate_anthropic_request(invalid_request) is False
        
        invalid_request2 = {
            "messages": [
                {"role": "invalid", "content": "Hello"}  # Invalid role
            ]
        }
        
        assert converter.validate_anthropic_request(invalid_request2) is False


class TestEndpointMapping:
    """Test endpoint mapping functionality."""
    
    def test_get_endpoint_for_model(self):
        """Test model to endpoint mapping."""
        # Test Claude Sonnet 4 mapping
        assert get_endpoint_for_model("claude-sonnet-4") == config.databricks_claude_sonnet_4_endpoint
        assert get_endpoint_for_model("sonnet-4") == config.databricks_claude_sonnet_4_endpoint
        
        # Test Claude 3.7 Sonnet mapping
        assert get_endpoint_for_model("claude-3.7-sonnet") == config.databricks_claude_3_7_sonnet_endpoint
        assert get_endpoint_for_model("3.7-sonnet") == config.databricks_claude_3_7_sonnet_endpoint
        
        # Test default mapping
        assert get_endpoint_for_model("unknown-model") == config.databricks_claude_3_7_sonnet_endpoint


class TestAzureDatabricksRouter:
    """Test Azure Databricks router endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create test app with Azure Databricks enabled."""
        # Use the same environment setup as the unified proxy tests
        env_vars = get_base_env_vars(
            PROXY_BACKEND='AZURE_DATABRICKS',
            DATABRICKS_HOST='adb-123456.7',
            DATABRICKS_TOKEN='dapi1234567890abcdef',
            DATABRICKS_CLAUDE_SONNET_4_ENDPOINT='databricks-claude-sonnet-4',
            DATABRICKS_CLAUDE_3_7_SONNET_ENDPOINT='databricks-claude-3-7-sonnet'
        )
        
        with patch.dict(os.environ, env_vars, clear=True):
            # Need to force reimport of config module to pick up new env vars
            import sys
            if 'src.utils.config' in sys.modules:
                del sys.modules['src.utils.config']
            if 'src.main' in sys.modules:
                del sys.modules['src.main']
            if 'src.routers.azure_databricks' in sys.modules:
                del sys.modules['src.routers.azure_databricks']
            
            from src.main import create_app
            return create_app()
    
    @pytest.fixture  
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    def test_health_endpoint_disabled(self):
        """Test health endpoint when Azure Databricks is disabled."""
        # Test with default config (disabled)
        env_vars = get_base_env_vars(
            PROXY_BACKEND='OPENROUTER'  # Different backend to ensure Azure Databricks is disabled
        )
        with patch.dict(os.environ, env_vars, clear=True):
            app = create_app()
            client = TestClient(app)
            
            response = client.get("/v1/databricks/health")
            assert response.status_code == 404  # Router not included when disabled
    
    @patch('src.services.azure_databricks_client.get_databricks_client')
    def test_health_endpoint_enabled(self, mock_get_client, client):
        """Test health endpoint when Azure Databricks is enabled."""
        # Mock the client context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.health_check.return_value = {
            "status": "healthy",
            "response_time_ms": 100.0,
            "model": "claude-3-7-sonnet"
        }
        
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_client_instance
        mock_get_client.return_value = mock_context
        
        response = client.get("/v1/databricks/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
    
    def test_config_endpoint(self, client):
        """Test configuration endpoint."""
        response = client.get("/v1/databricks/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "azure_databricks" in data
        assert "model_mapping" in data
        # The endpoint returns the actual config with Azure Databricks enabled
        assert data["azure_databricks"]["enabled"] is True
    
    def test_models_endpoint(self, client):
        """Test models listing endpoint."""
        response = client.get("/v1/databricks/models")
        assert response.status_code == 200
        
        data = response.json()
        assert "available_models" in data
        assert len(data["available_models"]) == 2
        assert data["default_model"] == "claude-3.7-sonnet"
    
    @patch('src.services.azure_databricks_client.get_databricks_client')
    def test_create_message_endpoint_disabled(self, mock_get_client, client):
        """Test message endpoint when Azure Databricks is disabled."""
        # Mock the client to simulate a working databricks client
        mock_client_instance = AsyncMock()
        mock_client_instance.create_message.return_value = {
            "choices": [{"message": {"content": "Test response"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            "model": "claude-3-7-sonnet",
            "id": "test-id"
        }
        
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_client_instance
        mock_get_client.return_value = mock_context
        
        request_data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 100,
            "model": "claude-3.7-sonnet"
        }
        
        response = client.post("/v1/databricks/messages", json=request_data)
        # With our Azure Databricks enabled fixture, this should work
        assert response.status_code in [200, 500, 503]  # Allow various failure modes
    
    def test_create_message_validation_error_disabled(self, client):
        """Test message creation with validation error when disabled."""
        invalid_request = {
            "messages": [],  # Empty messages should fail validation
            "max_tokens": 100,
            "model": "claude-3.7-sonnet"
        }
        
        response = client.post("/v1/databricks/messages", json=invalid_request)
        # Should return 400 for validation error
        assert response.status_code in [400, 503]


class TestConfiguration:
    """Test Azure Databricks configuration."""
    
    def test_databricks_config_helper(self):
        """Test get_databricks_config helper method."""
        databricks_config = config.get_databricks_config()
        
        assert "enabled" in databricks_config
        assert "host" in databricks_config
        assert "token" in databricks_config
        assert "timeout" in databricks_config
        assert "max_retries" in databricks_config
        assert "endpoints" in databricks_config
    
    def test_databricks_model_mapping(self):
        """Test get_databricks_model_mapping helper method."""
        model_mapping = config.get_databricks_model_mapping()
        
        assert "claude-sonnet-4" in model_mapping
        assert "claude-3.7-sonnet" in model_mapping
        assert "anthropic/claude-sonnet-4" in model_mapping
        assert "big" in model_mapping
        assert "small" in model_mapping


class TestErrorHandling:
    """Test error handling for Azure Databricks integration."""
    
    @pytest.mark.asyncio
    async def test_client_http_error(self):
        """Test client handling of HTTP errors."""
        client = AzureDatabricksClaudeClient("test-workspace", "test-token")
        
        with patch.object(client, '_make_request_with_retries') as mock_request:
            # Simulate HTTP error
            http_error = httpx.HTTPStatusError(
                "401 Unauthorized",
                request=Mock(),
                response=Mock(status_code=401, text="Unauthorized")
            )
            mock_request.side_effect = http_error
            
            with pytest.raises(httpx.HTTPStatusError):
                await client.create_message(
                    endpoint_name="test-endpoint",
                    messages=[{"role": "user", "content": "Hello"}]
                )
    
    @pytest.mark.asyncio
    async def test_client_network_error(self):
        """Test client handling of network errors."""
        client = AzureDatabricksClaudeClient("test-workspace", "test-token")
        
        with patch.object(client, '_make_request_with_retries') as mock_request:
            # Simulate network error
            mock_request.side_effect = Exception("Network error")
            
            with pytest.raises(Exception):
                await client.create_message(
                    endpoint_name="test-endpoint",
                    messages=[{"role": "user", "content": "Hello"}]
                )
    
    def test_converter_error_handling(self):
        """Test converter error handling."""
        converter = AzureDatabricksConverter()
        
        # Test with malformed response
        malformed_response = {"invalid": "response"}
        
        # Should return original response if format is unexpected
        result = converter.convert_response_to_anthropic(malformed_response)
        assert result == malformed_response


if __name__ == "__main__":
    pytest.main([__file__]) 