"""Debug coordinator for managing all debug operations."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from ..models.instructor import PerformanceMetrics
from ..flows.debug import (
    RequestLoggingFlow,
    StreamingDebugFlow,
    InstructorDebugFlow
)
from ..tasks.debug import (
    create_debug_directory,
    get_token_usage_stats,
    get_model_usage_stats,
    create_performance_summary
)
# Import config in a way that allows test mocking
try:
    from ..utils.debug import config
except ImportError:
    from ..utils.config import config
from ..core.logging_config import get_logger

logger = get_logger("debug.coordinator")


class DebugCoordinator:
    """Coordinator for managing all debug operations and flows."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern for global debug coordination."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (for testing purposes)."""
        if cls._instance is not None:
            cls._instance._initialized = False
        cls._instance = None
    
    def __init__(self):
        """Initialize the debug coordinator."""
        if hasattr(self, '_initialized'):
            return
            
        self.debug_dir = Path(config.debug_logs_dir)
        create_debug_directory(self.debug_dir)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Performance tracking
        self.request_count = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        
        # Initialize flows
        self.request_flow = RequestLoggingFlow(self.debug_dir, self.session_id)
        self.streaming_flow = StreamingDebugFlow(self.debug_dir, self.session_id)
        self.instructor_flow = InstructorDebugFlow(self.debug_dir, self.session_id)
        
        self._initialized = True
        
        logger.info("🔍 Enhanced debug coordinator initialized",
                   debug_dir=str(self.debug_dir),
                   session_id=self.session_id,
                   debug_enabled=config.debug_enabled)
    
    def generate_request_id(self) -> str:
        """Generate a unique request ID and increment counter."""
        from ..tasks.debug import generate_request_id
        self.request_count += 1
        return generate_request_id(self.request_count)
    
    async def log_request_response(
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
        """Coordinate request/response logging through the appropriate flow."""
        try:
            # Generate request ID if not provided and increment count
            if request_id is None:
                request_id = self.generate_request_id()
            else:
                # Still increment count even if request_id was provided
                self.request_count += 1
            
            # Update performance tracking
            self.total_processing_time += processing_time
            if error:
                self.error_count += 1
            
            result = await self.request_flow.log_request_response(
                request_data=request_data,
                litellm_request=litellm_request,
                litellm_response=litellm_response,
                anthropic_response=anthropic_response,
                instructor_data=instructor_data,
                error=error,
                processing_time=processing_time,
                request_id=request_id,
                response_data=response_data,
                success=success,
                request_count=self.request_count,
                total_processing_time=self.total_processing_time,
                error_count=self.error_count
            )
            
            logger.debug("Request/response logging coordinated", 
                        request_id=request_id, 
                        success=bool(result))
            return result
            
        except Exception as e:
            logger.error("Request/response logging coordination failed", 
                        error=str(e), exc_info=True)
            return ""
    
    async def log_streaming_debug(
        self,
        request_data: Dict[str, Any],
        litellm_request: Dict[str, Any],
        stream_events: List[Dict[str, Any]],
        instructor_data: Optional[Dict[str, Any]] = None,
        processing_time: float = 0.0
    ) -> str:
        """Coordinate streaming debug logging through the appropriate flow."""
        try:
            # Update performance tracking
            self.total_processing_time += processing_time
            
            result = await self.streaming_flow.log_streaming_debug(
                request_data=request_data,
                litellm_request=litellm_request,
                stream_events=stream_events,
                instructor_data=instructor_data,
                processing_time=processing_time,
                request_count=self.request_count,
                total_processing_time=self.total_processing_time
            )
            
            logger.debug("Streaming debug logging coordinated", 
                        event_count=len(stream_events), 
                        success=bool(result))
            return result
            
        except Exception as e:
            logger.error("Streaming debug logging coordination failed", 
                        error=str(e), exc_info=True)
            return ""
    
    async def log_instructor_operation(
        self,
        operation_type: str,
        input_data: Dict[str, Any],
        output_data: Optional[Any] = None,
        error: Optional[Exception] = None,
        processing_time: float = 0.0
    ) -> str:
        """Coordinate instructor operation logging through the appropriate flow."""
        try:
            # Update performance tracking
            self.total_processing_time += processing_time
            if error:
                self.error_count += 1
            
            result = await self.instructor_flow.log_instructor_operation(
                operation_type=operation_type,
                input_data=input_data,
                output_data=output_data,
                error=error,
                processing_time=processing_time,
                request_count=self.request_count,
                total_processing_time=self.total_processing_time
            )
            
            logger.debug("Instructor operation logging coordinated", 
                        operation_type=operation_type, 
                        success=bool(result))
            return result
            
        except Exception as e:
            logger.error("Instructor operation logging coordination failed", 
                        error=str(e), exc_info=True)
            return ""
    
    def get_performance_summary(self) -> PerformanceMetrics:
        """Get current performance metrics summary."""
        try:
            return create_performance_summary(
                request_count=self.request_count,
                total_processing_time=self.total_processing_time,
                error_count=self.error_count,
                token_usage_stats=get_token_usage_stats(),
                model_usage_stats=get_model_usage_stats()
            )
        except Exception as e:
            logger.error("Failed to create performance summary", error=str(e), exc_info=True)
            # Return empty metrics as fallback
            return PerformanceMetrics(
                request_count=0,
                average_response_time=0.0,
                error_rate=0.0,
                token_usage_stats={},
                model_usage_stats={}
            )