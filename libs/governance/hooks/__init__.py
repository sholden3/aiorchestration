"""
@fileoverview Hooks package - Integration hooks for external systems
@author Dr. Sarah Chen v1.0 & Alex Novak v1.0 - 2025-08-29
@architecture Backend - Hook integrations
@responsibility Provide hooks for git, CI/CD, and development tools
@dependencies Git, shell scripting, process management
@integration_points Git hooks, CI/CD pipelines, IDE integrations
@testing_strategy Hook execution tests, integration tests
@governance Hooks enforce governance at integration points

Business Logic Summary:
- Git pre-commit validation
- CI/CD pipeline checks
- IDE integration hooks
- CLI tool hooks
- Webhook handlers

Architecture Integration:
- Git hook scripts
- Shell/batch wrappers
- Python hook implementations
- Async webhook handlers
- Event triggers

Sarah's Framework Check:
- What breaks first: Hook timeout on large commits
- How we know: Git operations hang
- Plan B: Async validation with immediate response

Available Hooks:
- claude_code_governance_hook.py: Claude Code CLI integration
- governance_hook.sh: Unix/Linux shell hook
- governance_hook.bat: Windows batch hook
- (git hooks installed via scripts/)

Hook Installation:
Hooks are installed via:
1. scripts/install_git_hooks.py
2. Manual copying to .git/hooks/
3. CI/CD pipeline setup

Hook Configuration:
Configured via environment variables:
- GOVERNANCE_LEVEL
- GOVERNANCE_CONFIG
- GOVERNANCE_BYPASS
"""

# Hook implementations
from .claude_code_governance_hook import main as claude_hook

__all__ = [
    'claude_hook'
]

__version__ = '1.0.0'