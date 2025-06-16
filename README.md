# OpenRouter Anthropic Server v2.0

A production-ready, modular API proxy server that provides enhanced functionality for interacting with Anthropic's Claude models through OpenRouter with complete tool execution capabilities.

## 🚀 Quick Start

```bash
# Install dependencies
uv sync

# Set your OpenRouter API key
export OPENROUTER_API_KEY="your-api-key-here"

# Start the server
python start_server.py

# Test the server
curl http://localhost:4000/health
```

## ✨ Key Features

- **🔄 Full Anthropic API Compatibility** - Drop-in replacement for Anthropic API
- **🛠️ Advanced Tool Execution** - 15+ Claude Code tools with security controls
- **⚡ Production Ready** - Comprehensive monitoring, logging, and error handling
- **🏗️ Modular Architecture** - Clean, maintainable, and scalable Prefect-based design
- **🔒 Enhanced Security** - Input validation, rate limiting, and secure execution
- **📊 Comprehensive Testing** - 283+ tests with 100% critical path coverage
- **🌐 Streaming Support** - Real-time streaming responses
- **📈 Performance Optimized** - Concurrent task execution and resource optimization

## 📊 Status

**✅ PRODUCTION READY**

- **Test Suite**: 283/283 tests passing (100% success rate)
- **Architecture**: Modular coordinator-flow-task architecture fully implemented
- **Documentation**: Complete documentation suite
- **Deployment**: Multiple deployment options available
- **Security**: Production security controls implemented

## 🔧 Supported Tools

### File Operations (4 tools)
- **Write** - Create or overwrite files
- **Read** - Read file contents with options
- **Edit** - String replacement in files
- **MultiEdit** - Multiple replacements in one operation

### Search Operations (3 tools)
- **Glob** - File pattern matching with recursive search
- **Grep** - Content search with regex support  
- **LS** - Directory listing with detailed information

### System Operations (2 tools)
- **Bash** - Execute whitelisted shell commands
- **Task** - Simple task management

### Web Operations (2 tools)
- **WebSearch** - Web search using DuckDuckGo
- **WebFetch** - Fetch web page content

### Notebook Operations (2 tools)
- **NotebookRead** - Read Jupyter notebook contents
- **NotebookEdit** - Modify notebook cells

### Todo Operations (2 tools)
- **TodoRead** - Read and filter todo items
- **TodoWrite** - Full CRUD operations for tasks

## 🏗️ Architecture

The server uses a modular, task-based architecture with:

- **FastAPI** for high-performance API endpoints
- **Prefect** for workflow orchestration and task management
- **Pydantic** for type safety and validation
- **LiteLLM** for OpenRouter integration
- **Instructor** for structured outputs

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Routers   │ -> │   Workflows     │ -> │ Prefect Tasks   │
│                 │    │                 │    │                 │
│ • Messages      │    │ • Tool Exec     │    │ • File Ops      │
│ • Health        │    │ • Conversion    │    │ • Validation    │
│ • Debug         │    │ • Validation    │    │ • Security      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📚 Documentation

Visit [`docs/`](docs/) for comprehensive documentation:

- **[📖 Documentation Overview](docs/README.md)** - Complete documentation guide
- **[🔌 API Reference](docs/02-api-reference.md)** - Complete API documentation with examples
- **[🏗️ Architecture](docs/03-architecture.md)** - System architecture and design
- **[🔄 Unified Proxy Backend Guide](docs/17-unified-proxy-backend-guide.md)** - Backend configuration and routing
- **[☁️ Azure Databricks Integration](docs/16-azure-databricks-guide.md)** - Comprehensive Azure Databricks Claude guide
- **[🚀 Deployment Guide](docs/05-production-deployment-guide.md)** - Production deployment instructions
- **[📊 Implementation Status](docs/08-implementation-status.md)** - Current implementation status
- **[🧪 Testing Plan](docs/06-claude-code-cli-testing-plan.md)** - Comprehensive testing strategy

## 🚀 Deployment Options

### Option 1: Direct Python
```bash
# Install dependencies
uv sync

# Configure environment
export OPENROUTER_API_KEY="your-api-key"
export ENVIRONMENT="production"

# Start server
python start_server.py
```

### Option 2: Docker
```bash
# Build image
docker build -t openrouter-anthropic-server .

# Run container
docker run -d \
  -p 4000:4000 \
  -e OPENROUTER_API_KEY="your-api-key" \
  openrouter-anthropic-server
```

### Option 3: Docker Compose
```bash
# Configure environment
echo "OPENROUTER_API_KEY=your-api-key" > .env

# Start services
docker-compose up -d
```

## 🔧 Configuration

### Required Environment Variables
- `OPENROUTER_API_KEY` - Your OpenRouter API key

### Unified Proxy Backend Configuration
The server supports four backend modes via the `PROXY_BACKEND` environment variable:

#### **OPENROUTER** (Recommended)
Direct OpenRouter integration for best performance:
```bash
PROXY_BACKEND=OPENROUTER
OPENROUTER_API_KEY=your-api-key
```

#### **LITELLM_MESSAGES** (Native Anthropic Format)
Use LiteLLM's `/v1/messages` endpoint with no format conversion:
```bash
PROXY_BACKEND=LITELLM_MESSAGES
LITELLM_BASE_URL=http://localhost:4001
OPENROUTER_API_KEY=your-api-key
```
**Benefits**: No format conversion overhead, simplified architecture, native Anthropic format support

#### **AZURE_DATABRICKS**
Route requests to Azure Databricks Claude endpoints:
```bash
PROXY_BACKEND=AZURE_DATABRICKS
DATABRICKS_HOST=your-workspace-instance  # without .azuredatabricks.net
DATABRICKS_TOKEN=your-databricks-token
OPENROUTER_API_KEY=your-api-key  # still needed for fallback tools
```

#### **LITELLM_OPENROUTER** (Legacy)
Use LiteLLM with format conversion for advanced features:
```bash
PROXY_BACKEND=LITELLM_OPENROUTER
OPENROUTER_API_KEY=your-api-key
LITELLM_MASTER_KEY=your-secure-master-key
```

### Optional Environment Variables
- `ENVIRONMENT` - Environment mode (`development`/`production`)
- `HOST` - Server host (default: `127.0.0.1`)
- `PORT` - Server port (default: `4000`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `DEBUG_ENABLED` - Enable debug features (default: `false`)
- `LITELLM_BASE_URL` - LiteLLM proxy server URL (for LITELLM_MESSAGES backend)

> **Note:** Use `env.example` as a template for your `.env` file. The `.env` file is gitignored for security.

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test categories
uv run pytest tests/unit/
uv run pytest tests/integration/
```

## 📊 API Examples

### Basic Chat
```bash
curl -X POST http://localhost:4000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-sonnet-4",
    "max_tokens": 100,
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### With Tools
```bash
curl -X POST http://localhost:4000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "big",
    "max_tokens": 1000,
    "messages": [
      {"role": "user", "content": "Create a file called test.txt with hello world"}
    ],
    "tools": [
      {
        "name": "Write",
        "description": "Write content to a file",
        "input_schema": {
          "type": "object",
          "properties": {
            "file_path": {"type": "string"},
            "content": {"type": "string"}
          },
          "required": ["file_path", "content"]
        }
      }
    ]
  }'
```

### Health Check
```bash
curl http://localhost:4000/health
```

## 🔍 Monitoring

### Health Endpoints
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system status
- `GET /tool-metrics` - Tool execution metrics

### Debug Endpoints (Development)
- `GET /debug/errors/recent` - Recent error logs
- `GET /debug/errors/stats` - Error statistics

## 🛡️ Security Features

- **Input Validation** - Multi-layer request validation
- **Tool Security** - Whitelisted commands and path validation
- **Rate Limiting** - Configurable rate limits per tool
- **Error Sanitization** - Secure error responses
- **CORS Configuration** - Proper cross-origin handling

## 🔧 Claude Code CLI Integration

Set up Claude Code CLI to use this proxy:

```bash
# Set the base URL
export ANTHROPIC_BASE_URL=http://localhost:4000

# Use the no-proxy script to avoid conflicts
./claude-no-proxy "Hello, test the proxy server!"
```

## 📈 Performance

- **Concurrent Execution** - Independent operations run in parallel
- **Async Processing** - Non-blocking I/O throughout
- **Connection Pooling** - Efficient API connections
- **Resource Optimization** - Optimized memory and CPU usage
- **Horizontal Scaling** - Stateless design for easy scaling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:

1. Check the [Documentation](docs/)
2. Review [Debug Logging Guide](docs/07-debug-logging.md)
3. Check [API Reference](docs/02-api-reference.md)
4. Review [Implementation Status](docs/08-implementation-status.md)

## 🎯 Project Goals Achieved

- ✅ **Full Anthropic API Compatibility** - Complete drop-in replacement
- ✅ **Advanced Tool Execution** - All 15 Claude Code tools operational
- ✅ **Production Readiness** - Comprehensive testing and documentation
- ✅ **Modular Architecture** - Maintainable and scalable design
- ✅ **Security Controls** - Enterprise-grade security features
- ✅ **Performance Optimization** - Optimized for production workloads

---

**OpenRouter Anthropic Server v2.0** - Bridging Claude's capabilities with production reliability.
