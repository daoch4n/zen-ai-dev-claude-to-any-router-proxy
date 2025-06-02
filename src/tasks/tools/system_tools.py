"""System operation Prefect tasks for OpenRouter Anthropic Server.

Converts SystemToolExecutor methods into modular Prefect tasks.
Part of Phase 6A comprehensive refactoring - Task-per-Tool Architecture.
"""

import json
import re
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

from prefect import task

from ...tasks.tool_execution.tool_result_formatting_tasks import ToolExecutionResult
from ...core.logging_config import get_logger
from ...services.context_manager import ContextManager

# Initialize logging and context management
logger = get_logger("system_tools")
context_manager = ContextManager()


class SecurityValidator:
    """Security validation for command inputs"""
    
    # Dangerous command patterns
    DANGEROUS_COMMAND_PATTERNS = [
        r'rm\s+.*-rf\s*/',  # Dangerous recursive deletion of root
        r'&&.*rm\s',  # Command chaining with rm
        r'\|\s*rm\s',  # Piping to rm
        r'>>\?\s*/dev/',  # Writing to devices
        r'mkfs',  # Filesystem creation
        r'dd\s',  # Disk operations
        r'shutdown',  # System shutdown
        r'reboot',  # System reboot
        r'systemctl',  # System control
        r'sudo',  # Privilege escalation
        r'su\s',  # Switch user
        r'chmod\s+[0-7]*7[0-7]*',  # World writable permissions
        r'\|\s*sh\s',  # Piping to shell
        r'\|\s*bash\s',  # Piping to bash
        r'\|\s*/bin/',  # Piping to system binaries
    ]
    
    @staticmethod
    def validate_command(command: str) -> bool:
        """Validate command for security issues"""
        if not command:
            return False
        
        # Check for dangerous patterns
        for pattern in SecurityValidator.DANGEROUS_COMMAND_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                logger.warning("Dangerous command pattern detected", pattern=pattern)
                return False
        
        # Check for shell metacharacters that could be dangerous
        dangerous_chars = ['`', '$', '\\']
        for char in dangerous_chars:
            if char in command:
                logger.warning("Dangerous character in command", character=char, command=command)
                return False
        
        return True


# Whitelist of safe commands
SAFE_COMMANDS = {
    'ls', 'pwd', 'whoami', 'date', 'echo', 'cat', 'head', 'tail', 
    'grep', 'find', 'wc', 'sort', 'uniq', 'cut', 'tr', 'sed', 'awk',
    'which', 'where', 'type', 'file', 'stat', 'du', 'df', 'ps',
    'uname', 'hostname', 'uptime', 'id', 'groups', 'env', 'printenv',
    'printf', 'python', 'python3', 'node', 'npm', 'uv', 'rm'
}

# File deletion patterns that require confirmation
FILE_DELETION_PATTERNS = [
    r'rm\s+.*\.(py|js|ts|jsx|tsx|json|yaml|yml|md|txt|csv|sql|html|css|scss|sass)(\s|$)',
    r'rm\s+.*\..*(\s|$)',  # Any file with extension
    r'rm\s+.*/',  # Directories
    r';\s*rm\s+(-[rf]*\s+)?[^/]*',  # Chained rm commands
    r'&&\s*rm\s+(-[rf]*\s+)?[^/]*',  # Conditional rm commands
]


def _is_safe_command(command: str) -> bool:
    """Check if command is safe to execute"""
    # First check with SecurityValidator
    if not SecurityValidator.validate_command(command):
        return False
    
    # Handle piped commands (e.g., "printf '...' | python script.py")
    if '|' in command:
        # Split by pipes and check each command
        pipe_parts = [part.strip() for part in command.split('|')]
        for part in pipe_parts:
            if not _is_single_command_safe(part):
                return False
        return True
    else:
        return _is_single_command_safe(command)


def _is_single_command_safe(command: str) -> bool:
    """Check if a single command (no pipes) is safe"""
    # Get the first word (command name)
    cmd_parts = command.strip().split()
    if not cmd_parts:
        return False
    
    base_cmd = cmd_parts[0]
    
    # Check against whitelist
    return base_cmd in SAFE_COMMANDS


def _requires_deletion_confirmation(command: str) -> bool:
    """Check if command requires user confirmation for file deletion"""
    for pattern in FILE_DELETION_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


@task(name="execute_command", retries=1, retry_delay_seconds=2)
async def execute_command_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic command execution as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (Bash)
        tool_input: Dictionary containing command, timeout, description, input
    
    Returns:
        ToolExecutionResult with command output or error
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
        command = tool_input.get('command')
        timeout = tool_input.get('timeout', 30)
        description = tool_input.get('description', '')
        stdin_input = tool_input.get('input')  # New parameter for stdin input
        user_confirmed = tool_input.get('user_confirmed_deletion', False)
        
        if not command:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameter: command",
                execution_time=time.time() - start_time
            )
        
        # Safety check for dangerous patterns FIRST (before deletion confirmation)
        if not _is_safe_command(command):
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Command not allowed for security reasons: {command.split()[0]}",
                execution_time=time.time() - start_time
            )
        
        # Check for file deletion commands (only for safe commands that need confirmation)
        if _requires_deletion_confirmation(command) and not user_confirmed:
            # Extract file names for user-friendly prompt
            try:
                cmd_parts = shlex.split(command)
                files_to_delete = [part for part in cmd_parts[1:] if not part.startswith('-')]
                if files_to_delete:
                    file_list = ", ".join(files_to_delete)
                    question = f"⚠️  This command will delete: {file_list}\n\nDo you want to proceed with this deletion? (This action cannot be undone)"
                else:
                    question = f"⚠️  This deletion command may permanently remove files: {command}\n\nDo you want to proceed?"
            except:
                question = f"⚠️  This deletion command may permanently remove files: {command}\n\nDo you want to proceed?"
            
            # Ask the user directly - they'll respond and Claude will call this tool again
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,  # Not successful until user responds
                result=question,
                execution_time=time.time() - start_time,
                requires_user_input=True  # Indicate this needs user input
            )
        
        # Execute command with optional stdin input
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(Path.cwd()),
                input=stdin_input  # Provide input to stdin if specified
            )
            
            # Format output with input information
            output_parts = []
            if stdin_input:
                output_parts.append(f"INPUT PROVIDED:\n{stdin_input}")
            if result.stdout:
                output_parts.append(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                output_parts.append(f"STDERR:\n{result.stderr}")
            
            output = "\n".join(output_parts) if output_parts else "(no output)"
            
            if result.returncode != 0:
                error_msg = f"Command failed with exit code {result.returncode}\n{output}"
                logger.warning("Bash tool command failed with non-zero exit code",
                             command=command,
                             exit_code=result.returncode,
                             stdout=result.stdout[:500] if result.stdout else None,
                             stderr=result.stderr[:500] if result.stderr else None,
                             tool_call_id=tool_call_id)
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=error_msg,
                    execution_time=time.time() - start_time
                )
            
            result_message = f"Command executed successfully: {command}"
            if stdin_input:
                result_message += f" (with {len(stdin_input.splitlines())} lines of input)"
            logger.info("Bash tool executed successfully",
                       command=command,
                       stdin_input_lines=len(stdin_input.splitlines()) if stdin_input else 0,
                       stdout_length=len(result.stdout) if result.stdout else 0,
                       stderr_length=len(result.stderr) if result.stderr else 0,
                       tool_call_id=tool_call_id)
            
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=True,
                result=output,
                execution_time=time.time() - start_time
            )
            
        except subprocess.TimeoutExpired:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Command timed out after {timeout} seconds",
                execution_time=time.time() - start_time
            )
            
    except Exception as e:
        error_msg = f"Failed to execute command '{command}': {e}"
        logger.error("Bash tool execution failed",
                    command=command,
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


@task(name="task_management", retries=2, retry_delay_seconds=1)
async def task_management_task(
    tool_call_id: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> ToolExecutionResult:
    """
    Atomic task management operation as Prefect task.
    
    Args:
        tool_call_id: Unique identifier for the tool call
        tool_name: Name of the tool (Task)
        tool_input: Dictionary containing action, task, task_id
    
    Returns:
        ToolExecutionResult with task management result or error
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
        task = tool_input.get('task')
        task_id = tool_input.get('task_id')
        
        if not action:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error="Missing required parameter: action",
                execution_time=time.time() - start_time
            )
        
        # Simple file-based task storage
        tasks_file = Path.cwd() / '.claude_tasks.json'
        
        # Load existing tasks
        if tasks_file.exists():
            tasks = json.loads(tasks_file.read_text())
        else:
            tasks = []
        
        if action == 'list':
            if not tasks:
                result = "No tasks found"
            else:
                result_lines = []
                for i, task_item in enumerate(tasks, 1):
                    status = "✓" if task_item.get('completed', False) else "○"
                    result_lines.append(f"{i}. {status} {task_item['description']}")
                result = "\n".join(result_lines)
            
        elif action == 'add':
            if not task:
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error="Missing required parameter for add action: task",
                    execution_time=time.time() - start_time
                )
            
            tasks.append({
                'description': task,
                'completed': False,
                'created': time.time()
            })
            
            # Save tasks
            tasks_file.write_text(json.dumps(tasks, indent=2))
            result = f"Task added: {task}"
            
        elif action in ['complete', 'remove']:
            if task_id is None:
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=f"Missing required parameter for {action} action: task_id",
                    execution_time=time.time() - start_time
                )
            
            try:
                task_index = int(task_id) - 1
                if task_index < 0 or task_index >= len(tasks):
                    return ToolExecutionResult(
                        tool_call_id=tool_call_id,
                        tool_name=tool_name,
                        success=False,
                        result=None,
                        error=f"Invalid task ID: {task_id}",
                        execution_time=time.time() - start_time
                    )
                
                if action == 'complete':
                    tasks[task_index]['completed'] = True
                    result = f"Task {task_id} marked as completed"
                else:  # remove
                    removed_task = tasks.pop(task_index)
                    result = f"Task {task_id} removed: {removed_task['description']}"
                
                # Save tasks
                tasks_file.write_text(json.dumps(tasks, indent=2))
                
            except ValueError:
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=f"Invalid task ID format: {task_id}",
                    execution_time=time.time() - start_time
                )
                
        else:
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Unknown action: {action}. Use: list, add, complete, remove",
                execution_time=time.time() - start_time
            )
        
        logger.info("Task tool executed successfully",
                   action=action,
                   task_count=len(tasks),
                   tool_call_id=tool_call_id)
        
        return ToolExecutionResult(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            success=True,
            result=result,
            execution_time=time.time() - start_time
        )
        
    except Exception as e:
        error_msg = f"Failed to execute task action '{action}': {e}"
        logger.error("Task tool execution failed",
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