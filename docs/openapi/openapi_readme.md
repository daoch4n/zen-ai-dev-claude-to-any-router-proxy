# Generating API Markdown Documentation with OpenAPI Generator CLI

This guide demonstrates how to use the [openapi-generator-cli](https://github.com/OpenAPITools/openapi-generator-cli) to generate comprehensive markdown documentation from multiple AI API specifications: OpenAI, Anthropic, OpenRouter, and LiteLLM.

## Overview

The OpenAPI Generator CLI is a Node.js package wrapper that provides a command-line interface for the OpenAPI Generator tool. It automatically generates client libraries, server stubs, API documentation, and configuration files from OpenAPI (formerly Swagger) specification files.

## Prerequisites

- Node.js and npm installed
- Internet connection to download the API specifications

## Installation

Install the openapi-generator-cli globally:

```bash
npm install -g @openapitools/openapi-generator-cli
```

## Supported AI APIs

This guide covers documentation generation for five major AI API providers and tools:

1. **OpenAI** - GPT models, DALL-E, Whisper, and more
2. **Anthropic** - Claude models for conversations and text generation
3. **OpenRouter** - Unified access to 300+ AI models from multiple providers
4. **LiteLLM** - Universal proxy for 100+ LLM APIs with unified interface
5. **Claude Code CLI** - Agentic coding tool APIs (Claude, OAuth, Telemetry)

---

## 1. OpenAI API Documentation

### Generate OpenAI API Documentation

```bash
openapi-generator-cli generate \
  -g markdown \
  -i https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml \
  -o ./openai-api-docs \
  --skip-validate-spec
```

### OpenAI Documentation Structure

The generated documentation includes:

- **README.md** (944 lines) - Complete API overview and index
- **Apis/** directory containing:
  - `AudioApi.md` - Speech-to-text and text-to-speech endpoints
  - `ChatApi.md` - Chat completion endpoints (GPT models)
  - `CompletionsApi.md` - Legacy completion endpoints
  - `EmbeddingsApi.md` - Vector embedding generation
  - `FilesApi.md` - File upload and management
  - `FineTuningApi.md` - Custom model fine-tuning
  - `ImagesApi.md` - DALL-E image generation
  - `ModelsApi.md` - Model listing and information
  - `ModerationsApi.md` - Content moderation

- **Models/** directory with 50+ data model definitions including:
  - `CreateChatCompletionRequest.md` - Chat completion parameters
  - `ChatCompletionResponse.md` - Response structure
  - `CreateImageRequest.md` - Image generation parameters
  - And many more detailed model schemas

---

## 2. Anthropic API Documentation

### Generate Anthropic API Documentation

```bash
openapi-generator-cli generate \
  -g markdown \
  -i https://raw.githubusercontent.com/laszukdawid/anthropic-openapi-spec/main/hosted_spec.yaml \
  -o ./anthropic-api-docs \
  --skip-validate-spec
```

### Anthropic Documentation Structure

The generated documentation includes:

- **README.md** (173 lines) - API overview and endpoint index
- **Apis/** directory containing:
  - `MessagesApi.md` - Core message creation and conversation endpoints
  - `MessageBatchesApi.md` - Batch processing functionality 
  - `TextCompletionsApi.md` - Legacy completion endpoints

- **Models/** directory with detailed schemas including:
  - `BetaCreateMessageParams.md` - Message creation parameters
  - `BetaMessage.md` - Message response structure
  - `BetaTextBlock.md` - Text content blocks
  - And other Claude-specific model definitions

### Key Anthropic Features Documented

- **Streaming responses** for real-time conversations
- **Message batching** for efficient bulk processing
- **Beta features** clearly marked and documented
- **Token counting** and usage tracking
- **Content safety** and moderation guidelines

---

## 3. OpenRouter API Documentation

Since OpenRouter doesn't provide a public OpenAPI specification, I've created a comprehensive custom specification based on their documentation.

### Generate OpenRouter API Documentation

First, create the OpenRouter OpenAPI specification file (`openrouter-openapi.yaml`):

```yaml
openapi: 3.0.3
info:
  title: OpenRouter API
  description: |
    OpenRouter provides unified access to multiple AI models through a single API.
    
    OpenRouter normalizes the schema across models and providers to comply with the OpenAI Chat API,
    making it easy to switch between different AI models without changing your code.
  version: 1.0.0

servers:
  - url: https://openrouter.ai/api/v1

# ... (complete specification included in this repository)
```

Then generate the documentation:

```bash
openapi-generator-cli generate \
  -g markdown \
  -i openrouter-openapi.yaml \
  -o ./openrouter-api-docs \
  --skip-validate-spec
```

### OpenRouter Documentation Structure

The generated documentation includes:

- **README.md** (59 lines) - API overview and authentication
- **Apis/** directory containing:
  - `ChatApi.md` - Chat completion with model routing
  - `ModelsApi.md` - Available model listing (300+ models)
  - `GenerationsApi.md` - Generation tracking and analytics
  - `CreditsApi.md` - Credit balance and usage
  - `AuthenticationApi.md` - API key management

- **Models/** directory with OpenRouter-specific schemas including:
  - `ChatCompletionRequest.md` - Enhanced with routing options
  - `ProviderPreferences.md` - Provider fallback settings
  - `Generation.md` - Generation metadata and costs
  - `Model.md` - Model details with pricing information

### Key OpenRouter Features Documented

- **Model routing** and fallback strategies
- **Provider preferences** and data collection settings
- **Real-time pricing** per model and provider
- **Generation tracking** with cost analysis
- **OpenAI compatibility** with extensions

---

## 4. LiteLLM API Documentation

LiteLLM provides a universal proxy server that offers unified access to 100+ LLM APIs including OpenAI, Anthropic, Azure, AWS Bedrock, Google Vertex AI, and more through a single interface.

### Generate LiteLLM API Documentation

```bash
openapi-generator-cli generate \
  -g markdown \
  -i https://litellm-api.up.railway.app/openapi.json \
  -o ./litellm-api-docs \
  --skip-validate-spec
```

### LiteLLM Documentation Structure

The generated documentation includes:

- **README.md** (626 lines) - Comprehensive API overview with complete endpoint table
- **Apis/** directory containing 43+ endpoint documentation files:
  - `ChatCompletionsApi.md` - Core chat completion with multi-provider support
  - `EmbeddingsApi.md` - Text embeddings across providers
  - `AudioApi.md` - Speech and transcription services
  - `ImagesApi.md` - Image generation capabilities
  - `BatchApi.md` - Batch processing for bulk operations
  - `KeyManagementApi.md` - API key lifecycle management
  - `TeamManagementApi.md` - Multi-user team collaboration
  - `ModelManagementApi.md` - Model configuration and deployment
  - `GuardrailsApi.md` - Content safety and moderation
  - `CachingApi.md` - Response caching and optimization
  - `HealthApi.md` - System health monitoring
  - `FilesApi.md` - File upload and management
  - `FineTuningApi.md` - Custom model fine-tuning
  - `AssistantsApi.md` - OpenAI-compatible assistants
  - **Provider Pass-Through APIs**:
    - `AnthropicPassThroughApi.md` - Direct Anthropic API access
    - `OpenAIPassThroughApi.md` - Direct OpenAI API access
    - `AzurePassThroughApi.md` - Azure OpenAI service
    - `BedrockPassThroughApi.md` - AWS Bedrock models
    - `VertexAIPassThroughApi.md` - Google Vertex AI
    - `CoherePassThroughApi.md` - Cohere API access
    - `MistralPassThroughApi.md` - Mistral AI models
    - And more provider-specific endpoints
  - **Enterprise Features**:
    - `BudgetManagementApi.md` - Cost tracking and limits
    - `AuditLoggingApi.md` - Compliance and security logging
    - `SCIMV2Api.md` - Enterprise user provisioning
    - `SSOSettingsApi.md` - Single sign-on configuration
    - `OrganizationManagementApi.md` - Multi-tenant organization support

- **Models/** directory with 100+ detailed model schemas including:
  - `ChatCompletionRequest.md` - Multi-provider chat parameters
  - `LiteLLM_Params.md` - LiteLLM-specific configuration
  - `GenerateKeyRequest.md` - API key generation parameters
  - `TeamAddMemberRequest.md` - Team collaboration schemas
  - `GuardrailRequest.md` - Content safety configuration
  - `BatchProcessingRequest.md` - Bulk operation parameters
  - And comprehensive enterprise and provider-specific models

### Key LiteLLM Features Documented

- **Universal API Interface** - Single API for 100+ LLM providers
- **Enterprise Management** - Teams, organizations, budgets, and audit logs
- **Advanced Caching** - Intelligent response caching with Redis support
- **Batch Processing** - Efficient bulk operations with streaming
- **Content Safety** - Built-in guardrails and moderation tools
- **Cost Management** - Real-time usage tracking and budget controls
- **Health Monitoring** - Comprehensive system health and metrics
- **Provider Fallbacks** - Automatic failover between providers
- **SCIM v2 Support** - Enterprise user provisioning and management
- **SSO Integration** - Single sign-on with major identity providers
- **MCP Support** - Model Context Protocol for tool integration
- **Fine-tuning** - Custom model training across providers
- **Vector Stores** - Managed vector database integration
- **Pass-through APIs** - Direct access to native provider features

---

## 5. Claude Code CLI API Documentation

Claude Code CLI is an agentic coding tool by Anthropic that lives in your terminal, understands your codebase, and helps you code faster through natural language commands. Based on analysis of the Claude Code CLI source code, it uses three primary APIs for its functionality.

### Generate Claude Code CLI API Documentation

Since no public OpenAPI specification exists for Claude Code CLI's APIs, I've created a comprehensive custom specification based on source code analysis.

First, create the Claude Code CLI OpenAPI specification file (`claude-code-openapi.yaml`):

```yaml
openapi: 3.0.3
info:
  title: Claude Code CLI API
  description: |
    API specifications for the Anthropic Claude Code CLI tool, covering the main services used:
    
    1. **Claude API** - Main AI service for chat completions and code assistance
    2. **OAuth API** - Authentication service for secure access  
    3. **Telemetry API** - Analytics and error reporting service
  version: 1.0.0

servers:
  - url: https://api.anthropic.com
  - url: https://auth.anthropic.com
  - url: https://telemetry.anthropic.com

# ... (complete specification included in this repository)
```

Then generate the documentation:

```bash
openapi-generator-cli generate \
  -g markdown \
  -i claude-code-openapi.yaml \
  -o ./claude-api-docs \
  --skip-validate-spec
```

### Claude Code CLI Documentation Structure

The generated documentation includes:

- **README.md** (42 lines) - Complete API overview with endpoint table
- **Apis/** directory containing:
  - `ClaudeAPIApi.md` - Core AI chat completion endpoint (/v1/messages)
  - `OAuthAPIApi.md` - Authentication endpoints (/oauth2/auth, /oauth2/token)
  - `TelemetryAPIApi.md` - Analytics endpoint (/claude-code/events)

- **Models/** directory with 11 detailed schemas including:
  - `MessageRequest.md` - Chat completion request parameters
  - `MessageResponse.md` - Chat completion response structure
  - `TokenResponse.md` - OAuth token response format
  - `TelemetryEvent.md` - Telemetry event structure
  - `ClientInfo.md` - Client identification schema
  - And other API-specific model definitions

### Key Claude Code CLI APIs Documented

#### **1. Claude API (api.anthropic.com)**
- **Chat Completions** - Primary `/v1/messages` endpoint for AI interactions
- **Streaming Support** - Real-time response streaming with Server-Sent Events
- **Model Selection** - Support for Claude 3 Opus and other models
- **Advanced Parameters** - Temperature, top-p, top-k, stop sequences
- **System Messages** - Context setting for code assistance
- **Authentication** - API key via `X-Api-Key` header
- **Error Handling** - Comprehensive error responses and rate limiting

#### **2. OAuth API (auth.anthropic.com)**
- **PKCE OAuth 2.0 Flow** - Enhanced security with Proof Key for Code Exchange
- **Authorization Endpoint** - `/oauth2/auth` for user consent
- **Token Exchange** - `/oauth2/token` for code-to-token exchange
- **Refresh Tokens** - Token renewal for long-term access
- **Local Callback** - `localhost:3000/callback` redirect handling
- **Scope Management** - `anthropic.claude` permission scope
- **State Protection** - CSRF protection with random state parameters

#### **3. Telemetry API (telemetry.anthropic.com)**
- **Event Collection** - Anonymous usage analytics and error reporting
- **Privacy-First** - User-configurable data collection (can be disabled)
- **Event Types** - CLI start/exit, command execution, AI requests, errors
- **Client Identification** - Anonymous UUID-based client tracking
- **System Information** - OS, Node.js version, CLI version metadata
- **Batch Processing** - Efficient bulk event submission
- **Error Reporting** - Structured error categorization and context

### Key Claude Code CLI Features Documented

- **Terminal Integration** - Direct command-line interface with natural language
- **Codebase Understanding** - File system analysis and context gathering
- **Code Assistance** - AI-powered code explanation, editing, and debugging
- **Git Operations** - Automated commit creation and repository management
- **Security Model** - Local execution with secure API communication
- **Authentication Flow** - Seamless OAuth integration with token management
- **Privacy Controls** - Transparent telemetry with opt-out capabilities
- **Error Handling** - Comprehensive error classification and user guidance
- **Enterprise Integration** - Support for Bedrock and Vertex AI deployments
- **Cross-Platform** - Works on Windows, macOS, and Linux environments

---

## Configuration Options

### Custom Output Directory
```bash
openapi-generator-cli generate -g markdown -i <spec-url> -o ./custom-directory
```

### Skip Validation (Recommended)
```bash
--skip-validate-spec
```

### Additional Configuration
```bash
openapi-generator-cli generate \
  -g markdown \
  -i <spec-url> \
  -o ./output-directory \
  --skip-validate-spec \
  --additional-properties=projectName="Custom API Docs"
```

## Alternative Generators

Besides markdown, you can generate documentation in other formats:

```bash
# HTML documentation
openapi-generator-cli generate -g html2 -i <spec-url> -o ./html-docs

# Confluence documentation
openapi-generator-cli generate -g confluence -i <spec-url> -o ./confluence-docs

# AsciiDoc documentation
openapi-generator-cli generate -g asciidoc -i <spec-url> -o ./asciidoc-docs
```

## Python Client Generation

Generate Python clients for these APIs:

```bash
# OpenAI Python client
openapi-generator-cli generate -g python -i https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml -o ./openai-python-client

# Anthropic Python client
openapi-generator-cli generate -g python -i https://raw.githubusercontent.com/laszukdawid/anthropic-openapi-spec/main/hosted_spec.yaml -o ./anthropic-python-client

# OpenRouter Python client
openapi-generator-cli generate -g python -i openrouter-openapi.yaml -o ./openrouter-python-client

# LiteLLM Python client
openapi-generator-cli generate -g python -i https://litellm-api.up.railway.app/openapi.json -o ./litellm-python-client

# Claude Code CLI Python client
openapi-generator-cli generate -g python -i claude-code-openapi.yaml -o ./claude-code-python-client
```

## Troubleshooting

### Common Issues

1. **Validation Errors**: Use `--skip-validate-spec` flag
2. **Network Issues**: Download the YAML file locally first
3. **Permission Errors**: Ensure output directory is writable
4. **Missing Dependencies**: Reinstall openapi-generator-cli

### Manual Download and Generation

If direct URL access fails:

```bash
# Download specification manually
curl -o openai-spec.yaml https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml

# Generate from local file
openapi-generator-cli generate -g markdown -i ./openai-spec.yaml -o ./openai-docs --skip-validate-spec
```

## Benefits

✅ **Comprehensive Documentation** - Complete API reference with examples  
✅ **Searchable Format** - Easy to navigate markdown structure  
✅ **Version Control Friendly** - Track documentation changes over time  
✅ **Multiple Output Formats** - Markdown, HTML, Confluence, AsciiDoc  
✅ **Client Code Generation** - Generate SDKs in 40+ programming languages  
✅ **Automated Updates** - Regenerate docs when API specifications change  
✅ **Cross-Platform** - Works on Windows, macOS, and Linux  
✅ **Integration Ready** - Integrate into CI/CD pipelines  
✅ **Enterprise Features** - Complete enterprise-grade API documentation  
✅ **Multi-Provider Support** - Unified documentation across AI providers  

## Use Cases

- **API Documentation Websites** - Generate beautiful, searchable docs
- **Internal Developer Resources** - Comprehensive API references for teams
- **SDK Development** - Generate client libraries in multiple languages
- **API Integration Planning** - Understand endpoints and data models
- **Compliance Documentation** - Maintain up-to-date API documentation
- **Multi-Provider Integration** - Compare and contrast different AI APIs
- **Enterprise Deployment** - Document complex enterprise features and configurations
- **Proxy Server Integration** - Unified API interface documentation

## Resources

- [OpenAPI Generator CLI GitHub](https://github.com/OpenAPITools/openapi-generator-cli)
- [OpenAPI Generator Documentation](https://openapi-generator.tech/)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Anthropic API Documentation](https://docs.anthropic.com/claude/reference)
- [OpenRouter API Documentation](https://openrouter.ai/docs)
- [LiteLLM Documentation](https://docs.litellm.ai/)

---

## Complete Solution Summary

### **What This Guide Accomplishes:**

1. **✅ OpenAI API Documentation**
   - Used official OpenAI OpenAPI specification
   - Generated 944-line comprehensive markdown docs
   - Covers all endpoints: Chat, Images, Audio, Files, Fine-tuning, etc.
   - Complete model schemas and parameter documentation

2. **✅ Anthropic API Documentation**  
   - Used community-maintained OpenAPI specification
   - Generated 173-line documentation
   - Covers Messages, Batches, and Text Completions APIs
   - Beta features and Claude-specific functionality

3. **✅ OpenRouter API Documentation**
   - **Created custom OpenAPI specification** (since none existed publicly)
   - Generated comprehensive documentation for:
     - Model routing and fallback strategies
     - 300+ AI models from multiple providers
     - OpenAI-compatible API with extensions
     - Credit management and usage tracking

4. **✅ LiteLLM API Documentation**
   - **Used live OpenAPI specification** from LiteLLM proxy server
   - Generated extensive documentation (626-line README) covering:
     - Universal proxy for 100+ LLM APIs
     - Enterprise management features (teams, orgs, budgets)
     - Advanced caching and batch processing
     - Content safety and guardrails
     - Provider-specific pass-through APIs
     - SCIM v2 and SSO integration

5. **✅ Claude Code CLI API Documentation**
   - **Created custom OpenAPI specification** based on source code analysis
   - Generated comprehensive documentation covering:
     - Claude API for AI chat completions and code assistance
     - OAuth API for secure PKCE authentication flow
     - Telemetry API for privacy-compliant analytics
     - Terminal integration and codebase understanding
     - Enterprise deployments with Bedrock/Vertex AI support

### **Generated Files Structure:**

```
├── openai-api-docs/
│   ├── README.md (944 lines)
│   ├── Apis/ (9 endpoint files)
│   └── Models/ (50+ model schemas)
├── anthropic-api-docs/
│   ├── README.md (173 lines)
│   ├── Apis/ (3 endpoint files)
│   └── Models/ (15+ model schemas)
├── openrouter-api-docs/
│   ├── README.md (59 lines)
│   ├── Apis/ (5 endpoint files)
│   └── Models/ (30+ model schemas)
├── litellm-api-docs/
│   ├── README.md (626 lines)
│   ├── Apis/ (43+ endpoint files)
│   └── Models/ (100+ model schemas)
├── claude-api-docs/
│   ├── README.md (42 lines)
│   ├── Apis/ (3 endpoint files)
│   └── Models/ (11 model schemas)
├── openrouter-openapi.yaml (custom specification)
└── claude-code-openapi.yaml (custom specification)
```

### **Key Features of This Solution:**

✅ **Complete Coverage** - All five major AI API providers and tools  
✅ **Step-by-step Instructions** - Easy-to-follow commands  
✅ **Troubleshooting Guide** - Common issues and solutions  
✅ **Multiple Output Formats** - Markdown, HTML, Python clients  
✅ **Custom OpenAPI Specs** - Created from scratch where needed  
✅ **Professional Documentation** - Industry-standard format  
✅ **Production Ready** - Suitable for team documentation and integration  
✅ **Enterprise Features** - Complete enterprise-grade API documentation  
✅ **Universal Proxy Support** - LiteLLM unified interface documentation  

### **Use This Guide For:**

- **API Integration Projects** - Understand endpoints and data models
- **Team Documentation** - Comprehensive reference for developers
- **SDK Development** - Generate client libraries in 40+ languages
- **Compliance Requirements** - Maintain up-to-date API documentation
- **Multi-Provider Strategies** - Compare and contrast different AI APIs
- **Automated Documentation** - Integrate into CI/CD pipelines
- **Enterprise Deployments** - Document complex multi-tenant configurations
- **Proxy Server Integration** - Unified API interface documentation

---

**Generated Documentation Files:**
- `./openai-api-docs/` - OpenAI API documentation
- `./anthropic-api-docs/` - Anthropic API documentation  
- `./openrouter-api-docs/` - OpenRouter API documentation
- `./litellm-api-docs/` - LiteLLM universal proxy API documentation
- `./claude-api-docs/` - Claude Code CLI API documentation
- `openrouter-openapi.yaml` - Custom OpenRouter OpenAPI specification
- `claude-code-openapi.yaml` - Custom Claude Code CLI OpenAPI specification 