"""
Validator Plugin Architecture

This package provides a comprehensive plugin system for validators with:
- Dynamic plugin loading and registration
- Lifecycle management
- Configuration management
- Inter-plugin communication
- Integration with Claude Code and Git hooks

@description: Package initialization for validator plugin architecture
@author: AI Assistant (GitHub Copilot generated, reviewed by team)
@version: 1.0.0
@dependencies: None (package initialization)
@exports: IValidatorPlugin, BaseValidatorPlugin, PluginMetadata, PluginHealth,
          ValidationResult, PluginState, ValidationMode, ValidationSeverity
@testing: tests/unit/governance/plugins/
@last_review: 2025-01-06
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