"""Message Validation Flows for OpenRouter Anthropic Server.

Prefect flows that orchestrate message validation tasks into comprehensive
validation pipelines for different message validation scenarios.

Part of Phase 6B comprehensive refactoring - Validation Flow Orchestration.
"""

import asyncio
from typing import Any, Dict, List, Optional

from prefect import flow
from prefect.task_runners import ConcurrentTaskRunner

from ...core.logging_config import get_logger
from ...models.instructor import ConversionResult
from ...tasks.validation.message_validation import (
    validate_message_format_task,
    validate_message_content_task,
    validate_system_message_task,
    validate_tool_calls_task
)
from ...tasks.validation.security_validation import (
    validate_content_safety_task,
    validate_input_sanitization_task
)

# Initialize logging
logger = get_logger("message_validation_flows")


@flow(
    name="comprehensive_message_validation",
    description="Comprehensive validation of message structure, content, and safety",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "messages", "comprehensive"]
)
async def comprehensive_message_validation_flow(
    messages: List[Dict[str, Any]],
    validation_config: Dict[str, Any] = None,
    security_config: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform comprehensive validation of messages including format, content, and security.
    
    Args:
        messages: List of messages to validate
        validation_config: Message validation configuration
        security_config: Security validation configuration
    
    Returns:
        ConversionResult with comprehensive validation results
    """
    logger.info("Starting comprehensive message validation", message_count=len(messages))
    
    try:
        if validation_config is None:
            validation_config = {}
        if security_config is None:
            security_config = {}
        
        validation_results = {
            "overall_valid": True,
            "message_count": len(messages),
            "validation_summary": {
                "format_validation": [],
                "content_validation": [],
                "security_validation": [],
                "tool_call_validation": []
            },
            "errors": [],
            "warnings": [],
            "statistics": {
                "valid_messages": 0,
                "invalid_messages": 0,
                "security_violations": 0,
                "content_warnings": 0,
                "tool_calls_found": 0
            }
        }
        
        # Validate each message
        for i, message in enumerate(messages):
            logger.debug("Validating message", message_index=i, role=message.get("role"))
            
            # Step 1: Format validation
            format_result = await validate_message_format_task(
                message_data=message,
                expected_format=validation_config.get("expected_format", "anthropic")
            )
            
            validation_results["validation_summary"]["format_validation"].append({
                "message_index": i,
                "result": format_result.converted_data,
                "success": format_result.success
            })
            
            if not format_result.success or not format_result.converted_data.get("is_valid", True):
                validation_results["overall_valid"] = False
                validation_results["statistics"]["invalid_messages"] += 1
                if format_result.errors:
                    validation_results["errors"].extend([f"Message {i}: {error}" for error in format_result.errors])
                if format_result.converted_data:
                    validation_results["errors"].extend([f"Message {i}: {error}" for error in format_result.converted_data.get("errors", [])])
                continue
            
            # Step 2: Content validation
            content = message.get("content")
            if content:
                if isinstance(content, str):
                    content_text = content
                elif isinstance(content, list):
                    # Extract text from content blocks
                    content_text = " ".join([
                        block.get("text", "") for block in content 
                        if isinstance(block, dict) and block.get("type") == "text"
                    ])
                else:
                    content_text = str(content)
                
                content_result = await validate_message_content_task(
                    message_content=content_text,
                    content_rules=validation_config.get("content_rules", {})
                )
                
                validation_results["validation_summary"]["content_validation"].append({
                    "message_index": i,
                    "result": content_result.converted_data,
                    "success": content_result.success
                })
                
                if content_result.success and content_result.converted_data:
                    content_data = content_result.converted_data
                    if not content_data.get("is_valid", True):
                        validation_results["warnings"].extend([f"Message {i}: {warning}" for warning in content_data.get("warnings", [])])
                        validation_results["statistics"]["content_warnings"] += len(content_data.get("warnings", []))
                
                # Step 3: Security validation
                if security_config.get("enable_content_safety", True):
                    security_result = await validate_content_safety_task(
                        content=content_text,
                        safety_rules=security_config.get("safety_rules", {}),
                        validation_options=security_config.get("validation_options", {})
                    )
                    
                    validation_results["validation_summary"]["security_validation"].append({
                        "message_index": i,
                        "result": security_result.converted_data,
                        "success": security_result.success
                    })
                    
                    if security_result.success and security_result.converted_data:
                        security_data = security_result.converted_data
                        if not security_data.get("is_safe", True):
                            validation_results["overall_valid"] = False
                            validation_results["statistics"]["security_violations"] += len(security_data.get("violations", []))
                            validation_results["errors"].extend([f"Message {i}: {violation}" for violation in security_data.get("violations", [])])
            
            # Step 4: Tool call validation
            if isinstance(content, list):
                tool_calls = [block for block in content if isinstance(block, dict) and block.get("type") == "tool_use"]
                if tool_calls:
                    validation_results["statistics"]["tool_calls_found"] += len(tool_calls)
                    
                    tool_result = await validate_tool_calls_task(tool_calls)
                    
                    validation_results["validation_summary"]["tool_call_validation"].append({
                        "message_index": i,
                        "tool_calls": len(tool_calls),
                        "result": tool_result.converted_data,
                        "success": tool_result.success
                    })
                    
                    if tool_result.success and tool_result.converted_data:
                        tool_data = tool_result.converted_data
                        if not tool_data.get("is_valid", True):
                            validation_results["overall_valid"] = False
                            validation_results["errors"].extend([f"Message {i} tool calls: {error}" for error in tool_data.get("errors", [])])
            
            # Count valid messages
            if validation_results["overall_valid"] or len(validation_results["errors"]) == 0:
                validation_results["statistics"]["valid_messages"] += 1
        
        # Generate summary recommendations
        recommendations = await _generate_message_validation_recommendations(validation_results)
        validation_results["recommendations"] = recommendations
        
        logger.info("Comprehensive message validation completed",
                   message_count=len(messages),
                   overall_valid=validation_results["overall_valid"],
                   valid_messages=validation_results["statistics"]["valid_messages"],
                   errors=len(validation_results["errors"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "message_count": len(messages),
                "validation_type": "comprehensive_message",
                "overall_valid": validation_results["overall_valid"]
            }
        )
        
    except Exception as e:
        error_msg = f"Comprehensive message validation failed: {str(e)}"
        logger.error("Comprehensive message validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(
    name="conversation_validation",
    description="Validate conversation structure and flow patterns",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "conversation", "flow"]
)
async def conversation_validation_flow(
    messages: List[Dict[str, Any]],
    system_message: Optional[str] = None,
    conversation_rules: Dict[str, Any] = None
) -> ConversionResult:
    """
    Validate conversation structure, role alternation, and flow patterns.
    
    Args:
        messages: List of conversation messages
        system_message: Optional system message
        conversation_rules: Conversation validation rules
    
    Returns:
        ConversionResult with conversation validation results
    """
    logger.info("Starting conversation validation", message_count=len(messages))
    
    try:
        if conversation_rules is None:
            conversation_rules = {}
        
        validation_results = {
            "is_valid_conversation": True,
            "errors": [],
            "warnings": [],
            "conversation_analysis": {
                "message_count": len(messages),
                "has_system_message": bool(system_message),
                "role_distribution": {},
                "conversation_flow": [],
                "alternation_violations": [],
                "length_analysis": {}
            }
        }
        
        # Validate system message if present
        if system_message:
            system_result = await validate_system_message_task(
                system_message=system_message,
                validation_rules=conversation_rules.get("system_rules", {})
            )
            
            if not system_result.success or not system_result.converted_data.get("is_valid", True):
                validation_results["is_valid_conversation"] = False
                if system_result.errors:
                    validation_results["errors"].extend([f"System message: {error}" for error in system_result.errors])
                if system_result.converted_data:
                    validation_results["errors"].extend([f"System message: {error}" for error in system_result.converted_data.get("errors", [])])
        
        # Analyze conversation structure
        if not messages:
            validation_results["errors"].append("Conversation has no messages")
            validation_results["is_valid_conversation"] = False
            return ConversionResult(
                success=True,
                converted_data=validation_results,
                metadata={"validation_type": "conversation"}
            )
        
        # Extract roles and analyze flow
        roles = []
        role_counts = {}
        message_lengths = []
        
        for i, message in enumerate(messages):
            role = message.get("role", "unknown")
            roles.append(role)
            role_counts[role] = role_counts.get(role, 0) + 1
            
            content = message.get("content", "")
            if isinstance(content, str):
                message_lengths.append(len(content))
            elif isinstance(content, list):
                total_length = sum(len(str(block)) for block in content)
                message_lengths.append(total_length)
            else:
                message_lengths.append(len(str(content)))
        
        validation_results["conversation_analysis"]["role_distribution"] = role_counts
        validation_results["conversation_analysis"]["conversation_flow"] = roles
        
        # Check role alternation
        if len(roles) > 1:
            for i in range(len(roles) - 1):
                if roles[i] == roles[i + 1]:
                    if roles[i] == "user":
                        validation_results["conversation_analysis"]["alternation_violations"].append({
                            "position": i,
                            "issue": "consecutive_user_messages",
                            "description": f"Consecutive user messages at positions {i} and {i+1}"
                        })
                        validation_results["warnings"].append(f"Consecutive user messages at positions {i} and {i+1}")
                    elif roles[i] == "assistant":
                        validation_results["conversation_analysis"]["alternation_violations"].append({
                            "position": i,
                            "issue": "consecutive_assistant_messages", 
                            "description": f"Consecutive assistant messages at positions {i} and {i+1}"
                        })
                        validation_results["warnings"].append(f"Consecutive assistant messages at positions {i} and {i+1}")
        
        # Validate conversation start
        if roles[0] != "user":
            validation_results["warnings"].append(f"Conversation starts with '{roles[0]}' instead of 'user'")
        
        # Validate conversation end
        if len(roles) > 1 and roles[-1] != "user":
            validation_results["warnings"].append(f"Conversation ends with '{roles[-1]}' instead of 'user'")
        
        # Analyze message lengths
        if message_lengths:
            validation_results["conversation_analysis"]["length_analysis"] = {
                "average_length": sum(message_lengths) / len(message_lengths),
                "min_length": min(message_lengths),
                "max_length": max(message_lengths),
                "total_length": sum(message_lengths)
            }
            
            # Check for very long messages
            max_message_length = conversation_rules.get("max_message_length", 10000)
            long_messages = [i for i, length in enumerate(message_lengths) if length > max_message_length]
            if long_messages:
                validation_results["warnings"].append(f"Very long messages at positions: {long_messages}")
        
        # Apply conversation rules
        min_messages = conversation_rules.get("min_messages", 1)
        if len(messages) < min_messages:
            validation_results["errors"].append(f"Conversation too short: {len(messages)} < {min_messages}")
            validation_results["is_valid_conversation"] = False
        
        max_messages = conversation_rules.get("max_messages", 100)
        if len(messages) > max_messages:
            validation_results["warnings"].append(f"Very long conversation: {len(messages)} > {max_messages}")
        
        # Check role requirements
        required_roles = conversation_rules.get("required_roles", ["user"])
        missing_roles = [role for role in required_roles if role not in role_counts]
        if missing_roles:
            validation_results["errors"].append(f"Missing required roles: {missing_roles}")
            validation_results["is_valid_conversation"] = False
        
        logger.info("Conversation validation completed",
                   message_count=len(messages),
                   is_valid=validation_results["is_valid_conversation"],
                   role_distribution=role_counts)
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "message_count": len(messages),
                "validation_type": "conversation",
                "role_distribution": role_counts
            }
        )
        
    except Exception as e:
        error_msg = f"Conversation validation failed: {str(e)}"
        logger.error("Conversation validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(
    name="content_safety_validation",
    description="Comprehensive content safety validation pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "safety", "content"]
)
async def content_safety_validation_flow(
    content_items: List[str],
    safety_config: Dict[str, Any] = None,
    sanitization_config: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform comprehensive content safety validation and sanitization.
    
    Args:
        content_items: List of content strings to validate
        safety_config: Content safety configuration
        sanitization_config: Input sanitization configuration
    
    Returns:
        ConversionResult with safety validation results
    """
    logger.info("Starting content safety validation", content_count=len(content_items))
    
    try:
        if safety_config is None:
            safety_config = {}
        if sanitization_config is None:
            sanitization_config = {}
        
        validation_results = {
            "overall_safe": True,
            "content_count": len(content_items),
            "safety_summary": {
                "safe_content": 0,
                "unsafe_content": 0,
                "sanitized_content": 0,
                "violations_found": 0
            },
            "detailed_results": [],
            "errors": [],
            "warnings": [],
            "sanitized_content": []
        }
        
        # Process each content item
        for i, content in enumerate(content_items):
            logger.debug("Validating content item", content_index=i, content_length=len(content))
            
            content_result = {
                "index": i,
                "original_length": len(content),
                "safety_validation": None,
                "sanitization_result": None,
                "is_safe": True,
                "sanitized_content": content
            }
            
            # Step 1: Content safety validation
            safety_result = await validate_content_safety_task(
                content=content,
                safety_rules=safety_config.get("safety_rules", {}),
                validation_options=safety_config.get("validation_options", {})
            )
            
            content_result["safety_validation"] = safety_result.converted_data
            
            if safety_result.success and safety_result.converted_data:
                safety_data = safety_result.converted_data
                content_result["is_safe"] = safety_data.get("is_safe", True)
                
                if not safety_data.get("is_safe", True):
                    validation_results["overall_safe"] = False
                    validation_results["safety_summary"]["unsafe_content"] += 1
                    validation_results["safety_summary"]["violations_found"] += len(safety_data.get("violations", []))
                    
                    # Add violations with content index
                    for violation in safety_data.get("violations", []):
                        validation_results["errors"].append(f"Content {i}: {violation}")
                else:
                    validation_results["safety_summary"]["safe_content"] += 1
                
                # Add warnings with content index
                for warning in safety_data.get("warnings", []):
                    validation_results["warnings"].append(f"Content {i}: {warning}")
            
            # Step 2: Input sanitization
            if sanitization_config.get("enable_sanitization", True):
                # Prepare input for sanitization task
                input_data = {f"content_{i}": content}
                
                sanitization_result = await validate_input_sanitization_task(
                    user_inputs=input_data,
                    sanitization_rules=sanitization_config.get("sanitization_rules", {}),
                    validation_options=sanitization_config.get("validation_options", {})
                )
                
                content_result["sanitization_result"] = sanitization_result.converted_data
                
                if sanitization_result.success and sanitization_result.converted_data:
                    sanitization_data = sanitization_result.converted_data
                    
                    if not sanitization_data.get("is_safe", True):
                        validation_results["overall_safe"] = False
                        
                        # Add security violations with content index
                        for violation in sanitization_data.get("security_violations", []):
                            validation_results["errors"].append(f"Content {i}: {violation}")
                    
                    # Get sanitized content
                    sanitized_content = sanitization_data.get("sanitized_inputs", {}).get(f"content_{i}", content)
                    content_result["sanitized_content"] = sanitized_content
                    validation_results["sanitized_content"].append(sanitized_content)
                    
                    # Check if content was modified
                    if sanitized_content != content:
                        validation_results["safety_summary"]["sanitized_content"] += 1
                        validation_results["warnings"].append(f"Content {i}: content was sanitized")
                else:
                    validation_results["sanitized_content"].append(content)
            else:
                validation_results["sanitized_content"].append(content)
            
            validation_results["detailed_results"].append(content_result)
        
        # Generate safety recommendations
        recommendations = await _generate_safety_recommendations(validation_results)
        validation_results["recommendations"] = recommendations
        
        logger.info("Content safety validation completed",
                   content_count=len(content_items),
                   overall_safe=validation_results["overall_safe"],
                   safe_content=validation_results["safety_summary"]["safe_content"],
                   violations=validation_results["safety_summary"]["violations_found"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "content_count": len(content_items),
                "validation_type": "content_safety",
                "overall_safe": validation_results["overall_safe"]
            }
        )
        
    except Exception as e:
        error_msg = f"Content safety validation failed: {str(e)}"
        logger.error("Content safety validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(
    name="tool_call_validation",
    description="Comprehensive tool call validation pipeline",
    task_runner=ConcurrentTaskRunner(),
    tags=["validation", "tools", "calls"]
)
async def tool_call_validation_flow(
    tool_calls: List[Dict[str, Any]],
    available_tools: List[Dict[str, Any]] = None,
    validation_config: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform comprehensive validation of tool calls.
    
    Args:
        tool_calls: List of tool calls to validate
        available_tools: List of available tool definitions
        validation_config: Tool call validation configuration
    
    Returns:
        ConversionResult with tool call validation results
    """
    logger.info("Starting tool call validation", tool_call_count=len(tool_calls))
    
    try:
        if validation_config is None:
            validation_config = {}
        if available_tools is None:
            available_tools = []
        
        validation_results = {
            "is_valid": True,
            "tool_call_count": len(tool_calls),
            "validation_summary": {
                "valid_calls": 0,
                "invalid_calls": 0,
                "unknown_tools": 0,
                "parameter_errors": 0
            },
            "detailed_results": [],
            "errors": [],
            "warnings": [],
            "tool_analysis": {
                "tool_usage": {},
                "parameter_analysis": {},
                "availability_check": {}
            }
        }
        
        # Create tool lookup for validation
        available_tool_names = {tool.get("name"): tool for tool in available_tools}
        
        # Validate each tool call
        for i, tool_call in enumerate(tool_calls):
            logger.debug("Validating tool call", call_index=i, tool_name=tool_call.get("name"))
            
            call_result = {
                "index": i,
                "tool_name": tool_call.get("name"),
                "validation_result": None,
                "is_valid": True,
                "availability": "unknown"
            }
            
            # Basic tool call validation
            tool_result = await validate_tool_calls_task([tool_call])
            call_result["validation_result"] = tool_result.converted_data
            
            if tool_result.success and tool_result.converted_data:
                tool_data = tool_result.converted_data
                call_result["is_valid"] = tool_data.get("is_valid", True)
                
                if not tool_data.get("is_valid", True):
                    validation_results["is_valid"] = False
                    validation_results["validation_summary"]["invalid_calls"] += 1
                    validation_results["validation_summary"]["parameter_errors"] += len(tool_data.get("errors", []))
                    
                    # Add errors with call index
                    for error in tool_data.get("errors", []):
                        validation_results["errors"].append(f"Tool call {i}: {error}")
                else:
                    validation_results["validation_summary"]["valid_calls"] += 1
                
                # Add warnings with call index
                for warning in tool_data.get("warnings", []):
                    validation_results["warnings"].append(f"Tool call {i}: {warning}")
            
            # Check tool availability
            tool_name = tool_call.get("name")
            if tool_name:
                if tool_name in available_tool_names:
                    call_result["availability"] = "available"
                    
                    # Update tool usage statistics
                    if tool_name not in validation_results["tool_analysis"]["tool_usage"]:
                        validation_results["tool_analysis"]["tool_usage"][tool_name] = 0
                    validation_results["tool_analysis"]["tool_usage"][tool_name] += 1
                    
                    # Validate against tool definition
                    tool_def = available_tool_names[tool_name]
                    tool_input = tool_call.get("input", {})
                    
                    # Additional parameter validation against tool schema
                    input_schema = tool_def.get("input_schema", {})
                    if input_schema:
                        param_validation = await _validate_tool_parameters(tool_input, input_schema)
                        if not param_validation["is_valid"]:
                            validation_results["errors"].extend([f"Tool call {i}: {error}" for error in param_validation["errors"]])
                            validation_results["is_valid"] = False
                        
                        validation_results["warnings"].extend([f"Tool call {i}: {warning}" for warning in param_validation["warnings"]])
                else:
                    call_result["availability"] = "unavailable"
                    validation_results["validation_summary"]["unknown_tools"] += 1
                    validation_results["warnings"].append(f"Tool call {i}: unknown tool '{tool_name}'")
            
            validation_results["detailed_results"].append(call_result)
        
        # Analyze tool usage patterns
        if validation_results["tool_analysis"]["tool_usage"]:
            most_used_tools = sorted(
                validation_results["tool_analysis"]["tool_usage"].items(),
                key=lambda x: x[1],
                reverse=True
            )
            validation_results["tool_analysis"]["most_used_tools"] = most_used_tools[:5]
        
        # Check for excessive tool usage
        max_tool_calls = validation_config.get("max_tool_calls", 10)
        if len(tool_calls) > max_tool_calls:
            validation_results["warnings"].append(f"Many tool calls in request: {len(tool_calls)} > {max_tool_calls}")
        
        # Generate tool call recommendations
        recommendations = await _generate_tool_call_recommendations(validation_results)
        validation_results["recommendations"] = recommendations
        
        logger.info("Tool call validation completed",
                   tool_call_count=len(tool_calls),
                   is_valid=validation_results["is_valid"],
                   valid_calls=validation_results["validation_summary"]["valid_calls"],
                   unknown_tools=validation_results["validation_summary"]["unknown_tools"])
        
        return ConversionResult(
            success=True,
            converted_data=validation_results,
            metadata={
                "tool_call_count": len(tool_calls),
                "validation_type": "tool_calls",
                "is_valid": validation_results["is_valid"]
            }
        )
        
    except Exception as e:
        error_msg = f"Tool call validation failed: {str(e)}"
        logger.error("Tool call validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


# Helper functions for message validation flows

async def _generate_message_validation_recommendations(validation_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on message validation results."""
    recommendations = []
    
    try:
        stats = validation_results.get("statistics", {})
        
        # Check validation success rate
        total_messages = stats.get("valid_messages", 0) + stats.get("invalid_messages", 0)
        if total_messages > 0:
            success_rate = stats.get("valid_messages", 0) / total_messages
            if success_rate < 0.9:
                recommendations.append("Consider reviewing message format - low validation success rate")
        
        # Check security violations
        if stats.get("security_violations", 0) > 0:
            recommendations.append("Content safety review recommended - security violations detected")
        
        # Check content warnings
        if stats.get("content_warnings", 0) > 5:
            recommendations.append("Review message content - multiple content warnings detected")
        
        # Check tool call usage
        if stats.get("tool_calls_found", 0) > 10:
            recommendations.append("High tool usage detected - consider optimizing tool calls")
        
    except Exception:
        recommendations.append("Unable to generate specific recommendations")
    
    return recommendations


async def _generate_safety_recommendations(validation_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on safety validation results."""
    recommendations = []
    
    try:
        summary = validation_results.get("safety_summary", {})
        
        # Check safety status
        if not validation_results.get("overall_safe", True):
            recommendations.append("Content review required - safety violations detected")
        
        # Check violation rate
        total_content = summary.get("safe_content", 0) + summary.get("unsafe_content", 0)
        if total_content > 0:
            unsafe_rate = summary.get("unsafe_content", 0) / total_content
            if unsafe_rate > 0.1:  # More than 10% unsafe
                recommendations.append("High rate of unsafe content - implement stricter filtering")
        
        # Check sanitization rate
        if summary.get("sanitized_content", 0) > 0:
            recommendations.append("Content required sanitization - review input validation")
        
        # Check violations
        if summary.get("violations_found", 0) > 0:
            recommendations.append("Multiple safety violations - enhance content screening")
        
    except Exception:
        recommendations.append("Unable to generate safety recommendations")
    
    return recommendations


async def _generate_tool_call_recommendations(validation_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on tool call validation results."""
    recommendations = []
    
    try:
        summary = validation_results.get("validation_summary", {})
        
        # Check tool availability
        if summary.get("unknown_tools", 0) > 0:
            recommendations.append("Unknown tools detected - update tool registry")
        
        # Check parameter errors
        if summary.get("parameter_errors", 0) > 0:
            recommendations.append("Tool parameter errors detected - review tool schemas")
        
        # Check success rate
        total_calls = summary.get("valid_calls", 0) + summary.get("invalid_calls", 0)
        if total_calls > 0:
            success_rate = summary.get("valid_calls", 0) / total_calls
            if success_rate < 0.9:
                recommendations.append("Low tool call success rate - review tool configurations")
        
        # Check tool usage patterns
        tool_usage = validation_results.get("tool_analysis", {}).get("tool_usage", {})
        if len(tool_usage) == 1:
            recommendations.append("Only one tool type used - consider diversifying tool usage")
        
    except Exception:
        recommendations.append("Unable to generate tool call recommendations")
    
    return recommendations


async def _validate_tool_parameters(tool_input: Dict[str, Any], input_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate tool parameters against schema."""
    result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Check required parameters
        required = input_schema.get("required", [])
        for param in required:
            if param not in tool_input:
                result["errors"].append(f"Missing required parameter: {param}")
                result["is_valid"] = False
        
        # Check parameter types
        properties = input_schema.get("properties", {})
        for param_name, param_value in tool_input.items():
            if param_name in properties:
                expected_type = properties[param_name].get("type")
                if expected_type:
                    if expected_type == "string" and not isinstance(param_value, str):
                        result["errors"].append(f"Parameter '{param_name}' should be string")
                        result["is_valid"] = False
                    elif expected_type == "integer" and not isinstance(param_value, int):
                        result["errors"].append(f"Parameter '{param_name}' should be integer")
                        result["is_valid"] = False
            else:
                result["warnings"].append(f"Unexpected parameter: {param_name}")
    
    except Exception:
        result["warnings"].append("Error validating tool parameters")
    
    return result