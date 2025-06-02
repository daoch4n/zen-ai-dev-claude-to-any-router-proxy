"""File operation Prefect tasks for OpenRouter Anthropic Server.

Converts FileToolExecutor methods into modular Prefect tasks.
Part of Phase 6A comprehensive refactoring - Task-per-Tool Architecture.
"""

import time
from pathlib import Path
from typing import Any, Dict

from prefect import task

from ...services.tool_execution import ToolExecutionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager

# Initialize logging and context management
logger = get_logger("file_tools")
context_manager = ContextManager()


class ToolExecutorError(Exception):
    """Base exception for tool executor errors"""
    pass


class SecurityValidator:
    """Security validation for tool inputs (shared across all tool modules)"""
    
    # Dangerous path patterns
    DANGEROUS_PATH_PATTERNS = [
        r'\.\./',  # Path traversal
        r'/etc/',  # System config
        r'/proc/',  # Process info
        r'/sys/',  # System files
        r'/dev/',  # Device files
        r'~/',  # Home directory expansion
        r'\$\{',  # Variable expansion
        r'\$\(',  # Command substitution
    ]
    
    @staticmethod
    def validate_path(path: str) -> bool:
        """Validate path for security issues"""
        import re
        import os
        
        if not path:
            return False
        
        # Check for dangerous patterns
        for pattern in SecurityValidator.DANGEROUS_PATH_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                logger.warning("Dangerous path pattern detected", pattern=pattern, path=path)
                return False
        
        # Check absolute paths - allow /tmp/ and current working directory
        if path.startswith('/'):
            cwd = str(Path.cwd())
            if not (path.startswith('/tmp/') or path.startswith(cwd)):
                logger.warning("Absolute path outside allowed directories", path=path, allowed_dirs=["/tmp/", "current_directory"])
                return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent security issues"""
        import re
        import os
        
        # Remove any path components
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Ensure it doesn't start with a dot (hidden file)
        if filename.startswith('.'):
            filename = '_' + filename[1:]
        
        return filename


def _get_safe_path(file_path: str) -> Path:
    """Get safe, absolute path and ensure it's within allowed directory"""
    # First validate the path for security issues
    if not SecurityValidator.validate_path(file_path):
        raise ToolExecutorError(f"Invalid or unsafe path: {file_path}")
    
    # Convert to absolute path
    abs_path = Path(file_path).resolve()
    
    # Get current working directory as base
    cwd = Path.cwd()
    
    # Ensure the path is within current working directory or its subdirectories
    try:
        abs_path.relative_to(cwd)
    except ValueError:
        # Path is outside current directory, make it relative to cwd
        if abs_path.is_absolute():
            # If it's an absolute path outside cwd, treat as relative
            sanitized_name = SecurityValidator.sanitize_filename(Path(file_path).name)
            abs_path = cwd / sanitized_name
        else:
            abs_path = cwd / file_path
    
    return abs_path


@task(name="write_file", retries=2, retry_delay_seconds=1)
async def write_file_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic file write operation as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (Write)
        tool_input: Dictionary containing file_path and content
    
    Returns:
        ToolExecutionResult with success status and result
    """
    start_time = time.time()
    
    # Create tool context for structured logging
    context_manager.create_tool_context(
        tool_name=tool_name,
        tool_call_id=tool_call_id,
        input_data=tool_input,
        execution_step=1
    )
    
    try:
        file_path = tool_input.get('file_path')
        content = tool_input.get('content', '')
        
        if not file_path:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameter: file_path",
                execution_time=time.time() - start_time
            )
        
        # Get safe path
        safe_path = _get_safe_path(file_path)
        
        # Create parent directories if they don't exist
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to file
        safe_path.write_text(content, encoding='utf-8')
        
        result_message = f"File '{safe_path}' written successfully ({len(content)} characters)"
        logger.info("Write tool executed successfully",
                   file_path=str(safe_path),
                   content_length=len(content),
                   tool_call_id=tool_call_id)
        
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=True,
            result=result_message,
            execution_time=time.time() - start_time
        )
        
    except Exception as e:
        error_msg = f"Failed to write file '{file_path}': {e}"
        logger.error("Write tool execution failed",
                    file_path=file_path,
                    error=str(e),
                    tool_call_id=tool_call_id,
                    exc_info=True)
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=False,
            result=None,
            error=error_msg,
            execution_time=time.time() - start_time
        )


@task(name="read_file", retries=2, retry_delay_seconds=1)
async def read_file_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic file read operation as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (Read)
        tool_input: Dictionary containing file_path, optional offset and limit
    
    Returns:
        ToolExecutionResult with file content or error
    """
    start_time = time.time()
    
    # Create tool context for structured logging
    context_manager.create_tool_context(
        tool_name=tool_name,
        tool_call_id=tool_call_id,
        input_data=tool_input,
        execution_step=1
    )
    
    try:
        file_path = tool_input.get('file_path')
        offset = tool_input.get('offset')
        limit = tool_input.get('limit')
        
        if not file_path:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameter: file_path",
                execution_time=time.time() - start_time
            )
        
        # Get safe path
        safe_path = _get_safe_path(file_path)
        
        if not safe_path.exists():
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"File not found: {safe_path}",
                execution_time=time.time() - start_time
            )
        
        if not safe_path.is_file():
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Path is not a file: {safe_path}",
                execution_time=time.time() - start_time
            )
        
        # Read file content
        content = safe_path.read_text(encoding='utf-8')
        
        # Apply offset and limit if specified
        if offset is not None or limit is not None:
            lines = content.splitlines(keepends=True)
            
            start_line = max(0, (offset or 1) - 1)  # Convert to 0-indexed
            end_line = len(lines)
            
            if limit is not None:
                end_line = min(len(lines), start_line + limit)
            
            if start_line >= len(lines):
                content = ""
            else:
                content = ''.join(lines[start_line:end_line])
            
            result_info = f"Lines {start_line + 1}-{end_line} of {len(lines)} total lines"
        else:
            result_info = f"Complete file ({len(content.splitlines())} lines, {len(content)} characters)"
        
        logger.info("Read tool executed successfully",
                   file_path=str(safe_path),
                   result_info=result_info,
                   tool_call_id=tool_call_id)
        
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=True,
            result=content,
            execution_time=time.time() - start_time
        )
        
    except UnicodeDecodeError as e:
        error_msg = f"Cannot read file '{file_path}' as text: {e}"
        logger.error("Read tool execution failed - Unicode decode error",
                    file_path=file_path,
                    error=str(e),
                    tool_call_id=tool_call_id,
                    exc_info=True)
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=False,
            result=None,
            error=error_msg,
            execution_time=time.time() - start_time
        )
    except Exception as e:
        error_msg = f"Failed to read file '{file_path}': {e}"
        logger.error("Read tool execution failed",
                    file_path=file_path,
                    error=str(e),
                    tool_call_id=tool_call_id,
                    exc_info=True)
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=False,
            result=None,
            error=error_msg,
            execution_time=time.time() - start_time
        )


@task(name="edit_file", retries=2, retry_delay_seconds=1)
async def edit_file_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic file edit operation as Prefect task (string replacement).
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (Edit)
        tool_input: Dictionary containing file_path, old_string, new_string
    
    Returns:
        ToolExecutionResult with edit result or error
    """
    start_time = time.time()
    
    # Create tool context for structured logging
    context_manager.create_tool_context(
        tool_name=tool_name,
        tool_call_id=tool_call_id,
        input_data=tool_input,
        execution_step=1
    )
    
    try:
        file_path = tool_input.get('file_path')
        old_string = tool_input.get('old_string')
        new_string = tool_input.get('new_string', '')
        expected_replacements = tool_input.get('expected_replacements', 1)
        
        if not file_path or old_string is None:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameters: file_path, old_string",
                execution_time=time.time() - start_time
            )
        
        # Get safe path
        safe_path = _get_safe_path(file_path)
        
        if not safe_path.exists():
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"File not found: {safe_path}",
                execution_time=time.time() - start_time
            )
        
        # Read current content
        content = safe_path.read_text(encoding='utf-8')
        
        # Count potential replacements
        replacement_count = content.count(old_string)
        
        # Check if the replacement has already been made
        if replacement_count == 0:
            # Check if new_string is already in the file (indicating previous successful edit)
            if new_string and new_string in content:
                result_message = f"Edit already completed: '{new_string}' found in file '{safe_path}'"
                logger.info("Edit tool execution completed - already applied",
                           file_path=str(safe_path),
                           old_string=old_string[:100],
                           new_string=new_string[:100],
                           tool_call_id=tool_call_id)
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=True,
                    result=result_message,
                    execution_time=time.time() - start_time
                )
            else:
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=f"String not found in file: '{old_string}'",
                    execution_time=time.time() - start_time
                )
        
        if replacement_count != expected_replacements:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Expected {expected_replacements} replacements, but found {replacement_count} occurrences of '{old_string}'",
                execution_time=time.time() - start_time
            )
        
        # Perform replacement
        new_content = content.replace(old_string, new_string)
        
        # Write back to file
        safe_path.write_text(new_content, encoding='utf-8')
        
        result_message = f"File '{safe_path}' edited successfully ({replacement_count} replacements)"
        logger.info("Edit tool executed successfully",
                   file_path=str(safe_path),
                   replacement_count=replacement_count,
                   old_string=old_string[:100],
                   new_string=new_string[:100],
                   tool_call_id=tool_call_id)
        
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=True,
            result=result_message,
            execution_time=time.time() - start_time
        )
        
    except Exception as e:
        error_msg = f"Failed to edit file '{file_path}': {e}"
        logger.error("Edit tool execution failed",
                    file_path=file_path,
                    error=str(e),
                    tool_call_id=tool_call_id,
                    exc_info=True)
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=False,
            result=None,
            error=error_msg,
            execution_time=time.time() - start_time
        )


@task(name="multi_edit_file", retries=2, retry_delay_seconds=1)
async def multi_edit_file_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic multi-edit operation as Prefect task (multiple string replacements).
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (MultiEdit)
        tool_input: Dictionary containing file_path and edits list
    
    Returns:
        ToolExecutionResult with multi-edit result or error
    """
    start_time = time.time()
    
    # Create tool context for structured logging
    context_manager.create_tool_context(
        tool_name=tool_name,
        tool_call_id=tool_call_id,
        input_data=tool_input,
        execution_step=1
    )
    
    try:
        file_path = tool_input.get('file_path')
        edits = tool_input.get('edits', [])
        
        if not file_path:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameter: file_path",
                execution_time=time.time() - start_time
            )
        
        if not edits:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameter: edits (list of edit operations)",
                execution_time=time.time() - start_time
            )
        
        # Get safe path
        safe_path = _get_safe_path(file_path)
        
        if not safe_path.exists():
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"File not found: {safe_path}. MultiEdit only works on existing files.",
                execution_time=time.time() - start_time
            )
        
        # Read current content
        content = safe_path.read_text(encoding='utf-8')
        modified_content = content
        total_replacements = 0
        edit_details = []
        
        # Apply each edit operation
        for i, edit in enumerate(edits):
            if not isinstance(edit, dict):
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=f"Edit {i+1} is not a valid dictionary",
                    execution_time=time.time() - start_time
                )
            
            old_string = edit.get('old_string')
            new_string = edit.get('new_string', '')
            
            if old_string is None:
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=f"Edit {i+1} missing required 'old_string'",
                    execution_time=time.time() - start_time
                )
            
            # Count and perform replacement
            replacement_count = modified_content.count(old_string)
            if replacement_count > 0:
                modified_content = modified_content.replace(old_string, new_string)
                total_replacements += replacement_count
                edit_details.append(f"Edit {i+1}: {replacement_count} replacements")
            else:
                # Check if this edit was already applied
                if new_string and new_string in modified_content:
                    edit_details.append(f"Edit {i+1}: Already applied")
                else:
                    return ToolExecutionResult(
                        tool_call_id=tool_call_id,
                        tool_name=tool_name,
                        success=False,
                        result=None,
                        error=f"Edit {i+1}: String not found: '{old_string}'",
                        execution_time=time.time() - start_time
                    )
        
        # Write modified content back to file
        safe_path.write_text(modified_content, encoding='utf-8')
        
        result_message = f"File '{safe_path}' multi-edited successfully ({total_replacements} total replacements)\n" + "\n".join(edit_details)
        logger.info("MultiEdit tool executed successfully",
                   file_path=str(safe_path),
                   total_replacements=total_replacements,
                   edit_count=len(edits),
                   tool_call_id=tool_call_id)
        
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=True,
            result=result_message,
            execution_time=time.time() - start_time
        )
        
    except Exception as e:
        error_msg = f"Failed to multi-edit file '{file_path}': {e}"
        logger.error("MultiEdit tool execution failed",
                    file_path=file_path,
                    error=str(e),
                    tool_call_id=tool_call_id,
                    exc_info=True)
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=False,
            result=None,
            error=error_msg,
            execution_time=time.time() - start_time
        )