"""
@fileoverview Practices API endpoints
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - API Layer
@business_logic CRUD operations for best practices
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from database.database import get_db
from database.models import Practice, PracticeApplication as PracticeAppModel, AuditLog
from schemas.practices import (
    PracticeCreate, PracticeUpdate, PracticeResponse,
    PracticeListResponse, PracticeVote, PracticeApplication
)
from core.auth import get_current_user

router = APIRouter(prefix="/api/practices", tags=["practices"])

@router.get("/", response_model=PracticeListResponse)
async def list_practices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    min_effectiveness: Optional[float] = Query(None, ge=0, le=1),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all practices with filtering and pagination"""
    query = db.query(Practice)
    
    if category:
        query = query.filter(Practice.category == category)
    if min_effectiveness is not None:
        query = query.filter(Practice.effectiveness_score >= min_effectiveness)
    
    # Order by effectiveness score descending
    query = query.order_by(Practice.effectiveness_score.desc().nullslast())
    
    total = query.count()
    practices = query.offset(skip).limit(limit).all()
    
    return PracticeListResponse(
        practices=[PracticeResponse.from_orm(p) for p in practices],
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{practice_id}", response_model=PracticeResponse)
async def get_practice(
    practice_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific practice by ID"""
    practice = db.query(Practice).filter(Practice.id == practice_id).first()
    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found")
    
    return PracticeResponse.from_orm(practice)

@router.post("/", response_model=PracticeResponse)
async def create_practice(
    practice: PracticeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new best practice"""
    db_practice = Practice(
        **practice.dict(),
        author=current_user.get("name", "system"),
        effectiveness_score=0.5  # Start with neutral score
    )
    
    try:
        db.add(db_practice)
        db.commit()
        db.refresh(db_practice)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Practice creation failed")
    
    # Log creation
    audit = AuditLog(
        event_type="practice_created",
        entity_type="practice",
        entity_id=str(db_practice.id),
        action="create",
        actor=current_user.get("name", "system"),
        after_state=db_practice.to_dict()
    )
    db.add(audit)
    db.commit()
    
    return PracticeResponse.from_orm(db_practice)

@router.put("/{practice_id}", response_model=PracticeResponse)
async def update_practice(
    practice_id: UUID,
    practice_update: PracticeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing practice"""
    practice = db.query(Practice).filter(Practice.id == practice_id).first()
    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found")
    
    # Store previous state
    before_state = practice.to_dict()
    
    # Update fields
    update_data = practice_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(practice, field, value)
    
    try:
        db.commit()
        db.refresh(practice)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Practice update failed")
    
    # Log update
    audit = AuditLog(
        event_type="practice_updated",
        entity_type="practice",
        entity_id=str(practice_id),
        action="update",
        actor=current_user.get("name", "system"),
        before_state=before_state,
        after_state=practice.to_dict()
    )
    db.add(audit)
    db.commit()
    
    return PracticeResponse.from_orm(practice)

@router.delete("/{practice_id}")
async def delete_practice(
    practice_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a practice"""
    practice = db.query(Practice).filter(Practice.id == practice_id).first()
    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found")
    
    # Store state for audit
    before_state = practice.to_dict()
    
    # Hard delete for practices (unlike rules which are soft deleted)
    db.delete(practice)
    db.commit()
    
    # Log deletion
    audit = AuditLog(
        event_type="practice_deleted",
        entity_type="practice",
        entity_id=str(practice_id),
        action="delete",
        actor=current_user.get("name", "system"),
        before_state=before_state
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Practice deleted successfully", "id": str(practice_id)}

@router.post("/{practice_id}/vote")
async def vote_practice(
    practice_id: UUID,
    vote: PracticeVote,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Vote on a practice's effectiveness"""
    practice = db.query(Practice).filter(Practice.id == practice_id).first()
    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found")
    
    # Update vote counts
    if vote.vote_type == "up":
        practice.votes_up = (practice.votes_up or 0) + 1
    else:
        practice.votes_down = (practice.votes_down or 0) + 1
    
    # Recalculate effectiveness
    practice.effectiveness_score = practice.calculate_effectiveness()
    
    db.commit()
    
    # Log vote
    audit = AuditLog(
        event_type="practice_voted",
        entity_type="practice",
        entity_id=str(practice_id),
        action="vote",
        actor=current_user.get("name", "system"),
        metadata={"vote_type": vote.vote_type, "comment": vote.comment}
    )
    db.add(audit)
    db.commit()
    
    return {
        "message": "Vote recorded",
        "effectiveness_score": practice.effectiveness_score,
        "votes_up": practice.votes_up,
        "votes_down": practice.votes_down
    }

@router.post("/{practice_id}/apply")
async def apply_practice(
    practice_id: UUID,
    application: PracticeApplication,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Record an application of a practice"""
    practice = db.query(Practice).filter(Practice.id == practice_id).first()
    if not practice:
        raise HTTPException(status_code=404, detail="Practice not found")
    
    # Create application record
    db_application = PracticeAppModel(
        practice_id=practice_id,
        **application.dict()
    )
    
    db.add(db_application)
    
    # Update adoption rate (simplified calculation for Phase 1)
    total_applications = db.query(PracticeAppModel).filter(
        PracticeAppModel.practice_id == practice_id
    ).count() + 1
    
    # Calculate average effectiveness from applications
    applications = db.query(PracticeAppModel).filter(
        PracticeAppModel.practice_id == practice_id
    ).all()
    
    if applications:
        avg_rating = sum(a.effectiveness_rating for a in applications) / len(applications)
        practice.adoption_rate = min(1.0, total_applications / 10)  # Simple adoption metric
    
    db.commit()
    
    return {
        "message": "Practice application recorded",
        "application_id": str(db_application.id),
        "total_applications": total_applications
    }