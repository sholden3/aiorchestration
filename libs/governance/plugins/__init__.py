"""
Validator Plugin Architecture

This package provides a comprehensive plugin system for validators with:
- Dynamic plugin loading and registration
- Lifecycle management
- Configuration management
- Inter-plugin communication
- Integration with Claude Code and Git hooks
"""

from .base import (
    IValidatorPlugin,
    BaseValidatorPlugin,
    PluginMetadata,
    PluginHealth,
    ValidationResult,
    PluginState,
    ValidationMode,
    ValidationSeverity
)

__all__ = [
    'IValidatorPlugin',
    'BaseValidatorPlugin',
    'PluginMetadata', 
    'PluginHealth',
    'ValidationResult',
    'PluginState',
    'ValidationMode',
    'ValidationSeverity'
]