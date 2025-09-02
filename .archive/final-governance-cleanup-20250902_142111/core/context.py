"""
@fileoverview Governance context object for carrying validation information through the system
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Core governance data structure
@responsibility Define and manage the immutable context that flows through governance validation
@dependencies dataclasses, typing, datetime, uuid
@integration_points All governance components receive and pass this context
@testing_strategy Unit tests for serialization, immutability, and data integrity
@governance Core component that enables traceability and correlation tracking

Business Logic Summary:
- Immutable context object for governance operations
- Carries operation identity, configuration, and metadata
- Enables correlation tracking across distributed operations
- Supports feature flags for validation behavior
- Provides serialization for persistence and logging

Architecture Integration:
- Central data structure for the governance system
- Flows through all validation pipelines
- Enables parent-child operation tracking
- Supports dry-run and strict validation modes
- Integrates with all personas and frameworks

Sarah's Framework Check:
- What breaks first: Missing required fields in context creation
- How we know: Validation errors at context initialization
- Plan B: Default values for non-critical fields
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


@dataclass
class GovernanceContext:
    """
    Immutable context for governance operations.
    Carries all information needed for validation.
    
    This is the core data structure that flows through the entire system.
    """
    # Identity
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    
    # Operation details
    operation_type: str = ""  # e.g., "git_commit", "test_change", "architecture_change"
    operation_subtype: Optional[str] = None
    actor: str = ""  # User or system initiating operation
    
    # Governance configuration
    project_id: Optional[str] = None
    personas: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    
    # Operation data
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    timeout: Optional[float] = None  # Seconds
    
    # Feature flags
    strict_mode: bool = False  # Fail on any validation error
    dry_run: bool = False      # Validate without side effects
    bypass_cache: bool = False  # Force fresh validation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'operation_id': self.operation_id,
            'correlation_id': self.correlation_id,
            'parent_id': self.parent_id,
            'operation_type': self.operation_type,
            'operation_subtype': self.operation_subtype,
            'actor': self.actor,
            'project_id': self.project_id,
            'personas': self.personas,
            'frameworks': self.frameworks,
            'rules': self.rules,
            'payload': self.payload,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'timeout': self.timeout,
            'strict_mode': self.strict_mode,
            'dry_run': self.dry_run,
            'bypass_cache': self.bypass_cache
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GovernanceContext':
        """Create from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)
    
    def __str__(self) -> str:
        """String representation"""
        return f"GovernanceContext(op={self.operation_type}, actor={self.actor}, id={self.operation_id[:8]})"