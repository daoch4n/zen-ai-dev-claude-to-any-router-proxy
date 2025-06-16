# OpenRouter Anthropic Server Documentation

This directory contains comprehensive documentation for the OpenRouter Anthropic Server v2.0, a production-ready proxy server with enhanced Claude Code CLI support, universal AI streaming, and advanced error handling.

## 📋 **Documentation Index**

### 🚀 **Getting Started**
- **[00-master-implementation-plan.md](00-master-implementation-plan.md)** - Master implementation plan and project overview
- **[01-project-overview.md](01-project-overview.md)** - Project status, achievements, and enterprise readiness
- **[02-api-reference.md](02-api-reference.md)** - Complete API reference and endpoints documentation

### 🏗️ **Architecture & Implementation**
- **[03-architecture.md](03-architecture.md)** - System architecture and design patterns
- **[04-tool-execution-summary.md](04-tool-execution-summary.md)** - Tool execution system overview
- **[05-production-deployment-guide.md](05-production-deployment-guide.md)** - Production deployment and scaling guide

### 🧪 **Testing & Quality Assurance**
- **[06-claude-code-cli-testing-plan.md](06-claude-code-cli-testing-plan.md)** - Comprehensive Claude Code CLI testing plan with Anthropic best practices
- **[07-enhanced-error-handling.md](07-enhanced-error-handling.md)** - Enhanced error handling & debug logging system

### 📊 **Implementation Status & Progress**
- **[08-implementation-status.md](08-implementation-status.md)** - Current implementation status and progress
- **[09-project-completion-summary.md](09-project-completion-summary.md)** - Project completion summary and achievements
- **[13-implementation-summary.md](13-implementation-summary.md)** - Technical implementation summary

### 🔧 **API Enhancement & Configuration**
- **[10-api-enhancement-phases.md](10-api-enhancement-phases.md)** - API enhancement phases and roadmap
- **[11-api-conversion-guide.md](11-api-conversion-guide.md)** - API conversion guide and compatibility
- **[15-claude-code-openai-models-config.md](15-claude-code-openai-models-config.md)** - Configure Claude Code to use OpenAI/other models via proxy
- **[16-azure-databricks-guide.md](16-azure-databricks-guide.md)** - Comprehensive Azure Databricks Claude integration guide
- **[17-unified-proxy-backend-guide.md](17-unified-proxy-backend-guide.md)** - Unified proxy backend configuration and routing system
- **[18-model-configuration.md](18-model-configuration.md)** - Model configuration and environment setup
- **[19-litellm-bypass-implementation-plan.md](19-litellm-bypass-implementation-plan.md)** - LiteLLM bypass implementation plan

### 🛠️ **Operations & Maintenance**
- **[12-logs-management.md](12-logs-management.md)** - Complete logs directory consolidation and management
- **[14-troubleshooting-logs-consolidation.md](14-troubleshooting-logs-consolidation.md)** - Troubleshooting guide for logs consolidation

### 📁 **API Documentation**
- **[openapi/](openapi/)** - OpenAPI specifications and generated documentation
  - Anthropic API docs
  - OpenAI API docs  
  - OpenRouter API docs
  - LiteLLM API docs
  - Claude API docs

## 🎯 **Quick Navigation by Use Case**

### For Developers
1. **Setup**: Start with [01-project-overview.md](01-project-overview.md) and [18-model-configuration.md](18-model-configuration.md)
2. **Backend Configuration**: Configure with [17-unified-proxy-backend-guide.md](17-unified-proxy-backend-guide.md)
3. **Azure Databricks**: Set up Azure integration with [16-azure-databricks-guide.md](16-azure-databricks-guide.md)
4. **Claude Code + OpenAI**: Configure with [15-claude-code-openai-models-config.md](15-claude-code-openai-models-config.md)
5. **Architecture**: Review [03-architecture.md](03-architecture.md) 
6. **API Usage**: Check [02-api-reference.md](02-api-reference.md)
7. **Tool Development**: See [04-tool-execution-summary.md](04-tool-execution-summary.md)
8. **Error Handling**: Use [07-enhanced-error-handling.md](07-enhanced-error-handling.md)

### For Testers
1. **Testing Plan**: Follow [06-claude-code-cli-testing-plan.md](06-claude-code-cli-testing-plan.md)
2. **API Conversion**: Reference [11-api-conversion-guide.md](11-api-conversion-guide.md)
3. **Troubleshooting**: Use [14-troubleshooting-logs-consolidation.md](14-troubleshooting-logs-consolidation.md)

### For Operators
1. **Deployment**: Start with [05-production-deployment-guide.md](05-production-deployment-guide.md)
2. **Backend Configuration**: Reference [17-unified-proxy-backend-guide.md](17-unified-proxy-backend-guide.md)
3. **Logs Management**: Use [12-logs-management.md](12-logs-management.md)
4. **Error Debugging**: Reference [07-enhanced-error-handling.md](07-enhanced-error-handling.md)
5. **Configuration**: Check [18-model-configuration.md](18-model-configuration.md)

### For Project Managers
1. **Project Status**: Review [01-project-overview.md](01-project-overview.md) for achievements and enterprise readiness
2. **Master Plan**: Check [00-master-implementation-plan.md](00-master-implementation-plan.md)
3. **Implementation Status**: See [08-implementation-status.md](08-implementation-status.md)
4. **Completion Summary**: Review [09-project-completion-summary.md](09-project-completion-summary.md)
5. **Technical Summary**: Check [13-implementation-summary.md](13-implementation-summary.md)

## 🔄 **Documentation Updates**

This documentation has been recently updated to include:

### ✅ **Enhanced Error Handling System**
- Hash-based error tracking with unique identifiers
- Server instance separation for multi-deployment environments
- Comprehensive debugging endpoints and search capabilities
- Integration with existing error logging systems

### ✅ **Logs Directory Consolidation**
- Unified logs structure under `/logs` directory
- Clear separation of debug, error, and MCP logs
- Elimination of duplicate logging directories
- Streamlined log management and troubleshooting

### ✅ **Claude Code CLI Integration**
- Comprehensive testing plan with Anthropic best practices
- CLAUDE.md file support and thinking modes
- Tool allowlist management and permission systems
- Advanced workflow patterns and optimization techniques

### ✅ **Universal AI Streaming Platform**
- Multi-provider streaming support (7+ providers)
- Claude model auto-detection and intelligent routing
- Cross-provider format conversion and compatibility
- Performance optimization with universal caching

## 📚 **Additional Resources**

### External References
- [Anthropic Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [OpenRouter API Documentation](https://openrouter.ai/docs)
- [LiteLLM Documentation](https://docs.litellm.ai/)

### Project Resources
- **Configuration Files**: See `/configs` directory
- **Scripts**: See `/scripts` directory for utility scripts
- **Tests**: See `/tests` directory for test suites
- **Memory Bank**: See `/memory-bank` directory for project context

## 🆕 **What's New**

### Recent Additions
- **Unified Proxy Backend System**: Single PROXY_BACKEND configuration for three backend modes (OPENROUTER, AZURE_DATABRICKS, LITELLM_OPENROUTER)
- **Azure Databricks Integration**: Full Azure Databricks Claude endpoints integration with transparent proxy functionality
- **Enhanced Exception Handling**: Complete hash-based error tracking system
- **Logs Consolidation**: Unified logging structure with clear purposes
- **Universal Streaming**: Multi-provider AI streaming platform
- **Anthropic Best Practices**: Full integration of official Claude Code recommendations
- **Advanced Testing**: Comprehensive testing plan with 21 test phases
- **Production Ready**: Complete deployment and scaling documentation

### Documentation Organization
- **Numbered Structure**: Clear progression from setup to advanced topics
- **Use Case Navigation**: Quick access by role and need
- **Cross-References**: Linked documentation for easy navigation
- **Troubleshooting**: Dedicated troubleshooting and maintenance guides

## 📚 Documentation Structure

### Core Documentation
- **[🚀 Quick Start Guide](01-quick-start.md)** - Get up and running in 5 minutes
- **[🔌 API Reference](02-api-reference.md)** - Complete API documentation with examples
- **[🏗️ Architecture Overview](03-architecture.md)** - System design and component relationships
- **[🛠️ Tool Documentation](04-tool-documentation.md)** - Detailed guide for all 15 supported tools
- **[🚀 Deployment Guide](05-production-deployment-guide.md)** - Production deployment instructions

### Advanced Topics
- **[🔄 Unified Proxy Backend Guide](17-unified-proxy-backend-guide.md)** - Backend configuration and routing
- **[💬 LiteLLM Messages Backend Guide](18-litellm-messages-backend-guide.md)** - Native Anthropic format support via LiteLLM
- **[☁️ Azure Databricks Integration](16-azure-databricks-guide.md)** - Comprehensive Azure Databricks Claude guide
- **[🔧 Tool Security Configuration](12-tool-security-configuration.md)** - Security settings for tool execution

---

**For questions or contributions to this documentation, please refer to the project's contributing guidelines and issue tracker.** 