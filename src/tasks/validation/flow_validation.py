"""Flow Validation Tasks for OpenRouter Anthropic Server.

Prefect tasks for validating flow configurations, executions, and orchestration.
Part of Phase 6B comprehensive refactoring - Validation Tasks.
"""

import asyncio
import traceback
from typing import Any, Dict, List, Optional, Union

from prefect import task
from prefect.client.orchestration import PrefectClient
from prefect.states import State

from ...core.logging_config import get_logger
from ...models.instructor import ConversionResult

# Initialize logging
logger = get_logger("flow_validation")


@task(
    name="validate_flow_definition",
    description="Validate Prefect flow definition structure and configuration",
    tags=["validation", "flows", "prefect"]
)
async def validate_flow_definition_task(
    flow_definition: Dict[str, Any],
    validation_rules: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate a Prefect flow definition for correct structure and configuration.
    
    Args:
        flow_definition: Flow definition to validate
        validation_rules: Optional validation configuration
    
    Returns:
        ConversionResult with validation status and details
    """
    logger.info("Validating flow definition", flow_name=flow_definition.get("name", "unknown"))
    
    try:
        if validation_rules is None:
            validation_rules = {}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "flow_info": {
                "name": flow_definition.get("name"),
                "has_description": bool(flow_definition.get("description")),
                "has_version": bool(flow_definition.get("version")),
                "task_count": 0,
                "dependency_count": 0,
                "timeout_configured": False,
                "retry_configured": False
            }
        }
        
        # Check required fields
        required_fields = ["name", "fn"]
        for field in required_fields:
            if field not in flow_definition:
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False
        
        # Validate flow name
        flow_name = flow_definition.get("name")
        if flow_name:
            if not isinstance(flow_name, str):
                validation_result["errors"].append("Flow name must be a string")
                validation_result["is_valid"] = False
            elif not flow_name.strip():
                validation_result["errors"].append("Flow name cannot be empty")
                validation_result["is_valid"] = False
            elif len(flow_name) > 255:
                validation_result["warnings"].append("Flow name is very long (>255 characters)")
            
            # Check for valid characters in flow name
            if not all(c.isalnum() or c in "_-." for c in flow_name):
                validation_result["warnings"].append("Flow name contains special characters")
        
        # Validate description
        description = flow_definition.get("description")
        if description:
            if not isinstance(description, str):
                validation_result["warnings"].append("Description should be a string")
            elif len(description) < 10:
                validation_result["warnings"].append("Description is very short (<10 characters)")
            elif len(description) > 2000:
                validation_result["warnings"].append("Description is very long (>2000 characters)")
        
        # Validate version
        version = flow_definition.get("version")
        if version:
            validation_result["flow_info"]["has_version"] = True
            if not isinstance(version, str):
                validation_result["warnings"].append("Version should be a string")
        
        # Validate flow function
        flow_fn = flow_definition.get("fn")
        if flow_fn:
            if not callable(flow_fn):
                validation_result["errors"].append("Flow function must be callable")
                validation_result["is_valid"] = False
            else:
                # Check if it's an async function
                if asyncio.iscoroutinefunction(flow_fn):
                    validation_result["flow_info"]["is_async"] = True
                
                # Try to get function signature
                try:
                    import inspect
                    sig = inspect.signature(flow_fn)
                    param_count = len(sig.parameters)
                    validation_result["flow_info"]["parameter_count"] = param_count
                    
                    if param_count > 20:
                        validation_result["warnings"].append(f"Flow function has many parameters ({param_count})")
                except Exception:
                    validation_result["warnings"].append("Could not inspect flow function signature")
        
        # Validate flow configuration
        flow_config = flow_definition.get("configuration", {})
        if flow_config:
            # Check timeout configuration
            if "timeout" in flow_config:
                validation_result["flow_info"]["timeout_configured"] = True
                timeout = flow_config["timeout"]
                if not isinstance(timeout, (int, float)) or timeout <= 0:
                    validation_result["errors"].append("Timeout must be a positive number")
                    validation_result["is_valid"] = False
                elif timeout > 3600:  # 1 hour
                    validation_result["warnings"].append("Flow timeout is very long (>1 hour)")
            
            # Check retry configuration
            if "retries" in flow_config:
                validation_result["flow_info"]["retry_configured"] = True
                retries = flow_config["retries"]
                if not isinstance(retries, int) or retries < 0:
                    validation_result["errors"].append("Retries must be a non-negative integer")
                    validation_result["is_valid"] = False
                elif retries > 10:
                    validation_result["warnings"].append("Flow has many retries (>10)")
            
            # Check task runner configuration
            if "task_runner" in flow_config:
                task_runner = flow_config["task_runner"]
                if task_runner and not hasattr(task_runner, "submit"):
                    validation_result["warnings"].append("Task runner may not be properly configured")
        
        # Validate tags
        tags = flow_definition.get("tags", [])
        if tags:
            if not isinstance(tags, list):
                validation_result["warnings"].append("Tags should be a list")
            elif len(tags) > 20:
                validation_result["warnings"].append("Flow has many tags (>20)")
        
        # Apply custom validation rules
        if validation_rules.get("require_description", False):
            if not description:
                validation_result["warnings"].append("Flow should have a description")
        
        if validation_rules.get("require_version", False):
            if not version:
                validation_result["warnings"].append("Flow should have a version")
        
        if validation_rules.get("enforce_naming_convention", False):
            if flow_name and not flow_name.endswith("_flow"):
                validation_result["warnings"].append("Flow name should end with '_flow'")
        
        logger.info("Flow definition validation completed",
                   flow_name=flow_name,
                   is_valid=validation_result["is_valid"],
                   error_count=len(validation_result["errors"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "flow_name": flow_name,
                "validation_type": "flow_definition"
            }
        )
        
    except Exception as e:
        error_msg = f"Flow definition validation failed: {str(e)}"
        logger.error("Flow definition validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(
    name="validate_flow_execution_state",
    description="Validate flow execution state and results",
    tags=["validation", "flows", "execution"]
)
async def validate_flow_execution_state_task(
    flow_run_id: str,
    expected_state: str = None,
    validation_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate a flow execution state and results.
    
    Args:
        flow_run_id: ID of the flow run to validate
        expected_state: Expected flow state (optional)
        validation_options: Optional validation configuration
    
    Returns:
        ConversionResult with validation status and details
    """
    logger.info("Validating flow execution state", flow_run_id=flow_run_id)
    
    try:
        if validation_options is None:
            validation_options = {}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "execution_info": {
                "flow_run_id": flow_run_id,
                "state": None,
                "state_type": None,
                "start_time": None,
                "end_time": None,
                "duration": None,
                "task_runs": [],
                "failed_tasks": [],
                "successful_tasks": []
            }
        }
        
        # Get flow run information using Prefect client
        async with PrefectClient() as client:
            try:
                flow_run = await client.read_flow_run(flow_run_id)
                
                if not flow_run:
                    validation_result["errors"].append(f"Flow run {flow_run_id} not found")
                    validation_result["is_valid"] = False
                    return ConversionResult(
                        success=True,
                        converted_data=validation_result,
                        metadata={"flow_run_id": flow_run_id}
                    )
                
                # Extract state information
                validation_result["execution_info"]["state"] = flow_run.state.name if flow_run.state else None
                validation_result["execution_info"]["state_type"] = flow_run.state.type.value if flow_run.state else None
                validation_result["execution_info"]["start_time"] = flow_run.start_time
                validation_result["execution_info"]["end_time"] = flow_run.end_time
                
                # Calculate duration
                if flow_run.start_time and flow_run.end_time:
                    duration = (flow_run.end_time - flow_run.start_time).total_seconds()
                    validation_result["execution_info"]["duration"] = duration
                
                # Validate expected state
                if expected_state and flow_run.state:
                    if flow_run.state.name != expected_state:
                        validation_result["errors"].append(
                            f"Flow state is '{flow_run.state.name}', expected '{expected_state}'"
                        )
                        validation_result["is_valid"] = False
                
                # Check for failed state
                if flow_run.state and flow_run.state.is_failed():
                    validation_result["warnings"].append("Flow execution failed")
                    
                    # Get failure details if available
                    if hasattr(flow_run.state, 'message') and flow_run.state.message:
                        validation_result["execution_info"]["failure_message"] = flow_run.state.message
                
                # Get task run information
                task_runs = await client.read_task_runs(
                    flow_run_filter={"id": {"any_": [flow_run_id]}}
                )
                
                validation_result["execution_info"]["task_runs"] = []
                failed_tasks = []
                successful_tasks = []
                
                for task_run in task_runs:
                    task_info = {
                        "id": str(task_run.id),
                        "name": task_run.name,
                        "state": task_run.state.name if task_run.state else None,
                        "state_type": task_run.state.type.value if task_run.state else None
                    }
                    validation_result["execution_info"]["task_runs"].append(task_info)
                    
                    if task_run.state and task_run.state.is_failed():
                        failed_tasks.append(task_info)
                    elif task_run.state and task_run.state.is_completed():
                        successful_tasks.append(task_info)
                
                validation_result["execution_info"]["failed_tasks"] = failed_tasks
                validation_result["execution_info"]["successful_tasks"] = successful_tasks
                
                # Validate task execution
                if failed_tasks:
                    validation_result["warnings"].append(f"{len(failed_tasks)} task(s) failed")
                
                total_tasks = len(task_runs)
                if total_tasks > 0:
                    success_rate = len(successful_tasks) / total_tasks
                    validation_result["execution_info"]["task_success_rate"] = success_rate
                    
                    if success_rate < 0.8:  # Less than 80% success
                        validation_result["warnings"].append(f"Low task success rate: {success_rate:.2%}")
                
            except Exception as client_error:
                validation_result["errors"].append(f"Failed to query Prefect API: {str(client_error)}")
                validation_result["is_valid"] = False
        
        # Check execution duration limits
        max_duration = validation_options.get("max_duration_seconds", 3600)  # 1 hour default
        if validation_result["execution_info"]["duration"]:
            duration = validation_result["execution_info"]["duration"]
            if duration > max_duration:
                validation_result["warnings"].append(
                    f"Flow execution took very long: {duration:.2f}s"
                )
        
        logger.info("Flow execution state validation completed",
                   flow_run_id=flow_run_id,
                   state=validation_result["execution_info"]["state"],
                   is_valid=validation_result["is_valid"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "flow_run_id": flow_run_id,
                "validation_type": "execution_state"
            }
        )
        
    except Exception as e:
        error_msg = f"Flow execution state validation failed: {str(e)}"
        logger.error("Flow execution state validation failed", 
                    flow_run_id=flow_run_id, error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(
    name="validate_flow_dependencies",
    description="Validate flow task dependencies and execution order",
    tags=["validation", "flows", "dependencies"]
)
async def validate_flow_dependencies_task(
    flow_definition: Dict[str, Any],
    dependency_rules: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate flow task dependencies and execution order.
    
    Args:
        flow_definition: Flow definition with task dependencies
        dependency_rules: Optional dependency validation rules
    
    Returns:
        ConversionResult with validation status and details
    """
    logger.info("Validating flow dependencies")
    
    try:
        if dependency_rules is None:
            dependency_rules = {}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "dependency_info": {
                "total_tasks": 0,
                "dependency_count": 0,
                "circular_dependencies": [],
                "orphaned_tasks": [],
                "dependency_depth": 0,
                "execution_paths": []
            }
        }
        
        # Extract task information from flow definition
        tasks = flow_definition.get("tasks", {})
        dependencies = flow_definition.get("dependencies", {})
        
        validation_result["dependency_info"]["total_tasks"] = len(tasks)
        validation_result["dependency_info"]["dependency_count"] = len(dependencies)
        
        if not tasks:
            validation_result["warnings"].append("Flow has no tasks defined")
            return ConversionResult(
                success=True,
                converted_data=validation_result,
                metadata={"validation_type": "dependencies"}
            )
        
        # Check for circular dependencies
        circular_deps = await _detect_circular_dependencies(dependencies)
        if circular_deps:
            validation_result["dependency_info"]["circular_dependencies"] = circular_deps
            validation_result["errors"].append(f"Circular dependencies detected: {circular_deps}")
            validation_result["is_valid"] = False
        
        # Check for orphaned tasks (tasks with no incoming or outgoing dependencies)
        orphaned_tasks = await _find_orphaned_tasks(tasks, dependencies)
        if orphaned_tasks:
            validation_result["dependency_info"]["orphaned_tasks"] = orphaned_tasks
            validation_result["warnings"].append(f"Orphaned tasks found: {orphaned_tasks}")
        
        # Calculate dependency depth (longest path)
        dependency_depth = await _calculate_dependency_depth(dependencies)
        validation_result["dependency_info"]["dependency_depth"] = dependency_depth
        
        if dependency_depth > 10:
            validation_result["warnings"].append(f"Very deep dependency chain: {dependency_depth} levels")
        
        # Validate execution paths
        execution_paths = await _analyze_execution_paths(tasks, dependencies)
        validation_result["dependency_info"]["execution_paths"] = execution_paths
        
        # Check for potential bottlenecks
        bottlenecks = await _identify_dependency_bottlenecks(dependencies)
        if bottlenecks:
            validation_result["warnings"].append(f"Potential bottleneck tasks: {bottlenecks}")
        
        # Apply custom dependency rules
        if dependency_rules.get("max_dependency_depth", 0) > 0:
            max_depth = dependency_rules["max_dependency_depth"]
            if dependency_depth > max_depth:
                validation_result["errors"].append(f"Dependency depth {dependency_depth} exceeds limit {max_depth}")
                validation_result["is_valid"] = False
        
        if dependency_rules.get("allow_orphaned_tasks", True) is False:
            if orphaned_tasks:
                validation_result["errors"].append("Orphaned tasks not allowed")
                validation_result["is_valid"] = False
        
        logger.info("Flow dependencies validation completed",
                   total_tasks=len(tasks),
                   dependency_count=len(dependencies),
                   is_valid=validation_result["is_valid"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "total_tasks": len(tasks),
                "validation_type": "dependencies"
            }
        )
        
    except Exception as e:
        error_msg = f"Flow dependencies validation failed: {str(e)}"
        logger.error("Flow dependencies validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(
    name="validate_flow_performance",
    description="Validate flow performance metrics and resource usage",
    tags=["validation", "flows", "performance"]
)
async def validate_flow_performance_task(
    flow_run_id: str,
    performance_thresholds: Dict[str, Any] = None,
    validation_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate flow performance metrics and resource usage.
    
    Args:
        flow_run_id: ID of the flow run to analyze
        performance_thresholds: Performance threshold configuration
        validation_options: Optional validation configuration
    
    Returns:
        ConversionResult with validation status and details
    """
    logger.info("Validating flow performance", flow_run_id=flow_run_id)
    
    try:
        if performance_thresholds is None:
            performance_thresholds = {
                "max_duration_seconds": 300,  # 5 minutes
                "max_memory_mb": 1000,        # 1GB
                "max_task_failures": 3,
                "min_success_rate": 0.95      # 95%
            }
        
        if validation_options is None:
            validation_options = {}
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "performance_info": {
                "flow_run_id": flow_run_id,
                "total_duration": None,
                "task_count": 0,
                "failed_task_count": 0,
                "success_rate": None,
                "average_task_duration": None,
                "slowest_tasks": [],
                "resource_usage": {}
            }
        }
        
        # Get flow run performance data
        async with PrefectClient() as client:
            try:
                flow_run = await client.read_flow_run(flow_run_id)
                
                if not flow_run:
                    validation_result["errors"].append(f"Flow run {flow_run_id} not found")
                    validation_result["is_valid"] = False
                    return ConversionResult(
                        success=True,
                        converted_data=validation_result,
                        metadata={"flow_run_id": flow_run_id}
                    )
                
                # Calculate total duration
                if flow_run.start_time and flow_run.end_time:
                    total_duration = (flow_run.end_time - flow_run.start_time).total_seconds()
                    validation_result["performance_info"]["total_duration"] = total_duration
                    
                    # Check duration threshold
                    if total_duration > performance_thresholds["max_duration_seconds"]:
                        validation_result["errors"].append(
                            f"Flow duration {total_duration:.2f}s exceeds threshold {performance_thresholds['max_duration_seconds']}s"
                        )
                        validation_result["is_valid"] = False
                
                # Get task run performance data
                task_runs = await client.read_task_runs(
                    flow_run_filter={"id": {"any_": [flow_run_id]}}
                )
                
                task_durations = []
                failed_tasks = 0
                task_performance = []
                
                for task_run in task_runs:
                    if task_run.start_time and task_run.end_time:
                        duration = (task_run.end_time - task_run.start_time).total_seconds()
                        task_durations.append(duration)
                        task_performance.append({
                            "name": task_run.name,
                            "duration": duration,
                            "state": task_run.state.name if task_run.state else None
                        })
                    
                    if task_run.state and task_run.state.is_failed():
                        failed_tasks += 1
                
                validation_result["performance_info"]["task_count"] = len(task_runs)
                validation_result["performance_info"]["failed_task_count"] = failed_tasks
                
                # Calculate success rate
                if len(task_runs) > 0:
                    success_rate = 1 - (failed_tasks / len(task_runs))
                    validation_result["performance_info"]["success_rate"] = success_rate
                    
                    # Check success rate threshold
                    if success_rate < performance_thresholds["min_success_rate"]:
                        validation_result["errors"].append(
                            f"Success rate {success_rate:.2%} below threshold {performance_thresholds['min_success_rate']:.2%}"
                        )
                        validation_result["is_valid"] = False
                
                # Check task failure threshold
                if failed_tasks > performance_thresholds["max_task_failures"]:
                    validation_result["errors"].append(
                        f"Failed task count {failed_tasks} exceeds threshold {performance_thresholds['max_task_failures']}"
                    )
                    validation_result["is_valid"] = False
                
                # Calculate average task duration
                if task_durations:
                    avg_duration = sum(task_durations) / len(task_durations)
                    validation_result["performance_info"]["average_task_duration"] = avg_duration
                    
                    # Find slowest tasks
                    task_performance.sort(key=lambda x: x["duration"], reverse=True)
                    validation_result["performance_info"]["slowest_tasks"] = task_performance[:5]
                    
                    # Check for unusually slow tasks
                    slow_task_threshold = validation_options.get("slow_task_threshold_seconds", 60)
                    slow_tasks = [t for t in task_performance if t["duration"] > slow_task_threshold]
                    
                    if slow_tasks:
                        validation_result["warnings"].append(
                            f"{len(slow_tasks)} task(s) exceeded slow threshold ({slow_task_threshold}s)"
                        )
                
            except Exception as client_error:
                validation_result["errors"].append(f"Failed to query Prefect API: {str(client_error)}")
                validation_result["is_valid"] = False
        
        # Additional performance checks
        if validation_result["performance_info"]["task_count"] > 100:
            validation_result["warnings"].append("Flow has many tasks (>100), consider optimization")
        
        logger.info("Flow performance validation completed",
                   flow_run_id=flow_run_id,
                   duration=validation_result["performance_info"]["total_duration"],
                   success_rate=validation_result["performance_info"]["success_rate"],
                   is_valid=validation_result["is_valid"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "flow_run_id": flow_run_id,
                "validation_type": "performance"
            }
        )
        
    except Exception as e:
        error_msg = f"Flow performance validation failed: {str(e)}"
        logger.error("Flow performance validation failed", 
                    flow_run_id=flow_run_id, error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


# Helper functions for flow validation

async def _detect_circular_dependencies(dependencies: Dict[str, List[str]]) -> List[List[str]]:
    """Detect circular dependencies in the task graph."""
    circular_deps = []
    
    def has_cycle(node, visited, rec_stack, path):
        visited[node] = True
        rec_stack[node] = True
        path.append(node)
        
        for neighbor in dependencies.get(node, []):
            if neighbor not in visited:
                visited[neighbor] = False
            
            if not visited[neighbor]:
                if has_cycle(neighbor, visited, rec_stack, path):
                    return True
            elif rec_stack[neighbor]:
                # Found cycle, extract the cycle path
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                circular_deps.append(cycle)
                return True
        
        rec_stack[node] = False
        path.pop()
        return False
    
    try:
        all_nodes = set(dependencies.keys())
        for neighbors in dependencies.values():
            all_nodes.update(neighbors)
        
        visited = {node: False for node in all_nodes}
        rec_stack = {node: False for node in all_nodes}
        
        for node in all_nodes:
            if not visited[node]:
                has_cycle(node, visited, rec_stack, [])
    
    except Exception:
        # If we can't detect cycles, return empty list
        pass
    
    return circular_deps


async def _find_orphaned_tasks(tasks: Dict[str, Any], dependencies: Dict[str, List[str]]) -> List[str]:
    """Find tasks with no dependencies (incoming or outgoing)."""
    orphaned = []
    
    try:
        task_names = set(tasks.keys())
        has_incoming = set()
        has_outgoing = set(dependencies.keys())
        
        # Find tasks with incoming dependencies
        for deps in dependencies.values():
            has_incoming.update(deps)
        
        # Tasks with no incoming or outgoing dependencies are orphaned
        for task_name in task_names:
            if task_name not in has_incoming and task_name not in has_outgoing:
                orphaned.append(task_name)
    
    except Exception:
        # If we can't determine orphaned tasks, return empty list
        pass
    
    return orphaned


async def _calculate_dependency_depth(dependencies: Dict[str, List[str]]) -> int:
    """Calculate the maximum dependency depth (longest path)."""
    try:
        def dfs_depth(node, visited, memo):
            if node in memo:
                return memo[node]
            
            if node in visited:
                return 0  # Circular dependency, avoid infinite recursion
            
            visited.add(node)
            max_depth = 0
            
            for neighbor in dependencies.get(node, []):
                depth = dfs_depth(neighbor, visited, memo)
                max_depth = max(max_depth, depth)
            
            visited.remove(node)
            memo[node] = max_depth + 1
            return memo[node]
        
        memo = {}
        max_depth = 0
        
        for node in dependencies.keys():
            depth = dfs_depth(node, set(), memo)
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    except Exception:
        return 0


async def _analyze_execution_paths(tasks: Dict[str, Any], dependencies: Dict[str, List[str]]) -> List[List[str]]:
    """Analyze possible execution paths through the flow."""
    paths = []
    
    try:
        # Find entry points (tasks with no dependencies)
        entry_points = []
        all_dependents = set()
        for deps in dependencies.values():
            all_dependents.update(deps)
        
        for task_name in tasks.keys():
            if task_name not in all_dependents:
                entry_points.append(task_name)
        
        # Generate paths from each entry point
        def generate_paths(node, current_path, visited):
            if node in visited:
                return  # Avoid cycles
            
            visited.add(node)
            current_path.append(node)
            
            dependents = dependencies.get(node, [])
            if not dependents:
                # End of path
                paths.append(current_path.copy())
            else:
                for dependent in dependents:
                    generate_paths(dependent, current_path, visited.copy())
            
            current_path.pop()
        
        for entry_point in entry_points:
            generate_paths(entry_point, [], set())
        
        # Limit to first 10 paths to avoid excessive data
        return paths[:10]
    
    except Exception:
        return []


async def _identify_dependency_bottlenecks(dependencies: Dict[str, List[str]]) -> List[str]:
    """Identify tasks that are dependencies for many other tasks."""
    bottlenecks = []
    
    try:
        dependency_count = {}
        
        # Count how many tasks depend on each task
        for task, deps in dependencies.items():
            for dep in deps:
                dependency_count[dep] = dependency_count.get(dep, 0) + 1
        
        # Tasks with many dependents are potential bottlenecks
        for task, count in dependency_count.items():
            if count >= 3:  # Arbitrary threshold
                bottlenecks.append(task)
    
    except Exception:
        pass
    
    return bottlenecks