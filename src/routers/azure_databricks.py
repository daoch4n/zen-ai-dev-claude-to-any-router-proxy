"""
Azure Databricks Claude router.

This module provides FastAPI endpoints for Azure Databricks Claude integration,
acting as a transparent proxy between Claude Code and Azure Databricks endpoints.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
import json
import asyncio

from src.services.azure_databricks_client import AzureDatabricksClaudeClient, get_databricks_client, get_endpoint_for_model
from src.converters.azure_databricks_converter import AzureDatabricksConverter
from src.models.anthropic import MessagesRequest, MessagesResponse
from src.core.logging_config import get_logger
from src.utils.config import config
from src.utils.errors import ConfigurationError

router = APIRouter(prefix="/v1/databricks", tags=["Azure Databricks"])
logger = get_logger(__name__)

# Initialize converter (always available)
converter = AzureDatabricksConverter()


def get_databricks_dependency():
    """
    Dependency to check if Azure Databricks is enabled and configured.
    
    Raises:
        HTTPException: If Azure Databricks is not properly configured
    """
    if not config.is_azure_databricks_backend():
        raise HTTPException(
            status_code=503,
            detail="Azure Databricks integration is not enabled. Set PROXY_BACKEND=AZURE_DATABRICKS in environment."
        )
    
    if not config.databricks_host or not config.databricks_token:
        raise HTTPException(
            status_code=503,
            detail="Azure Databricks host and token must be configured. Set DATABRICKS_HOST and DATABRICKS_TOKEN in environment."
        )


@router.post("/messages", response_model=MessagesResponse)
async def create_message(
    request: MessagesRequest,
    _: None = Depends(get_databricks_dependency)
) -> MessagesResponse:
    """
    Create a message using Azure Databricks Claude.
    
    Accepts Anthropic format requests, routes to Azure Databricks Claude endpoints,
    and returns Anthropic format responses for full Claude Code compatibility.
    
    Args:
        request: Message request in Anthropic format
        
    Returns:
        Message response in Anthropic format
        
    Raises:
        HTTPException: For various error conditions
    """
    logger.info("Azure Databricks message request received",
               model=request.model,
               message_count=len(request.messages),
               max_tokens=request.max_tokens,
               temperature=request.temperature)
    
    try:
        # Validate the request format
        request_dict = request.dict()
        if not converter.validate_anthropic_request(request_dict):
            raise HTTPException(
                status_code=400,
                detail="Invalid Anthropic request format"
            )
        
        # Convert request to Azure Databricks format
        databricks_request = converter.convert_request_to_databricks(request_dict)
        
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
            anthropic_response = converter.convert_response_to_anthropic(databricks_response)
            
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


@router.post("/messages/claude-sonnet-4", response_model=MessagesResponse)
async def create_message_sonnet_4(
    request: MessagesRequest,
    _: None = Depends(get_databricks_dependency)
) -> MessagesResponse:
    """
    Create message using Claude Sonnet 4 specifically.
    
    This endpoint forces the use of the Claude Sonnet 4 endpoint regardless
    of the model specified in the request.
    """
    # Override the model to ensure Claude Sonnet 4 is used
    request.model = "claude-sonnet-4"
    
    logger.info("Forcing Claude Sonnet 4 endpoint", original_model=request.model)
    
    return await create_message(request)


@router.post("/messages/claude-3-7-sonnet", response_model=MessagesResponse)
async def create_message_3_7_sonnet(
    request: MessagesRequest,
    _: None = Depends(get_databricks_dependency)
) -> MessagesResponse:
    """
    Create message using Claude 3.7 Sonnet specifically.
    
    This endpoint forces the use of the Claude 3.7 Sonnet endpoint regardless
    of the model specified in the request.
    """
    # Override the model to ensure Claude 3.7 Sonnet is used
    request.model = "claude-3.7-sonnet"
    
    logger.info("Forcing Claude 3.7 Sonnet endpoint", original_model=request.model)
    
    return await create_message(request)


@router.post("/messages/stream")
async def create_message_stream(
    request: MessagesRequest,
    _: None = Depends(get_databricks_dependency)
):
    """
    Create streaming message using Azure Databricks Claude.
    
    Returns Server-Sent Events stream compatible with Anthropic streaming format.
    """
    logger.info("Azure Databricks streaming request received",
               model=request.model,
               message_count=len(request.messages))
    
    async def generate_stream():
        """Generate streaming response in Anthropic format."""
        try:
            # Validate and convert request
            request_dict = request.dict()
            if not converter.validate_anthropic_request(request_dict):
                error_response = {
                    "error": {
                        "type": "invalid_request_error",
                        "message": "Invalid Anthropic request format"
                    }
                }
                yield f"data: {json.dumps(error_response)}\n\n"
                return
            
            # Convert request for streaming
            databricks_request = converter.convert_request_to_databricks(request_dict)
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
                    anthropic_chunk = converter.convert_stream_chunk(chunk)
                    
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


@router.get("/health")
async def health_check():
    """
    Basic health check for Azure Databricks integration.
    
    Returns:
        Dict containing health status
    """
    if not config.is_azure_databricks_backend():
        return {
            "status": "disabled",
            "message": "Azure Databricks integration is not enabled",
            "timestamp": logger._get_timestamp() if hasattr(logger, '_get_timestamp') else None
        }
    
    if not config.databricks_host or not config.databricks_token:
        return {
            "status": "misconfigured",
            "message": "Azure Databricks host and/or token not configured",
            "timestamp": logger._get_timestamp() if hasattr(logger, '_get_timestamp') else None
        }
    
    try:
        # Test basic connectivity
        async with get_databricks_client() as client:
            # Quick test of both endpoints
            sonnet_4_health = await client.health_check(config.databricks_claude_sonnet_4_endpoint)
            sonnet_37_health = await client.health_check(config.databricks_claude_3_7_sonnet_endpoint)
            
            overall_status = "healthy" if (
                sonnet_4_health["status"] == "healthy" and 
                sonnet_37_health["status"] == "healthy"
            ) else "unhealthy"
            
            return {
                "status": overall_status,
                "endpoints": {
                    "claude-sonnet-4": sonnet_4_health,
                    "claude-3-7-sonnet": sonnet_37_health
                },
                "workspace": config.databricks_host,
                "timestamp": logger._get_timestamp() if hasattr(logger, '_get_timestamp') else None
            }
        
    except Exception as e:
        logger.error("Azure Databricks health check failed", 
                    error=str(e),
                    error_type=type(e).__name__)
        
        return {
            "status": "unhealthy",
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": logger._get_timestamp() if hasattr(logger, '_get_timestamp') else None
        }


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check for Azure Databricks integration.
    
    Performs comprehensive testing of both Claude endpoints with timing information.
    """
    if not config.is_azure_databricks_backend():
        return {
            "status": "disabled",
            "message": "Azure Databricks integration is not enabled"
        }
    
    import time
    from datetime import datetime
    
    start_time = time.time()
    results = {
        "overall_status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "configuration": {
            "enabled": config.is_azure_databricks_backend(),
            "host": config.databricks_host,
            "has_token": bool(config.databricks_token),
            "timeout": config.databricks_timeout,
            "max_retries": config.databricks_max_retries
        },
        "endpoints": {},
        "total_check_time_ms": 0
    }
    
    # Test both endpoints
    endpoint_configs = {
        "claude-sonnet-4": config.databricks_claude_sonnet_4_endpoint,
        "claude-3-7-sonnet": config.databricks_claude_3_7_sonnet_endpoint
    }
    
    try:
        async with get_databricks_client() as client:
            for name, endpoint in endpoint_configs.items():
                endpoint_start = time.time()
                
                try:
                    health_result = await client.health_check(endpoint)
                    health_result["check_time_ms"] = round((time.time() - endpoint_start) * 1000, 2)
                    results["endpoints"][name] = health_result
                    
                    if health_result["status"] != "healthy":
                        results["overall_status"] = "unhealthy"
                        
                except Exception as e:
                    results["endpoints"][name] = {
                        "status": "unhealthy",
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "check_time_ms": round((time.time() - endpoint_start) * 1000, 2)
                    }
                    results["overall_status"] = "unhealthy"
            
    except Exception as e:
        results["overall_status"] = "unhealthy"
        results["error"] = str(e)
        results["error_type"] = type(e).__name__
    
    results["total_check_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    return results


@router.get("/config")
async def get_configuration():
    """
    Get current Azure Databricks configuration (excluding sensitive data).
    
    Returns:
        Dict containing configuration information
    """
    databricks_config = config.get_databricks_config()
    
    # Remove sensitive information
    safe_config = {
        "enabled": databricks_config["enabled"],
        "host": databricks_config["host"],
        "has_token": bool(databricks_config["token"]),
        "timeout": databricks_config["timeout"],
        "max_retries": databricks_config["max_retries"],
        "endpoints": databricks_config["endpoints"]
    }
    
    return {
        "azure_databricks": safe_config,
        "model_mapping": config.get_databricks_model_mapping()
    }


@router.get("/models")
async def list_available_models():
    """
    List available Azure Databricks Claude models.
    
    Returns:
        Dict containing available models and their endpoints
    """
    return {
        "available_models": [
            {
                "id": "claude-sonnet-4",
                "endpoint": config.databricks_claude_sonnet_4_endpoint,
                "description": "Claude Sonnet 4 - Most capable model for complex tasks"
            },
            {
                "id": "claude-3.7-sonnet", 
                "endpoint": config.databricks_claude_3_7_sonnet_endpoint,
                "description": "Claude 3.7 Sonnet - Fast and capable model for most tasks"
            }
        ],
        "model_mapping": config.get_databricks_model_mapping(),
        "default_model": "claude-3.7-sonnet"
    } 