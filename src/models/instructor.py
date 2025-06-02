"""Instructor-enhanced models for structured outputs."""

from typing import List, Dict, Any, Optional, Literal, Union
from pydantic import BaseModel, Field, field_validator
from .base import BaseOpenRouterModel

class StructuredToolCall(BaseModel):
    """Structured tool call with validation."""
    
    name: str = Field(..., description="Tool name")
    arguments: Dict[str, Any] = Field(..., description="Tool arguments")
    reasoning: Optional[str] = Field(None, description="Reasoning for tool use")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in tool call")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate tool name is not empty."""
        if not v or not v.strip():
            raise ValueError("Tool name cannot be empty")
        return v.strip()
    
    @field_validator('arguments')
    @classmethod
    def validate_arguments(cls, v):
        """Validate arguments is a proper dictionary."""
        if not isinstance(v, dict):
            raise ValueError("Arguments must be a dictionary")
        return v

class StructuredResponse(BaseOpenRouterModel):
    """Structured response with enhanced validation."""
    
    content: str = Field(..., description="Response content")
    tool_calls: List[StructuredToolCall] = Field(default_factory=list, description="Tool calls made")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Response confidence")
    reasoning: Optional[str] = Field(None, description="Response reasoning")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Validate content is not empty."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v

class ValidationResult(BaseModel):
    """Structured validation result."""
    
    is_valid: bool = Field(..., description="Whether the input is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    corrected_data: Optional[Dict[str, Any]] = Field(None, description="Corrected data if applicable")
    
    @field_validator('errors', 'warnings', 'suggestions')
    @classmethod
    def validate_lists(cls, v):
        """Ensure lists contain only non-empty strings."""
        return [item.strip() for item in v if item and item.strip()]

class ConversionResult(BaseModel):
    """Structured conversion result."""
    
    success: bool = Field(..., description="Whether conversion succeeded")
    converted_data: Optional[Dict[str, Any]] = Field(None, description="Converted data")
    errors: List[str] = Field(default_factory=list, description="Conversion errors")
    warnings: List[str] = Field(default_factory=list, description="Conversion warnings")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Conversion metadata")
    
    @field_validator('converted_data')
    @classmethod
    def validate_converted_data(cls, v, info):
        """Validate converted_data is present when success is True."""
        if info.data.get('success') and v is None:
            raise ValueError("converted_data must be provided when success is True")
        return v

class ToolValidationResult(BaseModel):
    """Structured tool validation result."""
    
    is_valid: bool = Field(..., description="Whether tools are valid")
    orphaned_tools: List[str] = Field(default_factory=list, description="Orphaned tool IDs")
    missing_results: List[str] = Field(default_factory=list, description="Missing tool result IDs")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    
    @property
    def has_orphaned_tools(self) -> bool:
        """Check if there are orphaned tools."""
        return len(self.orphaned_tools) > 0
    
    @property
    def has_missing_results(self) -> bool:
        """Check if there are missing tool results."""
        return len(self.missing_results) > 0

class ConversationFlowResult(BaseModel):
    """Structured conversation flow validation result."""
    
    is_valid: bool = Field(..., description="Whether conversation flow is valid")
    flow_errors: List[str] = Field(default_factory=list, description="Flow validation errors")
    role_sequence_valid: bool = Field(default=True, description="Whether role sequence is valid")
    tool_flow_valid: bool = Field(default=True, description="Whether tool flow is valid")
    suggestions: List[str] = Field(default_factory=list, description="Flow improvement suggestions")
    
    @property
    def has_flow_errors(self) -> bool:
        """Check if there are flow errors."""
        return len(self.flow_errors) > 0

class ModelMappingResult(BaseModel):
    """Structured model mapping result."""
    
    original_model: str = Field(..., description="Original model name")
    mapped_model: str = Field(..., description="Mapped model name")
    mapping_applied: bool = Field(..., description="Whether mapping was applied")
    mapping_type: Literal["big", "small", "passthrough", "configured"] = Field(..., description="Type of mapping")
    
    @field_validator('original_model', 'mapped_model')
    @classmethod
    def validate_models(cls, v):
        """Validate model names are not empty."""
        if not v or not v.strip():
            raise ValueError("Model name cannot be empty")
        return v.strip()

class DebugInfo(BaseModel):
    """Structured debug information."""
    
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: str = Field(..., description="Request timestamp")
    model_used: str = Field(..., description="Model used for request")
    token_usage: Dict[str, int] = Field(default_factory=dict, description="Token usage information")
    processing_time: float = Field(default=0.0, description="Processing time in seconds")
    validation_results: Dict[str, Any] = Field(default_factory=dict, description="Validation results")
    conversion_results: Dict[str, Any] = Field(default_factory=dict, description="Conversion results")
    
    @field_validator('request_id')
    @classmethod
    def validate_request_id(cls, v):
        """Validate request ID is not empty."""
        if not v or not v.strip():
            raise ValueError("Request ID cannot be empty")
        return v.strip()

class StructuredErrorInfo(BaseModel):
    """Structured error information."""
    
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code if applicable")
    context: Dict[str, Any] = Field(default_factory=dict, description="Error context")
    suggestions: List[str] = Field(default_factory=list, description="Error resolution suggestions")
    recoverable: bool = Field(default=False, description="Whether error is recoverable")
    
    @field_validator('error_type', 'error_message')
    @classmethod
    def validate_required_fields(cls, v):
        """Validate required fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Error type and message cannot be empty")
        return v.strip()

class PerformanceMetrics(BaseModel):
    """Structured performance metrics."""
    
    request_count: int = Field(default=0, description="Number of requests processed")
    average_response_time: float = Field(default=0.0, description="Average response time in seconds")
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Error rate (0.0-1.0)")
    token_usage_stats: Dict[str, Any] = Field(default_factory=dict, description="Token usage statistics")
    model_usage_stats: Dict[str, int] = Field(default_factory=dict, description="Model usage statistics")
    
    @field_validator('error_rate')
    @classmethod
    def validate_error_rate(cls, v):
        """Validate error rate is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Error rate must be between 0.0 and 1.0")
        return v