"""
@fileoverview Practice schemas for API
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - API Layer
@business_logic Request/Response models for practices
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

class PracticeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    rationale: Optional[str] = None
    examples: Optional[List[str]] = []
    anti_patterns: Optional[List[str]] = []
    references: Optional[List[str]] = []
    score_weight: float = Field(1.0, ge=0.1, le=5.0)
    tags: Optional[List[str]] = []

class PracticeCreate(PracticeBase):
    pass

class PracticeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    rationale: Optional[str] = None
    examples: Optional[List[str]] = None
    anti_patterns: Optional[List[str]] = None
    references: Optional[List[str]] = None
    score_weight: Optional[float] = Field(None, ge=0.1, le=5.0)
    tags: Optional[List[str]] = None

class PracticeResponse(PracticeBase):
    id: UUID
    author: Optional[str] = None
    votes_up: int = 0
    votes_down: int = 0
    effectiveness_score: Optional[float] = None
    adoption_rate: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PracticeListResponse(BaseModel):
    practices: List[PracticeResponse]
    total: int
    skip: int
    limit: int

class PracticeVote(BaseModel):
    vote_type: str = Field(..., regex="^(up|down)$")
    comment: Optional[str] = None

class PracticeApplication(BaseModel):
    project_id: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = {}
    effectiveness_rating: int = Field(..., ge=1, le=5)
    notes: Optional[str] = None