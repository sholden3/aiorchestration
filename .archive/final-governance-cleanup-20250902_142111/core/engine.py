"""
@fileoverview Main governance orchestration engine for validation pipeline execution
@author Dr. Sarah Chen v1.5 - 2025-08-29
@architecture Backend - Core governance orchestration engine
@responsibility Orchestrate governance validation, manage rule execution, coordinate personas
@dependencies logging, pathlib, context, result, exceptions modules
@integration_points Personas, validators, rules, hooks, storage systems
@testing_strategy Unit tests for pipeline, integration tests for full validation flow
@governance Central orchestration point for all governance operations

Business Logic Summary:
- Orchestrate governance validation pipeline
- Load and manage validation rules
- Coordinate persona invocations
- Aggregate validation results
- Handle validation errors and timeouts
- Manage logging and audit trails

Architecture Integration:
- Central hub of the governance system
- Receives context and returns results
- Integrates with all validators and personas
- Manages validation pipeline flow
- Handles caching and performance optimization

Sarah's Framework Check:
- What breaks first: Rule loading failures or validator timeouts
- How we know: Comprehensive logging and error tracking
- Plan B: Graceful degradation with partial validation
"""

import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .context import GovernanceContext
from .result import GovernanceResult, ValidationResult
from .exceptions import GovernanceError, ValidationError


# Configure logging
import os
from datetime import datetime

# Create logs directory
log_dir = Path(".governance/logs")
log_dir.mkdir(parents=True, exist_ok=True)

# Create log file with timestamp
log_file = log_dir / f"governance_{datetime.now().strftime('%Y%m%d')}.log"

# Configure both file and console logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GovernanceEngine:
    """
    Main governance orchestration engine.
    This is the minimal version that we'll enhance incrementally.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the governance engine.
        
        Args:
            config_path: Path to configuration directory
        """
        self.config_path = config_path or Path("governance/definitions")
        self.evaluation_count = 0
        self.start_time = time.time()
        
        # Track decisions for metrics
        self.decision_history = []
        
        # Simple rules for initial testing
        self.rules = {
            "dangerous_operations": ["delete_all", "drop_database", "force_push"],
            "requires_review": ["architecture_change", "security_change"],
            "auto_approve": ["documentation", "typo_fix"]
        }
        
        logger.info(f"Governance Engine initialized with config path: {self.config_path}")
    
    def evaluate(self, context: GovernanceContext) -> GovernanceResult:
        """
        Evaluate governance rules for the given context.
        This is the main entry point for governance evaluation.
        
        Args:
            context: The governance context to evaluate
            
        Returns:
            GovernanceResult with the decision
        """
        start_time = time.time()
        self.evaluation_count += 1
        
        logger.info(f"Starting evaluation {self.evaluation_count}: {context}")
        
        # Audit log the request
        self._audit_log("evaluation_start", context, None)
        
        try:
            # Simple rule evaluation for now
            result = self._evaluate_simple_rules(context)
            
            # Track decision
            self.decision_history.append({
                'decision': result.decision,
                'operation_type': context.operation_type,
                'timestamp': time.time()
            })
            
            # Calculate execution time
            execution_time = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time
            result.context_id = context.operation_id
            
            # Audit log the result
            self._audit_log("evaluation_complete", context, result)
            
            logger.info(f"Evaluation complete: {result} in {execution_time:.2f}ms")
            
            # Log warning for rejected operations
            if result.is_rejected():
                logger.warning(f"Operation REJECTED: {context.operation_type} by {context.actor} - {result.reason}")
            
            return result
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return GovernanceResult(
                decision="error",
                reason=str(e),
                confidence=0.0,
                context_id=context.operation_id
            )
    
    def _evaluate_simple_rules(self, context: GovernanceContext) -> GovernanceResult:
        """
        Simple rule evaluation for initial testing.
        This will be replaced with more sophisticated evaluation.
        """
        operation = context.operation_type
        
        # Check dangerous operations
        if operation in self.rules["dangerous_operations"]:
            return GovernanceResult(
                decision="rejected",
                reason=f"Operation '{operation}' is marked as dangerous",
                confidence=1.0,
                evidence=[f"Operation {operation} is in dangerous list"]
            )
        
        # Check if review required
        if operation in self.rules["requires_review"]:
            return GovernanceResult(
                decision="review",
                reason=f"Operation '{operation}' requires review",
                confidence=0.8,
                evidence=[f"Operation {operation} requires human review"],
                recommendations=["Please get approval from team lead"]
            )
        
        # Check auto-approve
        if operation in self.rules["auto_approve"]:
            return GovernanceResult(
                decision="approved",
                confidence=1.0,
                evidence=[f"Operation {operation} is pre-approved"]
            )
        
        # Check payload for specific patterns
        if "test" in context.operation_type.lower():
            # Test operations get approved with lower confidence
            return GovernanceResult(
                decision="approved",
                confidence=0.7,
                evidence=["Test operation detected"]
            )
        
        # Default: approve with medium confidence
        return GovernanceResult(
            decision="approved",
            confidence=0.5,
            evidence=["No specific rules matched, defaulting to approval"],
            recommendations=["Consider adding specific rules for this operation type"]
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get engine metrics.
        """
        uptime = time.time() - self.start_time
        
        # Calculate approval rate
        if self.decision_history:
            approvals = sum(1 for d in self.decision_history if d['decision'] == 'approved')
            approval_rate = approvals / len(self.decision_history)
        else:
            approval_rate = 0.0
        
        return {
            'evaluation_count': self.evaluation_count,
            'uptime_seconds': uptime,
            'approval_rate': approval_rate,
            'total_decisions': len(self.decision_history),
            'decisions_by_type': self._count_decisions_by_type()
        }
    
    def _count_decisions_by_type(self) -> Dict[str, int]:
        """Count decisions by type"""
        counts = {}
        for decision in self.decision_history:
            decision_type = decision['decision']
            counts[decision_type] = counts.get(decision_type, 0) + 1
        return counts
    
    def add_rule(self, rule_type: str, value: str):
        """
        Add a new rule dynamically.
        
        Args:
            rule_type: Type of rule (dangerous_operations, requires_review, auto_approve)
            value: The value to add to the rule
        """
        if rule_type in self.rules:
            if value not in self.rules[rule_type]:
                self.rules[rule_type].append(value)
                logger.info(f"Added rule: {rule_type} -> {value}")
        else:
            logger.warning(f"Unknown rule type: {rule_type}")
    
    def remove_rule(self, rule_type: str, value: str):
        """
        Remove a rule dynamically.
        
        Args:
            rule_type: Type of rule
            value: The value to remove
        """
        if rule_type in self.rules and value in self.rules[rule_type]:
            self.rules[rule_type].remove(value)
            logger.info(f"Removed rule: {rule_type} -> {value}")
    
    def _audit_log(self, event_type: str, context: GovernanceContext, result: Optional[GovernanceResult]):
        """
        Write audit log entry
        """
        audit_dir = Path(".governance/audit")
        audit_dir.mkdir(parents=True, exist_ok=True)
        
        audit_file = audit_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'operation_id': context.operation_id,
            'correlation_id': context.correlation_id,
            'operation_type': context.operation_type,
            'actor': context.actor,
            'decision': result.decision if result else None,
            'confidence': result.confidence if result else None,
            'reason': result.reason if result else None
        }
        
        try:
            import json
            with open(audit_file, 'a') as f:
                f.write(json.dumps(audit_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def __str__(self) -> str:
        """String representation"""
        return f"GovernanceEngine(evaluations={self.evaluation_count})"