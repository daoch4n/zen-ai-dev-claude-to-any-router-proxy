"""
Messages router for OpenRouter Anthropic Server.
Handles /v1/messages endpoint using workflow orchestration.

This router has been refactored to use clean workflow orchestration,
replacing the monolithic 390+ line functions with simple orchestrator calls.
"""

from fastapi import APIRouter, Request, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Dict, Any, Optional
import json
import uuid
import time
from datetime import datetime

from src.models.anthropic import MessagesRequest, MessagesResponse
from src.models.base import Usage
from src.models.instructor import StructuredResponse, ConversionResult
from src.services.validation import MessageValidationService, ConversationFlowValidationService
from src.services.conversion import AnthropicToLiteLLMConverter, LiteLLMResponseToAnthropicConverter, ModelMappingService
from src.services.http_client import HTTPClientService
from src.services.tool_execution import ToolExecutionService, ToolUseDetector
from src.orchestrators.conversation_orchestrator import (
    process_message_request_orchestrated,
    process_message_stream_orchestrated
)
from src.services.context_manager import ContextManager
from src.core.logging_config import get_logger
from src.utils.config import config

# Create router instance
router = APIRouter(prefix="/v1", tags=["messages"])

# Initialize services
context_manager = ContextManager()
logger = get_logger(__name__)

# Helper functions for backward compatibility
async def validate_request_data(request: MessagesRequest) -> MessagesRequest:
    """Validate incoming request data using our validation services."""
    try:
        # Use the validation service
        validation_service = MessageValidationService()
        validated_request = validation_service.validate_messages_request(request)
        
        logger.info("Request validation completed successfully")
        return validated_request
        
    except Exception as e:
        logger.error("Request validation failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={"error": "Validation failed", "message": str(e)}
        )


async def process_model_mapping(request: MessagesRequest) -> MessagesRequest:
    """Process model mapping for the request."""
    try:
        # Use the model mapping service
        model_mapping_service = ModelMappingService()
        mapped_request = model_mapping_service.process_model_mapping(request)
        
        logger.info("Model mapping completed", 
                   original_model=request.model, 
                   final_model=mapped_request.model)
        return mapped_request
        
    except Exception as e:
        logger.error("Model mapping failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=400,
            detail={"error": "Model mapping failed", "message": str(e)}
        )


async def convert_to_litellm(request: MessagesRequest) -> Dict[str, Any]:
    """Convert Anthropic request to LiteLLM format."""
    try:
        converter = AnthropicToLiteLLMConverter()
        litellm_request = converter.convert(request)
        
        logger.info("LiteLLM conversion completed")
        return litellm_request
        
    except Exception as e:
        logger.error("LiteLLM conversion failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "Request conversion failed", "message": str(e)}
        )


async def call_litellm_api(litellm_request: Dict[str, Any]) -> Any:
    """Call LiteLLM API using the dedicated HTTP client service."""
    try:
        http_client = HTTPClientService()
        response = await http_client.call_litellm(litellm_request)
        
        logger.info("LiteLLM API call completed")
        return response
        
    except Exception as e:
        logger.error("LiteLLM API call failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "API call failed", "message": str(e)}
        )


async def convert_response_to_anthropic(litellm_response: Any, original_request: MessagesRequest) -> MessagesResponse:
    """Convert LiteLLM response back to Anthropic format using dedicated converter service."""
    try:
        # Use the dedicated response converter service
        response_converter = LiteLLMResponseToAnthropicConverter()
        conversion_result = response_converter.convert(litellm_response, original_request=original_request)
        
        if not conversion_result.success:
            error_msg = "; ".join(conversion_result.errors) if conversion_result.errors else "Unknown conversion error"
            raise ValueError(f"Response conversion failed: {error_msg}")
        
        # Convert dictionary back to MessagesResponse object
        response = MessagesResponse(**conversion_result.converted_data)
        
        logger.info("Response converted to Anthropic format using dedicated service")
        return response
            
    except Exception as e:
        logger.error("Response conversion failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "Response conversion failed", "message": str(e)}
        )


@router.post("/messages")
async def create_message(
    request: MessagesRequest,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_correlation_id: Optional[str] = Header(None)
) -> MessagesResponse:
    """
    Create a message completion using Anthropic's format via OpenRouter.
    
    Now using workflow orchestration to replace the monolithic function.
    This provides clean, maintainable, and testable message processing.
    """
    return await process_message_request_orchestrated(
        request=request,
        x_api_key=x_api_key,
        authorization=authorization,
        x_correlation_id=x_correlation_id
    )


@router.post("/messages/stream")
async def create_message_stream(
    request: MessagesRequest,
    raw_request: Request
) -> StreamingResponse:
    """
    Create a streaming message completion using Anthropic's format via OpenRouter.
    
    Now using workflow orchestration to replace the monolithic function.
    This eliminates the 284+ lines of code duplication between endpoints.
    """
    # Extract headers from the raw request
    x_api_key = raw_request.headers.get("x-api-key")
    authorization = raw_request.headers.get("authorization")
    x_correlation_id = raw_request.headers.get("x-correlation-id")
    
    return await process_message_stream_orchestrated(
        request=request,
        x_api_key=x_api_key,
        authorization=authorization,
        x_correlation_id=x_correlation_id
    )