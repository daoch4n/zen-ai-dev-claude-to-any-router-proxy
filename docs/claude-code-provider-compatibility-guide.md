# Claude Code LLM Provider Compatibility Verification Guide

## 📋 Overview

This comprehensive guide helps you verify if LLM service providers can support Claude Code CLI features, from basic messaging to advanced capabilities like tool execution, streaming, and prompt caching. Even providers with Anthropic API endpoints may have limitations that affect Claude Code functionality.

**Referenced Documentation:**
- [Claude Code Tutorials](https://docs.anthropic.com/en/docs/claude-code/tutorials)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Claude Code Official](https://www.anthropic.com/claude-code)

## 🎯 Claude Code Requirements Overview

### Core Features Claude Code Expects

Based on [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code/tutorials), Claude Code requires:

1. **Anthropic Messages API Compatibility** (`/v1/messages`)
2. **Tool Execution Framework** (15+ tools)
3. **Streaming Responses** with tool execution during streaming
4. **Multi-modal Content** support (images, files)
5. **Advanced Reasoning** capabilities
6. **Prompt Caching** for performance
7. **Error Handling** and recovery mechanisms

## 🧪 Provider Compatibility Testing Framework

### Phase 1: Basic API Compatibility

#### 1.1 Anthropic API Endpoint Verification

```bash
# Test basic messages endpoint
curl -X POST "https://[provider-endpoint]/v1/messages" \
  -H "Authorization: Bearer [api-key]" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-haiku-20240307",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**Expected Response Format:**
```json
{
  "id": "msg_xxx",
  "type": "message",
  "role": "assistant",
  "content": [{"type": "text", "text": "Hello! How can I help you?"}],
  "model": "claude-3-haiku-20240307",
  "usage": {"input_tokens": 8, "output_tokens": 12}
}
```

**Compatibility Levels:**
- ✅ **Full Support**: Perfect Anthropic API format
- ⚠️ **Partial Support**: Minor format differences
- ❌ **No Support**: Different API format entirely

#### 1.2 Model Support Verification

```bash
# Test Claude 4 support
curl -X POST "https://[provider-endpoint]/v1/messages" \
  -H "Authorization: Bearer [api-key]" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "What model are you?"}]
  }'
```

**Model Compatibility Matrix:**

| Provider         | Claude 4 | Claude 3.5 | Claude 3 | Model Aliases |
| ---------------- | -------- | ---------- | -------- | ------------- |
| Anthropic Direct | ✅        | ✅          | ✅        | ✅             |
| OpenRouter       | ✅        | ✅          | ✅        | ⚠️             |
| Azure Databricks | ✅        | ⚠️          | ⚠️        | ❌             |
| LiteLLM          | ✅        | ✅          | ✅        | ✅             |

### Phase 2: Streaming Capabilities

#### 2.1 Basic Streaming Test

```bash
# Test streaming response
curl -X POST "https://[provider-endpoint]/v1/messages" \
  -H "Authorization: Bearer [api-key]" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-haiku-20240307",
    "max_tokens": 200,
    "stream": true,
    "messages": [{"role": "user", "content": "Write a short story"}]
  }'
```

**Expected Streaming Format:**
```
data: {"type": "message_start", "message": {...}}
data: {"type": "content_block_start", "index": 0, "content_block": {...}}
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Once"}}
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": " upon"}}
data: [DONE]
```

**Streaming Compatibility:**
- ✅ **Full Support**: Proper SSE format with all event types
- ⚠️ **Basic Support**: Streaming works but may lack proper event types
- ❌ **No Support**: No streaming or incorrect format

#### 2.2 Advanced Streaming with Tools

According to [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices), Claude Code requires tool execution during streaming:

```bash
# Test streaming with tool use
curl -X POST "https://[provider-endpoint]/v1/messages" \
  -H "Authorization: Bearer [api-key]" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 1000,
    "stream": true,
    "tools": [
      {
        "name": "create_file",
        "description": "Create a new file",
        "input_schema": {
          "type": "object",
          "properties": {
            "filename": {"type": "string"},
            "content": {"type": "string"}
          }
        }
      }
    ],
    "messages": [{"role": "user", "content": "Create a hello.py file"}]
  }'
```

### Phase 3: Tool Execution Framework

#### 3.1 Tool Definition Support

Claude Code expects providers to support the full Anthropic tools schema:

```json
{
  "tools": [
    {
      "name": "str_replace_editor",
      "description": "String replacement based file editor",
      "input_schema": {
        "type": "object",
        "properties": {
          "command": {
            "type": "string",
            "enum": ["str_replace", "create", "view"]
          },
          "path": {"type": "string"},
          "file_text": {"type": "string"},
          "old_str": {"type": "string"},
          "new_str": {"type": "string"}
        }
      }
    }
  ]
}
```

#### 3.2 Tool Use Response Format

**Expected Tool Use Response:**
```json
{
  "content": [
    {
      "type": "tool_use",
      "id": "tool_call_123",
      "name": "str_replace_editor", 
      "input": {
        "command": "create",
        "path": "hello.py",
        "file_text": "print('Hello World')"
      }
    }
  ]
}
```

#### 3.3 Tool Result Handling

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "tool_call_123",
      "content": "File created successfully"
    }
  ]
}
```

**Tool Compatibility Test:**

| Feature                | Test Method           | Expected Result        |
| ---------------------- | --------------------- | ---------------------- |
| Tool Definition        | Send tools array      | Accepts without error  |
| Tool Use Generation    | Request file creation | Returns tool_use block |
| Tool Result Processing | Send tool_result      | Continues conversation |
| Complex Tool Chains    | Multi-step workflow   | Maintains context      |

### Phase 4: Advanced Features

#### 4.1 Prompt Caching Support

Based on [Claude Code tutorials](https://docs.anthropic.com/en/docs/claude-code/tutorials), prompt caching is crucial for performance:

```bash
# Test prompt caching
curl -X POST "https://[provider-endpoint]/v1/messages" \
  -H "Authorization: Bearer [api-key]" \
  -H "Content-Type: application/json" \
  -H "anthropic-beta: prompt-caching-2024-07-31" \
  -d '{
    "model": "claude-3-haiku-20240307",
    "max_tokens": 100,
    "system": [
      {
        "type": "text",
        "text": "You are an expert programmer. Here is the codebase context...",
        "cache_control": {"type": "ephemeral"}
      }
    ],
    "messages": [{"role": "user", "content": "Explain this code"}]
  }'
```

**Caching Support Levels:**
- ✅ **Full Support**: Supports `anthropic-beta` header and `cache_control`
- ⚠️ **Partial Support**: Basic caching without fine-grained control
- ❌ **No Support**: No caching capabilities

#### 4.2 Multi-modal Content

```bash
# Test image support
curl -X POST "https://[provider-endpoint]/v1/messages" \
  -H "Authorization: Bearer [api-key]" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 300,
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "What do you see in this image?"},
          {
            "type": "image",
            "source": {
              "type": "base64",
              "media_type": "image/png",
              "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            }
          }
        ]
      }
    ]
  }'
```

#### 4.3 Extended Thinking Modes

From [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices), test thinking capabilities:

```bash
# Test thinking mode
curl -X POST "https://[provider-endpoint]/v1/messages" \
  -H "Authorization: Bearer [api-key]" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 1000,
    "messages": [
      {"role": "user", "content": "Think hard about implementing a distributed cache system. Consider all architectural trade-offs."}
    ]
  }'
```

## 📊 Provider Compatibility Matrix

### Comprehensive Feature Support

| Feature             | Anthropic Direct | OpenRouter | Azure Databricks | LiteLLM | AWS Bedrock |
| ------------------- | ---------------- | ---------- | ---------------- | ------- | ----------- |
| **Basic Messaging** | ✅                | ✅          | ✅                | ✅       | ✅           |
| **Streaming**       | ✅                | ✅          | ⚠️                | ✅       | ⚠️           |
| **Tool Definition** | ✅                | ✅          | ⚠️                | ✅       | ❌           |
| **Tool Execution**  | ✅                | ✅          | ❌                | ✅       | ❌           |
| **Prompt Caching**  | ✅                | ⚠️          | ❌                | ⚠️       | ❌           |
| **Multi-modal**     | ✅                | ✅          | ⚠️                | ✅       | ⚠️           |
| **Beta Features**   | ✅                | ❌          | ❌                | ⚠️       | ❌           |
| **Model Aliases**   | ✅                | ⚠️          | ❌                | ✅       | ❌           |
| **Error Handling**  | ✅                | ✅          | ⚠️                | ✅       | ⚠️           |

**Legend:**
- ✅ **Full Support**: Complete compatibility
- ⚠️ **Partial Support**: Works with limitations
- ❌ **No Support**: Feature unavailable

### Provider-Specific Limitations

#### OpenRouter
- ✅ **Strengths**: Good API compatibility, multiple models
- ⚠️ **Limitations**: 
  - Limited prompt caching support
  - Some beta features unavailable
  - Model alias mapping may differ

#### Azure Databricks
- ✅ **Strengths**: Enterprise security, managed infrastructure
- ⚠️ **Limitations**:
  - Tool execution not supported
  - Limited streaming capabilities
  - No prompt caching
  - Frequent 503 Service Unavailable errors
  - Custom model endpoint names

#### LiteLLM
- ✅ **Strengths**: Multi-provider abstraction, good tooling
- ⚠️ **Limitations**:
  - Additional abstraction layer complexity
  - Some advanced features may be proxied incorrectly
  - Performance overhead

## 🧪 Automated Testing Script

### Comprehensive Provider Test

```bash
#!/bin/bash
# claude-code-provider-test.sh

PROVIDER_URL="$1"
API_KEY="$2"
PROVIDER_NAME="$3"

echo "🧪 Testing Claude Code compatibility for: $PROVIDER_NAME"
echo "📍 Endpoint: $PROVIDER_URL"

# Test 1: Basic Messages
echo "1️⃣ Testing basic messages..."
BASIC_RESPONSE=$(curl -s -X POST "$PROVIDER_URL/v1/messages" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-haiku-20240307",
    "max_tokens": 50,
    "messages": [{"role": "user", "content": "Hello"}]
  }')

if echo "$BASIC_RESPONSE" | jq -e '.content[0].text' > /dev/null; then
  echo "✅ Basic messaging: PASS"
else
  echo "❌ Basic messaging: FAIL"
fi

# Test 2: Streaming
echo "2️⃣ Testing streaming..."
STREAM_RESPONSE=$(curl -s -X POST "$PROVIDER_URL/v1/messages" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-haiku-20240307",
    "max_tokens": 50,
    "stream": true,
    "messages": [{"role": "user", "content": "Count to 5"}]
  }')

if echo "$STREAM_RESPONSE" | grep -q "data: "; then
  echo "✅ Streaming: PASS"
else
  echo "❌ Streaming: FAIL"
fi

# Test 3: Tool Support
echo "3️⃣ Testing tool support..."
TOOL_RESPONSE=$(curl -s -X POST "$PROVIDER_URL/v1/messages" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 200,
    "tools": [
      {
        "name": "test_tool",
        "description": "A test tool",
        "input_schema": {
          "type": "object",
          "properties": {
            "input": {"type": "string"}
          }
        }
      }
    ],
    "messages": [{"role": "user", "content": "Use the test tool with input hello"}]
  }')

if echo "$TOOL_RESPONSE" | jq -e '.content[] | select(.type == "tool_use")' > /dev/null; then
  echo "✅ Tool support: PASS"
else
  echo "❌ Tool support: FAIL"
fi

# Test 4: Prompt Caching
echo "4️⃣ Testing prompt caching..."
CACHE_RESPONSE=$(curl -s -X POST "$PROVIDER_URL/v1/messages" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "anthropic-beta: prompt-caching-2024-07-31" \
  -d '{
    "model": "claude-3-haiku-20240307",
    "max_tokens": 50,
    "system": [
      {
        "type": "text",
        "text": "You are a helpful assistant.",
        "cache_control": {"type": "ephemeral"}
      }
    ],
    "messages": [{"role": "user", "content": "Hello"}]
  }')

if echo "$CACHE_RESPONSE" | jq -e '.usage.cache_creation_input_tokens' > /dev/null; then
  echo "✅ Prompt caching: PASS"
else
  echo "⚠️ Prompt caching: LIMITED/UNSUPPORTED"
fi

echo "🏁 Testing complete for $PROVIDER_NAME"
```

## 🛠️ Troubleshooting Common Issues

### Issue 1: Tool Use Not Working

**Symptoms:**
- Provider accepts tool definitions but never generates tool_use
- Returns text responses instead of tool calls

**Diagnosis:**
```bash
# Test with explicit tool instruction
curl -X POST "https://[provider]/v1/messages" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 200,
    "tools": [...],
    "messages": [
      {"role": "user", "content": "You MUST use the create_file tool to create hello.py"}
    ]
  }'
```

**Solutions:**
- Check if provider supports Anthropic tools format
- Verify model supports tool use
- Use more explicit tool instructions

### Issue 2: Streaming Interruption

**Symptoms:**
- Streaming stops mid-response
- Empty responses with 200 status
- JSON decode errors

**Diagnosis:**
```bash
# Check streaming format
curl -N -X POST "https://[provider]/v1/messages" \
  -H "stream: true" \
  -d '{...}' | head -20
```

**Solutions:**
- Verify provider supports Server-Sent Events
- Check for rate limiting
- Implement retry logic

### Issue 3: Model Mapping Issues

**Symptoms:**
- "Model not found" errors
- Unexpected model responses

**Diagnosis:**
```bash
# Test available models
curl "https://[provider]/v1/models" \
  -H "Authorization: Bearer [key]"
```

**Solutions:**
- Use provider-specific model names
- Implement model mapping layer
- Check provider documentation for supported models

## 📈 Performance Benchmarks

### Response Time Expectations

| Feature          | Anthropic Direct | Good Provider | Poor Provider |
| ---------------- | ---------------- | ------------- | ------------- |
| Simple Message   | <2s              | <3s           | >5s           |
| Streaming Start  | <500ms           | <1s           | >2s           |
| Tool Execution   | <1s              | <2s           | >5s           |
| Image Processing | <3s              | <5s           | >10s          |

### Reliability Metrics

| Metric       | Excellent | Good  | Poor |
| ------------ | --------- | ----- | ---- |
| Uptime       | >99.9%    | >99%  | <99% |
| Error Rate   | <0.1%     | <1%   | >5%  |
| Timeout Rate | <0.01%    | <0.1% | >1%  |

## 🎯 Recommendation Framework

### Provider Selection Guide

#### For Full Claude Code Support
1. **Anthropic Direct** - Gold standard
2. **LiteLLM with Anthropic** - Good abstraction layer
3. **OpenRouter** - Good compatibility with minor limitations

#### For Basic Claude Code Support
1. **Azure Databricks** - Enterprise features but limited tools
2. **AWS Bedrock** - Good for basic messaging, limited advanced features

#### For Development/Testing
1. **Local proxy server** - Full control and debugging
2. **OpenRouter** - Good model variety for testing

### Migration Strategy

#### From Limited Provider to Full Support

1. **Assessment Phase**
   - Run compatibility tests
   - Identify missing features
   - Document limitations

2. **Implementation Phase**
   - Set up compatible provider
   - Implement feature mapping
   - Add fallback mechanisms

3. **Validation Phase**
   - Run full Claude Code test suite
   - Performance benchmarking
   - User acceptance testing

## 📋 Conclusion

Provider compatibility with Claude Code varies significantly. While basic messaging may work across providers, advanced features like tool execution, prompt caching, and streaming require careful validation. Use this guide to systematically test and verify provider capabilities before committing to a solution.

**Key Takeaways:**
- Not all Anthropic API endpoints are equal
- Tool execution is a major differentiator
- Streaming quality varies significantly
- Performance benchmarking is essential
- Always test with real Claude Code workflows

For optimal Claude Code experience, choose providers that support the full feature set outlined in the [official Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code/tutorials). 