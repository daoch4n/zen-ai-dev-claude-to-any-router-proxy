"""
Mixed Content Detection Service for OpenRouter Anthropic Server.

This service handles detection and cleaning of mixed content patterns
that were previously duplicated across monolithic router functions.
"""

import re
from typing import List, Dict, Any, Optional
from src.models.anthropic import MessagesRequest, Message
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class MixedContentDetector:
    """
    Service for detecting and cleaning mixed content patterns in conversations.
    
    This replaces the 284+ lines of duplicated logic from the original
    monolithic router functions.
    """
    
    def __init__(self):
        """Initialize the mixed content detector with pattern definitions."""
        # Common user denial patterns
        self.denial_patterns = [
            r"i\s+(?:can't|cannot|won't|will\s+not)\s+(?:help|assist|do|create)",
            r"(?:sorry|apologize),?\s+(?:but\s+)?i\s+(?:can't|cannot)",
            r"i'm\s+(?:not\s+)?(?:able\s+to|capable\s+of|allowed\s+to)",
            r"(?:that's|this\s+is)\s+(?:not\s+)?(?:something\s+i\s+can|appropriate)",
            r"i\s+(?:don't|do\s+not)\s+(?:feel\s+)?comfortable",
            r"against\s+my\s+(?:programming|guidelines|policy)",
            r"i\s+(?:must|have\s+to|need\s+to)\s+decline",
            r"i'm\s+(?:programmed\s+to|designed\s+to)\s+(?:not\s+)?(?:avoid|refuse)"
        ]
        
        # Potentially problematic content patterns
        self.mixed_content_patterns = [
            r"(?:illegal|unlawful|criminal)\s+(?:activity|behavior|content)",
            r"(?:harmful|dangerous|violent)\s+(?:content|material|instructions|behavior|guidelines)",
            r"(?:explicit|inappropriate|nsfw)\s+(?:content|material)",
            r"(?:personal|private|confidential)\s+(?:information|data)",
            r"(?:copyright|copyrighted)\s+(?:material|content)",
            r"(?:hate\s+speech|discrimination|harassment)",
            r"(?:self-harm|suicide|violence)",
            r"(?:drugs|weapons|explosives)\s+(?:instructions|recipes)"
        ]
        
        # Content cleaning patterns
        self.cleaning_patterns = {
            "excessive_caps": r"[A-Z]{4,}",
            "repeated_chars": r"(.)\1{3,}",
            "excessive_punctuation": r"[!?]{3,}",
            "special_chars": r"[^\w\s\.,!?;:\-()]+"
        }

    async def detect_user_denial_patterns(self, messages: List[Message]) -> bool:
        """
        Detect if any message contains user denial patterns.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            bool: True if denial patterns are detected
        """
        logger.debug("Checking for user denial patterns")
        
        try:
            for message in messages:
                if message.role == "assistant":
                    content = self._extract_text_content(message.content)
                    if content:
                        for pattern in self.denial_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                logger.info(
                                    "User denial pattern detected",
                                    pattern=pattern,
                                    message_role=message.role
                                )
                                return True
            
            logger.debug("No user denial patterns found")
            return False
            
        except Exception as e:
            logger.error(
                "Error detecting user denial patterns",
                error=str(e),
                exc_info=True
            )
            return False

    async def detect_mixed_content_issues(self, messages: List[Message]) -> List[str]:
        """
        Detect mixed content issues in conversation messages.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            List[str]: List of detected issues
        """
        logger.debug("Checking for mixed content issues")
        
        issues = []
        
        try:
            for i, message in enumerate(messages):
                content = self._extract_text_content(message.content)
                if content:
                    for pattern_name, pattern in enumerate(self.mixed_content_patterns):
                        if re.search(pattern, content, re.IGNORECASE):
                            issue = f"Mixed content detected in message {i}: {pattern}"
                            issues.append(issue)
                            logger.warning(
                                "Mixed content issue detected",
                                message_index=i,
                                pattern_index=pattern_name,
                                pattern=pattern
                            )
            
            if issues:
                logger.info("Mixed content issues found", issue_count=len(issues))
            else:
                logger.debug("No mixed content issues found")
            
            return issues
            
        except Exception as e:
            logger.error(
                "Error detecting mixed content issues",
                error=str(e),
                exc_info=True
            )
            return []

    async def clean_conversation(self, request: MessagesRequest) -> MessagesRequest:
        """
        Clean conversation by removing or modifying problematic content.
        
        Args:
            request: Original messages request
            
        Returns:
            MessagesRequest: Cleaned request
        """
        logger.debug("Starting conversation cleaning")
        
        try:
            cleaned_messages = []
            
            for message in request.messages:
                cleaned_message = await self._clean_message(message)
                cleaned_messages.append(cleaned_message)
            
            # Create cleaned request
            cleaned_request = request.model_copy()
            cleaned_request.messages = cleaned_messages
            
            logger.info(
                "Conversation cleaning completed",
                original_message_count=len(request.messages),
                cleaned_message_count=len(cleaned_messages)
            )
            
            return cleaned_request
            
        except Exception as e:
            logger.error(
                "Error cleaning conversation",
                error=str(e),
                exc_info=True
            )
            # Return original request if cleaning fails
            return request

    async def validate_content_safety(self, content: str) -> bool:
        """
        Validate if content is safe and appropriate.
        
        Args:
            content: Text content to validate
            
        Returns:
            bool: True if content is safe
        """
        logger.debug("Validating content safety")
        
        try:
            # Check against mixed content patterns
            for pattern in self.mixed_content_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    logger.warning(
                        "Unsafe content detected",
                        pattern=pattern
                    )
                    return False
            
            # Additional safety checks
            if self._contains_excessive_caps(content):
                logger.warning("Content contains excessive capitalization")
                return False
            
            if self._contains_repeated_chars(content):
                logger.warning("Content contains excessive repeated characters")
                return False
            
            logger.debug("Content passed safety validation")
            return True
            
        except Exception as e:
            logger.error(
                "Error validating content safety",
                error=str(e),
                exc_info=True
            )
            # Return False for safety if validation fails
            return False

    def _extract_text_content(self, content: Any) -> Optional[str]:
        """Extract text content from various content formats."""
        try:
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                # Handle list of content blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text" and "text" in block:
                            text_parts.append(block["text"])
                    elif isinstance(block, str):
                        text_parts.append(block)
                return " ".join(text_parts) if text_parts else None
            elif isinstance(content, dict):
                # Handle single content block
                if content.get("type") == "text" and "text" in content:
                    return content["text"]
            return None
        except Exception:
            return None

    async def _clean_message(self, message: Message) -> Message:
        """Clean individual message content."""
        try:
            content = message.content
            
            # Clean text content if it's a string
            if isinstance(content, str):
                cleaned_content = self._apply_cleaning_patterns(content)
                cleaned_message = message.model_copy()
                cleaned_message.content = cleaned_content
                return cleaned_message
            
            # Clean content blocks if it's a list
            elif isinstance(content, list):
                cleaned_blocks = []
                for block in content:
                    # Handle both dict and Pydantic model formats
                    if isinstance(block, dict) and block.get("type") == "text":
                        # Dictionary format
                        cleaned_text = self._apply_cleaning_patterns(block.get("text", ""))
                        cleaned_block = block.copy()
                        cleaned_block["text"] = cleaned_text
                        cleaned_blocks.append(cleaned_block)
                    elif hasattr(block, 'type') and block.type == "text":
                        # Pydantic model format
                        cleaned_text = self._apply_cleaning_patterns(getattr(block, 'text', ''))
                        cleaned_block = block.model_copy()
                        cleaned_block.text = cleaned_text
                        cleaned_blocks.append(cleaned_block)
                    else:
                        cleaned_blocks.append(block)
                
                cleaned_message = message.model_copy()
                cleaned_message.content = cleaned_blocks
                return cleaned_message
            
            # Return original message if no cleaning needed
            return message
            
        except Exception as e:
            logger.error(
                "Error cleaning individual message",
                error=str(e),
                exc_info=True
            )
            return message

    def _apply_cleaning_patterns(self, text: str) -> str:
        """Apply cleaning patterns to text content."""
        try:
            cleaned_text = text
            
            # Apply each cleaning pattern
            for pattern_name, pattern in self.cleaning_patterns.items():
                if pattern_name == "excessive_caps":
                    # Convert excessive caps to normal case
                    cleaned_text = re.sub(pattern, lambda m: m.group().lower(), cleaned_text)
                elif pattern_name == "repeated_chars":
                    # Reduce repeated characters to maximum of 2
                    cleaned_text = re.sub(pattern, r"\1\1", cleaned_text)
                elif pattern_name == "excessive_punctuation":
                    # Reduce excessive punctuation
                    cleaned_text = re.sub(pattern, "!", cleaned_text)
                elif pattern_name == "special_chars":
                    # Remove problematic special characters
                    cleaned_text = re.sub(pattern, "", cleaned_text)
            
            return cleaned_text.strip()
            
        except Exception:
            return text

    def _contains_excessive_caps(self, content: str) -> bool:
        """Check if content contains excessive capitalization."""
        caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        return caps_ratio > 0.7 and len(content) > 20

    def _contains_repeated_chars(self, content: str) -> bool:
        """Check if content contains excessive repeated characters."""
        return bool(re.search(r"(.)\1{5,}", content))