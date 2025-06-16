"""Tests for Batch Processing functionality."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from src.tasks.conversion.batch_processing_tasks import (
    BatchRequest,
    BatchResponse,
    validate_batch_request,
    process_message_batch,
    create_batch_request_from_dict,
    get_batch_processing_stats
)
from src.flows.conversion.batch_processing_flow import BatchProcessingFlow
from src.models.anthropic import MessagesRequest, Message
from src.models.instructor import ConversionResult


class TestBatchProcessingTasks:
    """Test batch processing task functions."""
    
    def test_validate_batch_request_valid(self):
        """Test validation of valid batch request."""
        valid_batch = {
            "messages": [
                {
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 100,
                    "model": "anthropic/claude-3-5-sonnet"
                },
                {
                    "messages": [{"role": "user", "content": "Hi there"}],
                    "max_tokens": 150,
                    "model": "anthropic/claude-3-5-sonnet"
                }
            ]
        }
        
        result = validate_batch_request(valid_batch)
        
        assert result.success is True
        assert result.converted_data == valid_batch
        assert len(result.errors) == 0
    
    def test_validate_batch_request_missing_messages(self):
        """Test validation with missing messages field."""
        invalid_batch = {"other_field": "value"}
        
        result = validate_batch_request(invalid_batch)
        
        assert result.success is False
        assert "Batch request must contain 'messages' field" in result.errors
    
    def test_validate_batch_request_invalid_messages_type(self):
        """Test validation with invalid messages type."""
        invalid_batch = {"messages": "not_a_list"}
        
        result = validate_batch_request(invalid_batch)
        
        assert result.success is False
        assert "'messages' field must be a list" in result.errors
    
    @patch.dict('os.environ', {'BATCH_MAX_SIZE': '2'})
    def test_validate_batch_request_exceeds_max_size(self):
        """Test validation with batch size exceeding limit."""
        large_batch = {
            "messages": [
                {"messages": [{"role": "user", "content": f"Message {i}"}], "max_tokens": 100}
                for i in range(5)  # Exceeds limit of 2
            ]
        }
        
        result = validate_batch_request(large_batch)
        
        assert result.success is False
        assert "Batch size 5 exceeds maximum 2" in result.errors
    
    def test_validate_batch_request_empty_messages(self):
        """Test validation with empty messages array."""
        empty_batch = {"messages": []}
        
        result = validate_batch_request(empty_batch)
        
        assert result.success is True
        assert "Batch contains no messages" in result.warnings
    
    def test_validate_batch_request_invalid_message_structure(self):
        """Test validation with invalid individual message structure."""
        invalid_batch = {
            "messages": [
                "not_a_dict",  # Invalid message structure
                {"messages": [{"role": "user", "content": "Valid"}], "max_tokens": 100}
            ]
        }
        
        result = validate_batch_request(invalid_batch)
        
        assert result.success is False
        assert "Message 0 must be a dictionary" in result.errors
    
    def test_create_batch_request_from_dict(self):
        """Test creating BatchRequest from dictionary."""
        batch_data = {
            "batch_id": "test-batch-123",
            "messages": [
                {
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 100,
                    "model": "anthropic/claude-3-5-sonnet"
                }
            ]
        }
        
        batch_request = create_batch_request_from_dict(batch_data)
        
        assert batch_request.batch_id == "test-batch-123"
        assert batch_request.total_messages == 1
        assert len(batch_request.messages) == 1
        assert batch_request.status == "pending"
    
    def test_create_batch_request_auto_id(self):
        """Test creating BatchRequest with auto-generated ID."""
        batch_data = {
            "messages": [
                {
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 100,
                    "model": "anthropic/claude-3-5-sonnet"
                }
            ]
        }
        
        batch_request = create_batch_request_from_dict(batch_data)
        
        assert batch_request.batch_id is not None
        assert len(batch_request.batch_id) > 0
        assert batch_request.total_messages == 1


class TestBatchProcessingAsync:
    """Test async batch processing functionality."""
    
    @pytest.mark.asyncio
    async def test_process_message_batch_success(self):
        """Test successful batch processing."""
        # Create test batch request
        messages = [
            MessagesRequest(
                messages=[Message(role="user", content="Hello")],
                max_tokens=100,
                model="anthropic/claude-3-5-sonnet"
            )
        ]
        batch_request = BatchRequest(messages, "test-batch")
        
        # Mock conversion flow
        mock_flow = Mock()
        mock_flow.convert.return_value = ConversionResult(
            success=True,
            converted_data={"response": "Test response"},
            errors=[],
            warnings=[]
        )
        
        # Process batch
        batch_response = await process_message_batch(batch_request, mock_flow)
        
        assert batch_response.batch_id == "test-batch"
        assert batch_response.total_messages == 1
        assert batch_response.successful_messages == 1
        assert batch_response.failed_messages == 0
        assert len(batch_response.results) == 1
    
    @pytest.mark.asyncio
    async def test_process_message_batch_partial_failure(self):
        """Test batch processing with partial failures."""
        # Create test batch request with 2 messages
        messages = [
            MessagesRequest(
                messages=[Message(role="user", content="Hello")],
                max_tokens=100,
                model="anthropic/claude-3-5-sonnet"
            ),
            MessagesRequest(
                messages=[Message(role="user", content="Hi")],
                max_tokens=100,
                model="anthropic/claude-3-5-sonnet"
            )
        ]
        batch_request = BatchRequest(messages, "test-batch")
        
        # Mock conversion flow with alternating success/failure
        mock_flow = Mock()
        mock_flow.convert.side_effect = [
            ConversionResult(success=True, converted_data={"response": "Success"}),
            ConversionResult(success=False, errors=["Conversion failed"])
        ]
        
        # Process batch
        batch_response = await process_message_batch(batch_request, mock_flow)
        
        assert batch_response.batch_id == "test-batch"
        assert batch_response.total_messages == 2
        assert batch_response.successful_messages == 1
        assert batch_response.failed_messages == 1
        assert len(batch_response.results) == 2
    
    @pytest.mark.asyncio
    async def test_process_message_batch_streaming(self):
        """Test batch processing with streaming enabled."""
        # Create large batch (>20 messages) to trigger streaming
        messages = [
            MessagesRequest(
                messages=[Message(role="user", content=f"Message {i}")],
                max_tokens=100,
                model="anthropic/claude-3-5-sonnet"
            )
            for i in range(25)
        ]
        batch_request = BatchRequest(messages, "streaming-batch")
        
        # Mock conversion flow
        mock_flow = Mock()
        mock_flow.convert.return_value = ConversionResult(
            success=True,
            converted_data={"response": "Test response"}
        )
        
        # Process batch with streaming enabled
        batch_response = await process_message_batch(batch_request, mock_flow, enable_streaming=True)
        
        assert batch_response.batch_id == "streaming-batch"
        assert batch_response.total_messages == 25
        assert batch_response.successful_messages == 25
        assert len(batch_response.results) == 25
    
    @pytest.mark.asyncio
    async def test_process_message_batch_exception_handling(self):
        """Test batch processing with exceptions."""
        messages = [
            MessagesRequest(
                messages=[Message(role="user", content="Hello")],
                max_tokens=100,
                model="anthropic/claude-3-5-sonnet"
            )
        ]
        batch_request = BatchRequest(messages, "error-batch")
        
        # Mock conversion flow that raises exception
        mock_flow = Mock()
        mock_flow.convert.side_effect = Exception("Conversion error")
        
        # Process batch
        batch_response = await process_message_batch(batch_request, mock_flow)
        
        assert batch_response.batch_id == "error-batch"
        assert batch_response.total_messages == 1
        assert batch_response.successful_messages == 0
        assert batch_response.failed_messages == 1
        assert len(batch_response.results) == 1
        assert not batch_response.results[0].success


class TestBatchProcessingFlow:
    """Test BatchProcessingFlow class."""
    
    def test_batch_processing_flow_initialization(self):
        """Test BatchProcessingFlow initialization."""
        flow = BatchProcessingFlow()
        
        # Check the service is properly initialized (service_name is accessed via method)
        assert hasattr(flow, 'conversion_flow')
        assert hasattr(flow, 'enable_streaming')
        assert hasattr(flow, 'max_batch_size')
        assert hasattr(flow, 'batch_timeout')
        
        # Verify service initialization worked
        assert flow.conversion_flow is not None
        assert isinstance(flow.enable_streaming, bool)
        assert isinstance(flow.max_batch_size, int)
        assert isinstance(flow.batch_timeout, int)
    
    def test_batch_processing_flow_convert_valid(self):
        """Test BatchProcessingFlow conversion with valid input."""
        flow = BatchProcessingFlow()
        
        # Mock the async processing
        with patch.object(flow, '_run_async_batch_processing') as mock_async:
            # Create a proper mock response with results attribute
            mock_result = ConversionResult(success=True, converted_data={"response": "Test"})
            
            mock_response = Mock()
            mock_response.batch_id = "test-batch"
            mock_response.total_messages = 1
            mock_response.successful_messages = 1
            mock_response.failed_messages = 0
            mock_response.completion_time.isoformat.return_value = "2024-12-05T10:00:00Z"
            mock_response.to_dict.return_value = {"batch_id": "test-batch", "total_messages": 1}
            mock_response.results = [mock_result]  # Add results attribute for stats calculation
            mock_async.return_value = mock_response
            
            batch_data = {
                "messages": [
                    {
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 100,
                        "model": "anthropic/claude-3-5-sonnet"
                    }
                ]
            }
            
            result = flow.convert(batch_data)
            
            assert result.success is True
            assert result.converted_data["batch_id"] == "test-batch"
    
    def test_batch_processing_flow_convert_invalid(self):
        """Test BatchProcessingFlow conversion with invalid input."""
        flow = BatchProcessingFlow()
        
        invalid_batch_data = {"invalid": "data"}
        
        result = flow.convert(invalid_batch_data)
        
        assert result.success is False
        assert len(result.errors) > 0
    
    def test_estimate_batch_processing_time(self):
        """Test batch processing time estimation."""
        flow = BatchProcessingFlow()
        
        # Test small batch (standard processing)
        small_estimate = flow.estimate_batch_processing_time(10)
        
        assert small_estimate["batch_size"] == 10
        assert small_estimate["processing_mode"] == "standard"
        assert small_estimate["estimated_time_seconds"] > 0
        
        # Test large batch (streaming processing)
        flow.enable_streaming = True
        large_estimate = flow.estimate_batch_processing_time(50)
        
        assert large_estimate["batch_size"] == 50
        assert large_estimate["processing_mode"] == "streaming"
        assert large_estimate["estimated_time_seconds"] > 0
        assert large_estimate["streaming_enabled"] is True


class TestBatchProcessingStats:
    """Test batch processing statistics functionality."""
    
    def test_get_batch_processing_stats(self):
        """Test generation of batch processing statistics."""
        # Create mock results
        results = [
            ConversionResult(success=True, converted_data={"response": "Success 1"}),
            ConversionResult(success=True, converted_data={"response": "Success 2"}),
            ConversionResult(success=False, errors=["Validation error"]),
            ConversionResult(success=False, errors=["Conversion error"]),
        ]
        
        batch_response = BatchResponse("test-batch", results)
        
        stats = get_batch_processing_stats(batch_response)
        
        assert stats["batch_id"] == "test-batch"
        assert stats["total_messages"] == 4
        assert stats["successful_messages"] == 2
        assert stats["failed_messages"] == 2
        assert stats["success_rate"] == 0.5
        assert "error_categories" in stats
    
    def test_batch_response_creation(self):
        """Test BatchResponse creation and methods."""
        results = [
            ConversionResult(success=True, converted_data={"response": "Success"}),
            ConversionResult(success=False, errors=["Error"])
        ]
        
        batch_response = BatchResponse("test-batch", results)
        
        assert batch_response.batch_id == "test-batch"
        assert batch_response.total_messages == 2
        assert batch_response.successful_messages == 1
        assert batch_response.failed_messages == 1
        
        response_dict = batch_response.to_dict()
        assert response_dict["batch_id"] == "test-batch"
        assert response_dict["success_rate"] == 0.5
        assert len(response_dict["results"]) == 2


class TestBatchProcessingIntegration:
    """Test batch processing integration scenarios."""
    
    def test_full_batch_processing_workflow(self):
        """Test complete batch processing workflow."""
        # Create batch data
        batch_data = {
            "messages": [
                {
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 100,
                    "model": "anthropic/claude-3-5-sonnet"
                },
                {
                    "messages": [{"role": "user", "content": "Hi there"}],
                    "max_tokens": 150,
                    "model": "anthropic/claude-3-5-sonnet"
                }
            ]
        }
        
        # Validate batch request
        validation_result = validate_batch_request(batch_data)
        assert validation_result.success is True
        
        # Create batch request
        batch_request = create_batch_request_from_dict(batch_data)
        assert batch_request.total_messages == 2
        
        # Test metadata initialization
        flow = BatchProcessingFlow()
        metadata = flow._initialize_batch_metadata(batch_data)
        assert metadata["original_batch_size"] == 2
    
    def test_error_handling_integration(self):
        """Test error handling throughout the batch processing pipeline."""
        flow = BatchProcessingFlow()
        
        # Test with completely invalid data
        invalid_data = None
        
        result = flow.convert(invalid_data)
        
        assert result.success is False
        assert len(result.errors) > 0
        assert "error_type" in result.metadata
    
    def test_batch_processing_with_warnings(self):
        """Test batch processing that generates warnings."""
        # Create batch with potential warnings (empty batch)
        batch_data = {"messages": []}
        
        validation_result = validate_batch_request(batch_data)
        
        assert validation_result.success is True
        assert "Batch contains no messages" in validation_result.warnings 