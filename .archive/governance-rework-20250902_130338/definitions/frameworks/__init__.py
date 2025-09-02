"""
@fileoverview Frameworks definitions - Governance frameworks from different architects
@author Dr. Sarah Chen v1.0 & Alex Novak v1.0 - 2025-08-29
@architecture Backend - Framework definitions
@responsibility Define and manage architect-specific governance frameworks
@dependencies None - pure configuration
@integration_points Loaded by governance engine, used by validators
@testing_strategy Framework loading tests, rule application tests
@governance Frameworks govern the governance system itself

Business Logic Summary:
- Sarah's Three Questions Framework
- Alex's 3 AM Test Framework
- Combined defensive programming patterns
- Failure mode analysis requirements
- Cross-validation requirements

Architecture Integration:
- Loaded at engine initialization
- Applied during validation
- Used for decision scoring
- Referenced in audit logs
- Enforced in code reviews

Sarah's Framework Check:
- What breaks first: Missing framework files
- How we know: Engine initialization failures
- Plan B: Embedded default frameworks

Available Frameworks:
1. sarah_chen_framework.yaml - Backend resilience and failure analysis
2. alex_novak_framework.yaml - Frontend integration and debugging
3. combined_framework.yaml - Unified governance approach

Framework Application:
Frameworks are automatically applied based on:
- File type and location
- Operation type
- Risk level
- Persona recommendations
"""

# Frameworks are loaded dynamically from YAML files
# No Python imports needed

__all__ = []

__version__ = '1.0.0'