"""
Main entry point for the OpenRouter Anthropic Server.

This is the enhanced main file that implements the complete modular architecture
with routers, middleware, and comprehensive error handling.
"""

import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

# Add the src directory to the Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn

# Import our modular components
from src.utils.config import config, ServerConfig
from src.core.logging_config import get_logger
from src.utils.errors import ConfigurationError

logger = get_logger(__name__)
from src.utils.debug import debug_logger

# Import unified logging system
from src.core.logging_config import configure_structlog, get_logger

# Import routers
from src.routers import messages_router, tokens_router, health_router, debug_router, mcp_router
from src.routers.claude_code_health import router as claude_code_health_router
from src.routers.claude_code_streaming import router as claude_code_streaming_router
from src.routers.streaming_cache import router as streaming_cache_router
from src.routers.universal_streaming import router as universal_streaming_router
from src.routers.azure_databricks import router as azure_databricks_router

# Import middleware
from src.middleware import LoggingMiddleware, UnifiedLoggingMiddleware, ErrorHandlingMiddleware, CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting OpenRouter Anthropic Server v2.0")
    logger.info("🔧 Environment configured", environment=config.environment)
    logger.info("🔑 API Key configuration status",
               api_key_configured=bool(config.openrouter_api_key))
    logger.info("📋 Model mapping configured",
               big_model=config.big_model,
               small_model=config.small_model)
    
    # Validate environment
    if not validate_environment():
        logger.error("🔴 FATAL: Environment validation failed")
        sys.exit(1)
    
    # Initialize services
    try:
        # Test service initialization
        from src.services.validation import MessageValidationService
        from src.services.conversion import ModelMappingService
        
        validator = MessageValidationService()
        mapper = ModelMappingService()
        
        logger.info("✅ Services initialized successfully")
        
    except Exception as e:
        logger.error("❌ Service initialization failed",
                    error_type=type(e).__name__,
                    error_message=str(e))
        sys.exit(1)
    
    logger.info("🎯 Server startup completed")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down OpenRouter Anthropic Server")


def validate_environment():
    """Validate that the environment is properly configured."""
    try:
        if not config:
            raise ConfigurationError("Configuration could not be loaded")
        
        if not config.openrouter_api_key:
            raise ConfigurationError("OPENROUTER_API_KEY is required but not found")
        
        # Test LiteLLM import
        try:
            import litellm
            logger.info("✅ LiteLLM available",
                       version=getattr(litellm, '__version__', 'unknown'))
        except ImportError as e:
            raise ConfigurationError(f"LiteLLM not available: {e}")
        
        # Test Instructor import
        try:
            import instructor
            logger.info("✅ Instructor available")
        except ImportError as e:
            logger.warning("⚠️ Instructor not available",
                          error_message=str(e))
        
        logger.info("✅ Environment validation passed")
        return True
        
    except Exception as e:
        logger.error("🔴 Environment validation failed",
                    error_type=type(e).__name__,
                    error_message=str(e))
        return False


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Initialize unified logging system FIRST
    if getattr(config, 'use_unified_logging', True):
        configure_structlog(
            development=config.environment == "development",
            log_level=config.log_level,
            json_logs=getattr(config, 'json_logs', False),
            logs_dir=getattr(config, 'unified_logs_dir', 'logs'),
            log_rotation=getattr(config, 'unified_log_file_rotation', 'daily'),
            log_retention_days=getattr(config, 'unified_log_retention_days', 30)
        )
        unified_logger = get_logger("app.startup")
        unified_logger.info("🔄 Unified Structlog logging system initialized")
        unified_logger.info(f"📁 Log directory: {getattr(config, 'unified_logs_dir', 'logs')}")
        unified_logger.info(f"🔄 Log rotation: {getattr(config, 'unified_log_file_rotation', 'daily')}")
    else:
        # Fallback to legacy logging - but this shouldn't happen anymore
        pass
        unified_logger = logger
    
    # Create FastAPI app with enhanced configuration
    app = FastAPI(
        title="OpenRouter Anthropic Server",
        description="Enhanced modular OpenRouter to Anthropic API proxy server with comprehensive validation, logging, and error handling",
        version="2.0.0",
        lifespan=lifespan,
        docs_url="/docs" if config.environment == "development" else None,
        redoc_url="/redoc" if config.environment == "development" else None,
        openapi_url="/openapi.json" if config.environment == "development" else None
    )
    
    # Add middleware (order matters - last added is executed first)
    
    # 1. Trusted Host middleware (security)
    if config.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure appropriately for production
        )
    
    # 2. CORS middleware
    app.add_middleware(CORSMiddleware)
    
    # 3. Error handling middleware
    app.add_middleware(ErrorHandlingMiddleware)
    
    # 4. Logging middleware (should be last to capture everything)
    if getattr(config, 'use_unified_logging', True):
        app.add_middleware(UnifiedLoggingMiddleware)
        unified_logger.info("🔄 Using unified logging middleware")
    else:
        app.add_middleware(LoggingMiddleware)
        unified_logger.info("⚠️ Using legacy logging middleware")
    
    # Include routers
    app.include_router(health_router)
    app.include_router(claude_code_health_router)  # Claude Code health endpoints
    app.include_router(claude_code_streaming_router)  # Phase 2: Advanced Streaming endpoints
    app.include_router(streaming_cache_router)  # Phase 3A: Advanced Streaming Cache endpoints
    app.include_router(universal_streaming_router)  # Phase 3B: Universal Multi-Model Streaming endpoints
    app.include_router(messages_router)
    app.include_router(tokens_router)
    app.include_router(mcp_router)
    
    # Log active proxy backend configuration
    backend = config.get_active_backend()
    logger.info("🔄 Active proxy backend configured",
               backend=backend,
               endpoint="/v1/messages")
    
    # Azure Databricks dedicated endpoints (always available for direct access)
    if config.requires_databricks_config():
        app.include_router(azure_databricks_router)
        logger.info("🟦 Azure Databricks dedicated endpoints enabled", 
                   endpoint_prefix="/v1/databricks/*",
                   workspace=config.databricks_host,
                   note="Direct access to Azure Databricks endpoints")
    
    # Log backend-specific information
    if backend == "AZURE_DATABRICKS":
        if config.databricks_host and config.databricks_token:
            logger.info("✅ Azure Databricks main routing active",
                       main_endpoint="/v1/messages",
                       workspace=config.databricks_host)
        else:
            logger.warning("⚠️ Azure Databricks backend selected but missing configuration",
                          missing_vars="DATABRICKS_HOST and/or DATABRICKS_TOKEN")
    elif backend == "OPENROUTER":
        logger.info("🔀 OpenRouter direct backend active",
                   main_endpoint="/v1/messages", 
                   mode="bypass_litellm")
    elif backend == "LITELLM_OPENROUTER":
        logger.info("🔗 LiteLLM + OpenRouter backend active",
                   main_endpoint="/v1/messages",
                   mode="litellm_proxy")
    
    # Include debug router (only in development)
    if config.environment == "development":
        app.include_router(debug_router)
        logger.info("🐛 Debug endpoints enabled", endpoint_prefix="/debug/*")
    
    logger.info("🔗 MCP management endpoints enabled", endpoint_prefix="/v1/mcp/*")
    logger.info("🎯 Claude Code health endpoints enabled", endpoint_prefix="/health/claude-code/*")
    logger.info("🚀 Phase 2: Advanced Streaming endpoints enabled", endpoint_prefix="/v1/streaming/*")
    logger.info("⚡ Phase 3A: Advanced Streaming Cache endpoints enabled", endpoint_prefix="/v1/cache/*")
    logger.info("🌐 Phase 3B: Universal Multi-Model Streaming endpoints enabled", endpoint_prefix="/v1/universal/*")
    
    # Add custom exception handlers
    from fastapi.exceptions import RequestValidationError
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Custom validation error handler with Anthropic format."""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Format validation errors for user
        formatted_errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            formatted_errors.append(f"{field_path}: {error['msg']}")
        
        return JSONResponse(
            status_code=400,
            content={
                "type": "error",
                "error": {
                    "type": "invalid_request_error",
                    "message": f"Request validation failed: {'; '.join(formatted_errors)}"
                }
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Custom HTTP exception handler with Anthropic format."""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": "error",
                "error": {
                    "type": "invalid_request_error" if exc.status_code == 400 else "api_error",
                    "message": str(exc.detail)
                }
            }
        )
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        """Custom 404 handler with Anthropic format."""
        return JSONResponse(
            status_code=404,
            content={
                "type": "error",
                "error": {
                    "type": "not_found_error",
                    "message": "The requested resource was not found"
                }
            }
        )
    
    logger.info("🏗️ FastAPI application created with modular architecture")
    logger.info("📚 API documentation configuration",
               docs_enabled=config.environment == 'development')
    
    return app


def main():
    """Main function to start the server."""
    
    # Initialize unified logging system FIRST
    if getattr(config, 'use_unified_logging', True):
        configure_structlog(
            development=config.environment == "development",
            log_level=config.log_level,
            json_logs=getattr(config, 'json_logs', False),
            logs_dir=getattr(config, 'unified_logs_dir', 'logs'),
            log_rotation=getattr(config, 'unified_log_file_rotation', 'daily'),
            log_retention_days=getattr(config, 'unified_log_retention_days', 30)
        )
        main_logger = get_logger("main")
        main_logger.info("🔄 Unified Structlog logging system initialized")
        main_logger.info(f"📁 Log files will be stored in: {getattr(config, 'unified_logs_dir', 'logs')}")
        
        # Initialize error logger with proper config
        from src.utils.error_logger import initialize_error_logger
        error_log_dir = f"{getattr(config, 'unified_logs_dir', 'logs')}/errors"
        initialize_error_logger(error_log_dir)
        main_logger.info(f"📝 Error logger initialized with directory: {error_log_dir}")
        
        # Initialize enhanced error handler with proper config
        from src.utils.enhanced_error_handler import initialize_enhanced_error_handler, SERVER_INSTANCE_ID
        debug_logs_dir = f"{getattr(config, 'unified_logs_dir', 'logs')}/debug"
        enhanced_handler = initialize_enhanced_error_handler(debug_logs_dir)
        main_logger.info(f"🔍 Enhanced error handler initialized with directory: {debug_logs_dir}")
        main_logger.info(f"🆔 Server instance ID: {SERVER_INSTANCE_ID}")
    else:
        # Fallback to legacy logging - but this shouldn't happen anymore
        pass
        main_logger = logger
    
    main_logger.info("🏗️ Starting OpenRouter Anthropic Server - Enhanced Modular Architecture v2.0")
    
    # Create the application
    try:
        app = create_app()
        
        # Configure uvicorn
        uvicorn_config = {
            "app": app,
            "host": config.host,
            "port": config.port,
            "log_level": "warning",  # We handle our own logging
            "access_log": False,     # We have our own access logging
        }
        
        # Add SSL configuration if available
        if hasattr(config, 'ssl_keyfile') and config.ssl_keyfile:
            uvicorn_config.update({
                "ssl_keyfile": config.ssl_keyfile,
                "ssl_certfile": config.ssl_certfile
            })
            logger.info("🔒 SSL/TLS enabled",
                       ssl_keyfile=config.ssl_keyfile,
                       ssl_certfile=config.ssl_certfile)
        
        # Development vs production configuration
        if config.environment == "development":
            uvicorn_config.update({
                "reload": False,  # We don't want auto-reload in our modular setup
                "log_level": "info"
            })
        
        logger.info("🌐 Starting server",
                   host=config.host,
                   port=config.port)
        logger.info("📖 API docs available",
                   docs_url=f"http://{config.host}:{config.port}/docs")
        
        # Start the server
        uvicorn.run(**uvicorn_config)
        
    except Exception as e:
        logger.error("🔴 Failed to start server",
                    error_type=type(e).__name__,
                    error_message=str(e))
        sys.exit(1)


# For development/testing
app = create_app()

if __name__ == "__main__":
    main()