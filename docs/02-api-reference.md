# API Reference

## OpenRouter Anthropic Server v2.0 - Complete API Documentation

This document provides comprehensive API reference for the OpenRouter Anthropic Server v2.0.

## 🌐 Base URL

```
Production: https://your-domain.com
Development: http://localhost:4000
```

## 🔑 Authentication

The server acts as a proxy to OpenRouter, so no direct authentication is required from clients. The server handles OpenRouter API authentication internally.

## 📋 API Endpoints

### 1. Messages API

#### Create Message
Create a new message using the Anthropic Messages API format.

**Endpoint:** `POST /v1/messages`

**Request Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
  "model": "anthropic/claude-sonnet-4",
  "max_tokens": 1000,
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "system": "You are a helpful assistant.",
  "tools": [
    {
      "name": "get_weather",
      "description": "Get weather information",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {"type": "string"}
        },
        "required": ["location"]
      }
    }
  ],
  "tool_choice": {"type": "auto"},
  "temperature": 0.7,
  "top_p": 0.9,
  "stream": false
}
```

**Request Parameters:**

| Parameter     | Type         | Required | Description                                         |
| ------------- | ------------ | -------- | --------------------------------------------------- |
| `model`       | string       | ✅        | Model identifier (supports aliases: "big", "small") |
| `max_tokens`  | integer      | ✅        | Maximum tokens to generate                          |
| `messages`    | array        | ✅        | Array of message objects                            |
| `system`      | string/array | ❌        | System message or array of system content           |
| `tools`       | array        | ❌        | Available tools for the model                       |
| `tool_choice` | object       | ❌        | Tool choice configuration                           |
| `temperature` | number       | ❌        | Sampling temperature (0.0-1.0)                      |
| `top_p`       | number       | ❌        | Nucleus sampling parameter                          |
| `stream`      | boolean      | ❌        | Enable streaming responses                          |

**Message Object:**
```json
{
  "role": "user|assistant|system",
  "content": "string or array of content blocks"
}
```

**Content Block Types:**
```json
// Text content
{
  "type": "text",
  "text": "Hello world"
}

// Tool use
{
  "type": "tool_use",
  "id": "tool_123",
  "name": "get_weather",
  "input": {"location": "San Francisco"}
}

// Tool result
{
  "type": "tool_result",
  "tool_use_id": "tool_123",
  "content": "Weather data here"
}
```

**Success Response (200):**
```json
{
  "id": "msg_01234567890abcdef",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Hello! I'm doing well, thank you for asking."
    }
  ],
  "model": "anthropic/claude-sonnet-4",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 10,
    "output_tokens": 15,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0
  }
}
```

**Error Response (400):**
```json
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "Request validation failed: messages -> 0 -> content: Content cannot be empty"
  }
}
```

#### Create Streaming Message
Create a streaming message response.

**Endpoint:** `POST /v1/messages/stream`

Same request format as `/v1/messages` but returns Server-Sent Events (SSE) stream.

**Response Format:**
```
data: {"type": "message_start", "message": {...}}

data: {"type": "content_block_start", "index": 0, "content_block": {...}}

data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hello"}}

data: {"type": "content_block_stop", "index": 0}

data: {"type": "message_delta", "delta": {"stop_reason": "end_turn", "usage": {...}}}

data: {"type": "message_stop"}
```

### 2. Token Counting API

#### Count Tokens
Count tokens in a message without generating a response.

**Endpoint:** `POST /v1/messages/count_tokens`

**Request Body:**
```json
{
  "model": "anthropic/claude-sonnet-4",
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "system": "You are a helpful assistant.",
  "tools": []
}
```

**Success Response (200):**
```json
{
  "input_tokens": 25,
  "output_tokens": 0
}
```

### 3. Health Check API

#### Basic Health Check
Check if the server is running.

**Endpoint:** `GET /health`

**Success Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Detailed Health Check
Get detailed server health information.

**Endpoint:** `GET /health/detailed`

**Success Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "2.0.0",
  "environment": "production",
  "services": {
    "openrouter_api": "healthy",
    "instructor": "healthy",
    "validation": "healthy"
  },
  "configuration": {
    "instructor_enabled": true,
    "debug_enabled": false,
    "model_mapping": {
      "big": "anthropic/claude-sonnet-4",
      "small": "anthropic/claude-3.7-sonnet"
    }
  }
}
```

#### Root Endpoint
Basic server information.

**Endpoint:** `GET /`

**Success Response (200):**
```json
{
  "name": "OpenRouter Anthropic Server",
  "version": "2.0.0",
  "status": "running",
  "documentation": "/docs"
}
```

#### Status Endpoint
Simple status check.

**Endpoint:** `GET /status`

**Success Response (200):**
```json
{
  "status": "ok"
}
```

## 🔧 Model Mapping

The server supports model aliases for convenience:

| Alias   | Maps To                       | Description             |
| ------- | ----------------------------- | ----------------------- |
| `big`   | `anthropic/claude-sonnet-4`   | Latest large model      |
| `small` | `anthropic/claude-3.7-sonnet` | Efficient smaller model |

**Example:**
```json
{
  "model": "big",  // Automatically mapped to anthropic/claude-sonnet-4
  "messages": [...]
}
```

## 🛠️ Advanced Features

### Tool Calling
The server supports Anthropic's tool calling format:

```json
{
  "model": "anthropic/claude-sonnet-4",
  "max_tokens": 1000,
  "messages": [
    {
      "role": "user",
      "content": "What's the weather in San Francisco?"
    }
  ],
  "tools": [
    {
      "name": "get_weather",
      "description": "Get current weather information",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City name"
          }
        },
        "required": ["location"]
      }
    }
  ]
}
```

### Structured Outputs
The server uses Instructor for enhanced structured outputs and validation.

### Request Validation
All requests are validated using:
- Message format validation
- Conversation flow validation
- Tool definition validation
- Content validation

## 📊 Response Headers

All responses include these headers:

| Header                          | Description               |
| ------------------------------- | ------------------------- |
| `X-Request-ID`                  | Unique request identifier |
| `X-Processing-Time`             | Request processing time   |
| `Access-Control-Expose-Headers` | CORS exposed headers      |

## ❌ Error Handling

### Error Response Format
All errors follow Anthropic's error format:

```json
{
  "type": "error",
  "error": {
    "type": "error_type",
    "message": "Human readable error message"
  }
}
```

### Error Types

| Error Type              | Status Code | Description                          |
| ----------------------- | ----------- | ------------------------------------ |
| `invalid_request_error` | 400         | Invalid request format or parameters |
| `authentication_error`  | 401         | Authentication failed                |
| `permission_error`      | 403         | Insufficient permissions             |
| `not_found_error`       | 404         | Resource not found                   |
| `rate_limit_error`      | 429         | Rate limit exceeded                  |
| `api_error`             | 500         | Internal server error                |
| `overloaded_error`      | 503         | Server overloaded                    |

### Common Error Scenarios

#### Invalid Message Format
```json
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "Invalid message format: Content cannot be empty"
  }
}
```

#### Missing Required Fields
```json
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "Request validation failed: max_tokens: Field required"
  }
}
```

#### Tool Validation Error
```json
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "Invalid tool definition: Tool name is required"
  }
}
```

## 🔄 Rate Limiting

The server respects OpenRouter's rate limits and implements:
- Request queuing
- Automatic retry with exponential backoff
- Rate limit headers forwarding

## 📈 Performance

### Optimization Features
- Request/response caching
- Connection pooling
- Async processing
- Structured logging
- Performance monitoring

### Monitoring Endpoints
- Health checks for monitoring systems
- Metrics collection via middleware
- Request tracing with unique IDs

## 🧪 Testing

### Example Requests

#### Basic Chat
```bash
curl -X POST http://localhost:4000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-sonnet-4",
    "max_tokens": 100,
    "messages": [
      {
        "role": "user",
        "content": "Hello!"
      }
    ]
  }'
```

#### With Tools
```bash
curl -X POST http://localhost:4000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "big",
    "max_tokens": 1000,
    "messages": [
      {
        "role": "user",
        "content": "What is the weather like in Paris?"
      }
    ],
    "tools": [
      {
        "name": "get_weather",
        "description": "Get weather information",
        "input_schema": {
          "type": "object",
          "properties": {
            "location": {"type": "string"}
          },
          "required": ["location"]
        }
      }
    ]
  }'
```

#### Token Counting
```bash
curl -X POST http://localhost:4000/v1/messages/count_tokens \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-sonnet-4",
    "messages": [
      {
        "role": "user",
        "content": "Count the tokens in this message"
      }
    ]
  }'
```

#### Health Check
```bash
curl http://localhost:4000/health
```

## 📚 SDK Examples

### Python
```python
import requests

def create_message(content: str, model: str = "big"):
    response = requests.post(
        "http://localhost:4000/v1/messages",
        json={
            "model": model,
            "max_tokens": 1000,
            "messages": [
                {"role": "user", "content": content}
            ]
        }
    )
    return response.json()

# Usage
result = create_message("Hello, how are you?")
print(result["content"][0]["text"])
```

### JavaScript
```javascript
async function createMessage(content, model = "big") {
  const response = await fetch("http://localhost:4000/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: model,
      max_tokens: 1000,
      messages: [
        { role: "user", content: content }
      ]
    })
  });
  
  return await response.json();
}

// Usage
createMessage("Hello, how are you?")
  .then(result => console.log(result.content[0].text));
```

### cURL Scripts
```bash
#!/bin/bash
# chat.sh - Simple chat script

CONTENT="$1"
MODEL="${2:-big}"

curl -s -X POST http://localhost:4000/v1/messages \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"max_tokens\": 1000,
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": \"$CONTENT\"
      }
    ]
  }" | jq -r '.content[0].text'
```

## 🔍 Debugging

### Debug Headers
When debug mode is enabled, responses include additional debug information:

```json
{
  "debug": {
    "request_id": "12345",
    "processing_time": 0.123,
    "model_mapping": {
      "original": "big",
      "mapped": "anthropic/claude-sonnet-4"
    }
  }
}
```

### Log Analysis
Server logs include structured information for debugging:
- Request/response correlation IDs
- Processing times
- Validation results
- Error details

## 📞 Support

For API issues:
1. Check the health endpoint
2. Verify request format against examples
3. Review error messages for specific issues
4. Check server logs for detailed error information

## 🔄 Changelog

### v2.0.0
- Complete modular architecture
- Enhanced error handling
- Instructor integration for structured outputs
- Comprehensive validation
- Model mapping support
- Tool calling support
- Streaming responses
- Production-ready deployment