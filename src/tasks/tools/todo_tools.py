"""Todo operation Prefect tasks for OpenRouter Anthropic Server.

Converts TodoToolExecutor methods into modular Prefect tasks.
Part of Phase 6A comprehensive refactoring - Task-per-Tool Architecture.
"""

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List

from prefect import task

from ...services.tool_execution import ToolExecutionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager

# Initialize logging and context management
logger = get_logger("todo_tools")
context_manager = ContextManager()

# Default todo file
TODO_FILE = "claude_todos.json"


class SecurityValidator:
    """Security validation for todo inputs"""
    
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


def _get_todo_file_path() -> Path:
    """Get the path to the todo file"""
    return _get_safe_path(TODO_FILE)


def _load_todos() -> List[Dict[str, Any]]:
    """Load todos from file"""
    todo_path = _get_todo_file_path()
    
    if not todo_path.exists():
        return []
    
    try:
        with open(todo_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('todos', [])
    except (json.JSONDecodeError, KeyError):
        return []


def _save_todos(todos: List[Dict[str, Any]]) -> None:
    """Save todos to file"""
    todo_path = _get_todo_file_path()
    
    data = {
        'todos': todos,
        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(todo_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@task(name="read_todos", retries=2, retry_delay_seconds=1)
async def read_todos_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic todo read operation as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (TodoRead)
        tool_input: Dictionary containing optional status_filter and priority_filter
    
    Returns:
        ToolExecutionResult with todo list or error
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
        status_filter = tool_input.get('status_filter', 'all')
        priority_filter = tool_input.get('priority_filter')
        
        # Load todos
        todos = _load_todos()
        
        # Apply filters
        filtered_todos = []
        for todo in todos:
            # Status filter
            if status_filter != 'all':
                if status_filter == 'pending' and todo.get('completed', False):
                    continue
                if status_filter == 'completed' and not todo.get('completed', False):
                    continue
            
            # Priority filter
            if priority_filter and todo.get('priority') != priority_filter:
                continue
            
            filtered_todos.append(todo)
        
        # Format output in beautiful markdown style
        if not filtered_todos:
            result_content = "# 📋 Todo List\n\n*No todos found matching the criteria*"
        else:
            result_lines = [f"# 📋 Todo List ({len(filtered_todos)} items)\n"]
            
            # Group todos by priority
            priority_groups = {'high': [], 'medium': [], 'low': []}
            for todo in filtered_todos:
                priority = todo.get('priority', 'medium').lower()
                if priority not in priority_groups:
                    priority = 'medium'
                priority_groups[priority].append(todo)
            
            # Priority display order and styling
            priority_display = {
                'high': {'emoji': '🔥', 'title': 'High Priority'},
                'medium': {'emoji': '⚡', 'title': 'Medium Priority'},
                'low': {'emoji': '📌', 'title': 'Low Priority'}
            }
            
            for priority in ['high', 'medium', 'low']:
                todos_in_priority = priority_groups[priority]
                if not todos_in_priority:
                    continue
                
                display_info = priority_display[priority]
                result_lines.append(f"## {display_info['emoji']} {display_info['title']}\n")
                
                for todo in todos_in_priority:
                    # Status checkbox
                    checkbox = "- [x]" if todo.get('completed', False) else "- [ ]"
                    title = todo.get('title', 'Untitled')
                    todo_id = todo.get('id', 'unknown')
                    
                    # Main todo line
                    result_lines.append(f"{checkbox} **{title}** *(ID: {todo_id})*")
                    
                    # Description with quote formatting
                    if todo.get('description'):
                        result_lines.append(f"  > {todo['description']}")
                    
                    # Additional info line
                    info_parts = []
                    if todo.get('due_date'):
                        info_parts.append(f"📅 Due: {todo['due_date']}")
                    if todo.get('tags'):
                        info_parts.append(f"🏷️ Tags: {', '.join(todo['tags'])}")
                    if todo.get('completed') and todo.get('completed_at'):
                        info_parts.append(f"✅ Completed: {todo['completed_at']}")
                    elif todo.get('created_at'):
                        info_parts.append(f"📝 Created: {todo['created_at']}")
                    
                    if info_parts:
                        result_lines.append(f"  {' | '.join(info_parts)}")
                    
                    result_lines.append("")  # Empty line between todos
                
                result_lines.append("")  # Empty line between priority sections
            
            result_content = '\n'.join(result_lines)
        
        logger.info("TodoRead tool executed successfully",
                   total_todos=len(todos),
                   filtered_todos=len(filtered_todos),
                   status_filter=status_filter,
                   priority_filter=priority_filter,
                   tool_call_id=tool_call_id)
        
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=True,
            result=result_content,
            execution_time=time.time() - start_time
        )
        
    except Exception as e:
        error_msg = f"Failed to read todos: {e}"
        logger.error("TodoRead tool execution failed",
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


@task(name="write_todos", retries=2, retry_delay_seconds=1)
async def write_todos_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic todo write operation as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (TodoWrite)
        tool_input: Dictionary containing action and action-specific parameters
    
    Returns:
        ToolExecutionResult with operation result or error
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
        action = tool_input.get('action')
        
        if not action:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameter: action",
                execution_time=time.time() - start_time
            )
        
        # Load current todos
        todos = _load_todos()
        
        if action == 'add':
            title = tool_input.get('title')
            if not title:
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error="Missing required parameter for add action: title",
                    execution_time=time.time() - start_time
                )
            
            # Create new todo
            new_todo = {
                'id': str(uuid.uuid4())[:8],
                'title': title,
                'description': tool_input.get('description', ''),
                'priority': tool_input.get('priority', 'medium'),
                'due_date': tool_input.get('due_date'),
                'tags': tool_input.get('tags', []),
                'completed': False,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            todos.append(new_todo)
            result_message = f"Added new todo: '{title}' (ID: {new_todo['id']})"
            
        elif action in ['update', 'delete', 'complete']:
            todo_id = tool_input.get('todo_id')
            if not todo_id:
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=f"Missing required parameter for {action} action: todo_id",
                    execution_time=time.time() - start_time
                )
            
            # Find todo by ID
            todo_index = -1
            for i, todo in enumerate(todos):
                if todo.get('id') == todo_id:
                    todo_index = i
                    break
            
            if todo_index == -1:
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=f"Todo with ID '{todo_id}' not found",
                    execution_time=time.time() - start_time
                )
            
            if action == 'update':
                # Update fields if provided
                todo = todos[todo_index]
                if 'title' in tool_input:
                    todo['title'] = tool_input['title']
                if 'description' in tool_input:
                    todo['description'] = tool_input['description']
                if 'priority' in tool_input:
                    todo['priority'] = tool_input['priority']
                if 'due_date' in tool_input:
                    todo['due_date'] = tool_input['due_date']
                if 'tags' in tool_input:
                    todo['tags'] = tool_input['tags']
                
                todo['updated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                result_message = f"Updated todo '{todo['title']}' (ID: {todo_id})"
                
            elif action == 'delete':
                deleted_todo = todos.pop(todo_index)
                result_message = f"Deleted todo '{deleted_todo['title']}' (ID: {todo_id})"
                
            elif action == 'complete':
                todo = todos[todo_index]
                todo['completed'] = True
                todo['completed_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                result_message = f"Completed todo '{todo['title']}' (ID: {todo_id})"
        
        else:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Invalid action: '{action}'. Must be one of: add, update, delete, complete",
                execution_time=time.time() - start_time
            )
        
        # Save updated todos
        _save_todos(todos)
        
        logger.info("TodoWrite tool executed successfully",
                   action=action,
                   todo_count=len(todos),
                   todo_id=tool_input.get('todo_id') if action != 'add' else new_todo.get('id') if action == 'add' else None,
                   tool_call_id=tool_call_id)
        
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=True,
            result=result_message,
            execution_time=time.time() - start_time
        )
        
    except Exception as e:
        error_msg = f"Failed to write todos: {e}"
        logger.error("TodoWrite tool execution failed",
                    action=action,
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