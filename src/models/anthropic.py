"""Anthropic API models."""

import uuid
import json
from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator
from .base import BaseOpenRouterModel, Usage, Tool, ThinkingConfig

class ContentBlockText(BaseModel):
    """Text content block."""
    type: Literal["text"]
    text: str

class ContentBlockImage(BaseModel):
    """Image content block."""
    type: Literal["image"]
    source: Dict[str, Any]

class ContentBlockToolUse(BaseModel):
    """Tool use content block."""
    type: Literal["tool_use"]
    id: Optional[str] = None
    name: Optional[str] = ""
    input: Dict[str, Any] = {}

class ContentBlockToolResult(BaseModel):
    """Tool result content block."""
    type: Literal["tool_result"]
    tool_use_id: Optional[str] = None
    content: Union[str, List[Dict[str, Any]], Dict[str, Any], List[Any], Any]

class SystemContent(BaseModel):
    """System message content."""
    type: Literal["text"]
    text: str

class Message(BaseOpenRouterModel):
    """Anthropic message model with enhanced validation."""
    
    role: Literal["user", "assistant"]
    content: Union[str, List[Union[ContentBlockText, ContentBlockImage, ContentBlockToolUse, ContentBlockToolResult]]]
    
    @field_validator('content', mode='before')
    def validate_content(cls, v):
        """Enhanced content validation with tool consolidation."""
        if isinstance(v, list):
            valid_blocks = []
            tool_consolidation_buffer = {}
            
            for block in v:
                if isinstance(block, dict):
                    block_type = block.get('type')
                    
                    if block_type == 'tool_use':
                        # Handle tool_use consolidation
                        tool_id = block.get('id')
                        if not tool_id:
                            tool_id = f"tool_{uuid.uuid4()}"
                            block['id'] = tool_id
                        
                        if tool_id not in tool_consolidation_buffer:
                            tool_consolidation_buffer[tool_id] = {
                                'type': 'tool_use',
                                'id': tool_id,
                                'name': block.get('name', ''),
                                'input': block.get('input', {}),
                                '_raw_input_parts': []
                            }
                        
                        # Consolidate input parts
                        if 'input' in block and block['input']:
                            if isinstance(block['input'], dict):
                                tool_consolidation_buffer[tool_id]['input'].update(block['input'])
                            elif isinstance(block['input'], str):
                                tool_consolidation_buffer[tool_id]['_raw_input_parts'].append(block['input'])
                    
                    elif block_type == 'tool_result':
                        # Ensure tool_result has required fields
                        if 'tool_use_id' not in block or block['tool_use_id'] is None:
                            block['tool_use_id'] = f"tool_{uuid.uuid4()}"
                        if 'content' not in block:
                            block['content'] = ""
                        valid_blocks.append(block)
                    
                    else:
                        valid_blocks.append(block)
                else:
                    valid_blocks.append(block)
            
            # Finalize consolidated tools
            for tool_id, tool_data in tool_consolidation_buffer.items():
                if tool_data['_raw_input_parts']:
                    # Attempt to parse consolidated input
                    full_input_str = "".join(tool_data['_raw_input_parts'])
                    try:
                        parsed_input = json.loads(full_input_str)
                        tool_data['input'] = parsed_input
                    except json.JSONDecodeError:
                        # Keep as raw string if parsing fails
                        tool_data['input'] = {"raw_input": full_input_str}
                
                # Remove internal tracking field
                del tool_data['_raw_input_parts']
                valid_blocks.append(tool_data)
            
            return valid_blocks
        return v

class MessagesRequest(BaseOpenRouterModel):
    """Anthropic messages request."""
    
    model: str
    max_tokens: int
    messages: List[Message]
    system: Optional[Union[str, List[SystemContent]]] = None
    stop_sequences: Optional[List[str]] = None
    stream: Optional[bool] = False
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    tools: Optional[List[Tool]] = None
    tool_choice: Optional[Dict[str, Any]] = None
    thinking: Optional[ThinkingConfig] = None
    original_model: Optional[str] = None
    
    def __init__(self, **data):
        """
        Custom initialization to handle model mapping and store original model.
        
        This approach is more similar to the openrouter_anthropic_server.py
        implementation and allows us to properly store the original model.
        """
        # Store the original model before any processing
        original_model = data.get('model')
        
        if original_model is not None and not data.get('original_model'):
            from ..utils.config import config
            from ..services.conversion import ensure_openrouter_prefix
            
            # Get comprehensive model mapping from configuration
            model_mapping = config.get_model_mapping()
            mapped_model = model_mapping.get(original_model, config.big_model)
            
            # Ensure openrouter/ prefix for LiteLLM routing
            final_model = ensure_openrouter_prefix(mapped_model)
            
            # Update the data with mapped model and store original
            data['model'] = final_model
            data['original_model'] = original_model
        
        # Call parent constructor
        super().__init__(**data)

class MessagesResponse(BaseOpenRouterModel):
    """Anthropic messages response."""
    
    id: str
    model: str
    role: Literal["assistant"] = "assistant"
    content: List[Union[ContentBlockText, ContentBlockToolUse]]
    type: Literal["message"] = "message"
    stop_reason: Optional[Literal["end_turn", "max_tokens", "stop_sequence", "tool_use", "error"]] = None
    stop_sequence: Optional[str] = None
    usage: Usage

class TokenCountRequest(BaseOpenRouterModel):
    """Token count request."""
    
    model: str
    messages: List[Message]
    system: Optional[Union[str, List[SystemContent]]] = None
    tools: Optional[List[Tool]] = None
    thinking: Optional[ThinkingConfig] = None
    tool_choice: Optional[Dict[str, Any]] = None
    original_model: Optional[str] = None

class TokenCountResponse(BaseOpenRouterModel):
    """Token count response."""
    
    input_tokens: int