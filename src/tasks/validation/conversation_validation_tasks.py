"""Conversation validation task functions."""

from typing import List
from ...models.anthropic import Message
from ...models.instructor import ConversationFlowResult
from ...core.logging_config import get_logger

logger = get_logger("validation.conversation_tasks")


def validate_conversation_flow_data(messages: List[Message]) -> ConversationFlowResult:
    """Validate conversation flow patterns.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        ConversationFlowResult with validation details
    """
    try:
        flow_errors = []
        suggestions = []
        
        if not messages:
            flow_errors.append("Conversation cannot be empty")
            return ConversationFlowResult(
                is_valid=False,
                flow_errors=flow_errors,
                role_sequence_valid=False,
                tool_flow_valid=False
            )
        
        # Validate role sequence
        role_sequence_valid = validate_role_sequence(messages, flow_errors)
        
        # Validate tool flow
        tool_flow_valid = validate_tool_flow_in_conversation(messages, flow_errors)
        
        # Generate suggestions
        if not role_sequence_valid:
            suggestions.append("Ensure proper alternating user/assistant roles")
        if not tool_flow_valid:
            suggestions.append("Check tool use and result pairing")
        
        is_valid = role_sequence_valid and tool_flow_valid and len(flow_errors) == 0
        
        result = ConversationFlowResult(
            is_valid=is_valid,
            flow_errors=flow_errors,
            role_sequence_valid=role_sequence_valid,
            tool_flow_valid=tool_flow_valid,
            suggestions=suggestions
        )
        
        logger.debug("Conversation flow validation completed",
                    message_count=len(messages),
                    role_sequence_valid=role_sequence_valid,
                    tool_flow_valid=tool_flow_valid)
        
        return result
        
    except Exception as e:
        logger.error("Conversation flow validation execution failed", error=str(e), exc_info=True)
        from ...utils.errors import ConversationFlowError
        raise ConversationFlowError(f"Conversation flow validation failed: {e}")


def validate_role_sequence(messages: List[Message], errors: List[str]) -> bool:
    """Validate role sequence in conversation.
    
    Args:
        messages: List of conversation messages
        errors: List to append error messages to
        
    Returns:
        True if role sequence is valid, False otherwise
    """
    if not messages:
        return True
    
    # First message should be user
    if messages[0].role != "user":
        errors.append("Conversation should start with a user message")
        return False
    
    # Check alternating pattern
    for i in range(1, len(messages)):
        current_role = messages[i].role
        previous_role = messages[i-1].role
        
        # Allow same role in some cases (e.g., tool results)
        if current_role == previous_role:
            # Check if this is a valid same-role sequence
            if not is_valid_same_role_sequence(messages[i-1], messages[i]):
                errors.append(f"Invalid role sequence at message {i}: {previous_role} -> {current_role}")
                return False
    
    return True


def is_valid_same_role_sequence(prev_msg: Message, curr_msg: Message) -> bool:
    """Check if same-role sequence is valid.
    
    Args:
        prev_msg: Previous message in sequence
        curr_msg: Current message in sequence
        
    Returns:
        True if same-role sequence is valid, False otherwise
    """
    # User can send multiple messages (e.g., tool results)
    if curr_msg.role == "user":
        # Check if current message contains tool results
        if isinstance(curr_msg.content, list):
            return any(
                hasattr(block, 'type') and block.type == "tool_result" 
                for block in curr_msg.content
            )
    
    # Assistant can send multiple messages in some cases
    if curr_msg.role == "assistant":
        # Generally not recommended, but not invalid
        return True
    
    return False


def validate_tool_flow_in_conversation(messages: List[Message], errors: List[str]) -> bool:
    """Validate tool flow within conversation.
    
    Args:
        messages: List of conversation messages
        errors: List to append error messages to
        
    Returns:
        True if tool flow is valid, False otherwise
    """
    tool_uses = set()
    tool_results = set()
    
    for msg in messages:
        if isinstance(msg.content, list):
            for block in msg.content:
                if hasattr(block, 'type'):
                    if block.type == "tool_use":
                        tool_id = getattr(block, 'id', None)
                        if tool_id:
                            tool_uses.add(tool_id)
                    elif block.type == "tool_result":
                        tool_use_id = getattr(block, 'tool_use_id', None)
                        if tool_use_id:
                            tool_results.add(tool_use_id)
    
    # Check for orphaned tools
    orphaned = tool_uses - tool_results
    if orphaned:
        errors.append(f"Orphaned tool uses found: {list(orphaned)}")
        return False
    
    # Check for results without uses
    missing_uses = tool_results - tool_uses
    if missing_uses:
        errors.append(f"Tool results without corresponding uses: {list(missing_uses)}")
        return False
    
    return True