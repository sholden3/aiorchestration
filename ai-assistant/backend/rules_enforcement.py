"""
Rules Enforcement Hooks System
Prevents assumption-based behavior and enforces governance
Evidence-Based Implementation with Cross-Persona Validation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import re

from specialized_databases import SpecializedDatabases, RuleEntry
from base_patterns import OrchestrationResult

logger = logging.getLogger(__name__)

class RuleType(Enum):
    """Types of enforcement rules"""
    PRE_EXECUTION = "pre_execution"    # Before action
    POST_EXECUTION = "post_execution"  # After action
    VALIDATION = "validation"           # Data validation
    ASSUMPTION = "assumption"           # Assumption prevention
    EVIDENCE = "evidence"              # Evidence requirement

class RuleViolation:
    """Records a rule violation"""
    def __init__(self, rule_id: str, rule_name: str, message: str, context: Dict = None):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.message = message
        self.context = context or {}
        self.timestamp = datetime.now()
        self.severity = self._calculate_severity()
    
    def _calculate_severity(self) -> str:
        """Calculate violation severity"""
        if "assumption" in self.rule_name.lower():
            return "high"
        elif "evidence" in self.rule_name.lower():
            return "medium"
        else:
            return "low"

class RulesEnforcementEngine:
    """
    Enforces rules to prevent assumption-based behavior
    Sarah: Validates AI operations against rules
    Marcus: Efficient rule evaluation with caching
    Emily: Clear violation reporting
    """
    
    def __init__(self, db: Optional[SpecializedDatabases] = None):
        self.db = db or SpecializedDatabases()
        self.rules_cache: Dict[str, RuleEntry] = {}
        self.hooks: Dict[RuleType, List[Callable]] = {
            rule_type: [] for rule_type in RuleType
        }
        self.violations: List[RuleViolation] = []
        self.max_violations = 1000  # Prevent memory bloat
        
        logger.info("Rules enforcement engine initialized")
    
    async def load_rules(self) -> int:
        """
        Load active rules from database
        Marcus: Caches rules for performance
        """
        if self.db.initialized:
            rules = await self.db.get_active_rules()
            for rule in rules:
                self.rules_cache[rule.id] = rule
            logger.info(f"Loaded {len(rules)} active rules")
            return len(rules)
        return 0
    
    def register_hook(self, rule_type: RuleType, hook: Callable) -> bool:
        """Register a hook for rule type"""
        self.hooks[rule_type].append(hook)
        logger.debug(f"Registered hook for {rule_type.value}")
        return True
    
    async def check_pre_execution(
        self,
        action: str,
        context: Dict[str, Any]
    ) -> OrchestrationResult[bool]:
        """
        Check rules before action execution
        Sarah: Prevents assumption-based actions
        """
        violations = []
        
        # Check assumption prevention rules
        if self._contains_assumption(action, context):
            violation = RuleViolation(
                rule_id="assumption-001",
                rule_name="No Assumptions Allowed",
                message=f"Action contains unverified assumption: {action}",
                context=context
            )
            violations.append(violation)
        
        # Check evidence requirements
        if not self._has_required_evidence(action, context):
            violation = RuleViolation(
                rule_id="evidence-001",
                rule_name="Evidence Required",
                message=f"Action lacks required evidence: {action}",
                context=context
            )
            violations.append(violation)
        
        # Execute custom hooks
        for hook in self.hooks[RuleType.PRE_EXECUTION]:
            try:
                result = await hook(action, context)
                if not result:
                    violations.append(RuleViolation(
                        rule_id="hook-001",
                        rule_name="Custom Hook Failed",
                        message=f"Pre-execution hook rejected action",
                        context=context
                    ))
            except Exception as e:
                logger.error(f"Hook execution failed: {e}")
        
        # Record violations
        for violation in violations:
            self._record_violation(violation)
        
        if violations:
            return OrchestrationResult.error(
                f"Rule violations: {[v.message for v in violations]}",
                violations=len(violations)
            )
        
        return OrchestrationResult.ok(True)
    
    async def check_post_execution(
        self,
        action: str,
        result: Any,
        context: Dict[str, Any]
    ) -> OrchestrationResult[bool]:
        """
        Check rules after action execution
        Marcus: Validates results meet requirements
        """
        violations = []
        
        # Check result contains evidence
        if not self._result_has_evidence(result):
            violation = RuleViolation(
                rule_id="evidence-002",
                rule_name="Result Must Have Evidence",
                message="Result lacks supporting evidence",
                context={'action': action, 'result_type': type(result).__name__}
            )
            violations.append(violation)
        
        # Execute custom hooks
        for hook in self.hooks[RuleType.POST_EXECUTION]:
            try:
                hook_result = await hook(action, result, context)
                if not hook_result:
                    violations.append(RuleViolation(
                        rule_id="hook-002",
                        rule_name="Post Hook Failed",
                        message="Post-execution validation failed",
                        context=context
                    ))
            except Exception as e:
                logger.error(f"Post hook failed: {e}")
        
        for violation in violations:
            self._record_violation(violation)
        
        if violations:
            return OrchestrationResult.error(
                f"Post-execution violations: {[v.message for v in violations]}",
                violations=len(violations)
            )
        
        return OrchestrationResult.ok(True)
    
    def _contains_assumption(self, action: str, context: Dict) -> bool:
        """
        Detect assumption-based language
        Emily: Clear patterns for assumption detection
        """
        assumption_patterns = [
            r'\bshould\s+work\b',
            r'\bprobably\b',
            r'\bassum\w+\b',
            r'\bexpect\w*\s+to\b',
            r'\blikely\b',
            r'\btheoretically\b',
            r'\bestimate\w*\b'
        ]
        
        text_to_check = f"{action} {str(context)}".lower()
        
        for pattern in assumption_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                logger.warning(f"Assumption detected: {pattern}")
                return True
        
        return False
    
    def _has_required_evidence(self, action: str, context: Dict) -> bool:
        """Check if action has required evidence"""
        evidence_keys = ['evidence', 'measurement', 'test_result', 'verification']
        
        # Check context for evidence
        for key in evidence_keys:
            if key in context and context[key]:
                return True
        
        # Actions that always require evidence
        evidence_required_actions = [
            'performance_claim',
            'optimization',
            'improvement',
            'faster',
            'better'
        ]
        
        action_lower = action.lower()
        for required in evidence_required_actions:
            if required in action_lower and not any(k in context for k in evidence_keys):
                logger.warning(f"Action '{action}' requires evidence")
                return False
        
        return True
    
    def _result_has_evidence(self, result: Any) -> bool:
        """Check if result contains evidence"""
        if isinstance(result, dict):
            evidence_indicators = ['measured', 'tested', 'verified', 'actual']
            return any(indicator in str(result).lower() for indicator in evidence_indicators)
        return True  # Non-dict results pass by default
    
    def _record_violation(self, violation: RuleViolation):
        """Record violation with size management"""
        self.violations.append(violation)
        
        # Maintain max violations
        if len(self.violations) > self.max_violations:
            self.violations = self.violations[-self.max_violations:]
        
        logger.warning(f"Rule violation: {violation.rule_name} - {violation.message}")
    
    async def validate_data(
        self,
        data: Dict[str, Any],
        schema_name: str
    ) -> OrchestrationResult[bool]:
        """
        Validate data against rules
        Sarah: Ensures data meets requirements
        """
        violations = []
        
        # Check for magic variables
        magic_patterns = ['localhost', '127.0.0.1', 'hardcoded', 'TODO', 'FIXME']
        data_str = str(data).lower()
        
        for pattern in magic_patterns:
            if pattern.lower() in data_str:
                violations.append(RuleViolation(
                    rule_id="magic-001",
                    rule_name="No Magic Variables",
                    message=f"Data contains magic variable: {pattern}",
                    context={'schema': schema_name}
                ))
        
        if violations:
            for v in violations:
                self._record_violation(v)
            return OrchestrationResult.error(
                f"Validation failed: {[v.message for v in violations]}"
            )
        
        return OrchestrationResult.ok(True)
    
    def get_violations_summary(self) -> Dict[str, Any]:
        """
        Get violations summary
        Marcus: Real metrics from actual violations
        """
        if not self.violations:
            return {
                'total_violations': 0,
                'by_severity': {},
                'by_rule': {},
                'recent': []
            }
        
        by_severity = {}
        by_rule = {}
        
        for violation in self.violations:
            # Count by severity
            severity = violation.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Count by rule
            rule = violation.rule_name
            by_rule[rule] = by_rule.get(rule, 0) + 1
        
        return {
            'total_violations': len(self.violations),
            'by_severity': by_severity,
            'by_rule': by_rule,
            'recent': [
                {
                    'rule': v.rule_name,
                    'message': v.message,
                    'timestamp': v.timestamp.isoformat()
                }
                for v in self.violations[-5:]  # Last 5 violations
            ]
        }
    
    async def enforce_assumption_prevention(
        self,
        text: str
    ) -> OrchestrationResult[str]:
        """
        Clean text of assumption-based language
        Emily: Clear feedback on what was removed
        """
        original = text
        cleaned = text
        
        replacements = {
            'should work': 'requires testing',
            'probably': 'possibly',
            'assuming': 'checking if',
            'expect': 'will verify',
            'likely': 'may',
            'theoretically': 'in theory',
            'estimated': 'calculated'
        }
        
        changes = []
        for old, new in replacements.items():
            if old in cleaned.lower():
                cleaned = re.sub(
                    re.escape(old),
                    new,
                    cleaned,
                    flags=re.IGNORECASE
                )
                changes.append(f"'{old}' -> '{new}'")
        
        if changes:
            logger.info(f"Cleaned assumptions: {', '.join(changes)}")
            return OrchestrationResult.ok(
                cleaned,
                changes=changes,
                original_length=len(original),
                cleaned_length=len(cleaned)
            )
        
        return OrchestrationResult.ok(text, changes=[])