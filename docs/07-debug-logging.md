# Debug Logging System

## Overview

The OpenRouter Anthropic Server implements comprehensive error logging following **Critical Development Rule #3**: "When ERROR happens, the first thing to do is check the debug log."

## Features

### 1. Automatic Error Logging
- All errors are automatically logged to `logs/errors/errors_YYYY-MM-DD.jsonl`
- Daily log rotation for easy management
- JSON Lines format for machine-readable analysis
- Full stack traces and request/response data captured

### 2. Debug Endpoints (Development Only)
- `GET /debug/errors/recent` - View recent errors
- `GET /debug/errors/{correlation_id}` - Find specific error
- `GET /debug/errors/stats` - Error statistics
- `POST /debug/errors/cleanup` - Clean old logs

### 3. Error Log Format
```json
{
  "timestamp": "2025-06-01T16:42:11.425Z",
  "correlation_id": "f81f3942-5199-4f3d-940f-f362c54c5c1c_continuation",
  "error_type": "BadRequestError",
  "error_message": "OpenrouterException - Provider returned error",
  "stack_trace": "Traceback (most recent call last):\n...",
  "request": {
    "model": "openrouter/anthropic/claude-sonnet-4",
    "messages": "[4 messages]",
    "api_key": "sk-o****xxxx",
    "api_base": "https://openrouter.ai/api/v1"
  },
  "response": {
    "status_code": 400,
    "headers": {},
    "body": "error details..."
  },
  "context": {
    "service": "HTTPClient",
    "method": "make_litellm_request",
    "processing_time": 2.865,
    "request_id": "f81f3942-5199-4f3d-940f-f362c54c5c1c_continuation"
  }
}
```

## Usage

### Quick Check Script
```bash
# Check recent errors
python check_debug_logs.py

# Check specific error
python check_debug_logs.py f81f3942-5199-4f3d-940f-f362c54c5c1c_continuation
```

### Manual API Calls
```bash
# Get recent 5 errors
curl http://localhost:4000/debug/errors/recent?count=5 | jq .

# Get specific error
curl http://localhost:4000/debug/errors/f81f3942-5199-4f3d-940f-f362c54c5c1c_continuation | jq .

# Get error statistics
curl http://localhost:4000/debug/errors/stats | jq .
```

### Direct File Access
```bash
# View today's errors
cat logs/errors/errors_$(date +%Y-%m-%d).jsonl | jq .

# Search for specific correlation ID
grep "f81f3942-5199-4f3d-940f-f362c54c5c1c" logs/errors/*.jsonl | jq .
```

## Debug Workflow

1. **See Error**: Notice error in console/logs
   ```
   2025-06-01 16:42:11,426 - openrouter_proxy - ERROR - ❌ Message creation failed: litellm.BadRequestError
   ```

2. **Note Correlation ID**: Find the ID in error messages
   ```
   Request ID: f81f3942-5199-4f3d-940f-f362c54c5c1c_continuation
   ```

3. **Check Debug Logs**: Use any method above
   ```bash
   python check_debug_logs.py f81f3942-5199-4f3d-940f-f362c54c5c1c_continuation
   ```

4. **Analyze Details**:
   - Full request data (sanitized)
   - Complete stack trace
   - Response from API
   - Context information

5. **Fix Issue**: Use comprehensive information to fix root cause

## Security Features

- **API Key Masking**: All API keys are automatically masked
- **Content Truncation**: Large messages truncated to prevent huge logs
- **Sanitized Headers**: Sensitive headers are masked
- **Development Only**: Debug endpoints only available in development mode

## Maintenance

### Log Rotation
- Logs automatically rotate daily
- Old logs can be cleaned up:
  ```bash
  curl -X POST http://localhost:4000/debug/errors/cleanup?days_to_keep=7
  ```

### Disk Space
- Each error typically uses 2-10KB
- Monitor `logs/errors/` directory size
- Configure retention period as needed

## Troubleshooting

### No Logs Found
- Ensure server is running with new code
- Check `ENVIRONMENT=development` for debug endpoints
- Verify `logs/errors/` directory exists

### Can't Access Debug Endpoints
- Only available in development mode
- Check server configuration
- Ensure port 4000 is accessible

### Large Log Files
- Use cleanup endpoint or script
- Adjust retention period
- Consider log aggregation service for production

## Example Error Analysis

When you see this error:
```
❌ LiteLLM API call failed: litellm.BadRequestError: OpenrouterException - Provider returned error
```

1. Check recent errors:
   ```bash
   curl http://localhost:4000/debug/errors/recent?count=1 | jq .
   ```

2. Find the detailed error with:
   - Exact request sent to OpenRouter
   - Full response received
   - Tool execution details
   - Message conversion steps

3. Common issues found via debug logs:
   - Invalid message format
   - Tool result formatting errors
   - API key issues
   - Rate limiting
   - Model availability

## Best Practices

1. **Always Check Logs First**: Follow Critical Rule #3
2. **Use Correlation IDs**: Track errors through the system
3. **Monitor Patterns**: Use stats endpoint to find trends
4. **Clean Up Regularly**: Don't let logs grow indefinitely
5. **Secure Production**: Disable debug endpoints in production 