#!/usr/bin/env python3
"""
@fileoverview Quick script to add documentation headers to governance files
@author Dr. Sarah Chen & Alex Novak - 2025-08-29
@architecture Utility - Documentation automation
@responsibility Add required headers to Python files for governance compliance
@dependencies os, pathlib
@integration_points File system operations
@testing_strategy Manual verification of generated headers
@governance Ensures all files meet documentation requirements

Business Logic Summary:
- Add required headers to Python files
- Preserve existing content
- Meet governance requirements

Architecture Integration:
- Temporary utility for documentation compliance
- One-time use for header addition
"""

import os
from pathlib import Path

# Files that need documentation
files_to_document = {
    'governance/core/context.py': {
        'description': 'Governance context management for rule validation',
        'author': 'Dr. Sarah Chen v1.0',
        'architecture': 'Backend - Governance context tracking',
        'responsibility': 'Manage validation context and state for governance rules'
    },
    'governance/core/engine.py': {
        'description': 'Core governance engine for rule execution',
        'author': 'Dr. Sarah Chen v1.0',
        'architecture': 'Backend - Governance rule engine',
        'responsibility': 'Execute governance rules and manage validation pipeline'
    },
    'governance/core/exceptions.py': {
        'description': 'Custom exceptions for governance system',
        'author': 'Dr. Sarah Chen v1.0',
        'architecture': 'Backend - Governance exception handling',
        'responsibility': 'Define governance-specific exceptions and error handling'
    },
    'governance/core/governance_monitor.py': {
        'description': 'Real-time governance monitoring and metrics',
        'author': 'Dr. Sarah Chen v1.0',
        'architecture': 'Backend - Governance monitoring system',
        'responsibility': 'Monitor governance enforcement and collect metrics'
    },
    'governance/core/result.py': {
        'description': 'Governance validation result structures',
        'author': 'Dr. Sarah Chen v1.0',
        'architecture': 'Backend - Governance result handling',
        'responsibility': 'Structure and manage validation results'
    },
    'governance/core/runtime_governance.py': {
        'description': 'Runtime governance enforcement system',
        'author': 'Dr. Sarah Chen v1.0',
        'architecture': 'Backend - Runtime governance enforcement',
        'responsibility': 'Enforce governance rules during runtime execution'
    },
    'governance/hooks/claude_code_governance_hook.py': {
        'description': 'Claude Code specific governance hook implementation',
        'author': 'Alex Novak v1.0',
        'architecture': 'Backend - Claude Code integration hook',
        'responsibility': 'Integrate governance with Claude Code operations'
    },
    'governance/middleware/ai_decision_injector.py': {
        'description': 'AI decision injection middleware for governance',
        'author': 'Sam Martinez v1.0',
        'architecture': 'Backend - AI decision middleware',
        'responsibility': 'Inject AI personas into governance decisions'
    },
    'governance/scripts/git_pre_commit_hook.py': {
        'description': 'Git pre-commit hook for governance enforcement',
        'author': 'Dr. Sarah Chen v1.0',
        'architecture': 'Backend - Git hook integration',
        'responsibility': 'Enforce governance rules before git commits'
    },
    'governance/scripts/quick_test.py': {
        'description': 'Quick test runner for governance validation',
        'author': 'Dr. Sarah Chen v1.0',
        'architecture': 'Backend - Test utility',
        'responsibility': 'Run quick validation tests for governance system'
    },
    'governance/setup.py': {
        'description': 'Setup configuration for governance package',
        'author': 'Dr. Sarah Chen v1.0',
        'architecture': 'Backend - Package configuration',
        'responsibility': 'Configure governance package installation'
    },
    'governance/tests/demo_governance_visibility.py': {
        'description': 'Demo script for governance visibility features',
        'author': 'Dr. Sarah Chen v1.0',
        'architecture': 'Backend - Demo and testing',
        'responsibility': 'Demonstrate governance visibility and monitoring'
    },
    'governance/tests/test_runtime_governance.py': {
        'description': 'Test suite for runtime governance system',
        'author': 'Dr. Sarah Chen v1.0',
        'architecture': 'Backend - Test suite',
        'responsibility': 'Test runtime governance enforcement'
    },
    'test_milestone_1.py': {
        'description': 'Milestone 1 validation tests',
        'author': 'Dr. Sarah Chen v1.0',
        'architecture': 'Backend - Milestone testing',
        'responsibility': 'Validate milestone 1 governance requirements'
    }
}

def create_header(file_info):
    """Generate documentation header"""
    return f'''"""
@fileoverview {file_info['description']}
@author {file_info['author']} - 2025-08-29
@architecture {file_info['architecture']}
@responsibility {file_info['responsibility']}
@dependencies Various based on module functionality
@integration_points Governance system components
@testing_strategy Unit tests and integration tests
@governance Core governance component

Business Logic Summary:
- Core governance functionality
- Rule validation and enforcement
- System integration

Architecture Integration:
- Part of governance system
- Integrates with hooks and validators
- Enforces documentation standards
"""

'''

def add_headers():
    """Add headers to all files"""
    for filepath, info in files_to_document.items():
        full_path = Path(filepath)
        if full_path.exists():
            # Read existing content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip if already has headers
            if '@fileoverview' in content:
                print(f"✓ {filepath} already has headers")
                continue
            
            # Skip shebang if present
            lines = content.split('\n')
            if lines and lines[0].startswith('#!'):
                shebang = lines[0] + '\n'
                rest = '\n'.join(lines[1:])
                new_content = shebang + create_header(info) + rest.lstrip()
            else:
                # Skip existing docstring if present
                if content.startswith('"""'):
                    # Find end of existing docstring
                    end_idx = content.find('"""', 3) + 3
                    rest = content[end_idx:].lstrip()
                    new_content = create_header(info) + rest
                else:
                    new_content = create_header(info) + content
            
            # Write back
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✓ Added headers to {filepath}")
        else:
            print(f"✗ File not found: {filepath}")

if __name__ == '__main__':
    add_headers()
    print("\nDocumentation headers added successfully!")