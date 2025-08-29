"""
@fileoverview Custom exception hierarchy for governance system error handling
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Governance exception definitions
@responsibility Define structured exceptions for governance error handling
@dependencies None (base Python exceptions only)
@integration_points Used throughout governance system for error signaling
@testing_strategy Unit tests for exception hierarchy and error messages
@governance Enables proper error handling and debugging in governance system

Business Logic Summary:
- Define governance-specific exception hierarchy
- Enable structured error handling
- Support detailed error messages
- Facilitate debugging and logging
- Enable circuit breaker patterns

Architecture Integration:
- Base GovernanceError for all governance exceptions
- Specific exceptions for different failure modes
- Supports retry logic and circuit breakers
- Enables proper error propagation
- Integrates with logging system

Sarah's Framework Check:
- What breaks first: Configuration errors before validation errors
- How we know: Exception type in error logs
- Plan B: Catch base GovernanceError for unknown error types
"""


class GovernanceError(Exception):
    """Base exception for governance system"""
    pass


class ValidationError(GovernanceError):
    """Validation failed"""
    pass


class ConfigurationError(GovernanceError):
    """Configuration error"""
    pass


class FrameworkNotFoundError(GovernanceError):
    """Framework not found"""
    pass


class PersonaNotFoundError(GovernanceError):
    """Persona not found"""
    pass


class TimeoutError(GovernanceError):
    """Operation timed out"""
    pass


class CircuitBreakerOpenError(GovernanceError):
    """Circuit breaker is open"""
    pass


class GovernanceViolation(GovernanceError):
    """Governance rule violation detected"""
    pass