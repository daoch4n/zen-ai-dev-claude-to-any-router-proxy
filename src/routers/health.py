"""
Health router for OpenRouter Anthropic Server.
Handles health check and status endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time
from datetime import datetime

from src.core.logging_config import get_logger
from src.utils.config import config

logger = get_logger(__name__)
from src.services.validation import MessageValidationService
from src.services.conversion import ModelMappingService
from src.services.tool_execution import ToolExecutionService

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns server status and basic configuration info.
    """
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "service": "OpenRouter Anthropic Server"
        }
    except Exception as e:
        logger.error("❌ Health check failed",
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Health check failed", "message": str(e)}
        )


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with service validation.
    Tests core services and dependencies.
    """
    try:
        start_time = time.time()
        
        # Test service initialization
        services_status = {}
        
        # Test message validation service
        try:
            validator = MessageValidationService()
            services_status["message_validator"] = "healthy"
        except Exception as e:
            services_status["message_validator"] = f"error: {str(e)}"
        
        # Test model mapping service
        try:
            mapper = ModelMappingService()
            test_mapping = mapper.map_model("test")
            services_status["model_mapper"] = "healthy"
        except Exception as e:
            services_status["model_mapper"] = f"error: {str(e)}"
        
        # Test configuration
        config_status = {}
        try:
            config_status["api_key_configured"] = bool(config.openrouter_api_key)
            config_status["big_model"] = config.big_model
            config_status["small_model"] = config.small_model
            config_status["environment"] = config.environment
        except Exception as e:
            config_status["error"] = str(e)
        
        # Test LiteLLM availability
        litellm_status = {}
        try:
            import litellm
            litellm_status["available"] = True
            litellm_status["version"] = getattr(litellm, '__version__', 'unknown')
        except Exception as e:
            litellm_status["available"] = False
            litellm_status["error"] = str(e)
        
        processing_time = time.time() - start_time
        
        # Determine overall health
        all_services_healthy = all(
            status == "healthy" for status in services_status.values()
        )
        
        overall_status = "healthy" if all_services_healthy else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "service": "OpenRouter Anthropic Server",
            "processing_time_ms": round(processing_time * 1000, 2),
            "services": services_status,
            "configuration": config_status,
            "dependencies": {
                "litellm": litellm_status
            }
        }
        
    except Exception as e:
        logger.error("❌ Detailed health check failed",
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Detailed health check failed", "message": str(e)}
        )


@router.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint with basic server information.
    """
    try:
        return {
            "service": "OpenRouter Anthropic Server",
            "version": "2.0.0",
            "description": "Modular OpenRouter to Anthropic API proxy server",
            "endpoints": {
                "messages": "/v1/messages",
                "count_tokens": "/v1/messages/count_tokens",
                "health": "/health",
                "detailed_health": "/health/detailed",
                "docs": "/docs"
            },
            "features": [
                "Enhanced validation with Pydantic models",
                "Structured logging and debugging",
                "Instructor integration for AI-powered operations",
                "Comprehensive error handling",
                "Model mapping and aliasing",
                "Streaming support",
                "Token counting"
            ]
        }
    except Exception as e:
        logger.error("❌ Root endpoint failed",
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Root endpoint failed", "message": str(e)}
        )


@router.get("/status")
async def status() -> Dict[str, Any]:
    """
    Status endpoint with runtime metrics.
    """
    try:
        import psutil
        import os
        
        # Get process info
        process = psutil.Process(os.getpid())
        
        return {
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": time.time() - process.create_time(),
            "memory_usage": {
                "rss_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                "vms_mb": round(process.memory_info().vms / 1024 / 1024, 2),
                "percent": round(process.memory_percent(), 2)
            },
            "cpu_usage": {
                "percent": round(process.cpu_percent(), 2),
                "num_threads": process.num_threads()
            },
            "environment": {
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                "platform": os.name,
                "pid": os.getpid()
            }
        }
        
    except ImportError:
        # psutil not available, return basic status
        return {
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Basic status (psutil not available for detailed metrics)"
        }
    except Exception as e:
        logger.error("❌ Status endpoint failed",
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Status endpoint failed", "message": str(e)}
        )


@router.get("/tool-metrics")
async def get_tool_metrics() -> Dict[str, Any]:
    """
    Get tool execution metrics.
    
    Returns tool execution statistics including:
    - Total executions
    - Success/failure rates
    - Average execution times
    - Tool usage counts
    - Error breakdown
    """
    try:
        # Get tool execution service instance
        from ..routers.messages import tool_executor
        
        if tool_executor:
            metrics = tool_executor.get_metrics()
        else:
            metrics = {
                'status': 'no_tool_executor',
                'message': 'Tool execution service not initialized'
            }
        
        return {
            "status": "healthy",
            "message": "Tool metrics retrieved",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "tool_execution": {
                "metrics": metrics,
                "enabled": getattr(config, 'tool_execution_enabled', True),
                "max_concurrent_tools": getattr(config, 'tool_max_concurrent_tools', 5),
                "execution_timeout": getattr(config, 'tool_execution_timeout', 30),
                "rate_limit_window": getattr(config, 'tool_rate_limit_window', 60),
                "rate_limit_max_requests": getattr(config, 'tool_rate_limit_max_requests', 100)
            }
        }
    except Exception as e:
        logger.error("Error retrieving tool metrics",
                    error_type=type(e).__name__,
                    error_message=str(e))
        return {
            "status": "error",
            "message": f"Error retrieving tool metrics: {str(e)}",
            "version": "2.0.0", 
            "timestamp": datetime.utcnow().isoformat()
        }