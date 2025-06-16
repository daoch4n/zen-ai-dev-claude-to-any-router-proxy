"""Batch Processing Flow for Anthropic Beta Features

This flow orchestrates the processing of multiple messages in batch requests,
integrating with the existing conversion infrastructure to provide high-performance
batch processing capabilities.

Key Features:
- Batch request orchestration and validation
- Integration with existing conversion flows
- Performance optimization for large batches
- Comprehensive error handling and reporting
- Memory-efficient processing with streaming support
"""

from typing import Any, Dict, List, Optional
import asyncio
import os
from ...services.base import ConversionService, InstructorService
from ...models.instructor import ConversionResult
from ...tasks.conversion.batch_processing_tasks import (
    BatchRequest,
    BatchResponse,
    validate_batch_request,
    process_message_batch,
    create_batch_request_from_dict,
    get_batch_processing_stats
)
from ...flows.conversion.anthropic_to_litellm_flow import AnthropicToLiteLLMFlow
from ...core.logging_config import get_logger

logger = get_logger("flow.batch_processing")


class BatchProcessingFlow(ConversionService[Dict, BatchResponse], InstructorService):
    """Flow for processing multiple messages in batch requests."""
    
    def __init__(self):
        """Initialize batch processing flow."""
        ConversionService.__init__(self, "BatchProcessing")
        InstructorService.__init__(self, "BatchProcessing")
        
        # Initialize conversion flow for individual messages
        self.conversion_flow = AnthropicToLiteLLMFlow()
        
        # Configuration
        self.enable_streaming = os.getenv("BATCH_ENABLE_STREAMING", "false").lower() == "true"
        self.max_batch_size = int(os.getenv("BATCH_MAX_SIZE", "100"))
        self.batch_timeout = int(os.getenv("BATCH_TIMEOUT", "300"))
        
        logger.info("Batch processing flow initialized",
                   enable_streaming=self.enable_streaming,
                   max_batch_size=self.max_batch_size,
                   batch_timeout=self.batch_timeout)
    
    def convert(self, source: Dict[str, Any], **kwargs) -> ConversionResult:
        """
        Convert a batch request to processed batch response.
        
        Args:
            source: Dictionary containing batch request data
            **kwargs: Additional conversion parameters
            
        Returns:
            ConversionResult with BatchResponse data
        """
        try:
            # Initialize batch metadata
            batch_metadata = self._initialize_batch_metadata(source)
            
            # Validate batch request
            validation_result = self._validate_batch_request(source, batch_metadata)
            if not validation_result.success:
                return validation_result
            
            # Create batch request object
            batch_request = self._create_batch_request(source, batch_metadata)
            
            # Process batch
            batch_response = self._process_batch(batch_request, batch_metadata)
            
            # Create final result
            return self._create_batch_result(batch_response, batch_metadata)
            
        except Exception as e:
            logger.error("Batch processing flow failed",
                        error=str(e),
                        operation="batch_processing",
                        exc_info=True)
            return self.create_conversion_result(
                success=False,
                errors=[f"Batch processing failed: {str(e)}"],
                metadata={"error_type": type(e).__name__}
            )
    
    def _initialize_batch_metadata(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize batch processing metadata."""
        return {
            "original_batch_size": len(source.get("messages", [])),
            "processed_messages": 0,
            "failed_messages": 0,
            "streaming_enabled": self.enable_streaming,
            "timeout_used": self.batch_timeout
        }
    
    def _validate_batch_request(
        self, 
        source: Dict[str, Any], 
        metadata: Dict[str, Any]
    ) -> ConversionResult:
        """Validate the batch request structure and contents."""
        try:
            logger.debug("Validating batch request",
                        batch_size=metadata["original_batch_size"])
            
            # Use batch validation task
            validation_result = validate_batch_request(source)
            
            if validation_result.success:
                logger.info("Batch request validation passed",
                           batch_size=metadata["original_batch_size"],
                           warnings_count=len(validation_result.warnings))
                metadata["validation_warnings"] = len(validation_result.warnings)
            else:
                logger.error("Batch request validation failed",
                           errors=validation_result.errors)
                metadata["validation_errors"] = len(validation_result.errors)
            
            return validation_result
            
        except Exception as e:
            logger.error("Error during batch validation", error=str(e))
            return ConversionResult(
                success=False,
                converted_data=None,
                errors=[f"Batch validation error: {str(e)}"]
            )
    
    def _create_batch_request(
        self, 
        source: Dict[str, Any], 
        metadata: Dict[str, Any]
    ) -> BatchRequest:
        """Create a BatchRequest object from source data."""
        try:
            logger.debug("Creating batch request object",
                        batch_size=metadata["original_batch_size"])
            
            batch_request = create_batch_request_from_dict(source)
            
            logger.info("Batch request created successfully",
                       batch_id=batch_request.batch_id,
                       message_count=batch_request.total_messages)
            
            metadata["batch_id"] = batch_request.batch_id
            metadata["batch_created_at"] = batch_request.created_at.isoformat()
            
            return batch_request
            
        except Exception as e:
            logger.error("Error creating batch request", error=str(e))
            raise ValueError(f"Failed to create batch request: {str(e)}")
    
    def _process_batch(
        self, 
        batch_request: BatchRequest, 
        metadata: Dict[str, Any]
    ) -> BatchResponse:
        """Process the batch request through the conversion pipeline."""
        try:
            logger.info("Starting batch processing",
                       batch_id=batch_request.batch_id,
                       message_count=batch_request.total_messages,
                       streaming_enabled=metadata["streaming_enabled"])
            
            # Determine if streaming should be used
            use_streaming = (
                metadata["streaming_enabled"] and 
                batch_request.total_messages > 20
            )
            
            if use_streaming:
                logger.info("Using streaming processing for large batch",
                           batch_id=batch_request.batch_id)
            
            # Process batch (this will be synchronous wrapper for async processing)
            batch_response = self._run_async_batch_processing(
                batch_request, 
                use_streaming
            )
            
            # Update metadata with results
            metadata["processed_messages"] = batch_response.successful_messages
            metadata["failed_messages"] = batch_response.failed_messages
            metadata["success_rate"] = batch_response.successful_messages / batch_response.total_messages
            metadata["completion_time"] = batch_response.completion_time.isoformat()
            
            logger.info("Batch processing completed successfully",
                       batch_id=batch_request.batch_id,
                       successful_messages=batch_response.successful_messages,
                       failed_messages=batch_response.failed_messages,
                       success_rate=metadata["success_rate"])
            
            return batch_response
            
        except Exception as e:
            logger.error("Error during batch processing",
                        batch_id=batch_request.batch_id,
                        error=str(e))
            raise RuntimeError(f"Batch processing failed: {str(e)}")
    
    def _run_async_batch_processing(
        self, 
        batch_request: BatchRequest, 
        use_streaming: bool
    ) -> BatchResponse:
        """Run async batch processing in synchronous context."""
        try:
            # Create new event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async batch processing
            batch_response = loop.run_until_complete(
                process_message_batch(
                    batch_request,
                    self.conversion_flow,
                    use_streaming
                )
            )
            
            return batch_response
            
        except Exception as e:
            logger.error("Error in async batch processing", error=str(e))
            raise
    
    def _create_batch_result(
        self, 
        batch_response: BatchResponse, 
        metadata: Dict[str, Any]
    ) -> ConversionResult:
        """Create the final ConversionResult with batch response."""
        try:
            # Generate processing statistics
            batch_stats = get_batch_processing_stats(batch_response)
            
            # Combine metadata
            final_metadata = {
                **metadata,
                "batch_stats": batch_stats,
                "processing_complete": True
            }
            
            # Determine overall success
            success = batch_response.successful_messages > 0
            
            # Create warnings for partial failures
            warnings = []
            if batch_response.failed_messages > 0:
                warnings.append(
                    f"Partial batch failure: {batch_response.failed_messages} "
                    f"out of {batch_response.total_messages} messages failed"
                )
            
            # Create errors if all messages failed
            errors = []
            if batch_response.successful_messages == 0:
                errors.append("All messages in batch failed to process")
                success = False
            
            logger.info("Created batch result",
                       batch_id=batch_response.batch_id,
                       overall_success=success,
                       success_rate=batch_response.successful_messages / batch_response.total_messages)
            
            # Log operation success
            self.log_operation(
                "batch_processing",
                success,
                **final_metadata
            )
            
            return self.create_conversion_result(
                success=success,
                converted_data=batch_response.to_dict(),
                errors=errors,
                warnings=warnings,
                metadata=final_metadata
            )
            
        except Exception as e:
            logger.error("Error creating batch result", error=str(e))
            return self.create_conversion_result(
                success=False,
                errors=[f"Failed to create batch result: {str(e)}"],
                metadata=metadata
            )
    
    def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a batch processing operation.
        
        Args:
            batch_id: ID of the batch to check
            
        Returns:
            Dictionary with batch status information or None if not found
        """
        # This would typically integrate with a batch status storage system
        # For now, we'll return a placeholder implementation
        logger.debug("Batch status requested", batch_id=batch_id)
        
        # In a full implementation, this would query a status store
        return {
            "batch_id": batch_id,
            "status": "unknown",
            "message": "Batch status tracking not yet implemented"
        }
    
    def estimate_batch_processing_time(self, batch_size: int) -> Dict[str, Any]:
        """
        Estimate processing time for a batch of given size.
        
        Args:
            batch_size: Number of messages in the batch
            
        Returns:
            Dictionary with time estimates
        """
        try:
            # Base processing time per message (estimated)
            base_time_per_message = 0.1  # 100ms per message
            
            # Streaming vs standard processing
            if self.enable_streaming and batch_size > 20:
                # Streaming provides better parallelization
                concurrent_factor = 0.3  # 70% time reduction due to concurrency
                estimated_time = (batch_size * base_time_per_message) * concurrent_factor
                processing_mode = "streaming"
            else:
                # Standard sequential processing
                estimated_time = batch_size * base_time_per_message
                processing_mode = "standard"
            
            # Add overhead
            overhead = 2.0  # 2 seconds overhead
            total_estimated_time = estimated_time + overhead
            
            logger.debug("Estimated batch processing time",
                        batch_size=batch_size,
                        processing_mode=processing_mode,
                        estimated_seconds=total_estimated_time)
            
            return {
                "batch_size": batch_size,
                "processing_mode": processing_mode,
                "estimated_time_seconds": total_estimated_time,
                "estimated_time_per_message": estimated_time / batch_size if batch_size > 0 else 0,
                "overhead_seconds": overhead,
                "streaming_enabled": self.enable_streaming
            }
            
        except Exception as e:
            logger.error("Error estimating batch processing time", error=str(e))
            return {
                "error": f"Failed to estimate processing time: {str(e)}"
            } 