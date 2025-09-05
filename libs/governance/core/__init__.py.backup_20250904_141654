"""
@fileoverview Core governance system package - Central components for AI governance enforcement
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Core governance infrastructure
@responsibility Export core governance components and provide unified API for governance operations
@dependencies Local modules only - no external dependencies at package level
@integration_points Engine, context, result, exceptions, monitoring, runtime governance
@testing_strategy Import tests, API surface tests, integration tests for component interaction
@governance This package IS the governance system - self-governing through its own rules

Business Logic Summary:
- Provides governance engine for rule evaluation
- Manages governance context and results
- Handles runtime governance and monitoring
- Tracks correlations and sessions
- Enforces governance at all decision points

Architecture Integration:
- Central package imported by all governance consumers
- Provides base classes and interfaces
- Integrates with hooks, middleware, and validators
- Used by git hooks for commit validation
- Powers runtime AI decision governance

Sarah's Framework Check:
- What breaks first: Import errors if modules are renamed without updating __init__
- How we know: Import tests fail immediately on CI/CD
- Plan B: Explicit imports with try/except for graceful degradation

Package Purpose:
This is the heart of the governance system, providing core functionality for:
1. Rule evaluation through the GovernanceEngine
2. Context management for governance decisions
3. Result structures for validation outcomes
4. Runtime governance for AI operations
5. Monitoring and visibility of all governance activities

Public API:
The following are intentionally exposed for external use:
- GovernanceEngine: Main engine for rule evaluation
- GovernanceContext: Context structure for decisions
- GovernanceResult: Result structure for outcomes
- GovernanceException: Base exception class
- RuntimeGovernanceSystem: Runtime AI governance
- GovernanceMonitor: Real-time monitoring

Internal Components (use with caution):
- correlation_tracker: Internal correlation tracking
- session_manager: Session management internals
- todo_tracker: Development task tracking

Usage Examples:
    # Basic governance evaluation
    from governance.core import GovernanceEngine, GovernanceContext
    
    engine = GovernanceEngine()
    context = GovernanceContext(
        operation_type="code_review",
        actor="developer",
        payload={"files": ["main.py"]}
    )
    result = engine.evaluate(context)
    
    # Runtime AI governance
    from governance.core import RuntimeGovernanceSystem
    
    runtime = RuntimeGovernanceSystem()
    await runtime.validate_agent_spawn(
        agent_type="assistant",
        agent_name="Helper"
    )

Stability Notes:
- API is stable as of v1.0
- GovernanceContext and GovernanceResult are frozen interfaces
- New features will be added via extension, not modification
- Breaking changes will be announced 2 versions in advance
"""

# Core engine and data structures
from .engine import GovernanceEngine
from .context import GovernanceContext
from .result import GovernanceResult, ValidationResult
from .exceptions import GovernanceError

# Runtime governance system
from .runtime_governance import (
    RuntimeGovernanceSystem,
    HookType,
    GovernanceLevel,
    AgentContext
)

# Monitoring and visibility
from .governance_monitor import (
    GovernanceMonitor,
    GovernanceEvent,
    GovernanceEventType,
    get_monitor,
    show_governance_banner
)

# Session and correlation tracking
from .correlation_tracker import CorrelationTracker
from .session_manager import SessionManager
from .todo_tracker import TodoTracker

# Define public API explicitly
__all__ = [
    # Core components
    'GovernanceEngine',
    'GovernanceContext',
    'GovernanceResult',
    'ValidationResult',
    'GovernanceError',
    
    # Runtime governance
    'RuntimeGovernanceSystem',
    'HookType',
    'GovernanceLevel',
    'AgentContext',
    
    # Monitoring
    'GovernanceMonitor',
    'GovernanceEvent',
    'GovernanceEventType',
    'get_monitor',
    'show_governance_banner',
    
    # Tracking (advanced use)
    'CorrelationTracker',
    'SessionManager',
    'TodoTracker'
]

# Version information
__version__ = '1.0.0'
__author__ = 'Dr. Sarah Chen'