"""
File: ai-assistant/backend/governance/middleware/__init__.py
Purpose: Initialize middleware package for governance system
Architecture: Exports middleware components for request processing
Dependencies: None
Owner: Dr. Sarah Chen

@fileoverview Middleware module exports for governance
@author Dr. Sarah Chen v1.0 - Backend Systems Architect
@architecture Backend - Middleware component exports
@business_logic AI decision injection and request processing
"""

from .ai_decision_injector import AIDecisionInjector, DecisionType

__all__ = ['AIDecisionInjector', 'DecisionType']