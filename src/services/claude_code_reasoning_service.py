"""
Claude Code Reasoning Service for thinking blocks and reasoning effort optimization.

This module implements the comprehensive reasoning content integration as outlined in the
Master Implementation Plan Phase 1.3 - Reasoning Content Integration.
"""

import json
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from src.core.logging_config import get_logger
from src.utils.config import config

logger = get_logger(__name__)


class ClaudeCodeReasoningService:
    """Reasoning service optimized for Claude Code CLI thinking blocks."""
    
    def __init__(self):
        """Initialize the Claude Code reasoning service."""
        
        # Model-specific reasoning configurations
        self.reasoning_profiles = {
            "claude-sonnet-4-20250514": {
                "reasoning_effort": "high",
                "thinking_budget": 2048,
                "enable_step_by_step": True,
                "show_reasoning": True,
                "confidence_threshold": 0.8,
                "max_thinking_steps": 10,
                "reasoning_timeout": 30
            },
            "claude-3-7-sonnet-20250219": {
                "reasoning_effort": "medium", 
                "thinking_budget": 1024,
                "enable_step_by_step": True,
                "show_reasoning": True,
                "confidence_threshold": 0.7,
                "max_thinking_steps": 8,
                "reasoning_timeout": 25
            },
            "claude-3-opus-20240229": {
                "reasoning_effort": "high",
                "thinking_budget": 1536,
                "enable_step_by_step": True,
                "show_reasoning": True,
                "confidence_threshold": 0.8,
                "max_thinking_steps": 12,
                "reasoning_timeout": 35
            },
            "claude-3.5-sonnet-20240620": {
                "reasoning_effort": "medium",
                "thinking_budget": 1024,
                "enable_step_by_step": True,
                "show_reasoning": True,
                "confidence_threshold": 0.7,
                "max_thinking_steps": 8,
                "reasoning_timeout": 25
            }
        }
        
        # Reasoning quality metrics
        self.reasoning_metrics = {
            "total_requests": 0,
            "reasoning_enabled_requests": 0,
            "average_thinking_tokens": 0,
            "average_confidence_score": 0.0,
            "reasoning_quality_scores": [],
            "step_by_step_usage": 0,
            "model_usage": {}
        }
        
        # Thinking pattern templates for Claude Code
        self.thinking_patterns = {
            "problem_analysis": {
                "description": "Systematic problem breakdown",
                "steps": [
                    "Understand the problem",
                    "Identify constraints and requirements",
                    "Consider available tools and approaches",
                    "Evaluate potential solutions"
                ]
            },
            "code_analysis": {
                "description": "Code review and analysis",
                "steps": [
                    "Examine the code structure",
                    "Identify potential issues",
                    "Check for best practices",
                    "Suggest improvements"
                ]
            },
            "tool_selection": {
                "description": "Tool selection reasoning",
                "steps": [
                    "Assess the task requirements",
                    "Compare available tools",
                    "Consider efficiency and safety",
                    "Select optimal tool combination"
                ]
            },
            "error_resolution": {
                "description": "Error analysis and resolution",
                "steps": [
                    "Understand the error context",
                    "Identify root causes",
                    "Develop resolution strategy",
                    "Implement and verify fix"
                ]
            }
        }
    
    def _supports_reasoning(self, model: str) -> bool:
        """Check if the model supports reasoning content."""
        # Extract base model name for checking
        base_model = model.replace('openrouter/anthropic/', '').replace('anthropic/', '')
        
        # All Claude models in our profiles support reasoning
        return any(profile_model in base_model for profile_model in self.reasoning_profiles.keys())
    
    def _get_reasoning_profile(self, model: str) -> Dict:
        """Get reasoning profile for the specified model."""
        # Try direct match first
        if model in self.reasoning_profiles:
            return self.reasoning_profiles[model]
        
        # Try to match based on model name patterns
        for profile_model, profile in self.reasoning_profiles.items():
            if profile_model in model or any(part in model for part in profile_model.split('-')):
                return profile
        
        # Default profile for Claude models
        return {
            "reasoning_effort": "medium",
            "thinking_budget": 1024,
            "enable_step_by_step": True,
            "show_reasoning": True,
            "confidence_threshold": 0.7,
            "max_thinking_steps": 6,
            "reasoning_timeout": 20
        }
    
    def _detect_reasoning_context(self, request: Dict) -> str:
        """Detect the type of reasoning context from the request."""
        messages = request.get('messages', [])
        tools = request.get('tools', [])
        
        # Analyze content for context clues
        content_text = ""
        for message in messages:
            if isinstance(message.get('content'), str):
                content_text += message['content'].lower() + " "
            elif isinstance(message.get('content'), list):
                for content_block in message['content']:
                    if isinstance(content_block, dict) and content_block.get('type') == 'text':
                        content_text += content_block.get('text', '').lower() + " "
        
        # Context detection based on keywords and tools
        if tools and len(tools) > 0:
            return "tool_selection"
        elif any(keyword in content_text for keyword in ['error', 'bug', 'issue', 'problem', 'fix']):
            return "error_resolution"
        elif any(keyword in content_text for keyword in ['code', 'function', 'class', 'method', 'review']):
            return "code_analysis"
        else:
            return "problem_analysis"
    
    def _generate_thinking_prompt(self, context_type: str, request: Dict) -> str:
        """Generate a thinking prompt based on context type."""
        pattern = self.thinking_patterns.get(context_type, self.thinking_patterns["problem_analysis"])
        
        prompt_parts = [
            f"Approach this as a {pattern['description']} task.",
            "Think through this step by step:",
        ]
        
        for i, step in enumerate(pattern['steps'], 1):
            prompt_parts.append(f"{i}. {step}")
        
        prompt_parts.append("Consider your confidence level at each step.")
        
        return "\n".join(prompt_parts)
    
    async def enhance_with_claude_code_reasoning(
        self, 
        request: Dict, 
        model: str
    ) -> Dict:
        """Enhance request with Claude Code compatible reasoning."""
        
        if not self._supports_reasoning(model):
            logger.debug("Model does not support reasoning", model=model)
            return request
        
        profile = self._get_reasoning_profile(model)
        enhanced_request = request.copy()
        
        # Add reasoning parameters if supported by LiteLLM
        try:
            reasoning_params = {
                "reasoning_effort": profile.get("reasoning_effort", "medium"),
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": profile.get("thinking_budget", 1024),
                    "show_reasoning": profile.get("show_reasoning", True)
                }
            }
            
            # Add step-by-step reasoning if enabled
            if profile.get("enable_step_by_step", True):
                context_type = self._detect_reasoning_context(request)
                thinking_prompt = self._generate_thinking_prompt(context_type, request)
                
                # Add thinking prompt to system message or create one
                messages = enhanced_request.get('messages', [])
                
                # Find or create system message
                system_message_idx = -1
                for i, msg in enumerate(messages):
                    if msg.get('role') == 'system':
                        system_message_idx = i
                        break
                
                if system_message_idx >= 0:
                    # Enhance existing system message
                    current_content = messages[system_message_idx].get('content', '')
                    enhanced_content = f"{current_content}\n\n{thinking_prompt}"
                    messages[system_message_idx]['content'] = enhanced_content
                else:
                    # Create new system message
                    system_message = {
                        "role": "system",
                        "content": thinking_prompt
                    }
                    messages.insert(0, system_message)
                
                enhanced_request['messages'] = messages
            
            # Add reasoning parameters to the request
            enhanced_request.update(reasoning_params)
            
            # Update metrics
            self._update_reasoning_metrics(model, reasoning_enabled=True)
            
            logger.debug("Enhanced request with reasoning support", 
                       model=model, 
                       effort=profile.get("reasoning_effort"),
                       thinking_budget=profile.get("thinking_budget"))
            
        except Exception as e:
            logger.warning("Failed to enhance request with reasoning", 
                         model=model, 
                         error=str(e))
            
            # Update metrics for failed enhancement
            self._update_reasoning_metrics(model, reasoning_enabled=False)
        
        return enhanced_request
    
    def extract_claude_code_thinking(self, response: Dict, model: str) -> Dict:
        """Extract and format thinking blocks for Claude Code CLI."""
        
        thinking_data = {
            "has_reasoning": False,
            "thinking_blocks": [],
            "reasoning_tokens": 0,
            "confidence_score": 0.0,
            "reasoning_quality": 0.0,
            "step_count": 0,
            "model_used": model,
            "extraction_timestamp": datetime.utcnow().isoformat()
        }
        
        # Try to extract reasoning content from various response formats
        choices = response.get("choices", [])
        if not choices:
            return thinking_data
        
        choice = choices[0]
        message = choice.get("message", {})
        
        # Check for reasoning_content field
        if hasattr(message, 'reasoning_content') or 'reasoning_content' in message:
            thinking_data["has_reasoning"] = True
            reasoning_content = getattr(message, 'reasoning_content', message.get('reasoning_content'))
            thinking_data["reasoning_content"] = reasoning_content
            
            # Analyze reasoning content
            if isinstance(reasoning_content, str):
                thinking_data["reasoning_tokens"] = len(reasoning_content.split())
                thinking_data["confidence_score"] = self._analyze_reasoning_confidence(reasoning_content)
        
        # Check for thinking_blocks field
        if hasattr(message, 'thinking_blocks') or 'thinking_blocks' in message:
            blocks = getattr(message, 'thinking_blocks', message.get('thinking_blocks', []))
            
            thinking_blocks = []
            total_tokens = 0
            confidence_scores = []
            
            for i, block in enumerate(blocks):
                if isinstance(block, dict):
                    block_content = block.get("thinking", block.get("content", ""))
                    block_confidence = block.get("confidence", self._calculate_confidence(block_content))
                else:
                    block_content = str(block)
                    block_confidence = self._calculate_confidence(block_content)
                
                tokens_used = len(str(block_content).split()) if block_content else 0
                total_tokens += tokens_used
                confidence_scores.append(block_confidence)
                
                thinking_block = {
                    "step": i + 1,
                    "type": "reasoning",
                    "content": block_content,
                    "confidence": block_confidence,
                    "tokens_used": tokens_used,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                thinking_blocks.append(thinking_block)
            
            thinking_data["thinking_blocks"] = thinking_blocks
            thinking_data["reasoning_tokens"] = total_tokens
            thinking_data["step_count"] = len(thinking_blocks)
            thinking_data["has_reasoning"] = True
            
            # Calculate overall confidence
            if confidence_scores:
                thinking_data["confidence_score"] = sum(confidence_scores) / len(confidence_scores)
        
        # Calculate reasoning quality score
        if thinking_data["has_reasoning"]:
            thinking_data["reasoning_quality"] = self._calculate_reasoning_quality(thinking_data)
            
            # Update metrics
            self._update_reasoning_extraction_metrics(thinking_data, model)
        
        return thinking_data
    
    def _analyze_reasoning_confidence(self, reasoning_content: str) -> float:
        """Analyze confidence level in reasoning content."""
        if not reasoning_content:
            return 0.0
        
        content_lower = reasoning_content.lower()
        
        # Confidence indicators
        high_confidence_indicators = [
            'certain', 'definitely', 'clearly', 'obviously', 'confident',
            'sure', 'absolutely', 'undoubtedly', 'precisely'
        ]
        
        low_confidence_indicators = [
            'maybe', 'possibly', 'might', 'could', 'perhaps',
            'uncertain', 'unsure', 'unclear', 'ambiguous'
        ]
        
        # Count indicators
        high_confidence_count = sum(1 for indicator in high_confidence_indicators if indicator in content_lower)
        low_confidence_count = sum(1 for indicator in low_confidence_indicators if indicator in content_lower)
        
        # Base confidence on content length and structure
        base_confidence = min(0.8, len(reasoning_content) / 2000)  # Longer reasoning = higher confidence
        
        # Adjust based on indicators
        confidence_adjustment = (high_confidence_count - low_confidence_count) * 0.1
        final_confidence = max(0.1, min(0.99, base_confidence + confidence_adjustment))
        
        return round(final_confidence, 2)
    
    def _calculate_confidence(self, content: str) -> float:
        """Calculate confidence score for reasoning content."""
        if not content:
            return 0.0
        
        # Use the same logic as analyze_reasoning_confidence
        return self._analyze_reasoning_confidence(content)
    
    def _calculate_reasoning_quality(self, thinking_data: Dict) -> float:
        """Calculate overall reasoning quality score."""
        quality_factors = []
        
        # Factor 1: Number of reasoning steps (more steps = better reasoning)
        step_count = thinking_data.get("step_count", 0)
        step_score = min(1.0, step_count / 5)  # Optimal around 5 steps
        quality_factors.append(step_score)
        
        # Factor 2: Token usage (adequate depth without excessive verbosity)
        token_count = thinking_data.get("reasoning_tokens", 0)
        token_score = min(1.0, max(0.1, 1 - abs(token_count - 500) / 1000))  # Optimal around 500 tokens
        quality_factors.append(token_score)
        
        # Factor 3: Average confidence score
        confidence_score = thinking_data.get("confidence_score", 0.0)
        quality_factors.append(confidence_score)
        
        # Factor 4: Consistency of thinking blocks
        thinking_blocks = thinking_data.get("thinking_blocks", [])
        if thinking_blocks:
            block_lengths = [len(block.get("content", "")) for block in thinking_blocks]
            if block_lengths:
                avg_length = sum(block_lengths) / len(block_lengths)
                length_variance = sum((length - avg_length) ** 2 for length in block_lengths) / len(block_lengths)
                consistency_score = max(0.1, 1 - (length_variance / (avg_length ** 2)) if avg_length > 0 else 0.1)
                quality_factors.append(consistency_score)
        
        # Calculate weighted average
        if quality_factors:
            quality_score = sum(quality_factors) / len(quality_factors)
        else:
            quality_score = 0.0
        
        return round(quality_score, 2)
    
    def _update_reasoning_metrics(self, model: str, reasoning_enabled: bool):
        """Update reasoning metrics."""
        self.reasoning_metrics["total_requests"] += 1
        
        if reasoning_enabled:
            self.reasoning_metrics["reasoning_enabled_requests"] += 1
        
        # Update model usage
        if model not in self.reasoning_metrics["model_usage"]:
            self.reasoning_metrics["model_usage"][model] = {
                "total_requests": 0,
                "reasoning_enabled": 0,
                "average_quality": 0.0
            }
        
        model_stats = self.reasoning_metrics["model_usage"][model]
        model_stats["total_requests"] += 1
        
        if reasoning_enabled:
            model_stats["reasoning_enabled"] += 1
    
    def _update_reasoning_extraction_metrics(self, thinking_data: Dict, model: str):
        """Update metrics after reasoning extraction."""
        reasoning_tokens = thinking_data.get("reasoning_tokens", 0)
        confidence_score = thinking_data.get("confidence_score", 0.0)
        quality_score = thinking_data.get("reasoning_quality", 0.0)
        
        # Update global averages
        total_requests = self.reasoning_metrics["reasoning_enabled_requests"]
        if total_requests > 0:
            current_avg_tokens = self.reasoning_metrics["average_thinking_tokens"]
            self.reasoning_metrics["average_thinking_tokens"] = (
                (current_avg_tokens * (total_requests - 1) + reasoning_tokens) / total_requests
            )
            
            current_avg_confidence = self.reasoning_metrics["average_confidence_score"]
            self.reasoning_metrics["average_confidence_score"] = (
                (current_avg_confidence * (total_requests - 1) + confidence_score) / total_requests
            )
        
        # Track quality scores
        self.reasoning_metrics["reasoning_quality_scores"].append(quality_score)
        
        # Update model-specific metrics
        if model in self.reasoning_metrics["model_usage"]:
            model_stats = self.reasoning_metrics["model_usage"][model]
            reasoning_count = model_stats["reasoning_enabled"]
            
            if reasoning_count > 0:
                current_model_quality = model_stats["average_quality"]
                model_stats["average_quality"] = (
                    (current_model_quality * (reasoning_count - 1) + quality_score) / reasoning_count
                )
    
    def get_reasoning_metrics(self) -> Dict:
        """Get comprehensive reasoning metrics."""
        metrics = self.reasoning_metrics.copy()
        
        # Calculate derived metrics
        total_requests = metrics["total_requests"]
        if total_requests > 0:
            metrics["reasoning_adoption_rate"] = metrics["reasoning_enabled_requests"] / total_requests
        else:
            metrics["reasoning_adoption_rate"] = 0.0
        
        # Calculate overall quality statistics
        quality_scores = metrics["reasoning_quality_scores"]
        if quality_scores:
            metrics["average_reasoning_quality"] = sum(quality_scores) / len(quality_scores)
            metrics["max_reasoning_quality"] = max(quality_scores)
            metrics["min_reasoning_quality"] = min(quality_scores)
        else:
            metrics["average_reasoning_quality"] = 0.0
            metrics["max_reasoning_quality"] = 0.0
            metrics["min_reasoning_quality"] = 0.0
        
        # Add configuration info
        metrics["supported_models"] = list(self.reasoning_profiles.keys())
        metrics["thinking_patterns"] = list(self.thinking_patterns.keys())
        
        return metrics
    
    def get_model_reasoning_capabilities(self, model: str) -> Dict:
        """Get reasoning capabilities for a specific model."""
        profile = self._get_reasoning_profile(model)
        
        return {
            "model": model,
            "supports_reasoning": self._supports_reasoning(model),
            "reasoning_profile": profile,
            "optimization_level": profile.get("reasoning_effort", "medium"),
            "thinking_budget": profile.get("thinking_budget", 1024),
            "max_steps": profile.get("max_thinking_steps", 6),
            "timeout": profile.get("reasoning_timeout", 20)
        } 