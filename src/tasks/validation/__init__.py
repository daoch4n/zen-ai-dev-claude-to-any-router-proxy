"""Validation Tasks for OpenRouter Anthropic Server.

This module provides comprehensive Prefect validation tasks for all aspects
of the system including messages, tools, flows, requests, and security.

Part of Phase 6B/6C comprehensive refactoring - Validation Task Modules.
"""

# Message validation tasks
from .message_validation import (
    validate_message_format_task,
    validate_message_content_task,
    validate_system_message_task,
    validate_tool_calls_task
)

# Tool validation tasks  
from .tool_validation import (
    validate_tool_definition_task,
    validate_tool_execution_request_task,
    validate_tool_execution_result_task,
    validate_tool_registry_task
)

# Flow validation tasks
from .flow_validation import (
    validate_flow_definition_task,
    validate_flow_execution_state_task,
    validate_flow_dependencies_task,
    validate_flow_performance_task
)

# Request validation tasks
from .request_validation import (
    validate_http_request_task,
    validate_api_parameters_task,
    validate_anthropic_request_task,
    validate_request_rate_limit_task
)

# Security validation tasks
from .security_validation import (
    validate_content_safety_task,
    validate_request_authentication_task,
    validate_request_origin_task,
    validate_input_sanitization_task
)

__all__ = [
    # Message validation tasks
    "validate_message_format_task",
    "validate_message_content_task", 
    "validate_system_message_task",
    "validate_tool_calls_task",
    
    # Tool validation tasks
    "validate_tool_definition_task",
    "validate_tool_execution_request_task",
    "validate_tool_execution_result_task",
    "validate_tool_registry_task",
    
    # Flow validation tasks
    "validate_flow_definition_task",
    "validate_flow_execution_state_task",
    "validate_flow_dependencies_task",
    "validate_flow_performance_task",
    
    # Request validation tasks
    "validate_http_request_task",
    "validate_api_parameters_task",
    "validate_anthropic_request_task",
    "validate_request_rate_limit_task",
    
    # Security validation tasks
    "validate_content_safety_task",
    "validate_request_authentication_task",
    "validate_request_origin_task",
    "validate_input_sanitization_task"
]

# Validation task categories for easy access
MESSAGE_VALIDATION_TASKS = [
    validate_message_format_task,
    validate_message_content_task,
    validate_system_message_task,
    validate_tool_calls_task
]

TOOL_VALIDATION_TASKS = [
    validate_tool_definition_task,
    validate_tool_execution_request_task,
    validate_tool_execution_result_task,
    validate_tool_registry_task
]

FLOW_VALIDATION_TASKS = [
    validate_flow_definition_task,
    validate_flow_execution_state_task,
    validate_flow_dependencies_task,
    validate_flow_performance_task
]

REQUEST_VALIDATION_TASKS = [
    validate_http_request_task,
    validate_api_parameters_task,
    validate_anthropic_request_task,
    validate_request_rate_limit_task
]

SECURITY_VALIDATION_TASKS = [
    validate_content_safety_task,
    validate_request_authentication_task,
    validate_request_origin_task,
    validate_input_sanitization_task
]

# All validation tasks registry
ALL_VALIDATION_TASKS = (
    MESSAGE_VALIDATION_TASKS +
    TOOL_VALIDATION_TASKS +
    FLOW_VALIDATION_TASKS +
    REQUEST_VALIDATION_TASKS +
    SECURITY_VALIDATION_TASKS
)

def get_validation_tasks_by_category(category: str):
    """
    Get validation tasks by category.
    
    Args:
        category: Validation category ("message", "tool", "flow", "request", "security")
    
    Returns:
        List of validation tasks for the specified category
    
    Raises:
        ValueError: If category is not found
    """
    categories = {
        "message": MESSAGE_VALIDATION_TASKS,
        "tool": TOOL_VALIDATION_TASKS,
        "flow": FLOW_VALIDATION_TASKS,
        "request": REQUEST_VALIDATION_TASKS,
        "security": SECURITY_VALIDATION_TASKS
    }
    
    if category not in categories:
        available_categories = list(categories.keys())
        raise ValueError(f"Unknown validation category '{category}'. Available categories: {available_categories}")
    
    return categories[category]


def get_all_validation_tasks():
    """
    Get all validation tasks.
    
    Returns:
        List of all validation tasks
    """
    return ALL_VALIDATION_TASKS


def get_validation_task_count():
    """
    Get the total count of validation tasks.
    
    Returns:
        Total number of validation tasks
    """
    return len(ALL_VALIDATION_TASKS)


def get_validation_categories():
    """
    Get all available validation categories.
    
    Returns:
        List of validation categories
    """
    return ["message", "tool", "flow", "request", "security"]