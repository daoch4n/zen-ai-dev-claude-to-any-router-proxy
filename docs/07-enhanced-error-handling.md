# Enhanced Error Handling & Debug Logging System

This document describes the comprehensive error handling and debugging system implemented for the OpenRouter Anthropic Server, including both the **Enhanced Exception Handling System** with hash-based tracking and the **General Debug Logging System**.

## 🎯 Key Features Overview

### ✅ **Enhanced Exception Handling System**
- **Time/Date tracking** with automatic UTC timestamps
- **Hash-based error blocks** for quick code location lookup
- **Server instance separation** with unique log directories
- **Detailed error context** including execution data and stack traces
- **Code location tracking** with precise file, function, and line numbers

### ✅ **General Debug Logging System**
- **Automatic error logging** to daily rotated JSONL files
- **Debug endpoints** for real-time error investigation (development only)
- **Correlation ID tracking** for request tracing
- **Comprehensive request/response logging** with security sanitization

## 🚀 Enhanced Exception Handling System

### Hash-Based Error Tracking

The enhanced system provides **unique 12-character hashes** for each error handling block, enabling instant code location lookup.

#### Log File Structure
```
logs/
└── debug/
    └── server_{instance_id}/
        ├── errors_{timestamp}.jsonl      # Enhanced error logs
        ├── debug_{timestamp}.jsonl       # Debug information  
        └── error_blocks_{timestamp}.json # Hash registry
```

#### Example Enhanced Error Log Entry
```json
{
  "timestamp": "2024-03-19T14:30:25.123456Z",
  "server_instance_id": "a1b2c3d4",
  "correlation_id": "req_123456789",
  "error_block_hash": "abc123def456",
  "error_details": {
    "type": "ValueError",
    "message": "Invalid input format",
    "args": ["Invalid input format"],
    "stack_trace": "Traceback (most recent call last):\n...",
    "stack_frames": [
      {
        "filename": "/src/services/validation.py",
        "line_number": 42,
        "function_name": "validate",
        "code_line": "raise ValueError('Invalid input format')"
      }
    ]
  },
  "code_location": {
    "function_name": "validate",
    "file_path": "/src/services/validation.py",
    "line_number": 42,
    "code_context": "Function: validate"
  },
  "execution_context": {
    "thread_id": "12345",
    "process_id": 12345,
    "context_data": {
      "service": "ValidationService",
      "method": "validate"
    }
  },
  "request_data": {
    "messages": [...],
    "model": "claude-3-sonnet"
  },
  "system_info": {
    "python_version": "3.10.0",
    "platform": "linux",
    "working_directory": "/app"
  }
}
```

### Debug Endpoints for Enhanced Error Handling

#### Server Instance Information
```http
GET /debug/server/instance
```
Returns current server instance ID, startup time, and log file locations.

#### Recent Enhanced Errors
```http
GET /debug/errors/enhanced/recent?count=10
```
Get recent errors with full debugging information.

#### Error Lookup by Hash
```http
GET /debug/errors/hash/{block_hash}
```
Find the exact code location for an error using its hash.

#### Error Block Registry
```http
GET /debug/errors/registry
```
View all registered error handling blocks and their hashes.

#### Enhanced Error Statistics
```http
GET /debug/errors/enhanced/stats
```
Detailed statistics grouped by hash, function, file, and error type.

#### Search Errors
```http
GET /debug/errors/search?error_type=ValueError&function_name=validate
```
Search errors with filters for type, function, file, or hash.

### Using Enhanced Error Handling

#### Decorator for Functions
```python
from src.utils.enhanced_error_handler import enhanced_exception_handler

@enhanced_exception_handler(context={"service": "MyService"})
def my_function():
    # Your code here
    pass
```

#### Context Manager for Blocks
```python
from src.utils.enhanced_error_handler import enhanced_error_context

def another_function():
    with enhanced_error_context("my_operation") as block_hash:
        # Code that might raise exceptions
        risky_operation()
```

#### Manual Error Logging
```python
from src.utils.enhanced_error_handler import log_error_with_hash

log_error_with_hash(
    error=exception,
    block_hash="abc123def456",
    context={"additional": "context"},
    request_data=request_dict
)
```

## 📋 General Debug Logging System

### Automatic Error Logging
- All errors are automatically logged to `logs/errors/errors_YYYY-MM-DD.jsonl`
- Daily log rotation for easy management
- JSON Lines format for machine-readable analysis
- Full stack traces and request/response data captured

### General Error Log Format
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

### Debug Endpoints for General Logging

#### Recent General Errors
```http
GET /debug/errors/recent?count=5
```
View recent general errors with correlation IDs.

#### Specific Error Lookup
```http
GET /debug/errors/{correlation_id}
```
Find specific error by correlation ID.

#### General Error Statistics
```http
GET /debug/errors/stats
```
General error statistics and trends.

#### Log Cleanup
```http
POST /debug/errors/cleanup?days_to_keep=7
```
Clean up old general error logs.

## 🔧 Configuration

### Environment Variables
```bash
# Enhanced error handling directory (default: logs/debug)
ENHANCED_ERROR_LOG_DIR=logs/debug

# General error logging directory (default: logs/errors)
ERROR_LOG_DIR=logs/errors

# Enable/disable enhanced error handling (default: true)
ENHANCED_ERROR_HANDLING_ENABLED=true
```

### Programmatic Configuration
```python
from src.utils.enhanced_error_handler import initialize_enhanced_error_handler
from src.utils.error_logger import initialize_error_logger

# Initialize enhanced error handler
handler = initialize_enhanced_error_handler("logs/debug")

# Initialize general error logger  
error_logger = initialize_error_logger("logs/errors")
```

## 🛠️ Usage Examples

### Quick Debug Check Script
```bash
# Check recent general errors
python check_debug_logs.py

# Check specific error by correlation ID
python check_debug_logs.py f81f3942-5199-4f3d-940f-f362c54c5c1c_continuation

# Check enhanced errors by hash
curl http://localhost:4000/debug/errors/hash/abc123def456
```

### Manual API Investigation
```bash
# Get recent enhanced errors
curl http://localhost:4000/debug/errors/enhanced/recent?count=5 | jq .

# Get recent general errors
curl http://localhost:4000/debug/errors/recent?count=5 | jq .

# Search for specific error patterns
curl "http://localhost:4000/debug/errors/search?error_type=ValueError" | jq .

# Get server instance information
curl http://localhost:4000/debug/server/instance | jq .
```

### Direct File Access
```bash
# View today's general errors
cat logs/errors/errors_$(date +%Y-%m-%d).jsonl | jq .

# View enhanced errors for a specific server instance
ls logs/debug/server_*/errors_*.jsonl
cat logs/debug/server_a1b2c3d4/errors_*.jsonl | jq .

# Search for correlation ID across all logs
grep "f81f3942-5199-4f3d-940f-f362c54c5c1c" logs/errors/*.jsonl
grep "f81f3942-5199-4f3d-940f-f362c54c5c1c" logs/debug/server_*/errors_*.jsonl
```

## 🐛 Debug Workflow

### When You See an Error

1. **Note the Error Details**
   ```
   2025-06-01 16:42:11,426 - openrouter_proxy - ERROR - ❌ Message creation failed
   Request ID: f81f3942-5199-4f3d-940f-f362c54c5c1c_continuation
   Error Block Hash: abc123def456
   ```

2. **Choose Your Investigation Method**:

   **For Code-Level Debugging (Enhanced System)**:
   ```bash
   # Use the error block hash to find exact code location
   curl http://localhost:4000/debug/errors/hash/abc123def456
   ```

   **For Request-Level Debugging (General System)**:
   ```bash
   # Use correlation ID to find request details
   curl http://localhost:4000/debug/errors/f81f3942-5199-4f3d-940f-f362c54c5c1c_continuation
   ```

3. **Analyze the Results**:
   - **Enhanced logs**: Exact file, function, line number + execution context
   - **General logs**: Full request/response data + stack traces

4. **Fix the Issue**: Use the comprehensive debugging information to identify and fix the root cause

## 🔍 Error Location Workflow

When you have an error block hash:

1. **Copy the hash** from the error log or console output
2. **Use the debug endpoint** to find the exact code location:
   ```bash
   curl http://localhost:4000/debug/errors/hash/{block_hash}
   ```
3. **Navigate to the file and line number** shown in the response
4. **Use the context information** to understand what was happening
5. **Check the enhanced error logs** for full execution details

## 🛡️ Security Features

- **API Key Masking**: All API keys are automatically masked in logs
- **Content Truncation**: Large messages truncated to prevent huge logs
- **Sensitive Data Sanitization**: Headers and request data sanitized
- **Development-Only Endpoints**: Debug endpoints only available in development mode
- **Server Instance Isolation**: Each server run has separate log directories

## 📊 Log System Comparison

| Feature              | Enhanced Error Handler (logs/debug/)           | Error Logger (logs/errors/)       |
| -------------------- | ---------------------------------------------- | --------------------------------- |
| **Purpose**          | Advanced debugging with code location tracking | General application error logging |
| **Hash Tracking**    | ✅ Unique hash for each error block             | ❌ No hash tracking                |
| **Server Instances** | ✅ Separate directories per server run          | ❌ Single file per day             |
| **Code Location**    | ✅ Exact file, function, line number            | ✅ Full stack traces               |
| **Lookup System**    | ✅ Hash-based debug endpoints                   | ❌ File-based search               |
| **Context Data**     | ✅ Execution context, request data              | ✅ Request/response data           |
| **Best For**         | Debugging specific code blocks                 | General error monitoring          |

Both systems are valuable and serve different purposes - they complement each other rather than duplicate functionality.

## 🔧 Maintenance

### Log Rotation and Cleanup

#### Enhanced Error Logs
- Logs are organized by server instance
- Each server run creates timestamped files
- Manual cleanup by removing old server instance directories

#### General Error Logs
- Automatically rotate daily
- Clean up old logs using API endpoint:
  ```bash
  curl -X POST http://localhost:4000/debug/errors/cleanup?days_to_keep=7
  ```

### Disk Space Management
- Enhanced logs: ~10-50KB per server instance
- General logs: 2-10KB per error entry
- Monitor `logs/` directory size regularly
- Configure retention periods based on needs

## 🚨 Troubleshooting

### No Enhanced Logs Found
- Check if enhanced error handling is enabled
- Verify server instance ID: `curl http://localhost:4000/debug/server/instance`
- Ensure `logs/debug/` directory exists and is writable

### No General Logs Found  
- Ensure server is running with proper configuration
- Check `ENVIRONMENT=development` for debug endpoints
- Verify `logs/errors/` directory exists

### Can't Access Debug Endpoints
- Only available in development mode
- Check server configuration and environment
- Ensure port 4000 is accessible
- Verify server is running

### Missing Error Block Hashes
- Hash generation happens when decorators/context managers are used
- Check that enhanced exception handling is properly applied to code
- Verify enhanced error handler is initialized

## 🎯 Best Practices

1. **Always Check Logs First**: Follow Critical Development Rule #3
2. **Use Both Systems**: Enhanced for code debugging, general for request monitoring  
3. **Track with IDs**: Use correlation IDs and error block hashes
4. **Monitor Patterns**: Use stats endpoints to identify trends
5. **Clean Up Regularly**: Manage disk space with proper retention
6. **Secure Production**: Disable debug endpoints in production
7. **Apply Enhanced Handling**: Use decorators and context managers in new code
8. **Document Error Blocks**: Add meaningful context to error handling blocks

## ✅ Quick Reference

### Most Common Commands
```bash
# Recent enhanced errors
curl http://localhost:4000/debug/errors/enhanced/recent?count=5

# Recent general errors  
curl http://localhost:4000/debug/errors/recent?count=5

# Find code location by hash
curl http://localhost:4000/debug/errors/hash/YOUR_HASH_HERE

# Find error by correlation ID
curl http://localhost:4000/debug/errors/YOUR_CORRELATION_ID_HERE

# Server instance info
curl http://localhost:4000/debug/server/instance

# Error statistics
curl http://localhost:4000/debug/errors/enhanced/stats
curl http://localhost:4000/debug/errors/stats
```

The enhanced error handling and debug logging systems provide comprehensive coverage for both development debugging and production monitoring needs. 