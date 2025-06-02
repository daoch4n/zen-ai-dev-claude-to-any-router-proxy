"""Instructor client setup and configuration."""

import instructor
from openai import OpenAI
from typing import Optional, Type, TypeVar, Any, Dict, List
from pydantic import BaseModel
from .config import config
from src.core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar('T', bound=BaseModel)

class InstructorClient:
    """Wrapper for Instructor-enhanced OpenAI client."""
    
    def __init__(self):
        """Initialize the Instructor client."""
        # Configure for OpenRouter
        self.client = instructor.from_openai(
            OpenAI(
                api_key=config.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        )
        logger.info("🎯 Instructor client initialized for structured outputs")
    
    def create_structured_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        response_model: Type[T],
        max_tokens: int = 4096,
        temperature: float = 0.1,
        **kwargs
    ) -> T:
        """Create a structured completion using Instructor.
        
        Args:
            model: The model to use for completion
            messages: List of messages in OpenAI format
            response_model: Pydantic model class for structured output
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters for the completion
            
        Returns:
            Structured response matching the response_model
            
        Raises:
            Exception: If structured completion fails
        """
        try:
            logger.info(f"🎯 Creating structured completion with {model}")
            logger.debug(f"Response model: {response_model.__name__}")
            logger.debug(f"Messages count: {len(messages)}")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                response_model=response_model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            logger.info(f"✅ Structured completion created: {type(response).__name__}")
            logger.debug(f"Response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Structured completion failed: {e}")
            raise
    
    def validate_with_instructor(
        self,
        data: Dict[str, Any],
        validation_model: Type[T],
        model: str = "anthropic/claude-3-5-sonnet-20241022"
    ) -> T:
        """Validate data using Instructor with a validation prompt.
        
        Args:
            data: Data to validate
            validation_model: Pydantic model for validation
            model: Model to use for validation
            
        Returns:
            Validated and potentially corrected data
        """
        try:
            validation_prompt = f"""
            Please validate and correct the following data according to the specified schema.
            If the data is valid, return it as-is. If there are issues, fix them and return the corrected version.
            
            Data to validate:
            {data}
            
            Return the validated/corrected data in the proper format.
            """
            
            messages = [
                {
                    "role": "user",
                    "content": validation_prompt
                }
            ]
            
            return self.create_structured_completion(
                model=model,
                messages=messages,
                response_model=validation_model,
                temperature=0.0  # Use deterministic output for validation
            )
            
        except Exception as e:
            logger.error(f"❌ Instructor validation failed: {e}")
            raise
    
    def extract_structured_data(
        self,
        text: str,
        extraction_model: Type[T],
        model: str = "anthropic/claude-3-5-sonnet-20241022"
    ) -> T:
        """Extract structured data from unstructured text using Instructor.
        
        Args:
            text: Unstructured text to extract data from
            extraction_model: Pydantic model for extracted data
            model: Model to use for extraction
            
        Returns:
            Extracted structured data
        """
        try:
            extraction_prompt = f"""
            Please extract structured information from the following text according to the specified schema.
            
            Text to analyze:
            {text}
            
            Extract all relevant information and return it in the proper structured format.
            """
            
            messages = [
                {
                    "role": "user",
                    "content": extraction_prompt
                }
            ]
            
            return self.create_structured_completion(
                model=model,
                messages=messages,
                response_model=extraction_model,
                temperature=0.1
            )
            
        except Exception as e:
            logger.error(f"❌ Instructor extraction failed: {e}")
            raise

# Global instructor client instance
instructor_client = InstructorClient()