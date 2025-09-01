"""
@fileoverview Templates API endpoints
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - API Layer
@business_logic CRUD operations for templates
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import json

from database.database import get_db
from database.models import Template, TemplateType, TemplateUsage as TemplateUsageModel, AuditLog
from schemas.templates import (
    TemplateCreate, TemplateUpdate, TemplateResponse,
    TemplateListResponse, TemplateRender, TemplateRenderResponse,
    TemplateUsage
)
from core.template_engine import render_template, validate_template_variables
from core.auth import get_current_user

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.get("/", response_model=TemplateListResponse)
async def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[TemplateType] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all templates with filtering and pagination"""
    query = db.query(Template)
    
    if type:
        query = query.filter(Template.type == type)
    if category:
        query = query.filter(Template.category == category)
    
    # Order by usage count descending
    query = query.order_by(Template.usage_count.desc())
    
    total = query.count()
    templates = query.offset(skip).limit(limit).all()
    
    return TemplateListResponse(
        templates=[TemplateResponse.model_validate(t) for t in templates],
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/types")
async def get_template_types():
    """Get all available template types"""
    return {
        "types": [
            {
                "value": t.value,
                "name": t.name,
                "description": f"Template for {t.value}"
            }
            for t in TemplateType
        ]
    }

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific template by ID"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return TemplateResponse.model_validate(template)

@router.post("/", response_model=TemplateResponse)
async def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new template"""
    # Convert variables dict to JSON string for storage
    template_dict = template.model_dump()
    if template_dict.get('variables'):
        template_dict['variables'] = json.dumps(template_dict['variables'])
    
    db_template = Template(
        **template_dict,
        author=current_user.get("name", "system"),
        version=1
    )
    
    try:
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Template creation failed")
    
    # Log creation
    audit = AuditLog(
        event_type="template_created",
        entity_type="template",
        entity_id=str(db_template.id),
        action="create",
        actor=current_user.get("name", "system"),
        after_state=db_template.to_dict()
    )
    db.add(audit)
    db.commit()
    
    return TemplateResponse.model_validate(db_template)

@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    template_update: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing template"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Store previous state
    before_state = template.to_dict()
    
    # Update fields
    update_data = template_update.model_dump(exclude_unset=True)
    
    # Convert variables dict to JSON string if provided
    if 'variables' in update_data and update_data['variables'] is not None:
        update_data['variables'] = json.dumps(update_data['variables'])
    
    for field, value in update_data.items():
        setattr(template, field, value)
    
    # Increment version
    template.version = (template.version or 1) + 1
    
    try:
        db.commit()
        db.refresh(template)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Template update failed")
    
    # Log update
    audit = AuditLog(
        event_type="template_updated",
        entity_type="template",
        entity_id=str(template_id),
        action="update",
        actor=current_user.get("name", "system"),
        before_state=before_state,
        after_state=template.to_dict()
    )
    db.add(audit)
    db.commit()
    
    return TemplateResponse.model_validate(template)

@router.delete("/{template_id}")
async def delete_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a template"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Store state for audit
    before_state = template.to_dict()
    
    # Hard delete
    db.delete(template)
    db.commit()
    
    # Log deletion
    audit = AuditLog(
        event_type="template_deleted",
        entity_type="template",
        entity_id=str(template_id),
        action="delete",
        actor=current_user.get("name", "system"),
        before_state=before_state
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Template deleted successfully", "id": str(template_id)}

@router.post("/{template_id}/render", response_model=TemplateRenderResponse)
async def render_template_endpoint(
    template_id: UUID,
    render_request: TemplateRender,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Render a template with provided variables"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Parse template variables if stored as JSON string
    template_vars = template.variables
    if isinstance(template_vars, str):
        try:
            template_vars = json.loads(template_vars)
        except json.JSONDecodeError:
            template_vars = {}
    
    # Validate variables
    is_valid, errors = validate_template_variables(
        template_vars,
        render_request.variables
    )
    
    if not is_valid:
        return TemplateRenderResponse(
            rendered_content="",
            validation_errors=errors,
            metadata={"template_id": str(template_id), "valid": False}
        )
    
    # Render the template
    try:
        rendered_content = render_template(
            template.template_content,
            render_request.variables
        )
    except Exception as e:
        return TemplateRenderResponse(
            rendered_content="",
            validation_errors=[f"Rendering error: {str(e)}"],
            metadata={"template_id": str(template_id), "valid": False}
        )
    
    # Update usage count
    template.usage_count = (template.usage_count or 0) + 1
    
    # Record usage
    usage = TemplateUsageModel(
        template_id=template_id,
        used_by=current_user.get("name", "system"),
        variable_values=render_request.variables,
        output_generated=rendered_content[:1000],  # Store first 1000 chars
        success=True
    )
    db.add(usage)
    db.commit()
    
    return TemplateRenderResponse(
        rendered_content=rendered_content,
        validation_errors=[],
        metadata={
            "template_id": str(template_id),
            "template_name": template.name,
            "template_type": template.type,
            "valid": True
        }
    )

@router.post("/{template_id}/clone", response_model=TemplateResponse)
async def clone_template(
    template_id: UUID,
    new_name: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Clone an existing template"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create new template as a copy
    new_template = Template(
        name=new_name,
        type=template.type,
        category=template.category,
        template_content=template.template_content,
        description=f"Cloned from: {template.name}",
        example_usage=template.example_usage,
        variables=template.variables,
        validation_rules=template.validation_rules,
        metadata=template.metadata,
        tags=template.tags,
        author=current_user.get("name", "system"),
        version=1,
        parent_id=template_id
    )
    
    try:
        db.add(new_template)
        db.commit()
        db.refresh(new_template)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Template clone failed")
    
    return TemplateResponse.model_validate(new_template)