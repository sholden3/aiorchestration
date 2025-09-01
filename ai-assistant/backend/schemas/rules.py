"""
@fileoverview Rule schemas for API
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - API Layer
@business_logic Request/Response models for rules
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator

from database.models import RuleSeverity, RuleStatus

class RuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    severity: RuleSeverity = RuleSeverity.INFO
    status: RuleStatus = RuleStatus.DRAFT
    condition: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    parameters: Optional[Dict[str, Any]] = None

class RuleCreate(RuleBase):
    pass

class RuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    severity: Optional[RuleSeverity] = None
    status: Optional[RuleStatus] = None
    condition: Optional[str] = Field(None, min_length=1)
    action: Optional[str] = Field(None, min_length=1)
    parameters: Optional[Dict[str, Any]] = None

class RuleResponse(RuleBase):
    id: UUID
    author: Optional[str] = None
    version: int = 1
    parent_id: Optional[UUID] = None
    enforcement_count: int = 0
    violation_count: int = 0
    effectiveness_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class RuleListResponse(BaseModel):
    rules: List[RuleResponse]
    total: int
    skip: int
    limit: int

class RuleStats(BaseModel):
    total_rules: int
    active_rules: int
    average_effectiveness: float
    severity_distribution: Dict[str, int]
    last_updated: datetime