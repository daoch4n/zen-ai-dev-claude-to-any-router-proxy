"""File operations tasks for debug utilities."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from ...core.logging_config import get_logger

logger = get_logger("debug.file_tasks")


def generate_request_id(request_count: int) -> str:
    """Generate a unique request ID."""
    timestamp = datetime.now()
    return f"{timestamp.strftime('%Y%m%d_%H%M%S_%f')}_{request_count}"


def create_debug_directory(debug_dir: Path) -> None:
    """Create debug directory if it doesn't exist."""
    debug_dir.mkdir(parents=True, exist_ok=True)


def write_debug_file(
    filepath: Path, 
    debug_data: Dict[str, Any], 
    json_serializer=None
) -> bool:
    """Write debug data to a JSON file."""
    try:
        if json_serializer is None:
            # Default serializer
            def default_serializer(obj):
                try:
                    return str(obj)
                except:
                    return f"Unserializable object: {type(obj).__name__}"
            json_serializer = default_serializer
        
        with open(filepath, 'w') as f:
            json.dump(debug_data, f, indent=2, default=json_serializer)
        
        logger.debug("Debug file written successfully", filepath=str(filepath))
        return True
        
    except Exception as e:
        logger.error("Failed to write debug file", 
                    filepath=str(filepath), 
                    error=str(e))
        return False