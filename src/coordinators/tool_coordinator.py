"""Tool Coordinator for OpenRouter Anthropic Server.

High-level coordinator that orchestrates tool execution using Prefect workflows.
Replaces the monolithic tool_executors.py with modular task-based architecture.

Part of Phase 6B comprehensive refactoring - Service Coordinators.
"""

import asyncio
from typing import Any, Dict, List, Optional

from ..core.logging_config import get_logger
from ..services.context_manager import ContextManager
from ..tasks.tool_execution.tool_result_formatting_tasks import ToolExecutionResult

# Initialize logging and context management
logger = get_logger("tool_coordinator")
context_manager = ContextManager()


class ToolCoordinator:
    """
    Coordinates tool execution using Prefect workflows.
    
    Replaces the monolithic tool_executors.py with a modular,
    task-based architecture that provides better concurrency,
    error handling, and maintainability.
    """
    
    def __init__(self):
        """Initialize the tool coordinator."""
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "execution_times": {},
            "tool_usage_counts": {}
        }
        
        logger.info("Tool coordinator initialized with task-based architecture")
    
    async def execute_tool(
        self, 
        tool_name: str, 
        tool_call_id: str, 
        tool_input: Dict[str, Any]
    ) -> ToolExecutionResult:
        """
        Execute a single tool using the appropriate Prefect workflow.
        
        Args:
            tool_name: Name of the tool to execute
            tool_call_id: Unique identifier for this tool call
            tool_input: Input parameters for the tool
        
        Returns:
            ToolExecutionResult with execution outcome
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Update usage statistics
            self.execution_stats["total_executions"] += 1
            tool_key = tool_name.lower()
            self.execution_stats["tool_usage_counts"][tool_key] = (
                self.execution_stats["tool_usage_counts"].get(tool_key, 0) + 1
            )
            
            logger.info("Executing tool via coordinator",
                       tool_name=tool_name,
                       tool_call_id=tool_call_id,
                       has_input=bool(tool_input))
            
            # Get the appropriate flow for this tool (lazy import to avoid circular import)
            from ..flows.tool_execution.tool_mapping import get_flow_for_tool
            flow_function = get_flow_for_tool(tool_name)
            
            if not flow_function:
                error_msg = f"No flow found for tool: {tool_name}"
                logger.error("Tool flow not found", tool_name=tool_name)
                
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=error_msg,
                    execution_time=0.0
                )
            
            # Prepare tool request for the flow
            tool_request = {
                "tool_call_id": tool_call_id,
                "name": tool_name,
                "input": tool_input
            }
            
            # Execute the tool via the appropriate flow
            flow_results = await flow_function([tool_request])
            
            # Extract the result (flows return lists, we want the single result)
            if flow_results and len(flow_results) > 0:
                result = flow_results[0]
                
                if isinstance(result, ToolExecutionResult):
                    tool_result = result
                else:
                    # Handle unexpected result format
                    tool_result = ToolExecutionResult(
                        tool_call_id=tool_call_id,
                        tool_name=tool_name,
                        success=False,
                        result=None,
                        error=f"Unexpected result format: {type(result)}",
                        execution_time=0.0
                    )
            else:
                # No results returned
                tool_result = ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error="No results returned from flow",
                    execution_time=0.0
                )
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            tool_result.execution_time = execution_time
            
            # Update statistics
            if tool_result.success:
                self.execution_stats["successful_executions"] += 1
            else:
                self.execution_stats["failed_executions"] += 1
            
            # Track execution times by tool
            if tool_key not in self.execution_stats["execution_times"]:
                self.execution_stats["execution_times"][tool_key] = []
            self.execution_stats["execution_times"][tool_key].append(execution_time)
            
            logger.info("Tool execution completed via coordinator",
                       tool_name=tool_name,
                       success=tool_result.success,
                       execution_time=execution_time)
            
            return tool_result
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Tool execution failed: {str(e)}"
            
            logger.error("Tool execution failed in coordinator",
                        tool_name=tool_name,
                        tool_call_id=tool_call_id,
                        error=error_msg,
                        execution_time=execution_time,
                        exc_info=True)
            
            self.execution_stats["failed_executions"] += 1
            
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=error_msg,
                execution_time=execution_time
            )
    
    async def execute_tools_batch(
        self,
        tool_requests: List[Dict[str, Any]]
    ) -> List[ToolExecutionResult]:
        """
        Execute multiple tools with optimal concurrency strategies.
        
        Args:
            tool_requests: List of tool request dictionaries
        
        Returns:
            List of ToolExecutionResult objects
        """
        if not tool_requests:
            return []
        
        logger.info("Executing tool batch via coordinator",
                   batch_size=len(tool_requests))
        
        try:
            # Group tools by category for optimal execution
            tool_groups = self._group_tools_by_category(tool_requests)
            
            # Execute each group with appropriate flow
            all_results = []
            
            for category, requests in tool_groups.items():
                if not requests:
                    continue
                
                logger.debug("Executing tool group",
                           category=category,
                           tool_count=len(requests))
                
                # Get the flow for this category
                flow_function = self._get_flow_for_category(category)
                
                if flow_function:
                    try:
                        # Execute the entire group via the appropriate flow
                        group_results = await flow_function(requests)
                        all_results.extend(group_results)
                    except Exception as e:
                        logger.error("Tool group execution failed",
                                   category=category,
                                   error=str(e),
                                   exc_info=True)
                        
                        # Create error results for all tools in the group
                        for request in requests:
                            error_result = ToolExecutionResult(
                                tool_call_id=request.get('tool_call_id', ''),
                                tool_name=request.get('name', ''),
                                success=False,
                                result=None,
                                error=f"Group execution failed: {str(e)}",
                                execution_time=0.0
                            )
                            all_results.append(error_result)
                else:
                    logger.error("No flow found for category", category=category)
                    
                    # Create error results for all tools in the group
                    for request in requests:
                        error_result = ToolExecutionResult(
                            tool_call_id=request.get('tool_call_id', ''),
                            tool_name=request.get('name', ''),
                            success=False,
                            result=None,
                            error=f"No flow found for category: {category}",
                            execution_time=0.0
                        )
                        all_results.append(error_result)
            
            # Update batch statistics
            successful_count = sum(1 for r in all_results if r.success)
            failed_count = len(all_results) - successful_count
            
            self.execution_stats["total_executions"] += len(all_results)
            self.execution_stats["successful_executions"] += successful_count
            self.execution_stats["failed_executions"] += failed_count
            
            logger.info("Tool batch execution completed",
                       total_tools=len(tool_requests),
                       successful_tools=successful_count,
                       failed_tools=failed_count)
            
            return all_results
            
        except Exception as e:
            error_msg = f"Batch tool execution failed: {str(e)}"
            logger.error("Batch tool execution failed",
                        batch_size=len(tool_requests),
                        error=error_msg,
                        exc_info=True)
            
            # Return error results for all tools
            error_results = []
            for request in tool_requests:
                error_result = ToolExecutionResult(
                    tool_call_id=request.get('tool_call_id', ''),
                    tool_name=request.get('name', ''),
                    success=False,
                    result=None,
                    error=error_msg,
                    execution_time=0.0
                )
                error_results.append(error_result)
            
            return error_results
    
    def _group_tools_by_category(
        self,
        tool_requests: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group tools by their execution category for optimal flow routing."""
        groups = {
            'file_operations': [],
            'system_operations': [],
            'search_operations': [],
            'web_operations': [],
            'notebook_operations': [],
            'todo_operations': []
        }
        
        # Tool category mapping
        category_mapping = {
            'write': 'file_operations',
            'read': 'file_operations', 
            'edit': 'file_operations',
            'multiedit': 'file_operations',
            'bash': 'system_operations',
            'task': 'system_operations',
            'glob': 'search_operations',
            'grep': 'search_operations',
            'ls': 'search_operations',
            'websearch': 'web_operations',
            'webfetch': 'web_operations',
            'notebookread': 'notebook_operations',
            'notebookedit': 'notebook_operations',
            'todoread': 'todo_operations',
            'todowrite': 'todo_operations'
        }
        
        for request in tool_requests:
            tool_name = request.get('name', '').lower()
            category = category_mapping.get(tool_name, 'file_operations')  # Default fallback
            groups[category].append(request)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def _get_flow_for_category(self, category: str):
        """Get the appropriate flow function for a tool category."""
        from ..flows.tool_execution import (
            file_operations_flow,
            system_operations_flow,
            search_operations_flow,
            web_operations_flow,
            notebook_operations_flow,
            todo_operations_flow
        )
        
        flow_mapping = {
            'file_operations': file_operations_flow,
            'system_operations': system_operations_flow,
            'search_operations': search_operations_flow,
            'web_operations': web_operations_flow,
            'notebook_operations': notebook_operations_flow,
            'todo_operations': todo_operations_flow
        }
        
        return flow_mapping.get(category)
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics."""
        # Calculate average execution times
        avg_execution_times = {}
        for tool, times in self.execution_stats["execution_times"].items():
            if times:
                avg_execution_times[tool] = sum(times) / len(times)
        
        # Calculate success rate
        total_executions = self.execution_stats["total_executions"]
        success_rate = (
            (self.execution_stats["successful_executions"] / total_executions * 100)
            if total_executions > 0 else 0
        )
        
        return {
            "total_executions": total_executions,
            "successful_executions": self.execution_stats["successful_executions"],
            "failed_executions": self.execution_stats["failed_executions"],
            "success_rate": round(success_rate, 2),
            "average_execution_times": avg_execution_times,
            "tool_usage_counts": self.execution_stats["tool_usage_counts"],
            "most_used_tools": sorted(
                self.execution_stats["tool_usage_counts"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def get_tool_health_status(self) -> Dict[str, Any]:
        """Get health status for all tool categories."""
        health_status = {
            "overall_health": "unknown",
            "category_health": {},
            "recommendations": []
        }
        
        # Analyze health by category
        categories = ['file_operations', 'system_operations', 'search_operations',
                     'web_operations', 'notebook_operations', 'todo_operations']
        
        healthy_categories = 0
        
        for category in categories:
            strategy = get_concurrency_strategy(category)
            category_tools = [tool for tool, cat in [
                ('write', 'file_operations'), ('read', 'file_operations'),
                ('bash', 'system_operations'), ('glob', 'search_operations'),
                ('websearch', 'web_operations'), ('notebookread', 'notebook_operations'),
                ('todoread', 'todo_operations')
            ] if cat == category]
            
            # Calculate category health based on recent success rates
            category_executions = sum(
                self.execution_stats["tool_usage_counts"].get(tool, 0)
                for tool in category_tools
            )
            
            if category_executions > 0:
                # Assume healthy if we have executions (real health would need more data)
                health_status["category_health"][category] = "healthy"
                healthy_categories += 1
            else:
                health_status["category_health"][category] = "untested"
        
        # Determine overall health
        if healthy_categories >= len(categories) * 0.8:
            health_status["overall_health"] = "healthy"
        elif healthy_categories >= len(categories) * 0.6:
            health_status["overall_health"] = "degraded"
        else:
            health_status["overall_health"] = "unhealthy"
        
        # Add recommendations
        if self.execution_stats["failed_executions"] > 0:
            failure_rate = (self.execution_stats["failed_executions"] / 
                          max(self.execution_stats["total_executions"], 1) * 100)
            if failure_rate > 10:
                health_status["recommendations"].append(
                    f"High failure rate detected: {failure_rate:.1f}%. Check tool configurations."
                )
        
        return health_status
    
    async def validate_tool_availability(self) -> Dict[str, bool]:
        """Validate that all tools are available and working."""
        tool_availability = {}
        
        # Test each tool category
        test_tools = [
            ('Write', {'path': '/tmp/test_file.txt', 'content': 'test'}),
            ('Read', {'path': '/etc/hostname'}),
            ('Bash', {'command': 'echo "test"'}),
            ('Glob', {'pattern': '*.py', 'directory': '.'}),
            ('LS', {'path': '.'})
        ]
        
        for tool_name, test_input in test_tools:
            try:
                result = await self.execute_tool(
                    tool_name=tool_name,
                    tool_call_id=f"test_{tool_name.lower()}",
                    tool_input=test_input
                )
                tool_availability[tool_name] = result.success
                
                logger.debug("Tool availability test",
                           tool_name=tool_name,
                           available=result.success)
                
            except Exception as e:
                tool_availability[tool_name] = False
                logger.warning("Tool availability test failed",
                             tool_name=tool_name,
                             error=str(e))
        
        return tool_availability


# Global tool coordinator instance
tool_coordinator = ToolCoordinator()