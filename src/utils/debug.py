"""Enhanced debug utilities with Instructor integration and structured logging."""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import traceback

from .config import config
from src.core.logging_config import get_logger
from src.models.instructor import DebugInfo, StructuredErrorInfo, PerformanceMetrics

logger = get_logger(__name__)

class EnhancedDebugLogger:
    """Enhanced debug logger with Instructor integration and structured outputs."""
    
    def __init__(self):
        """Initialize the enhanced debug logger."""
        self.debug_dir = Path(config.debug_logs_dir)
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Performance tracking
        self.request_count = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        
        logger.info("🔍 Enhanced debug logger initialized",
                   debug_dir=str(self.debug_dir),
                   session_id=self.session_id,
                   debug_enabled=config.debug_enabled)
    
    def generate_request_id(self) -> str:
        """Generate a unique request ID."""
        timestamp = datetime.now()
        self.request_count += 1
        return f"{timestamp.strftime('%Y%m%d_%H%M%S_%f')}_{self.request_count}"
    
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
        
        if request_id is None:
            request_id = self.generate_request_id()
        timestamp = datetime.now()
        
        # Use response_data if provided, otherwise use litellm_response
        actual_response = response_data if response_data is not None else litellm_response
        
        # Create structured debug info
        debug_info = DebugInfo(
            request_id=request_id,
            timestamp=timestamp.isoformat(),
            model_used=(request_data or {}).get("model", "unknown") if request_data else "unknown",
            token_usage=self._extract_token_usage(actual_response, anthropic_response),
            processing_time=processing_time,
            validation_results=instructor_data.get("validation_results", {}) if instructor_data else {},
            conversion_results=instructor_data.get("conversion_results", {}) if instructor_data else {}
        )
        
        # Build comprehensive debug data
        debug_data = {
            "debug_info": debug_info.model_dump(),
            "claude_code_request": self._serialize_request_data(request_data),
            "litellm_request": self._serialize_litellm_request(litellm_request),
            "litellm_response": self._serialize_response(actual_response),
            "anthropic_response": self._serialize_response(anthropic_response),
            "instructor_data": instructor_data or {},
            "performance_metrics": self._calculate_performance_metrics(processing_time),
            "environment": {
                "session_id": self.session_id,
                "config_snapshot": self._get_config_snapshot(),
                "timestamp": timestamp.isoformat()
            }
        }
        
        if error:
            error_info = StructuredErrorInfo(
                error_type="request_processing_error",
                error_message=error,
                context={"request_id": request_id, "model": request_data.get("model")},
                recoverable=True
            )
            debug_data["error_info"] = error_info.model_dump()
            self.error_count += 1
        
        # Write to file
        filename = f"request_response_{request_id}.json"
        filepath = self.debug_dir / filename
        
        try:
            # Custom JSON serializer that handles Mock objects
            def json_serializer(obj):
                if str(type(obj)).startswith("<class 'unittest.mock.Mock"):
                    return "Mock object (test environment)"
                try:
                    return str(obj)
                except:
                    return f"Unserializable object: {type(obj).__name__}"
            
            with open(filepath, 'w') as f:
                json.dump(debug_data, f, indent=2, default=json_serializer)
            
            logger.info("🔍 Debug log created",
                       filepath=str(filepath),
                       request_id=request_id,
                       processing_time_ms=round(processing_time * 1000, 2),
                       has_error=error is not None)
            
            # Update performance tracking
            self.total_processing_time += processing_time
            
            return str(filepath)
            
        except Exception as e:
            logger.error("Debug logging failed",
                        error_type=type(e).__name__,
                        error_message=str(e),
                        operation="debug_logging",
                        request_id=request_id)
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
        
        request_id = self.generate_request_id()
        timestamp = datetime.now()
        
        # Analyze stream events
        event_analysis = self._analyze_stream_events(stream_events)
        
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
            "claude_code_request": self._serialize_request_data(request_data),
            "litellm_request": self._serialize_litellm_request(litellm_request),
            "stream_events": stream_events,
            "stream_analysis": event_analysis,
            "instructor_data": instructor_data or {},
            "performance_metrics": self._calculate_performance_metrics(processing_time)
        }
        
        filename = f"streaming_{request_id}.json"
        filepath = self.debug_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(debug_data, f, indent=2, default=str)
            
            logger.info("🔍 Streaming debug log created",
                       filepath=str(filepath),
                       request_id=request_id,
                       event_count=len(stream_events),
                       processing_time_ms=round(processing_time * 1000, 2))
            
            return str(filepath)
            
        except Exception as e:
            logger.error("Streaming debug logging failed",
                        error_type=type(e).__name__,
                        error_message=str(e),
                        operation="streaming_debug_logging",
                        request_id=request_id)
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
        
        request_id = self.generate_request_id()
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
            "input_data": self._serialize_instructor_input(input_data),
            "output_data": self._serialize_instructor_output(output_data),
            "performance_metrics": self._calculate_performance_metrics(processing_time)
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
        
        try:
            with open(filepath, 'w') as f:
                json.dump(debug_data, f, indent=2, default=str)
            
            logger.info("🎯 Instructor operation completed",
                       operation_type=operation_type,
                       model=input_data.get("model", "unknown"),
                       success=error is None,
                       request_id=request_id,
                       processing_time_ms=round(processing_time * 1000, 2))
            
            return str(filepath)
            
        except Exception as e:
            logger.error("Instructor debug logging failed",
                        error_type=type(e).__name__,
                        error_message=str(e),
                        operation="instructor_debug_logging",
                        request_id=request_id)
            return ""
    
    def get_performance_summary(self) -> PerformanceMetrics:
        """Get current performance metrics summary."""
        avg_response_time = (
            self.total_processing_time / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        error_rate = (
            self.error_count / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        return PerformanceMetrics(
            request_count=self.request_count,
            average_response_time=avg_response_time,
            error_rate=error_rate,
            token_usage_stats=self._get_token_usage_stats(),
            model_usage_stats=self._get_model_usage_stats()
        )
    
    def _serialize_request_data(self, request_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced request data serialization."""
        if request_data is None:
            return {
                "model": None,
                "original_model": None,
                "max_tokens": None,
                "stream": None,
                "num_messages": 0,
                "num_tools": 0,
                "tool_names": [],
                "messages_preview": [],
                "instructor_enabled": config.instructor_enabled,
                "full_request": None
            }
        
        return {
            "model": request_data.get("model"),
            "original_model": request_data.get("original_model"),
            "max_tokens": request_data.get("max_tokens"),
            "stream": request_data.get("stream"),
            "num_messages": len(request_data.get("messages", [])),
            "num_tools": len(request_data.get("tools", [])),
            "tool_names": [tool.get("name") for tool in request_data.get("tools", [])],
            "messages_preview": self._serialize_messages_preview(request_data.get("messages", [])),
            "instructor_enabled": config.instructor_enabled,
            "full_request": request_data
        }
    
    def _serialize_messages_preview(self, messages: List[Any]) -> List[Dict[str, Any]]:
        """Create a preview of messages for logging."""
        previews = []
        for msg in messages[:5]:  # Limit to first 5 messages
            if hasattr(msg, 'model_dump'):
                msg_dict = msg.model_dump()
            elif isinstance(msg, dict):
                msg_dict = msg
            else:
                msg_dict = {"raw": str(msg)}
            
            content = msg_dict.get("content", "")
            if isinstance(content, str):
                preview = content[:100] + "..." if len(content) > 100 else content
                content_type = "string"
            else:
                preview = str(content)[:200] + "..." if len(str(content)) > 200 else str(content)
                content_type = "complex"
            
            previews.append({
                "role": msg_dict.get("role"),
                "content_type": content_type,
                "content_preview": preview
            })
        
        if len(messages) > 5:
            previews.append({"truncated": f"... and {len(messages) - 5} more messages"})
        
        return previews
    
    def _serialize_litellm_request(self, litellm_request: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced LiteLLM request serialization."""
        if litellm_request is None:
            return {
                "model": None,
                "num_messages": 0,
                "num_tools": 0,
                "stream": None,
                "max_tokens": None,
                "temperature": None,
                "instructor_enhanced": False,
                "full_request": None
            }
        
        safe_request = litellm_request.copy()
        if "api_key" in safe_request:
            safe_request["api_key"] = safe_request["api_key"][:10] + "..."
        
        return {
            "model": safe_request.get("model"),
            "num_messages": len(safe_request.get("messages", [])),
            "num_tools": len(safe_request.get("tools", [])),
            "stream": safe_request.get("stream"),
            "max_tokens": safe_request.get("max_tokens"),
            "temperature": safe_request.get("temperature"),
            "instructor_enhanced": "instructor" in str(safe_request),
            "full_request": safe_request
        }
    
    def _serialize_response(self, response: Any) -> Dict[str, Any]:
        """Enhanced response serialization."""
        if response is None:
            return {"type": None, "response_data": None}
        
        # Check if it's a Mock object
        if str(type(response)).startswith("<class 'unittest.mock.Mock"):
            return {
                "type": "Mock",
                "response_data": "Mock object (test environment)",
                "is_instructor_response": False
            }
        
        try:
            if hasattr(response, 'model_dump'):
                return {
                    "type": type(response).__name__,
                    "response_data": response.model_dump(),
                    "is_instructor_response": "instructor" in type(response).__module__.lower()
                }
            elif isinstance(response, dict):
                return {
                    "type": "dict",
                    "response_data": response,
                    "is_instructor_response": False
                }
            else:
                return {
                    "type": type(response).__name__,
                    "response_data": str(response),
                    "is_instructor_response": False
                }
        except Exception as e:
            return {
                "type": type(response).__name__,
                "response_data": f"Serialization failed: {e}",
                "is_instructor_response": False
            }
    
    def _serialize_instructor_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize Instructor input data."""
        return {
            "model": input_data.get("model"),
            "messages_count": len(input_data.get("messages", [])),
            "response_model": str(input_data.get("response_model")),
            "temperature": input_data.get("temperature"),
            "max_tokens": input_data.get("max_tokens"),
            "full_input": input_data
        }
    
    def _serialize_instructor_output(self, output_data: Any) -> Dict[str, Any]:
        """Serialize Instructor output data."""
        if output_data is None:
            return {"type": None, "data": None}
        
        try:
            if hasattr(output_data, 'model_dump'):
                return {
                    "type": type(output_data).__name__,
                    "data": output_data.model_dump(),
                    "is_structured": True
                }
            else:
                return {
                    "type": type(output_data).__name__,
                    "data": str(output_data),
                    "is_structured": False
                }
        except Exception as e:
            return {
                "type": type(output_data).__name__,
                "data": f"Serialization failed: {e}",
                "is_structured": False
            }
    
    def _extract_token_usage(self, litellm_response: Any, anthropic_response: Any) -> Dict[str, int]:
        """Extract token usage from responses."""
        usage = {}
        
        # Try LiteLLM response first
        if litellm_response and hasattr(litellm_response, 'usage'):
            if hasattr(litellm_response.usage, 'model_dump'):
                usage.update(litellm_response.usage.model_dump())
            elif isinstance(litellm_response.usage, dict):
                usage.update(litellm_response.usage)
        
        # Try Anthropic response
        if anthropic_response and hasattr(anthropic_response, 'usage'):
            if hasattr(anthropic_response.usage, 'model_dump'):
                usage.update(anthropic_response.usage.model_dump())
            elif isinstance(anthropic_response.usage, dict):
                usage.update(anthropic_response.usage)
        
        return usage
    
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
    
    def _calculate_performance_metrics(self, processing_time: float) -> Dict[str, Any]:
        """Calculate performance metrics for this request."""
        return {
            "processing_time_ms": round(processing_time * 1000, 2),
            "processing_time_category": self._categorize_processing_time(processing_time),
            "session_avg_time_ms": round((self.total_processing_time / max(self.request_count, 1)) * 1000, 2),
            "session_request_count": self.request_count
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
    
    def _get_config_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of current configuration."""
        return {
            "debug_enabled": config.debug_enabled,
            "instructor_enabled": config.instructor_enabled,
            "log_level": config.log_level,
            "max_tokens_limit": config.max_tokens_limit,
            "environment": "development" if config.is_development() else "production"
        }
    
    def _get_token_usage_stats(self) -> Dict[str, Any]:
        """Get token usage statistics (placeholder for future implementation)."""
        return {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "average_tokens_per_request": 0.0
        }
    
    def _get_model_usage_stats(self) -> Dict[str, int]:
        """Get model usage statistics (placeholder for future implementation)."""
        return {
            "claude-3-5-sonnet": 0,
            "claude-3-haiku": 0,
            "other": 0
        }

# Global enhanced debug logger instance
debug_logger = EnhancedDebugLogger()