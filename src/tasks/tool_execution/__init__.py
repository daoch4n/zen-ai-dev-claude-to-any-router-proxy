"""Tool execution task modules."""

from .tool_detection_tasks import (
    detect_tool_use_blocks,
    extract_tool_use_blocks,
    check_tools_need_confirmation
)

from .tool_result_formatting_tasks import (
    format_tool_result_content,
    create_tool_result_block,
    truncate_result_content
)

from .tool_execution_tasks import (
    execute_single_tool_with_timeout,
    validate_tool_input,
    check_tool_permissions
)

from .conversation_continuation_tasks import (
    create_assistant_tool_use_message,
    create_user_tool_result_message,
    create_tool_result_messages
)

from .metrics_tasks import (
    update_tool_execution_metrics,
    check_rate_limit,
    track_concurrent_execution,
    get_execution_metrics
)

__all__ = [
    # Tool detection
    "detect_tool_use_blocks",
    "extract_tool_use_blocks", 
    "check_tools_need_confirmation",
    
    # Result formatting
    "format_tool_result_content",
    "create_tool_result_block",
    "truncate_result_content",
    
    # Tool execution
    "execute_single_tool_with_timeout",
    "validate_tool_input",
    "check_tool_permissions",
    
    # Conversation continuation
    "create_assistant_tool_use_message",
    "create_user_tool_result_message", 
    "create_tool_result_messages",
    
    # Metrics and rate limiting
    "update_tool_execution_metrics",
    "check_rate_limit",
    "track_concurrent_execution",
    "get_execution_metrics",
]