# Claude Code LiteLLM Proxy

A simple proxy setup that enables Claude Code to work with various LLM providers (like OpenRouter) using LiteLLM's beta `/v1/messages` endpoint.

## 🚀 Quick Start

```bash
uv venv
source .venv/bin/activate

uv sync
uv pip install 'litellm[proxy]'

# Set your API key (e.g., for OpenRouter)
export OPENROUTER_API_KEY="your-api-key-here"

# Start the LiteLLM proxy server
litellm --config ./configs/litellm_config.yaml

# Use Claude Code with the proxy (in another terminal)
./claude-no-proxy "Hello, test the proxy!"
```

- Claude Code output:
```
> Hello, test the proxy!

● I need more information to test a proxy. Could you provide details about:

  - What type of proxy you want to test (HTTP, SOCKS, etc.)
  - The proxy server address and port
  - What you want to test (connectivity, performance, functionality)
```


## ✨ What This Does

This setup allows you to:
- Use Claude Code with **any LLM provider** supported by LiteLLM
- Route requests through **OpenRouter**, **Azure**, **AWS Bedrock**, and more
- Maintain Claude Code's native functionality while using different models
- Avoid proxy conflicts with the included `claude-no-proxy` script
- Leverage LiteLLM's [Anthropic unified `/v1/messages` endpoint](https://docs.litellm.ai/docs/anthropic_unified) for seamless integration

## 🔧 Setup

### 1. Install Dependencies
```bash
# Install latest LiteLLM with beta features support
uv add "litellm>=1.72.6"
uv pip install 'litellm[proxy]'
```

### 2. Configure Your LiteLLM Config
Edit `./configs/litellm_config.yaml` to configure your preferred LLM provider and models.

### 3. Set Environment Variables
```bash
# For OpenRouter
export OPENROUTER_API_KEY="your-openrouter-api-key"

# For other providers, set the appropriate API keys
# export OPENAI_API_KEY="your-openai-key"
# export ANTHROPIC_API_KEY="your-anthropic-key"
# etc.
```

### 4. Start the Proxy
```bash
litellm --config ./configs/litellm_config.yaml
```

The proxy will start on `http://localhost:4000` by default.

### 5. Use Claude Code
```bash
# Set Claude Code to use the proxy
export ANTHROPIC_BASE_URL=http://localhost:4000

# Use the no-proxy script to avoid conflicts
./claude-no-proxy "Your message here"
```

## 🛠️ Configuration

### LiteLLM Config
Configure your models and providers in `./configs/litellm_config.yaml`. See the [LiteLLM documentation](https://docs.litellm.ai/) for full configuration options.

### Claude No-Proxy Script
The `claude-no-proxy` script ensures no proxy environment variables interfere with Claude Code:

```bash
#!/bin/bash
# Unset all proxy-related environment variables
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy NO_PROXY no_proxy

# Run Claude Code with clean environment
exec claude "$@"
```

## 🔍 Supported Providers

Through LiteLLM, you can use:
- **OpenRouter** - Access to multiple models
- **OpenAI** - GPT models  
- **Anthropic** - Claude models (direct)
- **Azure OpenAI** - Enterprise Azure models
- **AWS Bedrock** - Amazon's model marketplace
- **Google AI** - Gemini and PaLM models
- **Cohere** - Command and Generate models
- And many more...

## 📊 Usage Examples

### Basic Chat
```bash
./claude-no-proxy "Explain how LiteLLM proxy works"
```

### Code Tasks
```bash
./claude-no-proxy "Create a Python function to calculate fibonacci numbers"
```

### File Operations (if your LiteLLM config supports tools)
```bash
./claude-no-proxy "Read the contents of config.yaml and explain it"
```

## 🐛 Troubleshooting

### Common Issues

**1. Invalid model name error**
```bash
  ⎿  API Error: 400 {"error":{"message":"400: {'error': 'completion: Invalid model name passed in 
     model=claude-sonnet-4-20250514'}","type":"None","param":"None","code":"400"}}
```

```
# Fix: Update your litellm_config.yaml with Claude Code desired model names
# Map the correct anthropic model names to the llm models you want to use

# Restart LiteLLM after updating config
litellm --config ./configs/litellm_config.yaml
```


## 🎯 Why This Approach?

This simplified setup:
- ✅ **Simple** - Just one proxy server, no complex architecture
- ✅ **Flexible** - Works with any LiteLLM-supported provider
- ✅ **Native** - Preserves Claude Code's full functionality
- ✅ **Reliable** - Uses LiteLLM's battle-tested proxy capabilities
- ✅ **Lightweight** - Minimal overhead and dependencies

## 📚 Documentation

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LiteLLM Proxy Server](https://docs.litellm.ai/docs/simple_proxy)
- [Anthropic Unified `/v1/messages` Endpoint](https://docs.litellm.ai/docs/anthropic_unified)
- [Supported Providers](https://docs.litellm.ai/docs/providers)


## 📄 License

MIT License

---

**Simple, effective LLM proxying for Claude Code** - Get the power of multiple LLM providers with the familiarity of Claude Code.
