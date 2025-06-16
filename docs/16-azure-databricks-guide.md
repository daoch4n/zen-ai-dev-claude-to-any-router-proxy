# Azure Databricks Claude Integration Guide

A comprehensive guide for integrating and using Anthropic's Claude models (Claude 3.7 Sonnet and Claude Sonnet 4) through Azure Databricks with the Universal AI Streaming Platform.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Backend Integration](#backend-integration)
- [Available Endpoints](#available-endpoints)
- [Usage Examples](#usage-examples)
- [Authentication Details](#authentication-details)
- [Error Handling](#error-handling)
- [Monitoring and Logging](#monitoring-and-logging)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Cost Optimization](#cost-optimization)
- [Best Practices](#best-practices)

## Overview

The Azure Databricks Claude integration provides a transparent proxy that:
- Accepts Anthropic-format requests from Claude Code
- Routes them to Azure Databricks Claude endpoints
- Returns Anthropic-format responses for full compatibility
- Integrates seamlessly with the unified proxy backend system

### Key Features
- **Transparent Proxy**: Full Anthropic API compatibility
- **Unified Backend**: Integrated with `PROXY_BACKEND=AZURE_DATABRICKS` system
- **Auto Model Detection**: Intelligent routing to appropriate Claude endpoints
- **Format Conversion**: Seamless conversion between Anthropic and Azure Databricks formats
- **Comprehensive Error Handling**: Production-ready error management
- **Health Monitoring**: Built-in health checks and monitoring

## Architecture

```
Request Flow:
Claude Code → anthropic-format → FastAPI Proxy → anthropic-format → Azure Databricks Claude

Response Flow:  
Azure Databricks Claude → anthropic-format → FastAPI Proxy → anthropic-format → Claude Code
```

### System Integration
The Azure Databricks integration is built into the unified proxy backend system:

```mermaid
graph TD
    A[Claude Code] --> B[Universal AI Streaming Platform]
    B --> C{PROXY_BACKEND}
    C -->|OPENROUTER| D[OpenRouter Direct]
    C -->|AZURE_DATABRICKS| E[Azure Databricks]
    C -->|LITELLM_OPENROUTER| F[LiteLLM → OpenRouter]
    
    E --> G[databricks-claude-sonnet-4]
    E --> H[databricks-claude-3-7-sonnet]
```

## Prerequisites

### 1. Azure Databricks Workspace
- **Premium tier** Azure Databricks workspace
- Workspace must be in a region that supports **Model Serving**
- Check [Azure Databricks Feature Region Support](https://docs.microsoft.com/en-us/azure/databricks/administration-guide/cloud-configurations/regions) for availability

### 2. Personal Access Token (PAT)
You need a Databricks Personal Access Token with appropriate permissions.

**To create a PAT:**
1. In Azure Databricks workspace, click your username in the top-right corner
2. Select **Settings** → **Developer** tab
3. Click **Manage** next to "Access tokens"
4. Click **Generate new token**
5. Set comment and lifetime (max 730 days by default)
6. **Copy and securely store the token** (you cannot retrieve it later)

> 📋 **Reference:** [Azure Databricks PAT Authentication](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/pat)

### 3. Claude Model Endpoints
Ensure the following endpoints are deployed in your Azure Databricks workspace:
- `databricks-claude-sonnet-4`
- `databricks-claude-3-7-sonnet`

## Configuration

### Unified Backend Configuration

Set the backend mode to Azure Databricks:

```bash
# Required: Set backend mode
PROXY_BACKEND=AZURE_DATABRICKS

# Required: OpenRouter API key (for fallback tools)
OPENROUTER_API_KEY=your-openrouter-api-key

# Required: Azure Databricks configuration
DATABRICKS_HOST=your-workspace-instance  # without .azuredatabricks.net
DATABRICKS_TOKEN=your-databricks-token
```

### Complete .env Configuration

```bash
# Unified Proxy Backend
PROXY_BACKEND=AZURE_DATABRICKS

# OpenRouter (required for tool fallback)
OPENROUTER_API_KEY=your-openrouter-api-key

# Azure Databricks Configuration
DATABRICKS_HOST=your-workspace-instance
DATABRICKS_TOKEN=dapi-your-databricks-token

# Optional: Advanced Configuration
DATABRICKS_TIMEOUT=30.0
DATABRICKS_MAX_RETRIES=3

# Server Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
PORT=4000
HOST=0.0.0.0
```

### Environment Setup

```bash
# Method 1: Copy and edit example
cp .env.example .env
# Edit .env with your actual values

# Method 2: Export directly
export PROXY_BACKEND=AZURE_DATABRICKS
export DATABRICKS_HOST="your-workspace-instance"
export DATABRICKS_TOKEN="your-databricks-token"
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

## Backend Integration

### How It Works

When `PROXY_BACKEND=AZURE_DATABRICKS` is set:

1. **Main `/v1/messages` endpoint** routes directly to Azure Databricks
2. **Model detection** automatically selects the appropriate Claude endpoint
3. **Format conversion** handles Anthropic ↔ Azure Databricks format translation
4. **Tool execution** falls back to OpenRouter for compatibility
5. **Error handling** provides comprehensive error management

### Model Mapping

The system automatically maps model names to appropriate Azure Databricks endpoints:

| Model Name                  | Azure Databricks Endpoint      | Description           |
| --------------------------- | ------------------------------ | --------------------- |
| `claude-sonnet-4`           | `databricks-claude-sonnet-4`   | Latest Claude Sonnet  |
| `claude-3.7-sonnet`         | `databricks-claude-3-7-sonnet` | Claude 3.7 Sonnet     |
| `anthropic/claude-sonnet-4` | `databricks-claude-sonnet-4`   | OpenRouter format     |
| `big`                       | `databricks-claude-sonnet-4`   | Alias for large model |
| `small`                     | `databricks-claude-3-7-sonnet` | Alias for fast model  |
| *default*                   | `databricks-claude-3-7-sonnet` | Default fallback      |

## Available Endpoints

### 1. Main Message Endpoint
**POST** `/v1/messages`

The primary endpoint that automatically routes to Azure Databricks when the backend is configured.

```bash
curl -X POST http://localhost:4000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3.7-sonnet",
    "max_tokens": 100,
    "messages": [
      {
        "role": "user",
        "content": "Hello, how are you?"
      }
    ]
  }'
```

### 2. Health Check Endpoints

**GET** `/health`
Basic server health check including Azure Databricks status.

**GET** `/health/detailed`
Detailed health check with Azure Databricks connectivity tests.

```bash
# Basic health check
curl http://localhost:4000/health

# Detailed health check
curl http://localhost:4000/health/detailed
```

### 3. Legacy Direct Endpoints

These endpoints are available but deprecated in favor of the unified system:

**POST** `/v1/databricks/messages`
**POST** `/v1/databricks/messages/claude-sonnet-4`
**POST** `/v1/databricks/messages/claude-3-7-sonnet`

## Usage Examples

### Claude Code CLI Integration

Simply set the backend and use Claude Code normally:

```bash
# Configure the backend
export PROXY_BACKEND=AZURE_DATABRICKS
export ANTHROPIC_BASE_URL=http://localhost:4000

# Start the proxy server
python start_server.py

# Use Claude Code normally - requests automatically route to Azure Databricks
claude "Explain quantum computing"
```

### Python Example

```python
import requests

# Configure the request - uses unified endpoint
url = "http://localhost:4000/v1/messages"
headers = {"Content-Type": "application/json"}
data = {
    "model": "claude-3.7-sonnet",
    "max_tokens": 150,
    "temperature": 0.7,
    "messages": [
        {
            "role": "user",
            "content": "Explain quantum computing in simple terms"
        }
    ]
}

# Make the request
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    print("Response:", result["content"][0]["text"])
else:
    print("Error:", response.status_code, response.text)
```

### JavaScript Example

```javascript
const response = await fetch('http://localhost:4000/v1/messages', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: 'claude-sonnet-4',
    max_tokens: 200,
    messages: [
      {
        role: 'user',
        content: 'Write a haiku about programming'
      }
    ]
  })
});

const result = await response.json();
console.log('Response:', result.content[0].text);
```

## Authentication Details

Azure Databricks uses **Basic Authentication** with a specific format:

### Token Format
```bash
# Format: base64_encode("token:{your_pat_token}")
echo -n "token:YOUR_DATABRICKS_PAT_TOKEN" | base64
# Result: dG9rZW46WU9VUl9EQVRBQlJJQ0tTX1BBVF9UT0tFTg==
```

### Authentication Header
```
Authorization: Basic dG9rZW46WU9VUl9EQVRBQlJJQ0tTX1BBVF9UT0tFTg==
```

### Why Official Anthropic Library Doesn't Work

The official Anthropic Python library cannot be used directly with Azure Databricks due to fundamental differences:

| Aspect               | Anthropic API                   | Azure Databricks                        |
| -------------------- | ------------------------------- | --------------------------------------- |
| **Authentication**   | `Authorization: Bearer {token}` | `Authorization: Basic {base64_encoded}` |
| **Endpoint Path**    | `/v1/messages`                  | `/serving-endpoints/{name}/invocations` |
| **URL Construction** | Hardcoded in library            | Custom endpoint names                   |
| **Token Format**     | Direct API key                  | `token:{pat}` base64 encoded            |

The Universal AI Streaming Platform handles these differences transparently.

## Error Handling

The system provides comprehensive error handling:

### Configuration Errors
- **503 Service Unavailable**: Azure Databricks backend not enabled
- **503 Service Unavailable**: Missing host or token configuration

### Request Errors
- **400 Bad Request**: Invalid Anthropic request format
- **400 Bad Request**: Empty messages array

### Azure Databricks Errors
- **401 Unauthorized**: Invalid Databricks token
- **403 Forbidden**: Access denied to Azure Databricks endpoints
- **404 Not Found**: Endpoint not found or workspace URL incorrect
- **500 Internal Server Error**: Azure Databricks request failed

### Error Response Format

```json
{
  "error": {
    "type": "authentication_error",
    "message": "Azure Databricks authentication failed. Check your PAT token."
  }
}
```

## Monitoring and Logging

### Structured Logging

The system provides detailed logging for:
- Backend routing decisions
- Model mapping choices
- Azure Databricks API calls
- Response conversions
- Error conditions

Example log output:
```json
{
  "event": "🔄 Backend routing", 
  "backend": "AZURE_DATABRICKS",
  "model": "claude-3.7-sonnet",
  "endpoint": "databricks-claude-3-7-sonnet"
}
{
  "event": "Azure Databricks message created successfully",
  "input_tokens": 15,
  "output_tokens": 42,
  "total_tokens": 57
}
```

### Health Monitoring

```bash
# Monitor system health
curl http://localhost:4000/health/detailed
```

Response includes Azure Databricks connectivity status:
```json
{
  "status": "healthy",
  "backend": "AZURE_DATABRICKS",
  "azure_databricks": {
    "status": "healthy",
    "endpoints": {
      "claude-sonnet-4": "available",
      "claude-3-7-sonnet": "available"
    },
    "workspace": "your-workspace-instance"
  }
}
```

## Testing

### Automated Testing

Run the comprehensive test suite:

```bash
# Test Azure Databricks integration
python -m pytest tests/test_azure_databricks.py -v

# Test unified backend system
python -m pytest tests/test_unified_backend.py -v

# Test integration with existing functionality
python -m pytest tests/integration/ -v
```

### Manual Testing

```bash
# Test configuration loading
python -c "from src.utils.config import config; print('Backend:', config.proxy_backend)"

# Test health endpoint
curl http://localhost:4000/health

# Test message endpoint
curl -X POST http://localhost:4000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-3.7-sonnet", "max_tokens": 50, "messages": [{"role": "user", "content": "Hello"}]}'
```

## Troubleshooting

### Common Issues

#### 1. Backend Not Activated
```
❌ Error: Request routed to OpenRouter instead of Azure Databricks
```
**Solutions:**
- Verify `PROXY_BACKEND=AZURE_DATABRICKS` is set
- Restart the server after configuration changes
- Check environment variable loading

#### 2. Authentication Failures
```
❌ Error: HTTP 401: Unauthorized
```
**Solutions:**
- Verify PAT token is correct and not expired
- Check token permissions for the endpoints
- Ensure proper base64 encoding: `echo -n "token:{pat}" | base64`

#### 3. Configuration Errors
```
❌ Error: HTTP 503: Azure Databricks integration not enabled
```
**Solutions:**
- Check that `DATABRICKS_HOST` and `DATABRICKS_TOKEN` are set
- Verify environment variables are loaded correctly
- Ensure workspace URL format is correct (no .azuredatabricks.net suffix)

#### 4. Endpoint Not Found
```
❌ Error: HTTP 404: Endpoint not found
```
**Solutions:**
- Verify endpoint names match your Azure Databricks configuration
- Check that the endpoints are deployed and accessible
- Confirm workspace instance URL is correct

#### 5. Connection Timeouts
```
❌ Request failed: Read timeout
```
**Solutions:**
- Increase `DATABRICKS_TIMEOUT` if needed
- Check network connectivity to Azure Databricks
- Verify workspace URL is accessible

### Diagnostic Commands

```bash
# Test workspace connectivity
curl -I https://${DATABRICKS_HOST}.azuredatabricks.net/

# Test authentication
TOKEN_ENCODED=$(echo -n "token:${DATABRICKS_TOKEN}" | base64)
curl -H "Authorization: Basic ${TOKEN_ENCODED}" \
     https://${DATABRICKS_HOST}.azuredatabricks.net/api/2.0/clusters/list

# Test endpoint availability  
curl -H "Authorization: Basic ${TOKEN_ENCODED}" \
     https://${DATABRICKS_HOST}.azuredatabricks.net/serving-endpoints/
```

### Log Analysis

```bash
# Monitor logs for Azure Databricks requests
tail -f logs/server.log | grep "Azure Databricks"

# Check for authentication errors
grep "401\|403" logs/server.log

# Monitor token usage
grep "total_tokens" logs/server.log
```

## Cost Optimization

### 1. Token Usage Monitoring

```python
def track_usage(response):
    """Track token usage for cost monitoring."""
    usage = response.get('usage', {})
    prompt_tokens = usage.get('input_tokens', 0)
    completion_tokens = usage.get('output_tokens', 0)
    total_tokens = prompt_tokens + completion_tokens
    
    print(f"💰 Usage: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total tokens")
```

### 2. Smart Model Selection

```bash
# Use Claude 3.7 Sonnet for simpler tasks (faster, cheaper)
curl -X POST http://localhost:4000/v1/messages \
  -d '{"model": "claude-3.7-sonnet", "messages": [...]}'

# Use Claude Sonnet 4 for complex tasks (more capable)
curl -X POST http://localhost:4000/v1/messages \
  -d '{"model": "claude-sonnet-4", "messages": [...]}'
```

### 3. Response Length Control

```json
{
  "model": "claude-3.7-sonnet",
  "max_tokens": 100,  // Limit response length
  "messages": [
    {
      "role": "user", 
      "content": "Give a brief explanation of quantum computing (max 100 words)"
    }
  ]
}
```

## Best Practices

### 1. Environment Management

```bash
# Use separate environments for different stages
export PROXY_BACKEND=AZURE_DATABRICKS  # Production
export DATABRICKS_HOST="prod-workspace-instance"

# Development
export PROXY_BACKEND=OPENROUTER  # Fallback for development
```

### 2. Error Handling

```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("❌ Authentication failed - check your PAT token")
    elif e.response.status_code == 403:
        print("❌ Forbidden - check workspace permissions")
    elif e.response.status_code == 404:
        print("❌ Endpoint not found - verify configuration")
    else:
        print(f"❌ HTTP error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

### 3. Connection Management

```python
# ✅ Good: Reuse HTTP client
import httpx

client = httpx.Client()
for prompt in prompts:
    response = client.post(url, json={"messages": [{"role": "user", "content": prompt}]})

# ❌ Bad: Create new client each time  
for prompt in prompts:
    response = requests.post(url, json={"messages": [{"role": "user", "content": prompt}]})
```

### 4. Security

```bash
# Store tokens securely
export DATABRICKS_TOKEN="$(cat ~/.databricks/token)"

# Use different tokens for different environments
export DATABRICKS_TOKEN_PROD="$(vault kv get -field=token secret/databricks/prod)"
export DATABRICKS_TOKEN_DEV="$(vault kv get -field=token secret/databricks/dev)"
```

### 5. Monitoring

```bash
# Set up health check monitoring
*/5 * * * * curl -f http://localhost:4000/health || alert-team

# Monitor token usage
grep "total_tokens" logs/server.log | tail -100
```

---

## Summary

The Azure Databricks Claude integration provides seamless access to Azure-hosted Claude models through the Universal AI Streaming Platform. With the unified backend system, you can easily switch between different providers while maintaining full API compatibility.

**Key Benefits:**
- ✅ **Seamless Integration**: Drop-in replacement for Anthropic API
- ✅ **Unified Configuration**: Single `PROXY_BACKEND` setting
- ✅ **Automatic Routing**: Intelligent model detection and endpoint selection
- ✅ **Production Ready**: Comprehensive error handling and monitoring
- ✅ **Cost Effective**: Direct Azure Databricks integration for enterprise users

For additional support, refer to the [Unified Proxy Backend Guide](17-unified-proxy-backend-guide.md) and [Production Deployment Guide](05-production-deployment-guide.md). 