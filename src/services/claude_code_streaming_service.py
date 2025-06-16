"""
Claude Code Advanced Streaming Service.

This service provides real-time tool execution during streaming responses,
a key Phase 2 feature that enhances user experience and showcases advanced LiteLLM capabilities.
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, AsyncIterator, Union
from datetime import datetime
from dataclasses import dataclass

from ..core.logging_config import get_logger
from ..services.base import BaseService
from ..services.claude_code_tool_service import ClaudeCodeToolService
from ..services.claude_code_reasoning_service import ClaudeCodeReasoningService
from ..models.anthropic import MessagesRequest
from ..utils.config import config

logger = get_logger("streaming.claude_code_advanced")


@dataclass
class StreamingChunk:
    """Represents a chunk in the streaming response."""
    type: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    thinking_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


@dataclass
class ToolExecutionResult:
    """Result of tool execution during streaming."""
    tool_name: str
    success: bool
    result: Any
    execution_time: float
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ClaudeCodeAdvancedStreamingService(BaseService):
    """Advanced streaming service with real-time tool execution capabilities."""
    
    def __init__(self):
        """Initialize the advanced streaming service."""
        super().__init__("ClaudeCodeAdvancedStreaming")
        
        # Initialize dependent services
        self.tool_service = ClaudeCodeToolService()
        self.reasoning_service = ClaudeCodeReasoningService()
        
        # Streaming configuration
        self.streaming_config = {
            "tool_execution_timeout": 30,  # seconds
            "max_concurrent_tools": 3,
            "chunk_size": 1024,
            "heartbeat_interval": 1.0,  # seconds
            "buffer_size": 8192
        }
        
        # Performance tracking
        self.streaming_metrics = {
            "total_streams": 0,
            "tools_executed_during_stream": 0,
            "average_tool_execution_time": 0.0,
            "concurrent_streams": 0,
            "stream_completion_rate": 0.0
        }
        
        # Active streams tracking
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Claude Code Advanced Streaming Service initialized",
                   tool_execution_timeout=self.streaming_config["tool_execution_timeout"],
                   max_concurrent_tools=self.streaming_config["max_concurrent_tools"])
    
    async def create_advanced_stream(
        self,
        request: MessagesRequest,
        litellm_response_stream: AsyncIterator[Dict[str, Any]],
        request_id: str
    ) -> AsyncIterator[StreamingChunk]:
        """
        Create an advanced streaming response with real-time tool execution.
        
        Args:
            request: Original Claude Code request
            litellm_response_stream: Base LiteLLM streaming response
            request_id: Unique request identifier
            
        Yields:
            StreamingChunk: Enhanced streaming chunks with tool execution
        """
        stream_start_time = time.time()
        
        try:
            # Initialize stream tracking
            await self._initialize_stream_tracking(request_id, request)
            
            logger.info("Starting advanced streaming with real-time tool execution",
                       request_id=request_id,
                       model=request.model,
                       has_tools=bool(request.tools))
            
            # Process the stream with tool execution
            async for chunk in self._process_stream_with_tools(
                litellm_response_stream,
                request,
                request_id
            ):
                # Add performance metadata
                chunk.timestamp = datetime.utcnow().isoformat()
                chunk.metadata = {
                    **(chunk.metadata or {}),
                    "request_id": request_id,
                    "stream_time": time.time() - stream_start_time
                }
                
                yield chunk
            
            # Finalize stream
            await self._finalize_stream(request_id, stream_start_time)
            
        except Exception as e:
            logger.error("Advanced streaming failed",
                        request_id=request_id,
                        error=str(e),
                        exc_info=True)
            
            # Yield error chunk
            yield StreamingChunk(
                type="error",
                content=f"Streaming error: {str(e)}",
                metadata={"error_type": type(e).__name__, "request_id": request_id}
            )
            
        finally:
            # Cleanup stream tracking
            await self._cleanup_stream_tracking(request_id)
    
    async def _process_stream_with_tools(
        self,
        response_stream: AsyncIterator[Dict[str, Any]],
        request: MessagesRequest,
        request_id: str
    ) -> AsyncIterator[StreamingChunk]:
        """Process streaming response with real-time tool execution."""
        
        tool_execution_tasks: List[asyncio.Task] = []
        accumulated_content = ""
        
        async for raw_chunk in response_stream:
            try:
                # Parse the streaming chunk
                chunk_data = await self._parse_streaming_chunk(raw_chunk)
                
                if chunk_data["type"] == "content_delta":
                    # Accumulate content for tool detection
                    content = chunk_data.get("content", "")
                    accumulated_content += content
                    
                    # Yield content chunk
                    yield StreamingChunk(
                        type="content",
                        content=content,
                        metadata={"chunk_type": "content_delta"}
                    )
                    
                    # Check for tool calls in accumulated content
                    tool_calls = await self._detect_tool_calls_in_content(
                        accumulated_content, request
                    )
                    
                    if tool_calls:
                        # Execute tools in parallel during streaming
                        for tool_call in tool_calls:
                            task = asyncio.create_task(
                                self._execute_tool_during_stream(
                                    tool_call, request_id
                                )
                            )
                            tool_execution_tasks.append(task)
                            
                            # Yield tool call notification
                            yield StreamingChunk(
                                type="tool_call",
                                content=f"Executing tool: {tool_call['name']}",
                                tool_calls=[tool_call],
                                metadata={"execution_status": "started"}
                            )
                
                elif chunk_data["type"] == "thinking_delta":
                    # Handle reasoning content
                    thinking_content = chunk_data.get("content", "")
                    
                    yield StreamingChunk(
                        type="thinking",
                        content="",
                        thinking_content=thinking_content,
                        metadata={"reasoning_type": "thinking_block"}
                    )
                
                elif chunk_data["type"] == "tool_use":
                    # Handle explicit tool use from model
                    tool_call = chunk_data.get("tool_call")
                    if tool_call:
                        # Execute tool immediately
                        task = asyncio.create_task(
                            self._execute_tool_during_stream(tool_call, request_id)
                        )
                        tool_execution_tasks.append(task)
                
                # Check for completed tool executions
                completed_tools = await self._check_completed_tool_executions(
                    tool_execution_tasks
                )
                
                for tool_result in completed_tools:
                    # Yield tool result
                    yield StreamingChunk(
                        type="tool_result",
                        content=f"Tool {tool_result.tool_name} completed",
                        tool_results=[{
                            "tool_name": tool_result.tool_name,
                            "result": tool_result.result,
                            "success": tool_result.success,
                            "execution_time": tool_result.execution_time
                        }],
                        metadata={"execution_status": "completed"}
                    )
                
            except Exception as e:
                logger.error("Error processing streaming chunk",
                           request_id=request_id,
                           error=str(e))
                continue
        
        # Wait for any remaining tool executions
        if tool_execution_tasks:
            logger.info("Waiting for remaining tool executions",
                       request_id=request_id,
                       remaining_tasks=len(tool_execution_tasks))
            
            remaining_results = await asyncio.gather(
                *tool_execution_tasks, return_exceptions=True
            )
            
            for result in remaining_results:
                if isinstance(result, ToolExecutionResult):
                    yield StreamingChunk(
                        type="tool_result",
                        content=f"Tool {result.tool_name} completed",
                        tool_results=[{
                            "tool_name": result.tool_name,
                            "result": result.result,
                            "success": result.success,
                            "execution_time": result.execution_time
                        }],
                        metadata={"execution_status": "final"}
                    )
    
    async def _parse_streaming_chunk(self, raw_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw streaming chunk into structured format."""
        try:
            # Handle different streaming formats
            if "choices" in raw_chunk:
                choice = raw_chunk["choices"][0]
                delta = choice.get("delta", {})
                
                if "content" in delta:
                    return {
                        "type": "content_delta",
                        "content": delta["content"]
                    }
                elif "tool_calls" in delta:
                    return {
                        "type": "tool_use",
                        "tool_call": delta["tool_calls"][0] if delta["tool_calls"] else None
                    }
            
            # Handle thinking/reasoning content
            if "thinking" in raw_chunk:
                return {
                    "type": "thinking_delta",
                    "content": raw_chunk["thinking"]
                }
            
            # Default content parsing
            return {
                "type": "content_delta",
                "content": str(raw_chunk.get("content", ""))
            }
            
        except Exception as e:
            logger.error("Failed to parse streaming chunk", error=str(e))
            return {"type": "unknown", "content": ""}
    
    async def _detect_tool_calls_in_content(
        self, 
        content: str, 
        request: MessagesRequest
    ) -> List[Dict[str, Any]]:
        """Detect tool calls in streaming content."""
        try:
            # Look for tool call patterns in content
            tool_calls = []
            
            # Check for explicit tool call syntax
            if "<tool_call>" in content or "function_call" in content.lower():
                # Parse tool calls from content
                detected_calls = await self._parse_tool_calls_from_text(content)
                tool_calls.extend(detected_calls)
            
            # Check for natural language tool requests
            available_tools = self.tool_service.get_available_claude_code_tools()
            for tool_name in available_tools:
                if tool_name.lower() in content.lower():
                    # Check if this looks like a tool request
                    if await self._is_likely_tool_request(content, tool_name):
                        tool_calls.append({
                            "name": tool_name,
                            "arguments": await self._extract_tool_arguments(content, tool_name),
                            "detection_method": "natural_language"
                        })
            
            return tool_calls[:self.streaming_config["max_concurrent_tools"]]
            
        except Exception as e:
            logger.error("Tool call detection failed", error=str(e))
            return []
    
    async def _execute_tool_during_stream(
        self, 
        tool_call: Dict[str, Any], 
        request_id: str
    ) -> ToolExecutionResult:
        """Execute a tool during streaming response."""
        tool_name = tool_call["name"]
        execution_start = time.time()
        
        try:
            logger.debug("Executing tool during stream",
                        tool_name=tool_name,
                        request_id=request_id)
            
            # Execute the tool using our tool service
            result = await self.tool_service.execute_claude_code_tool(
                tool_name,
                tool_call.get("arguments", {}),
                timeout=self.streaming_config["tool_execution_timeout"]
            )
            
            execution_time = time.time() - execution_start
            
            # Update metrics
            await self._update_tool_execution_metrics(tool_name, execution_time, True)
            
            logger.info("Tool executed successfully during stream",
                       tool_name=tool_name,
                       execution_time=f"{execution_time:.2f}s",
                       request_id=request_id)
            
            return ToolExecutionResult(
                tool_name=tool_name,
                success=True,
                result=result,
                execution_time=execution_time,
                metadata={"request_id": request_id}
            )
            
        except Exception as e:
            execution_time = time.time() - execution_start
            
            logger.error("Tool execution failed during stream",
                        tool_name=tool_name,
                        error=str(e),
                        execution_time=f"{execution_time:.2f}s",
                        request_id=request_id)
            
            # Update metrics
            await self._update_tool_execution_metrics(tool_name, execution_time, False)
            
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                execution_time=execution_time,
                error=str(e),
                metadata={"request_id": request_id}
            )
    
    async def _check_completed_tool_executions(
        self, 
        tasks: List[asyncio.Task]
    ) -> List[ToolExecutionResult]:
        """Check for completed tool execution tasks."""
        completed_results = []
        remaining_tasks = []
        
        for task in tasks:
            if task.done():
                try:
                    result = await task
                    completed_results.append(result)
                except Exception as e:
                    logger.error("Tool execution task failed", error=str(e))
            else:
                remaining_tasks.append(task)
        
        # Update tasks list to only include remaining tasks
        tasks[:] = remaining_tasks
        
        return completed_results
    
    async def _initialize_stream_tracking(
        self, 
        request_id: str, 
        request: MessagesRequest
    ) -> None:
        """Initialize tracking for a new stream."""
        self.active_streams[request_id] = {
            "start_time": time.time(),
            "model": request.model,
            "tools_executed": 0,
            "chunks_sent": 0,
            "status": "active"
        }
        
        self.streaming_metrics["concurrent_streams"] += 1
        self.streaming_metrics["total_streams"] += 1
    
    async def _finalize_stream(self, request_id: str, start_time: float) -> None:
        """Finalize stream and update metrics."""
        if request_id in self.active_streams:
            stream_data = self.active_streams[request_id]
            execution_time = time.time() - start_time
            
            logger.info("Advanced stream completed",
                       request_id=request_id,
                       execution_time=f"{execution_time:.2f}s",
                       tools_executed=stream_data["tools_executed"],
                       chunks_sent=stream_data["chunks_sent"])
            
            stream_data["status"] = "completed"
            stream_data["completion_time"] = execution_time
    
    async def _cleanup_stream_tracking(self, request_id: str) -> None:
        """Clean up stream tracking data."""
        if request_id in self.active_streams:
            del self.active_streams[request_id]
            self.streaming_metrics["concurrent_streams"] -= 1
    
    async def _update_tool_execution_metrics(
        self, 
        tool_name: str, 
        execution_time: float, 
        success: bool
    ) -> None:
        """Update tool execution performance metrics."""
        self.streaming_metrics["tools_executed_during_stream"] += 1
        
        # Update average execution time
        total_executions = self.streaming_metrics["tools_executed_during_stream"]
        current_avg = self.streaming_metrics["average_tool_execution_time"]
        
        new_avg = ((current_avg * (total_executions - 1)) + execution_time) / total_executions
        self.streaming_metrics["average_tool_execution_time"] = new_avg
    
    async def _parse_tool_calls_from_text(self, content: str) -> List[Dict[str, Any]]:
        """Parse explicit tool calls from text content."""
        # Implementation for parsing structured tool calls
        # This would handle XML-like tool call syntax or JSON
        return []
    
    async def _is_likely_tool_request(self, content: str, tool_name: str) -> bool:
        """Determine if content contains a likely tool request."""
        # Simple heuristic - look for action words near tool name
        action_words = ["use", "run", "execute", "call", "invoke", "please"]
        content_lower = content.lower()
        tool_lower = tool_name.lower()
        
        tool_index = content_lower.find(tool_lower)
        if tool_index == -1:
            return False
        
        # Check for action words near the tool name
        search_range = 50  # characters to search around tool name
        start = max(0, tool_index - search_range)
        end = min(len(content_lower), tool_index + len(tool_lower) + search_range)
        context = content_lower[start:end]
        
        return any(action in context for action in action_words)
    
    async def _extract_tool_arguments(self, content: str, tool_name: str) -> Dict[str, Any]:
        """Extract tool arguments from natural language content."""
        # Basic implementation - would be enhanced with NLP
        return {}
    
    def get_streaming_metrics(self) -> Dict[str, Any]:
        """Get comprehensive streaming performance metrics."""
        return {
            **self.streaming_metrics,
            "active_streams": len(self.active_streams),
            "configuration": self.streaming_config,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_active_streams_status(self) -> Dict[str, Any]:
        """Get status of all active streams."""
        return {
            "active_count": len(self.active_streams),
            "streams": {
                request_id: {
                    **stream_data,
                    "duration": time.time() - stream_data["start_time"]
                }
                for request_id, stream_data in self.active_streams.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
