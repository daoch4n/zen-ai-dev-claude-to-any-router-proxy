"""Enhanced configuration management for the OpenRouter Anthropic Server."""

import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import logging after env loading to avoid circular imports
try:
    from src.core.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Fallback for initialization scenarios
    logger = None

class ServerConfig(BaseModel):
    """Enhanced server configuration settings with validation."""
    
    # API Configuration
    openrouter_api_key: str = Field(..., description="OpenRouter API key")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", description="OpenRouter API base URL")
    host: str = Field(..., description="Server host")
    port: int = Field(..., description="Server port")
    
    # Model Configuration
    big_model: str = Field(..., description="Big model for complex tasks")
    small_model: str = Field(..., description="Small model for simple tasks")
    
    # Logging Configuration
    log_level: str = Field(..., description="Logging level")
    debug_enabled: bool = Field(..., description="Enable debug mode")
    debug_logs_dir: str = Field(..., description="Debug logs directory")
    environment: str = Field(..., description="Environment (development/production)")
    
    # Unified Logging Configuration (Structlog)
    use_unified_logging: bool = Field(default=True, description="Use unified structlog logging system")
    json_logs: bool = Field(default=False, description="Use JSON log format (recommended for production)")
    unified_logs_dir: str = Field(default="logs", description="Directory for unified log files")
    unified_log_file_rotation: str = Field(default="daily", description="Log file rotation interval")
    unified_log_retention_days: int = Field(default=30, description="Log file retention in days")
    
    # Request Configuration
    max_tokens_limit: int = Field(..., description="Maximum tokens limit")
    request_timeout: int = Field(..., description="Request timeout in seconds")
    
    # Instructor Configuration
    instructor_enabled: bool = True
    instructor_model: str = "anthropic/claude-3-5-sonnet-20241022"
    
    # Tool execution configuration
    tool_execution_enabled: bool = True
    tool_execution_timeout: int = 30
    tool_working_directory: str = "/tmp/claude-code-proxy"
    tool_max_file_size: int = 10 * 1024 * 1024  # 10MB
    tool_allowed_commands: List[str] = Field(
        default_factory=lambda: [
            "ls", "pwd", "whoami", "date", "echo", "cat", "head", "tail",
            "grep", "find", "wc", "sort", "uniq", "cut", "tr", "sed", "awk",
            "which", "where", "type", "file", "stat", "du", "df", "ps",
            "uname", "hostname", "uptime", "id", "groups", "env", "printenv"
        ]
    )
    tool_debug_enabled: bool = False
    tool_max_concurrent_tools: int = 5
    
    # Tool rate limiting
    tool_rate_limit_window: int = 60  # seconds
    tool_rate_limit_max_requests: int = 100  # max requests per window
    
    # Tool security settings
    tool_security_strict_mode: bool = True
    tool_security_allow_absolute_paths: bool = False
    tool_security_max_path_depth: int = 10
    tool_security_blocked_extensions: List[str] = Field(
        default_factory=lambda: [
            ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
            ".exe", ".dll", ".so", ".dylib", ".app", ".deb", ".rpm"
        ]
    )
    
    # Performance Configuration
    enable_caching: bool = Field(..., description="Enable response caching")
    cache_ttl: int = Field(..., description="Cache TTL in seconds")
    max_concurrent_requests: int = Field(..., description="Max concurrent requests")
    
    @field_validator('openrouter_api_key')
    @classmethod
    def validate_api_key(cls, v):
        """Validate API key is not empty."""
        if not v or not v.strip():
            raise ValueError("OpenRouter API key cannot be empty")
        return v.strip()
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        """Validate port is in valid range."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        """Validate environment is valid."""
        valid_environments = ["development", "production", "testing"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v.lower()
    
    @field_validator('max_tokens_limit')
    @classmethod
    def validate_max_tokens(cls, v):
        """Validate max tokens is positive."""
        if v <= 0:
            raise ValueError("Max tokens limit must be positive")
        return v
    
    @field_validator('cache_ttl')
    @classmethod
    def validate_cache_ttl(cls, v):
        """Validate cache TTL is positive."""
        if v <= 0:
            raise ValueError("Cache TTL must be positive")
        return v
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create configuration from environment variables."""
        # Validate required environment variables
        required_vars = {
            "OPENROUTER_API_KEY": "OpenRouter API key is required",
            "HOST": "HOST is required",
            "PORT": "PORT is required",
            "ANTHROPIC_MODEL": "ANTHROPIC_MODEL is required",
            "ANTHROPIC_SMALL_FAST_MODEL": "ANTHROPIC_SMALL_FAST_MODEL is required",
            "LOG_LEVEL": "LOG_LEVEL is required",
            "DEBUG": "DEBUG is required",
            "DEBUG_LOGS_DIR": "DEBUG_LOGS_DIR is required",
            "ENVIRONMENT": "ENVIRONMENT is required",
            "MAX_TOKENS_LIMIT": "MAX_TOKENS_LIMIT is required",
            "REQUEST_TIMEOUT": "REQUEST_TIMEOUT is required",
            "INSTRUCTOR_ENABLED": "INSTRUCTOR_ENABLED is required",
            "ENABLE_CACHING": "ENABLE_CACHING is required",
            "CACHE_TTL": "CACHE_TTL is required",
            "MAX_CONCURRENT_REQUESTS": "MAX_CONCURRENT_REQUESTS is required"
        }
        
        missing_vars = []
        for var, description in required_vars.items():
            if not os.environ.get(var):
                missing_vars.append(f"{var} ({description})")
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return cls(
            openrouter_api_key=os.environ["OPENROUTER_API_KEY"],
            openrouter_base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            host=os.environ["HOST"],
            port=int(os.environ["PORT"]),
            big_model=os.environ["ANTHROPIC_MODEL"],
            small_model=os.environ["ANTHROPIC_SMALL_FAST_MODEL"],
            debug_enabled=os.environ["DEBUG"].lower() == "true",
            log_level=os.environ["LOG_LEVEL"],
            debug_logs_dir=os.environ["DEBUG_LOGS_DIR"],
            max_tokens_limit=int(os.environ["MAX_TOKENS_LIMIT"]),
            request_timeout=int(os.environ["REQUEST_TIMEOUT"]),
            instructor_enabled=os.environ["INSTRUCTOR_ENABLED"].lower() == "true",
            enable_caching=os.environ["ENABLE_CACHING"].lower() == "true",
            cache_ttl=int(os.environ["CACHE_TTL"]),
            max_concurrent_requests=int(os.environ["MAX_CONCURRENT_REQUESTS"]),
            environment=os.environ["ENVIRONMENT"],
            # Unified Logging Configuration (with defaults)
            use_unified_logging=os.environ.get("USE_UNIFIED_LOGGING", "true").lower() == "true",
            json_logs=os.environ.get("JSON_LOGS", "false").lower() == "true",
            unified_logs_dir=os.environ.get("UNIFIED_LOGS_DIR", "logs"),
            unified_log_file_rotation=os.environ.get("UNIFIED_LOG_FILE_ROTATION", "daily"),
            unified_log_retention_days=int(os.environ.get("UNIFIED_LOG_RETENTION_DAYS", "30"))
        )
    
    def get_model_mapping(self) -> Dict[str, str]:
        """Get comprehensive model mapping configuration including legacy mappings."""
        return {
            # Configuration-based mappings
            "big": self.big_model,
            "small": self.small_model,
            "anthropic/claude-sonnet-4": self.big_model,
            "anthropic/claude-3.7-sonnet": self.small_model,
            
            # Claude Code default models (from legacy)
            'claude-sonnet-4-20250514': 'anthropic/claude-sonnet-4',
            'claude-opus-4-20250514': 'anthropic/claude-sonnet-4',  # Map to sonnet-4 as fallback
            'claude-3-7-sonnet-20250219': 'anthropic/claude-3.7-sonnet',
            
            # Common Claude model names (from legacy)
            'claude-sonnet-4': 'anthropic/claude-sonnet-4',
            'claude-3.7-sonnet': 'anthropic/claude-3.7-sonnet',
            'claude-3-5-sonnet-20241022': 'anthropic/claude-3.7-sonnet',
            'claude-3-5-sonnet': 'anthropic/claude-3.7-sonnet',
            'claude-3-sonnet-20240229': 'anthropic/claude-3.7-sonnet',
            'claude-3-sonnet': 'anthropic/claude-3.7-sonnet',
            'claude-3-haiku-20241022': 'anthropic/claude-3.7-sonnet',  # Map to fast model
            'claude-3-haiku': 'anthropic/claude-3.7-sonnet',
            'claude-3-opus': 'anthropic/claude-sonnet-4',  # Map to big model
            
            # Generic mappings (from legacy)
            'sonnet': 'anthropic/claude-sonnet-4',
            'haiku': 'anthropic/claude-3.7-sonnet',
            'opus': 'anthropic/claude-sonnet-4',
            
            # Additional common variations
            'claude-3-5-haiku-20241022': 'anthropic/claude-3.7-sonnet',
            'claude-3-5-haiku': 'anthropic/claude-3.7-sonnet',
            'claude-3-haiku-20240307': 'anthropic/claude-3.7-sonnet',
            'claude-3-opus-20240229': 'anthropic/claude-sonnet-4',
            
            # Handle models with anthropic/ prefix that need remapping
            'anthropic/claude-3-5-sonnet-20241022': 'anthropic/claude-3.7-sonnet',
            'anthropic/claude-3-5-sonnet': 'anthropic/claude-3.7-sonnet',
            'anthropic/claude-3-sonnet-20240229': 'anthropic/claude-3.7-sonnet',
            'anthropic/claude-3-sonnet': 'anthropic/claude-3.7-sonnet',
            'anthropic/claude-3-haiku-20241022': 'anthropic/claude-3.7-sonnet',
            'anthropic/claude-3-haiku': 'anthropic/claude-3.7-sonnet',
            'anthropic/claude-3-opus': 'anthropic/claude-sonnet-4',
            'anthropic/claude-3-opus-20240229': 'anthropic/claude-sonnet-4'
        }
    
    def get_instructor_config(self) -> Dict[str, Any]:
        """Get Instructor-specific configuration."""
        return {
            "enabled": self.instructor_enabled,
            "model": self.instructor_model
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance-related configuration."""
        return {
            "enable_caching": self.enable_caching,
            "cache_ttl": self.cache_ttl,
            "max_concurrent_requests": self.max_concurrent_requests,
            "request_timeout": self.request_timeout
        }
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug_enabled or self.log_level == "DEBUG"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.is_development()

# Global configuration instance
try:
    config = ServerConfig.from_env()
except Exception as e:
    # Fallback configuration for testing or when env vars are missing
    if logger:
        logger.error("Failed to load configuration from environment",
                    error=str(e),
                    message="Please ensure all required environment variables are set in your .env file",
                    reference="See .env.example for the complete list of required variables")
    else:
        # Fallback to basic logging during early initialization
        import sys
        print(f"Warning: Failed to load configuration from environment: {e}", file=sys.stderr)
        print("Please ensure all required environment variables are set in your .env file", file=sys.stderr)
        print("See .env.example for the complete list of required variables", file=sys.stderr)
    raise e
