"""Tool validation flow for orchestrating tool validation operations."""

from typing import Any, List
from ...models.anthropic import Message, Tool
from ...models.instructor import ValidationResult, ToolValidationResult
from ...tasks.validation.tool_validation_tasks import (
    validate_tool_data,
    validate_tool_flow_data
)
from ...tasks.validation.schema_validation_tasks import create_validation_result
from ...core.logging_config import get_logger

logger = get_logger("validation.tool_flow")


class ToolValidationFlow:
    """Orchestrates tool validation operations using task-based architecture."""
    
    def __init__(self):
        """Initialize tool validation flow."""
        logger.info("ToolValidationFlow initialized")
    
    async def validate_tool(self, data: Any, **kwargs) -> ValidationResult:
        """Validate tool data.
        
        Args:
            data: Tool data to validate
            **kwargs: Additional validation parameters
            
        Returns:
            ValidationResult with validation details
        """
        try:
            logger.debug("Starting tool validation", data_type=type(data).__name__)
            
            # Use task function for validation
            result_data = validate_tool_data(data)
            
            # Convert to ValidationResult
            result = create_validation_result(
                is_valid=result_data["is_valid"],
                errors=result_data["errors"],
                warnings=result_data["warnings"],
                suggestions=result_data["suggestions"]
            )
            
            logger.debug("Tool validation completed",
                        is_valid=result.is_valid,
                        error_count=len(result.errors),
                        warning_count=len(result.warnings))
            
            return result
            
        except Exception as e:
            logger.error("Tool validation flow failed", error=str(e), exc_info=True)
            return create_validation_result(
                False,
                errors=[f"Tool validation failed: {str(e)}"]
            )
    
    async def validate_tool_flow(
        self,
        messages: List[Message],
        available_tools: List[Tool]
    ) -> ToolValidationResult:
        """Validate tool flow across messages to detect orphaned tools.
        
        Args:
            messages: List of conversation messages
            available_tools: List of available tools
            
        Returns:
            ToolValidationResult with orphaned tools and validation errors
        """
        try:
            logger.debug("Starting tool flow validation",
                        message_count=len(messages),
                        available_tool_count=len(available_tools))
            
            # Use task function for validation
            result = validate_tool_flow_data(messages, available_tools)
            
            logger.info("Tool flow validation completed",
                       is_valid=result.is_valid,
                       orphaned_count=len(result.orphaned_tools),
                       missing_results_count=len(result.missing_results))
            
            return result
            
        except Exception as e:
            logger.error("Tool flow validation flow failed", error=str(e), exc_info=True)
            raise
    
    async def batch_validate_tools(self, tools: List[Tool]) -> List[ValidationResult]:
        """Validate multiple tools in batch.
        
        Args:
            tools: List of tools to validate
            
        Returns:
            List of ValidationResult objects
        """
        try:
            logger.debug("Starting batch tool validation", tool_count=len(tools))
            
            results = []
            for i, tool in enumerate(tools):
                try:
                    result = await self.validate_tool(tool)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to validate tool {i}", error=str(e))
                    results.append(create_validation_result(
                        False,
                        errors=[f"Tool {i} validation failed: {str(e)}"]
                    ))
            
            valid_count = sum(1 for r in results if r.is_valid)
            logger.info("Batch tool validation completed",
                       total_tools=len(tools),
                       valid_tools=valid_count,
                       invalid_tools=len(tools) - valid_count)
            
            return results
            
        except Exception as e:
            logger.error("Batch tool validation flow failed", error=str(e), exc_info=True)
            return [create_validation_result(
                False,
                errors=[f"Batch validation failed: {str(e)}"]
            ) for _ in tools]
    
    async def validate_tool_schema_compatibility(
        self,
        tool: Tool,
        input_data: dict
    ) -> ValidationResult:
        """Validate that input data matches tool schema.
        
        Args:
            tool: Tool definition with schema
            input_data: Input data to validate against schema
            
        Returns:
            ValidationResult indicating schema compatibility
        """
        try:
            logger.debug("Starting tool schema compatibility validation",
                        tool_name=getattr(tool, 'name', 'unknown'))
            
            # First validate the tool itself
            tool_result = await self.validate_tool(tool)
            if not tool_result.is_valid:
                return tool_result
            
            # TODO: Add actual schema validation logic here
            # For now, basic validation
            errors = []
            warnings = []
            suggestions = []
            
            if not isinstance(input_data, dict):
                errors.append("Input data must be a dictionary")
            
            is_valid = len(errors) == 0
            
            result = create_validation_result(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions
            )
            
            logger.debug("Tool schema compatibility validation completed",
                        is_valid=result.is_valid)
            
            return result
            
        except Exception as e:
            logger.error("Tool schema compatibility validation failed", error=str(e), exc_info=True)
            return create_validation_result(
                False,
                errors=[f"Schema compatibility validation failed: {str(e)}"]
            )