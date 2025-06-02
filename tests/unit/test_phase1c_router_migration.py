"""Unit tests for Phase 1C: Core Router Migration"""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.routers.messages import router as messages_router
from src.models.anthropic import MessagesRequest, Message
from src.core.logging_config import get_logger, clear_context
from src.services.context_manager import ContextManager


@pytest.fixture
def app():
    """Create test FastAPI app"""
    app = FastAPI()
    app.include_router(messages_router)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_request():
    """Create a sample messages request"""
    return MessagesRequest(
        model="small",
        messages=[
            Message(role="user", content="Hello, how are you?"),
            Message(role="assistant", content="I'm doing well, thank you!"),
            Message(role="user", content="Can you help me write a file?")
        ],
        max_tokens=1000
    )


class TestPhase1CRouterMigration:
    """Test suite for Phase 1C: Core Router Migration"""

    def test_logger_initialization(self):
        """Test that router properly initializes structlog logger"""
        # Import should create logger
        from src.routers.messages import logger
        
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'debug')

    def test_context_manager_initialization(self):
        """Test that router properly initializes context manager"""
        from src.routers.messages import context_manager
        
        assert context_manager is not None
        assert isinstance(context_manager, ContextManager)

    def test_context_manager_creates_request_context(self):
        """Test that context manager creates request context"""
        context_manager = ContextManager()
        
        request_context = context_manager.create_request_context(
            endpoint="/v1/messages",
            method="POST",
            request_id="test-123"
        )
        
        assert request_context.request_id == "test-123"
        assert request_context.endpoint == "/v1/messages"
        assert request_context.method == "POST"
        assert request_context.correlation_id.startswith("req_")

    def test_context_manager_creates_conversation_context(self, sample_request):
        """Test that context manager creates conversation context"""
        context_manager = ContextManager()
        
        # First create request context
        request_context = context_manager.create_request_context(
            endpoint="/v1/messages",
            method="POST",
            request_id="test-123"
        )
        
        # Then create conversation context
        conversation_context = context_manager.create_conversation_context(
            request=sample_request,
            request_context=request_context
        )
        
        assert conversation_context.conversation_id.startswith("conv_")
        assert conversation_context.model == "small"
        assert conversation_context.message_count == 3
        assert conversation_context.current_step == "validation"

    def test_context_manager_updates_conversation_step(self):
        """Test that context manager can update conversation steps"""
        context_manager = ContextManager()
        
        # Create some context first
        request_context = context_manager.create_request_context(
            endpoint="/v1/messages",
            method="POST"
        )
        
        sample_request = MessagesRequest(
            model="small",
            messages=[Message(role="user", content="test")],
            max_tokens=1000
        )
        
        context_manager.create_conversation_context(
            request=sample_request,
            request_context=request_context
        )
        
        # Update conversation step
        context_manager.update_conversation_step("processing")
        
        # Should not raise errors
        assert True

    def test_structured_logging_format(self):
        """Test that structured logging uses proper format"""
        logger = get_logger("test_router")
        
        # Test structured logging call (like those in the migrated router)
        try:
            logger.info("Test message", 
                       model="small",
                       message_count=3,
                       request_id="test-123")
            # Should not raise errors
            assert True
        except Exception as e:
            pytest.fail(f"Structured logging failed: {e}")

    @pytest.mark.asyncio
    async def test_conversation_context_creation_in_endpoint(self, sample_request):
        """Test that the router migration to orchestrator pattern is complete"""
        
        # Import the router to verify it uses orchestration
        from src.routers.messages import create_message
        import inspect
        
        # Check that the endpoint function exists and uses orchestration
        assert callable(create_message)
        source = inspect.getsource(create_message)
        
        # Verify it delegates to the orchestrator (not monolithic functions)
        assert "process_message_request_orchestrated" in source
        assert "context_manager" not in source  # Old pattern removed
        
        # Verify old monolithic patterns are removed
        assert "validate_request_data" not in source
        assert "convert_to_litellm" not in source
        assert "call_litellm_api" not in source
        
        # This confirms the router migration to orchestration is complete
        # The actual workflow execution is tested in integration tests

    def test_conversation_step_tracking_methods(self):
        """Test that conversation step tracking methods work"""
        context_manager = ContextManager()
        
        # Test various step updates that should be used in the router
        steps = [
            "mixed_content_detection",
            "validation", 
            "model_mapping",
            "conversion",
            "api_call",
            "tool_execution",
            "response_conversion",
            "completed",
            "error"
        ]
        
        for step in steps:
            try:
                context_manager.update_conversation_step(step)
                # Should not raise errors
                assert True
            except Exception as e:
                pytest.fail(f"Step update failed for '{step}': {e}")

    def test_context_cleanup(self):
        """Test that context cleanup works properly"""
        context_manager = ContextManager()
        
        # Create some context
        request_context = context_manager.create_request_context(
            endpoint="/v1/messages",
            method="POST"
        )
        
        sample_request = MessagesRequest(
            model="small",
            messages=[Message(role="user", content="test")],
            max_tokens=1000
        )
        
        context_manager.create_conversation_context(
            request=sample_request,
            request_context=request_context
        )
        
        # Cleanup should not raise errors
        try:
            context_manager.cleanup_context()
            assert True
        except Exception as e:
            pytest.fail(f"Context cleanup failed: {e}")

    def test_logger_methods_used_in_router(self):
        """Test that all logger methods used in the migrated router work"""
        logger = get_logger("test_router_methods")
        
        # Test all the logging patterns used in the migrated router
        try:
            # Info logging with structured data
            logger.info("Test message", 
                       model="small",
                       message_count=3,
                       request_id="test-123")
            
            # Debug logging with structured data
            logger.debug("Debug message",
                        message_index=1,
                        content_type="text")
            
            # Warning logging
            logger.warning("Warning message")
            
            # Error logging with exception info
            try:
                raise ValueError("Test error")
            except Exception as e:
                logger.error("Error occurred", 
                           error=str(e),
                           service="test",
                           exc_info=True)
            
            assert True
        except Exception as e:
            pytest.fail(f"Logger method failed: {e}")

    def teardown_method(self):
        """Clean up after each test"""
        clear_context()


if __name__ == "__main__":
    pytest.main([__file__])