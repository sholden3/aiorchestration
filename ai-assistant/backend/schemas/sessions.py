"""
@fileoverview Session schemas for API
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - API Layer
@business_logic Request/Response models for sessions
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from database.models import SessionStatus

class SessionBase(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100)
    architects: List[str] = Field(..., min_items=1)
    status: SessionStatus = SessionStatus.ACTIVE
    environment: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    architects: Optional[List[str]] = None
    status: Optional[SessionStatus] = None
    environment: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    id: UUID
    session_id: str
    architects: List[str]
    status: SessionStatus
    environment: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
    total: int
    skip: int
    limit: int

class SessionEnd(BaseModel):
    end_time: Optional[datetime] = None
    metrics: Optional[Dict[str, Any]] = {}
    summary: Optional[str] = None

class SessionMetrics(BaseModel):
    total_sessions: int
    active_sessions: int
    average_duration_minutes: float
    total_decisions: int
    total_audit_logs: int
    sessions_by_status: Dict[str, int]