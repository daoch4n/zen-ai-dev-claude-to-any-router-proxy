"""Search operation Prefect tasks for OpenRouter Anthropic Server.

Converts SearchToolExecutor methods into modular Prefect tasks.
Part of Phase 6A comprehensive refactoring - Task-per-Tool Architecture.
"""

import glob as glob_module
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List

from prefect import task

from ...tasks.tool_execution.tool_result_formatting_tasks import ToolExecutionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager

# Initialize logging and context management
logger = get_logger("search_tools")
context_manager = ContextManager()


class SecurityValidator:
    """Security validation for search inputs"""
    
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
    def validate_search_path(path: str) -> bool:
        """Validate search path for security issues"""
        if not path:
            return False
        
        # Check for dangerous patterns
        for pattern in SecurityValidator.DANGEROUS_PATH_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                logger.warning("Dangerous path pattern detected in search", pattern=pattern, path=path)
                return False
        
        # Check absolute paths - allow /tmp/ and current working directory
        if path.startswith('/'):
            cwd = str(Path.cwd())
            if not (path.startswith('/tmp/') or path.startswith(cwd)):
                logger.warning("Absolute search path outside allowed directories", path=path, allowed_dirs=["/tmp/", "current_directory"])
                return False
        
        return True


def _get_safe_search_path(search_path: str) -> Path:
    """Get safe, absolute path for searching"""
    # First validate the path for security issues
    if not SecurityValidator.validate_search_path(search_path):
        raise ValueError(f"Invalid or unsafe search path: {search_path}")
    
    # Convert to absolute path
    if search_path == '.':
        return Path.cwd()
    
    abs_path = Path(search_path).resolve()
    
    # Get current working directory as base
    cwd = Path.cwd()
    
    # Ensure the path is within current working directory or its subdirectories
    try:
        abs_path.relative_to(cwd)
    except ValueError:
        # Path is outside current directory, make it relative to cwd
        if abs_path.is_absolute():
            # If it's an absolute path outside cwd, default to current directory
            abs_path = cwd
        else:
            abs_path = cwd / search_path
    
    return abs_path


@task(name="glob_search", retries=2, retry_delay_seconds=1)
async def glob_search_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic glob search operation as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (Glob)
        tool_input: Dictionary containing pattern and optional directory
    
    Returns:
        ToolExecutionResult with matching files or error
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
        pattern = tool_input.get('pattern')
        directory = tool_input.get('directory', '.')
        
        if not pattern:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameter: pattern",
                execution_time=time.time() - start_time
            )
        
        # Get safe search path
        search_path = _get_safe_search_path(directory)
        
        # Change to search directory temporarily
        old_cwd = Path.cwd()
        try:
            os.chdir(search_path)
            
            # Perform glob search
            matches = glob_module.glob(pattern, recursive=True)
            
            # Sort results for consistent output
            matches.sort()
            
            if not matches:
                result = f"No files found matching pattern '{pattern}' in {search_path}"
            else:
                result_lines = [f"Found {len(matches)} files matching '{pattern}' in {search_path}:"]
                result_lines.extend(f"  {match}" for match in matches)
                result = "\n".join(result_lines)
            
            logger.info("Glob search executed successfully",
                       pattern=pattern,
                       directory=str(search_path),
                       match_count=len(matches),
                       tool_call_id=tool_call_id)
            
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=True,
                result=result,
                execution_time=time.time() - start_time
            )
            
        finally:
            # Restore original working directory
            os.chdir(old_cwd)
            
    except Exception as e:
        error_msg = f"Failed to execute glob search for pattern '{pattern}': {e}"
        logger.error("Glob search execution failed",
                    pattern=pattern,
                    directory=directory,
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


@task(name="grep_search", retries=2, retry_delay_seconds=1)
async def grep_search_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic grep search operation as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (Grep)
        tool_input: Dictionary containing pattern, path, and optional flags
    
    Returns:
        ToolExecutionResult with matching lines or error
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
        pattern = tool_input.get('pattern')
        search_path = tool_input.get('path', '.')
        case_sensitive = tool_input.get('case_sensitive', True)
        max_matches = tool_input.get('max_matches', 100)
        
        if not pattern:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameter: pattern",
                execution_time=time.time() - start_time
            )
        
        # Get safe search path
        safe_path = _get_safe_search_path(search_path)
        
        # Compile regex pattern
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Invalid regex pattern: {e}",
                execution_time=time.time() - start_time
            )
        
        matches = []
        total_files_searched = 0
        
        # Search through files
        if safe_path.is_file():
            # Search single file
            try:
                content = safe_path.read_text(encoding='utf-8')
                total_files_searched = 1
                
                for line_num, line in enumerate(content.splitlines(), 1):
                    if regex.search(line):
                        matches.append(f"{safe_path}:{line_num}:{line.strip()}")
                        if len(matches) >= max_matches:
                            break
            except UnicodeDecodeError:
                logger.debug("Skipping binary file", file=str(safe_path))
        else:
            # Search directory recursively
            for file_path in safe_path.rglob('*'):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        total_files_searched += 1
                        
                        for line_num, line in enumerate(content.splitlines(), 1):
                            if regex.search(line):
                                matches.append(f"{file_path}:{line_num}:{line.strip()}")
                                if len(matches) >= max_matches:
                                    break
                        
                        if len(matches) >= max_matches:
                            break
                            
                    except (UnicodeDecodeError, PermissionError):
                        # Skip binary files and files without permission
                        continue
        
        if not matches:
            result = f"No matches found for pattern '{pattern}' in {safe_path} ({total_files_searched} files searched)"
        else:
            result_lines = [f"Found {len(matches)} matches for '{pattern}' in {safe_path} ({total_files_searched} files searched):"]
            result_lines.extend(matches)
            if len(matches) >= max_matches:
                result_lines.append(f"... (limited to {max_matches} matches)")
            result = "\n".join(result_lines)
        
        logger.info("Grep search executed successfully",
                   pattern=pattern,
                   path=str(safe_path),
                   match_count=len(matches),
                   files_searched=total_files_searched,
                   case_sensitive=case_sensitive,
                   tool_call_id=tool_call_id)
        
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=True,
            result=result,
            execution_time=time.time() - start_time
        )
        
    except Exception as e:
        error_msg = f"Failed to execute grep search for pattern '{pattern}': {e}"
        logger.error("Grep search execution failed",
                    pattern=pattern,
                    path=search_path,
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


@task(name="list_directory", retries=2, retry_delay_seconds=1)
async def list_directory_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic directory listing operation as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (LS)
        tool_input: Dictionary containing path and optional flags
    
    Returns:
        ToolExecutionResult with directory listing or error
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
        directory_path = tool_input.get('path', '.')
        show_all = tool_input.get('all', False)  # Show hidden files
        long_format = tool_input.get('long', False)  # Show detailed info
        
        # Get safe search path
        safe_path = _get_safe_search_path(directory_path)
        
        if not safe_path.exists():
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Path does not exist: {safe_path}",
                execution_time=time.time() - start_time
            )
        
        if not safe_path.is_dir():
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Path is not a directory: {safe_path}",
                execution_time=time.time() - start_time
            )
        
        # List directory contents
        entries = []
        try:
            for item in safe_path.iterdir():
                # Skip hidden files unless show_all is True
                if not show_all and item.name.startswith('.'):
                    continue
                
                if long_format:
                    # Show detailed information
                    try:
                        stat = item.stat()
                        size = stat.st_size
                        mtime = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))
                        file_type = 'd' if item.is_dir() else '-'
                        permissions = oct(stat.st_mode)[-3:]
                        
                        entries.append(f"{file_type}{permissions} {size:>10} {mtime} {item.name}")
                    except (PermissionError, OSError):
                        entries.append(f"??????? {item.name} (permission denied)")
                else:
                    # Simple listing
                    if item.is_dir():
                        entries.append(f"{item.name}/")
                    else:
                        entries.append(item.name)
                        
        except PermissionError:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Permission denied accessing directory: {safe_path}",
                execution_time=time.time() - start_time
            )
        
        # Sort entries
        entries.sort()
        
        if not entries:
            result = f"Directory '{safe_path}' is empty"
        else:
            header = f"Contents of '{safe_path}' ({len(entries)} items):"
            if long_format:
                header += "\nType Perm      Size Modified         Name"
                header += "\n" + "-" * 50
            result = header + "\n" + "\n".join(entries)
        
        logger.info("Directory listing executed successfully",
                   path=str(safe_path),
                   item_count=len(entries),
                   show_all=show_all,
                   long_format=long_format,
                   tool_call_id=tool_call_id)
        
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=True,
            result=result,
            execution_time=time.time() - start_time
        )
        
    except Exception as e:
        error_msg = f"Failed to list directory '{directory_path}': {e}"
        logger.error("Directory listing execution failed",
                    path=directory_path,
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