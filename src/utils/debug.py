"""Enhanced debug utilities with modular architecture - Refactored."""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from ..coordinators.debug_coordinator import DebugCoordinator
from ..models.instructor import PerformanceMetrics
from ..core.logging_config import get_logger
from .config import config  # Import for test compatibility

logger = get_logger(__name__)


class EnhancedDebugLogger:
    """Enhanced debug logger with modular architecture - Refactored facade."""
    
    def __init__(self):
        """Initialize the enhanced debug logger."""
        # Reset coordinator to pick up any mocked config
        DebugCoordinator.reset_instance()
        self._coordinator = DebugCoordinator()
        logger.info("🔍 Enhanced debug logger initialized (refactored)",
                   debug_dir=str(self._coordinator.debug_dir),
                   session_id=self._coordinator.session_id)
    
    @property
    def debug_dir(self) -> Path:
        """Get debug directory from coordinator."""
        return self._coordinator.debug_dir
    
    @property
    def session_id(self) -> str:
        """Get session ID from coordinator."""
        return self._coordinator.session_id
    
    @property
    def request_count(self) -> int:
        """Get request count from coordinator."""
        return self._coordinator.request_count
    
    @request_count.setter
    def request_count(self, value: int):
        """Set request count in coordinator."""
        self._coordinator.request_count = value
    
    @property
    def total_processing_time(self) -> float:
        """Get total processing time from coordinator."""
        return self._coordinator.total_processing_time
    
    @total_processing_time.setter
    def total_processing_time(self, value: float):
        """Set total processing time in coordinator."""
        self._coordinator.total_processing_time = value
    
    @property
    def error_count(self) -> int:
        """Get error count from coordinator."""
        return self._coordinator.error_count
    
    @error_count.setter
    def error_count(self, value: int):
        """Set error count in coordinator."""
        self._coordinator.error_count = value
    
    def _run_async(self, coro):
        """Run async coroutine in sync context."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)
    
    def generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return self._coordinator.generate_request_id()
    
    def log_request_response(
        self,
        request_data: Optional[Dict[str, Any]] = None,
        litellm_request: Optional[Dict[str, Any]] = None,
        litellm_response: Optional[Any] = None,
        anthropic_response: Optional[Any] = None,
        instructor_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        processing_time: float = 0.0,
        request_id: Optional[str] = None,
        response_data: Optional[Any] = None,
        success: bool = True
    ) -> str:
        """Log complete request/response cycle with enhanced structured data."""
        try:
            return self._run_async(
                self._coordinator.log_request_response(
                    request_data=request_data,
                    litellm_request=litellm_request,
                    litellm_response=litellm_response,
                    anthropic_response=anthropic_response,
                    instructor_data=instructor_data,
                    error=error,
                    processing_time=processing_time,
                    request_id=request_id,
                    response_data=response_data,
                    success=success
                )
            )
        except Exception as e:
            logger.error("Request/response logging failed", error=str(e), exc_info=True)
            return ""
    
    def log_streaming_debug(
        self,
        request_data: Dict[str, Any],
        litellm_request: Dict[str, Any],
        stream_events: List[Dict[str, Any]],
        instructor_data: Optional[Dict[str, Any]] = None,
        processing_time: float = 0.0
    ) -> str:
        """Log streaming request with enhanced event tracking."""
        try:
            return self._run_async(
                self._coordinator.log_streaming_debug(
                    request_data=request_data,
                    litellm_request=litellm_request,
                    stream_events=stream_events,
                    instructor_data=instructor_data,
                    processing_time=processing_time
                )
            )
        except Exception as e:
            logger.error("Streaming debug logging failed", error=str(e), exc_info=True)
            return ""
    
    def log_instructor_operation(
        self,
        operation_type: str,
        input_data: Dict[str, Any],
        output_data: Optional[Any] = None,
        error: Optional[Exception] = None,
        processing_time: float = 0.0
    ) -> str:
        """Log Instructor-specific operations with detailed tracking."""
        try:
            return self._run_async(
                self._coordinator.log_instructor_operation(
                    operation_type=operation_type,
                    input_data=input_data,
                    output_data=output_data,
                    error=error,
                    processing_time=processing_time
                )
            )
        except Exception as e:
            logger.error("Instructor debug logging failed", error=str(e), exc_info=True)
            return ""
    
    def get_performance_summary(self) -> PerformanceMetrics:
        """Get current performance metrics summary."""
        try:
            return self._coordinator.get_performance_summary()
        except Exception as e:
            logger.error("Failed to get performance summary", error=str(e), exc_info=True)
            # Return empty metrics as fallback
            return PerformanceMetrics(
                request_count=0,
                average_response_time=0.0,
                error_rate=0.0,
                token_usage_stats={},
                model_usage_stats={}
            )
    
    def _analyze_stream_events(self, stream_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze streaming events for insights."""
        if not stream_events:
            return {"total_events": 0}
        
        event_types = {}
        total_content_length = 0
        
        for event in stream_events:
            event_type = event.get("type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Count content length for text deltas
            if event_type == "content_block_delta":
                delta = event.get("delta", {})
                if "text" in delta:
                    total_content_length += len(delta["text"])
        
        return {
            "total_events": len(stream_events),
            "event_types": event_types,
            "total_content_length": total_content_length,
            "avg_content_per_event": total_content_length / len(stream_events) if stream_events else 0
        }
    
    def _categorize_processing_time(self, processing_time: float) -> str:
        """Categorize processing time for analysis."""
        if processing_time < 1.0:
            return "fast"
        elif processing_time < 5.0:
            return "normal"
        elif processing_time < 15.0:
            return "slow"
        else:
            return "very_slow"


# Global enhanced debug logger instances - maintain backward compatibility
debug_logger = EnhancedDebugLogger()
enhanced_debug_logger = debug_logger  # Alias for compatibility