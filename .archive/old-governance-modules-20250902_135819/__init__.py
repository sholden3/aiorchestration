"""
@fileoverview Root governance package - Unified AI governance system for development operations
@author Dr. Sarah Chen v1.0 & Alex Novak v1.0 - 2025-08-29
@architecture Backend - Top-level governance package
@responsibility Provide unified entry point for all governance functionality
@dependencies All governance subpackages and their dependencies
@integration_points Git hooks, CI/CD, runtime AI systems, development tools
@testing_strategy Package-level integration tests, API stability tests
@governance Self-governing through its own rules and validation

Business Logic Summary:
- Single entry point for governance operations
- Coordinates between core, hooks, middleware, validators
- Enforces governance at git, runtime, and AI decision levels
- Provides monitoring and audit capabilities
- Manages rules and persona consultations

Architecture Integration:
- Imported by git pre-commit hooks
- Used by CI/CD pipelines
- Integrated with AI runtime systems
- Powers development tool governance
- Provides CLI and API interfaces

Sarah's Framework Check:
- What breaks first: Circular imports if subpackages import from root
- How we know: Import errors during module loading
- Plan B: Lazy imports for circular dependency resolution

Package Purpose:
The governance package provides comprehensive AI and development governance:
1. Git commit validation and enforcement
2. AI decision interception and validation
3. Runtime agent lifecycle management
4. Multi-persona consultation system
5. Real-time monitoring and audit trails
6. Smart rules and pattern detection

Public API:
Primary interfaces for external consumers:
- GovernanceEngine: Rule evaluation engine
- RuntimeGovernanceSystem: Runtime AI governance
- AIDecisionInjector: AI output validation
- GovernanceMonitor: Monitoring and visibility
- SmartRules: Intelligent pattern detection

Subpackages:
- core: Core engine and data structures
- hooks: Git and system hook integrations  
- middleware: AI decision interception layer
- validators: Validation implementations
- rules: Rule definitions and smart rules
- scripts: Git hooks and utilities
- api: REST API endpoints (future)
- cli: Command-line interface (future)

Usage Examples:
    # Basic governance check
    from governance import GovernanceEngine, GovernanceContext
    
    engine = GovernanceEngine()
    context = GovernanceContext(
        operation_type="code_change",
        actor="developer"
    )
    result = engine.evaluate(context)
    
    # AI decision validation
    from governance import AIDecisionInjector, DecisionType
    
    injector = AIDecisionInjector()
    validation = await injector.intercept_decision(
        agent_id="agent_001",
        decision_type=DecisionType.CODE_GENERATION,
        proposed_output=code
    )
    
    # Git hook usage
    from governance.scripts import IntegratedGovernanceHook
    
    hook = IntegratedGovernanceHook()
    hook.run()

Stability and Versioning:
- Current version: 1.0.0
- Semantic versioning followed
- Backward compatibility maintained within major versions
- Deprecation warnings provided 2 versions in advance
- Migration guides for breaking changes

Environment Variables:
- GOVERNANCE_LEVEL: Set governance strictness (STRICT|STANDARD|RELAXED|BYPASS)
- GOVERNANCE_BYPASS: Emergency bypass (use with extreme caution)
- GOVERNANCE_CONFIG: Path to configuration directory
- GOVERNANCE_LOG_LEVEL: Logging verbosity
"""

# Core components - these are the foundation
from governance.core import (
    GovernanceEngine,
    GovernanceContext,
    GovernanceResult,
    ValidationResult,
    GovernanceError,
    RuntimeGovernanceSystem,
    GovernanceMonitor,
    get_monitor,
    show_governance_banner
)

# Middleware for AI decision interception
from governance.middleware.ai_decision_injector import (
    AIDecisionInjector,
    DecisionType,
    DecisionValidation,
    RiskLevel
)

# Smart rules for intelligent validation
from governance.rules.smart_rules import (
    SmartRules,
    RuleEnhancer
)

# Validators for specific checks
from governance.validators.basic_hallucination_detector import (
    BasicHallucinationDetector
)

# Define the public API
__all__ = [
    # Core engine
    'GovernanceEngine',
    'GovernanceContext', 
    'GovernanceResult',
    'ValidationResult',
    'GovernanceError',
    
    # Runtime governance
    'RuntimeGovernanceSystem',
    
    # Monitoring
    'GovernanceMonitor',
    'get_monitor',
    'show_governance_banner',
    
    # AI decision validation
    'AIDecisionInjector',
    'DecisionType',
    'DecisionValidation',
    'RiskLevel',
    
    # Smart rules
    'SmartRules',
    'RuleEnhancer',
    
    # Validators
    'BasicHallucinationDetector'
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'Dr. Sarah Chen & Alex Novak'
__license__ = 'MIT'
__description__ = 'Comprehensive AI and development governance system'