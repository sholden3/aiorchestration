"""
@fileoverview Project definitions - Project-specific governance rules and configurations
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Project configuration
@responsibility Manage project-specific governance rules and overrides
@dependencies None - pure configuration
@integration_points Core engine, rule evaluation
@testing_strategy Project rule loading tests, override validation tests
@governance Project rules must align with core governance principles

Business Logic Summary:
- Define project-specific rules
- Configure project overrides
- Set project thresholds
- Manage exemptions
- Track project metadata

Architecture Integration:
- Loaded per project context
- Merged with core rules
- Applied during validation
- Tracked in project logs
- Audited for compliance

Sarah's Framework Check:
- What breaks first: Conflicting project rules
- How we know: Rule merge conflicts at load time
- Plan B: Core rules take precedence

Project Configuration:
Each project can define:
- Custom validation rules
- Risk thresholds
- Required personas
- Exemption patterns
- Special requirements

Note: Project rules cannot bypass core security rules.
"""

# Project configurations loaded dynamically

__all__ = []

__version__ = '1.0.0'