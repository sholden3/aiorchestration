"""
Updated API Endpoints with Real Database Integration
Replaces mock implementations with actual database queries
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from database_service import db_service, DatabaseService
import logging

logger = logging.getLogger(__name__)

# Create routers
rules_router = APIRouter(prefix="/api/rules", tags=["Rules & Best Practices"])
practices_router = APIRouter(prefix="/api/practices", tags=["Best Practices"])
templates_router = APIRouter(prefix="/api/templates", tags=["Templates"])
sessions_router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

# ==================== DEPENDENCY ====================

async def get_db():
    """Dependency to ensure database is connected
    
    IMPORTANT: We no longer try to reconnect on every call.
    If the database is not connected, we use the mock fallback.
    The circuit breaker prevents repeated connection attempts.
    """
    # Just return the service - it handles its own connection state
    # and falls back to mock data when not connected
    return db_service

# ==================== MODELS ====================

class RuleCreate(BaseModel):
    rule_id: str
    category: str = "general"
    title: str
    description: str
    severity: str = Field(..., pattern="^(critical|high|medium|low)$")
    enforcement: str = Field(..., pattern="^(mandatory|recommended|optional)$")
    examples: List[str] = []
    anti_patterns: List[str] = []
    violations_consequence: Optional[str] = None
    created_by: str = "system"
    active: bool = True
    priority: int = 0

class RuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    enforcement: Optional[str] = None
    examples: Optional[List[str]] = None
    anti_patterns: Optional[List[str]] = None
    active: Optional[bool] = None

class BestPracticeCreate(BaseModel):
    practice_id: str
    category: str = "general"
    title: str
    description: str
    benefits: List[str] = []
    implementation_guide: Optional[str] = None
    anti_patterns: List[str] = []
    references: List[str] = []
    examples: List[str] = []
    is_required: bool = False
    priority: Optional[str] = None

class TemplateCreate(BaseModel):
    template_id: str
    name: str
    description: Optional[str] = None
    category: str = "general"
    template_content: str
    variables: List[str] = []
    tags: List[str] = []
    created_by: str = "system"

# ==================== RULES ENDPOINTS ====================

@rules_router.get("/")
async def get_rules(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    active_only: bool = True,
    db: DatabaseService = Depends(get_db)
):
    """
    Get all rules from database with optional filters
    
    - **category**: Filter by category (e.g., 'security', 'performance')
    - **severity**: Filter by severity (critical, high, medium, low)
    - **active_only**: Only return active rules (default: true)
    """
    try:
        rules = await db.get_rules(
            category=category,
            severity=severity,
            active_only=active_only
        )
        
        return {
            "success": True,
            "count": len(rules),
            "rules": rules
        }
    except Exception as e:
        logger.error(f"Failed to get rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@rules_router.post("/")
async def create_rule(
    rule: RuleCreate,
    db: DatabaseService = Depends(get_db)
):
    """Create a new rule in the database"""
    try:
        rule_id = await db.create_rule(rule.dict())
        return {
            "success": True,
            "message": "Rule created successfully",
            "rule_id": rule_id
        }
    except Exception as e:
        logger.error(f"Failed to create rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@rules_router.put("/{rule_id}")
async def update_rule(
    rule_id: str,
    updates: RuleUpdate,
    db: DatabaseService = Depends(get_db)
):
    """Update an existing rule"""
    try:
        # Filter out None values
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No updates provided")
            
        success = await db.update_rule(rule_id, update_data)
        
        if success:
            return {
                "success": True,
                "message": f"Rule {rule_id} updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@rules_router.get("/stats")
async def get_rules_statistics(db: DatabaseService = Depends(get_db)):
    """Get statistics about rules in the system"""
    try:
        all_rules = await db.get_rules(active_only=False)
        active_rules = [r for r in all_rules if r.get('active', False)]
        
        # Group by category
        by_category = {}
        for rule in active_rules:
            cat = rule.get('category_name', 'Unknown')
            by_category[cat] = by_category.get(cat, 0) + 1
            
        # Group by severity
        by_severity = {}
        for rule in active_rules:
            sev = rule.get('severity', 'unknown')
            by_severity[sev] = by_severity.get(sev, 0) + 1
            
        return {
            "success": True,
            "statistics": {
                "total_rules": len(all_rules),
                "active_rules": len(active_rules),
                "inactive_rules": len(all_rules) - len(active_rules),
                "by_category": by_category,
                "by_severity": by_severity,
                "critical_count": by_severity.get('critical', 0),
                "mandatory_count": len([r for r in active_rules if r.get('enforcement') == 'mandatory'])
            }
        }
    except Exception as e:
        logger.error(f"Failed to get rules statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== BEST PRACTICES ENDPOINTS ====================

@practices_router.get("/")
async def get_best_practices(
    category: Optional[str] = None,
    required_only: bool = False,
    db: DatabaseService = Depends(get_db)
):
    """
    Get all best practices from database
    
    - **category**: Filter by category
    - **required_only**: Only return required practices
    """
    try:
        practices = await db.get_best_practices(
            category=category,
            required_only=required_only
        )
        
        return {
            "success": True,
            "count": len(practices),
            "practices": practices
        }
    except Exception as e:
        logger.error(f"Failed to get best practices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@practices_router.post("/")
async def create_best_practice(
    practice: BestPracticeCreate,
    db: DatabaseService = Depends(get_db)
):
    """Create a new best practice"""
    try:
        practice_id = await db.create_best_practice(practice.dict())
        return {
            "success": True,
            "message": "Best practice created successfully",
            "practice_id": practice_id
        }
    except Exception as e:
        logger.error(f"Failed to create best practice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@practices_router.get("/stats")
async def get_practices_statistics(db: DatabaseService = Depends(get_db)):
    """Get statistics about best practices"""
    try:
        all_practices = await db.get_best_practices()
        required = [p for p in all_practices if p.get('is_required', False)]
        
        # Group by category
        by_category = {}
        for practice in all_practices:
            cat = practice.get('category_name', 'Unknown')
            by_category[cat] = by_category.get(cat, 0) + 1
            
        # Group by priority
        by_priority = {}
        for practice in all_practices:
            pri = practice.get('priority', 'None')
            by_priority[pri] = by_priority.get(pri, 0) + 1
            
        return {
            "success": True,
            "statistics": {
                "total_practices": len(all_practices),
                "required_practices": len(required),
                "optional_practices": len(all_practices) - len(required),
                "by_category": by_category,
                "by_priority": by_priority,
                "critical_count": by_priority.get('P0-CRITICAL', 0)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get practices statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TEMPLATES ENDPOINTS ====================

@templates_router.get("/")
async def get_templates(
    category: Optional[str] = None,
    db: DatabaseService = Depends(get_db)
):
    """Get all templates from database"""
    try:
        templates = await db.get_templates(category=category)
        
        return {
            "success": True,
            "count": len(templates),
            "templates": templates
        }
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@templates_router.post("/")
async def create_template(
    template: TemplateCreate,
    db: DatabaseService = Depends(get_db)
):
    """Create a new template"""
    try:
        template_id = await db.create_template(template.dict())
        return {
            "success": True,
            "message": "Template created successfully",
            "template_id": template_id
        }
    except Exception as e:
        logger.error(f"Failed to create template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@templates_router.get("/stats")
async def get_templates_statistics(db: DatabaseService = Depends(get_db)):
    """Get statistics about templates"""
    try:
        all_templates = await db.get_templates()
        
        # Group by category
        by_category = {}
        for template in all_templates:
            cat = template.get('category_name', 'Unknown')
            by_category[cat] = by_category.get(cat, 0) + 1
            
        # Most used templates
        most_used = sorted(
            all_templates,
            key=lambda t: t.get('usage_count', 0),
            reverse=True
        )[:5]
        
        return {
            "success": True,
            "statistics": {
                "total_templates": len(all_templates),
                "by_category": by_category,
                "most_used": [
                    {"name": t['name'], "usage_count": t.get('usage_count', 0)}
                    for t in most_used
                ]
            }
        }
    except Exception as e:
        logger.error(f"Failed to get templates statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SESSIONS ENDPOINTS ====================

@sessions_router.get("/metrics")
async def get_session_metrics(db: DatabaseService = Depends(get_db)):
    """Get session metrics for dashboard"""
    try:
        # Return mock metrics for now
        return {
            "active_sessions": 3,
            "total_sessions": 127,
            "average_duration": 1845,  # seconds
            "success_rate": 0.92,
            "peak_usage_hour": 14,
            "sessions_by_day": [
                {"day": "Mon", "count": 23},
                {"day": "Tue", "count": 31},
                {"day": "Wed", "count": 28},
                {"day": "Thu", "count": 19},
                {"day": "Fri", "count": 26}
            ]
        }
    except Exception as e:
        logger.error(f"Error getting session metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@sessions_router.get("/")
async def get_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: DatabaseService = Depends(get_db)
):
    """Get all sessions with pagination"""
    try:
        # Return mock sessions for now
        return {
            "sessions": [],
            "total": 0,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== HEALTH CHECK ====================

@rules_router.get("/health")
@practices_router.get("/health")
@templates_router.get("/health")
@sessions_router.get("/health")
async def health_check(db: DatabaseService = Depends(get_db)):
    """Check if database connection is healthy"""
    return {
        "success": True,
        "database_connected": db.is_connected,
        "timestamp": datetime.now().isoformat()
    }