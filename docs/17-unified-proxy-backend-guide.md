# Unified Proxy Backend System Guide

## Overview

The Unified Proxy Backend System consolidates multiple proxy configuration flags into a single, clean `PROXY_BACKEND` environment variable. This simplifies configuration and makes the system more maintainable and extensible.

## Migration from Multiple Flags

### Old System (Deprecated)
```bash
# Multiple boolean flags - confusing and hard to maintain
DATABRICKS_ENABLED=true
BYPASS_LITELLM_ENABLED=false
```

### New System (Recommended)
```bash
# Single backend selector - clear and extensible
PROXY_BACKEND=AZURE_DATABRICKS
```

## Available Backends

### 1. `AZURE_DATABRICKS`
Routes all `/v1/messages` requests to Azure Databricks Claude endpoints.

**Configuration Required:**
```bash
PROXY_BACKEND=AZURE_DATABRICKS
DATABRICKS_HOST=your-workspace-instance
DATABRICKS_TOKEN=your-databricks-token
```

**Request Flow:**
```
Claude Code → /v1/messages → Azure Databricks Claude → Response
```

### 2. `OPENROUTER`
Routes all `/v1/messages` requests directly to OpenRouter (bypasses LiteLLM).

**Configuration Required:**
```bash
PROXY_BACKEND=OPENROUTER
OPENROUTER_API_KEY=your-openrouter-api-key
```

**Request Flow:**
```
Claude Code → /v1/messages → OpenRouter Direct → Response
```

### 3. `LITELLM_OPENROUTER`
Routes all `/v1/messages` requests through LiteLLM to OpenRouter (legacy mode).

**Configuration Required:**
```bash
PROXY_BACKEND=LITELLM_OPENROUTER
OPENROUTER_API_KEY=your-openrouter-api-key
```

**Request Flow:**
```
Claude Code → /v1/messages → LiteLLM → OpenRouter → Response
```

### 4. `LITELLM_MESSAGES`
Routes all `/v1/messages` requests to LiteLLM's native `/v1/messages` endpoint.

**Configuration Required:**
```bash
PROXY_BACKEND=LITELLM_MESSAGES
LITELLM_BASE_URL=http://localhost:4001
OPENROUTER_API_KEY=your-openrouter-api-key
```

**Request Flow:**
```
Claude Code → /v1/messages → LiteLLM /v1/messages → OpenRouter → Response
```

**Key Benefits:**
- No format conversion needed (native Anthropic format support)
- Simpler architecture with less code complexity
- Full LiteLLM features (fallbacks, load balancing, caching)
- Better performance due to eliminated conversion overhead

See the [LiteLLM Messages Backend Guide](18-litellm-messages-backend-guide.md) for detailed setup instructions.

## Configuration Examples

### Example 1: Azure Databricks Production
```bash
# Azure Databricks for production workloads
PROXY_BACKEND=AZURE_DATABRICKS
DATABRICKS_HOST=adb-1234567890123456.7
DATABRICKS_TOKEN=dapi1234567890abcdefghijklmnopqrstuv-0
DATABRICKS_TIMEOUT=30.0
DATABRICKS_MAX_RETRIES=3
```

### Example 2: OpenRouter Direct Development
```bash
# OpenRouter direct for development (fastest)
PROXY_BACKEND=OPENROUTER
OPENROUTER_API_KEY=sk-or-v1-abcdefghijklmnop
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
```

### Example 3: LiteLLM Legacy Mode
```bash
# LiteLLM mode for compatibility
PROXY_BACKEND=LITELLM_OPENROUTER
OPENROUTER_API_KEY=sk-or-v1-abcdefghijklmnop
LITELLM_TIMEOUT=120
```

## Default Configuration

If `PROXY_BACKEND` is not set, the system defaults to `OPENROUTER` backend.

## API Endpoint Behavior

### Main Message Endpoint
`POST /v1/messages` now routes based on `PROXY_BACKEND`:

```bash
# Azure Databricks backend
curl -X POST http://localhost:4000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3.7-sonnet",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### Dedicated Endpoints
Azure Databricks dedicated endpoints remain available for direct access:
- `POST /v1/databricks/messages`
- `POST /v1/databricks/messages/claude-sonnet-4`
- `POST /v1/databricks/messages/claude-3-7-sonnet`
- `POST /v1/databricks/messages/stream`

## Model Mapping

Each backend handles model mapping differently:

### Azure Databricks
| Model Request       | Azure Databricks Endpoint      |
| ------------------- | ------------------------------ |
| `claude-sonnet-4`   | `databricks-claude-sonnet-4`   |
| `claude-3.7-sonnet` | `databricks-claude-3-7-sonnet` |
| `big`               | `databricks-claude-sonnet-4`   |
| `small`             | `databricks-claude-3-7-sonnet` |

### OpenRouter
| Model Request       | OpenRouter Model              |
| ------------------- | ----------------------------- |
| `claude-sonnet-4`   | `anthropic/claude-sonnet-4`   |
| `claude-3.7-sonnet` | `anthropic/claude-3.7-sonnet` |
| `big`               | `anthropic/claude-sonnet-4`   |
| `small`             | `anthropic/claude-3.7-sonnet` |

## Configuration Validation

The system validates backend configuration at startup:

### Valid Backend Values
- `AZURE_DATABRICKS`
- `OPENROUTER`
- `LITELLM_OPENROUTER`
- `LITELLM_MESSAGES`

### Required Configuration Check
- **Azure Databricks**: Requires `DATABRICKS_HOST` and `DATABRICKS_TOKEN`
- **OpenRouter**: Requires `OPENROUTER_API_KEY`
- **LiteLLM**: Requires `OPENROUTER_API_KEY`

## Monitoring and Logging

### Startup Logging
```json
{"backend": "AZURE_DATABRICKS", "endpoint": "/v1/messages", "event": "Active proxy backend configured"}
{"main_endpoint": "/v1/messages", "workspace": "your-workspace", "event": "Azure Databricks main routing active"}
```

### Request Logging
```json
{"model": "claude-3.7-sonnet", "backend": "AZURE_DATABRICKS", "correlation_id": "req_123", "event": "Processing message request"}
{"model": "claude-3.7-sonnet", "event": "Routing to Azure Databricks backend"}
```

## Health Checks

### Backend Status Check
```bash
# Check which backend is active
curl http://localhost:4000/health
```

### Backend-Specific Health
```bash
# Azure Databricks health (when active)
curl http://localhost:4000/v1/databricks/health/detailed
```

## Troubleshooting

### Common Issues

1. **Backend Validation Error**
   ```
   ValueError: Invalid PROXY_BACKEND value: INVALID. Must be one of: ['AZURE_DATABRICKS', 'OPENROUTER', 'LITELLM_OPENROUTER']
   ```
   **Solution**: Use a valid backend value.

2. **Missing Configuration**
   ```
   503 Service Unavailable: Azure Databricks host and token must be configured
   ```
   **Solution**: Set required environment variables for the selected backend.

3. **Backend Mismatch**
   ```
   Warning: Azure Databricks backend selected but missing configuration
   ```
   **Solution**: Either provide the required configuration or change the backend.

### Debug Commands

```bash
# Check current backend configuration
python -c "from src.utils.config import config; print(f'Backend: {config.get_active_backend()}')"

# Check configuration requirements
python -c "from src.utils.config import config; print(f'Requires Databricks: {config.requires_databricks_config()}')"
```

## Migration Guide

### Step 1: Choose Unified Backend
Determine your desired backend:
- **Production with Azure Databricks**: `PROXY_BACKEND=AZURE_DATABRICKS`
- **Development/Fast**: `PROXY_BACKEND=OPENROUTER`
- **Legacy/Compatibility**: `PROXY_BACKEND=LITELLM_OPENROUTER`

### Step 2: Update Configuration
Add the new configuration:
```bash
echo "PROXY_BACKEND=AZURE_DATABRICKS" >> .env
```

### Step 3: Test
Restart the server and verify the backend is active:
```bash
curl http://localhost:4000/health
```

## Best Practices

### 1. Environment-Specific Configuration
```bash
# Development
PROXY_BACKEND=OPENROUTER

# Staging  
PROXY_BACKEND=AZURE_DATABRICKS

# Production
PROXY_BACKEND=AZURE_DATABRICKS
```

### 2. Configuration Management
Use environment-specific `.env` files:
- `.env.development`
- `.env.staging`
- `.env.production`

### 3. Monitoring
Set up monitoring for backend health:
```bash
# Add to monitoring script
curl -f http://localhost:4000/v1/databricks/health || alert "Azure Databricks down"
```

### 4. Fallback Strategy
Consider fallback configuration:
```bash
# Primary backend
PROXY_BACKEND=AZURE_DATABRICKS

# Fallback configuration
BYPASS_FALLBACK_ENABLED=true  # Falls back to OpenRouter if Azure Databricks fails
```

## Future Extensions

The unified backend system is designed for easy extension:

### Adding New Backends
```python
# New backend types can be easily added:
# PROXY_BACKEND=AWS_BEDROCK
# PROXY_BACKEND=GOOGLE_VERTEX
# PROXY_BACKEND=ANTHROPIC_DIRECT
```

### Configuration Validation
```python
valid_backends = ["AZURE_DATABRICKS", "OPENROUTER", "LITELLM_OPENROUTER", "NEW_BACKEND"]
```

## Summary

The Unified Proxy Backend System provides:

✅ **Simplified Configuration**: Single `PROXY_BACKEND` variable  
✅ **Clear Backend Selection**: Explicit backend choice  
✅ **Backward Compatibility**: Existing configurations continue to work  
✅ **Extensibility**: Easy to add new backends  
✅ **Better Monitoring**: Clear logging of active backend  
✅ **Production Ready**: Comprehensive validation and error handling  

The system maintains the flexibility of the original multi-flag approach while providing a much cleaner and more maintainable configuration interface. 