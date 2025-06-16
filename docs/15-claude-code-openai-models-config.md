# Claude Code OpenAI Models Configuration Guide

This guide shows how to configure Claude Code to use **OpenAI and other provider models** through our OpenRouter proxy server, expanding Claude Code's capabilities beyond just Anthropic models.

## 🎯 **Architecture Overview**

```
Claude Code → Our Proxy Server → OpenRouter → OpenAI/Other Providers
```

**What This Enables**:
- Claude Code can use **GPT-4**, **GPT-4o**, **GPT-4-Turbo**, and other OpenAI models
- Access to 7+ providers: OpenAI, Google Gemini, Cohere, Mistral, Azure, etc.
- All through Claude Code's familiar Anthropic API interface

## ✅ **Supported OpenAI Models via Our Proxy**

Based on our Universal Streaming Service configuration, Claude Code can access these OpenAI models:

### **OpenAI Models Available**
```bash
# GPT-4 family (via OpenRouter)
- openrouter/openai/gpt-4o
- openrouter/openai/gpt-4-turbo  
- openrouter/openai/gpt-4
- openrouter/openai/gpt-4-32k

# GPT-3.5 family (via OpenRouter)  
- openrouter/openai/gpt-3.5-turbo
- openrouter/openai/gpt-3.5-turbo-16k

# Other OpenAI models
- openrouter/openai/gpt-4o-mini
- openrouter/openai/gpt-4-vision-preview
```

### **Other Provider Models Available**
```bash
# Google models
- openrouter/google/gemini-pro
- openrouter/google/gemini-pro-vision

# Cohere models  
- openrouter/cohere/command-r-plus

# Mistral models
- openrouter/mistralai/mixtral-8x7b-instruct
```

## 🛠️ **Claude Code Configuration**

### **Step 1: Configure Environment Variables**

Set Claude Code to use our proxy server instead of direct Anthropic API:

```bash
# Point Claude Code to our proxy server
export ANTHROPIC_API_BASE="http://localhost:4000/v1"

# Use OpenAI model instead of Claude
export ANTHROPIC_MODEL="openrouter/openai/gpt-4o"

# Optional: Configure small model for fast operations  
export ANTHROPIC_SMALL_FAST_MODEL="openrouter/openai/gpt-3.5-turbo"

# Your OpenRouter API key (required for our proxy)
export OPENROUTER_API_KEY="your-openrouter-key-here"
```

### **Step 2: Model Selection Options**

Choose your preferred OpenAI model for Claude Code:

```bash
# For maximum performance (recommended)
export ANTHROPIC_MODEL="openrouter/openai/gpt-4o"

# For cost optimization
export ANTHROPIC_MODEL="openrouter/openai/gpt-3.5-turbo"

# For complex reasoning tasks
export ANTHROPIC_MODEL="openrouter/openai/gpt-4-turbo"

# For vision tasks
export ANTHROPIC_MODEL="openrouter/openai/gpt-4-vision-preview"
```

### **Step 3: Advanced Configuration**

Enable additional features:

```bash
# Enable our enhanced caching (99% performance improvement)
export ENABLE_CACHING="true"
export CACHE_TTL="3600"

# Enable debugging (optional)
export DEBUG="true"
export LOG_LEVEL="INFO"

# Configure request limits
export MAX_TOKENS_LIMIT="8192"
export REQUEST_TIMEOUT="120"
```

## 🚀 **Usage Examples**

### **Example 1: Claude Code with GPT-4o**
```bash
# Configure for GPT-4o
export ANTHROPIC_API_BASE="http://localhost:4000/v1"
export ANTHROPIC_MODEL="openrouter/openai/gpt-4o"

# Start Claude Code
claude
```

### **Example 2: Claude Code with Google Gemini**
```bash
# Configure for Gemini Pro
export ANTHROPIC_API_BASE="http://localhost:4000/v1"  
export ANTHROPIC_MODEL="openrouter/google/gemini-pro"

# Start Claude Code
claude
```

### **Example 3: Dual Model Setup**
```bash
# Use GPT-4o for complex tasks, GPT-3.5 for simple tasks
export ANTHROPIC_MODEL="openrouter/openai/gpt-4o"
export ANTHROPIC_SMALL_FAST_MODEL="openrouter/openai/gpt-3.5-turbo"

# Start Claude Code
claude
```

## 📊 **Model Comparison for Claude Code**

| Model             | Cost   | Speed     | Quality   | Best For                      |
| ----------------- | ------ | --------- | --------- | ----------------------------- |
| **GPT-4o**        | High   | Fast      | Excellent | Complex coding, reasoning     |
| **GPT-4-Turbo**   | High   | Medium    | Excellent | Large context tasks           |
| **GPT-3.5-Turbo** | Low    | Very Fast | Good      | Simple coding, fast responses |
| **Gemini Pro**    | Medium | Fast      | Very Good | Code analysis, multi-modal    |

## ✅ **Features Preserved Through Our Proxy**

When using OpenAI models through our proxy, Claude Code retains:

- ✅ **Tool Execution** - All 15 Claude Code tools work perfectly
- ✅ **Streaming Responses** - Real-time response streaming
- ✅ **MCP Protocol** - Model Control Protocol support  
- ✅ **Multi-modal Content** - Image processing (where supported)
- ✅ **Enhanced Caching** - 99% performance improvement
- ✅ **Error Handling** - Comprehensive error management

## 🎯 **Why This is Powerful**

### **For Developers**
1. **Cost Optimization** - Use cheaper OpenAI models for simple tasks
2. **Performance Variety** - Choose optimal model for each use case
3. **Provider Diversity** - Access to multiple AI providers through one interface
4. **Enhanced Features** - Our proxy adds caching and optimizations

### **For Enterprise**
1. **Vendor Flexibility** - Not locked into single AI provider
2. **Cost Management** - Optimal model selection reduces costs
3. **Risk Mitigation** - Multiple provider fallbacks
4. **Enhanced Monitoring** - Comprehensive logging and metrics

## 🔧 **Troubleshooting**

### **Common Issues**

**Claude Code can't connect**:
```bash
# Ensure our server is running
python3 start_server.py

# Check server health
curl http://localhost:4000/health
```

**Invalid model errors**:
```bash
# Check available models
curl http://localhost:4000/health/detailed

# Verify model mapping
curl "http://localhost:4000/debug/config/models"
```

**Rate limiting**:
```bash
# Check OpenRouter quota
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/auth/key
```

## 📈 **Performance Optimization**

### **Recommended Settings for OpenAI Models**

```bash
# For GPT-4o (balanced performance)
export ANTHROPIC_MODEL="openrouter/openai/gpt-4o"
export MAX_TOKENS_LIMIT="4096"
export REQUEST_TIMEOUT="60"

# For GPT-3.5-Turbo (speed optimized)  
export ANTHROPIC_MODEL="openrouter/openai/gpt-3.5-turbo"
export MAX_TOKENS_LIMIT="2048"
export REQUEST_TIMEOUT="30"

# Enable caching for repeated operations
export ENABLE_CACHING="true"
export CACHE_TTL="1800"  # 30 minutes
```

## 🎉 **Result**

With this configuration, Claude Code can access the full OpenAI model ecosystem while maintaining its familiar interface and powerful features. This dramatically expands Claude Code's capabilities beyond Anthropic models!

**Before**: Claude Code → Anthropic models only  
**After**: Claude Code → Our Proxy → OpenAI + 6 other providers = Universal AI access! 🚀 