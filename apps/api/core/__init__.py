"""
Core Backend Module

Contains core configuration, authentication, and shared utilities.

Recovery Note: Created 2025-09-03 during dependency recovery (DEC-2025-010)
"""

from .config import get_config, get_backend_url, is_development

__all__ = ['get_config', 'get_backend_url', 'is_development']