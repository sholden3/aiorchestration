"""
@fileoverview Sessions API endpoints
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - API Layer
@business_logic CRUD operations for development sessions
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from database.database import get_db
from database.models import (
    Session as DBSession, SessionStatus, AuditLog, AIDecision
)
from schemas.sessions import (
    SessionCreate, SessionUpdate, SessionResponse,
    SessionListResponse, SessionEnd, SessionMetrics
)
from core.auth import get_current_user

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[SessionStatus] = None,
    architect: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all sessions with filtering and pagination"""
    query = db.query(DBSession)
    
    if status:
        query = query.filter(DBSession.status == status)
    
    # Filter by architect (check if architect is in the JSON array)
    if architect:
        query = query.filter(DBSession.architects.contains([architect]))
    
    # Order by start time descending (most recent first)
    query = query.order_by(DBSession.start_time.desc())
    
    total = query.count()
    sessions = query.offset(skip).limit(limit).all()
    
    return SessionListResponse(
        sessions=[SessionResponse.from_orm(s) for s in sessions],
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/active")
async def get_active_sessions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all currently active sessions"""
    active_sessions = db.query(DBSession).filter(
        DBSession.status == SessionStatus.ACTIVE
    ).all()
    
    return {
        "active_sessions": [SessionResponse.from_orm(s) for s in active_sessions],
        "count": len(active_sessions)
    }

@router.get("/metrics", response_model=SessionMetrics)
async def get_session_metrics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get session metrics and statistics"""
    total_sessions = db.query(DBSession).count()
    active_sessions = db.query(DBSession).filter(
        DBSession.status == SessionStatus.ACTIVE
    ).count()
    
    # Calculate average duration
    completed_sessions = db.query(DBSession).filter(
        DBSession.duration_minutes.isnot(None)
    ).all()
    
    avg_duration = 0
    if completed_sessions:
        total_duration = sum(s.duration_minutes for s in completed_sessions)
        avg_duration = total_duration / len(completed_sessions)
    
    # Count related entities
    total_decisions = db.query(AIDecision).count()
    total_audit_logs = db.query(AuditLog).count()
    
    # Sessions by status
    status_counts = {}
    for status in SessionStatus:
        count = db.query(DBSession).filter(DBSession.status == status.value).count()
        status_counts[status.value] = count
    
    return SessionMetrics(
        total_sessions=total_sessions,
        active_sessions=active_sessions,
        average_duration_minutes=avg_duration,
        total_decisions=total_decisions,
        total_audit_logs=total_audit_logs,
        sessions_by_status=status_counts
    )

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific session by ID"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse.from_orm(session)

@router.post("/", response_model=SessionResponse)
async def create_session(
    session: SessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new development session"""
    db_session = DBSession(
        **session.dict(),
        start_time=datetime.utcnow()
    )
    
    try:
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Session with this ID already exists"
        )
    
    # Log session creation
    audit = AuditLog(
        event_type="session_started",
        entity_type="session",
        entity_id=str(db_session.id),
        action="create",
        actor=current_user.get("name", "system"),
        session_id=db_session.id,
        after_state=db_session.to_dict()
    )
    db.add(audit)
    db.commit()
    
    return SessionResponse.from_orm(db_session)

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: UUID,
    session_update: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing session"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Store previous state
    before_state = session.to_dict()
    
    # Update fields
    update_data = session_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    try:
        db.commit()
        db.refresh(session)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Session update failed")
    
    # Log update
    audit = AuditLog(
        event_type="session_updated",
        entity_type="session",
        entity_id=str(session_id),
        action="update",
        actor=current_user.get("name", "system"),
        session_id=session_id,
        before_state=before_state,
        after_state=session.to_dict()
    )
    db.add(audit)
    db.commit()
    
    return SessionResponse.from_orm(session)

@router.post("/{session_id}/end", response_model=SessionResponse)
async def end_session(
    session_id: UUID,
    end_data: SessionEnd,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """End a development session"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != SessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Update session
    session.end_time = end_data.end_time or datetime.utcnow()
    session.status = SessionStatus.ENDED
    session.metrics = end_data.metrics
    
    # Calculate duration
    session.calculate_duration()
    
    db.commit()
    db.refresh(session)
    
    # Log session end
    audit = AuditLog(
        event_type="session_ended",
        entity_type="session",
        entity_id=str(session_id),
        action="end",
        actor=current_user.get("name", "system"),
        session_id=session_id,
        metadata={
            "duration_minutes": session.duration_minutes,
            "summary": end_data.summary
        }
    )
    db.add(audit)
    db.commit()
    
    return SessionResponse.from_orm(session)

@router.get("/{session_id}/audit-logs")
async def get_session_audit_logs(
    session_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all audit logs for a session"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    query = db.query(AuditLog).filter(AuditLog.session_id == session_id)
    query = query.order_by(AuditLog.created_at.desc())
    
    total = query.count()
    logs = query.offset(skip).limit(limit).all()
    
    return {
        "session_id": str(session_id),
        "logs": [log.to_dict() for log in logs],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{session_id}/decisions")
async def get_session_decisions(
    session_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all AI decisions for a session"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    query = db.query(AIDecision).filter(AIDecision.session_id == session_id)
    query = query.order_by(AIDecision.created_at.desc())
    
    total = query.count()
    decisions = query.offset(skip).limit(limit).all()
    
    return {
        "session_id": str(session_id),
        "decisions": [decision.to_dict() for decision in decisions],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.delete("/{session_id}")
async def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a session (soft delete by setting status)"""
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Soft delete by setting status to expired
    session.status = SessionStatus.EXPIRED
    db.commit()
    
    # Log deletion
    audit = AuditLog(
        event_type="session_deleted",
        entity_type="session",
        entity_id=str(session_id),
        action="delete",
        actor=current_user.get("name", "system"),
        session_id=session_id
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Session deleted successfully", "id": str(session_id)}