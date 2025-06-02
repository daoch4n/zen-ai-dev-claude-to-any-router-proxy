"""Data serialization tasks for debug utilities."""

import json
from typing import Dict, Any, Optional, List
# Import config in a way that allows test mocking
try:
    from ...utils.debug import config
except ImportError:
    from ...utils.config import config
from ...core.logging_config import get_logger

logger = get_logger("debug.serialization_tasks")


def create_json_serializer():
    """Create a custom JSON serializer that handles Mock objects."""
    def json_serializer(obj):
        if str(type(obj)).startswith("<class 'unittest.mock.Mock"):
            return "Mock object (test environment)"
        try:
            return str(obj)
        except:
            return f"Unserializable object: {type(obj).__name__}"
    return json_serializer


def serialize_request_data(request_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
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
        "messages_preview": serialize_messages_preview(request_data.get("messages", [])),
        "instructor_enabled": config.instructor_enabled,
        "full_request": request_data
    }


def serialize_messages_preview(messages: List[Any]) -> List[Dict[str, Any]]:
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


def serialize_litellm_request(litellm_request: Optional[Dict[str, Any]]) -> Dict[str, Any]:
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


def serialize_response(response: Any) -> Dict[str, Any]:
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


def serialize_instructor_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize Instructor input data."""
    return {
        "model": input_data.get("model"),
        "messages_count": len(input_data.get("messages", [])),
        "response_model": str(input_data.get("response_model")),
        "temperature": input_data.get("temperature"),
        "max_tokens": input_data.get("max_tokens"),
        "full_input": input_data
    }


def serialize_instructor_output(output_data: Any) -> Dict[str, Any]:
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