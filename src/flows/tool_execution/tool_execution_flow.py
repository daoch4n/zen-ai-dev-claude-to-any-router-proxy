"""Tool execution orchestration flow."""

import asyncio
from typing import Any, Dict, List
from ...tasks.tool_execution.tool_detection_tasks import (
    detect_tool_use_blocks,
    extract_tool_use_blocks,
    check_tools_need_confirmation
)
from ...tasks.tool_execution.tool_execution_tasks import (
    execute_single_tool_with_timeout,
    ToolExecutionError
)
from ...tasks.tool_execution.tool_result_formatting_tasks import ToolExecutionResult
from ...tasks.tool_execution.metrics_tasks import (
    update_tool_execution_metrics,
    check_rate_limit,
    track_concurrent_execution
)
from ...core.logging_config import get_logger

logger = get_logger("tool_execution.flow")


class ToolExecutionFlow:
    """Handles the complete tool execution workflow"""
    
    def __init__(self, 
                 max_concurrent_tools: int = 5,
                 execution_timeout: float = 30.0,
                 rate_limit_window: float = 60.0,
                 rate_limit_max_requests: int = 100):
        """Initialize tool execution flow"""
        self.max_concurrent_tools = max_concurrent_tools
        self.execution_timeout = execution_timeout
        self.rate_limit_window = rate_limit_window
        self.rate_limit_max_requests = rate_limit_max_requests
        
        # Rate limiting tracker
        self.rate_limit_tracker = {}
        
        # Metrics
        self.metrics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'execution_times': {},
            'tool_usage_count': {},
            'error_count_by_type': {},
            'concurrent_executions': 0,
            'max_concurrent_executions': 0
        }
        
        logger.info("ToolExecutionFlow initialized",
                   max_concurrent=max_concurrent_tools,
                   timeout=execution_timeout)
    
    def has_tool_use_blocks(self, response: Any) -> bool:
        """Check if response contains tool_use blocks"""
        return detect_tool_use_blocks(response)
    
    async def should_execute_tools(self, response: Any) -> bool:
        """Determine if tools should be executed"""
        if not self.has_tool_use_blocks(response):
            return False
        
        # Extract tool blocks to check for confirmation requirements
        tool_use_blocks = extract_tool_use_blocks(response)
        if not tool_use_blocks:
            return False
        
        # Check if any tools need user confirmation
        requires_confirmation = await check_tools_need_confirmation(tool_use_blocks)
        if requires_confirmation:
            logger.info("Tools require user confirmation, skipping execution")
            return False
        
        return True
    
    async def execute_tools_from_response(self, response: Any, request_id: str) -> List[ToolExecutionResult]:
        """Execute all tools from a response"""
        # Check rate limit
        if not check_rate_limit(
            self.rate_limit_tracker,
            request_id,
            self.rate_limit_window,
            self.rate_limit_max_requests
        ):
            raise ToolExecutionError("Rate limit exceeded for tool execution")
        
        # Extract tool blocks
        tool_use_blocks = extract_tool_use_blocks(response)
        if not tool_use_blocks:
            logger.warning("No tool_use blocks found in response")
            return []
        
        logger.info("Found tools to execute", tool_count=len(tool_use_blocks))
        
        # Execute tools concurrently
        return await self._execute_tools_concurrently(tool_use_blocks, request_id)
    
    async def _execute_tools_concurrently(self, tool_use_blocks: List[Dict[str, Any]], request_id: str) -> List[ToolExecutionResult]:
        """Execute all tools concurrently with semaphore limiting"""
        results = []
        
        # Limit concurrent executions
        semaphore = asyncio.Semaphore(self.max_concurrent_tools)
        
        # Reset concurrent execution counter
        self.metrics['concurrent_executions'] = 0
        
        async def execute_single_tool(tool_block: Dict[str, Any]) -> ToolExecutionResult:
            async with semaphore:
                # Update concurrent execution metrics
                track_concurrent_execution(self.metrics, increment=True)
                
                try:
                    tool_call_id = tool_block.get('id', '')
                    tool_name = tool_block.get('name', '')
                    tool_input = tool_block.get('input', {})
                    
                    result = await execute_single_tool_with_timeout(
                        tool_call_id,
                        tool_name,
                        tool_input,
                        self.execution_timeout
                    )
                    
                    return result
                finally:
                    track_concurrent_execution(self.metrics, increment=False)
        
        # Execute tools concurrently
        tasks = [execute_single_tool(block) for block in tool_use_blocks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                tool_block = tool_use_blocks[i]
                error_result = ToolExecutionResult(
                    tool_call_id=tool_block.get('id', f'error_{i}'),
                    tool_name=tool_block.get('name', 'unknown'),
                    success=False,
                    result=None,
                    error=f"Execution exception: {result}"
                )
                update_tool_execution_metrics(self.metrics, error_result)
                processed_results.append(error_result)
            else:
                update_tool_execution_metrics(self.metrics, result)
                processed_results.append(result)
        
        return processed_results
    
    def check_security_errors(self, tool_results: List[ToolExecutionResult]) -> bool:
        """Check if any tool failed with security/permission errors"""
        security_errors = [
            r for r in tool_results 
            if not r.success and r.error and (
                "not allowed for security reasons" in r.error or
                "permission denied" in r.error.lower() or
                "access denied" in r.error.lower()
            )
        ]
        
        if security_errors:
            logger.warning("Tool execution blocked by security policy",
                          security_error_count=len(security_errors))
            return True
        
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current execution metrics"""
        from ...tasks.tool_execution.metrics_tasks import get_execution_metrics
        return get_execution_metrics(self.metrics)