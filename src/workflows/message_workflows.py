"""
Message processing workflows using Prefect orchestration.

This module contains the main message processing flows that replace 
the monolithic router functions with clean, testable workflows.
"""

import uuid
from typing import Dict, Any, Optional, List
from prefect import flow, task
from prefect.cache_policies import NO_CACHE
from fastapi import HTTPException

from src.models.anthropic import MessagesRequest, MessagesResponse
from src.services.context_manager import ContextManager
from src.core.logging_config import get_logger
from src.services import message_validator
from src.services.conversion import AnthropicToLiteLLMConverter, LiteLLMResponseToAnthropicConverter
from src.services.http_client import HTTPClientService
from src.services.tool_execution import ToolExecutionService

logger = get_logger(__name__)


@flow(name="process_message_request")
async def process_message_request(
    request: MessagesRequest,
    request_id: str,
    streaming: bool = False,
    api_key: Optional[str] = None
) -> MessagesResponse:
    """
    Main message processing workflow that replaces the monolithic router function.
    
    This flow orchestrates the complete message processing pipeline:
    1. Context creation and mixed content detection
    2. Request validation and conversion
    3. API call execution
    4. Tool execution if needed
    5. Response conversion and cleanup
    """
    
    # Create flow-scoped logger with request context
    flow_logger = logger.bind(
        flow_name="process_message_request",
        request_id=request_id,
        model=request.model,
        message_count=len(request.messages),
        streaming=streaming
    )
    
    flow_logger.info("Message processing workflow started")
    
    try:
        # Step 1: Create conversation context and handle mixed content
        context_result = await create_conversation_context_task(
            request=request,
            request_id=request_id
        )
        
        cleaned_request = context_result["cleaned_request"]
        conversation_context = context_result["conversation_context"]
        
        # Step 2: Validate and convert request
        flow_logger.info("Starting request validation and conversion")
        
        validated_request = await validate_request_task(
            request=cleaned_request
        )
        
        litellm_request = await convert_to_litellm_task(
            request=validated_request,
            api_key=api_key
        )
        
        # Step 3: Execute API call
        flow_logger.info("Executing LiteLLM API call")
        
        if streaming:
            response = await execute_streaming_api_call_task(
                litellm_request=litellm_request,
                conversation_context=conversation_context
            )
        else:
            response = await execute_api_call_task(
                litellm_request=litellm_request,
                conversation_context=conversation_context
            )
        
        # Step 4: Handle tool execution if needed
        if await detect_tool_use_task(response):
            flow_logger.info("Tool use detected, executing tool workflow")
            
            final_response = await execute_tool_workflow_task(
                response=response,
                conversation_context=conversation_context,
                original_request=validated_request
            )
        else:
            flow_logger.info("No tool use detected")
            final_response = response
        
        # Step 5: Convert response to Anthropic format
        flow_logger.info("Converting response to Anthropic format")
        
        anthropic_response = await convert_to_anthropic_task(
            response=final_response,
            original_request=validated_request
        )
        
        flow_logger.info("Message processing workflow completed successfully")
        return anthropic_response
        
    except ValueError as e:
        # Handle validation errors with HTTP 400
        if "validation failed" in str(e).lower():
            flow_logger.error(
                "Message processing workflow validation failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise HTTPException(
                status_code=400,
                detail={"error": "Validation failed", "message": str(e)}
            )
        else:
            # Other ValueErrors still get 500
            flow_logger.error(
                "Message processing workflow failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise HTTPException(
                status_code=500,
                detail={"error": "Message processing failed", "message": str(e)}
            )
    except Exception as e:
        flow_logger.error(
            "Message processing workflow failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=500,
            detail={"error": "Message processing failed", "message": str(e)}
        )


@task(name="create_conversation_context")
async def create_conversation_context_task(
    request: MessagesRequest,
    request_id: str
) -> Dict[str, Any]:
    """Create conversation context and handle mixed content detection."""
    
    task_logger = logger.bind(
        task_name="create_conversation_context",
        request_id=request_id
    )
    
    task_logger.info("Creating conversation context")
    
    context_manager = ContextManager()
    
    # Create request context
    request_context = context_manager.create_request_context(
        endpoint="/v1/messages",
        method="POST",
        request_id=request_id
    )
    
    # Create conversation context
    conversation_context = context_manager.create_conversation_context(
        request=request,
        request_context=request_context
    )
    
    # Handle mixed content detection
    context_manager.update_conversation_step("mixed_content_detection")
    
    # Check for user denial pattern and clean conversation
    cleaned_request = await detect_and_clean_mixed_content_task(request)
    
    task_logger.info("Conversation context created successfully")
    
    return {
        "cleaned_request": cleaned_request,
        "conversation_context": conversation_context
    }


@task(name="detect_and_clean_mixed_content")
async def detect_and_clean_mixed_content_task(request: MessagesRequest) -> MessagesRequest:
    """Detect and clean mixed content in messages."""
    
    task_logger = logger.bind(task_name="detect_and_clean_mixed_content")
    
    task_logger.info("Checking for mixed content patterns")
    
    # Import the detector service
    from src.services.mixed_content_detector import MixedContentDetector
    
    try:
        detector = MixedContentDetector()
        
        # Check for user denial patterns
        has_denial = await detector.detect_user_denial_patterns(request.messages)
        if has_denial:
            task_logger.warning("User denial patterns detected, cleaning conversation")
            cleaned_request = await detector.clean_conversation(request)
            task_logger.info("Conversation cleaned due to denial patterns")
            return cleaned_request
        
        # Check for mixed content issues
        issues = await detector.detect_mixed_content_issues(request.messages)
        if issues:
            task_logger.warning(
                "Mixed content issues detected, cleaning conversation",
                issue_count=len(issues),
                issues=issues
            )
            cleaned_request = await detector.clean_conversation(request)
            task_logger.info("Conversation cleaned due to content issues")
            return cleaned_request
        
        task_logger.info("No mixed content issues found, request unchanged")
        return request
        
    except Exception as e:
        task_logger.error(
            "Mixed content detection failed, returning original request",
            error=str(e),
            error_type=type(e).__name__
        )
        # Return original request if detection fails
        return request


@task(name="validate_request")
async def validate_request_task(request: MessagesRequest) -> MessagesRequest:
    """Validate the request using the validation service."""
    
    task_logger = logger.bind(task_name="validate_request")
    task_logger.info("Validating request")
    
    validated_request = message_validator.validate_messages_request(request)
    
    task_logger.info("Request validation completed")
    return validated_request


@task(name="convert_to_litellm")
async def convert_to_litellm_task(
    request: MessagesRequest,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """Convert Anthropic request to LiteLLM format."""
    
    task_logger = logger.bind(task_name="convert_to_litellm")
    task_logger.info("Converting request to LiteLLM format")
    
    converter = AnthropicToLiteLLMConverter()
    litellm_request = converter.convert(request, api_key=api_key)
    
    task_logger.info("Request conversion completed")
    return litellm_request


@task(name="execute_api_call", cache_policy=NO_CACHE)
async def execute_api_call_task(
    litellm_request: Any,  # This is actually a ConversionResult object
    conversation_context: Any
) -> Any:
    """Execute non-streaming API call."""
    
    task_logger = logger.bind(task_name="execute_api_call")
    task_logger.info("Executing API call")
    
    # Extract request ID from conversation context
    request_id = getattr(conversation_context, 'request_id', 'unknown')
    
    # Extract the actual request data from ConversionResult
    if hasattr(litellm_request, 'converted_data'):
        request_data = litellm_request.converted_data
    else:
        # Fallback in case it's already a dictionary
        request_data = litellm_request
    
    http_client = HTTPClientService()
    response = await http_client.make_litellm_request(request_data, request_id)
    
    task_logger.info("API call completed")
    return response


@task(name="execute_streaming_api_call", cache_policy=NO_CACHE)
async def execute_streaming_api_call_task(
    litellm_request: Any,  # This is actually a ConversionResult object
    conversation_context: Any
) -> Any:
    """Execute streaming API call."""
    
    task_logger = logger.bind(task_name="execute_streaming_api_call")
    task_logger.info("Executing streaming API call")
    
    # Extract request ID from conversation context
    request_id = getattr(conversation_context, 'request_id', 'unknown')
    
    # Extract the actual request data from ConversionResult
    if hasattr(litellm_request, 'converted_data'):
        request_data = litellm_request.converted_data.copy()  # Make a copy to modify
    else:
        # Fallback in case it's already a dictionary
        request_data = litellm_request.copy() if isinstance(litellm_request, dict) else litellm_request
    
    # Ensure streaming is enabled in the request
    request_data['stream'] = True
    
    http_client = HTTPClientService()
    response = await http_client.make_litellm_request(request_data, request_id)
    
    task_logger.info("Streaming API call completed")
    return response


@task(name="detect_tool_use")
async def detect_tool_use_task(response: Any) -> bool:
    """Detect if the response contains tool use."""
    
    task_logger = logger.bind(task_name="detect_tool_use")
    task_logger.debug("Checking for tool use in response")
    
    try:
        # Import the detector service
        from src.services.tool_execution import ToolUseDetector
        
        detector = ToolUseDetector()
        has_tools = detector.has_tool_use_blocks(response)
        
        if has_tools:
            # Extract tool blocks for logging
            tool_blocks = detector.extract_tool_use_blocks(response)
            tool_names = [block.get('name', 'unknown') for block in tool_blocks]
            task_logger.info(
                "Tool use detected in response",
                tool_count=len(tool_blocks),
                tool_names=tool_names
            )
        else:
            task_logger.debug("No tool use detected in response")
        
        task_logger.debug("Tool use detection completed", has_tools=has_tools)
        return has_tools
        
    except Exception as e:
        task_logger.error(
            "Tool use detection failed",
            error=str(e),
            error_type=type(e).__name__
        )
        # Return False for safety if detection fails
        return False


@task(name="execute_tool_workflow")
async def execute_tool_workflow_task(
    response: Any,
    conversation_context: Any,
    original_request: MessagesRequest
) -> Any:
    """Execute tool workflow if tools are detected."""
    
    task_logger = logger.bind(task_name="execute_tool_workflow")
    task_logger.info("Executing tool workflow")
    
    try:
        # Import the tool execution service
        from src.services.tool_execution import ToolExecutionService
        
        # Create tool execution service instance
        tool_service = ToolExecutionService()
        
        # Generate a request ID for tool execution tracking
        import uuid
        request_id = str(uuid.uuid4())
        
        # Handle the tool use response - this orchestrates the entire flow:
        # 1. Extract tool_use blocks from response
        # 2. Execute each tool locally
        # 3. Create tool_result messages
        # 4. Continue conversation with tool results
        final_response = await tool_service.handle_tool_use_response(
            response=response,
            original_request=original_request,
            request_id=request_id
        )
        
        task_logger.info(
            "Tool workflow completed successfully",
            request_id=request_id
        )
        return final_response
        
    except Exception as e:
        task_logger.error(
            "Tool workflow execution failed",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        # Return original response if tool execution fails
        task_logger.warning("Returning original response due to tool execution failure")
        return response


@task(name="convert_to_anthropic", cache_policy=NO_CACHE)
async def convert_to_anthropic_task(
    response: Any,
    original_request: MessagesRequest
) -> MessagesResponse:
    """Convert LiteLLM response to Anthropic format."""
    
    task_logger = logger.bind(task_name="convert_to_anthropic")
    task_logger.info("Converting response to Anthropic format")
    
    converter = LiteLLMResponseToAnthropicConverter()
    conversion_result = converter.convert(response, original_request)
    
    # Extract the actual response data from ConversionResult
    if hasattr(conversion_result, 'converted_data'):
        anthropic_response = conversion_result.converted_data
    else:
        # Fallback in case it's already the final response
        anthropic_response = conversion_result
    
    task_logger.info("Response conversion completed")
    return anthropic_response