"""
Debug endpoints for OpenRouter Anthropic Server.
Provides access to error logs and debugging information with enhanced error tracking.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..utils.error_logger import error_logger
from ..utils.enhanced_error_handler import get_enhanced_error_handler, SERVER_INSTANCE_ID
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


# Enhanced Error Handling Endpoints

@router.get("/server/instance")
async def get_server_instance_info() -> Dict[str, Any]:
    """
    Get current server instance information.
    
    Useful for identifying which server instance logs belong to.
    """
    try:
        handler = get_enhanced_error_handler()
        return {
            "server_instance_id": SERVER_INSTANCE_ID,
            "start_time": handler.SERVER_START_TIME.isoformat(),
            "instance_log_dir": str(handler.instance_log_dir),
            "error_blocks_count": len(handler.error_blocks),
            "log_files": {
                "errors": str(handler.error_log_file),
                "debug": str(handler.debug_log_file),
                "hash_registry": str(handler.hash_registry_file)
            }
        }
    except Exception as e:
        logger.error("Failed to get server instance info", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to get server instance info", "message": str(e)}
        )


@router.get("/errors/enhanced/recent")
async def get_recent_enhanced_errors(
    count: int = Query(10, description="Number of recent errors to retrieve", ge=1, le=100)
) -> Dict[str, Any]:
    """
    Get recent enhanced errors with full debugging information.
    
    Provides detailed error information including hash, location, and context.
    """
    try:
        handler = get_enhanced_error_handler()
        errors = handler.list_recent_errors(count)
        
        return {
            "server_instance_id": SERVER_INSTANCE_ID,
            "count": len(errors),
            "log_file": str(handler.error_log_file),
            "errors": errors
        }
    except Exception as e:
        logger.error("Failed to retrieve enhanced error logs", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to retrieve enhanced error logs", "message": str(e)}
        )


@router.get("/errors/hash/{block_hash}")
async def get_error_by_hash(block_hash: str) -> Dict[str, Any]:
    """
    Get error block information by hash.
    
    Use this to locate the exact code block that generated an error.
    """
    try:
        handler = get_enhanced_error_handler()
        block_info = handler.get_error_by_hash(block_hash)
        
        if not block_info:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Error block not found",
                    "message": f"No error block found with hash: {block_hash}"
                }
            )
        
        return {
            "block_hash": block_hash,
            "function_name": block_info.function_name,
            "file_path": block_info.file_path,
            "line_number": block_info.line_number,
            "code_context": block_info.code_context,
            "created_at": block_info.created_at.isoformat(),
            "server_instance_id": SERVER_INSTANCE_ID
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get error by hash", block_hash=block_hash, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to get error by hash", "message": str(e)}
        )


@router.get("/errors/registry")
async def get_error_block_registry() -> Dict[str, Any]:
    """
    Get the complete error block registry.
    
    Shows all registered error handling blocks with their hashes and locations.
    """
    try:
        handler = get_enhanced_error_handler()
        
        registry = {}
        for block_hash, block_info in handler.error_blocks.items():
            registry[block_hash] = {
                "function_name": block_info.function_name,
                "file_path": block_info.file_path,
                "line_number": block_info.line_number,
                "code_context": block_info.code_context,
                "created_at": block_info.created_at.isoformat()
            }
        
        return {
            "server_instance_id": SERVER_INSTANCE_ID,
            "total_blocks": len(registry),
            "registry_file": str(handler.hash_registry_file),
            "error_blocks": registry
        }
    except Exception as e:
        logger.error("Failed to get error block registry", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to get error block registry", "message": str(e)}
        )


@router.get("/errors/enhanced/stats")
async def get_enhanced_error_stats() -> Dict[str, Any]:
    """
    Get enhanced error statistics with hash-based tracking.
    
    Provides detailed statistics about errors grouped by hash, location, and type.
    """
    try:
        handler = get_enhanced_error_handler()
        errors = handler.list_recent_errors(100)
        
        # Calculate enhanced statistics
        error_by_hash = {}
        error_by_function = {}
        error_by_file = {}
        error_types = {}
        
        for error in errors:
            # Count by error block hash
            block_hash = error.get("error_block_hash", "unknown")
            error_by_hash[block_hash] = error_by_hash.get(block_hash, 0) + 1
            
            # Count by function
            function_name = error.get("code_location", {}).get("function_name", "unknown")
            error_by_function[function_name] = error_by_function.get(function_name, 0) + 1
            
            # Count by file
            file_path = error.get("code_location", {}).get("file_path", "unknown")
            if file_path != "unknown":
                file_name = file_path.split("/")[-1]  # Get just the filename
                error_by_file[file_name] = error_by_file.get(file_name, 0) + 1
            
            # Count by error type
            error_type = error.get("error_details", {}).get("type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "server_instance_id": SERVER_INSTANCE_ID,
            "total_errors": len(errors),
            "time_range": {
                "oldest": errors[-1]["timestamp"] if errors else None,
                "newest": errors[0]["timestamp"] if errors else None
            },
            "error_by_hash": error_by_hash,
            "error_by_function": error_by_function,
            "error_by_file": error_by_file,
            "error_types": error_types,
            "total_error_blocks": len(handler.error_blocks)
        }
    except Exception as e:
        logger.error("Failed to calculate enhanced error statistics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to calculate enhanced error statistics", "message": str(e)}
        )


@router.get("/errors/search")
async def search_errors(
    error_type: Optional[str] = Query(None, description="Filter by error type"),
    function_name: Optional[str] = Query(None, description="Filter by function name"),
    file_name: Optional[str] = Query(None, description="Filter by file name"),
    block_hash: Optional[str] = Query(None, description="Filter by error block hash"),
    limit: int = Query(50, description="Maximum number of results", ge=1, le=200)
) -> Dict[str, Any]:
    """
    Search through errors with various filters.
    
    Allows filtering by error type, function name, file name, or block hash.
    """
    try:
        handler = get_enhanced_error_handler()
        all_errors = handler.list_recent_errors(1000)  # Get more errors for searching
        
        filtered_errors = []
        for error in all_errors:
            # Apply filters
            if error_type and error.get("error_details", {}).get("type") != error_type:
                continue
            
            if function_name and error.get("code_location", {}).get("function_name") != function_name:
                continue
            
            if file_name:
                file_path = error.get("code_location", {}).get("file_path", "")
                if file_name not in file_path:
                    continue
            
            if block_hash and error.get("error_block_hash") != block_hash:
                continue
            
            filtered_errors.append(error)
            
            # Limit results
            if len(filtered_errors) >= limit:
                break
        
        return {
            "server_instance_id": SERVER_INSTANCE_ID,
            "total_found": len(filtered_errors),
            "filters_applied": {
                "error_type": error_type,
                "function_name": function_name,
                "file_name": file_name,
                "block_hash": block_hash
            },
            "errors": filtered_errors
        }
    except Exception as e:
        logger.error("Failed to search errors", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to search errors", "message": str(e)}
        ) 