"""
Debug endpoints for OpenRouter Anthropic Server.
Provides access to error logs and debugging information.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..utils.error_logger import error_logger
from src.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/errors/recent")
async def get_recent_errors(
    count: int = Query(10, description="Number of recent errors to retrieve", ge=1, le=100)
) -> Dict[str, Any]:
    """
    Get the most recent errors from the error log.
    
    This endpoint is useful for debugging issues without accessing log files directly.
    """
    try:
        errors = error_logger.get_recent_errors(count)
        
        return {
            "count": len(errors),
            "log_file": str(error_logger.current_log_file),
            "errors": errors
        }
    except Exception as e:
        logger.error("Failed to retrieve error logs",
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to retrieve error logs", "message": str(e)}
        )


@router.get("/errors/stats")
async def get_error_stats() -> Dict[str, Any]:
    """
    Get error statistics from recent logs.
    
    Provides a summary of error types and frequencies.
    """
    try:
        errors = error_logger.get_recent_errors(100)
        
        # Calculate statistics
        error_types = {}
        error_services = {}
        error_endpoints = {}
        
        for error in errors:
            # Count by error type
            error_type = error.get("error_type", "Unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Count by service
            context = error.get("context", {})
            service = context.get("service", "Unknown")
            error_services[service] = error_services.get(service, 0) + 1
            
            # Count by endpoint
            endpoint = context.get("endpoint", "Unknown")
            if endpoint != "Unknown":
                error_endpoints[endpoint] = error_endpoints.get(endpoint, 0) + 1
        
        return {
            "total_errors": len(errors),
            "time_range": {
                "oldest": errors[-1]["timestamp"] if errors else None,
                "newest": errors[0]["timestamp"] if errors else None
            },
            "error_types": error_types,
            "error_services": error_services,
            "error_endpoints": error_endpoints
        }
    except Exception as e:
        logger.error("Failed to calculate error statistics",
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to calculate error statistics", "message": str(e)}
        )


@router.get("/errors/{correlation_id}")
async def get_error_by_correlation_id(correlation_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific error by correlation ID.
    
    Useful for debugging specific failed requests.
    """
    try:
        # Search through recent errors for the correlation ID
        errors = error_logger.get_recent_errors(1000)  # Search through more errors
        
        for error in errors:
            if error.get("correlation_id") == correlation_id:
                return error
        
        return None
    except Exception as e:
        logger.error("Failed to retrieve error by correlation ID",
                    correlation_id=correlation_id,
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to retrieve error", "message": str(e)}
        )


@router.post("/errors/cleanup")
async def cleanup_old_error_logs(days_to_keep: int = Query(7, ge=1, le=30)) -> Dict[str, str]:
    """
    Clean up error log files older than specified days.
    
    Helps manage disk space by removing old error logs.
    """
    try:
        error_logger.cleanup_old_logs(days_to_keep)
        return {
            "status": "success",
            "message": f"Cleaned up error logs older than {days_to_keep} days"
        }
    except Exception as e:
        logger.error("Failed to cleanup error logs",
                    days_to_keep=days_to_keep,
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to cleanup error logs", "message": str(e)}
        ) 