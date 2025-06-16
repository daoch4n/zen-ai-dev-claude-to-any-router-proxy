# LiteLLM Bypass Implementation Plan

## 🎯 Project Overview

**Objective**: Implement direct OpenRouter API integration bypassing LiteLLM with our own API schema converter

**Current Flow**: 
```
Claude Code → anthropic-format → FastAPI → anthropic-format → 
our API schema converter → openai-format → LiteLLM → OpenRouter
```

**Target Flow**:
```
Request:  Claude Code → anthropic-format → FastAPI → anthropic-format → 
          our API schema converter → openai-format → OpenRouter
Response: OpenRouter → openai-format → our API schema converter → 
          anthropic-format → FastAPI → anthropic-format → Claude Code
```

## 📋 Implementation Phases

### Phase 1: Configuration & Foundation (Days 1-2)

#### 1.1 Configuration Enhancement 
**File**: `src/utils/config.py`
- Add `bypass_litellm_enabled: bool = False`
- Add `openrouter_api_base: str = "https://openrouter.ai/api/v1"`
- Add `openrouter_direct_timeout: int = 120`
- Add `openrouter_direct_retries: int = 3`
- Add environment variable mapping

#### 1.2 OpenAI Format Models
**File**: `src/models/openai.py` (New)
- `OpenAIMessage` class for OpenAI message format
- `OpenAIChatRequest` class for OpenAI chat completion requests
- `OpenAIChatResponse` class for OpenAI responses
- Support for tools, streaming, and all OpenAI parameters

### Phase 2: Core Services (Days 3-5)

#### 2.1 Direct OpenRouter Client
**File**: `src/services/openrouter_direct_client.py` (New)
- `OpenRouterDirectClient` class extending `BaseService`
- `chat_completion()` method for non-streaming requests
- `chat_completion_stream()` method for streaming requests
- HTTP client using httpx with proper authentication
- Retry logic and error handling

#### 2.2 API Schema Converter
**File**: `src/services/anthropic_openai_converter.py` (New)
- `AnthropicOpenAIConverter` class extending `BaseService`
- `anthropic_to_openai()` - Convert Anthropic → OpenAI format
- `openai_to_anthropic_response()` - Convert OpenAI → Anthropic format
- `convert_streaming_chunk()` - Handle streaming conversions
- Tool format conversion (anthropic tools ↔ openai functions)
- Multimodal content handling

#### 2.3 Bypass Flow Service
**File**: `src/services/litellm_bypass_flow.py` (New)
- `LiteLLMBypassFlow` class extending `ConversionService`
- `convert()` method for complete bypass flow orchestration
- `convert_streaming()` method for streaming bypass
- Fallback to LiteLLM on errors
- Error handling and logging

### Phase 3: Integration (Days 6-8)

#### 3.1 Router Updates
**File**: `src/routers/messages.py` (Modified)
- Update `/messages` endpoint to check bypass flag
- Update `/messages/stream` endpoint for streaming bypass
- Add bypass-specific orchestration calls
- Maintain backward compatibility

#### 3.2 Orchestrator Enhancement
**File**: `src/orchestrators/conversation_orchestrator.py` (Modified)
- `process_bypass_request_orchestrated()` function
- `process_bypass_stream_orchestrated()` function
- Integration with existing middleware and validation
- Error handling and logging consistency

#### 3.3 Health Check Integration
**File**: `src/routers/health.py` (Modified)
- Add `check_openrouter_direct_health()` function
- Test direct OpenRouter connectivity when bypass enabled
- Validate API key and model availability
- Include bypass status in health endpoints

### Phase 4: Testing & Validation (Days 9-15)

#### 4.1 Unit Tests
- `tests/services/test_openrouter_direct_client.py`
- `tests/services/test_anthropic_openai_converter.py`
- `tests/services/test_litellm_bypass_flow.py`
- `tests/utils/test_bypass_configuration.py`

#### 4.2 Integration Tests
- `tests/integration/test_bypass_flow_integration.py`
- End-to-end bypass flow testing
- Fallback mechanism validation
- Streaming functionality testing
- Performance comparison testing

#### 4.3 Configuration Tests
- Feature flag behavior validation
- Environment variable handling
- Configuration validation testing
- Error scenario testing

## 🔧 Technical Implementation Details

### Configuration Environment Variables
```bash
# Add to .env
BYPASS_LITELLM_ENABLED=true          # Enabled by default for optimal performance
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_DIRECT_TIMEOUT=120
OPENROUTER_DIRECT_RETRIES=3
OPENROUTER_DIRECT_MODEL_FORMAT=anthropic/claude-sonnet-4
```

### Key Service Interfaces

#### OpenRouterDirectClient
```python
class OpenRouterDirectClient(BaseService):
    async def chat_completion(self, request: OpenAIChatRequest) -> Dict[str, Any]
    async def chat_completion_stream(self, request: OpenAIChatRequest) -> AsyncIterator[Dict[str, Any]]
```

#### AnthropicOpenAIConverter  
```python
class AnthropicOpenAIConverter(BaseService):
    def anthropic_to_openai(self, request: MessagesRequest) -> OpenAIChatRequest
    def openai_to_anthropic_response(self, openai_response: Dict[str, Any], 
                                   original_request: MessagesRequest) -> MessagesResponse
    def convert_streaming_chunk(self, openai_chunk: Dict[str, Any]) -> Dict[str, Any]
```

#### LiteLLMBypassFlow
```python
class LiteLLMBypassFlow(ConversionService):
    async def convert(self, source: MessagesRequest, **kwargs) -> ConversionResult
    async def convert_streaming(self, source: MessagesRequest, **kwargs) -> AsyncIterator[Dict[str, Any]]
```

## 🚀 Benefits

1. **Backward Compatibility**: Existing LiteLLM flow preserved
2. **Feature Flag Control**: Enable/disable without code changes
3. **Graceful Fallback**: Automatic fallback to LiteLLM on errors
4. **Performance**: Direct API calls eliminate proxy overhead
5. **Easy Testing**: Independent testing of both flows
6. **Monitoring**: Separate metrics for bypass vs LiteLLM

## ⏰ Timeline

- **Week 1**: Configuration, models, and core services
- **Week 2**: Integration, orchestration, and initial testing  
- **Week 3**: Comprehensive testing, optimization, and documentation

## 📊 Success Metrics

- Bypass flow functional with 100% feature parity
- Performance improvement (reduced latency)
- Zero regression in existing LiteLLM functionality
- Comprehensive test coverage (>95%)
- Graceful fallback working in error scenarios
- Production-ready deployment capability

## 🔄 Migration Strategy

1. **Phase 1**: Implement with bypass enabled by default for optimal performance
2. **Phase 2**: Comprehensive testing in development/testing environments  
3. **Phase 3**: Production deployment with automatic LiteLLM fallback
4. **Phase 4**: Monitor performance gains and optimize bypass flow further

## 📝 Documentation Updates Required

- Update API documentation for bypass mode
- Add configuration guide for bypass settings
- Update deployment documentation
- Add troubleshooting guide for bypass issues
- Update performance benchmarking documentation

## 🎛️ Feature Flag Strategy

- `BYPASS_LITELLM_ENABLED=true` by default (optimized for performance)
- Environment-based enable/disable
- Runtime configuration validation
- Graceful degradation if configuration invalid
- Automatic fallback to LiteLLM on bypass failures
- Monitoring and alerting for bypass failures 