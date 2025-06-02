"""Conversion orchestration flows for OpenRouter Anthropic Server.

Complete conversion workflows that orchestrate multiple conversion tasks.
Part of Phase 6A comprehensive refactoring - Conversion Pipelines.
"""

import asyncio
from typing import Any, Dict, List, Optional

from prefect import flow

from ...models.instructor import ConversionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager
from ...tasks.conversion.format_conversion import (
    anthropic_to_litellm_task,
    litellm_response_to_anthropic_task,
    litellm_to_anthropic_task
)
from ...tasks.conversion.model_mapping import (
    map_model_task,
    update_request_model_task,
    ensure_openrouter_prefix_task
)
from ...tasks.conversion.schema_processing import (
    clean_openrouter_schema_task,
    batch_clean_tool_schemas_task
)
from ...tasks.conversion.response_processing import (
    validate_response_format_task,
    calculate_response_metrics_task
)

# Initialize logging and context management
logger = get_logger("conversion_orchestration")
context_manager = ContextManager()


@flow(name="complete_request_conversion")
async def complete_request_conversion_flow(
    anthropic_request: Dict[str, Any],
    conversion_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Complete request conversion from Anthropic to LiteLLM format.
    
    Orchestrates the full conversion pipeline including model mapping,
    schema cleaning, and format conversion.
    
    Args:
        anthropic_request: Anthropic format request
        conversion_options: Optional conversion configuration
    
    Returns:
        ConversionResult with converted LiteLLM request
    """
    logger.info("Starting complete request conversion",
               has_tools=bool(anthropic_request.get('tools')),
               model=anthropic_request.get('model'))
    
    try:
        if conversion_options is None:
            conversion_options = {}
        
        # Step 1: Model mapping
        model_mapping_result = await map_model_task(
            original_model=anthropic_request.get('model', ''),
            custom_mapping=conversion_options.get('custom_model_mapping')
        )
        
        if not model_mapping_result.success:
            logger.error("Model mapping failed", errors=model_mapping_result.errors)
            return model_mapping_result
        
        # Step 2: Update request with mapped model
        updated_request_result = await update_request_model_task(
            request_data=anthropic_request,
            mapping_result=model_mapping_result.converted_data
        )
        
        if not updated_request_result.success:
            logger.error("Request model update failed", errors=updated_request_result.errors)
            return updated_request_result
        
        updated_request = updated_request_result.converted_data
        
        # Step 3: Clean tool schemas if tools are present
        if updated_request.get('tools'):
            schema_cleaning_result = await batch_clean_tool_schemas_task(
                tools=updated_request['tools']
            )
            
            if schema_cleaning_result.success:
                updated_request['tools'] = schema_cleaning_result.converted_data
                logger.debug("Tool schemas cleaned",
                           tool_count=len(updated_request['tools']),
                           fields_removed=schema_cleaning_result.metadata.get('total_fields_removed', 0))
            else:
                logger.warning("Tool schema cleaning failed, using original schemas",
                             errors=schema_cleaning_result.errors)
        
        # Step 4: Main format conversion
        conversion_metadata = {
            "model_mapping_applied": model_mapping_result.converted_data.get('mapping_applied', False),
            "schema_cleaning_performed": bool(updated_request.get('tools')),
            **conversion_options.get('metadata', {})
        }
        
        final_conversion_result = await anthropic_to_litellm_task(
            source_request=updated_request,
            conversion_metadata=conversion_metadata
        )
        
        if not final_conversion_result.success:
            logger.error("Format conversion failed", errors=final_conversion_result.errors)
            return final_conversion_result
        
        # Step 5: Ensure OpenRouter prefix on final model
        litellm_request = final_conversion_result.converted_data
        prefix_result = await ensure_openrouter_prefix_task(
            model_name=litellm_request['model']
        )
        
        if prefix_result.success:
            litellm_request['model'] = prefix_result.converted_data
        
        # Aggregate metadata from all steps
        complete_metadata = {
            **model_mapping_result.metadata,
            **final_conversion_result.metadata,
            "conversion_steps": ["model_mapping", "schema_cleaning", "format_conversion", "prefix_ensure"],
            "total_conversion_steps": 4
        }
        
        logger.info("Complete request conversion successful",
                   original_model=anthropic_request.get('model'),
                   final_model=litellm_request['model'],
                   steps_completed=4)
        
        return ConversionResult(
            success=True,
            converted_data=litellm_request,
            metadata=complete_metadata
        )
        
    except Exception as e:
        error_msg = f"Complete request conversion failed: {str(e)}"
        logger.error("Complete request conversion failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(name="complete_response_conversion")
async def complete_response_conversion_flow(
    litellm_response: Any,
    original_request: Optional[Dict[str, Any]] = None,
    validation_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Complete response conversion from LiteLLM to Anthropic format.
    
    Includes response validation and metrics calculation.
    
    Args:
        litellm_response: LiteLLM response object
        original_request: Original Anthropic request for context
        validation_options: Optional validation configuration
    
    Returns:
        ConversionResult with converted Anthropic response
    """
    logger.info("Starting complete response conversion",
               response_type=str(type(litellm_response)),
               has_original_request=bool(original_request))
    
    try:
        if validation_options is None:
            validation_options = {}
        
        # Step 1: Main format conversion
        conversion_result = await litellm_response_to_anthropic_task(
            litellm_response=litellm_response,
            original_request=original_request,
            conversion_metadata=validation_options.get('metadata', {})
        )
        
        if not conversion_result.success:
            logger.error("Response format conversion failed", errors=conversion_result.errors)
            return conversion_result
        
        anthropic_response = conversion_result.converted_data
        
        # Step 2: Response validation (if enabled)
        validation_result = None
        if validation_options.get('enable_validation', True):
            validation_result = await validate_response_format_task(
                response_data=anthropic_response,
                expected_format="anthropic"
            )
            
            if validation_result.success:
                validation_data = validation_result.converted_data
                if not validation_data.get('is_valid', True):
                    logger.warning("Response validation failed",
                                 errors=validation_data.get('errors', []),
                                 warnings=validation_data.get('warnings', []))
                else:
                    logger.debug("Response validation passed")
            else:
                logger.warning("Response validation task failed", errors=validation_result.errors)
        
        # Step 3: Calculate response metrics (if enabled)
        metrics_result = None
        if validation_options.get('enable_metrics', False):
            metrics_result = await calculate_response_metrics_task(
                response_data=anthropic_response
            )
            
            if metrics_result.success:
                logger.debug("Response metrics calculated",
                           content_blocks=metrics_result.converted_data.get('content_blocks', 0),
                           complexity_score=metrics_result.converted_data.get('complexity_score', 0))
        
        # Aggregate metadata from all steps
        complete_metadata = {
            **conversion_result.metadata,
            "validation_performed": bool(validation_result),
            "validation_passed": validation_result.converted_data.get('is_valid', True) if validation_result and validation_result.success else None,
            "metrics_calculated": bool(metrics_result and metrics_result.success),
            "conversion_steps": ["format_conversion", "validation", "metrics"],
            "total_conversion_steps": 3
        }
        
        # Add validation details if available
        if validation_result and validation_result.success:
            complete_metadata["validation_details"] = validation_result.converted_data
        
        # Add metrics if available
        if metrics_result and metrics_result.success:
            complete_metadata["response_metrics"] = metrics_result.converted_data
        
        logger.info("Complete response conversion successful",
                   validation_passed=complete_metadata.get('validation_passed'),
                   metrics_available=complete_metadata.get('metrics_calculated'))
        
        return ConversionResult(
            success=True,
            converted_data=anthropic_response,
            metadata=complete_metadata
        )
        
    except Exception as e:
        error_msg = f"Complete response conversion failed: {str(e)}"
        logger.error("Complete response conversion failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(name="bidirectional_conversion")
async def bidirectional_conversion_flow(
    request_data: Dict[str, Any],
    source_format: str,
    target_format: str,
    conversion_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Perform bidirectional conversion between Anthropic and LiteLLM formats.
    
    Args:
        request_data: Request data to convert
        source_format: Source format ("anthropic" or "litellm")
        target_format: Target format ("anthropic" or "litellm")
        conversion_options: Optional conversion configuration
    
    Returns:
        ConversionResult with converted data
    """
    logger.info("Starting bidirectional conversion",
               source_format=source_format,
               target_format=target_format)
    
    try:
        if conversion_options is None:
            conversion_options = {}
        
        if source_format == target_format:
            logger.warning("Source and target formats are the same, returning original data")
            return ConversionResult(
                success=True,
                converted_data=request_data,
                metadata={
                    "source_format": source_format,
                    "target_format": target_format,
                    "conversion_skipped": True
                }
            )
        
        # Route to appropriate conversion flow
        if source_format == "anthropic" and target_format == "litellm":
            return await complete_request_conversion_flow(
                anthropic_request=request_data,
                conversion_options=conversion_options
            )
        
        elif source_format == "litellm" and target_format == "anthropic":
            conversion_result = await litellm_to_anthropic_task(
                source_request=request_data,
                conversion_metadata=conversion_options.get('metadata', {})
            )
            
            # Add bidirectional metadata
            if conversion_result.success:
                conversion_result.metadata.update({
                    "source_format": source_format,
                    "target_format": target_format,
                    "conversion_type": "bidirectional"
                })
            
            return conversion_result
        
        else:
            raise ValueError(f"Unsupported conversion: {source_format} -> {target_format}")
            
    except Exception as e:
        error_msg = f"Bidirectional conversion failed: {str(e)}"
        logger.error("Bidirectional conversion failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@flow(name="conversion_health_check")
async def conversion_health_check_flow(
    test_requests: List[Dict[str, Any]] = None
) -> ConversionResult:
    """
    Perform health checks on conversion system.
    
    Tests various conversion scenarios to ensure system health.
    
    Args:
        test_requests: Optional test requests to use
    
    Returns:
        ConversionResult with health check status
    """
    logger.info("Starting conversion health check")
    
    try:
        # Default test requests if none provided
        if test_requests is None:
            test_requests = [
                {
                    "model": "big",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 100
                },
                {
                    "model": "small", 
                    "messages": [{"role": "user", "content": "Test"}],
                    "max_tokens": 50,
                    "tools": [{
                        "name": "test_tool",
                        "description": "Test tool",
                        "input_schema": {"type": "object", "properties": {}}
                    }]
                }
            ]
        
        health_results = {
            "total_tests": len(test_requests),
            "successful_tests": 0,
            "failed_tests": 0,
            "test_results": [],
            "system_health": "unknown"
        }
        
        # Run conversion tests concurrently
        async def test_conversion(test_request: Dict[str, Any], test_index: int):
            test_result = {
                "test_index": test_index,
                "test_request": test_request,
                "anthropic_to_litellm": {"success": False, "error": None},
                "litellm_to_anthropic": {"success": False, "error": None}
            }
            
            try:
                # Test Anthropic -> LiteLLM conversion
                conversion_result = await complete_request_conversion_flow(
                    anthropic_request=test_request,
                    conversion_options={"metadata": {"health_check": True}}
                )
                
                test_result["anthropic_to_litellm"]["success"] = conversion_result.success
                if not conversion_result.success:
                    test_result["anthropic_to_litellm"]["error"] = conversion_result.errors
                
                # Test LiteLLM -> Anthropic conversion if first test passed
                if conversion_result.success:
                    litellm_request = conversion_result.converted_data
                    reverse_result = await litellm_to_anthropic_task(
                        source_request=litellm_request,
                        conversion_metadata={"health_check": True}
                    )
                    
                    test_result["litellm_to_anthropic"]["success"] = reverse_result.success
                    if not reverse_result.success:
                        test_result["litellm_to_anthropic"]["error"] = reverse_result.errors
                
            except Exception as e:
                test_result["anthropic_to_litellm"]["error"] = str(e)
                test_result["litellm_to_anthropic"]["error"] = str(e)
            
            return test_result
        
        # Execute all tests concurrently
        test_tasks = [
            test_conversion(request, i) 
            for i, request in enumerate(test_requests)
        ]
        
        test_results = await asyncio.gather(*test_tasks, return_exceptions=True)
        
        # Analyze results
        for result in test_results:
            if isinstance(result, dict):
                health_results["test_results"].append(result)
                
                # Count successes
                if (result["anthropic_to_litellm"]["success"] and 
                    result["litellm_to_anthropic"]["success"]):
                    health_results["successful_tests"] += 1
                else:
                    health_results["failed_tests"] += 1
            else:
                health_results["failed_tests"] += 1
                health_results["test_results"].append({
                    "error": str(result),
                    "test_failed": True
                })
        
        # Determine overall health
        success_rate = (health_results["successful_tests"] / health_results["total_tests"]) * 100
        
        if success_rate >= 90:
            health_results["system_health"] = "healthy"
        elif success_rate >= 70:
            health_results["system_health"] = "degraded"
        else:
            health_results["system_health"] = "unhealthy"
        
        health_results["success_rate"] = success_rate
        
        logger.info("Conversion health check completed",
                   total_tests=health_results["total_tests"],
                   successful_tests=health_results["successful_tests"],
                   success_rate=success_rate,
                   system_health=health_results["system_health"])
        
        return ConversionResult(
            success=True,
            converted_data=health_results,
            metadata={
                "health_check": True,
                "success_rate": success_rate,
                "system_health": health_results["system_health"]
            }
        )
        
    except Exception as e:
        error_msg = f"Conversion health check failed: {str(e)}"
        logger.error("Conversion health check failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data={
                "system_health": "error",
                "error": error_msg
            }
        )


@flow(name="batch_conversion_pipeline")
async def batch_conversion_pipeline_flow(
    batch_requests: List[Dict[str, Any]],
    conversion_type: str = "anthropic_to_litellm",
    batch_options: Dict[str, Any] = None
) -> ConversionResult:
    """
    Process multiple conversion requests in batch with optimal concurrency.
    
    Args:
        batch_requests: List of requests to convert
        conversion_type: Type of conversion to perform
        batch_options: Optional batch processing configuration
    
    Returns:
        ConversionResult with batch conversion results
    """
    logger.info("Starting batch conversion pipeline",
               batch_size=len(batch_requests),
               conversion_type=conversion_type)
    
    try:
        if batch_options is None:
            batch_options = {}
        
        max_concurrent = batch_options.get('max_concurrent', 5)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def convert_single_request(request: Dict[str, Any], index: int):
            async with semaphore:
                try:
                    if conversion_type == "anthropic_to_litellm":
                        result = await complete_request_conversion_flow(
                            anthropic_request=request,
                            conversion_options=batch_options.get('conversion_options', {})
                        )
                    elif conversion_type == "litellm_to_anthropic":
                        result = await litellm_to_anthropic_task(
                            source_request=request,
                            conversion_metadata=batch_options.get('metadata', {})
                        )
                    else:
                        raise ValueError(f"Unsupported conversion type: {conversion_type}")
                    
                    return {
                        "index": index,
                        "success": result.success,
                        "converted_data": result.converted_data,
                        "errors": result.errors,
                        "metadata": result.metadata
                    }
                    
                except Exception as e:
                    return {
                        "index": index,
                        "success": False,
                        "converted_data": None,
                        "errors": [str(e)],
                        "metadata": {"conversion_error": True}
                    }
        
        # Execute batch conversion with controlled concurrency
        conversion_tasks = [
            convert_single_request(request, i)
            for i, request in enumerate(batch_requests)
        ]
        
        batch_results = await asyncio.gather(*conversion_tasks, return_exceptions=True)
        
        # Analyze batch results
        batch_summary = {
            "total_requests": len(batch_requests),
            "successful_conversions": 0,
            "failed_conversions": 0,
            "conversion_results": [],
            "success_rate": 0
        }
        
        for result in batch_results:
            if isinstance(result, dict):
                batch_summary["conversion_results"].append(result)
                if result.get("success", False):
                    batch_summary["successful_conversions"] += 1
                else:
                    batch_summary["failed_conversions"] += 1
            else:
                batch_summary["failed_conversions"] += 1
                batch_summary["conversion_results"].append({
                    "success": False,
                    "errors": [str(result)],
                    "conversion_error": True
                })
        
        batch_summary["success_rate"] = (
            batch_summary["successful_conversions"] / batch_summary["total_requests"] * 100
            if batch_summary["total_requests"] > 0 else 0
        )
        
        logger.info("Batch conversion pipeline completed",
                   total_requests=batch_summary["total_requests"],
                   successful_conversions=batch_summary["successful_conversions"],
                   success_rate=batch_summary["success_rate"])
        
        return ConversionResult(
            success=True,
            converted_data=batch_summary,
            metadata={
                "batch_conversion": True,
                "conversion_type": conversion_type,
                "max_concurrent": max_concurrent,
                "success_rate": batch_summary["success_rate"]
            }
        )
        
    except Exception as e:
        error_msg = f"Batch conversion pipeline failed: {str(e)}"
        logger.error("Batch conversion pipeline failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )