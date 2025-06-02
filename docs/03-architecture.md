# Architecture Overview

## OpenRouter Anthropic Server v2.0 - Production Architecture

This document provides an overview of the current production architecture of the OpenRouter Anthropic Server v2.0 after the comprehensive Phase 6 refactoring to a modular, task-based architecture.

## 🏗️ System Architecture

The server follows a modular, production-ready architecture with clear separation of concerns and Prefect-based workflow orchestration:

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                      │
│              (Claude Code, API Clients)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/HTTPS Requests
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Server                            │
│                   (Port 4000)                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Middleware Stack                             │
│  ┌─────────────┬─────────────┬─────────────────────────────┐ │
│  │   Logging   │    CORS     │    Error Handling           │ │
│  │ Middleware  │ Middleware  │     Middleware              │ │
│  └─────────────┴─────────────┴─────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Routers                              │
│  ┌─────────────┬─────────────┬─────────────┬───────────────┐ │
│  │  Messages   │   Tokens    │    Health   │     MCP       │ │
│  │   Router    │   Router    │   Router    │   Router      │ │
│  └─────────────┴─────────────┴─────────────┴───────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Workflow Orchestration Layer                  │
│  ┌─────────────┬─────────────┬─────────────────────────────┐ │
│  │  Message    │    Tool     │       MCP                   │ │
│  │ Workflows   │ Workflows   │   Workflows                 │ │
│  └─────────────┴─────────────┴─────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Service Coordinators                        │
│  ┌─────────────┬─────────────┬─────────────────────────────┐ │
│  │Execution    │Conversion   │   Validation                │ │
│  │Coordinator  │Coordinator  │  Coordinator                │ │
│  └─────────────┴─────────────┴─────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Prefect Flows                             │
│  ┌─────────────┬─────────────┬─────────────────────────────┐ │
│  │   Tool      │ Conversion  │     Validation              │ │
│  │   Flows     │   Flows     │      Flows                  │ │
│  └─────────────┴─────────────┴─────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Prefect Tasks                            │
│  ┌─────────────┬─────────────┬─────────────────────────────┐ │
│  │    Tool     │   Format    │      Security               │ │
│  │   Tasks     │   Tasks     │      Tasks                  │ │
│  └─────────────┴─────────────┴─────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                External Services                            │
│  ┌─────────────┬─────────────┬─────────────────────────────┐ │
│  │  LiteLLM    │ OpenRouter  │     Instructor              │ │
│  │ Integration │     API     │   (Structured Outputs)      │ │
│  └─────────────┴─────────────┴─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Modular Code Organization

```
src/
├── main.py                      # FastAPI application entry point
├── models/                      # Pydantic data models
│   ├── anthropic.py            # Anthropic API models
│   ├── base.py                 # Base models and utilities
│   ├── instructor.py           # Instructor-enhanced models
│   └── litellm.py              # LiteLLM integration models
├── workflows/                   # High-level orchestration workflows
│   ├── message_workflows.py    # Message processing workflows
│   ├── tool_workflows.py       # Tool execution workflows
│   └── mcp_workflows.py        # MCP management workflows (if applicable)
├── coordinators/                # Service coordination layer
│   ├── execution_coordinator.py # Tool execution coordination
│   ├── tool_coordinator.py     # Tool orchestration
│   └── __init__.py             # Coordinator registry
├── flows/                       # Specialized Prefect flows
│   ├── tool_execution/         # Tool execution flows
│   │   ├── file_operations.py  # File operation flows
│   │   ├── system_operations.py # System operation flows
│   │   ├── web_operations.py   # Web operation flows
│   │   └── search_operations.py # Search operation flows
│   ├── conversion/             # Format conversion flows
│   │   └── conversion_orchestration.py # Conversion pipelines
│   └── validation/             # Validation flows
│       ├── message_validation_flows.py # Message validation
│       └── validation_orchestration.py # Validation pipelines
├── tasks/                       # Atomic Prefect tasks
│   ├── tools/                  # Tool execution tasks
│   │   ├── file_tools.py       # File operations (Write, Read, Edit)
│   │   ├── system_tools.py     # System operations (Bash, Task)
│   │   ├── search_tools.py     # Search operations (Glob, Grep, LS)
│   │   ├── web_tools.py        # Web operations (WebSearch, WebFetch)
│   │   ├── notebook_tools.py   # Notebook operations
│   │   └── todo_tools.py       # Todo management
│   ├── conversion/             # Format conversion tasks
│   │   ├── format_conversion.py # Message format tasks
│   │   ├── message_transformation.py # Message processing
│   │   ├── model_mapping.py    # Model name mapping
│   │   ├── response_processing.py # Response handling
│   │   ├── schema_processing.py # Schema operations
│   │   └── structured_output.py # Structured outputs
│   └── validation/             # Validation tasks
│       ├── message_validation.py # Message validation
│       ├── request_validation.py # Request validation
│       ├── security_validation.py # Security validation
│       ├── tool_validation.py  # Tool validation
│       └── flow_validation.py  # Flow validation
├── services/                    # Business logic services
│   ├── base.py                 # Base service classes
│   ├── validation.py           # Request/response validation
│   ├── conversion.py           # Format conversion services
│   ├── tool_execution.py       # Tool execution orchestration
│   ├── context_manager.py      # Request context management
│   ├── mixed_content_detector.py # Content type detection
│   └── http_client.py          # HTTP client configuration
├── routers/                     # API endpoint handlers
│   ├── messages.py             # Messages API endpoints
│   ├── tokens.py               # Token counting endpoints
│   ├── health.py               # Health monitoring endpoints
│   ├── debug.py                # Debug endpoints (development only)
│   └── mcp.py                  # MCP management endpoints
├── middleware/                  # Request/response middleware
│   ├── logging_middleware.py   # Request logging
│   ├── error_middleware.py     # Error handling
│   ├── cors_middleware.py      # CORS configuration
│   └── unified_logging_middleware.py # Unified logging
├── orchestrators/               # Legacy orchestration layer
│   └── conversation_orchestrator.py # Conversation management
├── mcp/                        # MCP (Model Context Protocol) support
│   ├── lifecycle_service.py    # MCP server lifecycle
│   ├── environment_manager.py  # Environment management
│   └── server_configs.py       # Server configuration
├── core/                       # Core infrastructure
│   └── logging_config.py       # Structured logging configuration
└── utils/                      # Configuration and utilities
    ├── config.py               # Environment configuration
    ├── debug.py                # Debug utilities
    ├── error_logger.py         # Error logging utilities
    ├── errors.py               # Custom error classes
    └── instructor_client.py    # Instructor integration
```

## 🔄 Request Flow

### Standard Message Request with Tool Execution
1. **Client Request** → FastAPI server receives Anthropic API request
2. **Middleware Processing** → Logging, CORS, error handling
3. **Router Dispatch** → Request routed to messages router
4. **Workflow Orchestration** → Message workflow coordinates processing
5. **Validation Flow** → Request validated using Prefect validation tasks
6. **Model Mapping** → Model aliases resolved (big/small → actual models)
7. **Conversion Flow** → Anthropic format → LiteLLM format via Prefect tasks
8. **API Call** → LiteLLM calls OpenRouter API
9. **Tool Detection** → Check for tool_use blocks in response
10. **Tool Execution Flow** → Execute tools via Prefect tool tasks (if needed)
11. **Conversation Continuation** → Follow-up API call with tool results
12. **Response Conversion** → LiteLLM response → Anthropic format
13. **Structured Processing** → Instructor processes structured outputs
14. **Response** → Formatted response returned to client

### Streaming Request Flow
- Same flow as above, but with Server-Sent Events (SSE) streaming
- Real-time chunk processing and format conversion
- Maintains Anthropic streaming format compatibility

## 🔧 Key Components

### Workflow Orchestration Layer
- **Message Workflows**: High-level message processing coordination
- **Tool Workflows**: Tool execution orchestration and result aggregation
- **MCP Workflows**: MCP server management and operations

### Service Coordinators
- **Execution Coordinator**: Coordinates tool execution and conversation flow
- **Tool Coordinator**: Orchestrates individual tool operations
- **Conversion Coordinator**: Manages format conversion pipelines

### Prefect Flow Architecture
- **Tool Execution Flows**: Specialized flows for different tool categories
- **Conversion Flows**: Format conversion pipelines with parallel processing
- **Validation Flows**: Multi-stage validation with error aggregation

### Atomic Task System
- **Tool Tasks**: Individual tool operations as atomic tasks
- **Conversion Tasks**: Format transformation operations
- **Validation Tasks**: Validation checks as isolated tasks
- **Security Tasks**: Security validation and sanitization

### Configuration Management
- **Environment-aware settings** with Pydantic validation
- **Model mapping configuration** (big/small aliases)
- **Performance and security settings**
- **Debug and logging configuration**

### Validation Services
- **Message format validation** using Pydantic models
- **Conversation flow validation** for multi-turn conversations
- **Tool definition validation** for function calling
- **Request/response validation** with comprehensive error handling

### Conversion Services
- **Anthropic ↔ LiteLLM format conversion**
- **Model mapping and alias resolution**
- **OpenRouter prefix handling** for proper routing
- **Structured output processing** with Instructor

### Middleware Stack
- **Logging Middleware**: Request/response logging with correlation IDs
- **Error Middleware**: Comprehensive error handling and formatting
- **CORS Middleware**: Cross-origin resource sharing configuration
- **Unified Logging**: Consolidated logging across all components

## 🛡️ Production Features

### Reliability
- **Comprehensive error handling** with Anthropic-format responses
- **Task-based error isolation** - individual task failures don't affect others
- **Built-in retry logic** via Prefect task retry mechanisms
- **Health monitoring** with detailed status endpoints
- **Performance tracking** with request timing metrics

### Security
- **Input validation** and sanitization at multiple layers
- **Tool execution security** with whitelisted commands and path validation
- **Environment variable security** for API keys
- **CORS configuration** for web security
- **Rate limiting** capabilities with tool-specific limits

### Monitoring & Observability
- **Structured JSON logging** with component identification
- **Prefect dashboard** for workflow monitoring and debugging
- **Health check endpoints** for monitoring systems
- **Performance metrics** collection with tool-specific timing
- **Debug logging** (configurable, disabled in production)
- **Task execution tracking** with detailed error reporting

### Scalability Features
- **Concurrent task execution** - independent operations run in parallel
- **Horizontal scaling** via Prefect workers
- **Resource optimization** - better CPU and memory utilization
- **Async processing** throughout the entire stack

## 📊 Model Mapping

The server provides convenient model aliases:

| Alias   | Maps To                       | Use Case                |
| ------- | ----------------------------- | ----------------------- |
| `big`   | `anthropic/claude-sonnet-4`   | Complex reasoning tasks |
| `small` | `anthropic/claude-3.7-sonnet` | Fast, efficient tasks   |

All model names are automatically prefixed with `openrouter/` for proper LiteLLM routing.

## 🔌 API Endpoints

### Core Endpoints
- `POST /v1/messages` - Create message completions
- `POST /v1/messages/count_tokens` - Count tokens in requests
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system status
- `GET /tool-metrics` - Tool execution metrics

### Debug Endpoints (Development Only)
- `GET /debug/errors/recent` - Recent error logs
- `GET /debug/errors/{correlation_id}` - Specific error details
- `GET /debug/errors/stats` - Error statistics

### Features
- **Full Anthropic API compatibility**
- **Advanced tool calling** with 15+ Claude Code tools
- **Streaming responses** with SSE
- **Token counting** for cost estimation
- **MCP server management** (if configured)

## 🚀 Deployment Architecture

### Production Deployment
- **Docker containerization** for consistent deployment
- **Environment-based configuration** for different environments
- **Health checks** for container orchestration
- **Horizontal scaling** support with load balancing
- **Prefect worker scaling** for task execution

### Performance Characteristics
- **Async processing** for high concurrency
- **Connection pooling** for efficient API calls
- **Parallel task execution** for independent operations
- **Request/response caching** for improved performance
- **Optimized memory usage** with proper cleanup

## 📈 Scalability

### Horizontal Scaling
- **Stateless design** enables easy horizontal scaling
- **Load balancer compatibility** for multi-instance deployment
- **Container orchestration** support (Kubernetes, Docker Swarm)
- **Prefect worker distribution** across multiple machines

### Vertical Scaling
- **Configurable worker processes** for CPU optimization
- **Memory optimization** settings
- **Performance tuning** parameters
- **Task concurrency limits** for resource management

## 🔍 Monitoring and Observability

### Prefect Dashboard
- **Visual workflow monitoring** for all flows and tasks
- **Real-time execution tracking** with detailed timing
- **Error visualization** with stack traces and context
- **Performance analytics** across all operations

### Logging
- **Structured JSON logs** for easy parsing
- **Request correlation IDs** for tracing
- **Component-specific logging** for debugging
- **Performance metrics** in logs
- **Task execution logs** with detailed context

### Health Monitoring
- **Basic health endpoint** for simple checks
- **Detailed health endpoint** with service status
- **Tool metrics endpoint** with execution statistics
- **Dependency health checks** (OpenRouter, LiteLLM)
- **System resource monitoring** (when available)

## 🎯 Design Principles

### Modularity
- **Task-based architecture** with atomic operations
- **Clear separation of concerns** between components
- **Dependency injection** for testability
- **Interface-based design** for flexibility

### Reliability
- **Comprehensive error handling** at all layers
- **Task-level error isolation** for fault tolerance
- **Built-in retry mechanisms** with exponential backoff
- **Graceful degradation** for service failures

### Maintainability
- **Type safety** with full type hints
- **Comprehensive testing** (334+ tests)
- **Clear documentation** and code comments
- **Consistent coding standards**
- **Modular task organization** for easy maintenance

### Performance
- **Concurrent execution** of independent operations
- **Optimized resource utilization** via task scheduling
- **Efficient error handling** without system-wide impact
- **Scalable architecture** for growing workloads

## 🔄 Workflow Examples

### Simple Message Processing
```
Client Request → Validation Flow → Conversion Flow → API Call → Response
```

### Complex Tool Execution
```
Client Request → Validation Flow → Conversion Flow → API Call → 
Tool Detection → Tool Execution Flow → Conversation Continuation → Response
```

### Multi-Tool Coordination
```
Tool Use Detection → Parallel Tool Tasks → Result Aggregation → 
Continuation Request → Final Response
```

This architecture provides a robust, scalable, and maintainable foundation for the OpenRouter Anthropic Server, ensuring reliable operation in production environments while maintaining full compatibility with the Anthropic API and providing enhanced tool execution capabilities.