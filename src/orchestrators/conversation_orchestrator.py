"""
Main conversation orchestrator that replaces monolithic router functions.

This orchestrator coordinates the complete message processing pipeline
using Prefect workflows, replacing the 390+ line router functions.
"""

import uuid
import json
from typing import Optional
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from src.models.anthropic import MessagesRequest, MessagesResponse
from src.workflows.message_workflows import process_message_request
from src.services.litellm_bypass_flow import LiteLLMBypassFlow
from src.services.litellm_messages_service import LiteLLMMessagesService
from src.services.context_manager import ContextManager
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class ConversationOrchestrator:
    """
    Main orchestrator that replaces the monolithic router functions.
    
    This class provides a clean interface for message processing that
    eliminates the 390+ line functions and 284+ lines of code duplication.
    """
    
    def __init__(self):
        """Initialize the conversation orchestrator."""
        self.logger = logger.bind(component="conversation_orchestrator")
        self.logger.info("Conversation orchestrator initialized")
    
    async def process_message(
        self,
        request: MessagesRequest,
        x_api_key: Optional[str] = None,
        authorization: Optional[str] = None,
        x_correlation_id: Optional[str] = None
    ) -> MessagesResponse:
        """
        Process a non-streaming message request.
        
        This method replaces the 390+ line create_message function
        with a clean workflow orchestration.
        """
        
        # Generate request ID
        request_id = x_correlation_id or str(uuid.uuid4())
        
        # Extract API key
        api_key = self._extract_api_key(x_api_key, authorization)
        
        # Create request-scoped logger
        request_logger = self.logger.bind(
            request_id=request_id,
            model=request.model,
            message_count=len(request.messages),
            streaming=False
        )
        
        request_logger.info("Processing message request via orchestrator")
        
        try:
            # Execute the main workflow
            response = await process_message_request(
                request=request,
                request_id=request_id,
                streaming=False,
                api_key=api_key
            )
            
            request_logger.info("Message request processed successfully")
            return response
            
        except Exception as e:
            request_logger.error(
                "Message request processing failed",
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Re-raise as HTTPException for FastAPI
            if isinstance(e, HTTPException):
                raise
            else:
                raise HTTPException(
                    status_code=500,
                    detail={"error": "Message processing failed", "message": str(e)}
                )
    
    async def process_message_stream(
        self,
        request: MessagesRequest,
        x_api_key: Optional[str] = None,
        authorization: Optional[str] = None,
        x_correlation_id: Optional[str] = None
    ):
        """
        Process a streaming message request.
        
        This method replaces the 404+ line create_message_stream function
        with a clean workflow orchestration, eliminating code duplication.
        """
        
        # Generate request ID
        request_id = x_correlation_id or str(uuid.uuid4())
        
        # Extract API key
        api_key = self._extract_api_key(x_api_key, authorization)
        
        # Create request-scoped logger
        request_logger = self.logger.bind(
            request_id=request_id,
            model=request.model,
            message_count=len(request.messages),
            streaming=True
        )
        
        request_logger.info("Processing streaming message request via orchestrator")
        
        try:
            # Execute the main workflow with streaming enabled
            response = await process_message_request(
                request=request,
                request_id=request_id,
                streaming=True,
                api_key=api_key
            )
            
            request_logger.info("Streaming message request processed successfully")
            return response
            
        except Exception as e:
            request_logger.error(
                "Streaming message request processing failed",
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Re-raise as HTTPException for FastAPI
            if isinstance(e, HTTPException):
                raise
            else:
                raise HTTPException(
                    status_code=500,
                    detail={"error": "Streaming message processing failed", "message": str(e)}
                )
    
    def _extract_api_key(
        self,
        x_api_key: Optional[str],
        authorization: Optional[str]
    ) -> Optional[str]:
        """Extract API key from headers."""
        
        if x_api_key:
            return x_api_key
        
        if authorization:
            # Handle "Bearer " prefix
            if authorization.startswith("Bearer "):
                return authorization[7:]
            return authorization
        
        return None


# Global orchestrator instance
conversation_orchestrator = ConversationOrchestrator()


# Convenience functions for router usage
async def process_message_request_orchestrated(
    request: MessagesRequest,
    x_api_key: Optional[str] = None,
    authorization: Optional[str] = None,
    x_correlation_id: Optional[str] = None
) -> MessagesResponse:
    """
    Convenience function for non-streaming message processing.
    
    This function provides a simple interface for the router to replace
    the monolithic create_message function.
    """
    return await conversation_orchestrator.process_message(
        request=request,
        x_api_key=x_api_key,
        authorization=authorization,
        x_correlation_id=x_correlation_id
    )


async def process_message_stream_orchestrated(
    request: MessagesRequest,
    x_api_key: Optional[str] = None,
    authorization: Optional[str] = None,
    x_correlation_id: Optional[str] = None
):
    """
    Convenience function for streaming message processing.
    
    This function provides a simple interface for the router to replace
    the monolithic create_message_stream function.
    """
    return await conversation_orchestrator.process_message_stream(
        request=request,
        x_api_key=x_api_key,
        authorization=authorization,
        x_correlation_id=x_correlation_id
    )


# Bypass orchestrator functions
async def process_bypass_request_orchestrated(
    request: MessagesRequest,
    x_api_key: Optional[str] = None,
    authorization: Optional[str] = None,
    x_correlation_id: Optional[str] = None
) -> MessagesResponse:
    """
    Process message request using LiteLLM bypass flow.
    
    This function provides direct OpenRouter communication bypassing LiteLLM
    for improved performance while maintaining full compatibility.
    """
    # Initialize context manager
    context_manager = ContextManager()
    
    # Generate request ID
    request_id = x_correlation_id or str(uuid.uuid4())
    
    # Extract API key
    api_key = conversation_orchestrator._extract_api_key(x_api_key, authorization)
    
    # Create request-scoped logger
    request_logger = logger.bind(
        request_id=request_id,
        model=request.model,
        message_count=len(request.messages),
        streaming=False,
        bypass_mode=True
    )
    
    request_logger.info("Processing message request via bypass orchestrator")
    
    try:
        # Set up request context
        request_context = context_manager.create_request_context(
            endpoint="/v1/messages",
            method="POST",
            user_agent="bypass-mode",
            request_id=request_id
        )
        
        try:
            # Initialize bypass flow
            async with LiteLLMBypassFlow() as bypass_flow:
                # Execute bypass conversion
                result = await bypass_flow.convert_async(
                    source=request,
                    request_id=request_id,
                    api_key=api_key
                )
                
                if not result.success:
                    # Check if this is a client error (4xx) that should be returned as-is
                    if result.metadata.get("client_error"):
                        # This is a 4xx client error - return it with proper status code
                        status_code = result.metadata.get("status_code", 400)
                        request_logger.info("Returning client error response", 
                                          status_code=status_code,
                                          errors=result.errors)
                        
                        raise HTTPException(
                            status_code=status_code,
                            detail=result.converted_data
                        )
                    else:
                        # This is a server error or other failure
                        error_msg = "; ".join(result.errors) if result.errors else "Unknown bypass error"
                        request_logger.error("Bypass flow failed", errors=result.errors)
                        raise ValueError(f"Bypass processing failed: {error_msg}")
                
                # Convert result back to MessagesResponse object
                response = MessagesResponse(**result.converted_data)
                
                request_logger.info("Bypass message request processed successfully",
                                  response_id=response.id,
                                  bypass_used=result.metadata.get("bypass_used", False),
                                  fallback_used=result.metadata.get("fallback_used", False))
                
                return response
        finally:
            # Clean up context
            context_manager.cleanup_context()
                
    except Exception as e:
        request_logger.error(
            "Bypass message request processing failed",
            error=str(e),
            error_type=type(e).__name__
        )
        
        # Re-raise as HTTPException for FastAPI
        if isinstance(e, HTTPException):
            raise
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Bypass message processing failed", 
                    "message": str(e),
                    "bypass_mode": True
                }
            )


async def process_bypass_stream_orchestrated(
    request: MessagesRequest,
    x_api_key: Optional[str] = None,
    authorization: Optional[str] = None,
    x_correlation_id: Optional[str] = None
) -> StreamingResponse:
    """
    Process streaming message request using LiteLLM bypass flow.
    
    This function provides direct OpenRouter streaming bypassing LiteLLM
    for improved performance while maintaining full compatibility.
    """
    # Initialize context manager
    context_manager = ContextManager()
    
    # Generate request ID
    request_id = x_correlation_id or str(uuid.uuid4())
    
    # Extract API key
    api_key = conversation_orchestrator._extract_api_key(x_api_key, authorization)
    
    # Create request-scoped logger
    request_logger = logger.bind(
        request_id=request_id,
        model=request.model,
        message_count=len(request.messages),
        streaming=True,
        bypass_mode=True
    )
    
    request_logger.info("Processing streaming message request via bypass orchestrator")
    
    async def stream_generator():
        """Generate streaming response chunks."""
        try:
            # Set up request context
            request_context = context_manager.create_request_context(
                endpoint="/v1/messages",
                method="POST",
                user_agent="bypass-streaming-mode",
                request_id=request_id
            )
            
            try:
                # Initialize bypass flow
                async with LiteLLMBypassFlow() as bypass_flow:
                    # Execute bypass streaming
                    async for chunk in bypass_flow.convert_streaming(
                        source=request,
                        request_id=request_id,
                        api_key=api_key
                    ):
                        # Format chunk for SSE streaming
                        if chunk.get("type") == "error":
                            # Handle error chunks
                            request_logger.error("Streaming error chunk received", 
                                               error=chunk.get("error"))
                            yield f"data: {json.dumps(chunk)}\n\n"
                        else:
                            # Handle normal chunks
                            yield f"data: {json.dumps(chunk)}\n\n"
                    
                    # Send completion signal
                    yield "data: [DONE]\n\n"
                    
                    request_logger.info("Bypass streaming request completed successfully")
            finally:
                # Clean up context
                context_manager.cleanup_context()
                    
        except Exception as e:
            request_logger.error(
                "Bypass streaming request processing failed",
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Send error chunk
            error_chunk = {
                "type": "error",
                "error": {
                    "type": "bypass_streaming_failed",
                    "message": str(e),
                    "bypass_mode": True
                }
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            yield "data: [DONE]\n\n"
    
    # Return streaming response
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "X-Request-ID": request_id,
            "X-Bypass-Mode": "true"
        }
    )


# LiteLLM Messages orchestrator functions
async def process_litellm_messages_orchestrated(
    request: MessagesRequest,
    x_api_key: Optional[str] = None,
    authorization: Optional[str] = None,
    x_correlation_id: Optional[str] = None
) -> MessagesResponse:
    """
    Process message request using LiteLLM's native /v1/messages endpoint.
    
    This function calls LiteLLM's /v1/messages endpoint which natively
    accepts Anthropic format, eliminating the need for format conversion.
    """
    # Generate request ID
    request_id = x_correlation_id or str(uuid.uuid4())
    
    # Extract API key
    api_key = conversation_orchestrator._extract_api_key(x_api_key, authorization)
    
    # Create request-scoped logger
    request_logger = logger.bind(
        request_id=request_id,
        model=request.model,
        message_count=len(request.messages),
        streaming=False,
        backend="LITELLM_MESSAGES"
    )
    
    request_logger.info("Processing message via LiteLLM /v1/messages endpoint")
    
    try:
        # Initialize the LiteLLM Messages service
        litellm_service = LiteLLMMessagesService()
        
        # Call LiteLLM's /v1/messages endpoint directly - no conversion needed!
        response = await litellm_service.create_message(
            request=request,
            api_key=api_key
        )
        
        request_logger.info("LiteLLM /v1/messages request completed successfully",
                          response_id=response.id)
        
        return response
        
    except Exception as e:
        request_logger.error(
            "LiteLLM /v1/messages request failed",
            error=str(e),
            error_type=type(e).__name__
        )
        
        # Re-raise as HTTPException for FastAPI
        if isinstance(e, HTTPException):
            raise
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "LiteLLM messages processing failed", 
                    "message": str(e),
                    "backend": "LITELLM_MESSAGES"
                }
            )


async def process_litellm_messages_stream_orchestrated(
    request: MessagesRequest,
    x_api_key: Optional[str] = None,
    authorization: Optional[str] = None,
    x_correlation_id: Optional[str] = None
) -> StreamingResponse:
    """
    Process streaming message request using LiteLLM's native /v1/messages endpoint.
    
    This function streams from LiteLLM's /v1/messages endpoint which natively
    accepts and returns Anthropic format.
    """
    # Generate request ID
    request_id = x_correlation_id or str(uuid.uuid4())
    
    # Extract API key
    api_key = conversation_orchestrator._extract_api_key(x_api_key, authorization)
    
    # Create request-scoped logger
    request_logger = logger.bind(
        request_id=request_id,
        model=request.model,
        message_count=len(request.messages),
        streaming=True,
        backend="LITELLM_MESSAGES"
    )
    
    request_logger.info("Processing streaming via LiteLLM /v1/messages endpoint")
    
    async def stream_generator():
        """Generate streaming response chunks from LiteLLM."""
        try:
            # Initialize the LiteLLM Messages service
            litellm_service = LiteLLMMessagesService()
            
            # Stream from LiteLLM's /v1/messages endpoint
            async for chunk in litellm_service.create_message_stream(
                request=request,
                api_key=api_key
            ):
                # Chunks are already in Anthropic format - just pass through
                yield f"data: {json.dumps(chunk)}\n\n"
            
            # Send completion signal
            yield "data: [DONE]\n\n"
            
            request_logger.info("LiteLLM streaming completed successfully")
            
        except Exception as e:
            request_logger.error(
                "LiteLLM streaming failed",
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Send error chunk
            error_chunk = {
                "type": "error",
                "error": {
                    "type": "litellm_streaming_failed",
                    "message": str(e),
                    "backend": "LITELLM_MESSAGES"
                }
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            yield "data: [DONE]\n\n"
    
    # Return streaming response
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Request-ID": request_id,
            "X-Backend": "LITELLM_MESSAGES"
        }
    )