# Claude Code with OpenRouter Proxy

> **Note**: This project provides two approaches for connecting Claude Code to OpenRouter API.

## 🏗️ Two Implementation Approaches

### 1. **LiteLLM Docker Proxy**
- **File**: [`docker-compose.yml`](docker-compose.yml)
- **Port**: `4000`
- **Purpose**: General-purpose proxy supporting multiple providers
- **Note**: Response format depends on the provider (Google Vertex, Amazon Bedrock, OpenRouter, etc.)

### 2. **OpenRouter to Anthropic API Conversion Server** ⭐ **Recommended**
- **File**: [`openrouter_anthropic_server.py`](openrouter_anthropic_server.py)
- **Port**: `5001`
- **Purpose**: Converts OpenRouter responses to Anthropic API format for perfect Claude Code compatibility

## 🚀 Quick Start

### Option 1: LiteLLM Docker

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY and LITELLM_MASTER_KEY

# 2. Start LiteLLM
docker-compose up -d

# 3. Configure Claude Code
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_AUTH_TOKEN=your-secure-master-key-here

# 4. Test
python test_litellm.py
```

### Option 2: OpenRouter Anthropic Server (Recommended)

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY

# 2. Install dependencies
pip install fastapi uvicorn litellm python-dotenv pydantic

# 3. Start the server
python openrouter_anthropic_server.py

# 4. Configure Claude Code
export ANTHROPIC_BASE_URL=http://localhost:5001
export ANTHROPIC_AUTH_TOKEN=dummy-key

# 5. Test
python test_openrouter_server.py
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file:
```bash
# Required for both approaches
OPENROUTER_API_KEY=sk-or-v1-your-actual-openrouter-api-key-here

# Required only for LiteLLM Docker
LITELLM_MASTER_KEY=your-secure-master-key-here

# Optional: Model configuration for OpenRouter server
ANTHROPIC_MODEL=anthropic/claude-sonnet-4
ANTHROPIC_SMALL_FAST_MODEL=anthropic/claude-3.7-sonnet
```

### Key Files

| File | Purpose |
|------|---------|
| [`docker-compose.yml`](docker-compose.yml) | LiteLLM Docker deployment |
| [`litellm_config.yaml`](litellm_config.yaml) | LiteLLM configuration |
| [`openrouter_anthropic_server.py`](openrouter_anthropic_server.py) | OpenRouter to Anthropic API converter |
| [`.env.example`](.env.example) | Environment template |

## 🧪 Testing

```bash
# Test LiteLLM Docker
python test_litellm.py

# Test OpenRouter Anthropic Server
python test_openrouter_server.py
```

## 🔍 Key Differences

| Feature | LiteLLM Docker | OpenRouter Server |
|---------|----------------|-------------------|
| **Response Format** | Depends on provider | Always Anthropic API format |
| **Claude Code Compatibility** | Variable | Perfect |
| **Setup Complexity** | Docker + Config | Simple Python script |
| **Provider Support** | Multiple (Vertex, Bedrock, etc.) | OpenRouter only |

## 🔧 Key Technical Details

### LiteLLM Response Format Issue
LiteLLM's response format varies depending on the provider:
- **Google Vertex AI**: Different response structure
- **Amazon Bedrock**: Different response structure  
- **OpenRouter**: Different response structure
- **Direct Anthropic**: Native Anthropic format

This variability can cause compatibility issues with Claude Code.

### OpenRouter Anthropic Server Solution
The custom server solves this by:
- Converting OpenRouter responses to exact Anthropic API format
- Handling model name mapping automatically
- Supporting all Claude Code features (tools, streaming, etc.)
- Providing consistent behavior regardless of underlying provider

## 🎯 Recommendation

**Use the OpenRouter Anthropic Server** for Claude Code integration because:
- ✅ Consistent Anthropic API response format
- ✅ Perfect Claude Code compatibility
- ✅ Simple deployment (single Python file)
- ✅ Full feature support

## ⚠️ Important: Claude Code Environment

**Do NOT set proxy environment variables** (`HTTP_PROXY`, `HTTPS_PROXY`) in the Claude Code running environment. This will cause multiple errors including:
- "API Error"
- "Type Error"
- Connection failures

If you need proxy access for the servers themselves, configure proxy settings only in:
- Docker container environment (for LiteLLM)
- Server process environment (for OpenRouter Anthropic Server)

**Keep Claude Code environment clean** - no proxy variables should be set when running `claude`.

## 📁 Final Project Structure

```
claude-code-proxy/
├── README.md                      # Main documentation
├── .env.example                   # Environment template
├── docker-compose.yml             # LiteLLM Docker setup
├── litellm_config.yaml            # LiteLLM configuration
├── openrouter_anthropic_server.py # OpenRouter to Anthropic converter
├── test_litellm.py               # LiteLLM tests
├── test_openrouter_server.py     # OpenRouter server tests
└── LICENSE                        # MIT license
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Project Status**: ✅ **COMPLETE**

Both approaches are working. The OpenRouter Anthropic Server is recommended for Claude Code due to its perfect API compatibility.