"""Unit tests for unified logging configuration"""
import pytest
import structlog
from unittest.mock import patch
from src.core.logging_config import (
    configure_structlog,
    get_logger,
    bind_request_context,
    bind_conversation_context,
    bind_tool_context,
    clear_context
)

def test_structlog_configuration():
    """Test structlog configuration"""
    configure_structlog(development=True)
    logger = get_logger("test")
    assert logger is not None
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')
    assert hasattr(logger, 'debug')

def test_get_logger():
    """Test logger creation"""
    logger = get_logger("test_module")
    assert logger is not None
    
    # Test logger without name
    logger_no_name = get_logger()
    assert logger_no_name is not None

def test_request_context_binding():
    """Test request context binding"""
    bind_request_context(
        request_id="test-123",
        endpoint="/v1/messages",
        method="POST",
        user_agent="test-agent",
        correlation_id="corr-123"
    )
    
    # Test that context is bound (we can't easily test the actual output without capturing logs)
    # But we can test that the function doesn't raise errors
    logger = get_logger("test")
    logger.info("Test message with request context")

def test_conversation_context_binding():
    """Test conversation context binding"""
    bind_conversation_context(
        conversation_id="conv-123",
        model="small",
        message_count=2,
        current_step="validation"
    )
    
    logger = get_logger("test")
    logger.info("Test message with conversation context")

def test_tool_context_binding():
    """Test tool context binding"""
    bind_tool_context(
        tool_name="Write",
        tool_call_id="call-123",
        execution_step=1,
        input_keys=["path", "content"]
    )
    
    logger = get_logger("test")
    logger.info("Test message with tool context")

def test_context_clearing():
    """Test context clearing"""
    # Bind some context
    bind_request_context("test-123", "/test")
    bind_conversation_context("conv-123", "small")
    bind_tool_context("TestTool", "call-123")
    
    # Clear context
    clear_context()
    
    # Should not raise errors
    logger = get_logger("test")
    logger.info("Test message after context clear")

def test_json_configuration():
    """Test JSON logging configuration"""
    configure_structlog(development=False, json_logs=True)
    logger = get_logger("test_json")
    logger.info("Test JSON logging")

def test_development_configuration():
    """Test development logging configuration"""
    configure_structlog(development=True, log_level="DEBUG")
    logger = get_logger("test_dev")
    logger.debug("Test development logging")