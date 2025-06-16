"""Flow for converting Anthropic format to LiteLLM format."""

from typing import Any, Dict, List, Optional

from ...services.base import ConversionService, InstructorService
from ...models.anthropic import MessagesRequest
from ...models.litellm import LiteLLMMessage, LiteLLMRequest
from ...models.instructor import ConversionResult
from ...tasks.conversion.model_mapping_tasks import (
    ensure_openrouter_prefix,
    map_model_name,
    update_request_with_model_mapping
)
from ...tasks.conversion.message_conversion_tasks import (
    extract_system_message_content,
    convert_anthropic_message_to_litellm,
    handle_tool_result_blocks,
    create_system_message
)
from ...tasks.conversion.tool_conversion_tasks import (
    convert_anthropic_tool_to_litellm,
    convert_anthropic_tool_choice_to_litellm
)
from ...tasks.conversion.prompt_caching_tasks import (
    generate_prompt_cache_key,
    get_cached_prompt_response,
    cache_prompt_response
)
from ...utils.config import config, OPENROUTER_API_BASE
from ...core.logging_config import get_logger

logger = get_logger("conversion.anthropic_to_litellm")


class AnthropicToLiteLLMFlow(ConversionService[MessagesRequest, LiteLLMRequest], InstructorService):
    """Flow for converting Anthropic format to LiteLLM format."""
    
    def __init__(self):
        """Initialize Anthropic to LiteLLM flow."""
        ConversionService.__init__(self, "AnthropicToLiteLLM")
        InstructorService.__init__(self, "AnthropicToLiteLLM")
    
    def convert(self, source: MessagesRequest, **kwargs) -> ConversionResult:
        """Convert Anthropic MessagesRequest to LiteLLM format."""
        try:
            # Initialize conversion metadata
            conversion_metadata = self._initialize_metadata(source)
            
            # Check for cached response first
            cache_result = self._check_prompt_cache(source, conversion_metadata)
            if cache_result and cache_result.success:
                logger.info("Returning cached prompt response",
                           cache_key=cache_result.metadata.get("cache_key", "unknown")[:16] + "...")
                return cache_result
            
            # Convert messages
            litellm_messages = self._convert_messages(source, conversion_metadata)
            
            # Convert tools
            litellm_tools = self._convert_tools(source, conversion_metadata)
            
            # Build LiteLLM request
            litellm_request_data = self._build_litellm_request(
                source, litellm_messages, litellm_tools, conversion_metadata
            )
            
            # Cache the successful conversion result
            self._cache_conversion_result(source, litellm_request_data, conversion_metadata)
            
            # Log success
            self.log_operation(
                "anthropic_to_litellm_conversion",
                True,
                **conversion_metadata
            )
            
            return self.create_conversion_result(
                success=True,
                converted_data=litellm_request_data,
                metadata=conversion_metadata
            )
            
        except Exception as e:
            logger.error("Anthropic to LiteLLM conversion failed",
                        error=str(e),
                        operation="anthropic_to_litellm_conversion",
                        exc_info=True)
            return self.create_conversion_result(
                success=False,
                errors=[f"Conversion failed: {str(e)}"],
                metadata={"error_type": type(e).__name__}
            )
    
    def _initialize_metadata(self, source: MessagesRequest) -> Dict[str, Any]:
        """Initialize conversion metadata."""
        return {
            "original_message_count": len(source.messages),
            "converted_message_count": 0,
            "tool_conversions": 0,
            "content_block_conversions": 0,
            "system_message_added": False
        }
    
    def _convert_messages(self, source: MessagesRequest, metadata: Dict[str, Any]) -> List[LiteLLMMessage]:
        """Convert all messages including system message."""
        litellm_messages = []
        
        # Handle system message first
        if source.system:
            system_content = extract_system_message_content(source.system)
            if system_content:
                system_msg = create_system_message(system_content)
                litellm_messages.append(system_msg)
                metadata["system_message_added"] = True
                logger.info("Added system message",
                           message_preview=system_content[:100] + ('...' if len(system_content) > 100 else ''))
        
        # Convert regular messages
        for msg in source.messages:
            # Check if message contains tool_result blocks
            if isinstance(msg.content, list) and any(
                hasattr(block, 'type') and block.type == "tool_result" 
                for block in msg.content
            ):
                # Handle tool_result blocks specially
                text_parts = handle_tool_result_blocks(msg)
                if text_parts:
                    text_content = " ".join(text_parts).strip()
                    if text_content:
                        litellm_messages.append(LiteLLMMessage(
                            role=msg.role,
                            content=text_content
                        ))
            else:
                # Regular message conversion
                converted_msg = convert_anthropic_message_to_litellm(msg, metadata)
                litellm_messages.append(converted_msg)
        
        metadata["converted_message_count"] = len(litellm_messages)
        return litellm_messages
    
    def _convert_tools(self, source: MessagesRequest, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert tools to LiteLLM format with OpenRouter compatibility and intelligent error handling."""
        if not source.tools:
            return None
        
        # Use intelligent error handling approach - send tools and let HTTP client handle parsing errors
        litellm_tools = []
        logger.debug("Processing tools for OpenRouter with intelligent error handling", tool_count=len(source.tools))
        
        # Use a reasonable subset of tools to avoid overwhelming OpenRouter
        limited_tools = source.tools[:5]  # Limit to 5 most essential tools
        
        for i, tool in enumerate(limited_tools):
            logger.debug("Converting tool with error handling support",
                        tool_index=i+1,
                        tool_name=tool.name,
                        description_preview=tool.description[:50] if tool.description else 'None')
            
            # Apply OpenRouter compatibility conversion
            converted_tool = self._convert_tool_for_openrouter(tool)
            if converted_tool:
                litellm_tools.append(converted_tool)
                metadata["tool_conversions"] += 1
                logger.debug("Tool converted successfully", tool_name=tool.name)
        
        logger.info("Tools prepared for OpenRouter with intelligent error handling", 
                   original_count=len(source.tools),
                   limited_count=len(limited_tools),
                   converted_count=len(litellm_tools))
        
        return litellm_tools if litellm_tools else None
    
    def _filter_essential_tools(self, tools: List) -> List:
        """Filter to most essential tools for OpenRouter compatibility."""
        # Priority order: most essential and simple tools first
        tool_priority = {
            'Write': 1,      # File creation
            'Read': 2,       # File reading  
            'WebFetch': 3,   # Web access
            'Edit': 4,       # File editing
            'Bash': 5,       # Commands
            'LS': 6,         # Directory listing
            'WebSearch': 7,  # Web search
        }
        
        # Filter to tools that exist in our priority list
        essential_tools = []
        for tool in tools:
            if tool.name in tool_priority:
                essential_tools.append((tool_priority[tool.name], tool))
        
        # Sort by priority and take only the top 2 most essential
        essential_tools.sort(key=lambda x: x[0])
        selected_tools = [tool for _, tool in essential_tools[:2]]
        
        logger.info("Filtered essential tools for OpenRouter",
                   available_tools=[t.name for t in tools],
                   selected_tools=[t.name for t in selected_tools])
        
        return selected_tools
    
    def _convert_tool_for_openrouter(self, tool) -> Dict[str, Any]:
        """Convert tool with standard OpenAI format (this works with OpenRouter!)"""
        try:
            from ...tasks.conversion.tool_conversion_tasks import conservative_clean_openrouter_schema
            
            # Process description for OpenRouter compatibility
            description = self._simplify_description(tool.description or "", max_length=200)
            
            # Use standard OpenAI format with nested function object - this works!
            converted_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": description,
                    "parameters": conservative_clean_openrouter_schema(tool.input_schema)
                }
            }
            
            logger.debug("Created OpenRouter-compatible tool",
                        tool_name=tool.name,
                        schema_properties=len(converted_tool["function"]["parameters"].get("properties", {})))
            
            return converted_tool
            
        except Exception as e:
            logger.warning("Failed to convert tool for OpenRouter",
                          tool_name=tool.name,
                          error=str(e))
            return None
    
    def _create_minimal_schema(self, tool) -> Dict[str, Any]:
        """Create minimal schema for maximum OpenRouter compatibility."""
        original_schema = tool.input_schema
        
        # Start with absolute minimal schema
        minimal_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Add only the most essential properties with simplified types
        if isinstance(original_schema, dict):
            original_props = original_schema.get("properties", {})
            original_required = original_schema.get("required", [])
            
            # Predefined minimal schemas for essential tools
            minimal_schemas = {
                'Write': {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "File path"},
                        "content": {"type": "string", "description": "File content"}
                    },
                    "required": ["file_path", "content"]
                },
                'Read': {
                    "type": "object", 
                    "properties": {
                        "file_path": {"type": "string", "description": "File path"}
                    },
                    "required": ["file_path"]
                },
                'WebFetch': {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to fetch"}
                    },
                    "required": ["url"]
                },
                'Edit': {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "File path"},
                        "old_str": {"type": "string", "description": "Text to replace"},
                        "new_str": {"type": "string", "description": "Replacement text"}
                    },
                    "required": ["file_path", "old_str", "new_str"]
                },
                'Bash': {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command"}
                    },
                    "required": ["command"]
                }
            }
            
            # Use predefined minimal schema if available
            if tool.name in minimal_schemas:
                return minimal_schemas[tool.name]
        
        # Fallback: create generic minimal schema
        return minimal_schema
    
    def _simplify_description(self, description: str, max_length: int = 200) -> str:
        """Simplify description for OpenRouter compatibility."""
        if not description:
            return ""
        
        # Clean and ensure proper punctuation
        description = description.strip()
        
        # Add period if description doesn't end with punctuation
        if description and not description[-1] in '.!?':
            description += '.'
        
        # Truncate if too long
        if len(description) > max_length:
            # Try to truncate at word boundary
            truncated = description[:max_length-3]
            last_space = truncated.rfind(' ')
            if last_space > max_length * 0.7:  # If we can find a reasonable word boundary
                description = truncated[:last_space] + '...'
            else:
                description = truncated + '...'
        
        return description
    
    def _build_litellm_request(
        self, 
        source: MessagesRequest, 
        litellm_messages: List[LiteLLMMessage],
        litellm_tools: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build the final LiteLLM request data."""
        # Map model using task module
        mapping_result = map_model_name(source.model)
        
        # Build base request
        litellm_request_data = {
            "model": mapping_result.mapped_model,
            "messages": [msg.model_dump() for msg in litellm_messages],
            "max_tokens": source.max_tokens,
            "temperature": source.temperature or 1.0,
            "stream": source.stream or False,
            "api_key": config.openrouter_api_key,
            "api_base": OPENROUTER_API_BASE,
            "extra_headers": {
                "HTTP-Referer": "https://github.com/openrouter-anthropic-server",
                "X-Title": "OpenRouter Anthropic Server"
            }
        }
        
        # Log request details
        logger.debug("Building LiteLLM request",
                    original_model=source.model,
                    mapped_model=mapping_result.mapped_model,
                    api_base=OPENROUTER_API_BASE)
        
        # Add optional parameters
        self._add_optional_parameters(source, litellm_request_data, litellm_tools)
        
        return litellm_request_data
    
    def _add_optional_parameters(
        self, 
        source: MessagesRequest, 
        request_data: Dict[str, Any],
        litellm_tools: List[Dict[str, Any]]
    ) -> None:
        """Add optional parameters to the request."""
        if source.top_p is not None:
            request_data["top_p"] = source.top_p
        if source.top_k is not None:
            request_data["top_k"] = source.top_k
        if source.stop_sequences:
            request_data["stop"] = source.stop_sequences
        if litellm_tools:
            request_data["tools"] = litellm_tools
            # Only add tool_choice if we have tools to send
            if source.tool_choice:
                request_data["tool_choice"] = convert_anthropic_tool_choice_to_litellm(source.tool_choice)
        
        # Add OpenRouter extensions if configured
        self._add_openrouter_extensions(request_data)
        
        # Add OpenAI advanced parameters if configured
        self._add_openai_advanced_parameters(request_data)
    
    def _add_openrouter_extensions(self, request_data: Dict[str, Any]) -> None:
        """Add OpenRouter-specific extensions when configured."""
        try:
            from ...tasks.conversion.openrouter_extensions import (
                add_openrouter_extensions,
                should_use_openrouter_extensions
            )
            
            # Check if OpenRouter extensions should be applied
            if should_use_openrouter_extensions():
                # Get configuration and apply extensions
                openrouter_config = config.get_openrouter_extensions_config()
                if openrouter_config:
                    # Apply extensions and update request_data in place
                    enhanced_request = add_openrouter_extensions(request_data, openrouter_config)
                    request_data.update(enhanced_request)
                    
                    logger.info("OpenRouter extensions applied to request",
                               extensions_count=len([k for k in enhanced_request.keys() 
                                                   if k not in request_data]),
                               model=request_data.get("model"))
        except ImportError as e:
            logger.warning("OpenRouter extensions module not available", error=str(e))
        except Exception as e:
            logger.error("Failed to apply OpenRouter extensions", 
                        error=str(e), 
                        exc_info=True)
    
    def _add_openai_advanced_parameters(self, request_data: Dict[str, Any]) -> None:
        """Add OpenAI advanced parameters when configured."""
        try:
            from ...tasks.conversion.openai_advanced_parameters import (
                add_openai_advanced_parameters,
                should_use_openai_advanced_parameters
            )
            
            # Check if OpenAI advanced parameters should be applied
            if should_use_openai_advanced_parameters(request_data):
                # Get configuration and apply parameters
                openai_config = config.get_openai_advanced_config()
                if openai_config:
                    # Apply parameters
                    result = add_openai_advanced_parameters(request_data, openai_config)
                    if result.success:
                        # Update request_data with enhanced data
                        request_data.update(result.data)
                        
                        logger.info("OpenAI advanced parameters applied to request",
                                   parameters_count=len(openai_config),
                                   model=request_data.get("model"))
                    else:
                        logger.warning("Failed to apply OpenAI advanced parameters",
                                     errors=result.errors)
        except ImportError as e:
            logger.warning("OpenAI advanced parameters module not available", error=str(e))
        except Exception as e:
            logger.error("Failed to apply OpenAI advanced parameters", 
                        error=str(e), 
                        exc_info=True)
    
    def _check_prompt_cache(self, source: MessagesRequest, metadata: Dict[str, Any]) -> Optional[ConversionResult]:
        """Check if there's a cached response for this prompt."""
        try:
            # Generate cache key from the source request
            source_dict = source.model_dump()
            cache_key = generate_prompt_cache_key(source_dict)
            
            # Check for cached response
            cached_result = get_cached_prompt_response(cache_key)
            
            if cached_result:
                # Update metadata with cache information
                metadata.update({
                    "cache_hit": True,
                    "cache_key": cache_key,
                    "cached_at": cached_result.metadata.get("cached_at")
                })
                
                logger.info("Cache hit for prompt conversion",
                           cache_key=cache_key[:16] + "...",
                           model=source.model)
                
                # Return the cached result with updated metadata
                return self.create_conversion_result(
                    success=True,
                    converted_data=cached_result.converted_data,
                    metadata={**metadata, **cached_result.metadata}
                )
            else:
                # Cache miss
                metadata.update({
                    "cache_hit": False,
                    "cache_key": cache_key
                })
                
                logger.debug("Cache miss for prompt conversion",
                            cache_key=cache_key[:16] + "...",
                            model=source.model)
                
                return None
                
        except Exception as e:
            logger.error("Error checking prompt cache", error=str(e))
            metadata["cache_error"] = str(e)
            return None
    
    def _cache_conversion_result(
        self, 
        source: MessagesRequest, 
        litellm_request_data: Dict[str, Any], 
        metadata: Dict[str, Any]
    ) -> None:
        """Cache the successful conversion result."""
        try:
            # Only cache if we have a cache key from the earlier check
            cache_key = metadata.get("cache_key")
            if not cache_key:
                return
            
            # Cache the conversion result
            cache_result = cache_prompt_response(cache_key, litellm_request_data)
            
            if cache_result.success:
                metadata["cached"] = True
                logger.info("Cached conversion result",
                           cache_key=cache_key[:16] + "...",
                           model=source.model)
            else:
                metadata["cached"] = False
                metadata["cache_errors"] = cache_result.errors
                logger.warning("Failed to cache conversion result",
                              cache_key=cache_key[:16] + "...",
                              errors=cache_result.errors)
                
        except Exception as e:
            logger.error("Error caching conversion result", error=str(e))
            metadata["cache_error"] = str(e)