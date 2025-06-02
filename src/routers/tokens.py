"""
Tokens router for OpenRouter Anthropic Server.
Handles /v1/messages/count_tokens endpoint with enhanced validation.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import json

from src.models.anthropic import TokenCountRequest, TokenCountResponse
from src.services.validation import MessageValidationService
from src.services.conversion import ModelMappingService
from src.core.logging_config import get_logger
from src.utils.errors import OpenRouterProxyError

logger = get_logger(__name__)
from src.utils.config import config

router = APIRouter(prefix="/v1/messages", tags=["tokens"])

# Initialize services
message_validator = MessageValidationService()
model_mapper = ModelMappingService()


async def validate_token_request(request: TokenCountRequest) -> TokenCountRequest:
    """Validate token counting request."""
    try:
        # Validate individual messages
        for message in request.messages:
            validation_result = message_validator.validate(message)
            if not validation_result.is_valid:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid message format",
                        "errors": validation_result.errors,
                        "warnings": validation_result.warnings
                    }
                )
        
        logger.info("✅ Token request validation passed",
                   message_count=len(request.messages))
        return request
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Token request validation failed",
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Token request validation failed", "message": str(e)}
        )


async def count_tokens_with_litellm(request: TokenCountRequest) -> int:
    """Count tokens using LiteLLM's token counting functionality."""
    import litellm
    
    try:
        # Map model if needed
        mapping_result = model_mapper.map_model(request.model)
        model_to_use = mapping_result.mapped_model
        
        logger.info("🔢 Counting tokens for model",
                   model=model_to_use,
                   original_model=request.model)
        
        # Convert messages to LiteLLM format for token counting
        litellm_messages = []
        for message in request.messages:
            if isinstance(message.content, str):
                litellm_messages.append({
                    "role": message.role,
                    "content": message.content
                })
            elif isinstance(message.content, list):
                # Handle complex content blocks
                content_text = ""
                for block in message.content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            content_text += block.get("text", "")
                        elif block.get("type") == "tool_use":
                            # Include tool use in token count
                            content_text += f"Tool: {block.get('name', '')} {json.dumps(block.get('input', {}))}"
                        elif block.get("type") == "tool_result":
                            # Include tool result in token count
                            content_text += f"Result: {block.get('content', '')}"
                
                litellm_messages.append({
                    "role": message.role,
                    "content": content_text
                })
        
        # Count tokens using LiteLLM
        token_count = litellm.token_counter(
            model=model_to_use,
            messages=litellm_messages
        )
        
        logger.info("✅ Token count completed",
                   token_count=token_count,
                   model=model_to_use)
        return token_count
        
    except Exception as e:
        logger.error("❌ Token counting failed",
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Token counting failed", "message": str(e)}
        )


@router.post("/count_tokens")
async def count_tokens(request: TokenCountRequest) -> TokenCountResponse:
    """
    Count tokens in a set of messages.
    
    This endpoint:
    1. Validates the incoming messages
    2. Maps model names if needed
    3. Converts messages to appropriate format for token counting
    4. Uses LiteLLM to count tokens
    5. Returns the token count in Anthropic format
    """
    try:
        logger.info("🔢 Received token count request",
                   model=request.model,
                   message_count=len(request.messages))
        
        # Step 1: Validate request
        validated_request = await validate_token_request(request)
        
        # Step 2: Count tokens
        token_count = await count_tokens_with_litellm(validated_request)
        
        # Step 3: Create response
        response = TokenCountResponse(input_tokens=token_count)
        
        logger.info("✅ Token counting completed successfully",
                   token_count=token_count,
                   model=request.model)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Token counting endpoint failed",
                    error_type=type(e).__name__,
                    error_message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error": "Token counting failed", "message": str(e)}
        )