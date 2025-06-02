"""Base service classes for the OpenRouter Anthropic Server."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel

from ..core.logging_config import get_logger
from ..utils.errors import OpenRouterProxyError
from ..models.instructor import ValidationResult, ConversionResult

T = TypeVar('T', bound=BaseModel)
U = TypeVar('U', bound=BaseModel)

class BaseService(ABC):
    """Base class for all services."""
    
    def __init__(self, name: str):
        """Initialize the base service."""
        self.name = name
        self.logger = get_logger(f"service.{name}")
        self.logger.info("Service initialized", service_name=name)
    
    def log_operation(self, operation: str, success: bool, **kwargs):
        """Log service operation."""
        if success:
            self.logger.info("Service operation completed",
                           service=self.name,
                           operation=operation,
                           success=success,
                           **kwargs)
        else:
            self.logger.error("Service operation failed",
                            service=self.name,
                            operation=operation,
                            success=success,
                            **kwargs)

class ValidationService(BaseService, Generic[T]):
    """Base validation service with structured results."""
    
    def __init__(self, name: str):
        """Initialize validation service."""
        super().__init__(name)
    
    @abstractmethod
    def validate(self, data: Any, **kwargs) -> ValidationResult:
        """Validate data and return structured result."""
        pass
    
    def create_validation_result(
        self,
        is_valid: bool,
        errors: List[str] = None,
        warnings: List[str] = None,
        suggestions: List[str] = None,
        corrected_data: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Create a structured validation result."""
        return ValidationResult(
            is_valid=is_valid,
            errors=errors or [],
            warnings=warnings or [],
            suggestions=suggestions or [],
            corrected_data=corrected_data
        )

class ConversionService(BaseService, Generic[T, U]):
    """Base conversion service with structured results."""
    
    def __init__(self, name: str):
        """Initialize conversion service."""
        super().__init__(name)
    
    @abstractmethod
    def convert(self, source: T, **kwargs) -> ConversionResult:
        """Convert data and return structured result."""
        pass
    
    def create_conversion_result(
        self,
        success: bool,
        converted_data: Optional[Dict[str, Any]] = None,
        errors: List[str] = None,
        warnings: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> ConversionResult:
        """Create a structured conversion result."""
        return ConversionResult(
            success=success,
            converted_data=converted_data,
            errors=errors or [],
            warnings=warnings or [],
            metadata=metadata or {}
        )

class InstructorService(BaseService):
    """Base service for Instructor-powered operations."""
    
    def __init__(self, name: str):
        """Initialize Instructor service."""
        super().__init__(name)
        from ..utils.instructor_client import instructor_client
        self.instructor_client = instructor_client
    
    def create_structured_output(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        response_model: type,
        **kwargs
    ) -> Any:
        """Create structured output using Instructor."""
        try:
            result = self.instructor_client.create_structured_completion(
                model=model,
                messages=messages,
                response_model=response_model,
                **kwargs
            )
            
            self.log_operation(
                "structured_output",
                True,
                model=model,
                response_model=response_model.__name__
            )
            
            return result
            
        except Exception as e:
            self.log_operation(
                "structured_output",
                False,
                model=model,
                response_model=response_model.__name__,
                error=str(e)
            )
            raise OpenRouterProxyError(f"Structured output creation failed: {e}")
    
    def validate_with_instructor(
        self,
        data: Dict[str, Any],
        validation_model: type,
        model: str = "anthropic/claude-3-5-sonnet-20241022"
    ) -> Any:
        """Validate data using Instructor."""
        try:
            result = self.instructor_client.validate_with_instructor(
                data=data,
                validation_model=validation_model,
                model=model
            )
            
            self.log_operation(
                "instructor_validation",
                True,
                model=model,
                validation_model=validation_model.__name__
            )
            
            return result
            
        except Exception as e:
            self.log_operation(
                "instructor_validation",
                False,
                model=model,
                validation_model=validation_model.__name__,
                error=str(e)
            )
            raise OpenRouterProxyError(f"Instructor validation failed: {e}")
    
    def extract_structured_data(
        self,
        text: str,
        extraction_model: type,
        model: str = "anthropic/claude-3-5-sonnet-20241022"
    ) -> Any:
        """Extract structured data using Instructor."""
        try:
            result = self.instructor_client.extract_structured_data(
                text=text,
                extraction_model=extraction_model,
                model=model
            )
            
            self.log_operation(
                "data_extraction",
                True,
                model=model,
                extraction_model=extraction_model.__name__,
                text_length=len(text)
            )
            
            return result
            
        except Exception as e:
            self.log_operation(
                "data_extraction",
                False,
                model=model,
                extraction_model=extraction_model.__name__,
                error=str(e)
            )
            raise OpenRouterProxyError(f"Data extraction failed: {e}")