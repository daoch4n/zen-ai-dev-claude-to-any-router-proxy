"""Performance analysis tasks for debug utilities."""

from typing import Dict, Any, List
from ...models.instructor import PerformanceMetrics
from ...core.logging_config import get_logger

logger = get_logger("debug.performance_tasks")


def extract_token_usage(litellm_response: Any, anthropic_response: Any) -> Dict[str, int]:
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


def analyze_stream_events(stream_events: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def calculate_performance_metrics(
    processing_time: float, 
    total_processing_time: float, 
    request_count: int
) -> Dict[str, Any]:
    """Calculate performance metrics for this request."""
    return {
        "processing_time_ms": round(processing_time * 1000, 2),
        "processing_time_category": categorize_processing_time(processing_time),
        "session_avg_time_ms": round((total_processing_time / max(request_count, 1)) * 1000, 2),
        "session_request_count": request_count
    }


def categorize_processing_time(processing_time: float) -> str:
    """Categorize processing time for analysis."""
    if processing_time < 1.0:
        return "fast"
    elif processing_time < 5.0:
        return "normal"
    elif processing_time < 15.0:
        return "slow"
    else:
        return "very_slow"


def create_performance_summary(
    request_count: int,
    total_processing_time: float,
    error_count: int,
    token_usage_stats: Dict[str, Any],
    model_usage_stats: Dict[str, int]
) -> PerformanceMetrics:
    """Create a performance metrics summary."""
    avg_response_time = (
        total_processing_time / request_count 
        if request_count > 0 else 0.0
    )
    
    error_rate = (
        error_count / request_count 
        if request_count > 0 else 0.0
    )
    
    return PerformanceMetrics(
        request_count=request_count,
        average_response_time=avg_response_time,
        error_rate=error_rate,
        token_usage_stats=token_usage_stats,
        model_usage_stats=model_usage_stats
    )