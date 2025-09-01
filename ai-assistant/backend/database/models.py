"""
@fileoverview Database models for AI Development Assistant
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - Database Layer
@business_logic Core entity definitions for governance system
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, 
    DateTime, JSON, ForeignKey, Table, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

Base = declarative_base()

# Association tables
rule_tags = Table('rule_tags', Base.metadata,
    Column('rule_id', UUID(as_uuid=True), ForeignKey('rules.id')),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'))
)

template_variables = Table('template_variables_assoc', Base.metadata,
    Column('template_id', UUID(as_uuid=True), ForeignKey('templates.id')),
    Column('variable_id', UUID(as_uuid=True), ForeignKey('template_variables.id'))
)

# Enums
class RuleSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class RuleStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"

class TemplateType(str, Enum):
    DOCUMENTATION = "documentation"
    CODE = "code"
    PROMPT = "prompt"
    PERSONA = "persona"
    WORKFLOW = "workflow"

class SessionStatus(str, Enum):
    ACTIVE = "active"
    WARNING = "warning"
    EXPIRED = "expired"
    ENDED = "ended"

# Models
class Rule(Base):
    """Governance rules model"""
    __tablename__ = 'rules'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(50))
    severity = Column(String(20), default=RuleSeverity.INFO)
    status = Column(String(20), default=RuleStatus.DRAFT)
    
    # Rule logic
    condition = Column(Text, nullable=False)  # Python expression or JSON
    action = Column(Text, nullable=False)     # Action to take
    parameters = Column(JSON)                 # Additional parameters
    
    # Metadata
    author = Column(String(100))
    version = Column(Integer, default=1)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('rules.id'))
    
    # Effectiveness tracking
    enforcement_count = Column(Integer, default=0)
    violation_count = Column(Integer, default=0)
    effectiveness_score = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    tags = relationship("Tag", secondary=rule_tags, back_populates="rules")
    children = relationship("Rule", backref="parent", remote_side=[id])
    audit_logs = relationship("AuditLog", back_populates="rule")
    
    # Indexes
    __table_args__ = (
        Index('idx_rule_status', 'status'),
        Index('idx_rule_category', 'category'),
        Index('idx_rule_severity', 'severity'),
    )
    
    @validates('severity')
    def validate_severity(self, key, value):
        if value not in [s.value for s in RuleSeverity]:
            raise ValueError(f"Invalid severity: {value}")
        return value
    
    def to_dict(self) -> Dict:
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'severity': self.severity,
            'status': self.status,
            'condition': self.condition,
            'action': self.action,
            'parameters': self.parameters,
            'effectiveness_score': self.effectiveness_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Practice(Base):
    """Best practices model"""
    __tablename__ = 'practices'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    category = Column(String(50))
    description = Column(Text)
    rationale = Column(Text)
    
    # Content
    examples = Column(JSON)        # List of examples
    anti_patterns = Column(JSON)   # What not to do
    references = Column(JSON)      # External references
    
    # Scoring
    score_weight = Column(Float, default=1.0)
    votes_up = Column(Integer, default=0)
    votes_down = Column(Integer, default=0)
    effectiveness_score = Column(Float)
    adoption_rate = Column(Float)
    
    # Metadata
    author = Column(String(100))
    tags = Column(JSON)  # Simple list of tags
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    applications = relationship("PracticeApplication", back_populates="practice")
    
    # Indexes
    __table_args__ = (
        Index('idx_practice_category', 'category'),
        Index('idx_practice_effectiveness', 'effectiveness_score'),
    )
    
    def calculate_effectiveness(self) -> float:
        """Calculate effectiveness based on votes and applications"""
        if self.votes_up + self.votes_down == 0:
            return 0.5
        return self.votes_up / (self.votes_up + self.votes_down)
    
    def to_dict(self) -> Dict:
        return {
            'id': str(self.id),
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'rationale': self.rationale,
            'examples': self.examples,
            'effectiveness_score': self.effectiveness_score,
            'adoption_rate': self.adoption_rate
        }


class Template(Base):
    """Templates model"""
    __tablename__ = 'templates'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)
    category = Column(String(100))
    
    # Content
    template_content = Column(Text, nullable=False)
    description = Column(Text)
    example_usage = Column(JSON)
    
    # Variables and validation
    variables = Column(JSON)  # List of variable definitions
    validation_rules = Column(JSON)
    metadata = Column(JSON)
    
    # Versioning
    version = Column(Integer, default=1)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('templates.id'))
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float)
    
    # Metadata
    author = Column(String(100))
    tags = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    children = relationship("Template", backref="parent", remote_side=[id])
    usage_logs = relationship("TemplateUsage", back_populates="template")
    
    # Indexes
    __table_args__ = (
        Index('idx_template_type', 'type'),
        Index('idx_template_category', 'category'),
        UniqueConstraint('name', 'version', name='uq_template_name_version'),
    )
    
    @validates('type')
    def validate_type(self, key, value):
        if value not in [t.value for t in TemplateType]:
            raise ValueError(f"Invalid template type: {value}")
        return value
    
    def to_dict(self) -> Dict:
        return {
            'id': str(self.id),
            'name': self.name,
            'type': self.type,
            'category': self.category,
            'template_content': self.template_content,
            'variables': self.variables,
            'version': self.version,
            'usage_count': self.usage_count
        }


class Session(Base):
    """Development sessions model"""
    __tablename__ = 'sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(100), unique=True, nullable=False)
    
    # Session info
    architects = Column(JSON)  # List of architects
    status = Column(String(20), default=SessionStatus.ACTIVE)
    environment = Column(JSON)  # Environment details
    
    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # Metadata
    metadata = Column(JSON)
    metrics = Column(JSON)  # Performance metrics
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="session")
    ai_decisions = relationship("AIDecision", back_populates="session")
    
    # Indexes
    __table_args__ = (
        Index('idx_session_status', 'status'),
        Index('idx_session_start', 'start_time'),
    )
    
    def calculate_duration(self):
        """Calculate session duration"""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)
    
    def to_dict(self) -> Dict:
        return {
            'id': str(self.id),
            'session_id': self.session_id,
            'architects': self.architects,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes
        }


class AIDecision(Base):
    """AI decision tracking model"""
    __tablename__ = 'ai_decisions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Decision info
    decision_type = Column(String(50), nullable=False)
    persona = Column(String(100))
    task = Column(Text)
    
    # Decision details
    input_context = Column(JSON)
    decision_chain = Column(JSON)  # Step-by-step reasoning
    output = Column(JSON)
    confidence = Column(Float)
    
    # Validation
    approved = Column(Boolean)
    approval_by = Column(String(100))
    approval_notes = Column(Text)
    
    # Performance
    execution_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    cost = Column(Float)
    
    # Session linkage
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id'))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="ai_decisions")
    
    # Indexes
    __table_args__ = (
        Index('idx_decision_type', 'decision_type'),
        Index('idx_decision_persona', 'persona'),
        Index('idx_decision_session', 'session_id'),
    )
    
    def to_dict(self) -> Dict:
        return {
            'id': str(self.id),
            'decision_type': self.decision_type,
            'persona': self.persona,
            'task': self.task,
            'confidence': self.confidence,
            'approved': self.approved,
            'execution_time_ms': self.execution_time_ms
        }


class AuditLog(Base):
    """Audit logging model"""
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event info
    event_type = Column(String(50), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(String(100))
    
    # Action details
    action = Column(String(100))
    actor = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Data
    before_state = Column(JSON)
    after_state = Column(JSON)
    metadata = Column(JSON)
    
    # Linkages
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id'))
    rule_id = Column(UUID(as_uuid=True), ForeignKey('rules.id'))
    
    # Timestamp
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="audit_logs")
    rule = relationship("Rule", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_event', 'event_type'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_actor', 'actor'),
        Index('idx_audit_created', 'created_at'),
    )
    
    def to_dict(self) -> Dict:
        return {
            'id': str(self.id),
            'event_type': self.event_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action': self.action,
            'actor': self.actor,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PracticeApplication(Base):
    """Track practice applications"""
    __tablename__ = 'practice_applications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey('practices.id'))
    project_id = Column(String(100))
    
    # Application details
    context = Column(JSON)
    effectiveness_rating = Column(Integer)  # 1-5 scale
    notes = Column(Text)
    
    # Timestamp
    applied_at = Column(DateTime, default=func.now())
    
    # Relationships
    practice = relationship("Practice", back_populates="applications")


class TemplateUsage(Base):
    """Track template usage"""
    __tablename__ = 'template_usage'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey('templates.id'))
    
    # Usage details
    used_by = Column(String(100))
    variable_values = Column(JSON)
    output_generated = Column(Text)
    success = Column(Boolean)
    feedback = Column(Text)
    
    # Timestamp
    used_at = Column(DateTime, default=func.now())
    
    # Relationships
    template = relationship("Template", back_populates="usage_logs")


class Tag(Base):
    """Tags for categorization"""
    __tablename__ = 'tags'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    category = Column(String(50))
    
    # Relationships
    rules = relationship("Rule", secondary=rule_tags, back_populates="tags")


class TemplateVariable(Base):
    """Template variable definitions"""
    __tablename__ = 'template_variables'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    type = Column(String(50))  # string, number, boolean, array, object
    required = Column(Boolean, default=True)
    default_value = Column(Text)
    validation_regex = Column(Text)
    description = Column(Text)
    options = Column(JSON)  # For enum-like variables