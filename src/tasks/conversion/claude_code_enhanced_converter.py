"""
Enhanced Schema Converter optimized for Claude Code CLI compatibility.

This module implements the comprehensive Claude Code optimization as outlined in the
Master Implementation Plan Phase 1.1 - Enhanced Schema Converter Implementation.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from src.core.logging_config import get_logger
from src.utils.config import config

logger = get_logger(__name__)


class ClaudeCodeEnhancedConverter:
    """Enhanced converter optimized for Claude Code CLI compatibility."""
    
    def __init__(self):
        """Initialize the Claude Code enhanced converter."""
        # Model mappings based on Claude Code CLI API analysis
        self.claude_code_models = {
            'claude-sonnet-4-20250514': 'openrouter/anthropic/claude-sonnet-4',
            'claude-3-7-sonnet-20250219': 'openrouter/anthropic/claude-3.7-sonnet',
            'claude-3-opus-20240229': 'openrouter/anthropic/claude-3-opus',
            'claude-3.5-sonnet-20240620': 'openrouter/anthropic/claude-3.5-sonnet',
            # Legacy mappings for compatibility
            'claude-sonnet-4': 'openrouter/anthropic/claude-sonnet-4',
            'claude-3.7-sonnet': 'openrouter/anthropic/claude-3.7-sonnet'
        }
        
        # Claude Code specific tools configuration
        self.claude_code_tools = {
            # Core Claude Code Tools
            "str_replace_editor": {"timeout": 15, "category": "file_ops"},
            "bash": {"timeout": 30, "category": "system", "security": "sandboxed"},
            "computer": {"timeout": 45, "category": "system", "requires_permission": True},
            
            # Enhanced File Operations
            "read_file": {"timeout": 10, "max_size": "10MB"},
            "write_file": {"timeout": 10, "max_size": "10MB"},
            "edit_file": {"timeout": 20, "max_size": "10MB"},
            "list_dir": {"timeout": 5},
            "file_search": {"timeout": 15},
            "grep_search": {"timeout": 20},
            "codebase_search": {"timeout": 30},
            
            # Development Tools
            "run_terminal_cmd": {"timeout": 60, "security": "restricted"},
            "create_diagram": {"timeout": 10},
            "web_search": {"timeout": 25},
            
            # Notebook Operations
            "edit_notebook": {"timeout": 15},
            "run_notebook_cell": {"timeout": 45}
        }
        
        # Reasoning profiles for different models
        self.reasoning_profiles = {
            "claude-sonnet-4-20250514": {
                "reasoning_effort": "high",
                "thinking_budget": 2048,
                "enable_step_by_step": True,
                "show_reasoning": True,
                "timeout": 30
            },
            "claude-3-7-sonnet-20250219": {
                "reasoning_effort": "medium", 
                "thinking_budget": 1024,
                "enable_step_by_step": True,
                "show_reasoning": True,
                "timeout": 25
            },
            "claude-3-opus-20240229": {
                "reasoning_effort": "high",
                "thinking_budget": 1536,
                "enable_step_by_step": True,
                "show_reasoning": True,
                "timeout": 35
            },
            "claude-3.5-sonnet-20240620": {
                "reasoning_effort": "medium",
                "thinking_budget": 1024,
                "enable_step_by_step": True,
                "show_reasoning": True,
                "timeout": 25
            }
        }
    
    def _map_claude_code_model(self, model: str) -> str:
        """Map Claude Code model identifier to LiteLLM compatible model."""
        if model in self.claude_code_models:
            mapped_model = self.claude_code_models[model]
            logger.debug("Claude Code model mapped", 
                        original_model=model, 
                        mapped_model=mapped_model)
            return mapped_model
        
        # If not in our mapping, assume it's already properly formatted
        logger.debug("Model not in Claude Code mapping, using as-is", model=model)
        return model
    
    def _supports_reasoning(self, model: str) -> bool:
        """Check if the model supports reasoning content."""
        # Extract base model name for checking
        base_model = model.replace('openrouter/anthropic/', '').replace('anthropic/', '')
        
        # All Claude models support some form of reasoning
        claude_models = ['claude-sonnet-4', 'claude-3.7-sonnet', 'claude-3-opus', 'claude-3.5-sonnet']
        return any(claude_model in base_model for claude_model in claude_models)
    
    def _is_claude_code_request(self, anthropic_request: Dict) -> bool:
        """Detect if this is a Claude Code CLI request."""
        # Check for Claude Code specific patterns
        tools = anthropic_request.get('tools', [])
        tool_names = [tool.get('name', '') for tool in tools if isinstance(tool, dict)]
        
        # Claude Code commonly uses these tools
        claude_code_indicators = [
            'str_replace_editor', 'bash', 'computer', 'read_file', 'write_file',
            'edit_file', 'codebase_search', 'run_terminal_cmd'
        ]
        
        has_claude_code_tools = any(tool_name in claude_code_indicators for tool_name in tool_names)
        
        # Also check for Claude Code user agent or headers (if available)
        is_claude_code = has_claude_code_tools
        
        if is_claude_code:
            logger.debug("Claude Code CLI request detected", tools_count=len(tools))
        
        return is_claude_code
    
    def _enhance_messages_for_claude_code(self, messages: List[Dict]) -> List[Dict]:
        """Enhance messages for Claude Code CLI optimization."""
        enhanced_messages = []
        
        for message in messages:
            enhanced_message = message.copy()
            
            # Add Claude Code specific optimizations
            if message.get('role') == 'system':
                # Enhance system messages for better Claude Code performance
                content = message.get('content', '')
                if isinstance(content, str) and 'coding' in content.lower():
                    enhanced_message['content'] = self._optimize_system_prompt_for_claude_code(content)
            
            enhanced_messages.append(enhanced_message)
        
        return enhanced_messages
    
    def _optimize_system_prompt_for_claude_code(self, content: str) -> str:
        """Optimize system prompt for Claude Code workflows."""
        # Add Claude Code specific instructions if not present
        claude_code_optimizations = [
            "Use tools efficiently and provide clear explanations.",
            "For file operations, always verify changes before proceeding.",
            "For code execution, explain what the code does before running it."
        ]
        
        # Only add if content doesn't already contain similar instructions
        if 'tool' in content.lower() and len(content) > 200:
            # Already has tool instructions, don't modify
            return content
        
        # Add Claude Code optimizations
        optimized_content = content
        if not content.endswith('\n'):
            optimized_content += '\n'
        
        optimized_content += '\n'.join(claude_code_optimizations)
        return optimized_content
    
    def _convert_anthropic_tools_to_openai(self, tools: List[Dict]) -> List[Dict]:
        """Convert Anthropic tool format to OpenAI function calling format."""
        openai_tools = []
        
        for tool in tools:
            if not isinstance(tool, dict):
                continue
                
            tool_name = tool.get('name', '')
            tool_description = tool.get('description', '')
            input_schema = tool.get('input_schema', {})
            
            # Convert to OpenAI function calling format
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_description,
                    "parameters": input_schema
                }
            }
            
            # Add Claude Code specific tool optimizations
            if tool_name in self.claude_code_tools:
                tool_config = self.claude_code_tools[tool_name]
                
                # Add timeout metadata (some providers support this)
                if 'timeout' in tool_config:
                    openai_tool['function']['timeout'] = tool_config['timeout']
                
                # Add security metadata
                if 'security' in tool_config:
                    openai_tool['function']['security'] = tool_config['security']
            
            openai_tools.append(openai_tool)
        
        logger.debug("Converted Anthropic tools to OpenAI format", 
                    tools_count=len(openai_tools))
        return openai_tools
    
    def _convert_tool_choice(self, tool_choice: Union[str, Dict]) -> Union[str, Dict]:
        """Convert Anthropic tool_choice to OpenAI format."""
        if isinstance(tool_choice, str):
            # Direct mapping for string values
            if tool_choice == "auto":
                return "auto"
            elif tool_choice == "any":
                return "required"  # OpenAI equivalent
            elif tool_choice == "tool":
                return "required"
            else:
                return "auto"  # Safe fallback
        
        elif isinstance(tool_choice, dict):
            # Handle specific tool selection
            if "name" in tool_choice:
                return {
                    "type": "function",
                    "function": {"name": tool_choice["name"]}
                }
        
        return "auto"  # Safe fallback
    
    async def anthropic_to_litellm_enhanced(self, anthropic_request: Dict) -> Dict:
        """Convert Anthropic format to LiteLLM with Claude Code optimizations."""
        
        # Extract model and map it
        original_model = anthropic_request.get('model', 'claude-3.7-sonnet')
        mapped_model = self._map_claude_code_model(original_model)
        
        # Base conversion
        litellm_request = {
            "model": mapped_model,
            "messages": self._enhance_messages_for_claude_code(anthropic_request.get('messages', [])),
            "max_tokens": min(anthropic_request.get('max_tokens', 8192), 8192),
            "temperature": anthropic_request.get('temperature', 0.7),
            "top_p": anthropic_request.get('top_p', 0.9),
            "stream": anthropic_request.get('stream', False)
        }
        
        # 🧠 Reasoning Support (Based on Claude Code CLI API)
        if self._supports_reasoning(mapped_model) and original_model in self.reasoning_profiles:
            profile = self.reasoning_profiles[original_model]
            
            # Add reasoning parameters if supported by LiteLLM
            try:
                litellm_request.update({
                    "reasoning_effort": profile.get("reasoning_effort", "medium"),
                    "thinking": {
                        "type": "enabled", 
                        "budget_tokens": profile.get("thinking_budget", 1024)
                    }
                })
                logger.debug("Added reasoning support", 
                           model=original_model, 
                           effort=profile.get("reasoning_effort"))
            except Exception as e:
                logger.warning("Failed to add reasoning support", 
                             model=original_model, 
                             error=str(e))
        
        # 🛠️ Tool Calling Enhancement (Critical for Claude Code)
        if 'tools' in anthropic_request and anthropic_request['tools']:
            litellm_request['tools'] = self._convert_anthropic_tools_to_openai(
                anthropic_request['tools']
            )
            litellm_request['tool_choice'] = self._convert_tool_choice(
                anthropic_request.get('tool_choice', 'auto')
            )
            
            logger.debug("Added tool calling support", 
                        tools_count=len(anthropic_request['tools']))
        
        # 🔧 Claude Code specific optimizations
        if self._is_claude_code_request(anthropic_request):
            model_profile = self.reasoning_profiles.get(original_model, {})
            timeout = model_profile.get('timeout', 60)
            
            litellm_request.update({
                "drop_params": True,  # Auto-handle unsupported params
                "timeout": timeout,   # Optimized for tool execution
                "metadata": {
                    "claude_code_optimized": True,
                    "original_model": original_model,
                    "optimization_profile": model_profile.get("reasoning_effort", "medium")
                }
            })
            
            logger.info("Applied Claude Code optimizations", 
                       model=original_model, 
                       timeout=timeout)
        
        # Add system prompt enhancement for Claude Code
        if anthropic_request.get('system'):
            # Convert system prompt to message format expected by LiteLLM
            system_message = {
                "role": "system",
                "content": anthropic_request['system']
            }
            litellm_request['messages'].insert(0, system_message)
        
        logger.debug("Enhanced Anthropic to LiteLLM conversion completed", 
                    original_model=original_model, 
                    mapped_model=mapped_model,
                    has_tools=bool(anthropic_request.get('tools')),
                    is_claude_code=self._is_claude_code_request(anthropic_request))
        
        return litellm_request
    
    async def litellm_to_anthropic_enhanced(self, litellm_response: Dict, original_request: Dict) -> Dict:
        """Convert LiteLLM response back to Anthropic format with Claude Code enhancements."""
        
        # Extract thinking content if available
        thinking_data = self._extract_claude_code_thinking(litellm_response)
        
        # Base conversion to Anthropic format
        anthropic_response = {
            "id": litellm_response.get("id", f"msg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            "type": "message",
            "role": "assistant",
            "model": original_request.get("model", "claude-3.7-sonnet"),
            "content": [],
            "usage": {
                "input_tokens": litellm_response.get("usage", {}).get("prompt_tokens", 0),
                "output_tokens": litellm_response.get("usage", {}).get("completion_tokens", 0)
            },
            "stop_reason": self._convert_stop_reason(litellm_response.get("finish_reason", "stop"))
        }
        
        # Add thinking content if available (Claude Code CLI feature)
        if thinking_data["has_reasoning"]:
            anthropic_response["reasoning_content"] = thinking_data
            logger.debug("Added reasoning content to response", 
                        thinking_blocks=len(thinking_data.get("thinking_blocks", [])))
        
        # Handle content from LiteLLM response
        choices = litellm_response.get("choices", [])
        if choices:
            choice = choices[0]
            message = choice.get("message", {})
            content = message.get("content", "")
            
            if content:
                anthropic_response["content"].append({
                    "type": "text",
                    "text": content
                })
            
            # Handle tool calls if present
            tool_calls = message.get("tool_calls", [])
            if tool_calls:
                for tool_call in tool_calls:
                    anthropic_response["content"].append({
                        "type": "tool_use",
                        "id": tool_call.get("id", ""),
                        "name": tool_call.get("function", {}).get("name", ""),
                        "input": json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                    })
        
        return anthropic_response
    
    def _extract_claude_code_thinking(self, response: Dict) -> Dict:
        """Extract and format thinking blocks for Claude Code CLI."""
        
        thinking_data = {
            "has_reasoning": False,
            "thinking_blocks": [],
            "reasoning_tokens": 0,
            "confidence_score": 0.0
        }
        
        # Try to extract reasoning content from various response formats
        choices = response.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            
            # Check for reasoning_content field
            if hasattr(message, 'reasoning_content') or 'reasoning_content' in message:
                thinking_data["has_reasoning"] = True
                thinking_data["reasoning_content"] = getattr(message, 'reasoning_content', 
                                                           message.get('reasoning_content'))
            
            # Check for thinking_blocks field
            if hasattr(message, 'thinking_blocks') or 'thinking_blocks' in message:
                blocks = getattr(message, 'thinking_blocks', message.get('thinking_blocks', []))
                thinking_data["thinking_blocks"] = [
                    {
                        "step": i + 1,
                        "type": "reasoning",
                        "content": block.get("thinking", "") if isinstance(block, dict) else str(block),
                        "confidence": self._calculate_confidence(block),
                        "tokens_used": len(str(block).split()) if block else 0
                    }
                    for i, block in enumerate(blocks)
                ]
                
                thinking_data["reasoning_tokens"] = sum(
                    block["tokens_used"] for block in thinking_data["thinking_blocks"]
                )
                thinking_data["has_reasoning"] = True
        
        return thinking_data
    
    def _calculate_confidence(self, block: Union[Dict, str]) -> float:
        """Calculate confidence score for a reasoning block."""
        if isinstance(block, dict) and 'confidence' in block:
            return float(block['confidence'])
        
        # Simple heuristic based on content length and keywords
        content = str(block) if block else ""
        
        # Longer, more detailed reasoning generally indicates higher confidence
        base_confidence = min(0.9, len(content) / 1000)  # Max 0.9 based on length
        
        # Adjust based on uncertainty keywords
        uncertainty_keywords = ['maybe', 'possibly', 'might', 'could', 'unsure', 'uncertain']
        certainty_keywords = ['definitely', 'clearly', 'obviously', 'certainly', 'confident']
        
        content_lower = content.lower()
        uncertainty_count = sum(1 for keyword in uncertainty_keywords if keyword in content_lower)
        certainty_count = sum(1 for keyword in certainty_keywords if keyword in content_lower)
        
        # Adjust confidence based on language used
        confidence_adjustment = (certainty_count - uncertainty_count) * 0.1
        final_confidence = max(0.1, min(0.99, base_confidence + confidence_adjustment))
        
        return round(final_confidence, 2)
    
    def _convert_stop_reason(self, finish_reason: str) -> str:
        """Convert LiteLLM finish_reason to Anthropic stop_reason."""
        mapping = {
            "stop": "end_turn",
            "length": "max_tokens",
            "tool_calls": "tool_use",
            "content_filter": "stop_sequence",
            "function_call": "tool_use"
        }
        return mapping.get(finish_reason, "end_turn") 