"""
OpenAI API format models for LiteLLM bypass implementation.

This module provides Pydantic models that match the OpenAI Chat Completion API format,
allowing direct communication with OpenRouter without LiteLLM intermediary.
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class OpenAIMessage(BaseModel):
    """OpenAI message format."""
    
    role: Literal["system", "user", "assistant", "tool"] = Field(..., description="Message role")
    content: Optional[Union[str, List[Dict[str, Any]]]] = Field(None, description="Message content")
    name: Optional[str] = Field(None, description="Message name (for function calls)")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls in message")
    tool_call_id: Optional[str] = Field(None, description="Tool call ID for tool responses")


class OpenAIFunction(BaseModel):
    """OpenAI function definition."""
    
    name: str = Field(..., description="Function name")
    description: Optional[str] = Field(None, description="Function description")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Function parameters schema")


class OpenAITool(BaseModel):
    """OpenAI tool definition."""
    
    type: Literal["function"] = Field(default="function", description="Tool type")
    function: OpenAIFunction = Field(..., description="Function definition")


class OpenAIToolChoice(BaseModel):
    """OpenAI tool choice configuration."""
    
    type: Literal["function"] = Field(..., description="Tool choice type")
    function: Dict[str, str] = Field(..., description="Function choice with name")


class OpenAIChatRequest(BaseModel):
    """OpenAI Chat Completion request format."""
    
    # Required fields
    model: str = Field(..., description="Model name")
    messages: List[OpenAIMessage] = Field(..., description="List of messages")
    
    # Optional core parameters
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Presence penalty")
    n: Optional[int] = Field(None, gt=0, description="Number of completions")
    
    # Streaming and tools
    stream: Optional[bool] = Field(False, description="Enable streaming")
    tools: Optional[List[OpenAITool]] = Field(None, description="Available tools")
    tool_choice: Optional[Union[str, OpenAIToolChoice]] = Field(None, description="Tool choice mode")
    
    # Advanced parameters
    seed: Optional[int] = Field(None, description="Random seed for deterministic output")
    user: Optional[str] = Field(None, description="User identifier")
    logit_bias: Optional[Dict[str, float]] = Field(None, description="Logit bias")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")
    
    # OpenRouter specific (passed through)
    provider: Optional[Dict[str, Any]] = Field(None, description="Provider-specific settings")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow additional fields for provider-specific parameters


class OpenAIUsage(BaseModel):
    """OpenAI usage statistics."""
    
    prompt_tokens: int = Field(..., description="Tokens in prompt")
    completion_tokens: int = Field(..., description="Tokens in completion")
    total_tokens: int = Field(..., description="Total tokens used")
    

class OpenAIChoice(BaseModel):
    """OpenAI completion choice."""
    
    index: int = Field(..., description="Choice index")
    message: OpenAIMessage = Field(..., description="Generated message")
    finish_reason: Optional[str] = Field(None, description="Reason for completion finish")
    logprobs: Optional[Dict[str, Any]] = Field(None, description="Log probabilities")


class OpenAIChatResponse(BaseModel):
    """OpenAI Chat Completion response format."""
    
    id: str = Field(..., description="Response ID")
    object: Literal["chat.completion"] = Field(default="chat.completion", description="Object type")
    created: int = Field(..., description="Creation timestamp")
    model: str = Field(..., description="Model used")
    choices: List[OpenAIChoice] = Field(..., description="Generated choices")
    usage: Optional[OpenAIUsage] = Field(None, description="Token usage statistics")
    system_fingerprint: Optional[str] = Field(None, description="System fingerprint")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow additional fields


class OpenAIStreamDelta(BaseModel):
    """OpenAI streaming delta."""
    
    role: Optional[str] = Field(None, description="Role delta")
    content: Optional[str] = Field(None, description="Content delta")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls delta")


class OpenAIStreamChoice(BaseModel):
    """OpenAI streaming choice."""
    
    index: int = Field(..., description="Choice index")
    delta: OpenAIStreamDelta = Field(..., description="Delta content")
    finish_reason: Optional[str] = Field(None, description="Finish reason")
    logprobs: Optional[Dict[str, Any]] = Field(None, description="Log probabilities")


class OpenAIStreamChunk(BaseModel):
    """OpenAI streaming chunk format."""
    
    id: str = Field(..., description="Chunk ID")
    object: Literal["chat.completion.chunk"] = Field(default="chat.completion.chunk", description="Object type")
    created: int = Field(..., description="Creation timestamp")
    model: str = Field(..., description="Model used")
    choices: List[OpenAIStreamChoice] = Field(..., description="Streaming choices")
    usage: Optional[OpenAIUsage] = Field(None, description="Token usage (final chunk)")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow additional fields


class OpenAIErrorDetail(BaseModel):
    """OpenAI error detail."""
    
    message: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")
    param: Optional[str] = Field(None, description="Parameter causing error")
    code: Optional[str] = Field(None, description="Error code")


class OpenAIError(BaseModel):
    """OpenAI error response."""
    
    error: OpenAIErrorDetail = Field(..., description="Error details")


# Utility functions for model conversion

def create_openai_message(role: str, content: Union[str, List[Dict[str, Any]]], **kwargs) -> OpenAIMessage:
    """Create an OpenAI message with proper validation."""
    return OpenAIMessage(role=role, content=content, **kwargs)


def create_openai_tool(name: str, description: str, parameters: Dict[str, Any]) -> OpenAITool:
    """Create an OpenAI tool definition."""
    function = OpenAIFunction(name=name, description=description, parameters=parameters)
    return OpenAITool(function=function)


def create_openai_request(
    model: str,
    messages: List[OpenAIMessage],
    **kwargs
) -> OpenAIChatRequest:
    """Create an OpenAI chat request with validation."""
    return OpenAIChatRequest(model=model, messages=messages, **kwargs)


def validate_openai_response(data: Dict[str, Any]) -> OpenAIChatResponse:
    """Validate and parse OpenAI response data."""
    return OpenAIChatResponse(**data)


def validate_openai_stream_chunk(data: Dict[str, Any]) -> OpenAIStreamChunk:
    """Validate and parse OpenAI streaming chunk data."""
    return OpenAIStreamChunk(**data) 