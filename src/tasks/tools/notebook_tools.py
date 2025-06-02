"""Notebook operation Prefect tasks for OpenRouter Anthropic Server.

Converts NotebookToolExecutor methods into modular Prefect tasks.
Part of Phase 6A comprehensive refactoring - Task-per-Tool Architecture.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from prefect import task

from ...services.tool_execution import ToolExecutionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager

# Initialize logging and context management
logger = get_logger("notebook_tools")
context_manager = ContextManager()


class SecurityValidator:
    """Security validation for notebook inputs"""
    
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


def _get_safe_path(file_path: str) -> Path:
    """Get safe, absolute path and ensure it's within allowed directory"""
    # First validate the path for security issues
    if not SecurityValidator.validate_path(file_path):
        raise ValueError(f"Invalid or unsafe path: {file_path}")
    
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
            abs_path = cwd / Path(file_path).name
        else:
            abs_path = cwd / file_path
    
    return abs_path


@task(name="read_notebook", retries=2, retry_delay_seconds=1)
async def read_notebook_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic notebook read operation as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (NotebookRead)
        tool_input: Dictionary containing file_path and optional cell_index
    
    Returns:
        ToolExecutionResult with notebook content or error
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
        cell_index = tool_input.get('cell_index')
        
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
                error=f"Notebook file not found: {safe_path}",
                execution_time=time.time() - start_time
            )
        
        # Read notebook JSON
        with open(safe_path, 'r', encoding='utf-8') as f:
            notebook_data = json.load(f)
        
        # Extract cells
        cells = notebook_data.get('cells', [])
        
        if cell_index is not None:
            # Read specific cell
            if cell_index < 0 or cell_index >= len(cells):
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=f"Cell index {cell_index} out of range (notebook has {len(cells)} cells)",
                    execution_time=time.time() - start_time
                )
            
            cell = cells[cell_index]
            result_lines = [f"Cell {cell_index} ({cell.get('cell_type', 'unknown')} cell):"]
            source = cell.get('source', [])
            if isinstance(source, list):
                result_lines.append(''.join(source))
            else:
                result_lines.append(str(source))
                
            result_content = '\n'.join(result_lines)
        else:
            # Read all cells
            result_lines = [f"Notebook: {safe_path} ({len(cells)} cells)\n"]
            
            for i, cell in enumerate(cells):
                cell_type = cell.get('cell_type', 'unknown')
                result_lines.append(f"Cell {i} ({cell_type}):")
                
                source = cell.get('source', [])
                if isinstance(source, list):
                    content = ''.join(source)
                else:
                    content = str(source)
                
                # Truncate long cells
                if len(content) > 500:
                    content = content[:500] + '\n[... truncated ...]'
                
                result_lines.append(content)
                result_lines.append("")  # Empty line between cells
            
            result_content = '\n'.join(result_lines)
        
        logger.info("NotebookRead tool executed successfully",
                   file_path=str(safe_path),
                   cell_count=len(cells),
                   specific_cell=cell_index,
                   tool_call_id=tool_call_id)
        
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=True,
            result=result_content,
            execution_time=time.time() - start_time
        )
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid notebook format in '{file_path}': {e}"
        logger.error("NotebookRead tool execution failed - JSON decode error",
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
        error_msg = f"Failed to read notebook '{file_path}': {e}"
        logger.error("NotebookRead tool execution failed",
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


@task(name="edit_notebook", retries=2, retry_delay_seconds=1)
async def edit_notebook_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic notebook edit operation as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (NotebookEdit)
        tool_input: Dictionary containing file_path, cell_index, new_content, optional cell_type
    
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
        cell_index = tool_input.get('cell_index')
        new_content = tool_input.get('new_content')
        cell_type = tool_input.get('cell_type')
        
        if not file_path or cell_index is None or new_content is None:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameters: file_path, cell_index, new_content",
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
                error=f"Notebook file not found: {safe_path}",
                execution_time=time.time() - start_time
            )
        
        # Read notebook JSON
        with open(safe_path, 'r', encoding='utf-8') as f:
            notebook_data = json.load(f)
        
        # Extract cells
        cells = notebook_data.get('cells', [])
        
        if cell_index < 0 or cell_index >= len(cells):
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Cell index {cell_index} out of range (notebook has {len(cells)} cells)",
                execution_time=time.time() - start_time
            )
        
        # Update cell content
        cell = cells[cell_index]
        
        # Convert new_content to proper format (list of strings)
        if isinstance(new_content, str):
            # Split by lines but preserve line endings
            lines = new_content.splitlines(keepends=True)
            # Ensure last line has newline if original didn't
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            cell['source'] = lines
        else:
            cell['source'] = new_content
        
        # Update cell type if specified
        if cell_type and cell_type in ['code', 'markdown', 'raw']:
            cell['cell_type'] = cell_type
        
        # Write updated notebook
        with open(safe_path, 'w', encoding='utf-8') as f:
            json.dump(notebook_data, f, indent=1, ensure_ascii=False)
        
        result_message = f"Updated cell {cell_index} in notebook '{safe_path}'"
        logger.info("NotebookEdit tool executed successfully",
                   file_path=str(safe_path),
                   cell_index=cell_index,
                   cell_type=cell_type,
                   content_length=len(new_content) if isinstance(new_content, str) else 0,
                   tool_call_id=tool_call_id)
        
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=True,
            result=result_message,
            execution_time=time.time() - start_time
        )
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid notebook format in '{file_path}': {e}"
        logger.error("NotebookEdit tool execution failed - JSON decode error",
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
        error_msg = f"Failed to edit notebook '{file_path}': {e}"
        logger.error("NotebookEdit tool execution failed",
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