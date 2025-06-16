"""
Azure Databricks format converter.

This module handles format conversion between Anthropic API and Azure Databricks API.
Based on analysis, formats are very similar, but Azure Databricks returns OpenAI-compatible
format that needs to be converted to Anthropic format for Claude Code compatibility.
"""

from typing import Dict, Any, List, Optional
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class AzureDatabricksConverter:
    """
    Handles format conversion between Anthropic API and Azure Databricks API.
    
    Azure Databricks accepts Anthropic-style requests but returns OpenAI-compatible
    responses, so the main conversion is on the response side.
    """
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.AzureDatabricksConverter")
    
    def convert_request_to_databricks(self, anthropic_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Anthropic API request to Azure Databricks format.
        
        Azure Databricks accepts Anthropic format directly, so this is mainly
        a validation and cleanup function with optional parameter handling.
        
        Args:
            anthropic_request: Request in Anthropic format
            
        Returns:
            Dict formatted for Azure Databricks API
        """
        self.logger.debug("Converting Anthropic request to Azure Databricks format",
                         keys=list(anthropic_request.keys()))
        
        # Azure Databricks accepts Anthropic format directly
        # Only need to ensure required fields are present and clean up
        converted = {
            "messages": anthropic_request.get("messages", []),
            "max_tokens": anthropic_request.get("max_tokens", 1000),
            "temperature": anthropic_request.get("temperature", 0.7)
        }
        
        # Pass through optional parameters that Azure Databricks supports
        optional_params = [
            "top_p", "top_k", "stop_sequences", "stream", "system"
        ]
        
        for param in optional_params:
            if param in anthropic_request and anthropic_request[param] is not None:
                converted[param] = anthropic_request[param]
        
        # Handle model parameter (for logging/tracking)
        if "model" in anthropic_request:
            converted["model"] = anthropic_request["model"]
        
        self.logger.debug("Request conversion complete",
                         input_keys=list(anthropic_request.keys()),
                         output_keys=list(converted.keys()),
                         message_count=len(converted["messages"]))
        
        return converted
    
    def convert_response_to_anthropic(self, databricks_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Azure Databricks response to Anthropic format.
        
        Azure Databricks returns OpenAI-compatible format, which needs to be
        converted to Anthropic format for Claude Code compatibility.
        
        Args:
            databricks_response: Response from Azure Databricks API
            
        Returns:
            Dict in Anthropic format
        """
        self.logger.debug("Converting Azure Databricks response to Anthropic format",
                         response_keys=list(databricks_response.keys()))
        
        # Check if this is an OpenAI-style response with choices
        if "choices" in databricks_response:
            return self._convert_openai_style_response(databricks_response)
        
        # Check if this is already in Anthropic format
        if "content" in databricks_response and "role" in databricks_response:
            self.logger.debug("Response already in Anthropic format")
            return databricks_response
        
        # Fallback: return original response if format is unexpected
        self.logger.warning("Unexpected response format, returning as-is",
                          response_keys=list(databricks_response.keys()))
        return databricks_response
    
    def _convert_openai_style_response(self, openai_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert OpenAI-style response to Anthropic format.
        
        Args:
            openai_response: Response in OpenAI format
            
        Returns:
            Dict in Anthropic format
        """
        choice = openai_response["choices"][0]
        message = choice["message"]
        message_content = message["content"]
        
        # Convert to Anthropic format
        anthropic_response = {
            "id": openai_response.get("id", ""),
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": message_content
                }
            ],
            "model": openai_response.get("model", ""),
            "stop_reason": self._convert_finish_reason(choice.get("finish_reason")),
            "stop_sequence": None,
            "usage": {
                "input_tokens": openai_response.get("usage", {}).get("prompt_tokens", 0),
                "output_tokens": openai_response.get("usage", {}).get("completion_tokens", 0)
            }
        }
        
        self.logger.debug("OpenAI-style response converted to Anthropic format",
                         original_model=openai_response.get("model", "unknown"),
                         input_tokens=anthropic_response["usage"]["input_tokens"],
                         output_tokens=anthropic_response["usage"]["output_tokens"],
                         stop_reason=anthropic_response["stop_reason"])
        
        return anthropic_response
    
    def _convert_finish_reason(self, openai_reason: Optional[str]) -> str:
        """
        Convert OpenAI finish_reason to Anthropic stop_reason.
        
        Args:
            openai_reason: OpenAI finish_reason value
            
        Returns:
            Anthropic stop_reason value
        """
        if not openai_reason:
            return "end_turn"
        
        mapping = {
            "stop": "end_turn",
            "length": "max_tokens",
            "function_call": "tool_use",
            "tool_calls": "tool_use",
            "content_filter": "stop_sequence",
            "null": "end_turn"
        }
        
        return mapping.get(openai_reason.lower(), "end_turn")
    
    def convert_stream_chunk(self, databricks_chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Azure Databricks streaming chunk to Anthropic format.
        
        Args:
            databricks_chunk: Streaming chunk from Azure Databricks
            
        Returns:
            Dict in Anthropic streaming format
        """
        self.logger.debug("Converting streaming chunk",
                         chunk_keys=list(databricks_chunk.keys()))
        
        # Handle OpenAI-style streaming chunks
        if "choices" in databricks_chunk:
            choice = databricks_chunk["choices"][0]
            
            # Check if this is a delta chunk
            if "delta" in choice:
                delta = choice["delta"]
                content = delta.get("content", "")
                
                if content:
                    # Content chunk
                    return {
                        "type": "content_block_delta",
                        "index": 0,
                        "delta": {
                            "type": "text_delta",
                            "text": content
                        }
                    }
                else:
                    # Non-content chunk (e.g., role, finish)
                    return {
                        "type": "message_delta",
                        "delta": {}
                    }
            
            # Handle complete message in chunk
            elif "message" in choice:
                message = choice["message"]
                return {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": message.get("content", "")
                        }
                    ]
                }
        
        # Handle usage information
        if "usage" in databricks_chunk:
            usage = databricks_chunk["usage"]
            return {
                "type": "message_stop",
                "usage": {
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0)
                }
            }
        
        # Fallback for unknown chunk types
        self.logger.debug("Unknown streaming chunk format, returning as-is")
        return databricks_chunk
    
    def validate_anthropic_request(self, request: Dict[str, Any]) -> bool:
        """
        Validate that a request is in proper Anthropic format.
        
        Args:
            request: Request to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["messages"]
        
        for field in required_fields:
            if field not in request:
                self.logger.error("Missing required field in request", field=field)
                return False
        
        # Validate messages format
        messages = request["messages"]
        if not isinstance(messages, list) or len(messages) == 0:
            self.logger.error("Messages must be a non-empty list")
            return False
        
        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                self.logger.error("Message must be a dict", index=i)
                return False
            
            if "role" not in message or "content" not in message:
                self.logger.error("Message missing role or content", index=i)
                return False
            
            if message["role"] not in ["user", "assistant", "system"]:
                self.logger.error("Invalid message role", index=i, role=message["role"])
                return False
        
        self.logger.debug("Request validation passed")
        return True
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """
        Get statistics about conversions performed.
        
        Returns:
            Dict containing conversion statistics
        """
        # This could be enhanced to track conversion metrics
        return {
            "conversions_performed": "tracking_not_implemented",
            "note": "Conversion statistics tracking can be added if needed"
        } 