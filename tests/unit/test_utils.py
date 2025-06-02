"""Unit tests for enhanced utility modules."""

import pytest
import os
import tempfile
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
from pydantic import ValidationError

from src.utils.config import ServerConfig
from src.core.logging_config import get_logger, setup_logging
from src.utils.debug import EnhancedDebugLogger
from src.utils.errors import (
    OpenRouterProxyError, ToolValidationError, InstructorError,
    StructuredOutputError, ValidationExtractionError
)


class TestServerConfig:
    """Test ServerConfig class."""
    
    def test_default_config(self, test_config):
        """Test default configuration values using test fixture."""
        # Use the complete test config from conftest.py
        config = test_config
        
        assert config.openrouter_api_key == "test-key-123"
        assert config.host == "127.0.0.1"
        assert config.port == 4000
        assert config.log_level == "DEBUG"
        assert config.debug_enabled is True
        assert config.instructor_enabled is True
        assert config.max_tokens_limit == 8192
    
    def test_config_validation(self, test_config):
        """Test configuration validation using test fixture."""
        # Use the complete test config and verify specific values
        config = test_config
        assert config.port == 4000
        assert config.log_level == "DEBUG"
        
        # Test that we can create a modified config with all required fields
        modified_config = ServerConfig(
            openrouter_api_key="valid-key",
            host="localhost",
            port=8080,
            big_model="anthropic/claude-sonnet-4",
            small_model="anthropic/claude-3.7-sonnet",
            log_level="DEBUG",
            debug_enabled=False,
            debug_logs_dir="logs/debug",
            environment="testing",
            max_tokens_limit=8192,
            request_timeout=300,
            instructor_enabled=True,
            enable_caching=True,
            cache_ttl=3600,
            max_concurrent_requests=10
        )
        assert modified_config.port == 8080
        assert modified_config.log_level == "DEBUG"
    
    def test_invalid_api_key(self):
        """Test invalid API key validation."""
        with pytest.raises(ValidationError) as exc_info:
            ServerConfig(openrouter_api_key="")
        assert "OpenRouter API key cannot be empty" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            ServerConfig(openrouter_api_key="   ")
        assert "OpenRouter API key cannot be empty" in str(exc_info.value)
    
    def test_invalid_port(self):
        """Test invalid port validation."""
        with pytest.raises(ValidationError) as exc_info:
            ServerConfig(openrouter_api_key="test", port=0)
        assert "Port must be between 1 and 65535" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            ServerConfig(openrouter_api_key="test", port=70000)
        assert "Port must be between 1 and 65535" in str(exc_info.value)
    
    def test_invalid_log_level(self):
        """Test invalid log level validation."""
        with pytest.raises(ValidationError) as exc_info:
            ServerConfig(openrouter_api_key="test", log_level="INVALID")
        assert "Log level must be one of" in str(exc_info.value)
    
    def test_invalid_environment(self):
        """Test invalid environment validation."""
        with pytest.raises(ValidationError) as exc_info:
            ServerConfig(
                openrouter_api_key="test-key",
                host="localhost", 
                port=8080,
                big_model="anthropic/claude-sonnet-4",
                small_model="anthropic/claude-3.7-sonnet",
                log_level="INFO",
                debug_enabled=False,
                debug_logs_dir="logs/debug",
                environment="invalid_env",  # Invalid environment
                max_tokens_limit=8192,
                request_timeout=300,
                instructor_enabled=True,
                enable_caching=True,
                cache_ttl=3600,
                max_concurrent_requests=10
            )
        assert "Environment must be one of" in str(exc_info.value)
    
    def test_invalid_max_tokens(self):
        """Test invalid max tokens validation."""
        with pytest.raises(ValidationError) as exc_info:
            ServerConfig(openrouter_api_key="test", max_tokens_limit=0)
        assert "Max tokens limit must be positive" in str(exc_info.value)
    
    def test_invalid_cache_ttl(self):
        """Test invalid cache TTL validation."""
        with pytest.raises(ValidationError) as exc_info:
            ServerConfig(openrouter_api_key="test", cache_ttl=0)
        assert "Cache TTL must be positive" in str(exc_info.value)
    
    @patch.dict(os.environ, {
        "OPENROUTER_API_KEY": "env-key",
        "HOST": "127.0.0.1",
        "PORT": "3000",
        "ANTHROPIC_MODEL": "anthropic/claude-sonnet-4",
        "ANTHROPIC_SMALL_FAST_MODEL": "anthropic/claude-3.7-sonnet",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "DEBUG_LOGS_DIR": "logs/debug",
        "ENVIRONMENT": "testing",
        "MAX_TOKENS_LIMIT": "8192",
        "REQUEST_TIMEOUT": "300",
        "INSTRUCTOR_ENABLED": "false",
        "ENABLE_CACHING": "true",
        "CACHE_TTL": "3600",
        "MAX_CONCURRENT_REQUESTS": "10"
    })
    def test_from_env(self):
        """Test configuration from environment variables."""
        config = ServerConfig.from_env()
        
        assert config.openrouter_api_key == "env-key"
        assert config.host == "127.0.0.1"
        assert config.port == 3000
        assert config.debug_enabled is True
        assert config.log_level == "DEBUG"
        assert config.instructor_enabled is False
    
    def test_model_mapping(self):
        """Test model mapping functionality."""
        config = ServerConfig(
            openrouter_api_key="test",
            host="localhost",
            port=4000,
            big_model="anthropic/claude-sonnet-4",
            small_model="anthropic/claude-3.7-sonnet",
            log_level="INFO",
            debug_enabled=False,
            debug_logs_dir="logs/debug",
            environment="testing",
            max_tokens_limit=8192,
            request_timeout=300,
            instructor_enabled=True,
            enable_caching=True,
            cache_ttl=3600,
            max_concurrent_requests=10
        )
        
        mapping = config.get_model_mapping()
        assert mapping["big"] == "anthropic/claude-sonnet-4"
        assert mapping["small"] == "anthropic/claude-3.7-sonnet"
        
        # Test that legacy mappings are included
        assert mapping["claude-sonnet-4-20250514"] == "anthropic/claude-sonnet-4"
        assert mapping["claude-3-7-sonnet-20250219"] == "anthropic/claude-3.7-sonnet"
        assert mapping["claude-3-5-sonnet-20241022"] == "anthropic/claude-3.7-sonnet"
        assert mapping["sonnet"] == "anthropic/claude-sonnet-4"
        assert mapping["haiku"] == "anthropic/claude-3.7-sonnet"
    
    def test_instructor_config(self, test_config):
        """Test instructor configuration."""
        # Create a complete config with instructor settings
        config = ServerConfig(
            openrouter_api_key="test",
            host="localhost",
            port=4000,
            big_model="anthropic/claude-sonnet-4",
            small_model="anthropic/claude-3.7-sonnet",
            log_level="INFO",
            debug_enabled=False,
            debug_logs_dir="logs/debug",
            environment="testing",
            max_tokens_limit=8192,
            request_timeout=300,
            instructor_enabled=True,
            enable_caching=True,
            cache_ttl=3600,
            max_concurrent_requests=10
        )
        
        instructor_config = config.get_instructor_config()
        assert instructor_config["enabled"] is True
        assert instructor_config["model"] == "anthropic/claude-3-5-sonnet-20241022"
    
    def test_performance_config(self, test_config):
        """Test performance configuration."""
        # Create a complete config with performance settings
        config = ServerConfig(
            openrouter_api_key="test",
            host="localhost",
            port=4000,
            big_model="anthropic/claude-sonnet-4",
            small_model="anthropic/claude-3.7-sonnet",
            log_level="INFO",
            debug_enabled=False,
            debug_logs_dir="logs/debug",
            environment="testing",
            max_tokens_limit=8192,
            request_timeout=600,
            instructor_enabled=True,
            enable_caching=True,
            cache_ttl=7200,
            max_concurrent_requests=20
        )
        
        perf_config = config.get_performance_config()
        assert perf_config["enable_caching"] is True
        assert perf_config["cache_ttl"] == 7200
        assert perf_config["max_concurrent_requests"] == 20
        assert perf_config["request_timeout"] == 600
    
    def test_environment_detection(self, test_config):
        """Test development/production environment detection."""
        # Development mode - create complete config
        dev_config = ServerConfig(
            openrouter_api_key="test",
            host="localhost",
            port=4000,
            big_model="anthropic/claude-sonnet-4",
            small_model="anthropic/claude-3.7-sonnet",
            log_level="DEBUG",
            debug_enabled=True,
            debug_logs_dir="logs/debug",
            environment="development",
            max_tokens_limit=8192,
            request_timeout=300,
            instructor_enabled=True,
            enable_caching=True,
            cache_ttl=3600,
            max_concurrent_requests=10
        )
        assert dev_config.is_development() is True
        assert dev_config.is_production() is False
        
        # Production mode - create complete config
        prod_config = ServerConfig(
            openrouter_api_key="test",
            host="localhost",
            port=4000,
            big_model="anthropic/claude-sonnet-4",
            small_model="anthropic/claude-3.7-sonnet",
            log_level="INFO",
            debug_enabled=False,
            debug_logs_dir="logs/debug",
            environment="production",
            max_tokens_limit=8192,
            request_timeout=300,
            instructor_enabled=True,
            enable_caching=True,
            cache_ttl=3600,
            max_concurrent_requests=10
        )
        assert prod_config.is_development() is False
        assert prod_config.is_production() is True


class TestUnifiedLogging:
    """Test unified structlog logging system."""
    
    def test_get_logger(self):
        """Test logger retrieval."""
        logger = get_logger("test_logger")
        assert logger is not None
        # structlog loggers don't have a .name attribute in the same way
        # but we can verify it's a structlog BoundLogger
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'debug')
    
    def test_structured_logging(self):
        """Test structured logging functionality."""
        logger = get_logger("test_logger")
        
        # This should not raise an exception
        logger.info("Test message", key1="value1", key2="value2")
        logger.error("Error message", error_code=500)
    
    def test_context_logging(self):
        """Test logging with context."""
        logger = get_logger("test_logger")
        
        # Test various structured log calls
        logger.info(
            "Instructor operation",
            operation="structured_completion",
            model="anthropic/claude-3-5-sonnet",
            success=True,
            response_model="TestModel",
            processing_time=1.5
        )
        
        logger.error(
            "Validation failed",
            validation_type="tool_validation",
            success=False,
            errors=["Missing required field", "Invalid format"],
            context={"message_id": "msg_123"}
        )
    
    def test_performance_logging(self):
        """Test performance metric logging."""
        logger = get_logger("test_logger")
        
        logger.info(
            "Performance metric",
            metric_name="response_time",
            value=1.234,
            unit="seconds",
            endpoint="/v1/messages"
        )
        logger.info(
            "Performance metric",
            metric_name="token_count",
            value=150,
            unit="tokens",
            model="claude-3-5-sonnet"
        )
    
    def test_error_logging_with_context(self):
        """Test error logging with context."""
        logger = get_logger("test_logger")
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.error(
                "Error occurred",
                error=str(e),
                error_type=type(e).__name__,
                operation="test",
                request_id="req_123"
            )


class TestEnhancedDebugLogger:
    """Test EnhancedDebugLogger class."""
    
    def setup_method(self):
        """Set up test method."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock config to use temp directory
        with patch('src.utils.debug.config') as mock_config:
            mock_config.debug_logs_dir = self.temp_dir
            mock_config.debug_enabled = True
            mock_config.instructor_enabled = True
            self.debug_logger = EnhancedDebugLogger()
    
    def test_debug_logger_initialization(self):
        """Test debug logger initialization."""
        assert self.debug_logger.debug_dir == Path(self.temp_dir)
        assert self.debug_logger.request_count == 0
        assert self.debug_logger.total_processing_time == 0.0
        assert self.debug_logger.error_count == 0
    
    def test_request_id_generation(self):
        """Test request ID generation."""
        request_id1 = self.debug_logger.generate_request_id()
        request_id2 = self.debug_logger.generate_request_id()
        
        assert request_id1 != request_id2
        assert self.debug_logger.request_count == 2
    
    def test_request_response_logging(self):
        """Test request/response logging."""
        request_data = {
            "model": "anthropic/claude-3-5-sonnet",
            "messages": [{"role": "user", "content": "Hello"}],
            "tools": []
        }
        
        litellm_request = {
            "model": "anthropic/claude-3-5-sonnet",
            "messages": [{"role": "user", "content": "Hello"}],
            "api_key": "test-key-123"
        }
        
        mock_response = Mock()
        mock_response.usage = {"input_tokens": 10, "output_tokens": 15}
        
        filepath = self.debug_logger.log_request_response(
            request_data,
            litellm_request,
            litellm_response=mock_response,
            processing_time=1.5
        )
        
        assert filepath
        assert Path(filepath).exists()
        assert self.debug_logger.request_count == 1
        assert self.debug_logger.total_processing_time == 1.5
    
    def test_streaming_debug_logging(self):
        """Test streaming debug logging."""
        request_data = {"model": "test-model", "stream": True}
        litellm_request = {"model": "test-model", "stream": True}
        stream_events = [
            {"type": "message_start", "message": {"id": "msg_123"}},
            {"type": "content_block_delta", "delta": {"text": "Hello"}},
            {"type": "message_stop"}
        ]
        
        filepath = self.debug_logger.log_streaming_debug(
            request_data,
            litellm_request,
            stream_events,
            processing_time=2.0
        )
        
        assert filepath
        assert Path(filepath).exists()
    
    def test_instructor_operation_logging(self):
        """Test Instructor operation logging."""
        input_data = {
            "model": "anthropic/claude-3-5-sonnet",
            "messages": [{"role": "user", "content": "Test"}],
            "response_model": "TestModel"
        }
        
        mock_output = Mock()
        mock_output.model_dump.return_value = {"result": "success"}
        
        filepath = self.debug_logger.log_instructor_operation(
            "structured_completion",
            input_data,
            output_data=mock_output,
            processing_time=1.0
        )
        
        assert filepath
        assert Path(filepath).exists()
    
    def test_instructor_operation_with_error(self):
        """Test Instructor operation logging with error."""
        input_data = {"model": "test-model"}
        error = ValueError("Test error")
        
        filepath = self.debug_logger.log_instructor_operation(
            "validation",
            input_data,
            error=error,
            processing_time=0.5
        )
        
        assert filepath
        assert Path(filepath).exists()
    
    def test_performance_summary(self):
        """Test performance summary generation."""
        # Log some operations
        self.debug_logger.request_count = 5
        self.debug_logger.total_processing_time = 10.0
        self.debug_logger.error_count = 1
        
        summary = self.debug_logger.get_performance_summary()
        
        assert summary.request_count == 5
        assert summary.average_response_time == 2.0
        assert summary.error_rate == 0.2
    
    def test_stream_event_analysis(self):
        """Test stream event analysis."""
        stream_events = [
            {"type": "message_start"},
            {"type": "content_block_delta", "delta": {"text": "Hello"}},
            {"type": "content_block_delta", "delta": {"text": " world"}},
            {"type": "message_stop"}
        ]
        
        analysis = self.debug_logger._analyze_stream_events(stream_events)
        
        assert analysis["total_events"] == 4
        assert analysis["event_types"]["content_block_delta"] == 2
        assert analysis["total_content_length"] == 11  # "Hello world"
    
    def test_processing_time_categorization(self):
        """Test processing time categorization."""
        assert self.debug_logger._categorize_processing_time(0.5) == "fast"
        assert self.debug_logger._categorize_processing_time(3.0) == "normal"
        assert self.debug_logger._categorize_processing_time(10.0) == "slow"
        assert self.debug_logger._categorize_processing_time(20.0) == "very_slow"


class TestErrorClasses:
    """Test custom error classes."""
    
    def test_base_error(self):
        """Test base OpenRouterProxyError."""
        error = OpenRouterProxyError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_tool_validation_error(self):
        """Test ToolValidationError."""
        error = ToolValidationError("Tool validation failed")
        assert str(error) == "Tool validation failed"
        assert isinstance(error, OpenRouterProxyError)
    
    def test_instructor_error(self):
        """Test InstructorError."""
        error = InstructorError("Instructor operation failed")
        assert str(error) == "Instructor operation failed"
        assert isinstance(error, OpenRouterProxyError)
    
    def test_structured_output_error(self):
        """Test StructuredOutputError."""
        error = StructuredOutputError("Structured output generation failed")
        assert str(error) == "Structured output generation failed"
        assert isinstance(error, InstructorError)
    
    def test_validation_extraction_error(self):
        """Test ValidationExtractionError."""
        error = ValidationExtractionError("Validation extraction failed")
        assert str(error) == "Validation extraction failed"
        assert isinstance(error, InstructorError)


class TestLoggingIntegration:
    """Test logging system integration."""
    
    def test_setup_logging(self):
        """Test logging setup function."""
        # setup_logging() configures the system but doesn't return a logger
        setup_logging(log_level="DEBUG", development=True)
        
        # Get a logger after setup
        logger = get_logger("test_logger")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')
    
    def test_logging_with_different_configs(self):
        """Test logging with different configurations."""
        # Test development mode
        setup_logging(log_level="INFO", development=True)
        logger = get_logger("test_dev")
        logger.info("Development mode test")
        
        # Test production mode
        setup_logging(log_level="ERROR", development=False, json_logs=True)
        logger = get_logger("test_prod")
        logger.error("Production mode test")