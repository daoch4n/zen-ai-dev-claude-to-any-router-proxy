#!/usr/bin/env python3
"""
OpenRouter to Anthropic API Server
Uses LiteLLM to handle OpenRouter API calls and converts responses to Anthropic format.
Based on the Gemini proxy pattern but adapted for OpenRouter.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
import logging
import json
import os
import uuid
import time
import litellm
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union, Literal
from dotenv import load_dotenv
import sys

# Configure LiteLLM
litellm.set_verbose = False

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Configure uvicorn to be quieter
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

# Create a filter to block LiteLLM noise
class MessageFilter(logging.Filter):
    def filter(self, record):
        blocked_phrases = [
            "LiteLLM completion()",
            "HTTP Request:",
            "selected model name for cost calculation",
            "utils.py",
            "cost_calculator"
        ]
        
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            for phrase in blocked_phrases:
                if phrase in record.msg:
                    return False
        return True

# Apply the filter to the root logger
root_logger = logging.getLogger()
root_logger.addFilter(MessageFilter())

# Custom formatter for model mapping logs
class ColorizedFormatter(logging.Formatter):
    """Custom formatter to highlight model mappings"""
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, record):
        if record.levelno == logging.DEBUG and "MODEL MAPPING" in record.msg:
            # Apply colors and formatting to model mapping logs
            return f"{self.BOLD}{self.GREEN}{record.msg}{self.RESET}"
        return super().format(record)

# Apply custom formatter to console handler
for handler in logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setFormatter(ColorizedFormatter('%(asctime)s - %(levelname)s - %(message)s'))

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log HTTP requests"""
    method = request.method
    path = request.url.path
    logger.debug(f"Request: {method} {path}")
    response = await call_next(request)
    return response

# Get API keys from environment
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    logger.error("🔴 OPENROUTER_API_KEY not found in environment variables. Please set it.")

# OpenRouter model configuration
DEFAULT_BIG_MODEL = "anthropic/claude-sonnet-4"
DEFAULT_SMALL_MODEL = "anthropic/claude-3.7-sonnet"
BIG_MODEL = os.environ.get("ANTHROPIC_MODEL", DEFAULT_BIG_MODEL)
SMALL_MODEL = os.environ.get("ANTHROPIC_SMALL_FAST_MODEL", DEFAULT_SMALL_MODEL)

# Anthropic API Models (Pydantic) - Complete structure like Gemini server
class ContentBlockText(BaseModel):
    type: Literal["text"]
    text: str

class ContentBlockImage(BaseModel):
    type: Literal["image"]
    source: Dict[str, Any]

class ContentBlockToolUse(BaseModel):
    type: Literal["tool_use"]
    id: Optional[str] = None  # Can be null during streaming
    name: Optional[str] = ""  # Can be empty during streaming
    input: Dict[str, Any] = {}  # Can be empty initially

class ContentBlockToolResult(BaseModel):
    type: Literal["tool_result"]
    tool_use_id: Optional[str] = None  # Can be null in some cases
    content: Union[str, List[Dict[str, Any]], Dict[str, Any], List[Any], Any]

class SystemContent(BaseModel):
    type: Literal["text"]
    text: str

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: Union[str, List[Union[ContentBlockText, ContentBlockImage, ContentBlockToolUse, ContentBlockToolResult]]]
    
    @field_validator('content', mode='before')
    def validate_content(cls, v):
        # Handle edge cases where content might be malformed
        if isinstance(v, list):
            # Filter out any invalid content blocks
            valid_blocks = []
            for block in v:
                if isinstance(block, dict):
                    block_type = block.get('type')
                    if block_type == 'tool_use':
                        # Ensure tool_use blocks have required fields with defaults
                        if 'id' not in block or block['id'] is None:
                            block['id'] = f"tool_{uuid.uuid4()}"
                        if 'name' not in block or not block['name']:
                            block['name'] = "unknown_tool"
                        if 'input' not in block:
                            block['input'] = {}
                    elif block_type == 'tool_result':
                        # Ensure tool_result blocks have required fields
                        if 'tool_use_id' not in block or block['tool_use_id'] is None:
                            block['tool_use_id'] = f"tool_{uuid.uuid4()}"
                        if 'content' not in block:
                            block['content'] = ""
                    valid_blocks.append(block)
                else:
                    valid_blocks.append(block)
            return valid_blocks
        return v

class Tool(BaseModel):
    name: str
    description: Optional[str] = None
    input_schema: Dict[str, Any]

class ThinkingConfig(BaseModel):
    enabled: bool = True

class MessagesRequest(BaseModel):
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

    @field_validator('model')
    def validate_model_field(cls, v, info):
        original_model = v
        
        # Model mapping for Claude Code compatibility
        model_mapping = {
            'claude-sonnet-4-20250514': BIG_MODEL,
            'claude-opus-4-20250514': BIG_MODEL,
            'claude-3-7-sonnet-20250219': SMALL_MODEL,
            'claude-sonnet-4': BIG_MODEL,
            'claude-3.7-sonnet': SMALL_MODEL,
            'claude-3-5-sonnet': SMALL_MODEL,
            'claude-3-sonnet': SMALL_MODEL,
        }
        
        new_model = model_mapping.get(v, BIG_MODEL)
        
        # Ensure openrouter/ prefix for LiteLLM
        if not new_model.startswith('openrouter/'):
            new_model = f"openrouter/{new_model}"
        
        logger.info(f"🔄 Model mapping: {v} -> {new_model}")
        
        # Store original model
        values = info.data
        if isinstance(values, dict):
            values['original_model'] = original_model
        
        return new_model

class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0

class MessagesResponse(BaseModel):
    id: str
    model: str
    role: Literal["assistant"] = "assistant"
    content: List[Union[ContentBlockText, ContentBlockToolUse]]
    type: Literal["message"] = "message"
    stop_reason: Optional[Literal["end_turn", "max_tokens", "stop_sequence", "tool_use", "error"]] = None
    stop_sequence: Optional[str] = None
    usage: Usage

def parse_tool_result_content(content):
    """Helper function to properly parse and normalize tool result content."""
    if content is None:
        return "No content provided"

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        result = ""
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                result += item.get("text", "") + "\n"
            elif isinstance(item, str):
                result += item + "\n"
            elif isinstance(item, dict):
                if "text" in item:
                    result += item.get("text", "") + "\n"
                else:
                    try:
                        result += json.dumps(item) + "\n"
                    except:
                        result += str(item) + "\n"
            else:
                try:
                    result += str(item) + "\n"
                except:
                    result += "Unparseable content\n"
        return result.strip()

    if isinstance(content, dict):
        if content.get("type") == "text":
            return content.get("text", "")
        try:
            return json.dumps(content)
        except:
            return str(content)

    try:
        return str(content)
    except:
        return "Unparseable content"

def clean_openrouter_schema(schema: Any) -> Any:
    """Recursively removes unsupported fields from a JSON schema for OpenRouter."""
    if isinstance(schema, dict):
        # Remove specific keys that might be unsupported by OpenRouter
        schema.pop("additionalProperties", None)
        schema.pop("default", None)

        # Check for unsupported 'format' in string types
        if schema.get("type") == "string" and "format" in schema:
            allowed_formats = {"enum", "date-time"}  # Safe subset
            if schema["format"] not in allowed_formats:
                logger.debug(f"Removing unsupported format '{schema['format']}' for string type in OpenRouter schema.")
                schema.pop("format")

        # Recursively clean nested schemas
        for key, value in list(schema.items()):
            schema[key] = clean_openrouter_schema(value)
    elif isinstance(schema, list):
        # Recursively clean items in a list
        return [clean_openrouter_schema(item) for item in schema]
    return schema

def is_valid_json(json_str):
    """Helper function to validate JSON strings."""
    if not isinstance(json_str, str):
        return False
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False

def convert_anthropic_to_litellm(anthropic_request: MessagesRequest) -> Dict[str, Any]:
    """Convert Anthropic request to LiteLLM format - based on Gemini server"""
    
    litellm_messages = []

    # Handle system message
    if anthropic_request.system:
        system_content_str = ""
        if isinstance(anthropic_request.system, str):
            system_content_str = anthropic_request.system
        elif isinstance(anthropic_request.system, list):
            for block in anthropic_request.system:
                if hasattr(block, 'type') and block.type == "text":
                    system_content_str += block.text + "\n\n"
                elif isinstance(block, dict) and block.get("type") == "text":
                    system_content_str += block.get("text", "") + "\n\n"
        if system_content_str.strip():
            litellm_messages.append({"role": "system", "content": system_content_str.strip()})

    # Convert messages - full implementation like Gemini server
    for anthropic_msg in anthropic_request.messages:
        if isinstance(anthropic_msg.content, str):
            litellm_messages.append({"role": anthropic_msg.role, "content": anthropic_msg.content})
            continue

        # Handle complex content blocks
        current_msg_text_parts = []
        current_msg_image_parts = []
        current_msg_assistant_tool_calls = []
        pending_tool_role_messages = []

        for block in anthropic_msg.content:
            if block.type == "text":
                current_msg_text_parts.append(block.text)
            elif block.type == "image":
                if isinstance(block.source, dict) and \
                   block.source.get("type") == "base64" and \
                   "media_type" in block.source and "data" in block.source:
                    current_msg_image_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{block.source['media_type']};base64,{block.source['data']}"
                        }
                    })
                else:
                    logger.warning(f"Unsupported image block source format: {block.source}")
            elif block.type == "tool_use":
                if anthropic_msg.role == "assistant":
                    current_msg_assistant_tool_calls.append({
                        "id": block.id,
                        "type": "function",
                        "function": {
                            "name": block.name,
                            "arguments": json.dumps(block.input)
                        }
                    })
                else:
                    logger.error(f"CRITICAL: tool_use block found in non-assistant message: {anthropic_msg.role}")
            elif block.type == "tool_result":
                if anthropic_msg.role == "user":
                    if current_msg_text_parts or current_msg_image_parts:
                        user_content_for_litellm = []
                        if current_msg_text_parts:
                            user_content_for_litellm.append({"type": "text", "text": "".join(current_msg_text_parts).strip()})
                        user_content_for_litellm.extend(current_msg_image_parts)
                        
                        if user_content_for_litellm:
                           litellm_messages.append({
                               "role": "user",
                               "content": user_content_for_litellm[0]["text"] if len(user_content_for_litellm) == 1 and user_content_for_litellm[0]["type"] == "text" else user_content_for_litellm
                           })
                        current_msg_text_parts = []
                        current_msg_image_parts = []

                    parsed_tool_content = parse_tool_result_content(block.content)
                    pending_tool_role_messages.append({
                        "role": "tool",
                        "tool_call_id": block.tool_use_id,
                        "content": parsed_tool_content
                    })
                else:
                    logger.error(f"CRITICAL: tool_result block found in non-user message: {anthropic_msg.role}")

        # Build final message
        final_text_str = "".join(current_msg_text_parts).strip()

        if anthropic_msg.role == "user":
            if final_text_str or current_msg_image_parts:
                user_content_for_litellm = []
                if final_text_str:
                    user_content_for_litellm.append({"type": "text", "text": final_text_str})
                user_content_for_litellm.extend(current_msg_image_parts)

                if user_content_for_litellm:
                    litellm_messages.append({
                        "role": "user",
                        "content": user_content_for_litellm[0]["text"] if len(user_content_for_litellm) == 1 and user_content_for_litellm[0]["type"] == "text" else user_content_for_litellm
                    })
            litellm_messages.extend(pending_tool_role_messages)

        elif anthropic_msg.role == "assistant":
            assistant_litellm_msg = {"role": "assistant"}
            
            assistant_content_actual = []
            if final_text_str:
                assistant_content_actual.append({"type": "text", "text": final_text_str})
            assistant_content_actual.extend(current_msg_image_parts)

            if assistant_content_actual:
                 assistant_litellm_msg["content"] = assistant_content_actual[0]["text"] if len(assistant_content_actual) == 1 and assistant_content_actual[0]["type"] == "text" else assistant_content_actual
            else:
                assistant_litellm_msg["content"] = None

            if current_msg_assistant_tool_calls:
                assistant_litellm_msg["tool_calls"] = current_msg_assistant_tool_calls
            
            if assistant_litellm_msg.get("content") or assistant_litellm_msg.get("tool_calls"):
                litellm_messages.append(assistant_litellm_msg)
    
    # Build LiteLLM request
    litellm_request_dict = {
        "model": anthropic_request.model,
        "messages": litellm_messages,
        "max_tokens": min(anthropic_request.max_tokens, 8192),
        "temperature": anthropic_request.temperature,
        "stream": anthropic_request.stream,
    }

    if anthropic_request.stop_sequences:
        litellm_request_dict["stop"] = anthropic_request.stop_sequences
    if anthropic_request.top_p is not None:
        litellm_request_dict["top_p"] = anthropic_request.top_p
    if anthropic_request.top_k is not None:
        litellm_request_dict["top_k"] = anthropic_request.top_k

    # Convert tools
    if anthropic_request.tools:
        openrouter_tools = []
        for tool_obj in anthropic_request.tools:
            tool_dict = tool_obj.dict()
            input_schema = tool_dict.get("input_schema", {})
            cleaned_schema = clean_openrouter_schema(input_schema)  # Re-enable conservative schema cleaning
            openrouter_tools.append({
                "type": "function",
                "function": {
                    "name": tool_dict["name"],
                    "description": tool_dict.get("description", ""),
                    "parameters": cleaned_schema
                }
            })
        litellm_request_dict["tools"] = openrouter_tools
        

    if anthropic_request.tool_choice:
        tool_choice_dict = anthropic_request.tool_choice
        choice_type = tool_choice_dict.get("type")
        if choice_type == "auto":
            litellm_request_dict["tool_choice"] = "auto"
        elif choice_type == "any":
            litellm_request_dict["tool_choice"] = "auto"
        elif choice_type == "tool" and "name" in tool_choice_dict:
            litellm_request_dict["tool_choice"] = {"type": "function", "function": {"name": tool_choice_dict["name"]}}
        else:
            litellm_request_dict["tool_choice"] = "auto"
        
    return litellm_request_dict

def convert_litellm_to_anthropic(litellm_response: Union[Dict[str, Any], Any],
                                 original_request: MessagesRequest) -> MessagesResponse:
    """Convert LiteLLM (OpenRouter) response to Anthropic API response format - based on Gemini server"""
    try:
        response_id = f"msg_{uuid.uuid4()}"
        content_text = ""
        tool_calls = None
        finish_reason = "end_turn"
        prompt_tokens = 0
        completion_tokens = 0

        # Handle ModelResponse object from LiteLLM
        if hasattr(litellm_response, 'choices') and hasattr(litellm_response, 'usage'):
            choices = litellm_response.choices
            message = choices[0].message if choices and len(choices) > 0 else None
            content_text = message.content if message and hasattr(message, 'content') else ""
            tool_calls = message.tool_calls if message and hasattr(message, 'tool_calls') else None
            finish_reason = choices[0].finish_reason if choices and len(choices) > 0 else "stop"
            usage_info = litellm_response.usage
            prompt_tokens = getattr(usage_info, "prompt_tokens", 0)
            completion_tokens = getattr(usage_info, "completion_tokens", 0)
            response_id = getattr(litellm_response, 'id', response_id)
        elif isinstance(litellm_response, dict):
            choices = litellm_response.get("choices", [{}])
            message = choices[0].get("message", {}) if choices and len(choices) > 0 else {}
            content_text = message.get("content", "")
            tool_calls = message.get("tool_calls", None)
            finish_reason = choices[0].get("finish_reason", "stop") if choices and len(choices) > 0 else "stop"
            usage_info = litellm_response.get("usage", {})
            prompt_tokens = usage_info.get("prompt_tokens", 0)
            completion_tokens = usage_info.get("completion_tokens", 0)
            response_id = litellm_response.get("id", response_id)
        else:
             logger.error(f"Unexpected LiteLLM response type: {type(litellm_response)}")
             if hasattr(litellm_response, '__dict__'):
                 response_dict = litellm_response.__dict__
                 choices = response_dict.get("choices", [{}])
                 message = choices[0].get("message", {}) if choices and len(choices) > 0 else {}
                 content_text = message.get("content", "")
                 tool_calls = message.get("tool_calls", None)
             else:
                raise ValueError("LiteLLM response is not a recognized object or dictionary.")

        # Build content blocks
        content_blocks = []
        if content_text is not None and content_text.strip() != "":
            content_blocks.append(ContentBlockText(type="text", text=content_text))

        if tool_calls:
            logger.debug(f"Processing tool calls from LiteLLM (OpenRouter): {tool_calls}")
            if not isinstance(tool_calls, list):
                tool_calls = [tool_calls]

            for tc_idx, tool_call_item in enumerate(tool_calls):
                tool_id = ""
                name = ""
                arguments_str = "{}"

                if isinstance(tool_call_item, dict):
                    tool_id = tool_call_item.get("id", f"tool_{uuid.uuid4()}")
                    function_data = tool_call_item.get("function", {})
                    name = function_data.get("name", "")
                    arguments_str = function_data.get("arguments", "{}")
                elif hasattr(tool_call_item, "id") and hasattr(tool_call_item, "function"):
                    tool_id = tool_call_item.id
                    name = tool_call_item.function.name
                    arguments_str = tool_call_item.function.arguments
                else:
                    logger.warning(f"Skipping malformed tool_call_item: {tool_call_item}")
                    continue

                try:
                    arguments_dict = json.loads(arguments_str)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse tool arguments as JSON: {arguments_str}")
                    arguments_dict = {"raw_arguments": arguments_str}

                content_blocks.append(ContentBlockToolUse(
                    type="tool_use",
                    id=tool_id,
                    name=name,
                    input=arguments_dict
                ))

        # Map finish reason to stop reason
        anthropic_stop_reason: Any = "end_turn"
        if finish_reason == "stop":
            anthropic_stop_reason = "end_turn"
        elif finish_reason == "length":
            anthropic_stop_reason = "max_tokens"
        elif finish_reason == "tool_calls":
            anthropic_stop_reason = "tool_use"
        elif finish_reason is None and tool_calls:
             anthropic_stop_reason = "tool_use"
        elif finish_reason:
             anthropic_stop_reason = finish_reason

        if not content_blocks:
            content_blocks.append(ContentBlockText(type="text", text=""))

        anthropic_response = MessagesResponse(
            id=response_id,
            model=original_request.original_model or original_request.model,
            role="assistant",
            content=content_blocks,
            stop_reason=anthropic_stop_reason,
            stop_sequence=None,
            usage=Usage(
                input_tokens=prompt_tokens,
                output_tokens=completion_tokens
            )
        )
        return anthropic_response

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        error_message = f"Error converting LiteLLM (OpenRouter) response to Anthropic: {str(e)}\n\nFull traceback:\n{error_traceback}"
        logger.error(error_message)
        return MessagesResponse(
            id=f"msg_error_{uuid.uuid4()}",
            model=original_request.original_model or original_request.model,
            role="assistant",
            content=[ContentBlockText(type="text", text=f"Error converting response: {str(e)}.")],
            stop_reason="error",
            usage=Usage(input_tokens=0, output_tokens=0)
        )

@app.post("/v1/messages")
async def create_message(
    request: MessagesRequest,
    raw_request: Request
):
    try:
        logger.debug(f"📊 PROCESSING REQUEST: Original Model='{request.original_model}', Effective Model='{request.model}', Stream={request.stream}")

        litellm_request = convert_anthropic_to_litellm(request)
        litellm_request["api_key"] = OPENROUTER_API_KEY
        
        # Debug: Log the exact request being sent to OpenRouter
        if request.tools:
            logger.info(f"🔧 Sending {len(request.tools)} tools to OpenRouter")
            logger.debug(f"🔧 Tools payload: {json.dumps(litellm_request.get('tools', []), indent=2)}")
        logger.debug(f"🔧 Full LiteLLM request: {json.dumps({k: v for k, v in litellm_request.items() if k != 'api_key'}, indent=2)}")
        
        # Add OpenRouter specific headers
        litellm_request["extra_headers"] = {
            "HTTP-Referer": "http://localhost:5001",
            "X-Title": "OpenRouter-Anthropic-Proxy"
        }

        logger.debug(f"Using OpenRouter API key for model: {request.model}")

        num_tools = len(request.tools) if request.tools else 0
        log_request_beautifully(
            "POST",
            raw_request.url.path,
            request.original_model or request.model,
            litellm_request.get('model'),
            len(litellm_request['messages']),
            num_tools,
            200
        )

        if request.stream:
            response_generator = await litellm.acompletion(**litellm_request)
            return StreamingResponse(
                handle_streaming(response_generator, request),
                media_type="text/event-stream"
            )
        else:
            start_time = time.time()
            litellm_response_obj = await litellm.acompletion(**litellm_request)
            logger.debug(f"✅ RESPONSE RECEIVED: Model={litellm_request.get('model')}, Time={time.time() - start_time:.2f}s")

            anthropic_response = convert_litellm_to_anthropic(litellm_response_obj, request)
            return anthropic_response

    except litellm.exceptions.APIError as e:
        logger.error(f"🚨 LiteLLM APIError: Status Code: {e.status_code}, Message: {e.message}, LLM Provider: {e.llm_provider}, Model: {e.model}")
        logger.error(f"🔍 Full error details: {str(e)}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            logger.error(f"🔍 OpenRouter response text: {e.response.text}")
            try:
                response_json = json.loads(e.response.text)
                logger.error(f"🔍 OpenRouter response JSON: {json.dumps(response_json, indent=2)}")
            except:
                logger.error(f"🔍 Could not parse OpenRouter response as JSON")
        import traceback
        logger.error(traceback.format_exc())
        
        error_detail_msg = str(e.message)
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
             try:
                response_json = json.loads(e.response.text)
                if 'error' in response_json and 'message' in response_json['error']:
                    error_detail_msg = response_json['error']['message']
             except:
                error_detail_msg = e.response.text[:500]

        raise HTTPException(status_code=e.status_code or 500, detail=f"LLM Provider Error ({e.llm_provider} - {e.model}): {error_detail_msg}")

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        error_details = {
            "error": str(e), "type": type(e).__name__, "traceback": error_traceback
        }
        # Create serializable error details
        serializable_details = {}
        for key, value in error_details.items():
            try:
                json.dumps({key: value})
                serializable_details[key] = value
            except TypeError:
                serializable_details[key] = f"<{type(value).__name__}>: {str(value)}"
        logger.error(f"Error processing request: {json.dumps(serializable_details, indent=2)}")

        status_code = getattr(e, 'status_code', 500)
        raise HTTPException(status_code=status_code, detail=f"Internal Server Error: {str(e)}")

class TokenCountRequest(BaseModel):
    model: str
    messages: List[Message]
    system: Optional[Union[str, List[SystemContent]]] = None
    tools: Optional[List[Tool]] = None
    thinking: Optional[ThinkingConfig] = None
    tool_choice: Optional[Dict[str, Any]] = None
    original_model: Optional[str] = None

    @field_validator('model')
    def validate_model_token_count(cls, v, info):
        # Reuse the same validation logic from MessagesRequest
        original_model = v
        
        # Model mapping for Claude Code compatibility
        model_mapping = {
            'claude-sonnet-4-20250514': BIG_MODEL,
            'claude-opus-4-20250514': BIG_MODEL,
            'claude-3-7-sonnet-20250219': SMALL_MODEL,
            'claude-sonnet-4': BIG_MODEL,
            'claude-3.7-sonnet': SMALL_MODEL,
            'claude-3-5-sonnet': SMALL_MODEL,
            'claude-3-sonnet': SMALL_MODEL,
        }
        
        new_model = model_mapping.get(v, BIG_MODEL)
        
        # Ensure openrouter/ prefix for LiteLLM
        if not new_model.startswith('openrouter/'):
            new_model = f"openrouter/{new_model}"
        
        # Store original model
        values = info.data
        if isinstance(values, dict):
            values['original_model'] = original_model
        
        return new_model

class TokenCountResponse(BaseModel):
    input_tokens: int

@app.post("/v1/messages/count_tokens")
async def count_tokens(
    request: TokenCountRequest,
    raw_request: Request
):
    try:
        # Convert the messages to a format LiteLLM can understand for token counting
        temp_messages_request = MessagesRequest(
            model=request.model,
            max_tokens=1,
            messages=request.messages,
            system=request.system,
            tools=request.tools,
        )
        litellm_formatted_parts = convert_anthropic_to_litellm(temp_messages_request)

        num_tools = len(request.tools) if request.tools else 0
        log_request_beautifully(
            "POST", raw_request.url.path,
            request.original_model or request.model,
            litellm_formatted_parts.get('model'),
            len(litellm_formatted_parts['messages']), num_tools, 200
        )

        token_count = litellm.token_counter(
            model=litellm_formatted_parts["model"],
            messages=litellm_formatted_parts["messages"],
        )
        return TokenCountResponse(input_tokens=token_count)

    except Exception as e:
        import traceback
        logger.error(f"Error counting tokens: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error counting tokens: {str(e)}")

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "OpenRouter-Anthropic-Proxy"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "OpenRouter to Anthropic Proxy", "version": "1.0.0"}

async def handle_streaming(response_generator, original_request: MessagesRequest):
    """Handle streaming responses from LiteLLM (OpenRouter) and convert to Anthropic SSE format."""
    message_id = f"msg_{uuid.uuid4().hex[:24]}"
    
    # Send message_start
    yield f"event: message_start\ndata: {json.dumps({'type': 'message_start', 'message': {'id': message_id, 'type': 'message', 'role': 'assistant', 'model': original_request.original_model or original_request.model, 'content': [], 'stop_reason': None, 'stop_sequence': None, 'usage': {'input_tokens': 0, 'output_tokens': 0}}})}\n\n"

    # Start text block
    yield f"event: content_block_start\ndata: {json.dumps({'type': 'content_block_start', 'index': 0, 'content_block': {'type': 'text', 'text': ''}})}\n\n"
    yield f"event: ping\ndata: {json.dumps({'type': 'ping'})}\n\n"

    accumulated_text = ""
    text_block_index = 0
    tool_block_index_counter = 0  # For assigning new indices to tool blocks
    current_tool_calls_data = {}  # {tool_call_id: {"index": X, "name": Y, "args_buffer": Z}}
    input_tokens = 0
    output_tokens = 0
    final_stop_reason = "end_turn"

    async for chunk in response_generator:
        try:
            if isinstance(chunk, str):
                logger.warning(f"Received string chunk: {chunk}")
                if chunk.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(chunk)
                except json.JSONDecodeError:
                    logger.error(f"Could not parse string chunk as JSON: {chunk}")
                    continue

            delta_content_text = None
            delta_tool_calls = None
            chunk_finish_reason = None

            if hasattr(chunk, 'choices') and chunk.choices:
                choice = chunk.choices[0]
                if hasattr(choice, 'delta') and choice.delta:
                    delta = choice.delta
                    delta_content_text = delta.content
                    if hasattr(delta, 'tool_calls') and delta.tool_calls:
                        delta_tool_calls = delta.tool_calls
                chunk_finish_reason = choice.finish_reason

            if hasattr(chunk, 'usage') and chunk.usage:
                input_tokens = chunk.usage.prompt_tokens
                output_tokens = chunk.usage.completion_tokens
                logger.debug(f"Received usage in chunk: Input={input_tokens}, Output={output_tokens}")

            # Handle text delta
            if delta_content_text:
                accumulated_text += delta_content_text
                yield f"event: content_block_delta\ndata: {json.dumps({'type': 'content_block_delta', 'index': text_block_index, 'delta': {'type': 'text_delta', 'text': delta_content_text}})}\n\n"

            # Handle tool call deltas
            if delta_tool_calls:
                if not accumulated_text and text_block_index == 0:
                    # First content is a tool, text block was started but no text came
                    pass

                for tc_chunk in delta_tool_calls:
                    tool_call_id = tc_chunk.id
                    tool_index_in_chunk_list = tc_chunk.index

                    if tool_call_id not in current_tool_calls_data:
                        # New tool call started
                        tool_block_index_counter += 1
                        current_tool_block_anthropic_idx = text_block_index + tool_block_index_counter

                        current_tool_calls_data[tool_call_id] = {
                            "anthropic_idx": current_tool_block_anthropic_idx,
                            "name": tc_chunk.function.name if tc_chunk.function.name else "",
                            "args_buffer": tc_chunk.function.arguments if tc_chunk.function.arguments else "",
                            "id_sent": False,
                            "name_sent": bool(tc_chunk.function.name)
                        }
                        
                        # Send content_block_start for the new tool
                        if not current_tool_calls_data[tool_call_id]["id_sent"]:
                            yield f"event: content_block_start\ndata: {json.dumps({'type': 'content_block_start', 'index': current_tool_block_anthropic_idx, 'content_block': {'type': 'tool_use', 'id': tool_call_id, 'name': current_tool_calls_data[tool_call_id]['name'], 'input': {}}})}\n\n"
                            current_tool_calls_data[tool_call_id]["id_sent"] = True
                    else:
                        # Continuation of an existing tool call
                        if tc_chunk.function.name and not current_tool_calls_data[tool_call_id]["name_sent"]:
                            current_tool_calls_data[tool_call_id]["name"] = tc_chunk.function.name
                            logger.warning("Tool name received in a later chunk part, which is unusual for SSE.")

                        if tc_chunk.function.arguments:
                            current_tool_calls_data[tool_call_id]["args_buffer"] += tc_chunk.function.arguments

                    # Send argument delta
                    if tc_chunk.function.arguments:
                        yield f"event: content_block_delta\ndata: {json.dumps({'type': 'content_block_delta', 'index': current_tool_calls_data[tool_call_id]['anthropic_idx'], 'delta': {'type': 'input_json_delta', 'partial_json': tc_chunk.function.arguments}})}\n\n"

            if chunk_finish_reason:
                final_stop_reason = "end_turn"
                if chunk_finish_reason == "length":
                    final_stop_reason = "max_tokens"
                elif chunk_finish_reason == "tool_calls":
                    final_stop_reason = "tool_use"
                elif chunk_finish_reason == "stop":
                    final_stop_reason = "end_turn"
                else:
                    final_stop_reason = chunk_finish_reason

                # Stop the text block
                yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': text_block_index})}\n\n"

                # Stop all tool blocks
                for tool_data in current_tool_calls_data.values():
                    yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': tool_data['anthropic_idx']})}\n\n"

                # Send message_delta with stop reason and final usage
                final_usage = {"input_tokens": input_tokens, "output_tokens": output_tokens}
                yield f"event: message_delta\ndata: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': final_stop_reason, 'stop_sequence': None}, 'usage': final_usage})}\n\n"
                yield f"event: message_stop\ndata: {json.dumps({'type': 'message_stop'})}\n\n"
                return

        except Exception as e:
            logger.error(f"Error processing stream chunk: {str(e)} - Chunk: {chunk}")
            import traceback
            logger.error(traceback.format_exc())

    # Fallback if stream ends without explicit finish_reason
    logger.debug("Stream ended without explicit finish_reason in last chunk. Finalizing.")
    yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': text_block_index})}\n\n"
    for tool_data in current_tool_calls_data.values():
        yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': tool_data['anthropic_idx']})}\n\n"

    final_usage = {"input_tokens": input_tokens, "output_tokens": output_tokens}
    yield f"event: message_delta\ndata: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': final_stop_reason, 'stop_sequence': None}, 'usage': final_usage})}\n\n"
    yield f"event: message_stop\ndata: {json.dumps({'type': 'message_stop'})}\n\n"

class Colors:
    CYAN = "\033[96m"; BLUE = "\033[94m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    RED = "\033[91m"; MAGENTA = "\033[95m"; RESET = "\033[0m"; BOLD = "\033[1m"
    UNDERLINE = "\033[4m"; DIM = "\033[2m"

def log_request_beautifully(method, path, requested_model, openrouter_model_used, num_messages, num_tools, status_code):
    """Log requests, showing mapping from requested model to the actual OpenRouter model used."""
    req_display = f"{Colors.CYAN}{requested_model}{Colors.RESET}"
    openrouter_display = f"{Colors.GREEN}{openrouter_model_used.replace('openrouter/', '')}{Colors.RESET}"

    endpoint = path.split("?")[0] if "?" in path else path
    tools_str = f"{Colors.MAGENTA}{num_tools} tools{Colors.RESET}"
    messages_str = f"{Colors.BLUE}{num_messages} messages{Colors.RESET}"
    status_str = f"{Colors.GREEN}✓ {status_code} OK{Colors.RESET}" if status_code == 200 else f"{Colors.RED}✗ {status_code}{Colors.RESET}"

    log_line = f"{Colors.BOLD}{method} {endpoint}{Colors.RESET} {status_str}"
    model_line = f"Request: {req_display} → OpenRouter: {openrouter_display} ({tools_str}, {messages_str})"

    print(log_line); print(model_line); sys.stdout.flush()

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Run with: python openrouter_anthropic_server.py")
        print("Or: uvicorn openrouter_anthropic_server:app --reload --host 0.0.0.0 --port 5001")
        print("Ensure OPENROUTER_API_KEY is set in your environment or .env file.")
        print("Optional .env vars:")
        print(f"  ANTHROPIC_MODEL (default: {DEFAULT_BIG_MODEL})")
        print(f"  ANTHROPIC_SMALL_FAST_MODEL (default: {DEFAULT_SMALL_MODEL})")
        sys.exit(0)

    if not OPENROUTER_API_KEY:
        print("🔴 FATAL: OPENROUTER_API_KEY is not set. Please set it in your environment or .env file.")
        print("If you have a .env file, ensure it's in the same directory or loaded correctly.")
        sys.exit(1)
    else:
        print(f"✅ OPENROUTER_API_KEY loaded. BIG_MODEL='{BIG_MODEL}', SMALL_MODEL='{SMALL_MODEL}'")
    
    print("🚀 Starting OpenRouter to Anthropic Proxy...")
    print(f"🔑 API Key: {OPENROUTER_API_KEY[:10]}...")
    print(f"📋 Models: BIG={BIG_MODEL}, SMALL={SMALL_MODEL}")
    
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="warning")  # Match Gemini's log level

if __name__ == "__main__":
    main()