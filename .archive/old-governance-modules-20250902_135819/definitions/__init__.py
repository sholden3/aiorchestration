"""
@fileoverview Definitions package - Configuration and rule definitions for governance
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Configuration and definitions layer
@responsibility Manage governance rules, personas, validators, and frameworks
@dependencies YAML/JSON parsers, schema validators
@integration_points Core engine, validators, persona system
@testing_strategy Schema validation tests, rule loading tests, configuration tests
@governance Definitions are validated against schemas before use

Business Logic Summary:
- Define governance rules and policies
- Configure persona behaviors
- Specify validation frameworks
- Manage project-specific rules
- Store validator configurations

Architecture Integration:
- Loaded by governance engine at startup
- Used by validators for rule evaluation
- Referenced by personas for decision-making
- Integrated with smart rules
- Powers configuration-driven governance

Sarah's Framework Check:
- What breaks first: Malformed YAML/JSON causing parse errors
- How we know: Schema validation failures at load time
- Plan B: Default configurations with error logging

Package Structure:
- frameworks/: Governance frameworks (Sarah's, Alex's, etc.)
- personas/: Persona definitions and behaviors
- projects/: Project-specific governance rules
- rules/: Core governance rules and policies
- validators/: Validator configurations

Configuration Format:
All definitions use YAML or JSON with strict schemas.
Changes require review and testing before deployment.

Extensibility:
New definitions can be added by:
1. Creating appropriate YAML/JSON files
2. Following existing schemas
3. Testing with governance engine
4. Documenting purpose and usage
"""

# Subpackages for different definition types
# Definitions are loaded dynamically by the engine

__all__ = [
    'frameworks',
    'personas', 
    'projects',
    'rules',
    'validators'
]

__version__ = '1.0.0'
__config_format__ = 'YAML/JSON'