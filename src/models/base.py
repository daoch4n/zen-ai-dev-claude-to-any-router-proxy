"""Base models and common types."""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict

class BaseOpenRouterModel(BaseModel):
    """Base model for all OpenRouter proxy models."""
    
    model_config = ConfigDict(
        # Allow extra fields for flexibility
        extra="allow",
        # Use enum values for serialization
        use_enum_values=True
    )

class Usage(BaseModel):
    """Token usage information."""
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0

class Tool(BaseModel):
    """Tool definition."""
    name: str
    description: Optional[str] = None
    input_schema: Dict[str, Any]

class ThinkingConfig(BaseModel):
    """Thinking configuration."""
    enabled: bool = True