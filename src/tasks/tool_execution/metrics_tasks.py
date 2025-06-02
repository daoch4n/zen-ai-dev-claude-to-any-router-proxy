"""Tool execution metrics and rate limiting task functions."""

import time
from typing import Any, Dict
from .tool_result_formatting_tasks import ToolExecutionResult
from ...core.logging_config import get_logger

logger = get_logger("tool_execution.metrics")


def update_tool_execution_metrics(metrics: Dict[str, Any], result: ToolExecutionResult) -> None:
    """Update metrics based on tool execution result"""
    metrics['total_executions'] += 1
    
    if result.success:
        metrics['successful_executions'] += 1
    else:
        metrics['failed_executions'] += 1
        error_type = result.error.split(':')[0] if result.error else 'unknown'
        metrics['error_count_by_type'][error_type] = metrics['error_count_by_type'].get(error_type, 0) + 1
    
    # Track execution times
    if result.tool_name not in metrics['execution_times']:
        metrics['execution_times'][result.tool_name] = []
    metrics['execution_times'][result.tool_name].append(result.execution_time)
    
    # Keep only last 100 execution times per tool
    if len(metrics['execution_times'][result.tool_name]) > 100:
        metrics['execution_times'][result.tool_name] = metrics['execution_times'][result.tool_name][-100:]
    
    # Track tool usage
    metrics['tool_usage_count'][result.tool_name] = metrics['tool_usage_count'].get(result.tool_name, 0) + 1


def check_rate_limit(
    rate_limit_tracker: Dict[str, float],
    request_id: str,
    rate_limit_window: float = 60,
    rate_limit_max_requests: int = 100
) -> bool:
    """Check if request is within rate limits"""
    current_time = time.time()
    
    # Clean old entries
    cutoff_time = current_time - rate_limit_window
    to_remove = [
        req_id for req_id, timestamp in rate_limit_tracker.items() 
        if timestamp <= cutoff_time
    ]
    for req_id in to_remove:
        del rate_limit_tracker[req_id]
    
    # Check if over limit
    if len(rate_limit_tracker) >= rate_limit_max_requests:
        logger.warning("Rate limit exceeded",
                      request_id=request_id,
                      current_requests=len(rate_limit_tracker),
                      max_requests=rate_limit_max_requests)
        return False
    
    # Track this request
    rate_limit_tracker[request_id] = current_time
    return True


def track_concurrent_execution(metrics: Dict[str, Any], increment: bool = True) -> None:
    """Track concurrent execution count and maximum"""
    if increment:
        metrics['concurrent_executions'] += 1
        metrics['max_concurrent_executions'] = max(
            metrics['max_concurrent_executions'],
            metrics['concurrent_executions']
        )
    else:
        metrics['concurrent_executions'] -= 1


def get_execution_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Get current tool execution metrics"""
    avg_execution_times = {}
    for tool_name, times in metrics['execution_times'].items():
        if times:
            avg_execution_times[tool_name] = sum(times) / len(times)
    
    return {
        'total_executions': metrics['total_executions'],
        'successful_executions': metrics['successful_executions'],
        'failed_executions': metrics['failed_executions'],
        'success_rate': metrics['successful_executions'] / max(1, metrics['total_executions']),
        'average_execution_times': avg_execution_times,
        'tool_usage_count': metrics['tool_usage_count'],
        'error_breakdown': metrics['error_count_by_type'],
        'max_concurrent_executions': metrics['max_concurrent_executions']
    }