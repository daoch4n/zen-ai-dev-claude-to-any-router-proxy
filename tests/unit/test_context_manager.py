"""Unit tests for Context Manager service"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.context_manager import (
    ContextManager,
    RequestContextData,
    ConversationContextData,
    ToolContextData
)
from src.models.anthropic import MessagesRequest, Message

def test_context_manager_creation():
    """Test ContextManager instantiation"""
    context_manager = ContextManager()
    assert context_manager is not None
    assert hasattr(context_manager, 'logger')

def test_request_context_creation():
    """Test request context creation and binding"""
    context_manager = ContextManager()
    
    context_data = context_manager.create_request_context(
        endpoint="/v1/messages",
        method="POST",
        user_agent="test-agent"
    )
    
    assert isinstance(context_data, RequestContextData)
    assert context_data.endpoint == "/v1/messages"
    assert context_data.method == "POST"
    assert context_data.user_agent == "test-agent"
    assert context_data.request_id is not None
    assert context_data.correlation_id.startswith("req_")
    assert isinstance(context_data.timestamp, datetime)

def test_request_context_with_custom_id():
    """Test request context creation with custom request ID"""
    context_manager = ContextManager()
    
    context_data = context_manager.create_request_context(
        endpoint="/v1/health",
        request_id="custom-123"
    )
    
    assert context_data.request_id == "custom-123"
    assert context_data.correlation_id == "req_custom-1"

def test_conversation_context_creation():
    """Test conversation context creation"""
    context_manager = ContextManager()
    
    # Create mock request
    request = MessagesRequest(
        model="small",
        max_tokens=1000,
        messages=[
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!")
        ]
    )
    
    # Create request context first
    request_context = RequestContextData(
        request_id="test-123",
        endpoint="/v1/messages",
        method="POST",
        user_agent=None,
        correlation_id="req_test-123",
        timestamp=datetime.utcnow()
    )
    
    conversation_context = context_manager.create_conversation_context(
        request=request,
        request_context=request_context
    )
    
    assert isinstance(conversation_context, ConversationContextData)
    assert conversation_context.conversation_id == "conv_test-123"
    assert conversation_context.model == "small"
    assert conversation_context.message_count == 2
    assert conversation_context.current_step == "validation"
    assert isinstance(conversation_context.metadata, dict)

def test_tool_context_creation():
    """Test tool context creation"""
    context_manager = ContextManager()
    
    tool_context = context_manager.create_tool_context(
        tool_name="Write",
        tool_call_id="call-456",
        input_data={"path": "test.txt", "content": "Hello World"},
        execution_step=2
    )
    
    assert isinstance(tool_context, ToolContextData)
    assert tool_context.tool_name == "Write"
    assert tool_context.tool_call_id == "call-456"
    assert tool_context.execution_step == 2
    assert tool_context.input_keys == ["path", "content"]

def test_conversation_step_update():
    """Test conversation step updating"""
    context_manager = ContextManager()
    
    # Should not raise errors even without existing context
    context_manager.update_conversation_step("api_call")
    context_manager.update_conversation_step("tool_execution")
    context_manager.update_conversation_step("response_formatting")

def test_context_cleanup():
    """Test context cleanup"""
    context_manager = ContextManager()
    
    # Create some context
    context_manager.create_request_context("/test")
    
    # Cleanup should not raise errors
    context_manager.cleanup_context()

@patch('src.services.context_manager.get_logger')
def test_context_manager_logging(mock_get_logger):
    """Test that context manager logs appropriately"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    
    context_manager = ContextManager()
    
    # Test request context logging
    context_manager.create_request_context("/v1/messages")
    mock_logger.info.assert_called()
    
    # Test conversation context logging
    request = MessagesRequest(model="small", max_tokens=1000, messages=[Message(role="user", content="test")])
    request_context = RequestContextData(
        request_id="test-123",
        endpoint="/v1/messages",
        method="POST",
        user_agent=None,
        correlation_id="req_test-123",
        timestamp=datetime.utcnow()
    )
    
    context_manager.create_conversation_context(request, request_context)
    assert mock_logger.info.call_count >= 2
    
    # Test tool context logging
    context_manager.create_tool_context("TestTool", "call-123", {"test": "data"})
    assert mock_logger.info.call_count >= 3
    
    # Test cleanup logging
    context_manager.cleanup_context()
    mock_logger.debug.assert_called()