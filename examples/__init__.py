"""
Examples package for 3DSun.

This package contains example scripts demonstrating the usage of the 3DSun library.
"""

# Add the parent directory to the path so files in examples can import from src
import sys
import os

# Get the parent directory of the examples folder
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the Python path if it's not already there
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
