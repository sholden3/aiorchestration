"""
@fileoverview Middleware package - Interception layer for AI decisions
@author Dr. Sarah Chen v1.0 & Alex Novak v1.0 - 2025-08-29
@architecture Backend - Middleware layer
@responsibility Intercept and validate AI decisions before execution
@dependencies asyncio, core governance, validators
@integration_points AI agents, decision pipeline, audit system
@testing_strategy Interception tests, modification tests, performance tests
@governance Middleware enforces governance on all AI outputs

Business Logic Summary:
- Intercept AI decisions
- Multi-persona validation
- Risk assessment
- Decision modification
- Audit trail generation

Architecture Integration:
- Async middleware pattern
- Chain of responsibility
- Decorator pattern
- Strategy pattern
- Observer pattern

Sarah's Framework Check:
- What breaks first: Middleware timeout on complex decisions
- How we know: Decision latency metrics exceed SLA
- Plan B: Fast-path for low-risk decisions

Middleware Components:
- AIDecisionInjector: Main decision interceptor
- PersonaConsultation: Multi-persona validation
- RiskAssessment: Risk scoring
- DecisionModifier: Safe decision transformation
- AuditLogger: Decision audit trail

Usage Pattern:
    from governance.middleware import AIDecisionInjector
    
    injector = AIDecisionInjector()
    validation = await injector.intercept_decision(
        agent_id=agent_id,
        decision_type=DecisionType.CODE_GENERATION,
        proposed_output=code
    )
"""

from .ai_decision_injector import (
    AIDecisionInjector,
    DecisionType,
    DecisionValidation,
    RiskLevel,
    PersonaConsultation
)

__all__ = [
    'AIDecisionInjector',
    'DecisionType',
    'DecisionValidation',
    'RiskLevel',
    'PersonaConsultation'
]