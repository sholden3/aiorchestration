"""
Governance System Library
Consolidated governance system for the AI Orchestration Platform
"""

__version__ = "2.1.0"

# Export main modules
from . import core
from . import validators
from . import hooks
from . import middleware
from . import rules

__all__ = [
    "core",
    "validators", 
    "hooks",
    "middleware",
    "rules"
]