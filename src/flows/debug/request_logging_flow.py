"""Request logging flow for handling complete request/response cycles."""

import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from ...models.instructor import DebugInfo, StructuredErrorInfo
from ...tasks.debug import (
    serialize_request_data,
    serialize_litellm_request,
    serialize_response,
    extract_token_usage,
    calculate_performance_metrics,
    get_config_snapshot,
    generate_request_id,
    write_debug_file,
    create_json_serializer
)
from ...core.logging_config import get_logger

logger = get_logger("debug.request_flow")


class RequestLoggingFlow:
    """Flow for handling request/response logging operations."""
    
    def __init__(self, debug_dir: Path, session_id: str):
        """Initialize the request logging flow."""
        self.debug_dir = debug_dir
        self.session_id = session_id
    
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
        success: bool = True,
        request_count: int = 1,
        total_processing_time: float = 0.0,
        error_count: int = 0
    ) -> str:
        """Log complete request/response cycle with enhanced structured data."""
        
        if request_id is None:
            request_id = generate_request_id(request_count)
        timestamp = datetime.now()
        
        # Use response_data if provided, otherwise use litellm_response
        actual_response = response_data if response_data is not None else litellm_response
        
        # Create structured debug info
        debug_info = DebugInfo(
            request_id=request_id,
            timestamp=timestamp.isoformat(),
            model_used=(request_data or {}).get("model", "unknown") if request_data else "unknown",
            token_usage=extract_token_usage(actual_response, anthropic_response),
            processing_time=processing_time,
            validation_results=instructor_data.get("validation_results", {}) if instructor_data else {},
            conversion_results=instructor_data.get("conversion_results", {}) if instructor_data else {}
        )
        
        # Build comprehensive debug data
        debug_data = {
            "debug_info": debug_info.model_dump(),
            "claude_code_request": serialize_request_data(request_data),
            "litellm_request": serialize_litellm_request(litellm_request),
            "litellm_response": serialize_response(actual_response),
            "anthropic_response": serialize_response(anthropic_response),
            "instructor_data": instructor_data or {},
            "performance_metrics": calculate_performance_metrics(
                processing_time, total_processing_time, request_count
            ),
            "environment": {
                "session_id": self.session_id,
                "config_snapshot": get_config_snapshot(),
                "timestamp": timestamp.isoformat()
            }
        }
        
        if error:
            error_info = StructuredErrorInfo(
                error_type="request_processing_error",
                error_message=error,
                context={"request_id": request_id, "model": (request_data or {}).get("model")},
                recoverable=True
            )
            debug_data["error_info"] = error_info.model_dump()
        
        # Write to file
        filename = f"request_response_{request_id}.json"
        filepath = self.debug_dir / filename
        
        json_serializer = create_json_serializer()
        success = write_debug_file(filepath, debug_data, json_serializer)
        
        if success:
            logger.info("🔍 Debug log created",
                       filepath=str(filepath),
                       request_id=request_id,
                       processing_time_ms=round(processing_time * 1000, 2),
                       has_error=error is not None)
            return str(filepath)
        else:
            logger.error("Debug logging failed",
                        operation="debug_logging",
                        request_id=request_id)
            return ""