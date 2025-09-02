"""
@fileoverview Scripts package - Governance scripts and utilities
@author Dr. Sarah Chen v1.0 & Alex Novak v1.0 - 2025-08-29
@architecture Backend - Script utilities
@responsibility Provide scripts for governance operations and git integration
@dependencies Git, subprocess, governance core
@integration_points Git hooks, CI/CD, command line
@testing_strategy Script execution tests, integration tests
@governance Scripts enforce governance at development boundaries

Business Logic Summary:
- Git hook implementations
- Installation utilities
- Testing scripts
- Validation utilities
- Migration tools

Architecture Integration:
- Git pre-commit hooks
- CI/CD integration scripts
- Development tool plugins
- Command-line utilities
- Automation scripts

Sarah's Framework Check:
- What breaks first: Script execution permissions
- How we know: Permission denied errors
- Plan B: Fallback to Python subprocess

Available Scripts:
- integrated_pre_commit_hook.py: Main git pre-commit hook
- enhanced_pre_commit_hook.py: Enhanced validation hook
- git_pre_commit_hook.py: Basic git hook
- install_git_hooks.py: Hook installation utility
- quick_test.py: Quick governance testing

Script Usage:
1. Install hooks: python governance/scripts/install_git_hooks.py
2. Test governance: python governance/scripts/quick_test.py
3. Manual validation: python governance/scripts/integrated_pre_commit_hook.py

Configuration:
- GOVERNANCE_CONFIG: Config directory path
- GOVERNANCE_LEVEL: Enforcement level
- GOVERNANCE_BYPASS: Emergency bypass
"""

# Script modules
# Scripts are typically run directly, not imported

__all__ = []

__version__ = '1.0.0'