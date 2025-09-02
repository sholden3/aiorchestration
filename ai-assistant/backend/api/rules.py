"""
@fileoverview Rules API endpoints
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Backend - API Layer
@business_logic CRUD operations for governance rules
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from database.database import get_db
from database.models import Rule, RuleSeverity, RuleStatus, AuditLog
from schemas.rules import (
    RuleCreate, RuleUpdate, RuleResponse, 
    RuleListResponse, RuleStats
)
from core.governance import validate_rule_condition, evaluate_rule_condition
from core.auth import get_current_user

router = APIRouter(prefix="/api/rules", tags=["rules"])

@router.get("/", response_model=RuleListResponse)
async def list_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[RuleStatus] = None,
    severity: Optional[RuleSeverity] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all rules with filtering and pagination"""
    query = db.query(Rule)
    
    if status:
        query = query.filter(Rule.status == status)
    if severity:
        query = query.filter(Rule.severity == severity)
    if category:
        query = query.filter(Rule.category == category)
    
    total = query.count()
    rules = query.offset(skip).limit(limit).all()
    
    # Log access
    audit = AuditLog(
        event_type="rules_listed",
        entity_type="rule",
        action="list",
        actor=current_user.get("name", "system"),
        metadata={"count": len(rules), "filters": {
            "status": status, "severity": severity, "category": category
        }}
    )
    db.add(audit)
    db.commit()
    
    return RuleListResponse(
        rules=[RuleResponse.model_validate(rule) for rule in rules],
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/stats", response_model=RuleStats)
async def get_rule_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get rule statistics"""
    total_rules = db.query(Rule).count()
    active_rules = db.query(Rule).filter(Rule.status == RuleStatus.ACTIVE).count()
    
    # Calculate effectiveness
    rules = db.query(Rule).filter(Rule.enforcement_count > 0).all()
    avg_effectiveness = 0
    if rules:
        effectiveness_scores = [
            (r.enforcement_count - r.violation_count) / r.enforcement_count 
            for r in rules if r.enforcement_count > 0
        ]
        avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0
    
    # Count by severity
    severity_counts = {}
    for severity in RuleSeverity:
        count = db.query(Rule).filter(Rule.severity == severity.value).count()
        severity_counts[severity.value] = count
    
    return RuleStats(
        total_rules=total_rules,
        active_rules=active_rules,
        average_effectiveness=avg_effectiveness,
        severity_distribution=severity_counts,
        last_updated=datetime.utcnow()
    )

@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific rule by ID"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Log access
    audit = AuditLog(
        event_type="rule_accessed",
        entity_type="rule",
        entity_id=str(rule_id),
        action="read",
        actor=current_user.get("name", "system")
    )
    db.add(audit)
    db.commit()
    
    return RuleResponse.model_validate(rule)

@router.post("/", response_model=RuleResponse)
async def create_rule(
    rule: RuleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new rule"""
    # Validate rule condition
    is_valid, error = validate_rule_condition(rule.condition)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid rule condition: {error}")
    
    db_rule = Rule(
        **rule.model_dump(),
        author=current_user.get("name", "system"),
        version=1
    )
    
    try:
        db.add(db_rule)
        db.commit()
        db.refresh(db_rule)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Rule with this name already exists")
    
    # Log creation
    audit = AuditLog(
        event_type="rule_created",
        entity_type="rule",
        entity_id=str(db_rule.id),
        action="create",
        actor=current_user.get("name", "system"),
        after_state=db_rule.to_dict()
    )
    db.add(audit)
    db.commit()
    
    return RuleResponse.model_validate(db_rule)

@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: UUID,
    rule_update: RuleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing rule"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Store previous state for audit
    before_state = rule.to_dict()
    
    # Validate new condition if provided
    if rule_update.condition:
        is_valid, error = validate_rule_condition(rule_update.condition)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid rule condition: {error}")
    
    # Update fields
    update_data = rule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    # Increment version
    rule.version = (rule.version or 1) + 1
    
    try:
        db.commit()
        db.refresh(rule)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Rule with this name already exists")
    
    # Log update
    audit = AuditLog(
        event_type="rule_updated",
        entity_type="rule",
        entity_id=str(rule_id),
        action="update",
        actor=current_user.get("name", "system"),
        before_state=before_state,
        after_state=rule.to_dict()
    )
    db.add(audit)
    db.commit()
    
    return RuleResponse.model_validate(rule)

@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a rule (soft delete by setting status to deprecated)"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Store previous state for audit
    before_state = rule.to_dict()
    
    # Soft delete by setting status
    rule.status = RuleStatus.DEPRECATED
    db.commit()
    
    # Log deletion
    audit = AuditLog(
        event_type="rule_deleted",
        entity_type="rule",
        entity_id=str(rule_id),
        action="delete",
        actor=current_user.get("name", "system"),
        before_state=before_state,
        after_state={"status": "deprecated"}
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Rule deleted successfully", "id": str(rule_id)}

@router.post("/{rule_id}/enforce")
async def enforce_rule(
    rule_id: UUID,
    context: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Enforce a rule against given context"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    if rule.status != RuleStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Rule is not active")
    
    # Evaluate the rule condition
    passed, message = evaluate_rule_condition(rule.condition, context)
    
    # Build enforcement result
    enforcement_result = {
        "rule_id": str(rule_id),
        "rule_name": rule.name,
        "passed": passed,
        "severity": rule.severity,
        "message": message or f"Rule {rule.name} {'passed' if passed else 'failed'}",
        "action": rule.action if not passed else None,
        "context": context
    }
    
    # Update enforcement count
    rule.enforcement_count = (rule.enforcement_count or 0) + 1
    if not passed:
        rule.violation_count = (rule.violation_count or 0) + 1
    
    # Calculate new effectiveness score
    if rule.enforcement_count > 0:
        rule.effectiveness_score = (rule.enforcement_count - rule.violation_count) / rule.enforcement_count
    
    db.commit()
    
    # Log enforcement
    audit = AuditLog(
        event_type="rule_enforced",
        entity_type="rule",
        entity_id=str(rule_id),
        action="enforce",
        actor=current_user.get("name", "system"),
        metadata=enforcement_result
    )
    db.add(audit)
    db.commit()
    
    return enforcement_result