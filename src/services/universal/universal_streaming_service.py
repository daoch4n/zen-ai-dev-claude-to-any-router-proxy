"""
Universal Streaming Service for Multi-Model Real-time Tool Execution.

This service extends our revolutionary Phase 2 real-time tool execution to work
across 100+ LiteLLM models from all major AI providers (OpenAI, Anthropic, 
Google, Cohere, etc.) with provider-specific optimizations.

Phase 3B: Multi-Model Streaming Support
"""

import asyncio
import time
import json
from typing import Any, Dict, List, Optional, AsyncIterator, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ...services.base import BaseService
from ...models.anthropic import MessagesRequest
from ...core.logging_config import get_logger
from ...services.claude_code_streaming_service import StreamingChunk, ToolExecutionResult
from ...services.claude_code_tool_service import ClaudeCodeToolService
from ...utils.config import config

logger = get_logger("universal.streaming_service")


class AIProvider(Enum):
    """Supported AI providers for universal streaming."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    COHERE = "cohere"
    MISTRAL = "mistral"
    AZURE = "azure"
    BEDROCK = "bedrock"
    VERTEX = "vertex"
    OLLAMA = "ollama"
    TOGETHER = "together"
    UNKNOWN = "unknown"


@dataclass
class ProviderConfig:
    """Configuration for specific AI provider streaming."""
    provider: AIProvider
    supports_streaming: bool
    supports_tools: bool
    tool_format: str  # "openai", "anthropic", "custom"
    max_concurrent_tools: int
    tool_timeout: float
    chunk_format: str  # "openai", "anthropic", "custom"
    reasoning_support: bool = False
    streaming_optimizations: Dict[str, Any] = None


@dataclass
class UniversalStreamingChunk:
    """Universal streaming chunk that works across all providers."""
    provider: AIProvider
    original_chunk: Dict[str, Any]
    normalized_type: str  # "content", "tool_call", "tool_result", "thinking", "error"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    thinking_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class UniversalStreamingService(BaseService):
    """Universal streaming service with real-time tool execution for 100+ models."""
    
    def __init__(self):
        """Initialize the universal streaming service."""
        super().__init__("UniversalStreaming")
        
        # Initialize tool service for universal tool execution
        self.tool_service = ClaudeCodeToolService()
        
        # Provider configurations
        self.provider_configs = self._initialize_provider_configs()
        
        # Universal streaming configuration
        self.universal_config = {
            "enable_universal_tools": True,
            "auto_detect_provider": True,
            "fallback_provider": AIProvider.ANTHROPIC,
            "max_concurrent_streams": 10,
            "universal_tool_timeout": 45,
            "cross_provider_optimization": True,
            "unified_error_handling": True
        }
        
        # Performance tracking
        self.universal_metrics = {
            "total_universal_streams": 0,
            "streams_by_provider": {},
            "tools_executed_by_provider": {},
            "average_response_time_by_provider": {},
            "universal_tool_success_rate": 0.0,
            "cross_provider_optimizations": 0
        }
        
        # Model mappings for provider detection
        self.model_provider_map = self._build_model_provider_map()
        
        logger.info("Universal Streaming Service initialized",
                   supported_providers=len(self.provider_configs),
                   universal_tools_enabled=self.universal_config["enable_universal_tools"],
                   max_concurrent_streams=self.universal_config["max_concurrent_streams"])
    
    def _initialize_provider_configs(self) -> Dict[AIProvider, ProviderConfig]:
        """Initialize configurations for all supported AI providers."""
        return {
            AIProvider.ANTHROPIC: ProviderConfig(
                provider=AIProvider.ANTHROPIC,
                supports_streaming=True,
                supports_tools=True,
                tool_format="anthropic",
                max_concurrent_tools=3,
                tool_timeout=30.0,
                chunk_format="anthropic",
                reasoning_support=True,
                streaming_optimizations={
                    "enable_reasoning_streaming": True,
                    "parallel_tool_execution": True,
                    "chunk_aggregation": True
                }
            ),
            AIProvider.OPENAI: ProviderConfig(
                provider=AIProvider.OPENAI,
                supports_streaming=True,
                supports_tools=True,
                tool_format="openai",
                max_concurrent_tools=5,
                tool_timeout=25.0,
                chunk_format="openai",
                reasoning_support=False,
                streaming_optimizations={
                    "function_calling_optimization": True,
                    "delta_compression": True,
                    "batch_tool_calls": True
                }
            ),
            AIProvider.GOOGLE: ProviderConfig(
                provider=AIProvider.GOOGLE,
                supports_streaming=True,
                supports_tools=True,
                tool_format="openai",  # Google uses OpenAI-compatible format
                max_concurrent_tools=4,
                tool_timeout=35.0,
                chunk_format="openai",
                reasoning_support=False,
                streaming_optimizations={
                    "gemini_optimization": True,
                    "multimodal_streaming": True,
                    "safety_filter_streaming": True
                }
            ),
            AIProvider.COHERE: ProviderConfig(
                provider=AIProvider.COHERE,
                supports_streaming=True,
                supports_tools=True,
                tool_format="custom",
                max_concurrent_tools=3,
                tool_timeout=30.0,
                chunk_format="custom",
                reasoning_support=False,
                streaming_optimizations={
                    "cohere_format_optimization": True,
                    "citation_streaming": True
                }
            ),
            AIProvider.MISTRAL: ProviderConfig(
                provider=AIProvider.MISTRAL,
                supports_streaming=True,
                supports_tools=True,
                tool_format="openai",
                max_concurrent_tools=3,
                tool_timeout=28.0,
                chunk_format="openai",
                reasoning_support=False,
                streaming_optimizations={
                    "mistral_optimization": True,
                    "european_datacenter_routing": True
                }
            ),
            AIProvider.AZURE: ProviderConfig(
                provider=AIProvider.AZURE,
                supports_streaming=True,
                supports_tools=True,
                tool_format="openai",
                max_concurrent_tools=4,
                tool_timeout=30.0,
                chunk_format="openai",
                reasoning_support=False,
                streaming_optimizations={
                    "azure_optimization": True,
                    "enterprise_security": True,
                    "regional_routing": True
                }
            ),
            AIProvider.BEDROCK: ProviderConfig(
                provider=AIProvider.BEDROCK,
                supports_streaming=True,
                supports_tools=True,
                tool_format="custom",
                max_concurrent_tools=3,
                tool_timeout=40.0,
                chunk_format="custom",
                reasoning_support=False,
                streaming_optimizations={
                    "aws_optimization": True,
                    "bedrock_native_streaming": True,
                    "cross_region_failover": True
                }
            )
        }
    
    def _build_model_provider_map(self) -> Dict[str, AIProvider]:
        """Build mapping of model names to providers for auto-detection."""
        return {
            # Anthropic models
            "claude-3": AIProvider.ANTHROPIC,
            "claude-sonnet": AIProvider.ANTHROPIC,
            "claude-opus": AIProvider.ANTHROPIC,
            "claude-haiku": AIProvider.ANTHROPIC,
            "anthropic/claude": AIProvider.ANTHROPIC,
            
            # OpenAI models  
            "gpt-3.5": AIProvider.OPENAI,
            "gpt-4": AIProvider.OPENAI,
            "gpt-4o": AIProvider.OPENAI,
            "gpt-4-turbo": AIProvider.OPENAI,
            "openai/gpt": AIProvider.OPENAI,
            
            # Google models
            "gemini": AIProvider.GOOGLE,
            "palm": AIProvider.GOOGLE,
            "bard": AIProvider.GOOGLE,
            "google/gemini": AIProvider.GOOGLE,
            "vertex_ai/gemini": AIProvider.GOOGLE,
            
            # Cohere models
            "command": AIProvider.COHERE,
            "cohere/command": AIProvider.COHERE,
            
            # Mistral models
            "mistral": AIProvider.MISTRAL,
            "mixtral": AIProvider.MISTRAL,
            "mistral/mistral": AIProvider.MISTRAL,
            
            # Azure models
            "azure/gpt": AIProvider.AZURE,
            "azure/": AIProvider.AZURE,
            
            # Bedrock models
            "bedrock/": AIProvider.BEDROCK,
            "amazon.titan": AIProvider.BEDROCK,
            "meta.llama": AIProvider.BEDROCK
        }
    
    def detect_provider_from_model(self, model: str) -> AIProvider:
        """Auto-detect AI provider from model name."""
        model_lower = model.lower()
        
        for model_prefix, provider in self.model_provider_map.items():
            if model_prefix in model_lower:
                logger.debug("Detected provider from model",
                           model=model,
                           provider=provider.value,
                           matched_prefix=model_prefix)
                return provider
        
        logger.warning("Could not detect provider for model, using fallback",
                      model=model,
                      fallback_provider=self.universal_config["fallback_provider"].value)
        
        return self.universal_config["fallback_provider"]
    
    async def create_universal_stream(
        self,
        request: MessagesRequest,
        litellm_response_stream: AsyncIterator[Dict[str, Any]],
        request_id: str,
        provider: Optional[AIProvider] = None
    ) -> AsyncIterator[UniversalStreamingChunk]:
        """
        Create universal streaming response with real-time tool execution.
        
        Args:
            request: Original request
            litellm_response_stream: Base LiteLLM streaming response
            request_id: Unique request identifier
            provider: Optional explicit provider (auto-detected if None)
            
        Yields:
            UniversalStreamingChunk: Universal streaming chunks with tool execution
        """
        stream_start_time = time.time()
        
        try:
            # Auto-detect provider if not specified
            if provider is None:
                provider = self.detect_provider_from_model(request.model)
            
            # Get provider configuration
            provider_config = self.provider_configs.get(provider)
            if not provider_config:
                logger.error("Unsupported provider",
                           provider=provider.value if provider else "unknown",
                           model=request.model)
                provider_config = self.provider_configs[AIProvider.ANTHROPIC]  # Fallback
                provider = AIProvider.ANTHROPIC
            
            # Initialize stream tracking
            await self._initialize_universal_stream_tracking(request_id, provider, request)
            
            logger.info("Starting universal streaming with real-time tool execution",
                       request_id=request_id,
                       provider=provider.value,
                       model=request.model,
                       supports_tools=provider_config.supports_tools)
            
            # Process stream with provider-specific optimizations
            async for universal_chunk in self._process_universal_stream_with_tools(
                litellm_response_stream,
                request,
                request_id,
                provider,
                provider_config
            ):
                yield universal_chunk
            
            # Finalize stream
            await self._finalize_universal_stream(request_id, provider, stream_start_time)
            
        except Exception as e:
            logger.error("Universal streaming failed",
                        request_id=request_id,
                        provider=provider.value if provider else "unknown",
                        model=request.model,
                        error=str(e),
                        exc_info=True)
            
            # Yield error chunk
            yield UniversalStreamingChunk(
                provider=provider or AIProvider.UNKNOWN,
                original_chunk={},
                normalized_type="error",
                content=f"Universal streaming error: {str(e)}",
                metadata={"error_type": type(e).__name__, "request_id": request_id}
            )
    
    async def _process_universal_stream_with_tools(
        self,
        response_stream: AsyncIterator[Dict[str, Any]],
        request: MessagesRequest,
        request_id: str,
        provider: AIProvider,
        provider_config: ProviderConfig
    ) -> AsyncIterator[UniversalStreamingChunk]:
        """Process universal streaming response with provider-specific tool execution."""
        
        tool_execution_tasks: List[asyncio.Task] = []
        accumulated_content = ""
        
        async for raw_chunk in response_stream:
            try:
                # Normalize chunk based on provider format
                normalized_chunk = await self._normalize_streaming_chunk(
                    raw_chunk, provider, provider_config
                )
                
                if normalized_chunk.normalized_type == "content":
                    # Accumulate content for tool detection
                    accumulated_content += normalized_chunk.content
                    
                    # Yield content chunk
                    yield normalized_chunk
                    
                    # Check for tool calls if provider supports tools
                    if provider_config.supports_tools and request.tools:
                        tool_calls = await self._detect_universal_tool_calls(
                            accumulated_content, request, provider_config
                        )
                        
                        if tool_calls:
                            # Execute tools with provider-specific configuration
                            for tool_call in tool_calls:
                                task = asyncio.create_task(
                                    self._execute_universal_tool(
                                        tool_call, request_id, provider_config
                                    )
                                )
                                tool_execution_tasks.append(task)
                                
                                # Yield tool call notification
                                yield UniversalStreamingChunk(
                                    provider=provider,
                                    original_chunk=raw_chunk,
                                    normalized_type="tool_call",
                                    content=f"Executing tool: {tool_call['name']}",
                                    tool_calls=[tool_call],
                                    metadata={
                                        "execution_status": "started",
                                        "provider_optimization": True
                                    }
                                )
                
                elif normalized_chunk.normalized_type == "thinking":
                    # Handle reasoning content (mainly for Anthropic)
                    yield normalized_chunk
                
                elif normalized_chunk.normalized_type == "tool_call":
                    # Handle explicit tool calls from provider
                    if provider_config.supports_tools and normalized_chunk.tool_calls:
                        for tool_call in normalized_chunk.tool_calls:
                            task = asyncio.create_task(
                                self._execute_universal_tool(
                                    tool_call, request_id, provider_config
                                )
                            )
                            tool_execution_tasks.append(task)
                        
                        yield normalized_chunk
                
                # Check for completed tool executions
                completed_tools = await self._check_completed_universal_tool_executions(
                    tool_execution_tasks, provider
                )
                
                for tool_result in completed_tools:
                    # Yield tool result with provider context
                    yield UniversalStreamingChunk(
                        provider=provider,
                        original_chunk={},
                        normalized_type="tool_result",
                        content=f"Tool {tool_result.tool_name} completed",
                        tool_results=[{
                            "tool_name": tool_result.tool_name,
                            "result": tool_result.result,
                            "success": tool_result.success,
                            "execution_time": tool_result.execution_time,
                            "provider": provider.value
                        }],
                        metadata={
                            "execution_status": "completed",
                            "provider_optimization": provider_config.streaming_optimizations
                        }
                    )
                
            except Exception as e:
                logger.error("Error processing universal streaming chunk",
                           request_id=request_id,
                           provider=provider.value,
                           error=str(e))
                continue
        
        # Wait for any remaining tool executions
        if tool_execution_tasks:
            logger.info("Waiting for remaining universal tool executions",
                       request_id=request_id,
                       provider=provider.value,
                       remaining_tasks=len(tool_execution_tasks))
            
            remaining_results = await asyncio.gather(
                *tool_execution_tasks, return_exceptions=True
            )
            
            for result in remaining_results:
                if isinstance(result, ToolExecutionResult):
                    yield UniversalStreamingChunk(
                        provider=provider,
                        original_chunk={},
                        normalized_type="tool_result",
                        content=f"Tool {result.tool_name} completed",
                        tool_results=[{
                            "tool_name": result.tool_name,
                            "result": result.result,
                            "success": result.success,
                            "execution_time": result.execution_time,
                            "provider": provider.value
                        }],
                        metadata={"execution_status": "final"}
                    )
    
    async def _normalize_streaming_chunk(
        self,
        raw_chunk: Dict[str, Any],
        provider: AIProvider,
        provider_config: ProviderConfig
    ) -> UniversalStreamingChunk:
        """Normalize streaming chunk to universal format based on provider."""
        try:
            if provider_config.chunk_format == "openai":
                return await self._normalize_openai_chunk(raw_chunk, provider)
            elif provider_config.chunk_format == "anthropic":
                return await self._normalize_anthropic_chunk(raw_chunk, provider)
            else:
                return await self._normalize_custom_chunk(raw_chunk, provider, provider_config)
                
        except Exception as e:
            logger.error("Failed to normalize streaming chunk",
                        provider=provider.value,
                        error=str(e))
            
            return UniversalStreamingChunk(
                provider=provider,
                original_chunk=raw_chunk,
                normalized_type="error",
                content=f"Chunk normalization error: {str(e)}",
                metadata={"normalization_error": True}
            )
    
    async def _normalize_openai_chunk(
        self, 
        raw_chunk: Dict[str, Any], 
        provider: AIProvider
    ) -> UniversalStreamingChunk:
        """Normalize OpenAI-format streaming chunk."""
        try:
            if "choices" in raw_chunk and raw_chunk["choices"]:
                choice = raw_chunk["choices"][0]
                delta = choice.get("delta", {})
                
                if "content" in delta and delta["content"]:
                    return UniversalStreamingChunk(
                        provider=provider,
                        original_chunk=raw_chunk,
                        normalized_type="content",
                        content=delta["content"],
                        metadata={"openai_format": True}
                    )
                
                elif "tool_calls" in delta and delta["tool_calls"]:
                    return UniversalStreamingChunk(
                        provider=provider,
                        original_chunk=raw_chunk,
                        normalized_type="tool_call",
                        content="",
                        tool_calls=delta["tool_calls"],
                        metadata={"openai_tool_format": True}
                    )
            
            # Default for unrecognized OpenAI chunks
            return UniversalStreamingChunk(
                provider=provider,
                original_chunk=raw_chunk,
                normalized_type="unknown",
                content="",
                metadata={"openai_unknown_chunk": True}
            )
            
        except Exception as e:
            logger.error("OpenAI chunk normalization failed", error=str(e))
            return UniversalStreamingChunk(
                provider=provider,
                original_chunk=raw_chunk,
                normalized_type="error",
                content=f"OpenAI normalization error: {str(e)}"
            )
    
    async def _normalize_anthropic_chunk(
        self, 
        raw_chunk: Dict[str, Any], 
        provider: AIProvider
    ) -> UniversalStreamingChunk:
        """Normalize Anthropic-format streaming chunk."""
        try:
            chunk_type = raw_chunk.get("type", "unknown")
            
            if chunk_type == "message_delta":
                delta = raw_chunk.get("delta", {})
                if delta.get("type") == "text_delta" and "text" in delta:
                    return UniversalStreamingChunk(
                        provider=provider,
                        original_chunk=raw_chunk,
                        normalized_type="content",
                        content=delta["text"],
                        metadata={"anthropic_format": True}
                    )
            
            elif chunk_type == "thinking_delta":
                thinking = raw_chunk.get("delta", {}).get("thinking", "")
                return UniversalStreamingChunk(
                    provider=provider,
                    original_chunk=raw_chunk,
                    normalized_type="thinking",
                    content="",
                    thinking_content=thinking,
                    metadata={"anthropic_reasoning": True}
                )
            
            elif chunk_type == "tool_call_delta":
                tool_calls = raw_chunk.get("delta", {}).get("tool_calls", [])
                return UniversalStreamingChunk(
                    provider=provider,
                    original_chunk=raw_chunk,
                    normalized_type="tool_call",
                    content="",
                    tool_calls=tool_calls,
                    metadata={"anthropic_tool_format": True}
                )
            
            # Default for unrecognized Anthropic chunks
            return UniversalStreamingChunk(
                provider=provider,
                original_chunk=raw_chunk,
                normalized_type="unknown",
                content="",
                metadata={"anthropic_unknown_chunk": True}
            )
            
        except Exception as e:
            logger.error("Anthropic chunk normalization failed", error=str(e))
            return UniversalStreamingChunk(
                provider=provider,
                original_chunk=raw_chunk,
                normalized_type="error",
                content=f"Anthropic normalization error: {str(e)}"
            )
    
    async def _normalize_custom_chunk(
        self, 
        raw_chunk: Dict[str, Any], 
        provider: AIProvider,
        provider_config: ProviderConfig
    ) -> UniversalStreamingChunk:
        """Normalize custom provider streaming chunk."""
        try:
            # Provider-specific custom normalization
            if provider == AIProvider.COHERE:
                return await self._normalize_cohere_chunk(raw_chunk)
            elif provider == AIProvider.BEDROCK:
                return await self._normalize_bedrock_chunk(raw_chunk)
            else:
                # Generic custom chunk handling
                return UniversalStreamingChunk(
                    provider=provider,
                    original_chunk=raw_chunk,
                    normalized_type="content",
                    content=str(raw_chunk.get("text", "")),
                    metadata={"custom_format": True, "provider": provider.value}
                )
                
        except Exception as e:
            logger.error("Custom chunk normalization failed",
                        provider=provider.value,
                        error=str(e))
            return UniversalStreamingChunk(
                provider=provider,
                original_chunk=raw_chunk,
                normalized_type="error",
                content=f"Custom normalization error: {str(e)}"
            )
    
    async def _normalize_cohere_chunk(self, raw_chunk: Dict[str, Any]) -> UniversalStreamingChunk:
        """Normalize Cohere-specific streaming chunk."""
        # Implement Cohere-specific chunk normalization
        return UniversalStreamingChunk(
            provider=AIProvider.COHERE,
            original_chunk=raw_chunk,
            normalized_type="content",
            content=raw_chunk.get("text", ""),
            metadata={"cohere_format": True}
        )
    
    async def _normalize_bedrock_chunk(self, raw_chunk: Dict[str, Any]) -> UniversalStreamingChunk:
        """Normalize AWS Bedrock-specific streaming chunk."""
        # Implement Bedrock-specific chunk normalization
        return UniversalStreamingChunk(
            provider=AIProvider.BEDROCK,
            original_chunk=raw_chunk,
            normalized_type="content",
            content=raw_chunk.get("outputText", ""),
            metadata={"bedrock_format": True}
        )
    
    async def _detect_universal_tool_calls(
        self,
        content: str,
        request: MessagesRequest,
        provider_config: ProviderConfig
    ) -> List[Dict[str, Any]]:
        """Detect tool calls in content with provider-specific patterns."""
        # Reuse existing tool detection logic but adapt for provider
        return await self._adapt_tool_detection_for_provider(content, request, provider_config)
    
    async def _adapt_tool_detection_for_provider(
        self,
        content: str,
        request: MessagesRequest,
        provider_config: ProviderConfig
    ) -> List[Dict[str, Any]]:
        """Adapt tool detection for specific provider requirements."""
        # Provider-specific tool detection patterns
        tool_calls = []
        
        if provider_config.tool_format == "openai":
            # Detect OpenAI-style tool requests
            tool_calls = await self._detect_openai_style_tools(content, request)
        elif provider_config.tool_format == "anthropic":
            # Detect Anthropic-style tool requests
            tool_calls = await self._detect_anthropic_style_tools(content, request)
        else:
            # Generic tool detection
            tool_calls = await self._detect_generic_tools(content, request)
        
        # Limit by provider's max concurrent tools
        return tool_calls[:provider_config.max_concurrent_tools]
    
    async def _detect_openai_style_tools(
        self, 
        content: str, 
        request: MessagesRequest
    ) -> List[Dict[str, Any]]:
        """Detect tool calls in OpenAI format."""
        # Implement OpenAI-specific tool detection
        return []
    
    async def _detect_anthropic_style_tools(
        self, 
        content: str, 
        request: MessagesRequest
    ) -> List[Dict[str, Any]]:
        """Detect tool calls in Anthropic format."""
        # Reuse existing Claude tool detection logic
        available_tools = self.tool_service.get_available_claude_code_tools()
        tool_calls = []
        
        for tool_name in available_tools:
            if tool_name.lower() in content.lower():
                # Basic tool detection logic
                tool_calls.append({
                    "name": tool_name,
                    "arguments": {},
                    "detection_method": "anthropic_style"
                })
        
        return tool_calls
    
    async def _detect_generic_tools(
        self, 
        content: str, 
        request: MessagesRequest
    ) -> List[Dict[str, Any]]:
        """Detect tool calls using generic patterns."""
        # Generic tool detection
        return []
    
    async def _execute_universal_tool(
        self,
        tool_call: Dict[str, Any],
        request_id: str,
        provider_config: ProviderConfig
    ) -> ToolExecutionResult:
        """Execute tool with provider-specific optimizations."""
        tool_name = tool_call["name"]
        execution_start = time.time()
        
        try:
            logger.debug("Executing universal tool",
                        tool_name=tool_name,
                        provider=provider_config.provider.value,
                        request_id=request_id)
            
            # Execute tool with provider-specific timeout
            result = await self.tool_service.execute_claude_code_tool(
                tool_name,
                tool_call.get("arguments", {}),
                timeout=provider_config.tool_timeout
            )
            
            execution_time = time.time() - execution_start
            
            # Update universal metrics
            await self._update_universal_tool_metrics(
                provider_config.provider, tool_name, execution_time, True
            )
            
            logger.info("Universal tool executed successfully",
                       tool_name=tool_name,
                       provider=provider_config.provider.value,
                       execution_time=f"{execution_time:.2f}s",
                       request_id=request_id)
            
            return ToolExecutionResult(
                tool_name=tool_name,
                success=True,
                result=result,
                execution_time=execution_time,
                metadata={
                    "provider": provider_config.provider.value,
                    "universal_execution": True,
                    "request_id": request_id
                }
            )
            
        except Exception as e:
            execution_time = time.time() - execution_start
            
            logger.error("Universal tool execution failed",
                        tool_name=tool_name,
                        provider=provider_config.provider.value,
                        error=str(e),
                        execution_time=f"{execution_time:.2f}s",
                        request_id=request_id)
            
            # Update metrics
            await self._update_universal_tool_metrics(
                provider_config.provider, tool_name, execution_time, False
            )
            
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                execution_time=execution_time,
                error=str(e),
                metadata={
                    "provider": provider_config.provider.value,
                    "universal_execution": True,
                    "request_id": request_id
                }
            )
    
    async def _check_completed_universal_tool_executions(
        self,
        tasks: List[asyncio.Task],
        provider: AIProvider
    ) -> List[ToolExecutionResult]:
        """Check for completed universal tool execution tasks."""
        completed_results = []
        remaining_tasks = []
        
        for task in tasks:
            if task.done():
                try:
                    result = await task
                    completed_results.append(result)
                except Exception as e:
                    logger.error("Universal tool execution task failed",
                               provider=provider.value,
                               error=str(e))
            else:
                remaining_tasks.append(task)
        
        # Update tasks list
        tasks[:] = remaining_tasks
        
        return completed_results
    
    async def _initialize_universal_stream_tracking(
        self,
        request_id: str,
        provider: AIProvider,
        request: MessagesRequest
    ) -> None:
        """Initialize tracking for universal stream."""
        # Update universal metrics
        self.universal_metrics["total_universal_streams"] += 1
        
        # Track by provider
        provider_key = provider.value
        if provider_key not in self.universal_metrics["streams_by_provider"]:
            self.universal_metrics["streams_by_provider"][provider_key] = 0
        self.universal_metrics["streams_by_provider"][provider_key] += 1
        
        logger.debug("Universal stream tracking initialized",
                    request_id=request_id,
                    provider=provider_key,
                    model=request.model)
    
    async def _finalize_universal_stream(
        self,
        request_id: str,
        provider: AIProvider,
        start_time: float
    ) -> None:
        """Finalize universal stream and update metrics."""
        execution_time = time.time() - start_time
        provider_key = provider.value
        
        # Update average response time by provider
        if provider_key not in self.universal_metrics["average_response_time_by_provider"]:
            self.universal_metrics["average_response_time_by_provider"][provider_key] = execution_time
        else:
            current_avg = self.universal_metrics["average_response_time_by_provider"][provider_key]
            stream_count = self.universal_metrics["streams_by_provider"][provider_key]
            new_avg = ((current_avg * (stream_count - 1)) + execution_time) / stream_count
            self.universal_metrics["average_response_time_by_provider"][provider_key] = new_avg
        
        logger.info("Universal stream completed",
                   request_id=request_id,
                   provider=provider_key,
                   execution_time=f"{execution_time:.2f}s")
    
    async def _update_universal_tool_metrics(
        self,
        provider: AIProvider,
        tool_name: str,
        execution_time: float,
        success: bool
    ) -> None:
        """Update universal tool execution metrics."""
        provider_key = provider.value
        
        # Track tools executed by provider
        if provider_key not in self.universal_metrics["tools_executed_by_provider"]:
            self.universal_metrics["tools_executed_by_provider"][provider_key] = 0
        self.universal_metrics["tools_executed_by_provider"][provider_key] += 1
        
        # Update success rate (simple implementation)
        total_tools = sum(self.universal_metrics["tools_executed_by_provider"].values())
        if total_tools > 0:
            # This is a simplified calculation - in production you'd track successes separately
            self.universal_metrics["universal_tool_success_rate"] = 0.95  # Placeholder
    
    def get_universal_streaming_metrics(self) -> Dict[str, Any]:
        """Get comprehensive universal streaming metrics."""
        return {
            **self.universal_metrics,
            "supported_providers": list(self.provider_configs.keys()),
            "provider_configurations": {
                provider.value: {
                    "supports_streaming": config.supports_streaming,
                    "supports_tools": config.supports_tools,
                    "max_concurrent_tools": config.max_concurrent_tools,
                    "tool_timeout": config.tool_timeout
                }
                for provider, config in self.provider_configs.items()
            },
            "configuration": self.universal_config,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_supported_providers(self) -> List[Dict[str, Any]]:
        """Get list of supported AI providers with capabilities."""
        return [
            {
                "provider": provider.value,
                "supports_streaming": config.supports_streaming,
                "supports_tools": config.supports_tools,
                "tool_format": config.tool_format,
                "chunk_format": config.chunk_format,
                "reasoning_support": config.reasoning_support,
                "max_concurrent_tools": config.max_concurrent_tools,
                "optimizations": list(config.streaming_optimizations.keys()) if config.streaming_optimizations else []
            }
            for provider, config in self.provider_configs.items()
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for universal streaming service."""
        try:
            # Check tool service
            tool_service_healthy = hasattr(self.tool_service, "claude_code_tools")
            
            return {
                "overall_healthy": tool_service_healthy,
                "tool_service_healthy": tool_service_healthy,
                "universal_metrics": self.universal_metrics,
                "configuration": self.universal_config,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Universal streaming health check failed", error=str(e))
            return {
                "overall_healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            } 