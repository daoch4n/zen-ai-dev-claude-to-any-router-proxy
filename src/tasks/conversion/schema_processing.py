"""Schema processing tasks for OpenRouter Anthropic Server.

Prefect tasks for cleaning schemas and processing tool definitions.
Part of Phase 6A comprehensive refactoring - Conversion Tasks.
"""

from typing import Any, Dict, List

from prefect import task

from ...models.anthropic import Tool
from ...models.instructor import ConversionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager

# Initialize logging and context management
logger = get_logger("schema_processing")
context_manager = ContextManager()


@task(name="clean_openrouter_schema")
async def clean_openrouter_schema_task(
    schema: Any
) -> ConversionResult:
    """
    Recursively clean JSON schema for OpenRouter compatibility.
    
    Removes unsupported fields that might cause OpenRouter to reject requests.
    
    Args:
        schema: JSON schema to clean
    
    Returns:
        ConversionResult with cleaned schema
    """
    try:
        cleaned_schema = _clean_schema_recursive(schema)
        
        # Count removed fields for metrics
        original_fields = _count_schema_fields(schema) if isinstance(schema, dict) else 0
        cleaned_fields = _count_schema_fields(cleaned_schema) if isinstance(cleaned_schema, dict) else 0
        removed_fields = original_fields - cleaned_fields
        
        logger.debug("Schema cleaning completed",
                    original_fields=original_fields,
                    cleaned_fields=cleaned_fields,
                    removed_fields=removed_fields)
        
        return ConversionResult(
            success=True,
            converted_data=cleaned_schema,
            metadata={
                "original_fields": original_fields,
                "cleaned_fields": cleaned_fields,
                "removed_fields": removed_fields
            }
        )
        
    except Exception as e:
        error_msg = f"Schema cleaning failed: {str(e)}"
        logger.error("Schema cleaning failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=schema  # Return original on failure
        )


def _clean_schema_recursive(schema: Any) -> Any:
    """Recursively clean schema fields."""
    if isinstance(schema, dict):
        # Remove specific keys that might be unsupported by OpenRouter
        cleaned_schema = schema.copy()  # Don't modify the original
        cleaned_schema.pop("additionalProperties", None)
        cleaned_schema.pop("default", None)
        cleaned_schema.pop("$schema", None)  # Remove JSON schema metadata
        
        # Check for unsupported 'format' in string types
        if cleaned_schema.get("type") == "string" and "format" in cleaned_schema:
            allowed_formats = {"enum", "date-time"}  # Safe subset
            if cleaned_schema["format"] not in allowed_formats:
                logger.debug("Removing unsupported format for string type in OpenRouter schema",
                            format_removed=cleaned_schema["format"])
                cleaned_schema.pop("format")
        
        # Recursively clean nested schemas
        for key, value in list(cleaned_schema.items()):
            cleaned_schema[key] = _clean_schema_recursive(value)
        
        return cleaned_schema
    
    elif isinstance(schema, list):
        # Recursively clean items in a list
        return [_clean_schema_recursive(item) for item in schema]
    
    return schema


def _count_schema_fields(schema: Dict[str, Any]) -> int:
    """Count total fields in a schema recursively."""
    if not isinstance(schema, dict):
        return 0
    
    count = len(schema)
    for value in schema.values():
        if isinstance(value, dict):
            count += _count_schema_fields(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    count += _count_schema_fields(item)
    
    return count


@task(name="validate_tool_schema")
async def validate_tool_schema_task(
    tool_schema: Dict[str, Any]
) -> ConversionResult:
    """
    Validate tool schema for completeness and correctness.
    
    Args:
        tool_schema: Tool schema to validate
    
    Returns:
        ConversionResult with validation status and details
    """
    try:
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "schema_info": {}
        }
        
        # Check required top-level fields
        required_fields = ["name", "description", "input_schema"]
        for field in required_fields:
            if field not in tool_schema:
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False
        
        # Validate name
        if "name" in tool_schema:
            name = tool_schema["name"]
            if not isinstance(name, str) or not name.strip():
                validation_result["errors"].append("Tool name must be a non-empty string")
                validation_result["is_valid"] = False
            elif not name.replace("_", "").replace("-", "").isalnum():
                validation_result["warnings"].append("Tool name should contain only alphanumeric characters, hyphens, and underscores")
        
        # Validate description
        if "description" in tool_schema:
            description = tool_schema["description"]
            if description is not None and not isinstance(description, str):
                validation_result["errors"].append("Tool description must be a string or null")
                validation_result["is_valid"] = False
            elif description and len(description) > 1000:
                validation_result["warnings"].append("Tool description is very long (>1000 chars)")
        
        # Validate input_schema
        if "input_schema" in tool_schema:
            input_schema = tool_schema["input_schema"]
            if not isinstance(input_schema, dict):
                validation_result["errors"].append("input_schema must be a dictionary")
                validation_result["is_valid"] = False
            else:
                # Basic JSON schema validation
                schema_validation = _validate_json_schema(input_schema)
                validation_result["errors"].extend(schema_validation["errors"])
                validation_result["warnings"].extend(schema_validation["warnings"])
                validation_result["schema_info"] = schema_validation["info"]
                
                if schema_validation["errors"]:
                    validation_result["is_valid"] = False
        
        # Add summary information
        validation_result["summary"] = {
            "total_errors": len(validation_result["errors"]),
            "total_warnings": len(validation_result["warnings"]),
            "is_valid": validation_result["is_valid"]
        }
        
        logger.info("Tool schema validation completed",
                   tool_name=tool_schema.get("name", "unknown"),
                   is_valid=validation_result["is_valid"],
                   error_count=len(validation_result["errors"]),
                   warning_count=len(validation_result["warnings"]))
        
        return ConversionResult(
            success=True,
            converted_data=validation_result,
            metadata={
                "tool_name": tool_schema.get("name"),
                "is_valid": validation_result["is_valid"],
                "error_count": len(validation_result["errors"]),
                "warning_count": len(validation_result["warnings"])
            }
        )
        
    except Exception as e:
        error_msg = f"Tool schema validation failed: {str(e)}"
        logger.error("Tool schema validation failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


def _validate_json_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate JSON schema structure."""
    validation = {
        "errors": [],
        "warnings": [],
        "info": {}
    }
    
    # Check for required JSON schema fields
    if "type" not in schema:
        validation["errors"].append("JSON schema missing 'type' field")
    
    # Validate type field
    if "type" in schema:
        valid_types = ["object", "array", "string", "number", "integer", "boolean", "null"]
        schema_type = schema["type"]
        if schema_type not in valid_types:
            validation["errors"].append(f"Invalid schema type: {schema_type}")
    
    # Check properties for object types
    if schema.get("type") == "object":
        if "properties" not in schema:
            validation["warnings"].append("Object schema without properties field")
        elif not isinstance(schema["properties"], dict):
            validation["errors"].append("Properties field must be a dictionary")
        else:
            validation["info"]["property_count"] = len(schema["properties"])
            
            # Validate nested properties
            for prop_name, prop_schema in schema["properties"].items():
                if not isinstance(prop_schema, dict):
                    validation["errors"].append(f"Property '{prop_name}' schema must be a dictionary")
    
    # Check for common fields
    if "description" in schema and not isinstance(schema["description"], str):
        validation["errors"].append("Schema description must be a string")
    
    # Check for problematic fields that might cause issues
    problematic_fields = ["$ref", "allOf", "anyOf", "oneOf", "not"]
    for field in problematic_fields:
        if field in schema:
            validation["warnings"].append(f"Schema contains potentially problematic field: {field}")
    
    return validation


@task(name="convert_tool_definition")
async def convert_tool_definition_task(
    tool_data: Dict[str, Any],
    target_format: str = "litellm"
) -> ConversionResult:
    """
    Convert tool definition between Anthropic and LiteLLM formats.
    
    Args:
        tool_data: Tool definition to convert
        target_format: Target format ("litellm" or "anthropic")
    
    Returns:
        ConversionResult with converted tool definition
    """
    try:
        if target_format == "litellm":
            return await _convert_anthropic_tool_to_litellm(tool_data)
        elif target_format == "anthropic":
            return await _convert_litellm_tool_to_anthropic(tool_data)
        else:
            raise ValueError(f"Unsupported target format: {target_format}")
            
    except Exception as e:
        error_msg = f"Tool definition conversion failed: {str(e)}"
        logger.error("Tool definition conversion failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


async def _convert_anthropic_tool_to_litellm(tool_data: Dict[str, Any]) -> ConversionResult:
    """Convert Anthropic tool to LiteLLM format."""
    tool = Tool(**tool_data)
    
    # Clean the schema for OpenRouter compatibility
    clean_schema_result = await clean_openrouter_schema_task(tool.input_schema)
    cleaned_schema = clean_schema_result.converted_data if clean_schema_result.success else tool.input_schema
    
    # Convert to LiteLLM format (OpenRouter uses standard OpenAI nested format)
    converted_tool = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": cleaned_schema
        }
    }
    
    logger.debug("Anthropic tool converted to LiteLLM",
                tool_name=tool.name,
                has_description=bool(tool.description),
                schema_cleaned=clean_schema_result.success)
    
    return ConversionResult(
        success=True,
        converted_data=converted_tool,
        metadata={
            "tool_name": tool.name,
            "conversion_direction": "anthropic_to_litellm",
            "schema_cleaned": clean_schema_result.success
        }
    )


async def _convert_litellm_tool_to_anthropic(tool_data: Dict[str, Any]) -> ConversionResult:
    """Convert LiteLLM tool to Anthropic format."""
    function_def = tool_data.get("function", {})
    
    converted_tool = {
        "name": function_def.get("name", ""),
        "description": function_def.get("description"),
        "input_schema": function_def.get("parameters", {})
    }
    
    # Validate the converted tool
    validation_result = await validate_tool_schema_task(converted_tool)
    
    logger.debug("LiteLLM tool converted to Anthropic",
                tool_name=converted_tool["name"],
                is_valid=validation_result.converted_data.get("is_valid", False) if validation_result.success else False)
    
    return ConversionResult(
        success=True,
        converted_data=converted_tool,
        metadata={
            "tool_name": converted_tool["name"],
            "conversion_direction": "litellm_to_anthropic",
            "validation_performed": validation_result.success
        }
    )


@task(name="batch_clean_tool_schemas")
async def batch_clean_tool_schemas_task(
    tools: List[Dict[str, Any]]
) -> ConversionResult:
    """
    Clean schemas for multiple tools in batch.
    
    Args:
        tools: List of tool definitions
    
    Returns:
        ConversionResult with cleaned tools
    """
    try:
        cleaned_tools = []
        cleaning_stats = {
            "total_tools": len(tools),
            "successfully_cleaned": 0,
            "cleaning_errors": 0,
            "total_fields_removed": 0
        }
        
        for i, tool in enumerate(tools):
            if "input_schema" in tool:
                # Clean the input schema
                clean_result = await clean_openrouter_schema_task(tool["input_schema"])
                
                if clean_result.success:
                    cleaned_tool = tool.copy()
                    cleaned_tool["input_schema"] = clean_result.converted_data
                    cleaned_tools.append(cleaned_tool)
                    
                    cleaning_stats["successfully_cleaned"] += 1
                    if clean_result.metadata:
                        cleaning_stats["total_fields_removed"] += clean_result.metadata.get("removed_fields", 0)
                else:
                    # Use original tool if cleaning failed
                    cleaned_tools.append(tool)
                    cleaning_stats["cleaning_errors"] += 1
                    logger.warning("Failed to clean tool schema", 
                                 tool_index=i,
                                 tool_name=tool.get("name", "unknown"))
            else:
                # Tool without input_schema, use as-is
                cleaned_tools.append(tool)
        
        logger.info("Batch tool schema cleaning completed", **cleaning_stats)
        
        return ConversionResult(
            success=True,
            converted_data=cleaned_tools,
            metadata=cleaning_stats
        )
        
    except Exception as e:
        error_msg = f"Batch tool schema cleaning failed: {str(e)}"
        logger.error("Batch tool schema cleaning failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=tools  # Return original tools on failure
        )


@task(name="extract_schema_metadata")
async def extract_schema_metadata_task(
    schema: Dict[str, Any]
) -> ConversionResult:
    """
    Extract metadata information from a JSON schema.
    
    Args:
        schema: JSON schema to analyze
    
    Returns:
        ConversionResult with schema metadata
    """
    try:
        metadata = {
            "schema_type": schema.get("type"),
            "has_properties": "properties" in schema,
            "property_count": 0,
            "required_properties": [],
            "optional_properties": [],
            "nested_schemas": 0,
            "max_depth": 0
        }
        
        # Count properties
        if "properties" in schema and isinstance(schema["properties"], dict):
            metadata["property_count"] = len(schema["properties"])
            
            # Categorize required vs optional properties
            required = schema.get("required", [])
            for prop_name in schema["properties"].keys():
                if prop_name in required:
                    metadata["required_properties"].append(prop_name)
                else:
                    metadata["optional_properties"].append(prop_name)
        
        # Calculate schema depth and count nested schemas
        metadata["max_depth"] = _calculate_schema_depth(schema)
        metadata["nested_schemas"] = _count_nested_schemas(schema)
        
        # Check for complex patterns
        metadata["has_complex_patterns"] = any(
            key in schema for key in ["allOf", "anyOf", "oneOf", "not", "$ref"]
        )
        
        # Estimate schema complexity score
        complexity_score = (
            metadata["property_count"] +
            metadata["nested_schemas"] * 2 +
            metadata["max_depth"] * 1.5 +
            (10 if metadata["has_complex_patterns"] else 0)
        )
        metadata["complexity_score"] = int(complexity_score)
        
        logger.debug("Schema metadata extracted",
                    schema_type=metadata["schema_type"],
                    property_count=metadata["property_count"],
                    complexity_score=metadata["complexity_score"])
        
        return ConversionResult(
            success=True,
            converted_data=metadata,
            metadata={
                "schema_type": metadata["schema_type"],
                "complexity_score": metadata["complexity_score"]
            }
        )
        
    except Exception as e:
        error_msg = f"Schema metadata extraction failed: {str(e)}"
        logger.error("Schema metadata extraction failed", error=error_msg, exc_info=True)
        
        return ConversionResult(
            success=False,
            errors=[error_msg],
            converted_data=None
        )


def _calculate_schema_depth(schema: Any, current_depth: int = 0) -> int:
    """Calculate maximum depth of a JSON schema."""
    if not isinstance(schema, dict):
        return current_depth
    
    max_depth = current_depth
    
    # Check properties
    if "properties" in schema and isinstance(schema["properties"], dict):
        for prop_schema in schema["properties"].values():
            depth = _calculate_schema_depth(prop_schema, current_depth + 1)
            max_depth = max(max_depth, depth)
    
    # Check array items
    if "items" in schema:
        depth = _calculate_schema_depth(schema["items"], current_depth + 1)
        max_depth = max(max_depth, depth)
    
    # Check additional properties
    if "additionalProperties" in schema and isinstance(schema["additionalProperties"], dict):
        depth = _calculate_schema_depth(schema["additionalProperties"], current_depth + 1)
        max_depth = max(max_depth, depth)
    
    return max_depth


def _count_nested_schemas(schema: Any) -> int:
    """Count number of nested schemas in a JSON schema."""
    if not isinstance(schema, dict):
        return 0
    
    count = 0
    
    # Count properties as nested schemas
    if "properties" in schema and isinstance(schema["properties"], dict):
        for prop_schema in schema["properties"].values():
            count += 1 + _count_nested_schemas(prop_schema)
    
    # Count array items
    if "items" in schema:
        count += 1 + _count_nested_schemas(schema["items"])
    
    # Count additional properties
    if "additionalProperties" in schema and isinstance(schema["additionalProperties"], dict):
        count += 1 + _count_nested_schemas(schema["additionalProperties"])
    
    return count