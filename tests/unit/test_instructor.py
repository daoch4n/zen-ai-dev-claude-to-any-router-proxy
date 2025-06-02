"""Unit tests for Instructor integration and models."""

import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError

from src.models.instructor import (
    StructuredToolCall,
    StructuredResponse,
    ValidationResult,
    ConversionResult,
    ToolValidationResult,
    ConversationFlowResult,
    ModelMappingResult,
    DebugInfo,
    StructuredErrorInfo,
    PerformanceMetrics
)
from src.utils.instructor_client import InstructorClient
from src.utils.errors import StructuredOutputError


class TestStructuredToolCall:
    """Test StructuredToolCall model."""
    
    def test_valid_tool_call(self):
        """Test creating a valid tool call."""
        tool_call = StructuredToolCall(
            name="get_weather",
            arguments={"location": "San Francisco", "units": "celsius"},
            reasoning="User asked for weather information",
            confidence=0.95
        )
        
        assert tool_call.name == "get_weather"
        assert tool_call.arguments["location"] == "San Francisco"
        assert tool_call.reasoning == "User asked for weather information"
        assert tool_call.confidence == 0.95
    
    def test_empty_name_validation(self):
        """Test that empty tool name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            StructuredToolCall(
                name="",
                arguments={"location": "San Francisco"}
            )
        
        assert "Tool name cannot be empty" in str(exc_info.value)
    
    def test_whitespace_name_validation(self):
        """Test that whitespace-only tool name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            StructuredToolCall(
                name="   ",
                arguments={"location": "San Francisco"}
            )
        
        assert "Tool name cannot be empty" in str(exc_info.value)
    
    def test_invalid_arguments_type(self):
        """Test that non-dict arguments raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            StructuredToolCall(
                name="get_weather",
                arguments="invalid"
            )
        
        # Check for the actual Pydantic error message
        assert "Input should be a valid dictionary" in str(exc_info.value)
    
    def test_confidence_bounds(self):
        """Test confidence value bounds."""
        # Valid confidence values
        tool_call = StructuredToolCall(
            name="test",
            arguments={},
            confidence=0.0
        )
        assert tool_call.confidence == 0.0
        
        tool_call = StructuredToolCall(
            name="test",
            arguments={},
            confidence=1.0
        )
        assert tool_call.confidence == 1.0
        
        # Invalid confidence values
        with pytest.raises(ValidationError):
            StructuredToolCall(
                name="test",
                arguments={},
                confidence=-0.1
            )
        
        with pytest.raises(ValidationError):
            StructuredToolCall(
                name="test",
                arguments={},
                confidence=1.1
            )


class TestStructuredResponse:
    """Test StructuredResponse model."""
    
    def test_valid_response(self):
        """Test creating a valid structured response."""
        tool_call = StructuredToolCall(
            name="get_weather",
            arguments={"location": "San Francisco"}
        )
        
        response = StructuredResponse(
            content="The weather in San Francisco is sunny.",
            tool_calls=[tool_call],
            confidence=0.9,
            reasoning="Provided weather information as requested",
            metadata={"source": "weather_api"}
        )
        
        assert response.content == "The weather in San Francisco is sunny."
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "get_weather"
        assert response.confidence == 0.9
        assert response.metadata["source"] == "weather_api"
    
    def test_empty_content_validation(self):
        """Test that empty content raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            StructuredResponse(content="")
        
        assert "Content cannot be empty" in str(exc_info.value)
    
    def test_whitespace_content_validation(self):
        """Test that whitespace-only content raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            StructuredResponse(content="   ")
        
        assert "Content cannot be empty" in str(exc_info.value)


class TestValidationResult:
    """Test ValidationResult model."""
    
    def test_valid_result(self):
        """Test creating a valid validation result."""
        result = ValidationResult(
            is_valid=False,
            errors=["Missing required field"],
            warnings=["Deprecated field used"],
            suggestions=["Use new field instead"],
            corrected_data={"field": "corrected_value"}
        )
        
        assert not result.is_valid
        assert "Missing required field" in result.errors
        assert "Deprecated field used" in result.warnings
        assert "Use new field instead" in result.suggestions
        assert result.corrected_data["field"] == "corrected_value"
    
    def test_list_validation(self):
        """Test that empty strings are filtered from lists."""
        result = ValidationResult(
            is_valid=True,
            errors=["Valid error", "", "  ", "Another error"],
            warnings=["Valid warning", ""],
            suggestions=["Valid suggestion", "   "]
        )
        
        assert result.errors == ["Valid error", "Another error"]
        assert result.warnings == ["Valid warning"]
        assert result.suggestions == ["Valid suggestion"]


class TestConversionResult:
    """Test ConversionResult model."""
    
    def test_successful_conversion(self):
        """Test successful conversion result."""
        result = ConversionResult(
            success=True,
            converted_data={"key": "value"},
            metadata={"conversion_type": "anthropic_to_litellm"}
        )
        
        assert result.success
        assert result.converted_data["key"] == "value"
        assert result.metadata["conversion_type"] == "anthropic_to_litellm"
    
    def test_failed_conversion(self):
        """Test failed conversion result."""
        result = ConversionResult(
            success=False,
            errors=["Invalid format"],
            warnings=["Data may be incomplete"]
        )
        
        assert not result.success
        assert result.converted_data is None
        assert "Invalid format" in result.errors
    
    def test_success_without_data_validation(self):
        """Test that success=True without converted_data raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ConversionResult(
                success=True,
                converted_data=None
            )
        
        assert "converted_data must be provided when success is True" in str(exc_info.value)


class TestToolValidationResult:
    """Test ToolValidationResult model."""
    
    def test_valid_tools(self):
        """Test validation result for valid tools."""
        result = ToolValidationResult(
            is_valid=True,
            orphaned_tools=[],
            missing_results=[],
            validation_errors=[],
            suggestions=[]
        )
        
        assert result.is_valid
        assert not result.has_orphaned_tools
        assert not result.has_missing_results
    
    def test_orphaned_tools(self):
        """Test validation result with orphaned tools."""
        result = ToolValidationResult(
            is_valid=False,
            orphaned_tools=["tool_123", "tool_456"],
            validation_errors=["Orphaned tools detected"]
        )
        
        assert not result.is_valid
        assert result.has_orphaned_tools
        assert len(result.orphaned_tools) == 2
        assert "tool_123" in result.orphaned_tools
    
    def test_missing_results(self):
        """Test validation result with missing tool results."""
        result = ToolValidationResult(
            is_valid=False,
            missing_results=["tool_789"],
            validation_errors=["Missing tool results"]
        )
        
        assert not result.is_valid
        assert result.has_missing_results
        assert "tool_789" in result.missing_results


class TestModelMappingResult:
    """Test ModelMappingResult model."""
    
    def test_big_model_mapping(self):
        """Test big model mapping."""
        result = ModelMappingResult(
            original_model="big",
            mapped_model="anthropic/claude-sonnet-4",
            mapping_applied=True,
            mapping_type="big"
        )
        
        assert result.original_model == "big"
        assert result.mapped_model == "anthropic/claude-sonnet-4"
        assert result.mapping_applied
        assert result.mapping_type == "big"
    
    def test_passthrough_mapping(self):
        """Test passthrough mapping."""
        result = ModelMappingResult(
            original_model="anthropic/claude-3-5-sonnet-20241022",
            mapped_model="anthropic/claude-3-5-sonnet-20241022",
            mapping_applied=False,
            mapping_type="passthrough"
        )
        
        assert result.original_model == result.mapped_model
        assert not result.mapping_applied
        assert result.mapping_type == "passthrough"
    
    def test_empty_model_validation(self):
        """Test that empty model names raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ModelMappingResult(
                original_model="",
                mapped_model="test",
                mapping_applied=False,
                mapping_type="passthrough"
            )
        
        assert "Model name cannot be empty" in str(exc_info.value)


class TestPerformanceMetrics:
    """Test PerformanceMetrics model."""
    
    def test_valid_metrics(self):
        """Test creating valid performance metrics."""
        metrics = PerformanceMetrics(
            request_count=100,
            average_response_time=1.5,
            error_rate=0.05,
            token_usage_stats={"input": 1000, "output": 500},
            model_usage_stats={"claude-3-5-sonnet": 80, "claude-3-haiku": 20}
        )
        
        assert metrics.request_count == 100
        assert metrics.average_response_time == 1.5
        assert metrics.error_rate == 0.05
        assert metrics.token_usage_stats["input"] == 1000
        assert metrics.model_usage_stats["claude-3-5-sonnet"] == 80
    
    def test_error_rate_bounds(self):
        """Test error rate validation bounds."""
        # Valid error rates
        metrics = PerformanceMetrics(error_rate=0.0)
        assert metrics.error_rate == 0.0
        
        metrics = PerformanceMetrics(error_rate=1.0)
        assert metrics.error_rate == 1.0
        
        # Invalid error rates
        with pytest.raises(ValidationError):
            PerformanceMetrics(error_rate=-0.1)
        
        with pytest.raises(ValidationError):
            PerformanceMetrics(error_rate=1.1)


class TestInstructorClient:
    """Test InstructorClient functionality."""
    
    @patch('src.utils.instructor_client.instructor')
    @patch('src.utils.instructor_client.OpenAI')
    def test_client_initialization(self, mock_openai, mock_instructor):
        """Test instructor client initialization."""
        mock_client = Mock()
        mock_instructor.from_openai.return_value = mock_client
        
        client = InstructorClient()
        
        # Verify OpenAI client was created with correct parameters
        mock_openai.assert_called_once()
        call_kwargs = mock_openai.call_args[1]
        assert "api_key" in call_kwargs
        assert call_kwargs["base_url"] == "https://openrouter.ai/api/v1"
        
        # Verify instructor was initialized
        mock_instructor.from_openai.assert_called_once()
    
    @patch('src.utils.instructor_client.instructor')
    @patch('src.utils.instructor_client.OpenAI')
    def test_structured_completion(self, mock_openai, mock_instructor):
        """Test structured completion creation."""
        mock_client = Mock()
        mock_response = StructuredResponse(content="Test response")
        mock_client.chat.completions.create.return_value = mock_response
        mock_instructor.from_openai.return_value = mock_client
        
        client = InstructorClient()
        
        messages = [{"role": "user", "content": "Test message"}]
        result = client.create_structured_completion(
            model="anthropic/claude-3.7-sonnet",
            messages=messages,
            response_model=StructuredResponse,
            max_tokens=1000,
            temperature=0.5
        )
        
        assert result == mock_response
        mock_client.chat.completions.create.assert_called_once_with(
            model="anthropic/claude-3.7-sonnet",
            messages=messages,
            response_model=StructuredResponse,
            max_tokens=1000,
            temperature=0.5
        )
    
    @patch('src.utils.instructor_client.instructor')
    @patch('src.utils.instructor_client.OpenAI')
    def test_structured_completion_error(self, mock_openai, mock_instructor):
        """Test structured completion error handling."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_instructor.from_openai.return_value = mock_client
        
        client = InstructorClient()
        
        with pytest.raises(Exception) as exc_info:
            client.create_structured_completion(
                model="test-model",
                messages=[],
                response_model=StructuredResponse
            )
        
        assert "API Error" in str(exc_info.value)