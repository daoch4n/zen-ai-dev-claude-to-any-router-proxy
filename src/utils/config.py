"""Enhanced configuration management for the OpenRouter Anthropic Server."""

import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# API Base URL Constants
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
ANTHROPIC_API_BASE = "https://api.anthropic.com/v1"

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
    instructor_model: str = "anthropic/claude-sonnet-4"
    
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
    
    # LiteLLM Configuration
    litellm_timeout: int = Field(default=120, description="LiteLLM request timeout")
    litellm_num_retries: int = Field(default=3, description="Number of retries for failed requests") 
    litellm_retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    litellm_rpm: int = Field(default=10000, description="Requests per minute limit")
    litellm_tpm: int = Field(default=200000, description="Tokens per minute limit")
    
    # LiteLLM settings
    litellm_api_base: Optional[str] = Field(None, env="LITELLM_API_BASE")
    litellm_master_key: Optional[str] = Field(None, env="LITELLM_MASTER_KEY")
    litellm_base_url: Optional[str] = Field(None, env="LITELLM_BASE_URL")
    
    # Cache Configuration (Enhanced for LiteLLM)
    cache_type: str = Field(default="local", description="Cache type: local, redis")
    redis_host: str = Field(default="localhost", description="Redis host for caching")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    
    # Budget and Cost Management (LiteLLM features)
    budget_tracking_enabled: bool = Field(default=False, description="Enable budget tracking")
    max_budget_usd: Optional[float] = Field(default=None, description="Maximum budget in USD")
    budget_duration: str = Field(default="monthly", description="Budget duration: daily, weekly, monthly")
    cost_tracking_enabled: bool = Field(default=True, description="Enable cost tracking")
    
    # Health Monitoring
    health_check_enabled: bool = Field(default=True, description="Enable health monitoring")
    health_check_interval: int = Field(default=60, description="Health check interval in seconds")
    model_health_checks: bool = Field(default=True, description="Enable model connectivity health checks")
    
    # Audit and Logging (LiteLLM enterprise features)
    audit_logging_enabled: bool = Field(default=False, description="Enable audit logging")
    request_logging_enabled: bool = Field(default=True, description="Enable request logging")
    response_logging_enabled: bool = Field(default=False, description="Enable response logging")
    
    # Performance and Scaling
    connection_pool_size: int = Field(default=100, description="HTTP connection pool size")
    max_concurrent_litellm_requests: int = Field(default=50, description="Max concurrent LiteLLM requests")
    
    # Provider Configuration
    fallback_providers: List[str] = Field(
        default_factory=lambda: ["openrouter", "anthropic"],
        description="Fallback provider order"
    )
    provider_timeout_override: Dict[str, int] = Field(
        default_factory=dict,
        description="Per-provider timeout overrides"
    )
    
    # Unified Proxy Backend Configuration
    proxy_backend: str = Field(default="OPENROUTER", description="Proxy backend: AZURE_DATABRICKS, OPENROUTER, or LITELLM_OPENROUTER")
    
    # LiteLLM Bypass Configuration
    openrouter_api_base: str = Field(default="https://openrouter.ai/api/v1", description="OpenRouter API base URL")
    openrouter_direct_timeout: int = Field(default=120, description="Direct OpenRouter request timeout")
    openrouter_direct_retries: int = Field(default=3, description="Direct OpenRouter retry attempts")
    openrouter_direct_model_format: str = Field(default="anthropic/claude-sonnet-4", description="Model format for direct calls")
    bypass_fallback_enabled: bool = Field(default=True, description="Enable fallback to LiteLLM if bypass fails")
    
    # Azure Databricks Configuration
    databricks_host: Optional[str] = Field(default=None, description="Azure Databricks workspace instance (e.g., adb-1234567890123456.7)")
    databricks_token: Optional[str] = Field(default=None, description="Azure Databricks Personal Access Token")
    databricks_timeout: float = Field(default=30.0, description="Azure Databricks request timeout in seconds")
    databricks_max_retries: int = Field(default=3, description="Azure Databricks maximum retry attempts")
    databricks_claude_sonnet_4_endpoint: str = Field(default="databricks-claude-sonnet-4", description="Azure Databricks Claude Sonnet 4 endpoint name")
    databricks_claude_3_7_sonnet_endpoint: str = Field(default="databricks-claude-3-7-sonnet", description="Azure Databricks Claude 3.7 Sonnet endpoint name")
    
    @field_validator('proxy_backend')
    @classmethod
    def validate_proxy_backend(cls, v):
        """Validate proxy backend is valid."""
        valid_backends = ["AZURE_DATABRICKS", "OPENROUTER", "LITELLM_OPENROUTER", "LITELLM_MESSAGES"]
        if v.upper() not in valid_backends:
            raise ValueError(f"Proxy backend must be one of: {valid_backends}")
        return v.upper()
    
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
    def _determine_proxy_backend(cls) -> str:
        """
        Determine proxy backend from environment variables.
        
        Uses PROXY_BACKEND environment variable, defaults to OPENROUTER if not set.
        """
        # Check if PROXY_BACKEND is explicitly set
        proxy_backend = os.environ.get("PROXY_BACKEND")
        if proxy_backend:
            valid_backends = ["AZURE_DATABRICKS", "OPENROUTER", "LITELLM_OPENROUTER", "LITELLM_MESSAGES"]
            if proxy_backend.upper() in valid_backends:
                return proxy_backend.upper()
            else:
                raise ValueError(f"Invalid PROXY_BACKEND value: {proxy_backend}. Must be one of: {valid_backends}")
        
        # Default to OPENROUTER
        return "OPENROUTER"
    
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
            unified_log_retention_days=int(os.environ.get("UNIFIED_LOG_RETENTION_DAYS", "30")),
            
            # LiteLLM Configuration
            litellm_timeout=int(os.environ.get("LITELLM_TIMEOUT", "120")),
            litellm_num_retries=int(os.environ.get("LITELLM_NUM_RETRIES", "3")),
            litellm_retry_delay=float(os.environ.get("LITELLM_RETRY_DELAY", "1.0")),
            litellm_rpm=int(os.environ.get("LITELLM_RPM", "10000")),
            litellm_tpm=int(os.environ.get("LITELLM_TPM", "200000")),
            
            # LiteLLM settings
            litellm_api_base=os.environ.get("LITELLM_API_BASE"),
            litellm_master_key=os.environ.get("LITELLM_MASTER_KEY"),
            litellm_base_url=os.environ.get("LITELLM_BASE_URL"),
            
            # Enhanced Cache Configuration
            cache_type=os.environ.get("CACHE_TYPE", "local"),
            redis_host=os.environ.get("REDIS_HOST", "localhost"),
            redis_port=int(os.environ.get("REDIS_PORT", "6379")),
            redis_password=os.environ.get("REDIS_PASSWORD"),
            redis_url=os.environ.get("REDIS_URL"),
            
            # Budget and Cost Management
            budget_tracking_enabled=os.environ.get("BUDGET_TRACKING_ENABLED", "false").lower() == "true",
            max_budget_usd=float(os.environ["MAX_BUDGET_USD"]) if os.environ.get("MAX_BUDGET_USD") else None,
            budget_duration=os.environ.get("BUDGET_DURATION", "monthly"),
            cost_tracking_enabled=os.environ.get("COST_TRACKING_ENABLED", "true").lower() == "true",
            
            # Health Monitoring
            health_check_enabled=os.environ.get("HEALTH_CHECK_ENABLED", "true").lower() == "true",
            health_check_interval=int(os.environ.get("HEALTH_CHECK_INTERVAL", "60")),
            model_health_checks=os.environ.get("MODEL_HEALTH_CHECKS", "true").lower() == "true",
            
            # Audit and Logging
            audit_logging_enabled=os.environ.get("AUDIT_LOGGING_ENABLED", "false").lower() == "true",
            request_logging_enabled=os.environ.get("REQUEST_LOGGING_ENABLED", "true").lower() == "true",
            response_logging_enabled=os.environ.get("RESPONSE_LOGGING_ENABLED", "false").lower() == "true",
            
            # Performance and Scaling
            connection_pool_size=int(os.environ.get("CONNECTION_POOL_SIZE", "100")),
            max_concurrent_litellm_requests=int(os.environ.get("MAX_CONCURRENT_LITELLM_REQUESTS", "50")),
            
            # Provider Configuration
            fallback_providers=os.environ.get("FALLBACK_PROVIDERS", "openrouter,anthropic").split(","),
            
            # Unified Proxy Backend Configuration with backward compatibility
            proxy_backend=cls._determine_proxy_backend(),
            
            # LiteLLM Bypass Configuration
            openrouter_api_base=os.environ.get("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1"),
            openrouter_direct_timeout=int(os.environ.get("OPENROUTER_DIRECT_TIMEOUT", "120")),
            openrouter_direct_retries=int(os.environ.get("OPENROUTER_DIRECT_RETRIES", "3")),
            openrouter_direct_model_format=os.environ.get("OPENROUTER_DIRECT_MODEL_FORMAT", "anthropic/claude-sonnet-4"),
            bypass_fallback_enabled=os.environ.get("BYPASS_FALLBACK_ENABLED", "true").lower() == "true",
            
            # Azure Databricks Configuration
            databricks_host=os.environ.get("DATABRICKS_HOST"),
            databricks_token=os.environ.get("DATABRICKS_TOKEN"),
            databricks_timeout=float(os.environ.get("DATABRICKS_TIMEOUT", "30.0")),
            databricks_max_retries=int(os.environ.get("DATABRICKS_MAX_RETRIES", "3")),
            databricks_claude_sonnet_4_endpoint=os.environ.get("DATABRICKS_CLAUDE_SONNET_4_ENDPOINT", "databricks-claude-sonnet-4"),
            databricks_claude_3_7_sonnet_endpoint=os.environ.get("DATABRICKS_CLAUDE_3_7_SONNET_ENDPOINT", "databricks-claude-3-7-sonnet"),
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
    
    def get_openrouter_extensions_config(self) -> Dict[str, Any]:
        """Get OpenRouter extension configuration from environment variables."""
        # Import here to avoid circular imports
        try:
            from src.tasks.conversion.openrouter_extensions import get_openrouter_config_from_env
            return get_openrouter_config_from_env()
        except ImportError:
            # Fallback if module not available
            return {}
    
    def get_openai_advanced_config(self) -> Dict[str, Any]:
        """Get OpenAI advanced parameters configuration from environment variables."""
        # Import here to avoid circular imports
        try:
            from src.tasks.conversion.openai_advanced_parameters import get_openai_advanced_config_from_env
            return get_openai_advanced_config_from_env()
        except ImportError:
            # Fallback if module not available
            return {}
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug_enabled or self.log_level == "DEBUG"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.is_development()
    
    def get_litellm_config(self) -> Dict[str, Any]:
        """Get comprehensive LiteLLM configuration."""
        return {
            "timeout": self.litellm_timeout,
            "num_retries": self.litellm_num_retries,
            "retry_delay": self.litellm_retry_delay,
            "rpm": self.litellm_rpm,
            "tpm": self.litellm_tpm,
            "cache_enabled": self.enable_caching,
            "cache_type": self.cache_type,
            "fallback_providers": self.fallback_providers
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get enhanced cache configuration for LiteLLM."""
        config = {
            "enabled": self.enable_caching,
            "ttl": self.cache_ttl,
            "type": self.cache_type
        }
        
        if self.cache_type == "redis":
            config.update({
                "host": self.redis_host,
                "port": self.redis_port,
                "password": self.redis_password,
                "url": self.redis_url
            })
        
        return config
    
    def get_budget_config(self) -> Dict[str, Any]:
        """Get budget and cost tracking configuration."""
        return {
            "budget_tracking_enabled": self.budget_tracking_enabled,
            "max_budget_usd": self.max_budget_usd,
            "budget_duration": self.budget_duration,
            "cost_tracking_enabled": self.cost_tracking_enabled
        }
    
    def get_health_config(self) -> Dict[str, Any]:
        """Get health monitoring configuration."""
        return {
            "health_check_enabled": self.health_check_enabled,
            "health_check_interval": self.health_check_interval,
            "model_health_checks": self.model_health_checks
        }
    
    def get_audit_config(self) -> Dict[str, Any]:
        """Get audit and logging configuration."""
        return {
            "audit_logging_enabled": self.audit_logging_enabled,
            "request_logging_enabled": self.request_logging_enabled,
            "response_logging_enabled": self.response_logging_enabled
        }
    
    def get_litellm_params(self) -> Dict[str, Any]:
        """Get LiteLLM_Params compatible configuration."""
        params = {
            "timeout": self.litellm_timeout,
            "max_retries": self.litellm_num_retries,
            "rpm": self.litellm_rpm,
            "tpm": self.litellm_tpm
        }
        
        if self.max_budget_usd:
            params["max_budget"] = self.max_budget_usd
            params["budget_duration"] = self.budget_duration
        
        return params
    
    def get_bypass_config(self) -> Dict[str, Any]:
        """Get LiteLLM bypass configuration."""
        return {
            "enabled": self.is_openrouter_backend(),
            "api_base": self.openrouter_api_base,
            "timeout": self.openrouter_direct_timeout,
            "retries": self.openrouter_direct_retries,
            "model_format": self.openrouter_direct_model_format,
            "fallback_enabled": self.bypass_fallback_enabled,
            "api_key": self.openrouter_api_key
        }
    
    def get_bypass_model_mapping(self) -> Dict[str, str]:
        """Get model mapping for bypass mode with correct OpenRouter model names."""
        # OpenRouter model mapping using the configured model names
        bypass_mapping = {
            # Map config models to valid OpenRouter models
            "anthropic/claude-sonnet-4": "anthropic/claude-sonnet-4",
            "anthropic/claude-3.7-sonnet": "anthropic/claude-3.7-sonnet",
            "openrouter/anthropic/claude-sonnet-4": "anthropic/claude-sonnet-4",
            "openrouter/anthropic/claude-3.7-sonnet": "anthropic/claude-3.7-sonnet",
            
            # Direct OpenRouter model mappings
            "claude-sonnet-4": "anthropic/claude-sonnet-4",
            "claude-3.7-sonnet": "anthropic/claude-3.7-sonnet",
            
            # Legacy mappings
            "big": "anthropic/claude-sonnet-4",
            "small": "anthropic/claude-3.7-sonnet",
            "sonnet": "anthropic/claude-sonnet-4",
            "haiku": "anthropic/claude-3.7-sonnet",
            "opus": "anthropic/claude-sonnet-4",  # Map to sonnet-4 as fallback
            
            # Common variations
            "anthropic/claude-sonnet-4": "anthropic/claude-sonnet-4",
            "anthropic/claude-3.7-sonnet": "anthropic/claude-3.7-sonnet",
            
            # Handle any remaining openrouter/ prefixed models
            "openrouter/anthropic/claude-sonnet-4": "anthropic/claude-sonnet-4",
            "openrouter/anthropic/claude-3.7-sonnet": "anthropic/claude-3.7-sonnet"
        }
        
        return bypass_mapping
    
    def get_databricks_config(self) -> Dict[str, Any]:
        """Get Azure Databricks configuration."""
        return {
            "enabled": self.is_azure_databricks_backend(),
            "host": self.databricks_host,
            "token": self.databricks_token,
            "timeout": self.databricks_timeout,
            "max_retries": self.databricks_max_retries,
            "endpoints": {
                "claude_sonnet_4": self.databricks_claude_sonnet_4_endpoint,
                "claude_3_7_sonnet": self.databricks_claude_3_7_sonnet_endpoint
            }
        }
    
    def get_databricks_model_mapping(self) -> Dict[str, str]:
        """Get model mapping for Azure Databricks endpoints."""
        return {
            # Standard Claude model names to Azure Databricks endpoints
            "claude-sonnet-4": self.databricks_claude_sonnet_4_endpoint,
            "claude-3.7-sonnet": self.databricks_claude_3_7_sonnet_endpoint,
            "claude-3-7-sonnet": self.databricks_claude_3_7_sonnet_endpoint,
            
            # Anthropic format models
            "anthropic/claude-sonnet-4": self.databricks_claude_sonnet_4_endpoint,
            "anthropic/claude-3.7-sonnet": self.databricks_claude_3_7_sonnet_endpoint,
            "anthropic/claude-3-7-sonnet": self.databricks_claude_3_7_sonnet_endpoint,
            
            # Generic mappings
            "sonnet-4": self.databricks_claude_sonnet_4_endpoint,
            "3.7-sonnet": self.databricks_claude_3_7_sonnet_endpoint,
            "sonnet": self.databricks_claude_3_7_sonnet_endpoint,  # Default to 3.7
            "big": self.databricks_claude_sonnet_4_endpoint,
            "small": self.databricks_claude_3_7_sonnet_endpoint,
            
            # Version-specific mappings
            "claude-sonnet-4-20250514": self.databricks_claude_sonnet_4_endpoint,
            "claude-3-7-sonnet-20250219": self.databricks_claude_3_7_sonnet_endpoint,
            
            # Direct endpoint names (passthrough)
            self.databricks_claude_sonnet_4_endpoint: self.databricks_claude_sonnet_4_endpoint,
            self.databricks_claude_3_7_sonnet_endpoint: self.databricks_claude_3_7_sonnet_endpoint,
        }
    
    # Unified Proxy Backend Helper Methods
    
    def is_azure_databricks_backend(self) -> bool:
        """Check if Azure Databricks backend is active."""
        return self.proxy_backend == "AZURE_DATABRICKS"
    
    def is_openrouter_backend(self) -> bool:
        """Check if OpenRouter direct backend is active."""
        return self.proxy_backend == "OPENROUTER"
    
    def is_litellm_backend(self) -> bool:
        """Check if LiteLLM + OpenRouter backend is active."""
        return self.proxy_backend == "LITELLM_OPENROUTER"
    
    def get_active_backend(self) -> str:
        """Get the active proxy backend."""
        return self.proxy_backend
    
    def requires_databricks_config(self) -> bool:
        """Check if Azure Databricks configuration is required."""
        return self.is_azure_databricks_backend()
    
    def requires_openrouter_config(self) -> bool:
        """Check if OpenRouter configuration is required."""
        return self.is_openrouter_backend() or self.is_litellm_backend()
    


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