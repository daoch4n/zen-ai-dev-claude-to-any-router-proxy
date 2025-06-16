"""
Health router for OpenRouter Anthropic Server.
Handles health check and status endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import time
from datetime import datetime
import os
import sys

from src.core.logging_config import get_logger
from src.utils.config import config
from src.services.http_client import HTTPClientService

logger = get_logger(__name__)
from src.services.validation import MessageValidationService
from src.services.conversion import ModelMappingService
from src.services.tool_execution import ToolExecutionService
from src.services.openrouter_direct_client import OpenRouterDirectClient

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
            "timestamp": datetime.now().isoformat(),
            "service": "OpenRouter Anthropic Server",
            "version": "2.0.0"
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
    Detailed health check with LiteLLM integration.
    """
    try:
        start_time = time.time()
        
        # Basic system info
        health_info = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "OpenRouter Anthropic Server",
            "version": "2.0.0",
            "environment": config.environment,
            "checks": {}
        }
        
        # System checks
        health_info["checks"]["system"] = {
            "python_version": sys.version,
            "platform": sys.platform,
            "memory_usage": _get_memory_usage(),
            "uptime": time.time() - start_time
        }
        
        # Configuration checks
        health_info["checks"]["configuration"] = {
            "litellm_config": config.get_litellm_config(),
            "cache_config": config.get_cache_config(),
            "health_config": config.get_health_config(),
            "bypass_config": config.get_bypass_config()
        }
        
        # LiteLLM health checks
        if config.health_check_enabled:
            http_client = HTTPClientService()
            litellm_health = await http_client.get_litellm_health_status()
            health_info["checks"]["litellm"] = litellm_health
            
            # Model connectivity checks
            if config.model_health_checks:
                model_checks = {}
                for model_name, model_id in [("big_model", config.big_model), ("small_model", config.small_model)]:
                    try:
                        model_health = await http_client.test_model_connection(model_id)
                        model_checks[model_name] = model_health
                    except Exception as e:
                        model_checks[model_name] = {
                            "status": "error",
                            "error": str(e)
                        }
                
                health_info["checks"]["models"] = model_checks
        
        # Bypass health checks
        if config.is_openrouter_backend() and config.health_check_enabled:
            try:
                openrouter_client = OpenRouterDirectClient()
                bypass_health = await openrouter_client.get_health_status()
                health_info["checks"]["bypass"] = bypass_health
                await openrouter_client.close()
            except Exception as e:
                health_info["checks"]["bypass"] = {
                    "status": "error",
                    "error": str(e)
                }
        elif config.is_openrouter_backend():
            health_info["checks"]["bypass"] = {
                "status": "enabled_but_not_tested",
                "message": "Bypass enabled but health checks disabled"
            }
        
        # Budget and cost tracking status
        if config.budget_tracking_enabled:
            health_info["checks"]["budget"] = config.get_budget_config()
        
        # Determine overall status
        failed_checks = []
        for check_name, check_result in health_info["checks"].items():
            if isinstance(check_result, dict):
                if check_result.get("status") == "unhealthy" or check_result.get("status") == "error":
                    failed_checks.append(check_name)
                elif "status" in check_result and check_result["status"] not in ["healthy", "connected"]:
                    failed_checks.append(check_name)
        
        if failed_checks:
            health_info["status"] = "degraded"
            health_info["failed_checks"] = failed_checks
        
        processing_time = time.time() - start_time
        health_info["response_time_ms"] = round(processing_time * 1000, 2)
        
        return health_info
        
    except Exception as e:
        logger.error("❌ Detailed health check failed",
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
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
                "bypass_health": "/health/bypass",
                "docs": "/docs"
            },
            "features": [
                "Enhanced validation with Pydantic models",
                "Structured logging and debugging",
                "Instructor integration for AI-powered operations",
                "Comprehensive error handling",
                "Model mapping and aliasing",
                "Streaming support",
                "Token counting",
                f"LiteLLM bypass mode ({'enabled' if config.is_openrouter_backend() else 'disabled'})"
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
        # Initialize tool execution service to get metrics
        tool_execution_service = ToolExecutionService()
        
        try:
            metrics = tool_execution_service.get_metrics()
        except Exception as metrics_error:
            # If get_metrics doesn't exist, create basic metrics
            metrics = {
                'status': 'service_available',
                'message': 'Tool execution service initialized but metrics not available',
                'error': str(metrics_error)
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


@router.post("/health/test_connection")
async def test_model_connection(
    model: str = Query(..., description="Model to test"),
    provider: Optional[str] = Query(None, description="Provider to test")
):
    """Test connection to a specific model (similar to LiteLLM's test_connection endpoint)."""
    try:
        http_client = HTTPClientService()
        result = await http_client.test_model_connection(model, provider)
        
        if result["status"] == "unhealthy":
            raise HTTPException(
                status_code=503,
                detail=result
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Model connection test failed", model=model, provider=provider, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "model": model,
                "provider": provider,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/health/litellm")
async def litellm_health():
    """LiteLLM-specific health endpoint."""
    try:
        http_client = HTTPClientService()
        health_status = await http_client.get_litellm_health_status()
        
        return health_status
        
    except Exception as e:
        logger.error("LiteLLM health check failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/health/cache")
async def cache_health():
    """Cache health check endpoint."""
    try:
        cache_config = config.get_cache_config()
        
        if not cache_config["enabled"]:
            return {
                "status": "disabled",
                "message": "Caching is not enabled"
            }
        
        # Test cache connectivity if Redis
        if cache_config["type"] == "redis":
            try:
                import redis
                if cache_config.get("url"):
                    r = redis.from_url(cache_config["url"])
                else:
                    r = redis.Redis(
                        host=cache_config["host"],
                        port=cache_config["port"],
                        password=cache_config.get("password")
                    )
                
                # Test connection
                r.ping()
                
                return {
                    "status": "healthy",
                    "type": "redis",
                    "config": {
                        "host": cache_config["host"],
                        "port": cache_config["port"],
                        "ttl": cache_config.get("ttl")
                    }
                }
                
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "type": "redis",
                    "error": str(e)
                }
        else:
            return {
                "status": "healthy",
                "type": "local",
                "ttl": cache_config.get("ttl")
            }
            
    except Exception as e:
        logger.error("Cache health check failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error": str(e)
            }
        )


@router.get("/health/reasoning")
async def reasoning_capabilities():
    """Check reasoning capabilities for available models."""
    try:
        http_client = HTTPClientService()
        
        # Test common reasoning-capable models
        test_models = [
            "anthropic/claude-3-7-sonnet-20250219",
            "deepseek/deepseek-chat",
            "openrouter/deepseek/deepseek-r1",
            "openrouter/anthropic/claude-3-7-sonnet-20250219"
        ]
        
        reasoning_support = {}
        for model in test_models:
            try:
                result = await http_client.check_reasoning_support(model)
                reasoning_support[model] = result
            except Exception as e:
                reasoning_support[model] = {
                    "model": model,
                    "supports_reasoning": False,
                    "error": str(e)
                }
        
        # Overall reasoning status
        has_reasoning_models = any(
            support.get("supports_reasoning", False) 
            for support in reasoning_support.values()
        )
        
        return {
            "status": "healthy" if has_reasoning_models else "limited",
            "timestamp": datetime.now().isoformat(),
            "service": "LiteLLM Reasoning",
            "reasoning_available": has_reasoning_models,
            "models": reasoning_support,
            "total_models_tested": len(test_models),
            "reasoning_capable_count": sum(
                1 for support in reasoning_support.values() 
                if support.get("supports_reasoning", False)
            )
        }
        
    except Exception as e:
        logger.error("Reasoning capabilities check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail={"error": "Reasoning capabilities check failed", "message": str(e)}
        )


@router.get("/health/mcp")
async def mcp_health():
    """Check MCP (Model Context Protocol) health and capabilities."""
    try:
        from ..services.mcp_service import MCPService
        
        mcp_service = MCPService()
        
        # Get MCP status
        mcp_status = await mcp_service.is_mcp_enabled()
        
        # Get server and tool counts
        servers_result = await mcp_service.list_mcp_servers()
        tools_result = await mcp_service.list_mcp_tools()
        
        return {
            "status": "healthy" if mcp_status["enabled"] else "disabled",
            "timestamp": datetime.now().isoformat(),
            "service": "MCP (Model Context Protocol)",
            "enabled": mcp_status["enabled"],
            "python_compatible": mcp_status["python_version_compatible"],
            "servers": {
                "total": servers_result.get("total_count", 0),
                "active": len([s for s in servers_result.get("servers", []) if s.get("status") == "active"])
            },
            "tools": {
                "total": tools_result.get("total_count", 0),
                "available": len(tools_result.get("tools", []))
            }
        }
        
    except Exception as e:
        logger.error("MCP health check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail={"error": "MCP health check failed", "message": str(e)}
        )


@router.get("/health/bypass")
async def bypass_health():
    """Check LiteLLM bypass health and capabilities."""
    try:
        # Check if bypass is enabled
        if not config.is_openrouter_backend():
            return {
                "status": "disabled",
                "message": "LiteLLM bypass is not enabled",
                "enabled": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # Initialize OpenRouter direct client
        openrouter_client = OpenRouterDirectClient()
        
        try:
            # Get bypass health status
            health_status = await openrouter_client.get_health_status()
            
            # Test connection with configured models
            connection_tests = {}
            bypass_config = config.get_bypass_config()
            test_models = [
                config.big_model,
                config.small_model,
                bypass_config["model_format"]
            ]
            
            # Remove duplicates
            test_models = list(set(test_models))
            
            for model in test_models:
                try:
                    # Convert to bypass format
                    bypass_model = config.get_bypass_model_mapping().get(model, model)
                    test_result = await openrouter_client.test_connection(bypass_model)
                    connection_tests[model] = test_result
                except Exception as e:
                    connection_tests[model] = {
                        "status": "error",
                        "error": str(e),
                        "model": model
                    }
            
            # Overall bypass status
            all_healthy = all(
                test.get("status") == "healthy" 
                for test in connection_tests.values()
            )
            
            result = {
                "status": "healthy" if all_healthy else "degraded",
                "timestamp": datetime.now().isoformat(),
                "service": "LiteLLM Bypass",
                "enabled": True,
                "configuration": bypass_config,
                "client_health": health_status,
                "model_tests": connection_tests,
                "total_models_tested": len(test_models),
                "healthy_models": sum(
                    1 for test in connection_tests.values()
                    if test.get("status") == "healthy"
                )
            }
            
            return result
            
        finally:
            await openrouter_client.close()
            
    except Exception as e:
        logger.error("Bypass health check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "error": str(e),
                "message": "Bypass health check failed",
                "timestamp": datetime.now().isoformat()
            }
        )


def _get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage information."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
            "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
            "percent": round(process.memory_percent(), 2)
        }
    except ImportError:
        return {"error": "psutil not available"}
    except Exception as e:
        return {"error": str(e)}