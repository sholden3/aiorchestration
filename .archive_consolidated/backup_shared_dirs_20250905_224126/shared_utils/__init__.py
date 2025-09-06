"""Shared utils package - Python interface"""
# Import from the python subpackage
try:
    from .python import *
except ImportError:
    # Fallback for direct imports
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from python import *