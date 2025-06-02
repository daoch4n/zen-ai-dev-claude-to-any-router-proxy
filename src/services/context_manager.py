"""Context management service for request/conversation/tool contexts"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

from src.core.logging_config import (
    bind_request_context,
    bind_conversation_context, 
    bind_tool_context,
    clear_context,
    get_logger
)
from src.models.anthropic import MessagesRequest

@dataclass
class RequestContextData:
    """Request-level context data"""
    request_id: str
    endpoint: str
    method: str
    user_agent: Optional[str]
    correlation_id: str
    timestamp: datetime

@dataclass
class ConversationContextData:
    """Conversation-level context data"""
    conversation_id: str
    model: str
    message_count: int
    current_step: str
    metadata: Dict[str, Any]

@dataclass
class ToolContextData:
    """Tool execution context data"""
    tool_name: str
    tool_call_id: str
    execution_step: int
    input_keys: list

class ContextManager:
    """Manages context lifecycle and propagation"""
    
    def __init__(self):
        self.logger = get_logger("context_manager")
    
    def create_request_context(
        self,
        endpoint: str,
        method: str = "POST",
        user_agent: str = None,
        request_id: str = None
    ) -> RequestContextData:
        """Create and bind request context"""
        request_id = request_id or str(uuid.uuid4())
        correlation_id = f"req_{request_id[:8]}"
        
        context_data = RequestContextData(
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            user_agent=user_agent,
            correlation_id=correlation_id,
            timestamp=datetime.utcnow()
        )
        
        # Bind to contextvars for automatic propagation
        bind_request_context(
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            user_agent=user_agent,
            correlation_id=correlation_id
        )
        
        self.logger.info("Request context created", 
                        request_id=request_id, 
                        endpoint=endpoint)
        
        return context_data
    
    def create_conversation_context(
        self,
        request: MessagesRequest,
        request_context: RequestContextData
    ) -> ConversationContextData:
        """Create and bind conversation context"""
        conversation_id = f"conv_{request_context.request_id[:8]}"
        
        # Use original model if available, otherwise use mapped model
        model_for_context = getattr(request, 'original_model', None) or request.model
        
        context_data = ConversationContextData(
            conversation_id=conversation_id,
            model=model_for_context,
            message_count=len(request.messages),
            current_step="validation",
            metadata={}
        )
        
        # Bind to contextvars
        bind_conversation_context(
            conversation_id=conversation_id,
            model=model_for_context,
            message_count=len(request.messages),
            current_step="validation"
        )
        
        self.logger.info("Conversation context created",
                        conversation_id=conversation_id,
                        model=model_for_context,
                        message_count=len(request.messages))
        
        return context_data
    
    def create_tool_context(
        self,
        tool_name: str,
        tool_call_id: str,
        input_data: Dict[str, Any],
        execution_step: int = 1
    ) -> ToolContextData:
        """Create and bind tool execution context"""
        context_data = ToolContextData(
            tool_name=tool_name,
            tool_call_id=tool_call_id,
            execution_step=execution_step,
            input_keys=list(input_data.keys())
        )
        
        # Bind to contextvars
        bind_tool_context(
            tool_name=tool_name,
            tool_call_id=tool_call_id,
            execution_step=execution_step,
            input_keys=list(input_data.keys())
        )
        
        self.logger.info("Tool context created",
                        tool_name=tool_name,
                        tool_call_id=tool_call_id,
                        execution_step=execution_step)
        
        return context_data
    
    def update_conversation_step(self, step: str) -> None:
        """Update the current conversation step"""
        from src.core.logging_config import conversation_context
        
        current_ctx = conversation_context.get({})
        current_ctx["current_step"] = step
        conversation_context.set(current_ctx)
        
        self.logger.debug("Conversation step updated", current_step=step)
    
    def cleanup_context(self) -> None:
        """Clean up all context at end of request"""
        self.logger.debug("Cleaning up context")
        clear_context()