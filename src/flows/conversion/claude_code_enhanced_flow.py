"""
Claude Code Enhanced Conversion Flow.

This module integrates all Phase 1 Claude Code optimizations into a unified conversion flow
as outlined in the Master Implementation Plan.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from ...services.base import ConversionService, InstructorService
from ...models.anthropic import MessagesRequest
from ...models.litellm import LiteLLMMessage, LiteLLMRequest
from ...models.instructor import ConversionResult
from ...core.logging_config import get_logger

# Import Claude Code optimized services
from ...tasks.conversion.claude_code_enhanced_converter import ClaudeCodeEnhancedConverter
from ...services.claude_code_tool_service import ClaudeCodeToolService
from ...services.claude_code_reasoning_service import ClaudeCodeReasoningService

# Import existing conversion tasks for compatibility
from ...tasks.conversion.model_mapping_tasks import map_model_name
from ...tasks.conversion.message_conversion_tasks import (
    extract_system_message_content,
    convert_anthropic_message_to_litellm,
    handle_tool_result_blocks,
    create_system_message
)
from ...utils.config import config, OPENROUTER_API_BASE

logger = get_logger("conversion.claude_code_enhanced")


class ClaudeCodeEnhancedFlow(ConversionService[MessagesRequest, LiteLLMRequest], InstructorService):
    """Enhanced conversion flow optimized for Claude Code CLI compatibility."""
    
    def __init__(self):
        """Initialize Claude Code enhanced flow."""
        ConversionService.__init__(self, "ClaudeCodeEnhanced")
        InstructorService.__init__(self, "ClaudeCodeEnhanced")
        
        # Initialize Claude Code optimized services
        self.claude_converter = ClaudeCodeEnhancedConverter()
        self.tool_service = ClaudeCodeToolService()
        self.reasoning_service = ClaudeCodeReasoningService()
        
        # Performance tracking
        self.conversion_metrics = {
            "total_conversions": 0,
            "claude_code_optimized": 0,
            "reasoning_enhanced": 0,
            "tool_optimized": 0,
            "average_conversion_time": 0.0,
            "model_usage": {}
        }
    
    async def convert(self, source: MessagesRequest, **kwargs) -> ConversionResult:
        """Convert Anthropic MessagesRequest to LiteLLM format with Claude Code optimizations."""
        start_time = datetime.utcnow()
        
        try:
            # Initialize conversion metadata
            conversion_metadata = self._initialize_claude_code_metadata(source)
            
            # Detect if this is a Claude Code request
            is_claude_code_request = self._detect_claude_code_request(source)
            conversion_metadata["is_claude_code_request"] = is_claude_code_request
            
            if is_claude_code_request:
                logger.info("Claude Code CLI request detected - applying optimizations",
                           model=source.model,
                           tool_count=len(source.tools) if source.tools else 0)
                
                # Use Claude Code enhanced conversion path
                conversion_result = await self._convert_with_claude_code_optimizations(
                    source, conversion_metadata
                )
            else:
                logger.debug("Standard request - using standard conversion",
                            model=source.model)
                
                # Use standard conversion path with lightweight enhancements
                conversion_result = await self._convert_with_standard_enhancements(
                    source, conversion_metadata
                )
            
            # Update metrics
            conversion_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_conversion_metrics(source.model, conversion_time, is_claude_code_request)
            
            # Add performance metadata
            conversion_metadata.update({
                "conversion_time_seconds": conversion_time,
                "optimization_level": "claude_code" if is_claude_code_request else "standard"
            })
            
            # Log success
            self.log_operation(
                "claude_code_enhanced_conversion",
                True,
                **conversion_metadata
            )
            
            return self.create_conversion_result(
                success=True,
                converted_data=conversion_result,
                metadata=conversion_metadata
            )
            
        except Exception as e:
            conversion_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error("Claude Code enhanced conversion failed",
                        error=str(e),
                        model=source.model,
                        conversion_time=conversion_time,
                        exc_info=True)
            
            return self.create_conversion_result(
                success=False,
                errors=[f"Claude Code enhanced conversion failed: {str(e)}"],
                metadata={
                    "error_type": type(e).__name__,
                    "conversion_time_seconds": conversion_time
                }
            )
    
    def _initialize_claude_code_metadata(self, source: MessagesRequest) -> Dict[str, Any]:
        """Initialize Claude Code specific conversion metadata."""
        return {
            "original_message_count": len(source.messages),
            "converted_message_count": 0,
            "tool_conversions": 0,
            "reasoning_enhanced": False,
            "claude_code_optimizations_applied": [],
            "model_optimization_profile": None,
            "system_message_added": False,
            "conversion_timestamp": datetime.utcnow().isoformat()
        }
    
    def _detect_claude_code_request(self, source: MessagesRequest) -> bool:
        """Detect if this is a Claude Code CLI request."""
        # Use the enhanced converter's detection logic
        source_dict = source.model_dump()
        return self.claude_converter._is_claude_code_request(source_dict)
    
    async def _convert_with_claude_code_optimizations(
        self, 
        source: MessagesRequest, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert using full Claude Code optimizations."""
        
        # Convert to dictionary for processing
        source_dict = source.model_dump()
        
        # Step 1: Apply reasoning enhancements
        enhanced_request = await self.reasoning_service.enhance_with_claude_code_reasoning(
            source_dict, source.model
        )
        
        if enhanced_request != source_dict:
            metadata["reasoning_enhanced"] = True
            metadata["claude_code_optimizations_applied"].append("reasoning_enhancement")
            logger.debug("Applied reasoning enhancements", model=source.model)
        
        # Step 2: Apply Claude Code enhanced conversion
        litellm_request = await self.claude_converter.anthropic_to_litellm_enhanced(enhanced_request)
        
        # Step 3: Validate and optimize tools if present
        if source.tools:
            await self._validate_and_optimize_tools(source.tools, metadata)
        
        # Step 4: Add Claude Code specific metadata
        litellm_request["metadata"] = {
            **litellm_request.get("metadata", {}),
            "claude_code_optimized": True,
            "optimization_timestamp": datetime.utcnow().isoformat(),
            "tool_count": len(source.tools) if source.tools else 0
        }
        
        # Step 5: Apply final optimizations
        self._apply_final_claude_code_optimizations(litellm_request, source, metadata)
        
        return litellm_request
    
    async def _convert_with_standard_enhancements(
        self, 
        source: MessagesRequest, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert using standard path with lightweight Claude Code enhancements."""
        
        # Convert to dictionary for processing
        source_dict = source.model_dump()
        
        # Apply lightweight reasoning enhancement if the model supports it
        if self.reasoning_service._supports_reasoning(source.model):
            enhanced_request = await self.reasoning_service.enhance_with_claude_code_reasoning(
                source_dict, source.model
            )
            
            if enhanced_request != source_dict:
                metadata["reasoning_enhanced"] = True
                metadata["claude_code_optimizations_applied"].append("lightweight_reasoning")
        else:
            enhanced_request = source_dict
        
        # Use enhanced converter for model mapping and basic optimizations
        litellm_request = await self.claude_converter.anthropic_to_litellm_enhanced(enhanced_request)
        
        # Add standard metadata
        litellm_request["metadata"] = {
            **litellm_request.get("metadata", {}),
            "enhanced_conversion": True,
            "optimization_level": "standard"
        }
        
        return litellm_request
    
    async def _validate_and_optimize_tools(self, tools: List, metadata: Dict[str, Any]) -> None:
        """Validate and optimize tools for Claude Code workflows."""
        
        # Get available Claude Code tools
        available_tools = self.tool_service.get_available_claude_code_tools()
        
        optimized_tools = []
        unsupported_tools = []
        
        for tool in tools:
            tool_name = tool.name if hasattr(tool, 'name') else str(tool)
            
            if tool_name in available_tools:
                optimized_tools.append(tool_name)
                logger.debug("Tool optimization available", tool=tool_name)
            else:
                unsupported_tools.append(tool_name)
                logger.debug("Tool not in Claude Code optimization set", tool=tool_name)
        
        # Update metadata
        metadata.update({
            "tool_conversions": len(tools),
            "optimized_tools": optimized_tools,
            "unsupported_tools": unsupported_tools,
            "tool_optimization_ratio": len(optimized_tools) / len(tools) if tools else 0.0
        })
        
        if optimized_tools:
            metadata["claude_code_optimizations_applied"].append("tool_optimization")
    
    def _apply_final_claude_code_optimizations(
        self, 
        litellm_request: Dict[str, Any], 
        source: MessagesRequest, 
        metadata: Dict[str, Any]
    ) -> None:
        """Apply final Claude Code specific optimizations."""
        
        # Get model optimization profile
        profile = self.claude_converter.reasoning_profiles.get(source.model, {})
        metadata["model_optimization_profile"] = profile.get("reasoning_effort", "medium")
        
        # Add Claude Code specific headers and settings
        extra_headers = litellm_request.get("extra_headers", {})
        extra_headers.update({
            "X-Claude-Code-Optimized": "true",
            "X-Optimization-Profile": profile.get("reasoning_effort", "medium"),
            "X-Tool-Count": str(len(source.tools) if source.tools else 0)
        })
        litellm_request["extra_headers"] = extra_headers
        
        # Apply timeout optimizations
        if "timeout" not in litellm_request:
            timeout = profile.get("timeout", 60)
            litellm_request["timeout"] = timeout
            metadata["claude_code_optimizations_applied"].append("timeout_optimization")
        
        # Add performance tracking
        metadata["claude_code_optimizations_applied"].append("final_optimizations")
        
        logger.info("Applied final Claude Code optimizations",
                   model=source.model,
                   optimizations=metadata["claude_code_optimizations_applied"],
                   timeout=litellm_request.get("timeout"))
    
    def _update_conversion_metrics(self, model: str, conversion_time: float, is_claude_code: bool) -> None:
        """Update conversion performance metrics."""
        self.conversion_metrics["total_conversions"] += 1
        
        if is_claude_code:
            self.conversion_metrics["claude_code_optimized"] += 1
        
        # Update model usage
        if model not in self.conversion_metrics["model_usage"]:
            self.conversion_metrics["model_usage"][model] = {
                "count": 0,
                "total_time": 0.0,
                "claude_code_count": 0
            }
        
        model_stats = self.conversion_metrics["model_usage"][model]
        model_stats["count"] += 1
        model_stats["total_time"] += conversion_time
        
        if is_claude_code:
            model_stats["claude_code_count"] += 1
        
        # Update average conversion time
        total_time = sum(
            stats["total_time"] for stats in self.conversion_metrics["model_usage"].values()
        )
        self.conversion_metrics["average_conversion_time"] = total_time / self.conversion_metrics["total_conversions"]
    
    async def convert_response_from_litellm(
        self, 
        litellm_response: Dict[str, Any], 
        original_request: MessagesRequest
    ) -> Dict[str, Any]:
        """Convert LiteLLM response back to Anthropic format with Claude Code enhancements."""
        
        try:
            # Use enhanced converter for response conversion
            anthropic_response = await self.claude_converter.litellm_to_anthropic_enhanced(
                litellm_response, original_request.model_dump()
            )
            
            # Extract and process thinking content if available
            thinking_data = self.reasoning_service.extract_claude_code_thinking(
                litellm_response, original_request.model
            )
            
            if thinking_data["has_reasoning"]:
                anthropic_response["thinking"] = thinking_data
                logger.debug("Added thinking content to response",
                           thinking_blocks=len(thinking_data.get("thinking_blocks", [])),
                           reasoning_tokens=thinking_data.get("reasoning_tokens", 0))
            
            # Add Claude Code specific response metadata
            anthropic_response["claude_code_enhanced"] = True
            anthropic_response["optimization_metadata"] = {
                "model_used": original_request.model,
                "optimization_applied": True,
                "response_timestamp": datetime.utcnow().isoformat()
            }
            
            return anthropic_response
            
        except Exception as e:
            logger.error("Failed to convert response with Claude Code enhancements",
                        error=str(e), model=original_request.model)
            
            # Fallback to basic conversion
            return await self.claude_converter.litellm_to_anthropic_enhanced(
                litellm_response, original_request.model_dump()
            )
    
    def get_conversion_metrics(self) -> Dict[str, Any]:
        """Get comprehensive conversion metrics."""
        metrics = self.conversion_metrics.copy()
        
        # Calculate derived metrics
        total = metrics["total_conversions"]
        if total > 0:
            metrics["claude_code_optimization_rate"] = metrics["claude_code_optimized"] / total
        else:
            metrics["claude_code_optimization_rate"] = 0.0
        
        # Add service metrics
        metrics["tool_service_stats"] = self.tool_service.get_claude_code_tool_stats()
        metrics["reasoning_service_stats"] = self.reasoning_service.get_reasoning_metrics()
        
        # Add configuration info
        metrics["supported_models"] = list(self.claude_converter.claude_code_models.keys())
        metrics["available_tools"] = list(self.tool_service.claude_code_tools.keys())
        
        return metrics
    
    def get_claude_code_readiness(self) -> Dict[str, Any]:
        """Get Claude Code readiness assessment."""
        
        # Test each service
        converter_ready = hasattr(self.claude_converter, 'claude_code_models')
        tool_service_ready = hasattr(self.tool_service, 'claude_code_tools')
        reasoning_service_ready = hasattr(self.reasoning_service, 'reasoning_profiles')
        
        # Get tool availability
        available_tools = self.tool_service.get_available_claude_code_tools()
        
        # Get model capabilities
        model_capabilities = {}
        for model in self.claude_converter.claude_code_models.keys():
            model_capabilities[model] = self.reasoning_service.get_model_reasoning_capabilities(model)
        
        return {
            "overall_ready": converter_ready and tool_service_ready and reasoning_service_ready,
            "services": {
                "enhanced_converter": converter_ready,
                "tool_service": tool_service_ready,
                "reasoning_service": reasoning_service_ready
            },
            "capabilities": {
                "supported_models": len(self.claude_converter.claude_code_models),
                "available_tools": len(available_tools),
                "reasoning_models": len(self.reasoning_service.reasoning_profiles)
            },
            "model_capabilities": model_capabilities,
            "available_tools": available_tools,
            "readiness_timestamp": datetime.utcnow().isoformat()
        } 