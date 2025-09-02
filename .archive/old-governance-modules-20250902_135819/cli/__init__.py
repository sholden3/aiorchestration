"""
@fileoverview CLI package for governance system - Command-line interface for governance operations
@author Alex Novak v1.0 - 2025-08-29
@architecture Backend - Command-line interface layer
@responsibility Provide CLI commands for governance validation and management
@dependencies Click, core governance modules
@integration_points Terminal, shell scripts, CI/CD pipelines
@testing_strategy CLI command tests, argument parsing tests, output validation
@governance CLI operations are governed and audit-logged

Business Logic Summary:
- Provide CLI commands for governance checks
- Enable script integration
- Support batch validation operations
- Generate governance reports
- Manage governance configuration

Architecture Integration:
- Built with Click framework
- Uses core governance engine
- Integrates with git hooks
- Supports pipe operations
- Provides structured output formats

Sarah's Framework Check:
- What breaks first: Argument parsing with special characters
- How we know: Click validation errors
- Plan B: Escape and sanitize all inputs

Package Purpose:
Future CLI implementation for:
1. Manual governance validation
2. Batch file checking
3. Configuration management
4. Report generation
5. Git hook testing

Planned Commands:
- governance validate <files>
- governance report
- governance config
- governance test-hook
- governance metrics

Note: This package is planned for future implementation.
Currently using direct Python scripts for CLI operations.
"""

# Future CLI commands will be defined here
# from .main import cli
# from .commands import validate, report, config

__all__ = []  # Will be populated when implemented

__version__ = '0.0.1'
__status__ = 'planned'