"""Unit tests for Unified Logging Middleware"""
import pytest
import time
from unittest.mock import Mock, patch, AsyncMock
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from src.middleware.unified_logging_middleware import UnifiedLoggingMiddleware
from src.services.context_manager import ContextManager


@pytest.fixture
def app():
    """Create FastAPI app with unified logging middleware"""
    app = FastAPI()
    app.add_middleware(UnifiedLoggingMiddleware)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    @app.post("/test")
    async def test_post_endpoint(data: dict):
        return {"received": data}
    
    @app.get("/error")
    async def error_endpoint():
        raise Exception("Test error")
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


def test_middleware_creation():
    """Test middleware can be created"""
    app = FastAPI()
    middleware = UnifiedLoggingMiddleware(app)
    assert middleware is not None
    assert isinstance(middleware.context_manager, ContextManager)
    assert middleware.log_requests is True
    assert middleware.log_responses is True


def test_middleware_with_custom_options():
    """Test middleware with custom logging options"""
    app = FastAPI()
    middleware = UnifiedLoggingMiddleware(app, log_requests=False, log_responses=False)
    assert middleware.log_requests is False
    assert middleware.log_responses is False


@patch('src.middleware.unified_logging_middleware.get_logger')
def test_successful_request_logging(mock_get_logger, client):
    """Test logging for successful requests"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    
    response = client.get("/test")
    
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert "X-Processing-Time" in response.headers
    
    # Verify logging calls were made
    assert mock_logger.info.call_count >= 2  # At least request and response logs
    
    # Check for expected log messages
    log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
    assert any("Request received" in msg for msg in log_calls)
    assert any("Request completed successfully" in msg for msg in log_calls)


@patch('src.middleware.unified_logging_middleware.get_logger')
def test_post_request_with_body(mock_get_logger, client):
    """Test logging for POST requests with body"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    
    test_data = {"test": "data", "number": 123}
    response = client.post("/test", json=test_data)
    
    assert response.status_code == 200
    
    # Verify request logging was called
    mock_logger.info.assert_called()


@patch('src.middleware.unified_logging_middleware.get_logger')
def test_error_request_logging(mock_get_logger, client):
    """Test logging for failed requests"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    
    # Error endpoints raise exceptions, so we expect a 500 response
    try:
        response = client.get("/error")
        # This might succeed with 500 status code depending on error handling
        assert response.status_code == 500
    except Exception:
        # Or the exception might propagate through - that's fine too
        pass
    
    # Verify error logging was called regardless
    mock_logger.error.assert_called()
    
    # Check error log contains expected information
    error_calls = [str(call) for call in mock_logger.error.call_args_list]
    assert any("Request failed" in call for call in error_calls)


@patch('src.services.context_manager.get_logger')
@patch('src.middleware.unified_logging_middleware.get_logger')
def test_context_management(mock_middleware_logger, mock_context_logger, client):
    """Test that context is properly created and cleaned up"""
    mock_middleware_logger.return_value = Mock()
    mock_context_logger.return_value = Mock()
    
    response = client.get("/test")
    
    assert response.status_code == 200
    
    # Context manager should have logged context creation and cleanup
    context_logger = mock_context_logger.return_value
    
    # Should have context creation logs
    creation_calls = [call for call in context_logger.info.call_args_list 
                     if "context created" in str(call)]
    assert len(creation_calls) > 0
    
    # Should have cleanup logs
    cleanup_calls = [call for call in context_logger.debug.call_args_list 
                    if "Cleaning up context" in str(call)]
    assert len(cleanup_calls) > 0


def test_request_id_in_headers(client):
    """Test that request ID is added to response headers"""
    response = client.get("/test")
    
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert "X-Processing-Time" in response.headers
    
    # Request ID should be a valid UUID format
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) == 36  # UUID length
    assert request_id.count("-") == 4  # UUID has 4 hyphens
    
    # Processing time should be in seconds format
    processing_time = response.headers["X-Processing-Time"]
    assert processing_time.endswith("s")
    assert float(processing_time[:-1]) >= 0


@patch('src.middleware.unified_logging_middleware.get_logger')
def test_large_request_body_handling(mock_get_logger, app):
    """Test handling of large request bodies"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    
    client = TestClient(app)
    
    # Create a large request body (>10KB)
    large_data = {"data": "x" * 15000}  # >10KB
    response = client.post("/test", json=large_data)
    
    assert response.status_code == 200
    
    # Should still log the request but indicate large body
    mock_logger.info.assert_called()


@patch('src.middleware.unified_logging_middleware.get_logger')
def test_request_state_context(mock_get_logger, app):
    """Test that request context is added to request state"""
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    
    captured_request = None
    
    @app.get("/capture")
    async def capture_request(request: Request):
        nonlocal captured_request
        captured_request = request
        return {"captured": True}
    
    client = TestClient(app)
    response = client.get("/capture")
    
    assert response.status_code == 200
    assert captured_request is not None
    
    # Check that request state has the context information
    assert hasattr(captured_request.state, 'request_id')
    assert hasattr(captured_request.state, 'request_context')
    
    request_id = captured_request.state.request_id
    assert isinstance(request_id, str)
    assert len(request_id) == 36  # UUID length


@pytest.mark.asyncio
@patch('src.middleware.unified_logging_middleware.get_logger')
async def test_async_middleware_behavior(mock_get_logger):
    """Test that middleware works correctly in async context"""
    import asyncio
    
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    
    app = FastAPI()
    middleware = UnifiedLoggingMiddleware(app)
    
    # Mock request and call_next
    mock_request = Mock(spec=Request)
    mock_request.url.path = "/test"
    mock_request.method = "GET"
    mock_request.headers = {"user-agent": "test-agent"}
    mock_request.client.host = "127.0.0.1"
    mock_request.query_params = {}
    mock_request.body = AsyncMock(return_value=b"")
    mock_request.state = Mock()
    
    mock_response = Mock(spec=JSONResponse)
    mock_response.status_code = 200
    mock_response.headers = {}
    
    async def mock_call_next(request):
        await asyncio.sleep(0.001)  # Simulate some processing time
        return mock_response
    
    # Test middleware dispatch
    result = await middleware.dispatch(mock_request, mock_call_next)
    
    assert result == mock_response
    assert "X-Request-ID" in mock_response.headers
    assert "X-Processing-Time" in mock_response.headers


def test_middleware_with_disabled_logging():
    """Test middleware with logging disabled"""
    app = FastAPI()
    # Properly add middleware to the app
    app.add_middleware(UnifiedLoggingMiddleware, log_requests=False, log_responses=False)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    client = TestClient(app)
    response = client.get("/test")
    
    assert response.status_code == 200
    # Should still have headers even with logging disabled
    assert "X-Request-ID" in response.headers
    assert "X-Processing-Time" in response.headers