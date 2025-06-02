"""
Error logging utility for OpenRouter Anthropic Server.
Writes detailed error information to disk for debugging.
"""

import json
import traceback
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.core.logging_config import get_logger

logger = get_logger(__name__)

class ErrorLogger:
    """Handles comprehensive error logging to disk with full debug information."""
    
    def __init__(self, log_dir: str = "logs/errors"):
        """Initialize error logger with specified directory."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Thread pool for async file writes
        self._executor = ThreadPoolExecutor(max_workers=2)
        
        # Current log file based on date
        self._update_log_file()
    
    def _update_log_file(self):
        """Update the current log file based on date."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.current_log_file = self.log_dir / f"errors_{date_str}.jsonl"
    
    def log_error(
        self,
        error: Exception,
        correlation_id: str,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log an error with full debug information.
        
        Args:
            error: The exception that occurred
            correlation_id: Request correlation ID
            request_data: Full request data (will be sanitized)
            response_data: Full response data if available
            context: Additional context information
            
        Returns:
            The error log entry that was written
        """
        # Update log file in case date has changed
        self._update_log_file()
        
        # Build comprehensive error log entry
        error_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "correlation_id": correlation_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "request": self._sanitize_request(request_data) if request_data else None,
            "response": self._sanitize_response(response_data) if response_data else None,
            "context": context or {},
            "environment": {
                "service": "openrouter-anthropic-server",
                "version": "2.0",
                "pid": os.getpid()
            }
        }
        
        # Write to disk asynchronously
        asyncio.create_task(self._write_error_async(error_entry))
        
        return error_entry
    
    def _sanitize_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize request data to remove sensitive information."""
        sanitized = request_data.copy()
        
        # Sanitize API keys
        if "api_key" in sanitized:
            sanitized["api_key"] = self._mask_api_key(sanitized["api_key"])
        
        # Sanitize headers
        if "headers" in sanitized and isinstance(sanitized["headers"], dict):
            headers = sanitized["headers"].copy()
            for key in ["Authorization", "X-Api-Key", "api-key"]:
                if key in headers:
                    headers[key] = self._mask_api_key(headers[key])
            sanitized["headers"] = headers
        
        # Limit message size to prevent huge logs
        if "messages" in sanitized and isinstance(sanitized["messages"], list):
            messages = []
            for msg in sanitized["messages"][:10]:  # Limit to first 10 messages
                if isinstance(msg, dict):
                    msg_copy = msg.copy()
                    if "content" in msg_copy and isinstance(msg_copy["content"], str):
                        # Truncate very long content
                        if len(msg_copy["content"]) > 1000:
                            msg_copy["content"] = msg_copy["content"][:1000] + "... [truncated]"
                    messages.append(msg_copy)
            if len(sanitized["messages"]) > 10:
                messages.append({"note": f"... and {len(sanitized['messages']) - 10} more messages"})
            sanitized["messages"] = messages
        
        return sanitized
    
    def _sanitize_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize response data."""
        if isinstance(response_data, dict):
            sanitized = response_data.copy()
            
            # Limit response body size
            if "body" in sanitized and isinstance(sanitized["body"], str):
                if len(sanitized["body"]) > 5000:
                    sanitized["body"] = sanitized["body"][:5000] + "... [truncated]"
            
            return sanitized
        else:
            # If response is not a dict, convert to string and limit size
            response_str = str(response_data)
            if len(response_str) > 5000:
                response_str = response_str[:5000] + "... [truncated]"
            return {"raw_response": response_str}
    
    def _mask_api_key(self, api_key: str) -> str:
        """Mask API key for security."""
        if not api_key:
            return "None"
        if len(api_key) > 8:
            return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
        return "*" * len(api_key)
    
    async def _write_error_async(self, error_entry: Dict[str, Any]):
        """Write error entry to disk asynchronously."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self._executor,
            self._write_error_sync,
            error_entry
        )
    
    def _write_error_sync(self, error_entry: Dict[str, Any]):
        """Write error entry to disk synchronously."""
        try:
            # Write as JSON Lines format for easy parsing
            with open(self.current_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(error_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            # If we can't write to disk, use structured logging as fallback
            logger.error("Failed to write error log to disk",
                        error=str(e),
                        error_entry=error_entry,
                        log_file=str(self.current_log_file))
    
    def get_recent_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent errors from the log file."""
        if not self.current_log_file.exists():
            return []
        
        errors = []
        try:
            with open(self.current_log_file, "r", encoding="utf-8") as f:
                # Read lines in reverse order
                lines = f.readlines()
                for line in reversed(lines[-count:]):
                    if line.strip():
                        errors.append(json.loads(line))
            return errors
        except Exception:
            return []
    
    def cleanup_old_logs(self, days_to_keep: int = 7):
        """Clean up old error log files."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for log_file in self.log_dir.glob("errors_*.jsonl"):
            try:
                # Parse date from filename
                date_str = log_file.stem.replace("errors_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    log_file.unlink()
            except Exception:
                pass


# Global error logger instance - will be initialized in main.py with proper config
error_logger = None

def initialize_error_logger(log_dir: str = "logs/errors"):
    """Initialize the global error logger with proper configuration."""
    global error_logger
    error_logger = ErrorLogger(log_dir)

def get_error_logger() -> ErrorLogger:
    """Get the global error logger instance."""
    if error_logger is None:
        # Fallback to default if not initialized
        initialize_error_logger()
    return error_logger


def log_error(
    error: Exception,
    correlation_id: str,
    request_data: Optional[Dict[str, Any]] = None,
    response_data: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Log an error with full debug information.
    
    This is a convenience function that uses the global error logger.
    """
    return get_error_logger().log_error(
        error=error,
        correlation_id=correlation_id,
        request_data=request_data,
        response_data=response_data,
        context=context
    ) 