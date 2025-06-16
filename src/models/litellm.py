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
    
    # Reasoning content support (LiteLLM v1.63.0+)
    reasoning_content: Optional[str] = None
    thinking_blocks: Optional[List[Dict[str, Any]]] = None

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
    
    # Reasoning content support
    reasoning_effort: Optional[str] = None  # "low", "medium", "high"
    thinking: Optional[Dict[str, Any]] = None  # For Anthropic thinking parameter
    
    # Exception handling
    drop_params: Optional[bool] = None  # For switching between providers

class LiteLLMResponse(BaseOpenRouterModel):
    """LiteLLM response format."""
    
    id: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, Any]
    model: str
    
    # Reasoning content fields
    reasoning_content: Optional[str] = None
    thinking_blocks: Optional[List[Dict[str, Any]]] = None

class LiteLLMStreamChunk(BaseOpenRouterModel):
    """LiteLLM streaming chunk format."""
    
    id: str
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, Any]] = None
    model: str
    
    # Reasoning content in streaming
    reasoning_content: Optional[str] = None

class ReasoningSupport(BaseOpenRouterModel):
    """Model reasoning capability information."""
    
    model: str
    supports_reasoning: bool
    supported_efforts: Optional[List[str]] = None  # ["low", "medium", "high"]
    provider: Optional[str] = None