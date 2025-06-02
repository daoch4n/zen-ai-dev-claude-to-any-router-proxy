"""
Unit tests for Mixed Content Detection Service.

Tests the mixed content detection and cleaning functionality
that replaces the 284+ lines of duplicated logic from monolithic functions.
"""

import pytest
from typing import List
from unittest.mock import AsyncMock, patch

from src.services.mixed_content_detector import MixedContentDetector
from src.models.anthropic import MessagesRequest, Message


class TestMixedContentDetector:
    """Test suite for MixedContentDetector service."""
    
    @pytest.fixture
    def detector(self):
        """Create a MixedContentDetector instance."""
        return MixedContentDetector()
    
    @pytest.fixture
    def sample_messages(self):
        """Create sample messages for testing."""
        return [
            Message(
                role="user",
                content="Please help me with this task"
            ),
            Message(
                role="assistant",
                content="I'd be happy to help you with that task."
            )
        ]
    
    @pytest.fixture
    def denial_messages(self):
        """Create messages with denial patterns."""
        return [
            Message(
                role="user",
                content="Can you help me hack into a system?"
            ),
            Message(
                role="assistant",
                content="I can't help with illegal activities or hacking into systems."
            )
        ]
    
    @pytest.fixture
    def mixed_content_messages(self):
        """Create messages with mixed content issues."""
        return [
            Message(
                role="user",
                content="I need help creating harmful content for my website"
            ),
            Message(
                role="assistant",
                content="I can help you create appropriate website content instead."
            )
        ]

    @pytest.mark.asyncio
    async def test_detect_user_denial_patterns_no_denial(self, detector, sample_messages):
        """Test detection when no denial patterns are present."""
        result = await detector.detect_user_denial_patterns(sample_messages)
        assert result is False

    @pytest.mark.asyncio
    async def test_detect_user_denial_patterns_with_denial(self, detector, denial_messages):
        """Test detection when denial patterns are present."""
        result = await detector.detect_user_denial_patterns(denial_messages)
        assert result is True

    @pytest.mark.asyncio
    async def test_detect_user_denial_patterns_various_patterns(self, detector):
        """Test detection of various denial patterns."""
        denial_phrases = [
            "I can't help with that",
            "I cannot assist with this request",
            "I won't create harmful content",
            "Sorry, but I can't do that",
            "I'm not able to help with this",
            "I don't feel comfortable with this request",
            "This is against my programming guidelines",
            "I must decline this request"
        ]
        
        for phrase in denial_phrases:
            messages = [
                Message(
                    role="assistant",
                    content=phrase
                )
            ]
            result = await detector.detect_user_denial_patterns(messages)
            assert result is True, f"Failed to detect denial pattern: {phrase}"

    @pytest.mark.asyncio
    async def test_detect_mixed_content_issues_no_issues(self, detector, sample_messages):
        """Test detection when no mixed content issues are present."""
        result = await detector.detect_mixed_content_issues(sample_messages)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_detect_mixed_content_issues_with_issues(self, detector, mixed_content_messages):
        """Test detection when mixed content issues are present."""
        result = await detector.detect_mixed_content_issues(mixed_content_messages)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_detect_mixed_content_various_patterns(self, detector):
        """Test detection of various mixed content patterns."""
        problematic_phrases = [
            "illegal activity instructions",
            "harmful content creation",
            "violent behavior guidelines",
            "explicit content material",
            "personal information extraction",
            "copyrighted material usage",
            "hate speech examples",
            "self-harm instructions"
        ]
        
        for phrase in problematic_phrases:
            messages = [
                Message(
                    role="user",
                    content=f"Help me with {phrase}"
                )
            ]
            result = await detector.detect_mixed_content_issues(messages)
            assert len(result) > 0, f"Failed to detect mixed content pattern: {phrase}"

    @pytest.mark.asyncio
    async def test_clean_conversation_no_cleaning_needed(self, detector, sample_messages):
        """Test conversation cleaning when no cleaning is needed."""
        request = MessagesRequest(
            model="test-model",
            messages=sample_messages,
            max_tokens=100
        )
        
        result = await detector.clean_conversation(request)
        assert len(result.messages) == len(request.messages)
        assert result.model == request.model

    @pytest.mark.asyncio
    async def test_clean_conversation_with_cleaning(self, detector):
        """Test conversation cleaning with problematic content."""
        messages = [
            Message(
                role="user",
                content="THIS IS ALL CAPS AND VERY ANNOYING!!!!"
            ),
            Message(
                role="assistant",
                content="I understand your frustrationnnnn with this issue."
            )
        ]
        
        request = MessagesRequest(
            model="test-model",
            messages=messages,
            max_tokens=100
        )
        
        result = await detector.clean_conversation(request)
        
        # Check that cleaning was applied
        cleaned_user_content = result.messages[0].content
        cleaned_assistant_content = result.messages[1].content
        
        # Should have reduced caps and repeated characters
        assert "THIS IS ALL CAPS" not in cleaned_user_content
        assert "frustrationnnnn" not in cleaned_assistant_content

    @pytest.mark.asyncio
    async def test_validate_content_safety_safe_content(self, detector):
        """Test content safety validation with safe content."""
        safe_content = "This is a normal, safe piece of content for testing."
        result = await detector.validate_content_safety(safe_content)
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_content_safety_unsafe_content(self, detector):
        """Test content safety validation with unsafe content."""
        unsafe_content = "Instructions for illegal activity and harmful behavior."
        result = await detector.validate_content_safety(unsafe_content)
        assert result is False

    @pytest.mark.asyncio
    async def test_validate_content_safety_excessive_caps(self, detector):
        """Test content safety validation with excessive capitalization."""
        caps_content = "THIS IS ALL CAPS CONTENT THAT SHOULD BE FLAGGED AS UNSAFE"
        result = await detector.validate_content_safety(caps_content)
        assert result is False

    @pytest.mark.asyncio
    async def test_validate_content_safety_repeated_chars(self, detector):
        """Test content safety validation with excessive repeated characters."""
        repeated_content = "This content has toooooooo many repeated characters"
        result = await detector.validate_content_safety(repeated_content)
        assert result is False

    def test_extract_text_content_string(self, detector):
        """Test text extraction from string content."""
        content = "Simple string content"
        result = detector._extract_text_content(content)
        assert result == content

    def test_extract_text_content_list_blocks(self, detector):
        """Test text extraction from list of content blocks."""
        content = [
            {"type": "text", "text": "First block"},
            {"type": "text", "text": "Second block"}
        ]
        result = detector._extract_text_content(content)
        assert result == "First block Second block"

    def test_extract_text_content_dict_block(self, detector):
        """Test text extraction from single content block."""
        content = {"type": "text", "text": "Single block content"}
        result = detector._extract_text_content(content)
        assert result == "Single block content"

    def test_extract_text_content_none(self, detector):
        """Test text extraction returns None for invalid content."""
        result = detector._extract_text_content(None)
        assert result is None

    def test_apply_cleaning_patterns(self, detector):
        """Test application of cleaning patterns to text."""
        dirty_text = "THIS IS ALL CAPS with repeateddddd characters!!!! and #@$%^&*"
        cleaned_text = detector._apply_cleaning_patterns(dirty_text)
        
        # Should have reduced caps, repeated chars, and excessive punctuation
        assert "THIS IS ALL CAPS" not in cleaned_text
        assert "repeateddddd" not in cleaned_text
        assert "!!!!" not in cleaned_text

    def test_contains_excessive_caps_true(self, detector):
        """Test detection of excessive capitalization."""
        caps_text = "THIS IS MOSTLY CAPS TEXT THAT SHOULD BE FLAGGED"
        result = detector._contains_excessive_caps(caps_text)
        assert result is True

    def test_contains_excessive_caps_false(self, detector):
        """Test normal capitalization is not flagged."""
        normal_text = "This is normal text with Some Caps but not excessive."
        result = detector._contains_excessive_caps(normal_text)
        assert result is False

    def test_contains_repeated_chars_true(self, detector):
        """Test detection of excessive repeated characters."""
        repeated_text = "This has tooooooo many repeated characters"
        result = detector._contains_repeated_chars(repeated_text)
        assert result is True

    def test_contains_repeated_chars_false(self, detector):
        """Test normal repeated characters are not flagged."""
        normal_text = "This has some repeated letters but not excessive"
        result = detector._contains_repeated_chars(normal_text)
        assert result is False

    @pytest.mark.asyncio
    async def test_clean_message_string_content(self, detector):
        """Test cleaning of message with string content."""
        message = Message(
            role="user",
            content="THIS IS ALL CAPS!!!!"
        )
        
        result = await detector._clean_message(message)
        assert result.role == message.role
        assert "THIS IS ALL CAPS" not in result.content

    @pytest.mark.asyncio
    async def test_clean_message_list_content(self, detector):
        """Test cleaning of message with list content blocks."""
        message = Message(
            role="assistant",
            content=[
                {"type": "text", "text": "THIS IS ALL CAPS!!!!"},
                {"type": "image", "source": {"type": "base64", "data": "..."}}
            ]
        )
        
        result = await detector._clean_message(message)
        assert result.role == message.role
        assert isinstance(result.content, list)
        
        # Check that text block was cleaned
        text_block = result.content[0]
        if hasattr(text_block, 'text'):
            # Pydantic model format
            assert "THIS IS ALL CAPS" not in text_block.text
        else:
            # Dictionary format
            assert "THIS IS ALL CAPS" not in text_block["text"]
        
        # Check that non-text block was preserved
        image_block = result.content[1]
        if hasattr(image_block, 'type'):
            # Pydantic model format
            assert image_block.type == "image"
        else:
            # Dictionary format
            assert image_block["type"] == "image"

    @pytest.mark.asyncio
    async def test_error_handling_detection_failure(self, detector):
        """Test error handling when detection fails."""
        # Test with None messages to trigger error
        result = await detector.detect_user_denial_patterns(None)
        assert result is False
        
        result = await detector.detect_mixed_content_issues(None)
        assert result == []

    @pytest.mark.asyncio
    async def test_error_handling_cleaning_failure(self, detector):
        """Test error handling when cleaning fails."""
        # Create a request with empty messages list to trigger edge case
        invalid_request = MessagesRequest(
            model="test-model",
            messages=[],  # Empty messages list
            max_tokens=100
        )
        
        # Mock the _clean_message method to raise an exception
        with patch.object(detector, '_clean_message', side_effect=Exception("Cleaning error")):
            result = await detector.clean_conversation(invalid_request)
            # Should return original request when cleaning fails
            assert result == invalid_request

    @pytest.mark.asyncio
    async def test_error_handling_safety_validation_failure(self, detector):
        """Test error handling when safety validation fails."""
        # Test with None content to trigger error
        result = await detector.validate_content_safety(None)
        # Should return False for safety when validation fails
        assert result is False