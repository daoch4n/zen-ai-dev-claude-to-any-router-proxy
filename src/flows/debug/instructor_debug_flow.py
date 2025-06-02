"""Instructor debug flow for handling Instructor-specific operations."""

import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from ...models.instructor import DebugInfo, StructuredErrorInfo
from ...tasks.debug import (
    serialize_instructor_input,
    serialize_instructor_output,
    calculate_performance_metrics,
    generate_request_id,
    write_debug_file
)
from ...core.logging_config import get_logger

logger = get_logger("debug.instructor_flow")


class InstructorDebugFlow:
    """Flow for handling Instructor-specific debug logging operations."""
    
    def __init__(self, debug_dir: Path, session_id: str):
        """Initialize the instructor debug flow."""
        self.debug_dir = debug_dir
        self.session_id = session_id
    
    async def log_instructor_operation(
        self,
        operation_type: str,
        input_data: Dict[str, Any],
        output_data: Optional[Any] = None,
        error: Optional[Exception] = None,
        processing_time: float = 0.0,
        request_count: int = 1,
        total_processing_time: float = 0.0
    ) -> str:
        """Log Instructor-specific operations with detailed tracking."""
        
        request_id = generate_request_id(request_count)
        timestamp = datetime.now()
        
        debug_data = {
            "debug_info": DebugInfo(
                request_id=request_id,
                timestamp=timestamp.isoformat(),
                model_used=input_data.get("model", "instructor"),
                processing_time=processing_time
            ).model_dump(),
            "type": "instructor_operation",
            "operation_type": operation_type,
            "input_data": serialize_instructor_input(input_data),
            "output_data": serialize_instructor_output(output_data),
            "performance_metrics": calculate_performance_metrics(
                processing_time, total_processing_time, request_count
            )
        }
        
        if error:
            error_info = StructuredErrorInfo(
                error_type=type(error).__name__,
                error_message=str(error),
                context={"operation_type": operation_type, "request_id": request_id},
                recoverable=True
            )
            debug_data["error_info"] = error_info.model_dump()
            debug_data["stack_trace"] = traceback.format_exc()
        
        filename = f"instructor_{operation_type}_{request_id}.json"
        filepath = self.debug_dir / filename
        
        success = write_debug_file(filepath, debug_data)
        
        if success:
            logger.info("🎯 Instructor operation completed",
                       operation_type=operation_type,
                       model=input_data.get("model", "unknown"),
                       success=error is None,
                       request_id=request_id,
                       processing_time_ms=round(processing_time * 1000, 2))
            return str(filepath)
        else:
            logger.error("Instructor debug logging failed",
                        operation="instructor_debug_logging",
                        request_id=request_id)
            return ""