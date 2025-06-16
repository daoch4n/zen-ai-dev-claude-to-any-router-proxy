"""Test suite for image content conversion between Anthropic and OpenAI formats."""

import pytest
import base64
from unittest.mock import patch

from src.tasks.conversion.content_conversion_tasks import (
    convert_image_content_anthropic_to_openai,
    convert_image_content_openai_to_anthropic,
    convert_content_blocks_anthropic_to_openai,
    convert_content_blocks_openai_to_anthropic
)


class TestImageContentConversion:
    """Test image content conversion functions."""

    @pytest.fixture
    def sample_image_data(self):
        """Sample base64 image data for testing."""
        # Small 1x1 pixel PNG image encoded in base64
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAHGbYJYUgAAAABJRU5ErkJggg=="

    @pytest.fixture 
    def anthropic_image_block(self, sample_image_data):
        """Sample Anthropic image block."""
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": sample_image_data
            }
        }

    @pytest.fixture
    def openai_image_block(self, sample_image_data):
        """Sample OpenAI image block."""
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{sample_image_data}"
            }
        }

    def test_convert_anthropic_image_to_openai_success(self, anthropic_image_block, sample_image_data):
        """Test successful conversion from Anthropic to OpenAI format."""
        result = convert_image_content_anthropic_to_openai(anthropic_image_block)
        
        assert result["type"] == "image_url"
        assert "image_url" in result
        assert result["image_url"]["url"] == f"data:image/jpeg;base64,{sample_image_data}"

    def test_convert_anthropic_image_to_openai_png(self, sample_image_data):
        """Test conversion with PNG media type."""
        anthropic_block = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": sample_image_data
            }
        }
        
        result = convert_image_content_anthropic_to_openai(anthropic_block)
        
        assert result["type"] == "image_url"
        assert result["image_url"]["url"] == f"data:image/png;base64,{sample_image_data}"

    def test_convert_anthropic_image_empty_data(self):
        """Test handling of empty image data."""
        anthropic_block = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": ""
            }
        }
        
        result = convert_image_content_anthropic_to_openai(anthropic_block)
        
        assert result["type"] == "text"
        assert result["text"] == "[Empty image content]"

    def test_convert_anthropic_image_unsupported_source(self):
        """Test handling of unsupported source type."""
        anthropic_block = {
            "type": "image",
            "source": {
                "type": "url",
                "url": "https://example.com/image.jpg"
            }
        }
        
        result = convert_image_content_anthropic_to_openai(anthropic_block)
        
        assert result["type"] == "text"
        assert "Unsupported image source: url" in result["text"]

    def test_convert_anthropic_image_malformed_block(self):
        """Test handling of malformed image block."""
        malformed_block = {
            "type": "image"
            # Missing source
        }
        
        result = convert_image_content_anthropic_to_openai(malformed_block)
        
        assert result["type"] == "text"
        assert "Unsupported image source: unknown" in result["text"]

    def test_convert_openai_image_to_anthropic_success(self, openai_image_block, sample_image_data):
        """Test successful conversion from OpenAI to Anthropic format."""
        result = convert_image_content_openai_to_anthropic(openai_image_block)
        
        assert result["type"] == "image"
        assert "source" in result
        assert result["source"]["type"] == "base64"
        assert result["source"]["media_type"] == "image/jpeg"
        assert result["source"]["data"] == sample_image_data

    def test_convert_openai_image_to_anthropic_png(self, sample_image_data):
        """Test conversion with PNG media type from OpenAI."""
        openai_block = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{sample_image_data}"
            }
        }
        
        result = convert_image_content_openai_to_anthropic(openai_block)
        
        assert result["type"] == "image"
        assert result["source"]["media_type"] == "image/png"
        assert result["source"]["data"] == sample_image_data

    def test_convert_openai_image_empty_url(self):
        """Test handling of empty image URL."""
        openai_block = {
            "type": "image_url",
            "image_url": {
                "url": ""
            }
        }
        
        result = convert_image_content_openai_to_anthropic(openai_block)
        
        assert result["type"] == "text"
        assert result["text"] == "[Empty image URL]"

    def test_convert_openai_image_external_url(self):
        """Test handling of external URLs (not data URLs)."""
        openai_block = {
            "type": "image_url",
            "image_url": {
                "url": "https://example.com/image.jpg"
            }
        }
        
        result = convert_image_content_openai_to_anthropic(openai_block)
        
        assert result["type"] == "text"
        assert "External image URL not supported" in result["text"]

    def test_convert_openai_image_malformed_data_url(self):
        """Test handling of malformed data URL."""
        openai_block = {
            "type": "image_url",
            "image_url": {
                "url": "data:image/jpeg"  # Missing ;base64,data part
            }
        }
        
        result = convert_image_content_openai_to_anthropic(openai_block)
        
        assert result["type"] == "text"
        assert "Invalid image data URL" in result["text"]


class TestContentBlocksConversion:
    """Test content blocks conversion functions."""

    @pytest.fixture
    def sample_image_data(self):
        """Sample base64 image data for testing."""
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAHGbYJYUgAAAABJRU5ErkJggg=="

    def test_convert_anthropic_content_blocks_mixed(self, sample_image_data):
        """Test conversion of mixed content blocks from Anthropic."""
        anthropic_blocks = [
            {"type": "text", "text": "Here's an image:"},
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": sample_image_data
                }
            },
            {"type": "text", "text": "What do you see?"}
        ]
        
        result = convert_content_blocks_anthropic_to_openai(anthropic_blocks)
        
        assert len(result) == 3
        assert result[0]["type"] == "text"
        assert result[0]["text"] == "Here's an image:"
        
        assert result[1]["type"] == "image_url"
        assert f"data:image/jpeg;base64,{sample_image_data}" in result[1]["image_url"]["url"]
        
        assert result[2]["type"] == "text"
        assert result[2]["text"] == "What do you see?"

    def test_round_trip_conversion(self, sample_image_data):
        """Test round-trip conversion maintains data integrity."""
        # Start with Anthropic format
        original_anthropic = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": sample_image_data
            }
        }
        
        # Convert to OpenAI
        openai_format = convert_image_content_anthropic_to_openai(original_anthropic)
        
        # Convert back to Anthropic
        back_to_anthropic = convert_image_content_openai_to_anthropic(openai_format)
        
        # Verify data integrity
        assert back_to_anthropic["type"] == "image"
        assert back_to_anthropic["source"]["type"] == "base64"
        assert back_to_anthropic["source"]["media_type"] == "image/png"
        assert back_to_anthropic["source"]["data"] == sample_image_data 