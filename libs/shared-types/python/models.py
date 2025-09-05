"""
@fileoverview Shared Pydantic models for cross-cutting concerns
@author Dr. Sarah Chen & Alex Novak - Enterprise Architects
@architecture Shared Types Library
@description Base models and schemas used throughout Python services
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from .enums import (
    RuleSeverity,
    RuleStatus,
    TemplateType,
    SessionStatus,
    AuditEventType,
    EntityType,
    GovernanceLevel,
    RiskLevel
)

T = TypeVar('T')

# ============== BASE MODELS ==============

class TimestampedModel(BaseModel):
    """Base model with timestamps"""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class AuthoredModel(BaseModel):
    """Base model with authorship"""
    author: Optional[str] = None
    version: int = 1
    
    model_config = ConfigDict(from_attributes=True)


class TaggableModel(BaseModel):
    """Base model with tags and metadata"""
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class BaseEntity(TimestampedModel):
    """Base entity with ID and timestamps"""
    id: Optional[UUID] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============== PAGINATION ==============

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = 0
    limit: int = 100
    sort_by: Optional[str] = None
    order: str = "asc"
    
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool = False
    
    model_config = ConfigDict(from_attributes=True)


# ============== VALIDATION ==============

class ValidationError(BaseModel):
    """Validation error details"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None
    severity: Optional[RuleSeverity] = RuleSeverity.ERROR
    
    model_config = ConfigDict(from_attributes=True)


class ValidationWarning(BaseModel):
    """Validation warning details"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None
    suggestion: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ValidationResult(BaseModel):
    """Validation result"""
    valid: bool
    score: Optional[float] = None
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[ValidationWarning] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


# ============== API RESPONSES ==============

class ApiError(BaseModel):
    """API error response"""
    code: Optional[str] = None
    message: str
    detail: Optional[str] = None
    field: Optional[str] = None
    stack: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ResponseMetadata(BaseModel):
    """Response metadata"""
    request_id: Optional[str] = None
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    duration_ms: Optional[int] = None
    version: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response"""
    success: bool
    data: Optional[T] = None
    error: Optional[ApiError] = None
    metadata: Optional[ResponseMetadata] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============== AUDIT ==============

class AuditEntry(BaseModel):
    """Audit log entry"""
    id: UUID
    event_type: AuditEventType
    entity_type: EntityType
    entity_id: Optional[str] = None
    action: str
    actor: str
    session_id: Optional[str] = None
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============== GOVERNANCE ==============

class GovernanceContext(BaseModel):
    """Governance execution context"""
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    rules: List[str] = Field(default_factory=list)
    compliance_level: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class RuleViolation(BaseModel):
    """Rule violation details"""
    rule_id: str
    rule_name: str
    severity: RuleSeverity
    message: str
    context: Optional[Dict[str, Any]] = None
    fix_suggestion: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ComplianceWarning(BaseModel):
    """Compliance warning"""
    message: str
    severity: RuleSeverity
    context: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


class ComplianceResult(BaseModel):
    """Compliance check result"""
    compliant: bool
    score: float
    violations: List[RuleViolation] = Field(default_factory=list)
    warnings: List[ComplianceWarning] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


# ============== METRICS ==============

class MetricPoint(BaseModel):
    """Single metric point"""
    name: str
    value: float
    timestamp: datetime = Field(default_factory=datetime.now)
    tags: Dict[str, str] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class PerformanceMetrics(BaseModel):
    """Performance metrics"""
    response_time_ms: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    request_count: Optional[int] = None
    error_count: Optional[int] = None
    success_rate: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============== CONFIGURATION ==============

class ConfigValue(BaseModel, Generic[T]):
    """Configuration value"""
    key: str
    value: T
    description: Optional[str] = None
    type: Optional[str] = None
    default: Optional[T] = None
    required: bool = False
    validation: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class FeatureFlag(BaseModel):
    """Feature flag configuration"""
    key: str
    enabled: bool
    description: Optional[str] = None
    rollout_percentage: Optional[int] = None
    conditions: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============== ERROR HANDLING ==============

class ErrorContext(BaseModel):
    """Error context information"""
    error: str  # String representation of error
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    stack: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class CircuitBreakerState(BaseModel):
    """Circuit breaker state"""
    state: str  # 'CLOSED' | 'OPEN' | 'HALF_OPEN'
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None
    success_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)