"""LiteLLM models and types."""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
from .base import BaseOpenRouterModel

class LiteLLMMessage(BaseOpenRouterModel):
    """LiteLLM message format."""
    
    role: str
    content: Optional[Union[str, List[Dict[str, Any]]]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None  # For tool messages

class LiteLLMRequest(BaseOpenRouterModel):
    """LiteLLM request format."""
    
    model: str
    messages: List[LiteLLMMessage]
    max_tokens: int
    temperature: float = 1.0
    stream: bool = False
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    stop: Optional[List[str]] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    api_key: Optional[str] = None
    extra_headers: Optional[Dict[str, str]] = None

class LiteLLMResponse(BaseOpenRouterModel):
    """LiteLLM response format."""
    
    id: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, Any]
    model: str

class LiteLLMStreamChunk(BaseOpenRouterModel):
    """LiteLLM streaming chunk format."""
    
    id: str
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, Any]] = None
    model: str