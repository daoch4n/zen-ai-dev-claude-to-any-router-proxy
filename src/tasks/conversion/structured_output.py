"""Structured output tasks for OpenRouter Anthropic Server.

Prefect tasks for creating structured outputs using Instructor patterns.
Part of Phase 6A comprehensive refactoring - Conversion Tasks.
"""

from typing import Any, Dict, List

from prefect import task

from ...models.instructor import ConversionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager
from ...services.base import InstructorService

# Initialize logging and context management
logger = get_logger("structured_output")
context_manager = ContextManager()


@task(name="create_validation_summary")
async def create_validation_summary_task(
    validation_results: List[Dict[str, Any]],
    model: str = "anthropic/claude-3-5-sonnet-20241022"
) -> ConversionResult:
    """
    Create a structured validation summary using Instructor.
    
    Args:
        validation_results: List of validation result dictionaries
        model: Model to use for structured extraction
    
    Returns:
        ConversionResult with structured validation summary
    """
    try:
        # Create instructor service instance
        instructor_service = InstructorService("ValidationSummary")
        
        # Format validation data for Instructor
        validation_text = await _format_validation_results(validation_results)
        
        # Use Instructor to create structured summary
        from ...models.instructor import ValidationResult
        
        summary = instructor_service.extract_structured_data(
            text=validation_text,
            extraction_model=ValidationResult,
            model=model
        )
        
        logger.info("Validation summary created",
                   model=model,
                   validation_count=len(validation_results),
                   summary_created=bool(summary))
        
        return ConversionResult(
            success=True,
            converted_data=summary.model_dump() if summary else None,
            metadata={
                "model": model,
                "validation_count": len(validation_results),
                "summary_type": "structured_validation"
            }
        )
        
    except Exception as e:
        error_msg = f"Validation summary creation failed: {str(e)}"
        logger.error("Validation summary creation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


@task(name="format_validation_results")
async def format_validation_results_task(
    results: List[Dict[str, Any]],
    format_style: str = "detailed"
) -> ConversionResult:
    """
    Format validation results for processing or display.
    
    Args:
        results: List of validation result dictionaries
        format_style: Style of formatting ("detailed", "summary", "json")
    
    Returns:
        ConversionResult with formatted validation results
    """
    try:
        if format_style == "detailed":
            formatted_text = await _format_validation_results(results)
        elif format_style == "summary":
            formatted_text = await _format_validation_summary(results)
        elif format_style == "json":
            import json
            formatted_text = json.dumps(results, indent=2)
        else:
            raise ValueError(f"Unsupported format style: {format_style}")
        
        # Calculate formatting statistics
        stats = {
            "total_results": len(results),
            "valid_results": sum(1 for r in results if r.get('is_valid', False)),
            "invalid_results": sum(1 for r in results if not r.get('is_valid', True)),
            "results_with_errors": sum(1 for r in results if r.get('errors')),
            "results_with_warnings": sum(1 for r in results if r.get('warnings')),
            "formatted_length": len(formatted_text)
        }
        
        logger.info("Validation results formatted",
                   format_style=format_style,
                   **stats)
        
        return ConversionResult(
            success=True,
            converted_data=formatted_text,
            metadata={
                "format_style": format_style,
                **stats
            }
        )
        
    except Exception as e:
        error_msg = f"Validation results formatting failed: {str(e)}"
        logger.error("Validation results formatting failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


async def _format_validation_results(results: List[Dict[str, Any]]) -> str:
    """Format validation results for Instructor processing."""
    formatted_parts = []
    
    for i, result in enumerate(results):
        formatted_parts.append(f"Validation {i+1}:")
        formatted_parts.append(f"  Valid: {result.get('is_valid', False)}")
        
        if result.get('errors'):
            formatted_parts.append(f"  Errors: {', '.join(result['errors'])}")
        
        if result.get('warnings'):
            formatted_parts.append(f"  Warnings: {', '.join(result['warnings'])}")
        
        formatted_parts.append("")
    
    return "\n".join(formatted_parts)


async def _format_validation_summary(results: List[Dict[str, Any]]) -> str:
    """Format validation results as a summary."""
    total_results = len(results)
    valid_count = sum(1 for r in results if r.get('is_valid', False))
    invalid_count = total_results - valid_count
    
    error_count = sum(len(r.get('errors', [])) for r in results)
    warning_count = sum(len(r.get('warnings', [])) for r in results)
    
    summary_parts = [
        f"Validation Summary:",
        f"  Total validations: {total_results}",
        f"  Valid: {valid_count}",
        f"  Invalid: {invalid_count}",
        f"  Total errors: {error_count}",
        f"  Total warnings: {warning_count}",
        f"  Success rate: {(valid_count / total_results * 100):.1f}%" if total_results > 0 else "  Success rate: N/A"
    ]
    
    return "\n".join(summary_parts)


@task(name="extract_structured_data")
async def extract_structured_data_task(
    text: str,
    extraction_model_name: str,
    model: str = "anthropic/claude-sonnet-4",
    extraction_params: Dict[str, Any] = None
) -> ConversionResult:
    """
    Extract structured data from text using Instructor.
    
    Args:
        text: Text to extract data from
        extraction_model_name: Name of the Pydantic model to use
        model: LLM model to use for extraction
        extraction_params: Optional parameters for extraction
    
    Returns:
        ConversionResult with extracted structured data
    """
    try:
        # Create instructor service instance
        instructor_service = InstructorService("StructuredExtraction")
        
        # Get the extraction model class
        extraction_model = _get_extraction_model(extraction_model_name)
        
        if not extraction_model:
            raise ValueError(f"Unknown extraction model: {extraction_model_name}")
        
        # Perform structured extraction
        extracted_data = instructor_service.extract_structured_data(
            text=text,
            extraction_model=extraction_model,
            model=model,
            **(extraction_params or {})
        )
        
        logger.info("Structured data extracted",
                   model=model,
                   extraction_model=extraction_model_name,
                   text_length=len(text),
                   extracted=bool(extracted_data))
        
        return ConversionResult(
            success=True,
            converted_data=extracted_data.model_dump() if extracted_data else None,
            metadata={
                "model": model,
                "extraction_model": extraction_model_name,
                "text_length": len(text),
                "extraction_successful": bool(extracted_data)
            }
        )
        
    except Exception as e:
        error_msg = f"Structured data extraction failed: {str(e)}"
        logger.error("Structured data extraction failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


def _get_extraction_model(model_name: str):
    """Get extraction model class by name."""
    try:
        from ...models.instructor import (
            ValidationResult,
            ConversionResult as InstructorConversionResult,
            ModelMappingResult
        )
        
        model_mapping = {
            "ValidationResult": ValidationResult,
            "ConversionResult": InstructorConversionResult,
            "ModelMappingResult": ModelMappingResult
        }
        
        return model_mapping.get(model_name)
    
    except ImportError:
        logger.warning("Could not import instructor models", model_name=model_name)
        return None


@task(name="create_conversion_report")
async def create_conversion_report_task(
    conversion_results: List[Dict[str, Any]],
    report_format: str = "markdown"
) -> ConversionResult:
    """
    Create a comprehensive conversion report from multiple conversion results.
    
    Args:
        conversion_results: List of conversion result dictionaries
        report_format: Format for the report ("markdown", "json", "text")
    
    Returns:
        ConversionResult with conversion report
    """
    try:
        # Analyze conversion results
        analysis = await _analyze_conversion_results(conversion_results)
        
        # Generate report based on format
        if report_format == "markdown":
            report_content = await _generate_markdown_report(analysis)
        elif report_format == "json":
            import json
            report_content = json.dumps(analysis, indent=2)
        elif report_format == "text":
            report_content = await _generate_text_report(analysis)
        else:
            raise ValueError(f"Unsupported report format: {report_format}")
        
        logger.info("Conversion report created",
                   report_format=report_format,
                   conversion_count=len(conversion_results),
                   success_rate=analysis["success_rate"])
        
        return ConversionResult(
            success=True,
            converted_data=report_content,
            metadata={
                "report_format": report_format,
                "conversion_count": len(conversion_results),
                "success_rate": analysis["success_rate"],
                "report_length": len(report_content)
            }
        )
        
    except Exception as e:
        error_msg = f"Conversion report creation failed: {str(e)}"
        logger.error("Conversion report creation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


async def _analyze_conversion_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze conversion results and generate statistics."""
    total_conversions = len(results)
    successful_conversions = sum(1 for r in results if r.get('success', False))
    failed_conversions = total_conversions - successful_conversions
    
    # Categorize by conversion type
    conversion_types = {}
    for result in results:
        metadata = result.get('metadata', {})
        conversion_type = metadata.get('conversion_type', 'unknown')
        
        if conversion_type not in conversion_types:
            conversion_types[conversion_type] = {'total': 0, 'successful': 0}
        
        conversion_types[conversion_type]['total'] += 1
        if result.get('success', False):
            conversion_types[conversion_type]['successful'] += 1
    
    # Collect errors
    all_errors = []
    for result in results:
        if result.get('errors'):
            all_errors.extend(result['errors'])
    
    # Calculate success rates
    success_rate = (successful_conversions / total_conversions * 100) if total_conversions > 0 else 0
    
    analysis = {
        "total_conversions": total_conversions,
        "successful_conversions": successful_conversions,
        "failed_conversions": failed_conversions,
        "success_rate": round(success_rate, 2),
        "conversion_types": conversion_types,
        "total_errors": len(all_errors),
        "unique_errors": len(set(all_errors)),
        "most_common_errors": _get_most_common_errors(all_errors)
    }
    
    return analysis


def _get_most_common_errors(errors: List[str], limit: int = 5) -> List[Dict[str, Any]]:
    """Get most common errors with counts."""
    from collections import Counter
    
    error_counts = Counter(errors)
    most_common = error_counts.most_common(limit)
    
    return [{"error": error, "count": count} for error, count in most_common]


async def _generate_markdown_report(analysis: Dict[str, Any]) -> str:
    """Generate a markdown format conversion report."""
    report_parts = [
        "# Conversion Report",
        "",
        "## Summary",
        f"- **Total Conversions**: {analysis['total_conversions']}",
        f"- **Successful**: {analysis['successful_conversions']}",
        f"- **Failed**: {analysis['failed_conversions']}",
        f"- **Success Rate**: {analysis['success_rate']}%",
        "",
        "## Conversion Types",
        ""
    ]
    
    for conv_type, stats in analysis['conversion_types'].items():
        success_rate = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
        report_parts.extend([
            f"### {conv_type}",
            f"- Total: {stats['total']}",
            f"- Successful: {stats['successful']}",
            f"- Success Rate: {success_rate:.1f}%",
            ""
        ])
    
    if analysis['most_common_errors']:
        report_parts.extend([
            "## Most Common Errors",
            ""
        ])
        
        for error_info in analysis['most_common_errors']:
            report_parts.append(f"- **{error_info['error']}** (Count: {error_info['count']})")
        
        report_parts.append("")
    
    return "\n".join(report_parts)


async def _generate_text_report(analysis: Dict[str, Any]) -> str:
    """Generate a plain text format conversion report."""
    report_parts = [
        "CONVERSION REPORT",
        "=" * 50,
        "",
        "Summary:",
        f"  Total Conversions: {analysis['total_conversions']}",
        f"  Successful: {analysis['successful_conversions']}",
        f"  Failed: {analysis['failed_conversions']}",
        f"  Success Rate: {analysis['success_rate']}%",
        "",
        "Conversion Types:",
    ]
    
    for conv_type, stats in analysis['conversion_types'].items():
        success_rate = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
        report_parts.extend([
            f"  {conv_type}:",
            f"    Total: {stats['total']}",
            f"    Successful: {stats['successful']}",
            f"    Success Rate: {success_rate:.1f}%",
            ""
        ])
    
    if analysis['most_common_errors']:
        report_parts.extend([
            "Most Common Errors:",
            ""
        ])
        
        for error_info in analysis['most_common_errors']:
            report_parts.append(f"  - {error_info['error']} (Count: {error_info['count']})")
    
    return "\n".join(report_parts)


@task(name="aggregate_conversion_metrics")
async def aggregate_conversion_metrics_task(
    conversion_results: List[Dict[str, Any]],
    time_window: str = "all"
) -> ConversionResult:
    """
    Aggregate metrics from multiple conversion operations.
    
    Args:
        conversion_results: List of conversion result dictionaries
        time_window: Time window for aggregation ("all", "recent", "hourly")
    
    Returns:
        ConversionResult with aggregated metrics
    """
    try:
        metrics = {
            "total_conversions": len(conversion_results),
            "successful_conversions": 0,
            "failed_conversions": 0,
            "average_processing_time": 0,
            "conversion_types": {},
            "error_statistics": {},
            "performance_metrics": {}
        }
        
        processing_times = []
        
        for result in conversion_results:
            # Count successes and failures
            if result.get('success', False):
                metrics["successful_conversions"] += 1
            else:
                metrics["failed_conversions"] += 1
            
            # Track conversion types
            metadata = result.get('metadata', {})
            conversion_type = metadata.get('conversion_type', 'unknown')
            
            if conversion_type not in metrics["conversion_types"]:
                metrics["conversion_types"][conversion_type] = 0
            metrics["conversion_types"][conversion_type] += 1
            
            # Collect processing times
            processing_time = metadata.get('processing_time')
            if processing_time:
                processing_times.append(processing_time)
            
            # Track errors
            if result.get('errors'):
                for error in result['errors']:
                    if error not in metrics["error_statistics"]:
                        metrics["error_statistics"][error] = 0
                    metrics["error_statistics"][error] += 1
        
        # Calculate averages and rates
        if metrics["total_conversions"] > 0:
            metrics["success_rate"] = (metrics["successful_conversions"] / metrics["total_conversions"]) * 100
            metrics["failure_rate"] = (metrics["failed_conversions"] / metrics["total_conversions"]) * 100
        else:
            metrics["success_rate"] = 0
            metrics["failure_rate"] = 0
        
        if processing_times:
            metrics["average_processing_time"] = sum(processing_times) / len(processing_times)
            metrics["performance_metrics"] = {
                "min_processing_time": min(processing_times),
                "max_processing_time": max(processing_times),
                "median_processing_time": sorted(processing_times)[len(processing_times)//2]
            }
        
        logger.info("Conversion metrics aggregated",
                   total_conversions=metrics["total_conversions"],
                   success_rate=metrics["success_rate"],
                   time_window=time_window)
        
        return ConversionResult(
            success=True,
            converted_data=metrics,
            metadata={
                "time_window": time_window,
                "total_conversions": metrics["total_conversions"],
                "success_rate": metrics["success_rate"]
            }
        )
        
    except Exception as e:
        error_msg = f"Conversion metrics aggregation failed: {str(e)}"
        logger.error("Conversion metrics aggregation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )