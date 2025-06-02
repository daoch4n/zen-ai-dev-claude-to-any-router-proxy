#!/usr/bin/env python3
"""
Start the OpenRouter Anthropic Server
Simple startup script for the new modular server architecture.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

if __name__ == "__main__":
    from src.main import main
    main()