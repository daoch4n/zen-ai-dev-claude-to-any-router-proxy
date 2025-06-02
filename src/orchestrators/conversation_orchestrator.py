"""
Main conversation orchestrator that replaces monolithic router functions.

This orchestrator coordinates the complete message processing pipeline
using Prefect workflows, replacing the 390+ line router functions.
"""

import uuid
from typing import Optional
from fastapi import HTTPException

from src.models.anthropic import MessagesRequest, MessagesResponse
from src.workflows.message_workflows import process_message_request
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