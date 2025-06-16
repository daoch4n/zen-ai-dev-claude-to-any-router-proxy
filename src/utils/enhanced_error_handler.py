"""
Enhanced Exception Handling System for OpenRouter Anthropic Server.

Provides comprehensive error handling with hash-based error tracking, detailed 
error information, line number tracking, and server-instance-specific logging.
"""

import hashlib
import inspect
import traceback
import uuid
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union, Callable, Type, List
from functools import wraps
from contextlib import contextmanager
import asyncio
import json

from src.core.logging_config import get_logger
from src.utils.error_logger import get_error_logger

logger = get_logger(__name__)

# Global server instance ID for this server run
SERVER_INSTANCE_ID = str(uuid.uuid4())[:8]
SERVER_START_TIME = datetime.now(timezone.utc)

class ErrorBlockInfo:
    """Information about an error handling block."""
    
    def __init__(
        self,
        function_name: str,
        file_path: str,
        line_number: int,
        code_context: str,
        block_hash: str
    ):
        self.function_name = function_name
        self.file_path = file_path
        self.line_number = line_number
        self.code_context = code_context
        self.block_hash = block_hash
        self.created_at = datetime.now(timezone.utc)

class EnhancedErrorHandler:
    """Enhanced error handler with hash-based tracking and detailed logging."""
    
    def __init__(self, debug_logs_dir: str = "logs/debug"):
        """Initialize enhanced error handler."""
        self.debug_logs_dir = Path(debug_logs_dir)
        self.debug_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create server-instance-specific log directory
        self.instance_log_dir = self.debug_logs_dir / f"server_{SERVER_INSTANCE_ID}"
        self.instance_log_dir.mkdir(exist_ok=True)
        
        # Error block registry for hash-based lookup
        self.error_blocks: Dict[str, ErrorBlockInfo] = {}
        
        # Initialize instance-specific log files
        self._init_instance_logs()
        
        logger.info("Enhanced error handler initialized", 
                   server_instance_id=SERVER_INSTANCE_ID,
                   instance_log_dir=str(self.instance_log_dir))
    
    def _init_instance_logs(self):
        """Initialize server-instance-specific log files."""
        timestamp = SERVER_START_TIME.strftime("%Y%m%d_%H%M%S")
        
        # Create instance-specific log files
        self.error_log_file = self.instance_log_dir / f"errors_{timestamp}.jsonl"
        self.debug_log_file = self.instance_log_dir / f"debug_{timestamp}.jsonl"
        self.hash_registry_file = self.instance_log_dir / f"error_blocks_{timestamp}.json"
        
        # Write initial server info
        self._write_server_startup_info()
    
    def _write_server_startup_info(self):
        """Write server startup information to logs."""
        startup_info = {
            "event_type": "server_startup",
            "timestamp": SERVER_START_TIME.isoformat(),
            "server_instance_id": SERVER_INSTANCE_ID,
            "pid": os.getpid(),
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "command_line": " ".join(sys.argv)
        }
        
        self._write_to_log(self.debug_log_file, startup_info)
        logger.info("Server startup logged", startup_info=startup_info)
    
    def _write_to_log(self, log_file: Path, data: Dict[str, Any]):
        """Write data to a log file in JSON Lines format."""
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False, default=str) + "\n")
        except Exception as e:
            logger.error("Failed to write to log file", 
                        log_file=str(log_file), error=str(e))
    
    def generate_error_block_hash(
        self, 
        function_name: str, 
        file_path: str, 
        line_number: int
    ) -> str:
        """Generate a unique hash for an error handling block."""
        # Create a unique identifier for this error block
        block_identifier = f"{file_path}:{function_name}:{line_number}"
        
        # Generate SHA-256 hash (first 12 characters for readability)
        hash_object = hashlib.sha256(block_identifier.encode())
        return hash_object.hexdigest()[:12]
    
    def register_error_block(
        self,
        function_name: str,
        file_path: str,
        line_number: int,
        code_context: str = ""
    ) -> str:
        """Register an error block and return its hash."""
        block_hash = self.generate_error_block_hash(function_name, file_path, line_number)
        
        error_block = ErrorBlockInfo(
            function_name=function_name,
            file_path=file_path,
            line_number=line_number,
            code_context=code_context,
            block_hash=block_hash
        )
        
        self.error_blocks[block_hash] = error_block
        
        # Update hash registry file
        self._update_hash_registry()
        
        return block_hash
    
    def _update_hash_registry(self):
        """Update the hash registry file with current error blocks."""
        registry_data = {
            "server_instance_id": SERVER_INSTANCE_ID,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "error_blocks": {
                hash_key: {
                    "function_name": block.function_name,
                    "file_path": block.file_path,
                    "line_number": block.line_number,
                    "code_context": block.code_context,
                    "created_at": block.created_at.isoformat()
                }
                for hash_key, block in self.error_blocks.items()
            }
        }
        
        try:
            with open(self.hash_registry_file, "w", encoding="utf-8") as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Failed to update hash registry", error=str(e))
    
    def log_enhanced_error(
        self,
        error: Exception,
        block_hash: str,
        context: Dict[str, Any] = None,
        request_data: Dict[str, Any] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """Log an enhanced error with full debugging information."""
        # Get error block info
        block_info = self.error_blocks.get(block_hash)
        
        # Generate correlation ID if not provided
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Extract detailed error information
        error_info = self._extract_error_info(error)
        
        # Build comprehensive error entry
        error_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server_instance_id": SERVER_INSTANCE_ID,
            "correlation_id": correlation_id,
            "error_block_hash": block_hash,
            "error_details": {
                "type": error_info["type"],
                "message": error_info["message"],
                "args": error_info["args"],
                "stack_trace": error_info["stack_trace"],
                "stack_frames": error_info["stack_frames"]
            },
            "code_location": {
                "function_name": block_info.function_name if block_info else "unknown",
                "file_path": block_info.file_path if block_info else "unknown",
                "line_number": block_info.line_number if block_info else 0,
                "code_context": block_info.code_context if block_info else ""
            },
            "execution_context": {
                "thread_id": f"{os.getpid()}",
                "process_id": os.getpid(),
                "context_data": context or {}
            },
            "request_data": self._sanitize_request_data(request_data) if request_data else None,
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd()
            }
        }
        
        # Write to instance-specific error log
        self._write_to_log(self.error_log_file, error_entry)
        
        # Also use the existing error logger for compatibility
        try:
            get_error_logger().log_error(
                error=error,
                correlation_id=correlation_id,
                request_data=request_data,
                context={
                    "error_block_hash": block_hash,
                    "server_instance_id": SERVER_INSTANCE_ID,
                    **(context or {})
                }
            )
        except Exception as e:
            logger.warning("Failed to use existing error logger", error=str(e))
        
        return error_entry
    
    def _extract_error_info(self, error: Exception) -> Dict[str, Any]:
        """Extract detailed information from an exception."""
        return {
            "type": type(error).__name__,
            "message": str(error),
            "args": error.args,
            "stack_trace": traceback.format_exc(),
            "stack_frames": self._extract_stack_frames()
        }
    
    def _extract_stack_frames(self) -> List[Dict[str, Any]]:
        """Extract detailed stack frame information."""
        frames = []
        
        for frame_info in traceback.extract_tb(sys.exc_info()[2]):
            frames.append({
                "filename": frame_info.filename,
                "line_number": frame_info.lineno,
                "function_name": frame_info.name,
                "code_line": frame_info.line
            })
        
        return frames
    
    def _sanitize_request_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize request data to remove sensitive information."""
        if not request_data:
            return None
        
        sanitized = request_data.copy()
        
        # Remove or mask sensitive fields
        sensitive_fields = ["api_key", "authorization", "password", "secret", "token"]
        
        for field in sensitive_fields:
            if field in sanitized:
                if isinstance(sanitized[field], str) and len(sanitized[field]) > 8:
                    sanitized[field] = sanitized[field][:4] + "*" * 8 + sanitized[field][-4:]
                else:
                    sanitized[field] = "***MASKED***"
        
        return sanitized
    
    def get_error_by_hash(self, block_hash: str) -> Optional[ErrorBlockInfo]:
        """Get error block information by hash."""
        return self.error_blocks.get(block_hash)
    
    def list_recent_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors from the instance log."""
        try:
            if not self.error_log_file.exists():
                return []
            
            errors = []
            with open(self.error_log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines[-count:]):
                    if line.strip():
                        errors.append(json.loads(line))
            
            return errors
        except Exception as e:
            logger.error("Failed to read recent errors", error=str(e))
            return []


# Global enhanced error handler instance
enhanced_error_handler = None

def initialize_enhanced_error_handler(debug_logs_dir: str = "logs/debug"):
    """Initialize the global enhanced error handler."""
    global enhanced_error_handler
    enhanced_error_handler = EnhancedErrorHandler(debug_logs_dir)
    return enhanced_error_handler

def get_enhanced_error_handler() -> EnhancedErrorHandler:
    """Get the global enhanced error handler instance."""
    if enhanced_error_handler is None:
        initialize_enhanced_error_handler()
    return enhanced_error_handler


def enhanced_exception_handler(
    context: Dict[str, Any] = None,
    log_request_data: bool = True,
    reraise: bool = True
):
    """
    Decorator for enhanced exception handling with hash-based tracking.
    
    Args:
        context: Additional context information to log
        log_request_data: Whether to log request data if available
        reraise: Whether to reraise the exception after logging
    """
    def decorator(func: Callable) -> Callable:
        # Get function information for hash generation
        file_path = inspect.getfile(func)
        function_name = func.__name__
        line_number = inspect.getsourcelines(func)[1]
        
        # Generate and register error block hash
        handler = get_enhanced_error_handler()
        block_hash = handler.register_error_block(
            function_name=function_name,
            file_path=file_path,
            line_number=line_number,
            code_context=f"Function: {function_name}"
        )
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Extract request data if available
                request_data = None
                if log_request_data and args:
                    # Try to find request-like objects in arguments
                    for arg in args:
                        if hasattr(arg, 'dict') or isinstance(arg, dict):
                            request_data = arg.dict() if hasattr(arg, 'dict') else arg
                            break
                
                # Log enhanced error
                handler.log_enhanced_error(
                    error=e,
                    block_hash=block_hash,
                    context=context,
                    request_data=request_data
                )
                
                if reraise:
                    raise
                return None
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Extract request data if available
                request_data = None
                if log_request_data and args:
                    # Try to find request-like objects in arguments
                    for arg in args:
                        if hasattr(arg, 'dict') or isinstance(arg, dict):
                            request_data = arg.dict() if hasattr(arg, 'dict') else arg
                            break
                
                # Log enhanced error
                handler.log_enhanced_error(
                    error=e,
                    block_hash=block_hash,
                    context=context,
                    request_data=request_data
                )
                
                if reraise:
                    raise
                return None
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@contextmanager
def enhanced_error_context(
    context_name: str,
    context_data: Dict[str, Any] = None,
    log_request_data: bool = True
):
    """
    Context manager for enhanced exception handling.
    
    Args:
        context_name: Name of the context (used for hash generation)
        context_data: Additional context information
        log_request_data: Whether to log request data if available
    """
    # Get caller information for hash generation
    frame = inspect.currentframe().f_back
    file_path = frame.f_code.co_filename
    function_name = frame.f_code.co_name
    line_number = frame.f_lineno
    
    # Generate and register error block hash
    handler = get_enhanced_error_handler()
    block_hash = handler.register_error_block(
        function_name=function_name,
        file_path=file_path,
        line_number=line_number,
        code_context=f"Context: {context_name}"
    )
    
    try:
        yield block_hash
    except Exception as e:
        # Log enhanced error
        handler.log_enhanced_error(
            error=e,
            block_hash=block_hash,
            context={
                "context_name": context_name,
                **(context_data or {})
            }
        )
        raise


def log_error_with_hash(
    error: Exception,
    block_hash: str,
    context: Dict[str, Any] = None,
    request_data: Dict[str, Any] = None,
    correlation_id: str = None
) -> str:
    """
    Log an error with a specific block hash.
    
    Args:
        error: The exception to log
        block_hash: The error block hash
        context: Additional context information
        request_data: Request data to log
        correlation_id: Correlation ID for tracking
    
    Returns:
        The correlation ID used for logging
    """
    handler = get_enhanced_error_handler()
    error_entry = handler.log_enhanced_error(
        error=error,
        block_hash=block_hash,
        context=context,
        request_data=request_data,
        correlation_id=correlation_id
    )
    return error_entry["correlation_id"] 