"""
Unit tests for Tool Detection Service.

Tests the tool detection functionality that replaces the TODO
implementation in the workflow tasks.
"""

import pytest
import json
from typing import List, Dict, Any
from unittest.mock import Mock, MagicMock

from src.services.tool_execution import ToolUseDetector


class TestToolUseDetector:
    """Test suite for ToolUseDetector service."""
    
    @pytest.fixture
    def detector(self):
        """Create a ToolUseDetector instance."""
        return ToolUseDetector()
    
    @pytest.fixture
    def anthropic_tool_response(self):
        """Create a mock response with Anthropic tool_use blocks."""
        choice = Mock()
        choice.message = Mock()
        choice.message.content = [
            {
                "type": "text",
                "text": "I'll help you with that task."
            },
            {
                "type": "tool_use",
                "id": "tool_123",
                "name": "write_file",
                "input": {
                    "path": "test.txt",
                    "content": "Hello World"
                }
            }
        ]
        choice.message.tool_calls = None  # No OpenAI tool calls
        choice.finish_reason = "tool_calls"
        
        response = Mock()
        response.choices = [choice]
        return response
    
    @pytest.fixture
    def openai_tool_response(self):
        """Create a mock response with OpenAI tool_calls format."""
        tool_call = Mock()
        tool_call.id = "call_123"
        tool_call.function = Mock()
        tool_call.function.name = "read_file"
        tool_call.function.arguments = json.dumps({"path": "example.txt"})
        
        choice = Mock()
        choice.message = Mock()
        choice.message.content = "I'll read that file for you."
        choice.message.tool_calls = [tool_call]
        choice.finish_reason = "tool_calls"
        
        response = Mock()
        response.choices = [choice]
        return response
    
    @pytest.fixture
    def no_tool_response(self):
        """Create a mock response with no tools."""
        choice = Mock()
        choice.message = Mock()
        choice.message.content = "This is a regular response without tools."
        choice.message.tool_calls = None
        choice.finish_reason = "stop"
        
        response = Mock()
        response.choices = [choice]
        return response
    
    @pytest.fixture
    def mixed_content_response(self):
        """Create a mock response with mixed content including tools."""
        choice = Mock()
        choice.message = Mock()
        choice.message.content = [
            {
                "type": "text",
                "text": "Let me search for that information."
            },
            {
                "type": "tool_use",
                "id": "search_123",
                "name": "web_search",
                "input": {
                    "query": "python tutorial",
                    "max_results": 5
                }
            },
            {
                "type": "text",
                "text": "And then I'll create a file with the results."
            },
            {
                "type": "tool_use",
                "id": "write_456",
                "name": "write_file",
                "input": {
                    "path": "results.txt",
                    "content": "Search results will go here"
                }
            }
        ]
        choice.message.tool_calls = None  # No OpenAI tool calls
        choice.finish_reason = "tool_calls"
        
        response = Mock()
        response.choices = [choice]
        return response

    def test_has_tool_use_blocks_anthropic_format(self, detector, anthropic_tool_response):
        """Test detection of Anthropic format tool_use blocks."""
        result = detector.has_tool_use_blocks(anthropic_tool_response)
        assert result is True

    def test_has_tool_use_blocks_openai_format(self, detector, openai_tool_response):
        """Test detection of OpenAI format tool_calls."""
        result = detector.has_tool_use_blocks(openai_tool_response)
        assert result is True

    def test_has_tool_use_blocks_no_tools(self, detector, no_tool_response):
        """Test detection when no tools are present."""
        result = detector.has_tool_use_blocks(no_tool_response)
        assert result is False

    def test_has_tool_use_blocks_mixed_content(self, detector, mixed_content_response):
        """Test detection with mixed content including tools."""
        result = detector.has_tool_use_blocks(mixed_content_response)
        assert result is True

    def test_has_tool_use_blocks_finish_reason_detection(self, detector):
        """Test detection based on finish_reason."""
        choice = Mock()
        choice.message = Mock()
        choice.message.content = "Regular text response"
        choice.message.tool_calls = None
        choice.finish_reason = "tool_calls"  # Indicates tools were called
        
        response = Mock()
        response.choices = [choice]
        
        result = detector.has_tool_use_blocks(response)
        # The detector should return False because there are no actual tool blocks,
        # even though finish_reason suggests tools were intended
        assert result is False

    def test_has_tool_use_blocks_empty_response(self, detector):
        """Test detection with empty or invalid response."""
        # Test with None
        result = detector.has_tool_use_blocks(None)
        assert result is False
        
        # Test with empty choices
        empty_response = Mock()
        empty_response.choices = []
        result = detector.has_tool_use_blocks(empty_response)
        assert result is False
        
        # Test with no choices attribute
        invalid_response = Mock()
        del invalid_response.choices
        result = detector.has_tool_use_blocks(invalid_response)
        assert result is False

    def test_extract_tool_use_blocks_anthropic_format(self, detector, anthropic_tool_response):
        """Test extraction of Anthropic format tool_use blocks."""
        result = detector.extract_tool_use_blocks(anthropic_tool_response)
        
        assert len(result) == 1
        tool_block = result[0]
        assert tool_block["type"] == "tool_use"
        assert tool_block["id"] == "tool_123"
        assert tool_block["name"] == "write_file"
        assert tool_block["input"]["path"] == "test.txt"
        assert tool_block["input"]["content"] == "Hello World"

    def test_extract_tool_use_blocks_openai_format(self, detector, openai_tool_response):
        """Test extraction and conversion of OpenAI format tool_calls."""
        result = detector.extract_tool_use_blocks(openai_tool_response)
        
        assert len(result) == 1
        tool_block = result[0]
        assert tool_block["type"] == "tool_use"
        assert tool_block["id"] == "call_123"
        assert tool_block["name"] == "read_file"
        assert tool_block["input"]["path"] == "example.txt"

    def test_extract_tool_use_blocks_mixed_content(self, detector, mixed_content_response):
        """Test extraction from mixed content with multiple tools."""
        result = detector.extract_tool_use_blocks(mixed_content_response)
        
        assert len(result) == 2
        
        # First tool
        search_tool = result[0]
        assert search_tool["type"] == "tool_use"
        assert search_tool["id"] == "search_123"
        assert search_tool["name"] == "web_search"
        assert search_tool["input"]["query"] == "python tutorial"
        
        # Second tool
        write_tool = result[1]
        assert write_tool["type"] == "tool_use"
        assert write_tool["id"] == "write_456"
        assert write_tool["name"] == "write_file"
        assert write_tool["input"]["path"] == "results.txt"

    def test_extract_tool_use_blocks_no_tools(self, detector, no_tool_response):
        """Test extraction when no tools are present."""
        result = detector.extract_tool_use_blocks(no_tool_response)
        assert len(result) == 0

    def test_extract_tool_use_blocks_malformed_openai(self, detector):
        """Test extraction with malformed OpenAI tool_calls."""
        # Create tool call with malformed arguments
        tool_call = Mock()
        tool_call.id = "call_456"
        tool_call.function = Mock()
        tool_call.function.name = "invalid_tool"
        tool_call.function.arguments = "invalid json {"  # Malformed JSON
        
        choice = Mock()
        choice.message = Mock()
        choice.message.content = "Response with malformed tool call"
        choice.message.tool_calls = [tool_call]
        
        response = Mock()
        response.choices = [choice]
        
        result = detector.extract_tool_use_blocks(response)
        
        # The current implementation logs the error and returns empty list
        # This is actually correct behavior for malformed input
        assert len(result) == 0

    def test_extract_tool_use_blocks_empty_openai_arguments(self, detector):
        """Test extraction with empty OpenAI arguments."""
        tool_call = Mock()
        tool_call.id = "call_789"
        tool_call.function = Mock()
        tool_call.function.name = "simple_tool"
        tool_call.function.arguments = None  # No arguments
        
        choice = Mock()
        choice.message = Mock()
        choice.message.content = "Response with no arguments"
        choice.message.tool_calls = [tool_call]
        
        response = Mock()
        response.choices = [choice]
        
        result = detector.extract_tool_use_blocks(response)
        
        assert len(result) == 1
        tool_block = result[0]
        assert tool_block["name"] == "simple_tool"
        assert tool_block["input"] == {}

    def test_extract_tool_use_blocks_complex_anthropic_content(self, detector):
        """Test extraction from complex Anthropic content structure."""
        choice = Mock()
        choice.message = Mock()
        choice.message.content = [
            {"type": "text", "text": "Starting analysis..."},
            {
                "type": "tool_use",
                "id": "analysis_001",
                "name": "grep_search",
                "input": {
                    "path": "logs/",
                    "pattern": "ERROR",
                    "case_sensitive": False,
                    "max_results": 10
                }
            },
            {"type": "text", "text": "Now let me check the file system..."},
            {
                "type": "tool_use",
                "id": "list_002",
                "name": "list_directory",
                "input": {
                    "path": "/var/log",
                    "recursive": True,
                    "long_format": True
                }
            },
            {"type": "text", "text": "Analysis complete."}
        ]
        choice.message.tool_calls = None  # No OpenAI tool calls
        
        response = Mock()
        response.choices = [choice]
        
        result = detector.extract_tool_use_blocks(response)
        
        assert len(result) == 2
        
        # Verify first tool
        grep_tool = result[0]
        assert grep_tool["name"] == "grep_search"
        assert grep_tool["input"]["pattern"] == "ERROR"
        assert grep_tool["input"]["case_sensitive"] is False
        
        # Verify second tool
        list_tool = result[1]
        assert list_tool["name"] == "list_directory"
        assert list_tool["input"]["recursive"] is True

    def test_extract_tool_use_blocks_both_formats_mixed(self, detector):
        """Test extraction when both Anthropic and OpenAI formats are present."""
        # Create OpenAI tool call
        tool_call = Mock()
        tool_call.id = "openai_123"
        tool_call.function = Mock()
        tool_call.function.name = "bash_command"
        tool_call.function.arguments = json.dumps({"command": "ls -la"})
        
        choice = Mock()
        choice.message = Mock()
        choice.message.content = [
            {
                "type": "tool_use",
                "id": "anthropic_456",
                "name": "read_file",
                "input": {"path": "config.txt"}
            }
        ]
        choice.message.tool_calls = [tool_call]
        
        response = Mock()
        response.choices = [choice]
        
        result = detector.extract_tool_use_blocks(response)
        
        # Should extract both tools
        assert len(result) == 2
        
        # Find tools by ID
        anthropic_tool = next(t for t in result if t["id"] == "anthropic_456")
        openai_tool = next(t for t in result if t["id"] == "openai_123")
        
        assert anthropic_tool["name"] == "read_file"
        assert openai_tool["name"] == "bash_command"

    def test_detection_error_handling(self, detector):
        """Test error handling in detection methods."""
        # Test with response that raises exceptions
        bad_response = Mock()
        bad_response.choices = Mock()
        bad_response.choices.__iter__ = Mock(side_effect=Exception("Test error"))
        
        # Should not raise exception and return False
        result = detector.has_tool_use_blocks(bad_response)
        assert result is False
        
        # Should not raise exception and return empty list
        result = detector.extract_tool_use_blocks(bad_response)
        assert result == []

    def test_detection_with_string_content(self, detector):
        """Test detection when content is a string instead of list."""
        choice = Mock()
        choice.message = Mock()
        choice.message.content = "This is just a string response"
        choice.message.tool_calls = None
        choice.finish_reason = "stop"
        
        response = Mock()
        response.choices = [choice]
        
        result = detector.has_tool_use_blocks(response)
        assert result is False
        
        result = detector.extract_tool_use_blocks(response)
        assert len(result) == 0

    def test_detection_performance_with_large_content(self, detector):
        """Test detection performance with large content blocks."""
        # Create a response with many content blocks
        large_content = []
        for i in range(100):
            large_content.append({"type": "text", "text": f"Text block {i}"})
        
        # Add one tool use block at the end
        large_content.append({
            "type": "tool_use",
            "id": "final_tool",
            "name": "summary_tool",
            "input": {"count": 100}
        })
        
        choice = Mock()
        choice.message = Mock()
        choice.message.content = large_content
        choice.message.tool_calls = None  # No OpenAI tool calls
        
        response = Mock()
        response.choices = [choice]
        
        # Should still detect the tool efficiently
        result = detector.has_tool_use_blocks(response)
        assert result is True
        
        extracted = detector.extract_tool_use_blocks(response)
        assert len(extracted) == 1
        assert extracted[0]["name"] == "summary_tool"

    def test_detection_with_nested_tool_data(self, detector):
        """Test detection with complex nested tool input data."""
        choice = Mock()
        choice.message = Mock()
        choice.message.content = [
            {
                "type": "tool_use",
                "id": "complex_tool",
                "name": "multi_edit_file",
                "input": {
                    "path": "config.json",
                    "edits": [
                        {
                            "old_str": "old_value_1",
                            "new_str": "new_value_1"
                        },
                        {
                            "old_str": "old_value_2",
                            "new_str": "new_value_2"
                        }
                    ],
                    "metadata": {
                        "version": "1.0",
                        "author": "test_user",
                        "nested": {
                            "deep": "value"
                        }
                    }
                }
            }
        ]
        choice.message.tool_calls = None  # No OpenAI tool calls
        
        response = Mock()
        response.choices = [choice]
        
        result = detector.extract_tool_use_blocks(response)
        assert len(result) == 1
        
        tool = result[0]
        assert tool["name"] == "multi_edit_file"
        assert len(tool["input"]["edits"]) == 2
        assert tool["input"]["metadata"]["nested"]["deep"] == "value"