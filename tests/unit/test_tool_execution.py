"""Unit tests for tool execution service - Phase 1 infrastructure."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from src.services.tool_execution import (
    ToolExecutionService,
    ToolRegistry,
    ToolUseDetector,
    ToolExecutionResult,
    ToolResultFormatter,
    ConversationContinuation
)
from src.models.anthropic import MessagesRequest, Message


class TestToolExecutionResult:
    """Test ToolExecutionResult dataclass"""
    
    def test_successful_result(self):
        """Test successful tool execution result"""
        result = ToolExecutionResult(
            tool_call_id="test_id",
            tool_name="Write",
            success=True,
            result="File created successfully",
            execution_time=0.1
        )
        
        assert result.tool_call_id == "test_id"
        assert result.tool_name == "Write"
        assert result.success is True
        assert result.result == "File created successfully"
        assert result.error is None
        assert result.execution_time == 0.1
    
    def test_failed_result(self):
        """Test failed tool execution result"""
        result = ToolExecutionResult(
            tool_call_id="test_id",
            tool_name="Read",
            success=False,
            result=None,
            error="File not found",
            execution_time=0.05
        )
        
        assert result.tool_call_id == "test_id"
        assert result.tool_name == "Read"
        assert result.success is False
        assert result.result is None
        assert result.error == "File not found"


class TestToolResultFormatter:
    """Test ToolResultFormatter"""
    
    def test_create_tool_result_block_success(self):
        """Test creating tool_result block for successful execution"""
        result = ToolExecutionResult(
            tool_call_id="test_123",
            tool_name="Write",
            success=True,
            result="File created: logs/test_files/test.py"
        )
        
        formatter = ToolResultFormatter()
        block = formatter.create_tool_result_block(result)
        
        assert block["type"] == "tool_result"
        assert block["tool_use_id"] == "test_123"
        assert block["content"] == "File created: logs/test_files/test.py"
    
    def test_create_tool_result_block_error(self):
        """Test creating tool_result block for failed execution"""
        result = ToolExecutionResult(
            tool_call_id="test_456",
            tool_name="Read",
            success=False,
            result=None,
            error="Permission denied"
        )
        
        formatter = ToolResultFormatter()
        block = formatter.create_tool_result_block(result)
        
        assert block["type"] == "tool_result"
        assert block["tool_use_id"] == "test_456"
        assert block["content"] == "Error: Permission denied"
    
    def test_format_result_content_types(self):
        """Test formatting different result content types"""
        formatter = ToolResultFormatter()
        
        # Test dict result
        dict_result = ToolExecutionResult("id", "test", True, {"key": "value"})
        content = formatter._format_result_content(dict_result)
        assert "key" in content and "value" in content
        
        # Test list result
        list_result = ToolExecutionResult("id", "test", True, ["item1", "item2"])
        content = formatter._format_result_content(list_result)
        assert "item1" in content and "item2" in content
        
        # Test None result
        none_result = ToolExecutionResult("id", "test", True, None)
        content = formatter._format_result_content(none_result)
        assert "Tool executed successfully" in content


class TestToolRegistry:
    """Test ToolRegistry"""
    
    def test_initialization(self):
        """Test tool registry initialization"""
        registry = ToolRegistry()
        
        # Check that all expected tools are registered
        expected_tools = [
            "Write", "Read", "Edit", "MultiEdit",
            "Glob", "Grep", "LS",
            "Bash", "Task",
            "WebSearch", "WebFetch",
            "NotebookRead", "NotebookEdit",
            "TodoRead", "TodoWrite"
        ]
        
        available_tools = registry.get_available_tools()
        for tool in expected_tools:
            assert tool in available_tools
    
    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self):
        """Test executing unknown tool"""
        registry = ToolRegistry()
        
        result = await registry.execute_tool("test_id", "UnknownTool", {})
        
        assert result.success is False
        assert "No flow found for tool" in result.error
        assert result.tool_name == "UnknownTool"
    
    @pytest.mark.asyncio
    async def test_execute_placeholder_tool(self):
        """Test executing WebSearch tool (now fully implemented)"""
        registry = ToolRegistry()
        
        # Test WebSearch tool (now fully implemented in production)
        result = await registry.execute_tool("test_id", "WebSearch", {"query": "test"})
        
        # WebSearch is now fully implemented and should succeed
        assert result.success is True
        assert result.tool_name == "WebSearch"
        assert "test" in result.result.lower() or len(result.result) > 0


class TestToolUseDetector:
    """Test ToolUseDetector"""
    
    def test_has_tool_use_blocks_anthropic_format(self):
        """Test detecting tool_use blocks in Anthropic format"""
        # Mock response with tool_use blocks
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = [
            {"type": "text", "text": "I'll help you create a file."},
            {"type": "tool_use", "id": "test_123", "name": "Write", "input": {"file_path": "logs/test_files/test.py"}}
        ]
        
        detector = ToolUseDetector()
        result = detector.has_tool_use_blocks(mock_response)
        
        assert result is True
    
    def test_has_tool_use_blocks_openai_format(self):
        """Test detecting tool_calls in OpenAI format"""
        # Mock response with tool_calls
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "I'll help you with that."
        mock_response.choices[0].message.tool_calls = [
            Mock(id="test_123", function=Mock(name="Write", arguments='{"file_path": "logs/test_files/test.py"}'))
        ]
        
        detector = ToolUseDetector()
        result = detector.has_tool_use_blocks(mock_response)
        
        assert result is True
    
    def test_has_tool_use_blocks_none(self):
        """Test when no tool_use blocks present"""
        # Mock response without tool_use
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Here's your answer."
        mock_response.choices[0].message.tool_calls = None
        
        detector = ToolUseDetector()
        result = detector.has_tool_use_blocks(mock_response)
        
        assert result is False
    
    def test_extract_tool_use_blocks_anthropic(self):
        """Test extracting tool_use blocks from Anthropic format"""
        # Mock response with tool_use blocks
        mock_response = Mock()
        
        # Create mock choice with proper message
        mock_choice = Mock()
        mock_message = Mock()
        
        # Make content properly iterable
        content_list = [
            {"type": "text", "text": "I'll create the file."},
            {"type": "tool_use", "id": "test_123", "name": "Write", "input": {"file_path": "logs/test_files/test.py", "content": "print('hello')"}}
        ]
        mock_message.content = content_list
        
        # Ensure tool_calls is None to avoid the Mock len() issue
        mock_message.tool_calls = None
        
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        detector = ToolUseDetector()
        blocks = detector.extract_tool_use_blocks(mock_response)
        
        assert len(blocks) == 1
        assert blocks[0]["type"] == "tool_use"
        assert blocks[0]["id"] == "test_123"
        assert blocks[0]["name"] == "Write"
        assert blocks[0]["input"]["file_path"] == "logs/test_files/test.py"
    
    def test_extract_tool_use_blocks_openai(self):
        """Test extracting tool_calls from OpenAI format"""
        # Mock response with tool_calls - fix the function mock
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "I'll help you."
        
        # Properly mock the function object
        mock_function = Mock()
        mock_function.name = "Read"
        mock_function.arguments = '{"file_path": "logs/test_files/test.py"}'
        
        mock_tool_call = Mock()
        mock_tool_call.id = "test_456"
        mock_tool_call.function = mock_function
        
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        
        detector = ToolUseDetector()
        blocks = detector.extract_tool_use_blocks(mock_response)
        
        assert len(blocks) == 1
        assert blocks[0]["type"] == "tool_use"
        assert blocks[0]["id"] == "test_456"
        assert blocks[0]["name"] == "Read"
        assert blocks[0]["input"]["file_path"] == "logs/test_files/test.py"


class TestToolExecutionService:
    """Test ToolExecutionService - Phase 1 functionality"""
    
    def test_initialization(self):
        """Test service initialization"""
        service = ToolExecutionService()
        
        assert service.registry is not None
        assert service.detector is not None
        assert service.http_client is not None
        assert service.continuation is not None
        assert service.max_concurrent_tools > 0
        assert service.execution_timeout > 0
    
    @pytest.mark.asyncio
    async def test_execute_tools_placeholder(self):
        """Test executing all tools (now all implemented)"""
        service = ToolExecutionService()
        
        # Test file operation tool (should work)
        file_tool_blocks = [
            {
                "type": "tool_use",
                "id": "test_123",
                "name": "Write",
                "input": {"file_path": "logs/test_files/test.py", "content": "print('hello')"}
            }
        ]
        
        file_results = await service._execute_tools(file_tool_blocks, "test_request_id")
        
        assert len(file_results) == 1
        assert file_results[0].tool_call_id == "test_123"
        assert file_results[0].tool_name == "Write"
        assert file_results[0].success is True  # File tools work
        
        # Test web operation tool (now also implemented)
        web_tool_blocks = [
            {
                "type": "tool_use", 
                "id": "test_456",
                "name": "WebSearch",
                "input": {"query": "test search"}
            }
        ]
        
        web_results = await service._execute_tools(web_tool_blocks, "test_request_id")
        
        assert len(web_results) == 1
        assert web_results[0].tool_call_id == "test_456"
        assert web_results[0].tool_name == "WebSearch"
        assert web_results[0].success is True  # WebSearch now works
    
    @pytest.mark.asyncio
    async def test_execute_multiple_tools(self):
        """Test executing multiple tools concurrently (all now implemented)"""
        service = ToolExecutionService()
        
        tool_use_blocks = [
            {"type": "tool_use", "id": "test_1", "name": "Write", "input": {"file_path": "logs/test_files/test1.py", "content": "print('test1')"}},  # File operation
            {"type": "tool_use", "id": "test_2", "name": "Read", "input": {"file_path": "logs/test_files/nonexistent.txt"}},  # File operation (will fail - file doesn't exist)
            {"type": "tool_use", "id": "test_3", "name": "WebSearch", "input": {"query": "test"}}  # Web operation (now implemented)
        ]
        
        results = await service._execute_tools(tool_use_blocks, "test_request_id")
        
        assert len(results) == 3
        assert {result.tool_call_id for result in results} == {"test_1", "test_2", "test_3"}
        
        # Check individual results
        write_result = next(r for r in results if r.tool_name == "Write")
        read_result = next(r for r in results if r.tool_name == "Read")
        websearch_result = next(r for r in results if r.tool_name == "WebSearch")
        
        assert write_result.success is True  # Write should work
        assert read_result.success is False  # Read should fail (file doesn't exist)
        assert websearch_result.success is True  # WebSearch now works


@pytest.mark.asyncio
class TestToolExecutionMetrics:
    """Test tool execution metrics and rate limiting"""
    
    async def test_metrics_tracking(self):
        """Test that metrics are properly tracked"""
        service = ToolExecutionService()
        
        # Simulate successful execution
        success_result = ToolExecutionResult(
            tool_call_id="test_1",
            tool_name="TestTool",
            success=True,
            result="Success",
            execution_time=0.5
        )
        service._update_metrics(success_result)
        
        # Simulate failed execution
        fail_result = ToolExecutionResult(
            tool_call_id="test_2",
            tool_name="TestTool",
            success=False,
            result=None,
            error="Test error: failed",
            execution_time=0.1
        )
        service._update_metrics(fail_result)
        
        # Check metrics
        metrics = service.get_metrics()
        
        assert metrics['total_executions'] == 2
        assert metrics['successful_executions'] == 1
        assert metrics['failed_executions'] == 1
        assert metrics['success_rate'] == 0.5
        assert 'TestTool' in metrics['tool_usage_count']
        assert metrics['tool_usage_count']['TestTool'] == 2
        assert 'Test error' in metrics['error_breakdown']
    
    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        service = ToolExecutionService()
        service.rate_limit_max_requests = 5
        service.rate_limit_window = 60
        
        # First 5 requests should succeed
        for i in range(5):
            assert service._check_rate_limit(f"request_{i}") is True
        
        # 6th request should fail
        assert service._check_rate_limit("request_6") is False
        
        # Clear old entries (simulate time passing)
        service.rate_limit_tracker = {}
        
        # Should work again
        assert service._check_rate_limit("request_7") is True
    
    async def test_concurrent_execution_tracking(self):
        """Test concurrent execution metrics"""
        service = ToolExecutionService()
        
        # Mock tool blocks
        tool_blocks = [
            {"id": "tool_1", "name": "Write", "input": {"file_path": "logs/test_files/test1.txt", "content": "test"}},
            {"id": "tool_2", "name": "Read", "input": {"file_path": "logs/test_files/test1.txt"}},
        ]
        
        # Mock the registry to return quick results
        async def mock_execute(tool_call_id, tool_name, tool_input):
            await asyncio.sleep(0.01)  # Simulate quick execution
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=True,
                result="Mocked result",
                execution_time=0.01
            )
        
        service.registry.execute_tool = mock_execute
        
        # Execute tools
        results = await service._execute_tools(tool_blocks, "test_request")
        
        # Check results
        assert len(results) == 2
        assert all(r.success for r in results)
        
        # Check metrics
        assert service.metrics['max_concurrent_executions'] >= 1
    
    async def test_metrics_cleanup(self):
        """Test that execution time metrics are limited to 100 entries"""
        service = ToolExecutionService()
        
        # Add 150 execution times for a tool
        for i in range(150):
            result = ToolExecutionResult(
                tool_call_id=f"test_{i}",
                tool_name="TestTool",
                success=True,
                result="Success",
                execution_time=i * 0.01
            )
            service._update_metrics(result)
        
        # Check that only last 100 are kept
        assert len(service.metrics['execution_times']['TestTool']) == 100
        
        # Verify it's the last 100 (highest times)
        times = service.metrics['execution_times']['TestTool']
        assert times[0] == 0.5  # 50th execution (0-indexed)
        assert times[-1] == 1.49  # 149th execution


if __name__ == "__main__":
    pytest.main([__file__]) 