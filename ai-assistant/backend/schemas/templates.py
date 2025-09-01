"""
@fileoverview Template schemas for API
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - API Layer
@business_logic Request/Response models for templates
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator
import json

from database.models import TemplateType

class TemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    type: TemplateType
    category: Optional[str] = Field(None, max_length=100)
    template_content: str = Field(..., min_length=1)
    description: Optional[str] = None
    example_usage: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = {}
    validation_rules: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = []

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[TemplateType] = None
    category: Optional[str] = Field(None, max_length=100)
    template_content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    example_usage: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class TemplateResponse(BaseModel):
    id: UUID
    name: str
    type: TemplateType
    category: Optional[str] = None
    template_content: str
    description: Optional[str] = None
    example_usage: Optional[Dict[str, Any]] = None
    variables: Optional[Dict[str, Any]] = {}
    validation_rules: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = []
    author: Optional[str] = None
    version: int = 1
    parent_id: Optional[UUID] = None
    usage_count: int = 0
    success_rate: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    @validator('variables', pre=True)
    def parse_variables(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v or {}

class TemplateListResponse(BaseModel):
    templates: List[TemplateResponse]
    total: int
    skip: int
    limit: int

class TemplateRender(BaseModel):
    variables: Dict[str, Any] = Field(..., description="Variable values to substitute")

class TemplateRenderResponse(BaseModel):
    rendered_content: str
    validation_errors: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}

class TemplateUsage(BaseModel):
    variable_values: Dict[str, Any]
    output_generated: Optional[str] = None
    success: bool = True
    feedback: Optional[str] = None