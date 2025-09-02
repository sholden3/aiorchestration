"""
@fileoverview Rules definitions - Core governance rules and policies
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Rule definitions
@responsibility Define and manage core governance rules
@dependencies None - pure configuration
@integration_points Rule engine, validators, smart rules
@testing_strategy Rule loading tests, rule evaluation tests
@governance Rules are the heart of the governance system

Business Logic Summary:
- Define validation rules
- Configure enforcement levels
- Set pattern matchers
- Manage rule priorities
- Track rule versions

Architecture Integration:
- Loaded by rule engine
- Applied by validators
- Enhanced by smart rules
- Logged in decisions
- Versioned for audit

Sarah's Framework Check:
- What breaks first: Circular rule dependencies
- How we know: Rule resolution timeout
- Plan B: Dependency cycle detection

Core Rules:
- dangerous_operations: Patterns that require blocking
- requires_review: Operations needing human review
- auto_approve: Safe operations for fast-track
- test_exemptions: Patterns allowed in tests
- security_critical: High-risk security patterns

Rule Format:
Rules use YAML/JSON with:
- Pattern matching
- Risk scoring
- Action directives
- Exemption conditions
"""

# Rules loaded dynamically from configuration files

__all__ = []

__version__ = '1.0.0'