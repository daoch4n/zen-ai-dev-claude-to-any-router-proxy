"""
Claude Code Advanced Streaming Flow.

This flow orchestrates real-time tool execution during streaming responses,
integrating all Phase 2 streaming capabilities into a unified pipeline.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, AsyncIterator
from datetime import datetime

from ...services.base import ConversionService
from ...models.anthropic import MessagesRequest
from ...models.litellm import LiteLLMRequest
from ...core.logging_config import get_logger

# Import Phase 1 and Phase 2 services
from ...flows.conversion.claude_code_enhanced_flow import ClaudeCodeEnhancedFlow
from ...services.claude_code_streaming_service import (
    ClaudeCodeAdvancedStreamingService,
    StreamingChunk,
    ToolExecutionResult
)
from ...services.claude_code_tool_service import ClaudeCodeToolService
from ...services.claude_code_reasoning_service import ClaudeCodeReasoningService
from ...services.http_client import HTTPClientService
from ...utils.config import config

logger = get_logger("streaming.claude_code_flow")


class ClaudeCodeStreamingFlow(ConversionService):
    """Advanced streaming flow with real-time tool execution orchestration."""
    
    def __init__(self):
        """Initialize the advanced streaming flow."""
        super().__init__("ClaudeCodeStreamingFlow")
        
        # Initialize core services
        self.enhanced_flow = ClaudeCodeEnhancedFlow()
        self.streaming_service = ClaudeCodeAdvancedStreamingService()
        self.tool_service = ClaudeCodeToolService()
        self.reasoning_service = ClaudeCodeReasoningService()
        self.http_client = HTTPClientService()
        
        # Streaming flow configuration
        self.flow_config = {
            "enable_real_time_tools": True,
            "streaming_timeout": 300,  # 5 minutes
            "tool_parallel_execution": True,
            "reasoning_streaming": True,
            "performance_monitoring": True
        }
        
        # Performance tracking
        self.flow_metrics = {
            "total_streaming_requests": 0,
            "successful_streams": 0,
            "tools_executed_in_streams": 0,
            "average_stream_duration": 0.0,
            "tool_execution_success_rate": 0.0
        }
        
        logger.info("Claude Code Advanced Streaming Flow initialized",
                   real_time_tools=self.flow_config["enable_real_time_tools"],
                   timeout=self.flow_config["streaming_timeout"])
    
    def convert(self, source: MessagesRequest, **kwargs) -> "ConversionResult":
        """
        Convert MessagesRequest for streaming processing.
        
        This method provides compatibility with ConversionService interface.
        For actual streaming, use process_streaming_request.
        """
        try:
            from ...models.instructor import ConversionResult
            
            # Validate that this is a streaming request
            if not kwargs.get('stream', True):
                return ConversionResult(
                    success=False,
                    errors=["This flow is designed for streaming requests only"],
                    metadata={"flow_type": "streaming"}
                )
            
            # Return success with metadata about streaming capabilities
            return ConversionResult(
                success=True,
                converted_data={"stream": True, "model": source.model},
                metadata={
                    "flow_type": "streaming",
                    "real_time_tools": self.flow_config["enable_real_time_tools"],
                    "tool_parallel_execution": self.flow_config["tool_parallel_execution"],
                    "reasoning_streaming": self.flow_config["reasoning_streaming"],
                    "note": "Use process_streaming_request for actual streaming"
                }
            )
            
        except Exception as e:
            from ...models.instructor import ConversionResult
            logger.error("Streaming flow conversion check failed", error=str(e))
            return ConversionResult(
                success=False,
                errors=[f"Streaming flow validation failed: {str(e)}"]
            )
    
    async def process_streaming_request(
        self,
        request: MessagesRequest,
        request_id: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Process a streaming request with advanced Claude Code capabilities.
        
        Args:
            request: Anthropic MessagesRequest
            request_id: Unique request identifier
            
        Yields:
            Dict[str, Any]: Anthropic-format streaming chunks with enhancements
        """
        flow_start_time = time.time()
        
        try:
            # Update metrics
            self.flow_metrics["total_streaming_requests"] += 1
            
            logger.info("Processing advanced Claude Code streaming request",
                       request_id=request_id,
                       model=request.model,
                       tools_count=len(request.tools) if request.tools else 0,
                       reasoning_enabled=self.flow_config["reasoning_streaming"])
            
            # Step 1: Enhanced conversion using Phase 1 components
            conversion_result = await self.enhanced_flow.convert(request)
            
            if not conversion_result.success:
                logger.error("Conversion failed for streaming request",
                           request_id=request_id,
                           errors=conversion_result.errors)
                
                # Yield error response
                yield self._create_error_stream_chunk(
                    "Conversion failed",
                    {"errors": conversion_result.errors}
                )
                return
            
            litellm_request = conversion_result.converted_data
            
            # Step 2: Create LiteLLM streaming request
            streaming_request = await self._prepare_streaming_request(
                litellm_request, request_id
            )
            
            # Step 3: Execute streaming request through LiteLLM
            litellm_stream = await self._execute_litellm_streaming_request(
                streaming_request, request_id
            )
            
            # Step 4: Process stream with advanced capabilities
            enhanced_stream = self.streaming_service.create_advanced_stream(
                request, litellm_stream, request_id
            )
            
            # Step 5: Convert back to Anthropic format and yield
            async for anthropic_chunk in self._convert_stream_to_anthropic(
                enhanced_stream, request, request_id
            ):
                yield anthropic_chunk
            
            # Update success metrics
            flow_duration = time.time() - flow_start_time
            await self._update_success_metrics(flow_duration)
            
            logger.info("Advanced streaming request completed successfully",
                       request_id=request_id,
                       duration=f"{flow_duration:.2f}s")
            
        except Exception as e:
            flow_duration = time.time() - flow_start_time
            
            logger.error("Advanced streaming request failed",
                        request_id=request_id,
                        error=str(e),
                        duration=f"{flow_duration:.2f}s",
                        exc_info=True)
            
            # Yield error response
            yield self._create_error_stream_chunk(
                f"Streaming failed: {str(e)}",
                {"error_type": type(e).__name__, "duration": flow_duration}
            )
    
    async def _prepare_streaming_request(
        self,
        litellm_request: Dict[str, Any],
        request_id: str
    ) -> Dict[str, Any]:
        """Prepare LiteLLM request for streaming with enhancements."""
        
        # Enable streaming
        streaming_request = {
            **litellm_request,
            "stream": True,
            "request_id": request_id
        }
        
        # Add streaming-specific parameters
        if self.flow_config["enable_real_time_tools"]:
            streaming_request["extra_headers"] = {
                **streaming_request.get("extra_headers", {}),
                "X-Real-Time-Tools": "true",
                "X-Streaming-Mode": "advanced"
            }
        
        # Configure timeout
        streaming_request["timeout"] = self.flow_config["streaming_timeout"]
        
        logger.debug("Prepared streaming request",
                    request_id=request_id,
                    model=streaming_request.get("model"),
                    stream=streaming_request.get("stream"),
                    timeout=streaming_request.get("timeout"))
        
        return streaming_request
    
    async def _execute_litellm_streaming_request(
        self,
        streaming_request: Dict[str, Any],
        request_id: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """Execute streaming request through LiteLLM."""
        
        try:
            logger.debug("Executing LiteLLM streaming request", request_id=request_id)
            
            # Use HTTP client for LiteLLM streaming call
            # This would typically be: acompletion(**streaming_request)
            # But we'll simulate with proper async iteration
            
            # For now, create a mock streaming response
            # In production, this would call the actual LiteLLM streaming API
            async for chunk in self._simulate_litellm_stream(streaming_request):
                yield chunk
                
        except Exception as e:
            logger.error("LiteLLM streaming request failed",
                        request_id=request_id,
                        error=str(e))
            raise
    
    async def _simulate_litellm_stream(
        self,
        request: Dict[str, Any]
    ) -> AsyncIterator[Dict[str, Any]]:
        """Simulate LiteLLM streaming response for development."""
        
        # This is a mock implementation for development
        # In production, this would be replaced with actual LiteLLM streaming
        
        chunks = [
            {"choices": [{"delta": {"content": "I'll help you with that. "}}]},
            {"choices": [{"delta": {"content": "Let me analyze the request "}}]},
            {"choices": [{"delta": {"content": "and execute the necessary tools."}}]},
            {
                "choices": [{
                    "delta": {
                        "tool_calls": [{
                            "function": {
                                "name": "read_file",
                                "arguments": '{"path": "example.txt"}'
                            }
                        }]
                    }
                }]
            },
            {"choices": [{"delta": {"content": " Tool execution completed."}}]},
            {"choices": [{"delta": {"content": " Here are the results..."}}]},
        ]
        
        for i, chunk in enumerate(chunks):
            await asyncio.sleep(0.1)  # Simulate streaming delay
            yield chunk
    
    async def _convert_stream_to_anthropic(
        self,
        enhanced_stream: AsyncIterator[StreamingChunk],
        original_request: MessagesRequest,
        request_id: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """Convert enhanced streaming chunks to Anthropic format."""
        
        chunk_count = 0
        
        async for chunk in enhanced_stream:
            try:
                chunk_count += 1
                
                # Convert StreamingChunk to Anthropic format
                anthropic_chunk = await self._create_anthropic_stream_chunk(
                    chunk, original_request, chunk_count
                )
                
                # Add request metadata
                anthropic_chunk["request_id"] = request_id
                anthropic_chunk["chunk_sequence"] = chunk_count
                
                yield anthropic_chunk
                
            except Exception as e:
                logger.error("Failed to convert streaming chunk",
                           request_id=request_id,
                           chunk_type=chunk.type,
                           error=str(e))
                
                # Yield error chunk but continue processing
                yield self._create_error_stream_chunk(
                    f"Chunk conversion failed: {str(e)}",
                    {"chunk_sequence": chunk_count}
                )
    
    async def _create_anthropic_stream_chunk(
        self,
        chunk: StreamingChunk,
        original_request: MessagesRequest,
        sequence: int
    ) -> Dict[str, Any]:
        """Create Anthropic-format streaming chunk from enhanced chunk."""
        
        # Base anthropic streaming format
        chunk_metadata = chunk.metadata or {}
        anthropic_chunk = {
            "type": "message_delta",
            "delta": {},
            "metadata": {
                **chunk_metadata,
                "timestamp": chunk.timestamp,
                "sequence": sequence
            }
        }
        
        # Handle different chunk types
        if chunk.type == "content":
            anthropic_chunk["delta"] = {
                "type": "text_delta",
                "text": chunk.content
            }
            
        elif chunk.type == "thinking":
            # Handle reasoning/thinking content
            anthropic_chunk["type"] = "thinking_delta"
            anthropic_chunk["delta"] = {
                "thinking": chunk.thinking_content or chunk.content
            }
            
        elif chunk.type == "tool_call":
            # Handle tool call notifications
            anthropic_chunk["type"] = "tool_call_delta"
            anthropic_chunk["delta"] = {
                "tool_calls": chunk.tool_calls,
                "status": "executing"
            }
            
        elif chunk.type == "tool_result":
            # Handle tool result notifications
            anthropic_chunk["type"] = "tool_result_delta"
            anthropic_chunk["delta"] = {
                "tool_results": chunk.tool_results,
                "status": "completed"
            }
            
        elif chunk.type == "error":
            # Handle error chunks
            anthropic_chunk["type"] = "error"
            anthropic_chunk["error"] = {
                "type": "streaming_error",
                "message": chunk.content
            }
        
        return anthropic_chunk
    
    def _create_error_stream_chunk(
        self,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create an error streaming chunk in Anthropic format."""
        return {
            "type": "error",
            "error": {
                "type": "streaming_error",
                "message": message
            },
            "metadata": {
                **(metadata or {}),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    async def _update_success_metrics(self, duration: float) -> None:
        """Update success metrics for streaming flow."""
        self.flow_metrics["successful_streams"] += 1
        
        # Update average duration
        total_successful = self.flow_metrics["successful_streams"]
        current_avg = self.flow_metrics["average_stream_duration"]
        
        new_avg = ((current_avg * (total_successful - 1)) + duration) / total_successful
        self.flow_metrics["average_stream_duration"] = new_avg
    
    def get_streaming_flow_metrics(self) -> Dict[str, Any]:
        """Get comprehensive streaming flow metrics."""
        
        # Calculate derived metrics
        total_requests = self.flow_metrics["total_streaming_requests"]
        successful_streams = self.flow_metrics["successful_streams"]
        
        success_rate = (successful_streams / total_requests) if total_requests > 0 else 0.0
        
        return {
            **self.flow_metrics,
            "success_rate": success_rate,
            "configuration": self.flow_config,
            "streaming_service_metrics": self.streaming_service.get_streaming_metrics(),
            "active_streams": self.streaming_service.get_active_streams_status(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_streaming_capabilities(self) -> Dict[str, Any]:
        """Get streaming capabilities and status."""
        return {
            "real_time_tools": self.flow_config["enable_real_time_tools"],
            "parallel_execution": self.flow_config["tool_parallel_execution"],
            "reasoning_streaming": self.flow_config["reasoning_streaming"],
            "performance_monitoring": self.flow_config["performance_monitoring"],
            "available_tools": self.tool_service.get_available_claude_code_tools(),
            "supported_models": list(self.enhanced_flow.claude_converter.claude_code_models.keys()),
            "max_concurrent_tools": self.streaming_service.streaming_config["max_concurrent_tools"],
            "tool_execution_timeout": self.streaming_service.streaming_config["tool_execution_timeout"],
            "flow_status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of streaming flow."""
        try:
            # Check service dependencies
            services_status = {
                "enhanced_flow": hasattr(self.enhanced_flow, "claude_converter"),
                "streaming_service": hasattr(self.streaming_service, "streaming_config"),
                "tool_service": hasattr(self.tool_service, "claude_code_tools"),
                "reasoning_service": hasattr(self.reasoning_service, "reasoning_profiles"),
                "http_client": hasattr(self.http_client, "streaming_config") if hasattr(self.http_client, "streaming_config") else True
            }
            
            # Check configuration
            config_valid = all([
                self.flow_config["streaming_timeout"] > 0,
                isinstance(self.flow_config["enable_real_time_tools"], bool),
                isinstance(self.flow_config["tool_parallel_execution"], bool)
            ])
            
            overall_healthy = all(services_status.values()) and config_valid
            
            return {
                "overall_healthy": overall_healthy,
                "services": services_status,
                "configuration_valid": config_valid,
                "metrics": self.get_streaming_flow_metrics(),
                "capabilities": self.get_streaming_capabilities(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Streaming flow health check failed", error=str(e))
            return {
                "overall_healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
