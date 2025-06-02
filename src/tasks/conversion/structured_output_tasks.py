"""Structured output tasks for creating formatted validation summaries."""

from typing import Any, Dict, List

from ...core.logging_config import get_logger

logger = get_logger("conversion.structured_output")


def format_validation_results(results: List[Dict[str, Any]]) -> str:
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


def create_structured_validation_summary(
    validation_results: List[Dict[str, Any]],
    instructor_service,
    model: str = "anthropic/claude-3-5-sonnet-20241022"
) -> Dict[str, Any]:
    """Create a structured validation summary using Instructor."""
    try:
        # Prepare validation data for Instructor
        validation_text = format_validation_results(validation_results)
        
        # Use Instructor to create structured summary
        from ...models.instructor import ValidationResult
        
        summary = instructor_service.extract_structured_data(
            text=validation_text,
            extraction_model=ValidationResult,
            model=model
        )
        
        logger.info("Validation summary created",
                   model=model,
                   validation_count=len(validation_results))
        
        return summary.model_dump()
        
    except Exception as e:
        logger.error("Validation summary creation failed", 
                    error=str(e),
                    validation_count=len(validation_results))
        raise


def extract_validation_metadata(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract metadata from validation results."""
    total_validations = len(results)
    valid_count = sum(1 for result in results if result.get('is_valid', False))
    error_count = sum(1 for result in results if result.get('errors'))
    warning_count = sum(1 for result in results if result.get('warnings'))
    
    return {
        "total_validations": total_validations,
        "valid_count": valid_count,
        "invalid_count": total_validations - valid_count,
        "error_count": error_count,
        "warning_count": warning_count,
        "success_rate": valid_count / total_validations if total_validations > 0 else 0.0
    }


def categorize_validation_issues(results: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Categorize validation issues by type."""
    error_categories = {}
    warning_categories = {}
    
    for result in results:
        # Categorize errors
        if result.get('errors'):
            for error in result['errors']:
                category = _categorize_issue(error)
                if category not in error_categories:
                    error_categories[category] = []
                error_categories[category].append(error)
        
        # Categorize warnings
        if result.get('warnings'):
            for warning in result['warnings']:
                category = _categorize_issue(warning)
                if category not in warning_categories:
                    warning_categories[category] = []
                warning_categories[category].append(warning)
    
    return {
        "errors": error_categories,
        "warnings": warning_categories
    }


def _categorize_issue(issue: str) -> str:
    """Categorize a validation issue based on its content."""
    issue_lower = issue.lower()
    
    if any(keyword in issue_lower for keyword in ['tool', 'function']):
        return "tool_validation"
    elif any(keyword in issue_lower for keyword in ['message', 'content']):
        return "message_validation"
    elif any(keyword in issue_lower for keyword in ['conversation', 'flow']):
        return "conversation_validation"
    elif any(keyword in issue_lower for keyword in ['schema', 'format']):
        return "schema_validation"
    else:
        return "general"


def create_validation_report_text(results: List[Dict[str, Any]]) -> str:
    """Create a human-readable validation report."""
    metadata = extract_validation_metadata(results)
    categories = categorize_validation_issues(results)
    
    report_lines = [
        "Validation Summary Report",
        "=" * 25,
        f"Total Validations: {metadata['total_validations']}",
        f"Valid: {metadata['valid_count']}",
        f"Invalid: {metadata['invalid_count']}",
        f"Success Rate: {metadata['success_rate']:.1%}",
        ""
    ]
    
    if categories['errors']:
        report_lines.append("Error Categories:")
        for category, errors in categories['errors'].items():
            report_lines.append(f"  {category}: {len(errors)} errors")
        report_lines.append("")
    
    if categories['warnings']:
        report_lines.append("Warning Categories:")
        for category, warnings in categories['warnings'].items():
            report_lines.append(f"  {category}: {len(warnings)} warnings")
        report_lines.append("")
    
    return "\n".join(report_lines)