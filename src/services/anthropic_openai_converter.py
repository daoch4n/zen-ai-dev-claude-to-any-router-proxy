"""
Bidirectional API schema converter between Anthropic and OpenAI formats.

This module provides conversion capabilities for the LiteLLM bypass implementation,
enabling direct communication with OpenRouter using OpenAI format while maintaining
Anthropic API compatibility.
"""

import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..services.base import BaseService
from ..models.anthropic import MessagesRequest, MessagesResponse, Message, Tool, Usage
from ..models.openai import (
    OpenAIChatRequest, OpenAIChatResponse, OpenAIMessage, OpenAITool, OpenAIFunction,
    OpenAIChoice, OpenAIUsage, OpenAIStreamChunk, create_openai_message, create_openai_tool
)
from ..core.logging_config import get_logger

logger = get_logger(__name__)


class AnthropicOpenAIConverter(BaseService):
    """Bidirectional converter between Anthropic and OpenAI formats."""
    
    def __init__(self):
        """Initialize the converter."""
        super().__init__("AnthropicOpenAIConverter")
        logger.info("Anthropic-OpenAI converter initialized")
    
    def anthropic_to_openai(self, request: MessagesRequest) -> OpenAIChatRequest:
        """
        Convert Anthropic MessagesRequest to OpenAI format.
        
        Args:
            request: Anthropic format request
            
        Returns:
            OpenAI format request
        """
        try:
            logger.debug("Converting Anthropic request to OpenAI format",
                        model=request.model,
                        message_count=len(request.messages))
            
            # Convert messages
            openai_messages = []
            for msg in request.messages:
                openai_msg = self._convert_anthropic_message_to_openai(msg)
                openai_messages.append(openai_msg)
            
            # Convert tools if present
            openai_tools = None
            openai_tool_choice = None
            if request.tools:
                openai_tools = []
                for tool in request.tools:
                    openai_tool = self._convert_anthropic_tool_to_openai(tool)
                    openai_tools.append(openai_tool)
                
                # Handle tool choice
                if hasattr(request, 'tool_choice') and request.tool_choice:
                    openai_tool_choice = self._convert_tool_choice_to_openai(request.tool_choice)
            
            # Build OpenAI request
            openai_request_data = {
                "model": request.model,
                "messages": openai_messages
            }
            
            # Add optional parameters
            if request.max_tokens:
                openai_request_data["max_tokens"] = request.max_tokens
            
            if hasattr(request, 'temperature') and request.temperature is not None:
                openai_request_data["temperature"] = request.temperature
            
            if hasattr(request, 'top_p') and request.top_p is not None:
                openai_request_data["top_p"] = request.top_p
            
            if hasattr(request, 'stream') and request.stream is not None:
                openai_request_data["stream"] = request.stream
            
            if openai_tools:
                openai_request_data["tools"] = openai_tools
            
            if openai_tool_choice:
                openai_request_data["tool_choice"] = openai_tool_choice
            
            # Handle additional parameters from request
            if hasattr(request, 'stop_sequences') and request.stop_sequences:
                openai_request_data["stop"] = request.stop_sequences
            
            # Create and validate OpenAI request
            openai_request = OpenAIChatRequest(**openai_request_data)
            
            logger.debug("Anthropic to OpenAI conversion completed",
                        model=openai_request.model,
                        message_count=len(openai_request.messages),
                        has_tools=bool(openai_request.tools))
            
            self.log_operation("anthropic_to_openai_conversion", success=True,
                             model=request.model,
                             message_count=len(request.messages),
                             has_tools=bool(request.tools))
            
            return openai_request
            
        except Exception as e:
            logger.error("Failed to convert Anthropic request to OpenAI format",
                        error=str(e),
                        model=getattr(request, 'model', 'unknown'),
                        exc_info=True)
            
            self.log_operation("anthropic_to_openai_conversion", success=False,
                             error=str(e),
                             model=getattr(request, 'model', 'unknown'))
            
            raise
    
    def _convert_anthropic_message_to_openai(self, message: Message) -> OpenAIMessage:
        """Convert Anthropic message to OpenAI format."""
        # Handle different content types
        if isinstance(message.content, str):
            # Simple text content
            return create_openai_message(
                role=message.role,
                content=message.content
            )
        
        elif isinstance(message.content, list):
            # Complex content with potentially multiple blocks
            openai_content = []
            tool_calls = []
            
            for content_block in message.content:
                if isinstance(content_block, dict):
                    if content_block.get("type") == "text":
                        openai_content.append({
                            "type": "text",
                            "text": content_block.get("text", "")
                        })
                    
                    elif content_block.get("type") == "image":
                        # Convert image content
                        image_content = self._convert_image_content_to_openai(content_block)
                        if image_content:
                            openai_content.append(image_content)
                    
                    elif content_block.get("type") == "tool_use":
                        # Convert tool use to OpenAI tool calls
                        tool_call = self._convert_tool_use_to_openai(content_block)
                        if tool_call:
                            tool_calls.append(tool_call)
                
                elif isinstance(content_block, str):
                    openai_content.append({
                        "type": "text",
                        "text": content_block
                    })
            
            # Create OpenAI message
            openai_msg_data = {
                "role": message.role,
                "content": openai_content if openai_content else None
            }
            
            if tool_calls:
                openai_msg_data["tool_calls"] = tool_calls
            
            return OpenAIMessage(**openai_msg_data)
        
        else:
            # Fallback for unknown content types
            return create_openai_message(
                role=message.role,
                content=str(message.content)
            )
    
    def _convert_image_content_to_openai(self, image_block: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert Anthropic image content to OpenAI format."""
        try:
            source = image_block.get("source", {})
            
            if source.get("type") == "base64":
                return {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{source.get('media_type', 'image/jpeg')};base64,{source.get('data', '')}"
                    }
                }
            else:
                logger.warning("Unsupported image source type",
                             source_type=source.get("type"))
                return None
                
        except Exception as e:
            logger.error("Failed to convert image content",
                        error=str(e),
                        image_block=image_block)
            return None
    
    def _convert_tool_use_to_openai(self, tool_use_block: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert Anthropic tool_use to OpenAI tool_calls format."""
        try:
            return {
                "id": tool_use_block.get("id", str(uuid.uuid4())),
                "type": "function",
                "function": {
                    "name": tool_use_block.get("name", ""),
                    "arguments": json.dumps(tool_use_block.get("input", {}))
                }
            }
        except Exception as e:
            logger.error("Failed to convert tool use",
                        error=str(e),
                        tool_use_block=tool_use_block)
            return None
    
    def _convert_anthropic_tool_to_openai(self, tool: Tool) -> OpenAITool:
        """Convert Anthropic tool to OpenAI function format."""
        return create_openai_tool(
            name=tool.name,
            description=tool.description or "",
            parameters=tool.input_schema
        )
    
    def _convert_tool_choice_to_openai(self, tool_choice: Any) -> Union[str, Dict[str, Any]]:
        """Convert Anthropic tool choice to OpenAI format."""
        if isinstance(tool_choice, dict):
            if tool_choice.get("type") == "tool":
                return {
                    "type": "function",
                    "function": {"name": tool_choice.get("name", "")}
                }
        elif isinstance(tool_choice, str):
            if tool_choice == "auto":
                return "auto"
            elif tool_choice == "any":
                return "required"
        
        return "auto"  # Default fallback
    
    def openai_to_anthropic_response(
        self,
        openai_response: Dict[str, Any],
        original_request: MessagesRequest
    ) -> MessagesResponse:
        """
        Convert OpenAI response back to Anthropic MessagesResponse format.
        
        Args:
            openai_response: OpenAI format response
            original_request: Original Anthropic request for context
            
        Returns:
            Anthropic format response
        """
        try:
            logger.debug("Converting OpenAI response to Anthropic format",
                        response_id=openai_response.get("id"),
                        model=openai_response.get("model"))
            
            # Extract first choice
            choices = openai_response.get("choices", [])
            if not choices:
                raise ValueError("No choices in OpenAI response")
            
            first_choice = choices[0]
            openai_message = first_choice.get("message", {})
            
            # Convert message content
            anthropic_content = self._convert_openai_message_to_anthropic_content(openai_message)
            
            # Handle stop reason
            stop_reason = self._convert_finish_reason_to_anthropic(
                first_choice.get("finish_reason")
            )
            
            # Convert usage information
            usage = None
            if openai_response.get("usage"):
                openai_usage = openai_response["usage"]
                usage = Usage(
                    input_tokens=openai_usage.get("prompt_tokens", 0),
                    output_tokens=openai_usage.get("completion_tokens", 0)
                )
            
            # Create Anthropic response
            anthropic_response = MessagesResponse(
                id=openai_response.get("id", str(uuid.uuid4())),
                type="message",
                role="assistant",
                content=anthropic_content,
                model=original_request.model,  # Always preserve original model name
                stop_reason=stop_reason,
                stop_sequence=None,
                usage=usage
            )
            
            logger.debug("OpenAI to Anthropic conversion completed",
                        response_id=anthropic_response.id,
                        content_blocks=len(anthropic_content) if isinstance(anthropic_content, list) else 1,
                        stop_reason=stop_reason)
            
            self.log_operation("openai_to_anthropic_conversion", success=True,
                             response_id=openai_response.get("id"),
                             model=openai_response.get("model"))
            
            return anthropic_response
            
        except Exception as e:
            logger.error("Failed to convert OpenAI response to Anthropic format",
                        error=str(e),
                        response_id=openai_response.get("id"),
                        exc_info=True)
            
            self.log_operation("openai_to_anthropic_conversion", success=False,
                             error=str(e),
                             response_id=openai_response.get("id"))
            
            raise
    
    def _convert_openai_message_to_anthropic_content(
        self,
        openai_message: Dict[str, Any]
    ) -> Union[str, List[Dict[str, Any]]]:
        """Convert OpenAI message to Anthropic content format."""
        content_blocks = []
        
        # Handle text content
        text_content = openai_message.get("content")
        if text_content:
            if isinstance(text_content, str):
                content_blocks.append({
                    "type": "text",
                    "text": text_content
                })
            elif isinstance(text_content, list):
                for content_item in text_content:
                    if isinstance(content_item, dict):
                        if content_item.get("type") == "text":
                            content_blocks.append({
                                "type": "text",
                                "text": content_item.get("text", "")
                            })
        
        # Handle tool calls
        tool_calls = openai_message.get("tool_calls", [])
        for tool_call in tool_calls:
            if tool_call.get("type") == "function":
                function = tool_call.get("function", {})
                try:
                    arguments = json.loads(function.get("arguments", "{}"))
                except json.JSONDecodeError:
                    arguments = {}
                
                content_blocks.append({
                    "type": "tool_use",
                    "id": tool_call.get("id", str(uuid.uuid4())),
                    "name": function.get("name", ""),
                    "input": arguments
                })
        
        # Always return list format for Anthropic MessagesResponse compatibility
        if content_blocks:
            return content_blocks
        else:
            # Return empty text block for empty content
            return [{
                "type": "text",
                "text": ""
            }]
    
    def _convert_finish_reason_to_anthropic(self, finish_reason: Optional[str]) -> Optional[str]:
        """Convert OpenAI finish reason to Anthropic stop reason."""
        if not finish_reason:
            return None
        
        mapping = {
            "stop": "end_turn",
            "length": "max_tokens",
            "tool_calls": "tool_use",
            "content_filter": "stop_sequence",
            "function_call": "tool_use"  # Legacy OpenAI format
        }
        
        return mapping.get(finish_reason, "end_turn")
    
    def convert_streaming_chunk(
        self,
        openai_chunk: Dict[str, Any],
        original_request: MessagesRequest
    ) -> Dict[str, Any]:
        """
        Convert OpenAI streaming chunk to Anthropic format.
        
        Args:
            openai_chunk: OpenAI streaming chunk
            original_request: Original Anthropic request for context
            
        Returns:
            Anthropic format streaming chunk
        """
        try:
            # Get the delta from the first choice
            choices = openai_chunk.get("choices", [])
            if not choices:
                return self._create_anthropic_stream_end()
            
            first_choice = choices[0]
            delta = first_choice.get("delta", {})
            finish_reason = first_choice.get("finish_reason")
            
            # Handle different delta types
            if finish_reason:
                # Final chunk
                return self._create_anthropic_stream_end(finish_reason)
            
            elif delta.get("content"):
                # Text content delta
                return {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {
                        "type": "text_delta",
                        "text": delta["content"]
                    }
                }
            
            elif delta.get("tool_calls"):
                # Tool call delta
                tool_calls = delta["tool_calls"]
                if tool_calls and len(tool_calls) > 0:
                    tool_call = tool_calls[0]
                    function = tool_call.get("function", {})
                    
                    if function.get("name"):
                        # Start of tool call
                        return {
                            "type": "content_block_start",
                            "index": first_choice.get("index", 0),
                            "content_block": {
                                "type": "tool_use",
                                "id": tool_call.get("id", str(uuid.uuid4())),
                                "name": function["name"],
                                "input": {}
                            }
                        }
                    elif function.get("arguments"):
                        # Tool arguments delta
                        return {
                            "type": "content_block_delta",
                            "index": first_choice.get("index", 0),
                            "delta": {
                                "type": "input_json_delta",
                                "partial_json": function["arguments"]
                            }
                        }
            
            # Default: message start
            if delta.get("role"):
                return {
                    "type": "message_start",
                    "message": {
                        "id": openai_chunk.get("id", str(uuid.uuid4())),
                        "type": "message",
                        "role": "assistant",
                        "content": [],
                        "model": original_request.model,  # Always preserve original model name
                        "stop_reason": None,
                        "stop_sequence": None,
                        "usage": {"input_tokens": 0, "output_tokens": 0}
                    }
                }
            
            # Empty delta - return minimal chunk
            return {"type": "ping"}
            
        except Exception as e:
            logger.error("Failed to convert streaming chunk",
                        error=str(e),
                        chunk_id=openai_chunk.get("id"),
                        exc_info=True)
            
            return self._create_anthropic_stream_end()
    
    def _create_anthropic_stream_end(self, finish_reason: Optional[str] = None) -> Dict[str, Any]:
        """Create Anthropic streaming end chunk."""
        stop_reason = self._convert_finish_reason_to_anthropic(finish_reason) if finish_reason else "end_turn"
        
        return {
            "type": "message_delta",
            "delta": {
                "stop_reason": stop_reason,
                "stop_sequence": None
            },
            "usage": {
                "output_tokens": 0
            }
        } 