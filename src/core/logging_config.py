"""Unified Structlog logging configuration"""
import structlog
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from contextvars import ContextVar
from typing import Any, Dict


class SafeTimedRotatingFileHandler(TimedRotatingFileHandler):
    """File handler that gracefully handles I/O operations on closed files"""
    
    def emit(self, record):
        """Emit a record, handling closed file gracefully"""
        try:
            super().emit(record)
        except ValueError as e:
            # Handle "I/O operation on closed file" errors
            if "closed file" in str(e):
                # Silently ignore - this happens during application shutdown
                pass
            else:
                raise


class SafeStreamHandler(logging.StreamHandler):
    """Stream handler that gracefully handles I/O operations on closed streams"""
    
    def emit(self, record):
        """Emit a record, handling closed stream gracefully"""
        try:
            super().emit(record)
        except ValueError as e:
            # Handle "I/O operation on closed file" errors
            if "closed file" in str(e):
                # Silently ignore - this happens during application shutdown
                pass
            else:
                raise


class AioHttpCleanupFilter(logging.Filter):
    """Filter to suppress aiohttp cleanup messages during tests"""
    
    def filter(self, record):
        """Filter out aiohttp cleanup messages"""
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            # Suppress unclosed client session and connector warnings
            if ('Unclosed client session' in msg or
                'Unclosed connector' in msg or
                'connections:' in msg):
                return False
        return True

# Context variables for automatic propagation
request_context: ContextVar[Dict[str, Any]] = ContextVar('request_context', default={})
conversation_context: ContextVar[Dict[str, Any]] = ContextVar('conversation_context', default={})
tool_context: ContextVar[Dict[str, Any]] = ContextVar('tool_context', default={})

def configure_structlog(
    *,
    development: bool = True,
    log_level: str = "INFO",
    json_logs: bool = False,
    logs_dir: str = "logs",
    log_rotation: str = "daily",
    log_retention_days: int = 30,
    enable_file_logging: bool = None
) -> None:
    """Configure structlog for unified logging with file output"""
    
    # Auto-detect if we're in a test environment
    import sys
    import os
    import warnings
    is_testing = (
        'pytest' in sys.modules or
        'unittest' in sys.modules or
        any('test' in arg for arg in sys.argv) or
        os.environ.get('PYTEST_CURRENT_TEST') is not None or
        'PYTEST_RUNNING_SERVER' in os.environ
    )
    
    # Suppress aiohttp cleanup warnings during tests
    if is_testing:
        warnings.filterwarnings("ignore", category=ResourceWarning, module="aiohttp")
        # Also suppress asyncio unclosed client session warnings
        import asyncio
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    
    # Default file logging behavior: enabled except during testing
    if enable_file_logging is None:
        enable_file_logging = not is_testing
    
    # Create logs directory only if file logging is enabled
    if enable_file_logging:
        logs_path = Path(logs_dir)
        logs_path.mkdir(parents=True, exist_ok=True)
    
    # Processors for context enrichment
    processors = [
        add_request_context,
        add_conversation_context,
        add_tool_context,
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    # Output formatter based on environment
    if development and not json_logs:
        processors.append(
            structlog.dev.ConsoleRenderer(colors=True)
        )
    else:
        processors.append(
            structlog.processors.JSONRenderer(ensure_ascii=False)
        )
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging with file handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler (using safe version to handle closed streams during shutdown)
    console_handler = SafeStreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    if development and not json_logs:
        console_formatter = logging.Formatter("%(message)s")
    else:
        console_formatter = logging.Formatter("%(message)s")
    
    console_handler.setFormatter(console_formatter)
    
    # Add aiohttp cleanup filter during tests
    if is_testing:
        console_handler.addFilter(AioHttpCleanupFilter())
    
    root_logger.addHandler(console_handler)
    
    # Only add file handlers if file logging is enabled (not during tests)
    if enable_file_logging:
        # File handler with rotation
        log_file_path = logs_path / "application.log"
        
        # Configure rotation based on setting
        rotation_map = {
            "daily": "midnight",
            "hourly": "H",
            "weekly": "W0"  # Monday
        }
        when = rotation_map.get(log_rotation, "midnight")
        
        file_handler = SafeTimedRotatingFileHandler(
            filename=str(log_file_path),
            when=when,
            interval=1,
            backupCount=log_retention_days,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Use JSON format for file logs in production
        if json_logs or not development:
            file_formatter = logging.Formatter("%(message)s")
        else:
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Create separate error log file
        error_log_path = logs_path / "errors.log"
        error_handler = SafeTimedRotatingFileHandler(
            filename=str(error_log_path),
            when=when,
            interval=1,
            backupCount=log_retention_days,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)

def add_request_context(logger, method_name, event_dict):
    """Add request context to all log entries"""
    ctx = request_context.get({})
    if ctx:
        event_dict.setdefault("request", {}).update({
            "request_id": ctx.get("request_id"),
            "endpoint": ctx.get("endpoint"),
            "method": ctx.get("method"),
            "user_agent": ctx.get("user_agent"),
            "correlation_id": ctx.get("correlation_id")
        })
    return event_dict

def add_conversation_context(logger, method_name, event_dict):
    """Add conversation context to log entries"""
    ctx = conversation_context.get({})
    if ctx:
        event_dict.setdefault("conversation", {}).update({
            "conversation_id": ctx.get("conversation_id"),
            "model": ctx.get("model"),
            "message_count": ctx.get("message_count"),
            "current_step": ctx.get("current_step")
        })
    return event_dict

def add_tool_context(logger, method_name, event_dict):
    """Add tool execution context to log entries"""
    ctx = tool_context.get({})
    if ctx:
        event_dict.setdefault("tool", {}).update({
            "tool_name": ctx.get("tool_name"),
            "tool_call_id": ctx.get("tool_call_id"),
            "execution_step": ctx.get("execution_step"),
            "input_keys": ctx.get("input_keys")
        })
    return event_dict

def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structlog logger instance"""
    return structlog.get_logger(name)

def bind_request_context(
    request_id: str,
    endpoint: str,
    method: str = "POST",
    user_agent: str = None,
    correlation_id: str = None
) -> None:
    """Bind request context for automatic propagation"""
    request_context.set({
        "request_id": request_id,
        "endpoint": endpoint,
        "method": method,
        "user_agent": user_agent,
        "correlation_id": correlation_id or request_id,
        "timestamp": datetime.utcnow().isoformat()
    })

def bind_conversation_context(
    conversation_id: str,
    model: str,
    message_count: int = 0,
    current_step: str = "started"
) -> None:
    """Bind conversation context for automatic propagation"""
    conversation_context.set({
        "conversation_id": conversation_id,
        "model": model,
        "message_count": message_count,
        "current_step": current_step
    })

def bind_tool_context(
    tool_name: str,
    tool_call_id: str,
    execution_step: int = 1,
    input_keys: list = None
) -> None:
    """Bind tool execution context for automatic propagation"""
    tool_context.set({
        "tool_name": tool_name,
        "tool_call_id": tool_call_id,
        "execution_step": execution_step,
        "input_keys": input_keys or []
    })

def clear_context() -> None:
    """Clear all context variables"""
    request_context.set({})
    conversation_context.set({})
    tool_context.set({})

def setup_logging(
    log_level: str = "INFO",
    development: bool = True,
    json_logs: bool = False,
    logs_dir: str = "logs"
) -> None:
    """
    Backward compatibility wrapper for configure_structlog.
    Simplified interface for test initialization.
    """
    configure_structlog(
        development=development,
        log_level=log_level,
        json_logs=json_logs,
        logs_dir=logs_dir,
        enable_file_logging=False  # Disable file logging in tests by default
    )