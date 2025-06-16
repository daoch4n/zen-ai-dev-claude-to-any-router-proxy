"""
Batch Processing Tasks Module

This module provides functionality for processing multiple messages in batch requests,
a key Anthropic Beta Feature that enhances API compatibility and performance.
Supports batch validation, individual message processing, response aggregation,
and comprehensive error handling for partial batch failures.

Key Features:
- Batch request validation and structure validation
- Individual message conversion within batches
- Batch response aggregation and formatting
- Partial failure handling with detailed error reporting
- Performance optimization for large batch processing
- Memory-efficient processing with streaming support

Environment Variables:
- BATCH_MAX_SIZE: Maximum number of messages per batch (default: 100)
- BATCH_TIMEOUT: Timeout for batch processing in seconds (default: 300)
- BATCH_ENABLE_STREAMING: Enable streaming for large batches (default: false)

Author: Claude Code Proxy
Date: December 2024
"""

import asyncio
import os
import uuid
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
import time
from ...core.logging_config import get_logger
from ...models.instructor import ConversionResult
from ...models.anthropic import MessagesRequest, Message
from .message_conversion_tasks import convert_anthropic_message_to_litellm

logger = get_logger("conversion.batch_processing")


class BatchRequest:
    """Structured batch request for multiple message processing."""
    
    def __init__(self, messages: List[MessagesRequest], batch_id: Optional[str] = None):
        self.batch_id = batch_id or str(uuid.uuid4())
        self.messages = messages
        self.created_at = datetime.now(timezone.utc)
        self.status = "pending"
        self.total_messages = len(messages)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert batch request to dictionary."""
        return {
            "batch_id": self.batch_id,
            "total_messages": self.total_messages,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "messages": [msg.model_dump() for msg in self.messages]
        }


class BatchResponse:
    """Structured batch response with aggregated results."""
    
    def __init__(self, batch_id: str, results: List[ConversionResult]):
        self.batch_id = batch_id
        self.results = results
        self.total_messages = len(results)
        self.successful_messages = len([r for r in results if r.success])
        self.failed_messages = self.total_messages - self.successful_messages
        self.completion_time = datetime.now(timezone.utc)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert batch response to dictionary."""
        return {
            "batch_id": self.batch_id,
            "total_messages": self.total_messages,
            "successful_messages": self.successful_messages,
            "failed_messages": self.failed_messages,
            "success_rate": self.successful_messages / self.total_messages if self.total_messages > 0 else 0,
            "completion_time": self.completion_time.isoformat(),
            "results": [self._result_to_dict(r) for r in self.results]
        }
    
    def _result_to_dict(self, result: ConversionResult) -> Dict[str, Any]:
        """Convert conversion result to dictionary."""
        return {
            "success": result.success,
            "converted_data": result.converted_data,
            "errors": result.errors,
            "warnings": result.warnings,
            "metadata": result.metadata
        }


def validate_batch_request(batch_data: Dict[str, Any]) -> ConversionResult:
    """
    Validate a batch request structure and contents.
    
    Args:
        batch_data: Dictionary containing batch request data
        
    Returns:
        ConversionResult with validation status
    """
    try:
        errors = []
        warnings = []
        
        # Check required fields
        if "messages" not in batch_data:
            errors.append("Batch request must contain 'messages' field")
            return ConversionResult(
                success=False,
                converted_data=None,
                errors=errors
            )
        
        messages = batch_data["messages"]
        
        # Validate messages is a list
        if not isinstance(messages, list):
            errors.append("'messages' field must be a list")
            return ConversionResult(
                success=False,
                converted_data=None,
                errors=errors
            )
        
        # Check batch size limits
        max_batch_size = int(os.getenv("BATCH_MAX_SIZE", "100"))
        if len(messages) > max_batch_size:
            errors.append(f"Batch size {len(messages)} exceeds maximum {max_batch_size}")
            return ConversionResult(
                success=False,
                converted_data=None,
                errors=errors
            )
        
        if len(messages) == 0:
            warnings.append("Batch contains no messages")
        
        # Validate individual message structures
        for i, message_data in enumerate(messages):
            if not isinstance(message_data, dict):
                errors.append(f"Message {i} must be a dictionary")
                continue
                
            # Check required message fields
            required_fields = ["messages", "max_tokens"]
            for field in required_fields:
                if field not in message_data:
                    errors.append(f"Message {i} missing required field: {field}")
            
            # Validate message array within each request
            if "messages" in message_data:
                msg_array = message_data["messages"]
                if not isinstance(msg_array, list) or len(msg_array) == 0:
                    errors.append(f"Message {i} must contain non-empty messages array")
        
        success = len(errors) == 0
        
        if success:
            logger.debug("Batch request validation passed",
                        message_count=len(messages),
                        warnings_count=len(warnings))
        else:
            logger.warning("Batch request validation failed",
                         errors=errors, warnings=warnings)
        
        return ConversionResult(
            success=success,
            converted_data=batch_data if success else None,
            errors=errors,
            warnings=warnings
        )
        
    except Exception as e:
        logger.error("Error validating batch request", error=str(e))
        return ConversionResult(
            success=False,
            converted_data=None,
            errors=[f"Batch validation error: {str(e)}"]
        )


async def process_message_batch(
    batch_request: BatchRequest,
    conversion_flow: Any,
    enable_streaming: bool = False
) -> BatchResponse:
    """
    Process a batch of messages through the conversion pipeline.
    
    Args:
        batch_request: BatchRequest containing messages to process
        conversion_flow: Conversion flow instance to use for processing
        enable_streaming: Whether to enable streaming for large batches
        
    Returns:
        BatchResponse with aggregated results
    """
    try:
        batch_request.status = "processing"
        start_time = time.time()
        
        logger.info("Starting batch processing",
                   batch_id=batch_request.batch_id,
                   message_count=batch_request.total_messages)
        
        results = []
        
        if enable_streaming and batch_request.total_messages > 20:
            # Use streaming processing for large batches
            results = await _process_batch_streaming(batch_request, conversion_flow)
        else:
            # Use standard processing for smaller batches
            results = await _process_batch_standard(batch_request, conversion_flow)
        
        # Create batch response
        batch_response = BatchResponse(batch_request.batch_id, results)
        batch_request.status = "completed"
        
        processing_time = time.time() - start_time
        
        logger.info("Batch processing completed",
                   batch_id=batch_request.batch_id,
                   total_messages=batch_response.total_messages,
                   successful_messages=batch_response.successful_messages,
                   failed_messages=batch_response.failed_messages,
                   success_rate=batch_response.successful_messages / batch_response.total_messages,
                   processing_time_seconds=processing_time)
        
        return batch_response
        
    except Exception as e:
        batch_request.status = "failed"
        logger.error("Batch processing failed", 
                    batch_id=batch_request.batch_id,
                    error=str(e))
        
        # Return error result for all messages
        error_result = ConversionResult(
            success=False,
            converted_data=None,
            errors=[f"Batch processing failed: {str(e)}"]
        )
        
        results = [error_result] * batch_request.total_messages
        return BatchResponse(batch_request.batch_id, results)


async def _process_batch_standard(
    batch_request: BatchRequest,
    conversion_flow: Any
) -> List[ConversionResult]:
    """Process batch using standard approach."""
    results = []
    
    for i, message_request in enumerate(batch_request.messages):
        try:
            logger.debug("Processing message in batch",
                        batch_id=batch_request.batch_id,
                        message_index=i,
                        message_id=getattr(message_request, 'id', None))
            
            # Convert individual message
            result = conversion_flow.convert(message_request)
            results.append(result)
            
            if result.success:
                logger.debug("Message processed successfully",
                           batch_id=batch_request.batch_id,
                           message_index=i)
            else:
                logger.warning("Message processing failed",
                             batch_id=batch_request.batch_id,
                             message_index=i,
                             errors=result.errors)
            
        except Exception as e:
            logger.error("Error processing message in batch",
                        batch_id=batch_request.batch_id,
                        message_index=i,
                        error=str(e))
            
            error_result = ConversionResult(
                success=False,
                converted_data=None,
                errors=[f"Message {i} processing error: {str(e)}"]
            )
            results.append(error_result)
    
    return results


async def _process_batch_streaming(
    batch_request: BatchRequest,
    conversion_flow: Any
) -> List[ConversionResult]:
    """Process batch using streaming approach for large batches."""
    logger.info("Using streaming processing for large batch",
               batch_id=batch_request.batch_id,
               message_count=batch_request.total_messages)
    
    # Process in chunks to manage memory
    chunk_size = 10
    results = []
    
    for chunk_start in range(0, len(batch_request.messages), chunk_size):
        chunk_end = min(chunk_start + chunk_size, len(batch_request.messages))
        chunk = batch_request.messages[chunk_start:chunk_end]
        
        logger.debug("Processing batch chunk",
                    batch_id=batch_request.batch_id,
                    chunk_start=chunk_start,
                    chunk_end=chunk_end)
        
        # Process chunk concurrently
        chunk_tasks = []
        for i, message_request in enumerate(chunk):
            task = _process_single_message(
                message_request, 
                conversion_flow, 
                batch_request.batch_id,
                chunk_start + i
            )
            chunk_tasks.append(task)
        
        # Wait for chunk completion
        chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
        
        # Handle results and exceptions
        for result in chunk_results:
            if isinstance(result, Exception):
                error_result = ConversionResult(
                    success=False,
                    converted_data=None,
                    errors=[f"Concurrent processing error: {str(result)}"]
                )
                results.append(error_result)
            else:
                results.append(result)
    
    return results


async def _process_single_message(
    message_request: MessagesRequest,
    conversion_flow: Any,
    batch_id: str,
    message_index: int
) -> ConversionResult:
    """Process a single message with error handling."""
    try:
        result = conversion_flow.convert(message_request)
        return result
    except Exception as e:
        logger.error("Error in concurrent message processing",
                    batch_id=batch_id,
                    message_index=message_index,
                    error=str(e))
        return ConversionResult(
            success=False,
            converted_data=None,
            errors=[f"Message {message_index} error: {str(e)}"]
        )


def get_batch_processing_stats(batch_response: BatchResponse) -> Dict[str, Any]:
    """
    Get detailed statistics for batch processing results.
    
    Args:
        batch_response: BatchResponse to analyze
        
    Returns:
        Dictionary with detailed statistics
    """
    stats = {
        "batch_id": batch_response.batch_id,
        "total_messages": batch_response.total_messages,
        "successful_messages": batch_response.successful_messages,
        "failed_messages": batch_response.failed_messages,
        "success_rate": batch_response.successful_messages / batch_response.total_messages if batch_response.total_messages > 0 else 0,
        "error_categories": {},
        "warning_count": 0,
        "processing_metadata": {}
    }
    
    # Analyze error categories
    for result in batch_response.results:
        if result.errors:
            for error in result.errors:
                # Categorize errors by type
                if "validation" in error.lower():
                    category = "validation_errors"
                elif "conversion" in error.lower():
                    category = "conversion_errors"
                elif "timeout" in error.lower():
                    category = "timeout_errors"
                else:
                    category = "other_errors"
                
                stats["error_categories"][category] = stats["error_categories"].get(category, 0) + 1
        
        if result.warnings:
            stats["warning_count"] += len(result.warnings)
        
        # Aggregate processing metadata
        if result.metadata:
            for key, value in result.metadata.items():
                if key not in stats["processing_metadata"]:
                    stats["processing_metadata"][key] = []
                stats["processing_metadata"][key].append(value)
    
    return stats


def create_batch_request_from_dict(batch_data: Dict[str, Any]) -> BatchRequest:
    """
    Create a BatchRequest from dictionary data.
    
    Args:
        batch_data: Dictionary containing batch request data
        
    Returns:
        BatchRequest instance
    """
    try:
        messages = []
        
        for message_data in batch_data["messages"]:
            # Convert dict to MessagesRequest
            message_request = MessagesRequest(**message_data)
            messages.append(message_request)
        
        batch_id = batch_data.get("batch_id")
        batch_request = BatchRequest(messages, batch_id)
        
        logger.debug("Created batch request from dictionary",
                    batch_id=batch_request.batch_id,
                    message_count=len(messages))
        
        return batch_request
        
    except Exception as e:
        logger.error("Error creating batch request from dictionary", error=str(e))
        raise ValueError(f"Failed to create batch request: {str(e)}")