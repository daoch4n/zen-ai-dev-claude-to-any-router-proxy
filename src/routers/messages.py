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
    process_message_stream_orchestrated,
    process_bypass_request_orchestrated,
    process_bypass_stream_orchestrated,
    process_litellm_messages_orchestrated,
    process_litellm_messages_stream_orchestrated
)
from src.services.azure_databricks_client import get_databricks_client, get_endpoint_for_model
from src.converters.azure_databricks_converter import AzureDatabricksConverter
from src.flows.conversion.batch_processing_flow import BatchProcessingFlow
from src.tasks.conversion.prompt_caching_tasks import (
    get_prompt_cache_stats,
    clear_prompt_cache,
    cleanup_expired_cache_entries
)
from src.services.context_manager import ContextManager
from src.core.logging_config import get_logger
from src.utils.config import config

# Create router instance
router = APIRouter(prefix="/v1", tags=["messages"])

# Initialize services
context_manager = ContextManager()
logger = get_logger(__name__)

# Initialize Azure Databricks converter
databricks_converter = AzureDatabricksConverter()


# Azure Databricks wrapper functions
async def _route_to_azure_databricks(request: MessagesRequest) -> MessagesResponse:
    """
    Route message request to Azure Databricks Claude.
    
    Handles Azure Databricks configuration validation and message routing.
    """
    # Check Azure Databricks configuration
    if not config.is_azure_databricks_backend():
        raise HTTPException(
            status_code=503,
            detail="Azure Databricks backend not configured"
        )
    
    if not config.databricks_host or not config.databricks_token:
        raise HTTPException(
            status_code=503,
            detail="Azure Databricks host and token must be configured. Set DATABRICKS_HOST and DATABRICKS_TOKEN in environment."
        )
    
    logger.info("Azure Databricks message request received",
               model=request.model,
               message_count=len(request.messages),
               max_tokens=request.max_tokens,
               temperature=request.temperature)
    
    try:
        # Validate the request format
        request_dict = request.dict()
        if not databricks_converter.validate_anthropic_request(request_dict):
            raise HTTPException(
                status_code=400,
                detail="Invalid Anthropic request format"
            )
        
        # Convert request to Azure Databricks format
        databricks_request = databricks_converter.convert_request_to_databricks(request_dict)
        
        # Determine the appropriate Azure Databricks endpoint
        endpoint_name = get_endpoint_for_model(request.model)
        
        logger.info("Routing to Azure Databricks endpoint",
                   requested_model=request.model,
                   endpoint=endpoint_name)
        
        # Use the client context manager for proper resource cleanup
        async with get_databricks_client() as client:
            # Call Azure Databricks
            databricks_response = await client.create_message(
                endpoint_name=endpoint_name,
                **databricks_request
            )
            
            # Convert response back to Anthropic format
            anthropic_response = databricks_converter.convert_response_to_anthropic(databricks_response)
            
            logger.info("Azure Databricks message created successfully",
                       endpoint=endpoint_name,
                       input_tokens=anthropic_response.get("usage", {}).get("input_tokens", 0),
                       output_tokens=anthropic_response.get("usage", {}).get("output_tokens", 0),
                       model_returned=anthropic_response.get("model", "unknown"))
            
            return MessagesResponse(**anthropic_response)
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error("Azure Databricks message creation failed", 
                    error=str(e), 
                    error_type=type(e).__name__,
                    model=request.model)
        raise HTTPException(
            status_code=500,
            detail=f"Azure Databricks request failed: {str(e)}"
        )


async def _route_to_azure_databricks_stream(request: MessagesRequest) -> StreamingResponse:
    """
    Route streaming message request to Azure Databricks Claude.
    
    Handles Azure Databricks configuration validation and streaming message routing.
    """
    # Check Azure Databricks configuration
    if not config.is_azure_databricks_backend():
        raise HTTPException(
            status_code=503,
            detail="Azure Databricks backend not configured"
        )
    
    if not config.databricks_host or not config.databricks_token:
        raise HTTPException(
            status_code=503,
            detail="Azure Databricks host and token must be configured. Set DATABRICKS_HOST and DATABRICKS_TOKEN in environment."
        )
    
    logger.info("Azure Databricks streaming request received",
               model=request.model,
               message_count=len(request.messages))
    
    async def generate_stream():
        """Generate streaming response in Anthropic format."""
        try:
            # Validate and convert request
            request_dict = request.dict()
            if not databricks_converter.validate_anthropic_request(request_dict):
                error_response = {
                    "error": {
                        "type": "invalid_request_error",
                        "message": "Invalid Anthropic request format"
                    }
                }
                yield f"data: {json.dumps(error_response)}\n\n"
                return
            
            # Convert request for streaming
            databricks_request = databricks_converter.convert_request_to_databricks(request_dict)
            endpoint_name = get_endpoint_for_model(request.model)
            
            logger.info("Starting Azure Databricks streaming",
                       endpoint=endpoint_name,
                       model=request.model)
            
            # Stream from Azure Databricks
            async with get_databricks_client() as client:
                async for chunk in client.create_streaming_message(
                    endpoint_name=endpoint_name,
                    **databricks_request
                ):
                    # Convert chunk to Anthropic format
                    anthropic_chunk = databricks_converter.convert_stream_chunk(chunk)
                    
                    # Send as Server-Sent Event
                    yield f"data: {json.dumps(anthropic_chunk)}\n\n"
                
                # Send completion marker
                yield "data: [DONE]\n\n"
                
        except Exception as e:
            logger.error("Azure Databricks streaming failed", 
                        error=str(e),
                        error_type=type(e).__name__)
            
            error_response = {
                "error": {
                    "type": "api_error",
                    "message": str(e)
                }
            }
            yield f"data: {json.dumps(error_response)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )

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
    Create a message completion using Anthropic's format.
    
    Routes to different backends based on PROXY_BACKEND configuration:
    - AZURE_DATABRICKS: Routes to Azure Databricks Claude endpoints
    - OPENROUTER: Direct OpenRouter communication (bypass LiteLLM)
    - LITELLM_OPENROUTER: LiteLLM + OpenRouter (legacy mode)
    - LITELLM_MESSAGES: LiteLLM /v1/messages endpoint (native Anthropic format)
    """
    backend = config.get_active_backend()
    
    logger.info("Processing message request",
               model=request.model,
               backend=backend,
               correlation_id=x_correlation_id)
    
    if backend == "AZURE_DATABRICKS":
        logger.debug("Routing to Azure Databricks backend", 
                    model=request.model)
        
        # Route directly to Azure Databricks handler
        return await _route_to_azure_databricks(request)
        
    elif backend == "OPENROUTER":
        logger.debug("Using OpenRouter direct backend (bypass LiteLLM)", 
                    model=request.model)
        return await process_bypass_request_orchestrated(
            request=request,
            x_api_key=x_api_key,
            authorization=authorization,
            x_correlation_id=x_correlation_id
        )
        
    elif backend == "LITELLM_OPENROUTER":
        logger.debug("Using LiteLLM + OpenRouter backend", 
                   model=request.model)
        return await process_message_request_orchestrated(
            request=request,
            x_api_key=x_api_key,
            authorization=authorization,
            x_correlation_id=x_correlation_id
        )
        
    elif backend == "LITELLM_MESSAGES":
        logger.debug("Using LiteLLM /v1/messages backend (native Anthropic format)", 
                   model=request.model)
        return await process_litellm_messages_orchestrated(
            request=request,
            x_api_key=x_api_key,
            authorization=authorization,
            x_correlation_id=x_correlation_id
        )
        
    else:
        # This should never happen due to validation, but handle gracefully
        logger.error("Unknown proxy backend configuration", backend=backend)
        raise HTTPException(
            status_code=500,
            detail=f"Unknown proxy backend: {backend}"
        )


@router.post("/messages/stream")
async def create_message_stream(
    request: MessagesRequest,
    raw_request: Request
) -> StreamingResponse:
    """
    Create a streaming message completion using Anthropic's format.
    
    Routes to different backends based on PROXY_BACKEND configuration:
    - AZURE_DATABRICKS: Routes to Azure Databricks Claude streaming endpoints
    - OPENROUTER: Direct OpenRouter streaming (bypass LiteLLM)
    - LITELLM_OPENROUTER: LiteLLM + OpenRouter streaming (legacy mode)
    - LITELLM_MESSAGES: LiteLLM /v1/messages streaming (native Anthropic format)
    """
    # Extract headers from the raw request
    x_api_key = raw_request.headers.get("x-api-key")
    authorization = raw_request.headers.get("authorization")
    x_correlation_id = raw_request.headers.get("x-correlation-id")
    
    backend = config.get_active_backend()
    
    logger.info("Processing streaming message request",
               model=request.model,
               backend=backend,
               correlation_id=x_correlation_id)
    
    if backend == "AZURE_DATABRICKS":
        logger.debug("Routing to Azure Databricks streaming backend", 
                    model=request.model)
        
        # Route directly to Azure Databricks streaming handler
        return await _route_to_azure_databricks_stream(request)
        
    elif backend == "OPENROUTER":
        logger.debug("Using OpenRouter direct streaming backend (bypass LiteLLM)", 
                    model=request.model)
        return await process_bypass_stream_orchestrated(
            request=request,
            x_api_key=x_api_key,
            authorization=authorization,
            x_correlation_id=x_correlation_id
        )
        
    elif backend == "LITELLM_OPENROUTER":
        logger.debug("Using LiteLLM + OpenRouter streaming backend", 
                   model=request.model)
        return await process_message_stream_orchestrated(
            request=request,
            x_api_key=x_api_key,
            authorization=authorization,
            x_correlation_id=x_correlation_id
        )
        
    elif backend == "LITELLM_MESSAGES":
        logger.debug("Using LiteLLM /v1/messages streaming backend (native Anthropic format)", 
                   model=request.model)
        return await process_litellm_messages_stream_orchestrated(
            request=request,
            x_api_key=x_api_key,
            authorization=authorization,
            x_correlation_id=x_correlation_id
        )
        
    else:
        # This should never happen due to validation, but handle gracefully
        logger.error("Unknown proxy backend configuration for streaming", backend=backend)
        raise HTTPException(
            status_code=500,
            detail=f"Unknown proxy backend: {backend}"
        )


@router.post("/messages/batch")
async def process_message_batch(
    batch_request: Dict[str, Any],
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_correlation_id: Optional[str] = Header(None)
) -> JSONResponse:
    """
    Process multiple messages in a single batch request.
    
    This is an Anthropic Beta Feature that allows processing multiple messages
    efficiently with enhanced performance and proper error handling for partial failures.
    
    Args:
        batch_request: Dictionary containing batch of messages to process
        x_api_key: API key for authentication
        authorization: Alternative authorization header
        x_correlation_id: Request correlation ID for tracking
        
    Returns:
        JSONResponse with batch processing results
    """
    try:
        # Set up context for the batch request
        correlation_id = x_correlation_id or str(uuid.uuid4())
        start_time = time.time()
        
        with context_manager.request_context(
            correlation_id=correlation_id,
            user_agent="batch-processing",
            api_version="2023-06-01"
        ):
            logger.info("Starting batch processing request",
                       correlation_id=correlation_id,
                       batch_size=len(batch_request.get("messages", [])))
            
            # Initialize batch processing flow
            batch_flow = BatchProcessingFlow()
            
            # Process the batch
            result = batch_flow.convert(batch_request)
            
            processing_time = time.time() - start_time
            
            if result.success:
                logger.info("Batch processing completed successfully",
                           correlation_id=correlation_id,
                           processing_time=processing_time,
                           batch_id=result.converted_data.get("batch_id"),
                           success_rate=result.converted_data.get("success_rate"))
                
                return JSONResponse(
                    content=result.converted_data,
                    status_code=200,
                    headers={
                        "X-Correlation-ID": correlation_id,
                        "X-Processing-Time": str(processing_time),
                        "X-Batch-ID": result.converted_data.get("batch_id", ""),
                        "Content-Type": "application/json"
                    }
                )
            else:
                logger.error("Batch processing failed",
                           correlation_id=correlation_id,
                           errors=result.errors,
                           processing_time=processing_time)
                
                error_response = {
                    "error": {
                        "type": "batch_processing_error",
                        "message": "Batch processing failed",
                        "details": result.errors,
                        "correlation_id": correlation_id
                    }
                }
                
                return JSONResponse(
                    content=error_response,
                    status_code=400,
                    headers={
                        "X-Correlation-ID": correlation_id,
                        "X-Processing-Time": str(processing_time)
                    }
                )
            
    except Exception as e:
        logger.error("Batch processing endpoint error",
                    correlation_id=correlation_id if 'correlation_id' in locals() else "unknown",
                    error=str(e),
                    exc_info=True)
        
        error_response = {
            "error": {
                "type": "internal_error",
                "message": "Internal server error during batch processing",
                "details": [str(e)],
                "correlation_id": correlation_id if 'correlation_id' in locals() else None
            }
        }
        
        return JSONResponse(
            content=error_response,
            status_code=500,
            headers={
                "X-Correlation-ID": correlation_id if 'correlation_id' in locals() else str(uuid.uuid4())
            }
        )


@router.get("/messages/batch/{batch_id}/status")
async def get_batch_status(
    batch_id: str,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
) -> JSONResponse:
    """
    Get the status of a batch processing operation.
    
    Args:
        batch_id: ID of the batch to check status for
        x_api_key: API key for authentication
        authorization: Alternative authorization header
        
    Returns:
        JSONResponse with batch status information
    """
    try:
        logger.info("Batch status requested", batch_id=batch_id)
        
        # Initialize batch processing flow
        batch_flow = BatchProcessingFlow()
        
        # Get batch status
        status = batch_flow.get_batch_status(batch_id)
        
        if status:
            return JSONResponse(
                content=status,
                status_code=200
            )
        else:
            return JSONResponse(
                content={
                    "error": {
                        "type": "batch_not_found",
                        "message": f"Batch {batch_id} not found",
                        "batch_id": batch_id
                    }
                },
                status_code=404
            )
            
    except Exception as e:
        logger.error("Error getting batch status",
                    batch_id=batch_id,
                    error=str(e))
        
        return JSONResponse(
            content={
                "error": {
                    "type": "internal_error",
                    "message": "Failed to get batch status",
                    "details": [str(e)]
                }
            },
            status_code=500
        )


@router.get("/messages/cache/stats")
async def get_cache_stats(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
) -> JSONResponse:
    """
    Get prompt cache statistics and performance metrics.
    
    Args:
        x_api_key: API key for authentication
        authorization: Alternative authorization header
        
    Returns:
        JSONResponse with cache statistics
    """
    try:
        logger.info("Cache statistics requested")
        
        # Get cache statistics
        stats = get_prompt_cache_stats()
        
        return JSONResponse(
            content={
                "cache_stats": stats,
                "timestamp": datetime.now().isoformat()
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error("Error getting cache stats", error=str(e))
        
        return JSONResponse(
            content={
                "error": {
                    "type": "internal_error",
                    "message": "Failed to get cache statistics",
                    "details": [str(e)]
                }
            },
            status_code=500
        )


@router.post("/messages/cache/clear")
async def clear_cache(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
) -> JSONResponse:
    """
    Clear all cached prompt responses.
    
    Args:
        x_api_key: API key for authentication
        authorization: Alternative authorization header
        
    Returns:
        JSONResponse with clear operation result
    """
    try:
        logger.info("Cache clear requested")
        
        # Clear the cache
        result = clear_prompt_cache()
        
        if result.get("success", False):
            return JSONResponse(
                content=result,
                status_code=200
            )
        else:
            return JSONResponse(
                content={
                    "error": {
                        "type": "cache_clear_error",
                        "message": "Failed to clear cache",
                        "details": [result.get("error", "Unknown error")]
                    }
                },
                status_code=500
            )
        
    except Exception as e:
        logger.error("Error clearing cache", error=str(e))
        
        return JSONResponse(
            content={
                "error": {
                    "type": "internal_error",
                    "message": "Failed to clear cache",
                    "details": [str(e)]
                }
            },
            status_code=500
        )


@router.post("/messages/cache/cleanup")
async def cleanup_cache(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
) -> JSONResponse:
    """
    Clean up expired cache entries.
    
    Args:
        x_api_key: API key for authentication
        authorization: Alternative authorization header
        
    Returns:
        JSONResponse with cleanup operation result
    """
    try:
        logger.info("Cache cleanup requested")
        
        # Cleanup expired entries
        result = cleanup_expired_cache_entries()
        
        if result.get("success", False):
            return JSONResponse(
                content=result,
                status_code=200
            )
        else:
            return JSONResponse(
                content={
                    "error": {
                        "type": "cache_cleanup_error",
                        "message": "Failed to cleanup cache",
                        "details": [result.get("error", "Unknown error")]
                    }
                },
                status_code=500
            )
        
    except Exception as e:
        logger.error("Error cleaning up cache", error=str(e))
        
        return JSONResponse(
            content={
                "error": {
                    "type": "internal_error",
                    "message": "Failed to cleanup cache",
                    "details": [str(e)]
                }
            },
            status_code=500
        )