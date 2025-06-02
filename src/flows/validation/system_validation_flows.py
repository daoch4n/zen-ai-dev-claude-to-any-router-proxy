"""System Validation Flows for OpenRouter Anthropic Server.

Prefect flows that orchestrate system-level validation tasks including
tool system validation, flow system validation, security validation, and compliance validation.

Part of Phase 6C comprehensive refactoring - System Validation Flows.
"""

import asyncio
from typing import Any, Dict, List, Optional

from prefect import flow
from prefect.task_runners import ConcurrentTaskRunner

from ...core.logging_config import get_logger
from ...models.instructor import ConversionResult
from ...tasks.validation.tool_validation import (
    validate_tool_definition_task,
    validate_tool_execution_request_task,
    validate_tool_execution_result_task,
    validate_tool_registry_task
)
from ...tasks.validation.flow_validation import (
    validate_flow_definition_task,
    validate_flow_execution_state_task,
    validate_flow_dependencies_task,
    validate_flow_performance_task
)
from ...tasks.validation.security_validation import (
    validate_content_safety_task,
    validate_request_authentication_task,
    validate_request_origin_task,
    validate_input_sanitization_task
)

# Initialize logging
logger = get_logger("system_validation_flows")


@flow(
    name="tool_system_validation",
    description="Comprehensive tool system validation pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "tools", "system"]
)
async def tool_system_validation_flow(
    tool_registry: Dict[str, Any],
    tool_definitions: List[Dict[str, Any]] = None,
    execution_history: List[Dict[str, Any]] = None,
    validation_config: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform comprehensive tool system validation including registry, definitions, and execution history.
    
    Args:
        tool_registry: Tool registry to validate
        tool_definitions: Tool definitions to validate
        execution_history: Recent tool execution results to validate
        validation_config: Tool system validation configuration
    
    Returns:
        ConversionResult with comprehensive tool system validation results
    """
    logger.info("Starting tool system validation", 
                registry_size=len(tool_registry),
                definition_count=len(tool_definitions or []),
                execution_count=len(execution_history or []))
    
    try:
        if validation_config is None:
            validation_config = {}
        if tool_definitions is None:
            tool_definitions = []
        if execution_history is None:
            execution_history = []
        
        validation_results = {
            "is_valid_system": True,
            "system_health_score": 1.0,
            "validation_summary": {
                "registry_validation": None,
                "definition_validation": [],
                "execution_validation": [],
                "consistency_check": None
            },
            "errors": [],
            "warnings": [],
            "system_metrics": {
                "total_tools": len(tool_registry),
                "valid_tools": 0,
                "invalid_tools": 0,
                "definition_coverage": 0.0,
                "execution_success_rate": 0.0,
                "consistency_score": 1.0
            }
        }
        
        # Step 1: Tool registry validation
        expected_tools = validation_config.get("expected_tools", list(tool_registry.keys()))
        
        registry_result = await validate_tool_registry_task(
            tool_registry=tool_registry,
            expected_tools=expected_tools,
            validation_options=validation_config.get("registry_options", {})
        )
        
        validation_results["validation_summary"]["registry_validation"] = registry_result.converted_data
        
        if not registry_result.success or not registry_result.converted_data.get("is_valid", True):
            validation_results["is_valid_system"] = False
            if registry_result.errors:
                validation_results["errors"].extend(registry_result.errors)
            
            if registry_result.converted_data:
                registry_data = registry_result.converted_data
                validation_results["errors"].extend(registry_data.get("errors", []))
                validation_results["warnings"].extend(registry_data.get("warnings", []))
                
                # Update metrics
                registry_info = registry_data.get("registry_info", {})
                validation_results["system_metrics"]["invalid_tools"] = len(registry_info.get("invalid_tools", []))
                validation_results["system_metrics"]["valid_tools"] = (
                    validation_results["system_metrics"]["total_tools"] - 
                    validation_results["system_metrics"]["invalid_tools"]
                )
        
        # Step 2: Tool definition validation
        definition_results = []
        valid_definitions = 0
        
        for i, tool_def in enumerate(tool_definitions):
            logger.debug("Validating tool definition", 
                        definition_index=i, 
                        tool_name=tool_def.get("name"))
            
            def_result = await validate_tool_definition_task(
                tool_definition=tool_def,
                validation_rules=validation_config.get("definition_rules", {})
            )
            
            definition_results.append({
                "index": i,
                "tool_name": tool_def.get("name"),
                "result": def_result.converted_data,
                "success": def_result.success
            })
            
            if def_result.success and def_result.converted_data and def_result.converted_data.get("is_valid", True):
                valid_definitions += 1
            else:
                validation_results["is_valid_system"] = False
                if def_result.errors:
                    validation_results["errors"].extend([f"Tool def {i}: {error}" for error in def_result.errors])
                
                if def_result.converted_data:
                    def_data = def_result.converted_data
                    validation_results["errors"].extend([f"Tool def {i}: {error}" for error in def_data.get("errors", [])])
                    validation_results["warnings"].extend([f"Tool def {i}: {warning}" for warning in def_data.get("warnings", [])])
        
        validation_results["validation_summary"]["definition_validation"] = definition_results
        
        # Calculate definition coverage
        if len(tool_definitions) > 0:
            validation_results["system_metrics"]["definition_coverage"] = valid_definitions / len(tool_definitions)
        
        # Step 3: Execution history validation
        execution_results = []
        successful_executions = 0
        
        for i, execution in enumerate(execution_history):
            logger.debug("Validating execution result", execution_index=i)
            
            exec_result = await validate_tool_execution_result_task(
                execution_result=execution,
                expected_format=validation_config.get("execution_format", "standard"),
                validation_rules=validation_config.get("execution_rules", {})
            )
            
            execution_results.append({
                "index": i,
                "result": exec_result.converted_data,
                "success": exec_result.success
            })
            
            if exec_result.success and exec_result.converted_data and exec_result.converted_data.get("is_valid", True):
                successful_executions += 1
            else:
                if exec_result.errors:
                    validation_results["errors"].extend([f"Execution {i}: {error}" for error in exec_result.errors])
                
                if exec_result.converted_data:
                    exec_data = exec_result.converted_data
                    validation_results["errors"].extend([f"Execution {i}: {error}" for error in exec_data.get("errors", [])])
                    validation_results["warnings"].extend([f"Execution {i}: {warning}" for warning in exec_data.get("warnings", [])])
        
        validation_results["validation_summary"]["execution_validation"] = execution_results
        
        # Calculate execution success rate
        if len(execution_history) > 0:
            validation_results["system_metrics"]["execution_success_rate"] = successful_executions / len(execution_history)
        
        # Step 4: Consistency check
        consistency_check = await _perform_tool_system_consistency_check(
            tool_registry, tool_definitions, execution_history
        )
        validation_results["validation_summary"]["consistency_check"] = consistency_check
        
        if not consistency_check.get("is_consistent", True):
            validation_results["is_valid_system"] = False
            validation_results["errors"].extend(consistency_check.get("inconsistencies", []))
        
        validation_results["warnings"].extend(consistency_check.get("warnings", []))
        validation_results["system_metrics"]["consistency_score"] = consistency_check.get("consistency_score", 1.0)
        
        # Calculate overall system health score
        health_factors = [
            validation_results["system_metrics"]["definition_coverage"],
            validation_results["system_metrics"]["execution_success_rate"],
            validation_results["system_metrics"]["consistency_score"]
        ]
        
        validation_results["system_health_score"] = sum(health_factors) / len(health_factors)
        
        # Apply health thresholds
        min_health_score = validation_config.get("min_health_score", 0.8)
        if validation_results["system_health_score"] < min_health_score:
            validation_results["is_valid_system"] = False
            validation_results["errors"].append(f"System health score {validation_results['system_health_score']:.2f} below threshold {min_health_score}")
        
        # Generate system recommendations
        recommendations = await _generate_tool_system_recommendations(validation_results)
        validation_results["recommendations"] = recommendations
        
        logger.info("Tool system validation completed",
                   is_valid_system=validation_results["is_valid_system"],
                   health_score=validation_results["system_health_score"],
                   total_tools=validation_results["system_metrics"]["total_tools"],
                   valid_tools=validation_results["system_metrics"]["valid_tools"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "total_tools": validation_results["system_metrics"]["total_tools"],
                "validation_type": "tool_system",
                "health_score": validation_results["system_health_score"]
            }
        )
        
    except Exception as e:
        error_msg = f"Tool system validation failed: {str(e)}"
        logger.error("Tool system validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(
    name="flow_system_validation",
    description="Comprehensive flow system validation pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "flows", "system"]
)
async def flow_system_validation_flow(
    flow_definitions: List[Dict[str, Any]],
    flow_executions: List[str] = None,
    flow_dependencies: Dict[str, Any] = None,
    validation_config: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform comprehensive flow system validation including definitions, executions, and dependencies.
    
    Args:
        flow_definitions: Flow definitions to validate
        flow_executions: Flow execution IDs to validate
        flow_dependencies: Flow dependency definitions
        validation_config: Flow system validation configuration
    
    Returns:
        ConversionResult with comprehensive flow system validation results
    """
    logger.info("Starting flow system validation",
                definition_count=len(flow_definitions),
                execution_count=len(flow_executions or []))
    
    try:
        if validation_config is None:
            validation_config = {}
        if flow_executions is None:
            flow_executions = []
        if flow_dependencies is None:
            flow_dependencies = {}
        
        validation_results = {
            "is_valid_flow_system": True,
            "flow_health_score": 1.0,
            "validation_summary": {
                "definition_validation": [],
                "execution_validation": [],
                "dependency_validation": None,
                "performance_analysis": []
            },
            "errors": [],
            "warnings": [],
            "flow_metrics": {
                "total_flows": len(flow_definitions),
                "valid_flows": 0,
                "invalid_flows": 0,
                "execution_success_rate": 0.0,
                "average_performance_score": 0.0,
                "dependency_health": 1.0
            }
        }
        
        # Step 1: Flow definition validation
        definition_results = []
        valid_flows = 0
        
        for i, flow_def in enumerate(flow_definitions):
            logger.debug("Validating flow definition",
                        definition_index=i,
                        flow_name=flow_def.get("name"))
            
            def_result = await validate_flow_definition_task(
                flow_definition=flow_def,
                validation_rules=validation_config.get("definition_rules", {})
            )
            
            definition_results.append({
                "index": i,
                "flow_name": flow_def.get("name"),
                "result": def_result.converted_data,
                "success": def_result.success
            })
            
            if def_result.success and def_result.converted_data and def_result.converted_data.get("is_valid", True):
                valid_flows += 1
            else:
                validation_results["is_valid_flow_system"] = False
                if def_result.errors:
                    validation_results["errors"].extend([f"Flow def {i}: {error}" for error in def_result.errors])
                
                if def_result.converted_data:
                    def_data = def_result.converted_data
                    validation_results["errors"].extend([f"Flow def {i}: {error}" for error in def_data.get("errors", [])])
                    validation_results["warnings"].extend([f"Flow def {i}: {warning}" for warning in def_data.get("warnings", [])])
        
        validation_results["validation_summary"]["definition_validation"] = definition_results
        validation_results["flow_metrics"]["valid_flows"] = valid_flows
        validation_results["flow_metrics"]["invalid_flows"] = len(flow_definitions) - valid_flows
        
        # Step 2: Flow execution validation
        execution_results = []
        successful_executions = 0
        performance_scores = []
        
        for i, flow_run_id in enumerate(flow_executions):
            logger.debug("Validating flow execution", execution_index=i, flow_run_id=flow_run_id)
            
            # Validate execution state
            state_result = await validate_flow_execution_state_task(
                flow_run_id=flow_run_id,
                expected_state=validation_config.get("expected_state"),
                validation_options=validation_config.get("execution_options", {})
            )
            
            # Validate execution performance
            perf_result = await validate_flow_performance_task(
                flow_run_id=flow_run_id,
                performance_thresholds=validation_config.get("performance_thresholds", {}),
                validation_options=validation_config.get("performance_options", {})
            )
            
            execution_result = {
                "index": i,
                "flow_run_id": flow_run_id,
                "state_result": state_result.converted_data,
                "performance_result": perf_result.converted_data,
                "success": state_result.success and perf_result.success
            }
            
            execution_results.append(execution_result)
            
            if execution_result["success"]:
                successful_executions += 1
                
                # Extract performance score
                if perf_result.converted_data:
                    perf_data = perf_result.converted_data
                    success_rate = perf_data.get("performance_info", {}).get("success_rate")
                    if success_rate is not None:
                        performance_scores.append(success_rate)
            else:
                if state_result.errors:
                    validation_results["errors"].extend([f"Execution {i}: {error}" for error in state_result.errors])
                if perf_result.errors:
                    validation_results["errors"].extend([f"Performance {i}: {error}" for error in perf_result.errors])
        
        validation_results["validation_summary"]["execution_validation"] = execution_results
        validation_results["validation_summary"]["performance_analysis"] = performance_scores
        
        # Calculate execution success rate
        if len(flow_executions) > 0:
            validation_results["flow_metrics"]["execution_success_rate"] = successful_executions / len(flow_executions)
        
        # Calculate average performance score
        if performance_scores:
            validation_results["flow_metrics"]["average_performance_score"] = sum(performance_scores) / len(performance_scores)
        
        # Step 3: Dependency validation
        if flow_dependencies:
            dep_result = await validate_flow_dependencies_task(
                flow_definition=flow_dependencies,
                dependency_rules=validation_config.get("dependency_rules", {})
            )
            
            validation_results["validation_summary"]["dependency_validation"] = dep_result.converted_data
            
            if not dep_result.success or not dep_result.converted_data.get("is_valid", True):
                validation_results["is_valid_flow_system"] = False
                if dep_result.errors:
                    validation_results["errors"].extend(dep_result.errors)
                
                if dep_result.converted_data:
                    dep_data = dep_result.converted_data
                    validation_results["errors"].extend(dep_data.get("errors", []))
                    validation_results["warnings"].extend(dep_data.get("warnings", []))
                    
                    # Calculate dependency health
                    dep_info = dep_data.get("dependency_info", {})
                    total_tasks = dep_info.get("total_tasks", 1)
                    circular_deps = len(dep_info.get("circular_dependencies", []))
                    orphaned_tasks = len(dep_info.get("orphaned_tasks", []))
                    
                    penalty = (circular_deps + orphaned_tasks) / total_tasks
                    validation_results["flow_metrics"]["dependency_health"] = max(0.0, 1.0 - penalty)
        
        # Calculate overall flow health score
        health_factors = [
            validation_results["flow_metrics"]["valid_flows"] / max(1, validation_results["flow_metrics"]["total_flows"]),
            validation_results["flow_metrics"]["execution_success_rate"],
            validation_results["flow_metrics"]["average_performance_score"],
            validation_results["flow_metrics"]["dependency_health"]
        ]
        
        validation_results["flow_health_score"] = sum(health_factors) / len(health_factors)
        
        # Apply health thresholds
        min_health_score = validation_config.get("min_health_score", 0.8)
        if validation_results["flow_health_score"] < min_health_score:
            validation_results["is_valid_flow_system"] = False
            validation_results["errors"].append(f"Flow health score {validation_results['flow_health_score']:.2f} below threshold {min_health_score}")
        
        # Generate flow system recommendations
        recommendations = await _generate_flow_system_recommendations(validation_results)
        validation_results["recommendations"] = recommendations
        
        logger.info("Flow system validation completed",
                   is_valid_system=validation_results["is_valid_flow_system"],
                   health_score=validation_results["flow_health_score"],
                   total_flows=validation_results["flow_metrics"]["total_flows"],
                   valid_flows=validation_results["flow_metrics"]["valid_flows"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "total_flows": validation_results["flow_metrics"]["total_flows"],
                "validation_type": "flow_system",
                "health_score": validation_results["flow_health_score"]
            }
        )
        
    except Exception as e:
        error_msg = f"Flow system validation failed: {str(e)}"
        logger.error("Flow system validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(
    name="security_validation",
    description="Comprehensive security validation pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "security", "system"]
)
async def security_validation_flow(
    security_context: Dict[str, Any],
    content_samples: List[str] = None,
    request_samples: List[Dict[str, Any]] = None,
    validation_config: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform comprehensive security validation across the system.
    
    Args:
        security_context: Security context and configuration
        content_samples: Content samples to validate for safety
        request_samples: Request samples to validate for security
        validation_config: Security validation configuration
    
    Returns:
        ConversionResult with comprehensive security validation results
    """
    logger.info("Starting security validation",
                content_samples=len(content_samples or []),
                request_samples=len(request_samples or []))
    
    try:
        if validation_config is None:
            validation_config = {}
        if content_samples is None:
            content_samples = []
        if request_samples is None:
            request_samples = []
        
        validation_results = {
            "is_secure_system": True,
            "security_score": 1.0,
            "validation_summary": {
                "content_safety": [],
                "authentication_security": [],
                "origin_security": [],
                "input_sanitization": []
            },
            "security_violations": [],
            "security_warnings": [],
            "security_metrics": {
                "content_safety_score": 1.0,
                "authentication_score": 1.0,
                "origin_security_score": 1.0,
                "sanitization_score": 1.0,
                "overall_risk_level": "low"
            }
        }
        
        # Step 1: Content safety validation
        content_safety_results = []
        safe_content_count = 0
        
        for i, content in enumerate(content_samples):
            logger.debug("Validating content safety", content_index=i)
            
            safety_result = await validate_content_safety_task(
                content=content,
                safety_rules=validation_config.get("safety_rules", {}),
                validation_options=validation_config.get("safety_options", {})
            )
            
            content_result = {
                "index": i,
                "result": safety_result.converted_data,
                "success": safety_result.success
            }
            
            content_safety_results.append(content_result)
            
            if safety_result.success and safety_result.converted_data and safety_result.converted_data.get("is_safe", True):
                safe_content_count += 1
            else:
                validation_results["is_secure_system"] = False
                if safety_result.errors:
                    validation_results["security_violations"].extend([f"Content {i}: {error}" for error in safety_result.errors])
                
                if safety_result.converted_data:
                    safety_data = safety_result.converted_data
                    validation_results["security_violations"].extend([f"Content {i}: {violation}" for violation in safety_data.get("violations", [])])
                    validation_results["security_warnings"].extend([f"Content {i}: {warning}" for warning in safety_data.get("warnings", [])])
        
        validation_results["validation_summary"]["content_safety"] = content_safety_results
        
        # Calculate content safety score
        if len(content_samples) > 0:
            validation_results["security_metrics"]["content_safety_score"] = safe_content_count / len(content_samples)
        
        # Step 2: Authentication security validation
        auth_results = []
        secure_auth_count = 0
        
        for i, request in enumerate(request_samples):
            logger.debug("Validating authentication security", request_index=i)
            
            auth_data = {
                "api_key": request.get("headers", {}).get("x-api-key"),
                "authorization": request.get("headers", {}).get("authorization"),
                "x_api_key": request.get("headers", {}).get("x-api-key")
            }
            
            if any(auth_data.values()):
                auth_result = await validate_request_authentication_task(
                    auth_data=auth_data,
                    auth_requirements=validation_config.get("auth_requirements", {}),
                    validation_options=validation_config.get("auth_options", {})
                )
                
                auth_request_result = {
                    "index": i,
                    "result": auth_result.converted_data,
                    "success": auth_result.success
                }
                
                auth_results.append(auth_request_result)
                
                if auth_result.success and auth_result.converted_data and auth_result.converted_data.get("is_authenticated", False):
                    secure_auth_count += 1
                else:
                    if auth_result.errors:
                        validation_results["security_violations"].extend([f"Auth {i}: {error}" for error in auth_result.errors])
                    
                    if auth_result.converted_data:
                        auth_data_result = auth_result.converted_data
                        validation_results["security_violations"].extend([f"Auth {i}: {error}" for error in auth_data_result.get("errors", [])])
                        validation_results["security_warnings"].extend([f"Auth {i}: {warning}" for warning in auth_data_result.get("warnings", [])])
        
        validation_results["validation_summary"]["authentication_security"] = auth_results
        
        # Calculate authentication score
        if len(auth_results) > 0:
            validation_results["security_metrics"]["authentication_score"] = secure_auth_count / len(auth_results)
        
        # Step 3: Origin security validation
        origin_results = []
        secure_origin_count = 0
        
        for i, request in enumerate(request_samples):
            logger.debug("Validating origin security", request_index=i)
            
            request_metadata = {
                "client_ip": request.get("client_ip") or request.get("headers", {}).get("x-forwarded-for"),
                "user_agent": request.get("headers", {}).get("user-agent"),
                "referer": request.get("headers", {}).get("referer"),
                "origin": request.get("headers", {}).get("origin"),
                "x_forwarded_for": request.get("headers", {}).get("x-forwarded-for")
            }
            
            origin_result = await validate_request_origin_task(
                request_metadata=request_metadata,
                origin_rules=validation_config.get("origin_rules", {}),
                validation_options=validation_config.get("origin_options", {})
            )
            
            origin_request_result = {
                "index": i,
                "result": origin_result.converted_data,
                "success": origin_result.success
            }
            
            origin_results.append(origin_request_result)
            
            if origin_result.success and origin_result.converted_data and origin_result.converted_data.get("is_valid_origin", True):
                secure_origin_count += 1
            else:
                if origin_result.errors:
                    validation_results["security_violations"].extend([f"Origin {i}: {error}" for error in origin_result.errors])
                
                if origin_result.converted_data:
                    origin_data = origin_result.converted_data
                    validation_results["security_violations"].extend([f"Origin {i}: {error}" for error in origin_data.get("errors", [])])
                    validation_results["security_warnings"].extend([f"Origin {i}: {warning}" for warning in origin_data.get("warnings", [])])
        
        validation_results["validation_summary"]["origin_security"] = origin_results
        
        # Calculate origin security score
        if len(origin_results) > 0:
            validation_results["security_metrics"]["origin_security_score"] = secure_origin_count / len(origin_results)
        
        # Step 4: Input sanitization validation
        sanitization_results = []
        secure_input_count = 0
        
        # Extract inputs from request samples
        all_inputs = {}
        for i, request in enumerate(request_samples):
            body = request.get("body", {})
            if isinstance(body, dict):
                for key, value in body.items():
                    if isinstance(value, str):
                        all_inputs[f"request_{i}_{key}"] = value
        
        if all_inputs:
            sanitization_result = await validate_input_sanitization_task(
                user_inputs=all_inputs,
                sanitization_rules=validation_config.get("sanitization_rules", {}),
                validation_options=validation_config.get("sanitization_options", {})
            )
            
            sanitization_results.append({
                "result": sanitization_result.converted_data,
                "success": sanitization_result.success
            })
            
            if sanitization_result.success and sanitization_result.converted_data and sanitization_result.converted_data.get("is_safe", True):
                secure_input_count = 1
                validation_results["security_metrics"]["sanitization_score"] = 1.0
            else:
                validation_results["is_secure_system"] = False
                if sanitization_result.errors:
                    validation_results["security_violations"].extend(sanitization_result.errors)
                
                if sanitization_result.converted_data:
                    sanitization_data = sanitization_result.converted_data
                    validation_results["security_violations"].extend(sanitization_data.get("security_violations", []))
                    validation_results["security_warnings"].extend(sanitization_data.get("warnings", []))
                
                validation_results["security_metrics"]["sanitization_score"] = 0.0
        
        validation_results["validation_summary"]["input_sanitization"] = sanitization_results
        
        # Calculate overall security score
        security_scores = [
            validation_results["security_metrics"]["content_safety_score"],
            validation_results["security_metrics"]["authentication_score"],
            validation_results["security_metrics"]["origin_security_score"],
            validation_results["security_metrics"]["sanitization_score"]
        ]
        
        validation_results["security_score"] = sum(security_scores) / len(security_scores)
        
        # Determine risk level
        if validation_results["security_score"] >= 0.9:
            validation_results["security_metrics"]["overall_risk_level"] = "low"
        elif validation_results["security_score"] >= 0.7:
            validation_results["security_metrics"]["overall_risk_level"] = "medium"
        elif validation_results["security_score"] >= 0.5:
            validation_results["security_metrics"]["overall_risk_level"] = "high"
        else:
            validation_results["security_metrics"]["overall_risk_level"] = "critical"
        
        # Apply security thresholds
        min_security_score = validation_config.get("min_security_score", 0.8)
        if validation_results["security_score"] < min_security_score:
            validation_results["is_secure_system"] = False
            validation_results["security_violations"].append(f"Security score {validation_results['security_score']:.2f} below threshold {min_security_score}")
        
        # Generate security recommendations
        recommendations = await _generate_security_system_recommendations(validation_results)
        validation_results["recommendations"] = recommendations
        
        logger.info("Security validation completed",
                   is_secure_system=validation_results["is_secure_system"],
                   security_score=validation_results["security_score"],
                   risk_level=validation_results["security_metrics"]["overall_risk_level"],
                   violation_count=len(validation_results["security_violations"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "security_score": validation_results["security_score"],
                "validation_type": "security_system",
                "risk_level": validation_results["security_metrics"]["overall_risk_level"]
            }
        )
        
    except Exception as e:
        error_msg = f"Security validation failed: {str(e)}"
        logger.error("Security validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(
    name="compliance_validation",
    description="Comprehensive compliance validation pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "compliance", "audit"]
)
async def compliance_validation_flow(
    compliance_context: Dict[str, Any],
    audit_data: Dict[str, Any] = None,
    policy_rules: Dict[str, Any] = None,
    validation_config: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform comprehensive compliance validation for audit and policy requirements.
    
    Args:
        compliance_context: Compliance context and requirements
        audit_data: Audit data and logs to validate
        policy_rules: Policy rules and compliance requirements
        validation_config: Compliance validation configuration
    
    Returns:
        ConversionResult with comprehensive compliance validation results
    """
    logger.info("Starting compliance validation")
    
    try:
        if validation_config is None:
            validation_config = {}
        if audit_data is None:
            audit_data = {}
        if policy_rules is None:
            policy_rules = {}
        
        validation_results = {
            "is_compliant": True,
            "compliance_score": 1.0,
            "validation_summary": {
                "data_protection": None,
                "access_control": None,
                "audit_trail": None,
                "policy_compliance": None
            },
            "compliance_violations": [],
            "compliance_warnings": [],
            "compliance_metrics": {
                "data_protection_score": 1.0,
                "access_control_score": 1.0,
                "audit_trail_score": 1.0,
                "policy_compliance_score": 1.0,
                "overall_compliance_level": "compliant"
            }
        }
        
        # Step 1: Data protection compliance
        data_protection_check = await _validate_data_protection_compliance(
            compliance_context, validation_config.get("data_protection", {})
        )
        validation_results["validation_summary"]["data_protection"] = data_protection_check
        
        if not data_protection_check.get("is_compliant", True):
            validation_results["is_compliant"] = False
            validation_results["compliance_violations"].extend(data_protection_check.get("violations", []))
        
        validation_results["compliance_warnings"].extend(data_protection_check.get("warnings", []))
        validation_results["compliance_metrics"]["data_protection_score"] = data_protection_check.get("compliance_score", 1.0)
        
        # Step 2: Access control compliance
        access_control_check = await _validate_access_control_compliance(
            compliance_context, validation_config.get("access_control", {})
        )
        validation_results["validation_summary"]["access_control"] = access_control_check
        
        if not access_control_check.get("is_compliant", True):
            validation_results["is_compliant"] = False
            validation_results["compliance_violations"].extend(access_control_check.get("violations", []))
        
        validation_results["compliance_warnings"].extend(access_control_check.get("warnings", []))
        validation_results["compliance_metrics"]["access_control_score"] = access_control_check.get("compliance_score", 1.0)
        
        # Step 3: Audit trail compliance
        audit_trail_check = await _validate_audit_trail_compliance(
            audit_data, validation_config.get("audit_requirements", {})
        )
        validation_results["validation_summary"]["audit_trail"] = audit_trail_check
        
        if not audit_trail_check.get("is_compliant", True):
            validation_results["is_compliant"] = False
            validation_results["compliance_violations"].extend(audit_trail_check.get("violations", []))
        
        validation_results["compliance_warnings"].extend(audit_trail_check.get("warnings", []))
        validation_results["compliance_metrics"]["audit_trail_score"] = audit_trail_check.get("compliance_score", 1.0)
        
        # Step 4: Policy compliance
        policy_compliance_check = await _validate_policy_compliance(
            compliance_context, policy_rules, validation_config.get("policy_config", {})
        )
        validation_results["validation_summary"]["policy_compliance"] = policy_compliance_check
        
        if not policy_compliance_check.get("is_compliant", True):
            validation_results["is_compliant"] = False
            validation_results["compliance_violations"].extend(policy_compliance_check.get("violations", []))
        
        validation_results["compliance_warnings"].extend(policy_compliance_check.get("warnings", []))
        validation_results["compliance_metrics"]["policy_compliance_score"] = policy_compliance_check.get("compliance_score", 1.0)
        
        # Calculate overall compliance score
        compliance_scores = [
            validation_results["compliance_metrics"]["data_protection_score"],
            validation_results["compliance_metrics"]["access_control_score"],
            validation_results["compliance_metrics"]["audit_trail_score"],
            validation_results["compliance_metrics"]["policy_compliance_score"]
        ]
        
        validation_results["compliance_score"] = sum(compliance_scores) / len(compliance_scores)
        
        # Determine compliance level
        if validation_results["compliance_score"] >= 0.95:
            validation_results["compliance_metrics"]["overall_compliance_level"] = "fully_compliant"
        elif validation_results["compliance_score"] >= 0.8:
            validation_results["compliance_metrics"]["overall_compliance_level"] = "compliant"
        elif validation_results["compliance_score"] >= 0.6:
            validation_results["compliance_metrics"]["overall_compliance_level"] = "partially_compliant"
        else:
            validation_results["compliance_metrics"]["overall_compliance_level"] = "non_compliant"
        
        # Apply compliance thresholds
        min_compliance_score = validation_config.get("min_compliance_score", 0.9)
        if validation_results["compliance_score"] < min_compliance_score:
            validation_results["is_compliant"] = False
            validation_results["compliance_violations"].append(f"Compliance score {validation_results['compliance_score']:.2f} below threshold {min_compliance_score}")
        
        # Generate compliance recommendations
        recommendations = await _generate_compliance_recommendations(validation_results)
        validation_results["recommendations"] = recommendations
        
        logger.info("Compliance validation completed",
                   is_compliant=validation_results["is_compliant"],
                   compliance_score=validation_results["compliance_score"],
                   compliance_level=validation_results["compliance_metrics"]["overall_compliance_level"],
                   violation_count=len(validation_results["compliance_violations"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "compliance_score": validation_results["compliance_score"],
                "validation_type": "compliance",
                "compliance_level": validation_results["compliance_metrics"]["overall_compliance_level"]
            }
        )
        
    except Exception as e:
        error_msg = f"Compliance validation failed: {str(e)}"
        logger.error("Compliance validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


# Helper functions for system validation flows

async def _perform_tool_system_consistency_check(
    tool_registry: Dict[str, Any],
    tool_definitions: List[Dict[str, Any]],
    execution_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Perform consistency check across tool system components."""
    consistency_check = {
        "is_consistent": True,
        "consistency_score": 1.0,
        "inconsistencies": [],
        "warnings": []
    }
    
    try:
        # Check registry vs definitions consistency
        registry_tools = set(tool_registry.keys())
        definition_tools = set(tool_def.get("name") for tool_def in tool_definitions if tool_def.get("name"))
        
        missing_definitions = registry_tools - definition_tools
        extra_definitions = definition_tools - registry_tools
        
        if missing_definitions:
            consistency_check["inconsistencies"].append(f"Tools in registry but missing definitions: {list(missing_definitions)}")
            consistency_check["is_consistent"] = False
        
        if extra_definitions:
            consistency_check["warnings"].append(f"Tool definitions without registry entries: {list(extra_definitions)}")
        
        # Check execution history consistency
        executed_tools = set()
        for execution in execution_history:
            tool_name = execution.get("tool_name")
            if tool_name:
                executed_tools.add(tool_name)
        
        unregistered_executions = executed_tools - registry_tools
        if unregistered_executions:
            consistency_check["inconsistencies"].append(f"Executed tools not in registry: {list(unregistered_executions)}")
            consistency_check["is_consistent"] = False
        
        # Calculate consistency score
        total_inconsistencies = len(consistency_check["inconsistencies"])
        total_tools = len(registry_tools)
        
        if total_tools > 0:
            consistency_penalty = min(1.0, total_inconsistencies / total_tools)
            consistency_check["consistency_score"] = 1.0 - consistency_penalty
        
    except Exception:
        consistency_check["warnings"].append("Error performing consistency check")
    
    return consistency_check


async def _generate_tool_system_recommendations(validation_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations for tool system validation results."""
    recommendations = []
    
    try:
        health_score = validation_results.get("system_health_score", 1.0)
        metrics = validation_results.get("system_metrics", {})
        
        if health_score < 0.8:
            recommendations.append("Tool system health is low - review and fix validation errors")
        
        if metrics.get("definition_coverage", 1.0) < 0.9:
            recommendations.append("Low tool definition coverage - add missing tool definitions")
        
        if metrics.get("execution_success_rate", 1.0) < 0.8:
            recommendations.append("Low execution success rate - review tool implementations")
        
        if metrics.get("consistency_score", 1.0) < 0.9:
            recommendations.append("Tool system inconsistencies detected - synchronize components")
        
        if metrics.get("invalid_tools", 0) > 0:
            recommendations.append(f"Fix {metrics['invalid_tools']} invalid tool(s)")
        
    except Exception:
        recommendations.append("Unable to generate tool system recommendations")
    
    return recommendations


async def _generate_flow_system_recommendations(validation_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations for flow system validation results."""
    recommendations = []
    
    try:
        health_score = validation_results.get("flow_health_score", 1.0)
        metrics = validation_results.get("flow_metrics", {})
        
        if health_score < 0.8:
            recommendations.append("Flow system health is low - review and fix validation errors")
        
        if metrics.get("execution_success_rate", 1.0) < 0.8:
            recommendations.append("Low flow execution success rate - review flow implementations")
        
        if metrics.get("average_performance_score", 1.0) < 0.7:
            recommendations.append("Poor flow performance - optimize flow execution")
        
        if metrics.get("dependency_health", 1.0) < 0.9:
            recommendations.append("Flow dependency issues detected - review flow dependencies")
        
        if metrics.get("invalid_flows", 0) > 0:
            recommendations.append(f"Fix {metrics['invalid_flows']} invalid flow(s)")
        
    except Exception:
        recommendations.append("Unable to generate flow system recommendations")
    
    return recommendations


async def _generate_security_system_recommendations(validation_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations for security system validation results."""
    recommendations = []
    
    try:
        security_score = validation_results.get("security_score", 1.0)
        metrics = validation_results.get("security_metrics", {})
        
        if security_score < 0.8:
            recommendations.append("Security score is low - address security violations")
        
        if metrics.get("content_safety_score", 1.0) < 0.9:
            recommendations.append("Content safety issues detected - enhance content filtering")
        
        if metrics.get("authentication_score", 1.0) < 0.9:
            recommendations.append("Authentication security issues - strengthen auth validation")
        
        if metrics.get("origin_security_score", 1.0) < 0.9:
            recommendations.append("Origin security concerns - review origin validation")
        
        if metrics.get("sanitization_score", 1.0) < 0.9:
            recommendations.append("Input sanitization issues - enhance input validation")
        
        risk_level = metrics.get("overall_risk_level", "low")
        if risk_level in ["high", "critical"]:
            recommendations.append(f"High security risk level ({risk_level}) - immediate security review required")
        
    except Exception:
        recommendations.append("Unable to generate security system recommendations")
    
    return recommendations


async def _validate_data_protection_compliance(
    compliance_context: Dict[str, Any],
    data_protection_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate data protection compliance."""
    result = {
        "is_compliant": True,
        "compliance_score": 1.0,
        "violations": [],
        "warnings": []
    }
    
    try:
        # Check for data encryption requirements
        if data_protection_config.get("require_encryption", True):
            if not compliance_context.get("data_encrypted", False):
                result["violations"].append("Data encryption not enabled")
                result["is_compliant"] = False
        
        # Check for data retention policies
        if data_protection_config.get("check_retention", True):
            if not compliance_context.get("retention_policy_defined", False):
                result["warnings"].append("Data retention policy not defined")
        
        # Check for personal data handling
        if compliance_context.get("handles_personal_data", False):
            if not compliance_context.get("gdpr_compliant", False):
                result["violations"].append("GDPR compliance required for personal data")
                result["is_compliant"] = False
        
        # Calculate compliance score
        total_checks = 3
        violations = len(result["violations"])
        result["compliance_score"] = max(0.0, 1.0 - (violations / total_checks))
        
    except Exception:
        result["warnings"].append("Error validating data protection compliance")
    
    return result


async def _validate_access_control_compliance(
    compliance_context: Dict[str, Any],
    access_control_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate access control compliance."""
    result = {
        "is_compliant": True,
        "compliance_score": 1.0,
        "violations": [],
        "warnings": []
    }
    
    try:
        # Check for authentication requirements
        if access_control_config.get("require_authentication", True):
            if not compliance_context.get("authentication_enabled", False):
                result["violations"].append("Authentication not enabled")
                result["is_compliant"] = False
        
        # Check for authorization controls
        if access_control_config.get("require_authorization", True):
            if not compliance_context.get("authorization_controls", False):
                result["violations"].append("Authorization controls not implemented")
                result["is_compliant"] = False
        
        # Check for role-based access
        if access_control_config.get("require_rbac", False):
            if not compliance_context.get("rbac_implemented", False):
                result["warnings"].append("Role-based access control recommended")
        
        # Calculate compliance score
        total_checks = 2  # Only required checks
        violations = len(result["violations"])
        result["compliance_score"] = max(0.0, 1.0 - (violations / total_checks))
        
    except Exception:
        result["warnings"].append("Error validating access control compliance")
    
    return result


async def _validate_audit_trail_compliance(
    audit_data: Dict[str, Any],
    audit_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate audit trail compliance."""
    result = {
        "is_compliant": True,
        "compliance_score": 1.0,
        "violations": [],
        "warnings": []
    }
    
    try:
        # Check for audit logging
        if audit_requirements.get("require_audit_logging", True):
            if not audit_data.get("audit_logging_enabled", False):
                result["violations"].append("Audit logging not enabled")
                result["is_compliant"] = False
        
        # Check for log retention
        if audit_requirements.get("require_log_retention", True):
            retention_days = audit_data.get("log_retention_days", 0)
            min_retention = audit_requirements.get("min_retention_days", 90)
            if retention_days < min_retention:
                result["violations"].append(f"Log retention too short: {retention_days} < {min_retention} days")
                result["is_compliant"] = False
        
        # Check for log integrity
        if audit_requirements.get("require_log_integrity", True):
            if not audit_data.get("log_integrity_protection", False):
                result["warnings"].append("Log integrity protection not implemented")
        
        # Calculate compliance score
        total_checks = 2  # Only required checks
        violations = len(result["violations"])
        result["compliance_score"] = max(0.0, 1.0 - (violations / total_checks))
        
    except Exception:
        result["warnings"].append("Error validating audit trail compliance")
    
    return result


async def _validate_policy_compliance(
    compliance_context: Dict[str, Any],
    policy_rules: Dict[str, Any],
    policy_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate policy compliance."""
    result = {
        "is_compliant": True,
        "compliance_score": 1.0,
        "violations": [],
        "warnings": []
    }
    
    try:
        # Check against defined policies
        for policy_name, policy_rule in policy_rules.items():
            required = policy_rule.get("required", False)
            context_key = policy_rule.get("context_key")
            expected_value = policy_rule.get("expected_value")
            
            if context_key and context_key in compliance_context:
                actual_value = compliance_context[context_key]
                
                if expected_value is not None and actual_value != expected_value:
                    if required:
                        result["violations"].append(f"Policy violation: {policy_name} - expected {expected_value}, got {actual_value}")
                        result["is_compliant"] = False
                    else:
                        result["warnings"].append(f"Policy recommendation: {policy_name} - expected {expected_value}, got {actual_value}")
            elif required:
                result["violations"].append(f"Required policy context missing: {policy_name}")
                result["is_compliant"] = False
        
        # Calculate compliance score
        total_policies = len(policy_rules)
        violations = len(result["violations"])
        if total_policies > 0:
            result["compliance_score"] = max(0.0, 1.0 - (violations / total_policies))
        
    except Exception:
        result["warnings"].append("Error validating policy compliance")
    
    return result


async def _generate_compliance_recommendations(validation_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations for compliance validation results."""
    recommendations = []
    
    try:
        compliance_score = validation_results.get("compliance_score", 1.0)
        metrics = validation_results.get("compliance_metrics", {})
        
        if compliance_score < 0.9:
            recommendations.append("Compliance score is low - address compliance violations")
        
        if metrics.get("data_protection_score", 1.0) < 0.9:
            recommendations.append("Data protection compliance issues - review data handling procedures")
        
        if metrics.get("access_control_score", 1.0) < 0.9:
            recommendations.append("Access control compliance issues - strengthen access controls")
        
        if metrics.get("audit_trail_score", 1.0) < 0.9:
            recommendations.append("Audit trail compliance issues - enhance audit logging")
        
        if metrics.get("policy_compliance_score", 1.0) < 0.9:
            recommendations.append("Policy compliance issues - review and update policies")
        
        compliance_level = metrics.get("overall_compliance_level", "compliant")
        if compliance_level in ["partially_compliant", "non_compliant"]:
            recommendations.append(f"Compliance level is {compliance_level} - immediate compliance review required")
        
    except Exception:
        recommendations.append("Unable to generate compliance recommendations")
    
    return recommendations