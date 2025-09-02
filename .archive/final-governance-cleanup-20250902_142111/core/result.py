"""
@fileoverview Governance result structures for validation outcomes and decisions
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Governance result data structures
@responsibility Structure and manage validation results and governance decisions
@dependencies dataclasses, typing, datetime
@integration_points Engine returns these results, consumed by hooks and reporting
@testing_strategy Unit tests for serialization, aggregation, and result merging
@governance Core result structures for audit trails and decision tracking

Business Logic Summary:
- Structure validation results with confidence scores
- Aggregate multiple validation results
- Track evidence, errors, and warnings
- Support serialization for persistence
- Enable audit trail generation

Architecture Integration:
- Returned by governance engine
- Consumed by hooks and integrations
- Supports result aggregation
- Enables detailed reporting
- Integrates with logging and metrics

Sarah's Framework Check:
- What breaks first: Invalid confidence scores or missing evidence
- How we know: Result validation before return
- Plan B: Default confidence and empty evidence lists
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class ValidationResult:
    """Result from a single validation check"""
    passed: bool
    confidence: float = 1.0
    evidence: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'passed': self.passed,
            'confidence': self.confidence,
            'evidence': self.evidence,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata
        }


@dataclass
class GovernanceResult:
    """
    Result from governance evaluation.
    Contains the final decision and supporting information.
    """
    decision: str  # "approved", "rejected", "review", "error"
    confidence: float = 0.0
    reason: Optional[str] = None
    
    # Detailed results
    persona_results: Dict[str, ValidationResult] = field(default_factory=dict)
    framework_results: Dict[str, ValidationResult] = field(default_factory=dict)
    validator_results: Dict[str, ValidationResult] = field(default_factory=dict)
    
    # Evidence and recommendations
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    context_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'decision': self.decision,
            'confidence': self.confidence,
            'reason': self.reason,
            'persona_results': {k: v.to_dict() for k, v in self.persona_results.items()},
            'framework_results': {k: v.to_dict() for k, v in self.framework_results.items()},
            'validator_results': {k: v.to_dict() for k, v in self.validator_results.items()},
            'evidence': self.evidence,
            'recommendations': self.recommendations,
            'context_id': self.context_id,
            'timestamp': self.timestamp.isoformat(),
            'execution_time_ms': self.execution_time_ms
        }
    
    def is_approved(self) -> bool:
        """Check if decision is approved"""
        return self.decision == "approved"
    
    def is_rejected(self) -> bool:
        """Check if decision is rejected"""
        return self.decision == "rejected"
    
    def __str__(self) -> str:
        """String representation"""
        return f"GovernanceResult(decision={self.decision}, confidence={self.confidence:.2f})"