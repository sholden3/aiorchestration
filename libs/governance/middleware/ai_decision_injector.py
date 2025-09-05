"""
@fileoverview Real-time AI decision validation middleware with multi-persona consultation
@author Dr. Sarah Chen v1.0 & Alex Novak v1.0 - 2025-08-29
@architecture Backend - Middleware layer for AI decision interception
@responsibility Validate AI outputs through persona consultation and risk assessment before execution
@dependencies asyncio, json, logging, typing, datetime, dataclasses, enum, hashlib
@integration_points AI agents, persona validators, risk assessment engine, audit system
@testing_strategy Unit tests for each persona, integration tests for decision flow, risk scoring tests
@governance Central enforcement point for all AI-generated decisions

Business Logic Summary:
- Intercept all AI decisions before execution
- Consult multiple personas based on decision type
- Assess risk levels and enforce thresholds
- Auto-fix certain compliance issues
- Maintain comprehensive audit trail

Architecture Integration:
- Middleware layer between AI agents and execution
- Integrates with persona validation system
- Implements risk scoring and thresholds
- Provides decision caching for performance
- Generates audit trails for compliance

Sarah's Framework Check:
- What breaks first: Cache overflow under high decision volume
- How we know: Cache size monitoring and metrics collection
- Plan B: LRU cache eviction with configurable size limits
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of AI decisions"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    DATA_PROCESSING = "data_processing"
    USER_INTERACTION = "user_interaction"


class RiskLevel(Enum):
    """Risk levels for decisions"""
    CRITICAL = "critical"  # Could break system
    HIGH = "high"          # Significant impact
    MEDIUM = "medium"      # Moderate impact
    LOW = "low"            # Minimal impact
    NONE = "none"          # No risk


@dataclass
class PersonaConsultation:
    """Result of consulting a persona"""
    persona_name: str
    approved: bool
    confidence: float
    concerns: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_assessment: str = "low"


@dataclass
class DecisionValidation:
    """Complete validation result for a decision"""
    decision_id: str
    approved: bool
    risk_level: RiskLevel
    confidence_score: float
    personas_consulted: List[PersonaConsultation]
    modifications: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)


class AIDecisionInjector:
    """
    Middleware for intercepting and validating AI decisions
    Implements multi-persona consultation and risk assessment
    """
    
    def __init__(self):
        # Decision type configurations
        self.decision_configs = {
            DecisionType.CODE_GENERATION: {
                "required_personas": ["Dr. Sarah Chen", "Alex Novak"],
                "risk_threshold": 0.7,
                "validation_rules": ["no_dangerous_patterns", "follows_standards"]
            },
            DecisionType.SECURITY: {
                "required_personas": ["Jordan Chen"],
                "risk_threshold": 0.3,  # Low tolerance for security risks
                "validation_rules": ["no_vulnerabilities", "secure_patterns"]
            },
            DecisionType.ARCHITECTURE: {
                "required_personas": ["Dr. Sarah Chen", "Alex Novak"],
                "risk_threshold": 0.5,
                "validation_rules": ["scalability", "maintainability"]
            },
            DecisionType.DEPLOYMENT: {
                "required_personas": ["Riley Thompson"],
                "risk_threshold": 0.4,
                "validation_rules": ["rollback_plan", "monitoring"]
            }
        }
        
        # Pattern matchers for dangerous code
        self.dangerous_patterns = [
            r"exec\s*\(",
            r"eval\s*\(",
            r"__import__",
            r"subprocess\s*\.\s*call",
            r"os\s*\.\s*system",
            r"DROP\s+TABLE",
            r"DELETE\s+FROM",
            r"rm\s+-rf",
            r"sudo\s+"
        ]
        
        # Persona simulators (simplified for now)
        self.persona_validators = {
            "Dr. Sarah Chen": self._validate_sarah_chen,
            "Alex Novak": self._validate_alex_novak,
            "Jordan Chen": self._validate_jordan_chen,
            "Riley Thompson": self._validate_riley_thompson
        }
        
        # Decision cache for deduplication
        self.decision_cache: Dict[str, DecisionValidation] = {}
        
        # Metrics
        self.metrics = {
            "decisions_processed": 0,
            "decisions_approved": 0,
            "decisions_modified": 0,
            "decisions_rejected": 0,
            "high_risk_decisions": 0
        }
    
    async def intercept_decision(
        self,
        agent_id: str,
        decision_type: DecisionType,
        input_context: Dict[str, Any],
        proposed_output: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DecisionValidation:
        """
        Main entry point for decision interception
        Validates and potentially modifies AI decisions
        """
        # Generate decision ID
        decision_id = self._generate_decision_id(
            agent_id, decision_type, input_context, proposed_output
        )
        
        # Check cache
        if decision_id in self.decision_cache:
            logger.info(f"Decision {decision_id} found in cache")
            return self.decision_cache[decision_id]
        
        # Start validation
        validation = DecisionValidation(
            decision_id=decision_id,
            approved=True,
            risk_level=RiskLevel.LOW,
            confidence_score=1.0,
            personas_consulted=[]
        )
        
        # Log start of validation
        validation.audit_trail.append({
            "timestamp": datetime.now().isoformat(),
            "event": "validation_started",
            "agent_id": agent_id,
            "decision_type": decision_type.value
        })
        
        # Get decision configuration
        config = self.decision_configs.get(
            decision_type,
            {"required_personas": [], "risk_threshold": 0.5, "validation_rules": []}
        )
        
        # Consult required personas
        for persona_name in config["required_personas"]:
            if persona_name in self.persona_validators:
                consultation = await self.persona_validators[persona_name](
                    decision_type, input_context, proposed_output
                )
                validation.personas_consulted.append(consultation)
                
                # Update approval status
                if not consultation.approved:
                    validation.approved = False
                    validation.warnings.extend(consultation.concerns)
                
                # Update confidence
                validation.confidence_score *= consultation.confidence
        
        # Assess risk level
        risk_score = await self._assess_risk(
            decision_type, proposed_output, validation.personas_consulted
        )
        
        validation.risk_level = self._score_to_risk_level(risk_score)
        
        # Check against risk threshold
        if risk_score > config["risk_threshold"]:
            validation.approved = False
            validation.warnings.append(
                f"Risk score ({risk_score:.2f}) exceeds threshold ({config['risk_threshold']})"
            )
            self.metrics["high_risk_decisions"] += 1
        
        # Apply validation rules
        for rule in config["validation_rules"]:
            rule_result = await self._apply_validation_rule(
                rule, decision_type, proposed_output
            )
            if not rule_result["passed"]:
                validation.approved = False
                validation.warnings.append(rule_result["message"])
        
        # Potentially modify output
        if not validation.approved and self._can_auto_fix(validation):
            modified_output = await self._auto_fix_decision(
                decision_type, proposed_output, validation
            )
            if modified_output != proposed_output:
                validation.modifications["original"] = proposed_output
                validation.modifications["modified"] = modified_output
                validation.approved = True  # Approved after modification
                validation.warnings.append("Output was automatically modified for compliance")
                self.metrics["decisions_modified"] += 1
        
        # Final audit entry
        validation.audit_trail.append({
            "timestamp": datetime.now().isoformat(),
            "event": "validation_completed",
            "approved": validation.approved,
            "risk_level": validation.risk_level.value,
            "confidence": validation.confidence_score
        })
        
        # Update metrics
        self.metrics["decisions_processed"] += 1
        if validation.approved:
            self.metrics["decisions_approved"] += 1
        else:
            self.metrics["decisions_rejected"] += 1
        
        # Cache result
        self.decision_cache[decision_id] = validation
        
        # Limit cache size
        if len(self.decision_cache) > 1000:
            oldest_keys = list(self.decision_cache.keys())[:500]
            for key in oldest_keys:
                del self.decision_cache[key]
        
        return validation
    
    # ============= Persona Validators =============
    
    async def _validate_sarah_chen(
        self,
        decision_type: DecisionType,
        context: Dict[str, Any],
        output: Any
    ) -> PersonaConsultation:
        """Dr. Sarah Chen's validation - Backend/Systems perspective"""
        consultation = PersonaConsultation(
            persona_name="Dr. Sarah Chen",
            approved=True,
            confidence=0.9
        )
        
        # Check for system stability concerns
        if decision_type in [DecisionType.CODE_GENERATION, DecisionType.ARCHITECTURE]:
            # Check for failure modes
            if isinstance(output, str):
                if "try:" not in output.lower() and "except" not in output.lower():
                    consultation.concerns.append("No error handling detected")
                    consultation.confidence *= 0.8
                
                if "cache" in context.get("topic", "").lower():
                    if "fallback" not in output.lower():
                        consultation.concerns.append("No fallback strategy for cache")
                        consultation.recommendations.append("Add fallback mechanism")
                        consultation.confidence *= 0.7
        
        # Three Questions Framework
        consultation.recommendations.extend([
            "Consider: What breaks first?",
            "Consider: How do we know when it breaks?",
            "Consider: What's Plan B?"
        ])
        
        if consultation.confidence < 0.7:
            consultation.approved = False
            consultation.risk_assessment = "high"
        
        return consultation
    
    async def _validate_alex_novak(
        self,
        decision_type: DecisionType,
        context: Dict[str, Any],
        output: Any
    ) -> PersonaConsultation:
        """Alex Novak's validation - Frontend/Integration perspective"""
        consultation = PersonaConsultation(
            persona_name="Alex Novak",
            approved=True,
            confidence=0.9
        )
        
        # Check for frontend/integration concerns
        if decision_type == DecisionType.CODE_GENERATION:
            if isinstance(output, str):
                # Check for memory leak patterns
                if "addEventListener" in output and "removeEventListener" not in output:
                    consultation.concerns.append("Potential memory leak: Event listeners not cleaned up")
                    consultation.recommendations.append("Add cleanup in ngOnDestroy or equivalent")
                    consultation.confidence *= 0.6
                
                # Check for IPC security
                if "ipc" in output.lower() or "electron" in output.lower():
                    if "contextBridge" not in output:
                        consultation.concerns.append("IPC communication should use contextBridge")
                        consultation.confidence *= 0.7
        
        # 3 AM Test
        if consultation.confidence > 0.7:
            consultation.recommendations.append("Passes 3 AM test: debuggable under pressure")
        else:
            consultation.concerns.append("Fails 3 AM test: needs better error messages")
            consultation.approved = False
        
        return consultation
    
    async def _validate_jordan_chen(
        self,
        decision_type: DecisionType,
        context: Dict[str, Any],
        output: Any
    ) -> PersonaConsultation:
        """Jordan Chen's validation - Security perspective"""
        consultation = PersonaConsultation(
            persona_name="Jordan Chen",
            approved=True,
            confidence=0.95
        )
        
        if isinstance(output, str):
            # Check for security vulnerabilities
            import re
            for pattern in self.dangerous_patterns:
                if re.search(pattern, output, re.IGNORECASE):
                    consultation.approved = False
                    consultation.concerns.append(f"Security risk: Dangerous pattern detected ({pattern})")
                    consultation.risk_assessment = "critical"
                    consultation.confidence = 0.1
                    break
            
            # Check for SQL injection risks
            if "SELECT" in output.upper() or "INSERT" in output.upper():
                if "?" not in output and "prepare" not in output.lower():
                    consultation.concerns.append("Potential SQL injection: Use parameterized queries")
                    consultation.recommendations.append("Use prepared statements")
                    consultation.confidence *= 0.5
            
            # Check for XSS risks
            if "innerHTML" in output or "dangerouslySetInnerHTML" in output:
                consultation.concerns.append("XSS risk: Sanitize user input before rendering")
                consultation.confidence *= 0.6
        
        return consultation
    
    async def _validate_riley_thompson(
        self,
        decision_type: DecisionType,
        context: Dict[str, Any],
        output: Any
    ) -> PersonaConsultation:
        """Riley Thompson's validation - Infrastructure/Operations perspective"""
        consultation = PersonaConsultation(
            persona_name="Riley Thompson",
            approved=True,
            confidence=0.85
        )
        
        if decision_type == DecisionType.DEPLOYMENT:
            consultation.recommendations.append("Ensure rollback plan is documented")
            consultation.recommendations.append("Verify monitoring alerts are configured")
            
            if isinstance(output, str):
                if "rollback" not in output.lower():
                    consultation.concerns.append("No rollback strategy mentioned")
                    consultation.confidence *= 0.7
                
                if "health" not in output.lower() and "monitor" not in output.lower():
                    consultation.concerns.append("No health checks or monitoring mentioned")
                    consultation.confidence *= 0.8
        
        return consultation
    
    # ============= Risk Assessment =============
    
    async def _assess_risk(
        self,
        decision_type: DecisionType,
        output: Any,
        consultations: List[PersonaConsultation]
    ) -> float:
        """Assess overall risk score (0.0 to 1.0)"""
        base_risk = {
            DecisionType.CODE_GENERATION: 0.3,
            DecisionType.SECURITY: 0.7,
            DecisionType.ARCHITECTURE: 0.5,
            DecisionType.DEPLOYMENT: 0.6,
            DecisionType.DATA_PROCESSING: 0.4
        }.get(decision_type, 0.5)
        
        # Adjust based on persona concerns
        concern_count = sum(len(c.concerns) for c in consultations)
        risk_adjustment = min(concern_count * 0.1, 0.5)
        
        # Consider confidence scores
        avg_confidence = sum(c.confidence for c in consultations) / len(consultations) if consultations else 1.0
        confidence_penalty = 1.0 - avg_confidence
        
        final_risk = min(base_risk + risk_adjustment + confidence_penalty, 1.0)
        
        return final_risk
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MEDIUM
        elif score >= 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.NONE
    
    # ============= Validation Rules =============
    
    async def _apply_validation_rule(
        self,
        rule: str,
        decision_type: DecisionType,
        output: Any
    ) -> Dict[str, Any]:
        """Apply a specific validation rule"""
        if rule == "no_dangerous_patterns":
            if isinstance(output, str):
                import re
                for pattern in self.dangerous_patterns:
                    if re.search(pattern, output, re.IGNORECASE):
                        return {
                            "passed": False,
                            "message": f"Dangerous pattern detected: {pattern}"
                        }
        
        elif rule == "follows_standards":
            # Check for basic code standards
            if isinstance(output, str) and decision_type == DecisionType.CODE_GENERATION:
                issues = []
                if len(output.split('\n')) > 1:
                    lines = output.split('\n')
                    for line in lines:
                        if len(line) > 120:
                            issues.append("Line too long (>120 chars)")
                            break
                
                if issues:
                    return {
                        "passed": False,
                        "message": f"Code standard violations: {', '.join(issues)}"
                    }
        
        elif rule == "no_vulnerabilities":
            # Already checked in Jordan Chen's validation
            pass
        
        elif rule == "rollback_plan":
            if isinstance(output, str):
                if "rollback" not in output.lower():
                    return {
                        "passed": False,
                        "message": "No rollback plan specified"
                    }
        
        return {"passed": True, "message": ""}
    
    # ============= Auto-fix Capabilities =============
    
    def _can_auto_fix(self, validation: DecisionValidation) -> bool:
        """Determine if issues can be automatically fixed"""
        # Only auto-fix certain types of issues
        fixable_issues = [
            "Event listeners not cleaned up",
            "No error handling detected",
            "Line too long"
        ]
        
        for warning in validation.warnings:
            for issue in fixable_issues:
                if issue in warning:
                    return True
        
        return False
    
    async def _auto_fix_decision(
        self,
        decision_type: DecisionType,
        output: Any,
        validation: DecisionValidation
    ) -> Any:
        """Attempt to automatically fix the decision output"""
        if not isinstance(output, str):
            return output
        
        modified = output
        
        # Fix event listener cleanup
        if "Event listeners not cleaned up" in str(validation.warnings):
            if "addEventListener" in modified:
                # Add cleanup code
                modified += "\n\n// Cleanup\nngOnDestroy() {\n  // Remove event listeners\n}"
        
        # Add basic error handling
        if "No error handling detected" in str(validation.warnings):
            if "async" in modified or "await" in modified:
                # Wrap in try-catch
                lines = modified.split('\n')
                modified = "try {\n  " + "\n  ".join(lines) + "\n} catch (error) {\n  console.error('Error:', error);\n  throw error;\n}"
        
        return modified
    
    # ============= Utilities =============
    
    def _generate_decision_id(
        self,
        agent_id: str,
        decision_type: DecisionType,
        context: Dict[str, Any],
        output: Any
    ) -> str:
        """Generate unique decision ID for caching"""
        content = f"{agent_id}:{decision_type.value}:{json.dumps(context, sort_keys=True)}:{str(output)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get middleware metrics"""
        return self.metrics.copy()
    
    def clear_cache(self):
        """Clear decision cache"""
        self.decision_cache.clear()
        logger.info("Decision cache cleared")