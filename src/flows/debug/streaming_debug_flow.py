"""Streaming debug flow for handling streaming request logging."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from ...models.instructor import DebugInfo
from ...tasks.debug import (
    serialize_request_data,
    serialize_litellm_request,
    analyze_stream_events,
    calculate_performance_metrics,
    generate_request_id,
    write_debug_file
)
from ...core.logging_config import get_logger

logger = get_logger("debug.streaming_flow")


class StreamingDebugFlow:
    """Flow for handling streaming debug logging operations."""
    
    def __init__(self, debug_dir: Path, session_id: str):
        """Initialize the streaming debug flow."""
        self.debug_dir = debug_dir
        self.session_id = session_id
    
    async def log_streaming_debug(
        self,
        request_data: Dict[str, Any],
        litellm_request: Dict[str, Any],
        stream_events: List[Dict[str, Any]],
        instructor_data: Optional[Dict[str, Any]] = None,
        processing_time: float = 0.0,
        request_count: int = 1,
        total_processing_time: float = 0.0
    ) -> str:
        """Log streaming request with enhanced event tracking."""
        
        request_id = generate_request_id(request_count)
        timestamp = datetime.now()
        
        # Analyze stream events
        event_analysis = analyze_stream_events(stream_events)
        
        debug_data = {
            "debug_info": DebugInfo(
                request_id=request_id,
                timestamp=timestamp.isoformat(),
                model_used=request_data.get("model", "unknown"),
                processing_time=processing_time,
                validation_results=instructor_data.get("validation_results", {}) if instructor_data else {},
                conversion_results=instructor_data.get("conversion_results", {}) if instructor_data else {}
            ).model_dump(),
            "type": "streaming",
            "claude_code_request": serialize_request_data(request_data),
            "litellm_request": serialize_litellm_request(litellm_request),
            "stream_events": stream_events,
            "stream_analysis": event_analysis,
            "instructor_data": instructor_data or {},
            "performance_metrics": calculate_performance_metrics(
                processing_time, total_processing_time, request_count
            )
        }
        
        filename = f"streaming_{request_id}.json"
        filepath = self.debug_dir / filename
        
        success = write_debug_file(filepath, debug_data)
        
        if success:
            logger.info("🔍 Streaming debug log created",
                       filepath=str(filepath),
                       request_id=request_id,
                       event_count=len(stream_events),
                       processing_time_ms=round(processing_time * 1000, 2))
            return str(filepath)
        else:
            logger.error("Streaming debug logging failed",
                        operation="streaming_debug_logging",
                        request_id=request_id)
            return ""