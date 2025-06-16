"""
Utility to apply enhanced exception handling to existing codebase.

This script analyzes Python files and applies enhanced exception handling
decorators and context managers to existing try/except blocks and functions.
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
import argparse

from src.core.logging_config import get_logger

logger = get_logger(__name__)

class EnhancedErrorHandlingApplier:
    """Applies enhanced exception handling to Python source files."""
    
    def __init__(self, src_dir: str = "src"):
        """Initialize the applier with source directory."""
        self.src_dir = Path(src_dir)
        self.processed_files: List[str] = []
        self.errors: List[str] = []
        
        # Patterns to identify exception handling
        self.try_except_pattern = re.compile(r'(\s*)try:\s*\n(.*?)\n\s*except\s+(\w+)*\s*(?:as\s+(\w+))?\s*:\s*\n', re.DOTALL)
        self.function_pattern = re.compile(r'(\s*)(?:async\s+)?def\s+(\w+)\s*\([^)]*\)(?:\s*->\s*[^:]+)?:\s*\n', re.DOTALL)
        
    def analyze_file(self, file_path: Path) -> Dict[str, any]:
        """Analyze a Python file for exception handling opportunities."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST to find try/except blocks and functions
            tree = ast.parse(content)
            
            analysis = {
                "file_path": str(file_path),
                "try_except_blocks": [],
                "functions_without_handling": [],
                "functions_with_handling": [],
                "needs_enhancement": False
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    analysis["try_except_blocks"].append({
                        "line": node.lineno,
                        "col": node.col_offset,
                        "has_enhancement": self._has_enhanced_handling(content, node.lineno)
                    })
                
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    has_try_except = self._function_has_try_except(node)
                    has_decorator = self._has_enhanced_decorator(content, node.lineno)
                    
                    if has_try_except and not has_decorator:
                        analysis["functions_with_handling"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "is_async": isinstance(node, ast.AsyncFunctionDef),
                            "has_decorator": has_decorator
                        })
                    elif not has_try_except and not has_decorator:
                        analysis["functions_without_handling"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "is_async": isinstance(node, ast.AsyncFunctionDef),
                            "has_decorator": has_decorator
                        })
            
            # Determine if file needs enhancement
            analysis["needs_enhancement"] = (
                len([b for b in analysis["try_except_blocks"] if not b["has_enhancement"]]) > 0 or
                len(analysis["functions_with_handling"]) > 0
            )
            
            return analysis
            
        except Exception as e:
            self.errors.append(f"Failed to analyze {file_path}: {str(e)}")
            return {"file_path": str(file_path), "error": str(e)}
    
    def _has_enhanced_handling(self, content: str, line_number: int) -> bool:
        """Check if a try block has enhanced error handling."""
        lines = content.split('\n')
        start_line = max(0, line_number - 5)
        end_line = min(len(lines), line_number + 20)
        
        block_content = '\n'.join(lines[start_line:end_line])
        
        # Look for enhanced error handling patterns
        enhanced_patterns = [
            'enhanced_error_context',
            'log_error_with_hash',
            'enhanced_exception_handler',
            'get_enhanced_error_handler',
            'block_hash'
        ]
        
        return any(pattern in block_content for pattern in enhanced_patterns)
    
    def _function_has_try_except(self, func_node: ast.FunctionDef) -> bool:
        """Check if a function contains try/except blocks."""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Try):
                return True
        return False
    
    def _has_enhanced_decorator(self, content: str, line_number: int) -> bool:
        """Check if a function has enhanced exception handling decorator."""
        lines = content.split('\n')
        start_line = max(0, line_number - 10)
        end_line = line_number
        
        decorator_content = '\n'.join(lines[start_line:end_line])
        
        return '@enhanced_exception_handler' in decorator_content
    
    def generate_enhanced_code(self, analysis: Dict[str, any]) -> str:
        """Generate enhanced code with improved exception handling."""
        file_path = Path(analysis["file_path"])
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            enhanced_lines = lines.copy()
            
            # Add import for enhanced error handling at the top
            import_added = False
            for i, line in enumerate(enhanced_lines):
                if line.startswith('from ') or line.startswith('import '):
                    if not import_added and 'enhanced_error_handler' not in content:
                        enhanced_lines.insert(i, 'from src.utils.enhanced_error_handler import enhanced_exception_handler, enhanced_error_context, log_error_with_hash')
                        import_added = True
                        break
            
            # Offset for line number adjustments
            line_offset = 1 if import_added else 0
            
            # Enhance try/except blocks
            for block in analysis.get("try_except_blocks", []):
                if not block.get("has_enhancement", False):
                    self._enhance_try_except_block(enhanced_lines, block["line"] + line_offset - 1)
            
            # Add decorators to functions with exception handling
            for func in analysis.get("functions_with_handling", []):
                if not func.get("has_decorator", False):
                    self._add_function_decorator(enhanced_lines, func["line"] + line_offset - 1, func["name"])
            
            return '\n'.join(enhanced_lines)
            
        except Exception as e:
            self.errors.append(f"Failed to generate enhanced code for {file_path}: {str(e)}")
            return ""
    
    def _enhance_try_except_block(self, lines: List[str], try_line_index: int):
        """Enhance a try/except block with context manager."""
        try:
            # Find the except block
            except_line_index = None
            for i in range(try_line_index + 1, min(len(lines), try_line_index + 50)):
                if lines[i].strip().startswith('except'):
                    except_line_index = i
                    break
            
            if except_line_index is None:
                return
            
            # Get indentation
            try_line = lines[try_line_index]
            indent = len(try_line) - len(try_line.lstrip())
            
            # Replace try with enhanced error context
            context_name = f"error_handling_block_{try_line_index}"
            lines[try_line_index] = ' ' * indent + f'with enhanced_error_context("{context_name}") as block_hash:'
            
            # Enhance the except block
            except_line = lines[except_line_index]
            except_indent = len(except_line) - len(except_line.lstrip())
            
            # Find exception variable name
            exception_var = 'e'
            if ' as ' in except_line:
                parts = except_line.split(' as ')
                if len(parts) > 1:
                    exception_var = parts[1].strip().rstrip(':')
            
            # Add enhanced error logging
            enhanced_except_content = [
                except_line,
                ' ' * (except_indent + 4) + f'# Enhanced error logging',
                ' ' * (except_indent + 4) + f'log_error_with_hash(',
                ' ' * (except_indent + 8) + f'error={exception_var},',
                ' ' * (except_indent + 8) + f'block_hash=block_hash,',
                ' ' * (except_indent + 8) + f'context={{"function_line": {try_line_index + 1}}}',
                ' ' * (except_indent + 4) + ')'
            ]
            
            # Replace the except line
            lines[except_line_index:except_line_index + 1] = enhanced_except_content
            
        except Exception as e:
            logger.warning(f"Failed to enhance try/except block at line {try_line_index}: {str(e)}")
    
    def _add_function_decorator(self, lines: List[str], func_line_index: int, func_name: str):
        """Add enhanced exception handler decorator to a function."""
        try:
            func_line = lines[func_line_index]
            indent = len(func_line) - len(func_line.lstrip())
            
            # Add decorator before function
            decorator = ' ' * indent + f'@enhanced_exception_handler(context={{"function": "{func_name}"}})'
            lines.insert(func_line_index, decorator)
            
        except Exception as e:
            logger.warning(f"Failed to add decorator to function {func_name} at line {func_line_index}: {str(e)}")
    
    def apply_to_file(self, file_path: Path, dry_run: bool = True) -> bool:
        """Apply enhanced exception handling to a single file."""
        try:
            analysis = self.analyze_file(file_path)
            
            if analysis.get("error"):
                logger.error(f"Analysis failed for {file_path}: {analysis['error']}")
                return False
            
            if not analysis.get("needs_enhancement", False):
                logger.info(f"File {file_path} doesn't need enhancement")
                return True
            
            enhanced_code = self.generate_enhanced_code(analysis)
            
            if not enhanced_code:
                logger.error(f"Failed to generate enhanced code for {file_path}")
                return False
            
            if dry_run:
                logger.info(f"DRY RUN: Would enhance {file_path}")
                logger.info(f"  - Try/except blocks to enhance: {len([b for b in analysis.get('try_except_blocks', []) if not b.get('has_enhancement', False)])}")
                logger.info(f"  - Functions to add decorators: {len(analysis.get('functions_with_handling', []))}")
            else:
                # Create backup
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    with open(file_path, 'r', encoding='utf-8') as orig:
                        f.write(orig.read())
                
                # Write enhanced code
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_code)
                
                logger.info(f"Enhanced {file_path} (backup: {backup_path})")
                self.processed_files.append(str(file_path))
            
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to apply enhancement to {file_path}: {str(e)}")
            logger.error(f"Failed to apply enhancement to {file_path}: {str(e)}")
            return False
    
    def apply_to_directory(self, target_dir: Path = None, dry_run: bool = True, exclude_patterns: List[str] = None) -> Dict[str, any]:
        """Apply enhanced exception handling to all Python files in a directory."""
        if target_dir is None:
            target_dir = self.src_dir
        
        if exclude_patterns is None:
            exclude_patterns = ['__pycache__', '.git', 'test_', '.pyc', '.backup']
        
        results = {
            "processed_files": [],
            "skipped_files": [],
            "errors": [],
            "total_files": 0,
            "enhanced_files": 0
        }
        
        # Find all Python files
        python_files = []
        for root, dirs, files in os.walk(target_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                if file.endswith('.py') and not any(pattern in file for pattern in exclude_patterns):
                    python_files.append(Path(root) / file)
        
        results["total_files"] = len(python_files)
        
        logger.info(f"Found {len(python_files)} Python files to process")
        
        for file_path in python_files:
            try:
                success = self.apply_to_file(file_path, dry_run)
                if success:
                    results["processed_files"].append(str(file_path))
                    results["enhanced_files"] += 1
                else:
                    results["skipped_files"].append(str(file_path))
                    
            except Exception as e:
                error_msg = f"Failed to process {file_path}: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # Add any accumulated errors
        results["errors"].extend(self.errors)
        
        return results


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Apply enhanced exception handling to Python codebase")
    parser.add_argument("--src-dir", default="src", help="Source directory to process")
    parser.add_argument("--target", help="Specific file or directory to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--exclude", nargs="*", default=["__pycache__", ".git", "test_", ".pyc", ".backup"], 
                       help="Patterns to exclude from processing")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    applier = EnhancedErrorHandlingApplier(args.src_dir)
    
    if args.target:
        target_path = Path(args.target)
        if target_path.is_file():
            success = applier.apply_to_file(target_path, args.dry_run)
            print(f"{'DRY RUN: ' if args.dry_run else ''}{'Success' if success else 'Failed'}: {target_path}")
        elif target_path.is_dir():
            results = applier.apply_to_directory(target_path, args.dry_run, args.exclude)
            print(f"{'DRY RUN: ' if args.dry_run else ''}Processed {results['enhanced_files']}/{results['total_files']} files")
            if results['errors']:
                print(f"Errors: {len(results['errors'])}")
                for error in results['errors'][:5]:  # Show first 5 errors
                    print(f"  - {error}")
        else:
            print(f"Target path does not exist: {target_path}")
    else:
        results = applier.apply_to_directory(None, args.dry_run, args.exclude)
        print(f"{'DRY RUN: ' if args.dry_run else ''}Processed {results['enhanced_files']}/{results['total_files']} files")
        if results['errors']:
            print(f"Errors: {len(results['errors'])}")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")


if __name__ == "__main__":
    main() 