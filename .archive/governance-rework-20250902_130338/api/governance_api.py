#!/usr/bin/env python3
"""
Governance API Server
RESTful API for governance system integration

@author Dr. Sarah Chen v1.2 - Backend Systems & Governance Architecture
@architecture RESTful API with FastAPI for governance system access
@business_logic Provides governance validation, monitoring, and reporting endpoints
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import asyncio
import sys

# Add governance to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from governance.core.enhanced_governance_engine import (
    MagicVariableDetector,
    TestExecutionTracker,
    BoilerplateDetector
)
from governance.validators.domain_validators import (
    DatabaseValidator,
    CacheValidator,
    FrontendValidator,
    APIValidator,
    SecurityValidator
)
from governance.core.governance_monitor import GovernanceMonitor
from governance.scripts.integrated_pre_commit_hook import IntegratedGovernanceHook

# Initialize FastAPI app
app = FastAPI(
    title="Governance API",
    description="AI Governance System API for external integration",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
monitor = GovernanceMonitor()
magic_detector = MagicVariableDetector()
test_tracker = TestExecutionTracker()
boilerplate_detector = BoilerplateDetector()

# Domain validators
validators = {
    'database': DatabaseValidator(),
    'cache': CacheValidator(),
    'frontend': FrontendValidator(),
    'api': APIValidator(),
    'security': SecurityValidator()
}

# Request/Response models
class CodeCheckRequest(BaseModel):
    code: str
    filename: str
    language: str = "python"
    check_types: List[str] = ["all"]

class FileCheckRequest(BaseModel):
    file_path: str
    check_types: List[str] = ["all"]

class ValidationResponse(BaseModel):
    valid: bool
    issues: List[Dict[str, Any]]
    severity_counts: Dict[str, int]
    recommendations: List[str]
    metadata: Dict[str, Any]

class MetricsResponse(BaseModel):
    timestamp: str
    events_total: int
    violations_by_severity: Dict[str, int]
    test_status: Dict[str, Any]
    governance_health: int

class WebhookConfig(BaseModel):
    url: str
    events: List[str]
    secret: Optional[str] = None
    active: bool = True

# Webhook storage (in production, use database)
webhooks: List[WebhookConfig] = []

# API Endpoints

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "Governance API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "check_code": "/api/v1/check/code",
            "check_file": "/api/v1/check/file",
            "metrics": "/api/v1/metrics",
            "events": "/api/v1/events",
            "webhooks": "/api/v1/webhooks"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "active",
            "validators": "active",
            "monitor": "active"
        }
    }

@app.post("/api/v1/check/code", response_model=ValidationResponse)
async def check_code(request: CodeCheckRequest):
    """Check code snippet for governance violations"""
    issues = []
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    recommendations = []
    
    try:
        # Magic variable detection
        if "all" in request.check_types or "magic" in request.check_types:
            magic_issues = magic_detector.detect(request.code, request.filename)
            for issue in magic_issues:
                issues.append({
                    "type": "magic_variable",
                    "severity": issue.get("severity", "medium"),
                    "line": issue.get("line"),
                    "message": issue.get("message"),
                    "suggestion": issue.get("suggestion")
                })
        
        # Boilerplate detection
        if "all" in request.check_types or "boilerplate" in request.check_types:
            bp_issues = boilerplate_detector.detect_boilerplate(request.code, request.filename)
            for issue in bp_issues:
                issues.append({
                    "type": "boilerplate",
                    "severity": issue.get("severity", "low"),
                    "pattern": issue.get("pattern"),
                    "message": issue.get("message")
                })
        
        # Domain-specific validation
        for validator_name, validator in validators.items():
            if "all" in request.check_types or validator_name in request.check_types:
                result = validator.validate(request.code, request.filename)
                if hasattr(result, 'issues'):
                    issues.extend(result.issues)
        
        # Count severities
        for issue in issues:
            severity = issue.get("severity", "medium").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Generate recommendations
        if severity_counts["critical"] > 0:
            recommendations.append("Critical issues found - must be fixed before commit")
        if severity_counts["high"] > 2:
            recommendations.append("Multiple high-severity issues - consider code review")
        if len(issues) > 10:
            recommendations.append("Many issues detected - consider refactoring")
        
        # Record event
        monitor.record_event(
            event_type="api_check",
            severity="INFO",
            file_path=request.filename,
            message=f"API check: {len(issues)} issues found"
        )
        
        return ValidationResponse(
            valid=len(issues) == 0,
            issues=issues,
            severity_counts=severity_counts,
            recommendations=recommendations,
            metadata={
                "filename": request.filename,
                "language": request.language,
                "checked_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/check/file", response_model=ValidationResponse)
async def check_file(request: FileCheckRequest):
    """Check a file for governance violations"""
    file_path = Path(request.file_path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Use code check with file content
        code_request = CodeCheckRequest(
            code=code,
            filename=str(file_path),
            language=file_path.suffix.lstrip('.'),
            check_types=request.check_types
        )
        
        return await check_code(code_request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/metrics", response_model=MetricsResponse)
async def get_metrics(hours: int = 24):
    """Get governance metrics"""
    try:
        # Get recent events
        events = monitor.get_recent_events(hours)
        
        # Count violations by severity
        violations = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for event in events:
            if "violation" in event.get("event_type", ""):
                severity = event.get("severity", "medium").lower()
                if severity in violations:
                    violations[severity] += 1
        
        # Get test status
        test_status = test_tracker.get_test_status()
        
        # Calculate health score
        health_score = 100
        if violations["critical"] > 0:
            health_score -= 30
        if violations["high"] > 5:
            health_score -= 20
        if test_status.get("hours_since_last_run", 999) > 168:
            health_score -= 10
        
        return MetricsResponse(
            timestamp=datetime.now().isoformat(),
            events_total=len(events),
            violations_by_severity=violations,
            test_status=test_status,
            governance_health=max(0, health_score)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/events")
async def get_events(
    limit: int = 100,
    hours: int = 24,
    severity: Optional[str] = None,
    event_type: Optional[str] = None
):
    """Get recent governance events"""
    try:
        events = monitor.get_recent_events(hours)
        
        # Filter by severity if specified
        if severity:
            events = [e for e in events if e.get("severity", "").lower() == severity.lower()]
        
        # Filter by event type if specified
        if event_type:
            events = [e for e in events if event_type in e.get("event_type", "")]
        
        # Limit results
        events = events[:limit]
        
        return {
            "count": len(events),
            "events": events,
            "filters": {
                "hours": hours,
                "severity": severity,
                "event_type": event_type,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/webhooks")
async def register_webhook(config: WebhookConfig):
    """Register a webhook for governance events"""
    webhooks.append(config)
    return {
        "status": "registered",
        "webhook_id": len(webhooks) - 1,
        "config": config
    }

@app.get("/api/v1/webhooks")
async def list_webhooks():
    """List registered webhooks"""
    return {
        "count": len(webhooks),
        "webhooks": [
            {
                "id": i,
                "url": w.url,
                "events": w.events,
                "active": w.active
            }
            for i, w in enumerate(webhooks)
        ]
    }

@app.delete("/api/v1/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: int):
    """Delete a webhook"""
    if webhook_id >= len(webhooks):
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    del webhooks[webhook_id]
    return {"status": "deleted", "webhook_id": webhook_id}

@app.get("/api/v1/stream/events")
async def stream_events():
    """Stream governance events via Server-Sent Events"""
    async def event_generator():
        last_check = datetime.now()
        
        while True:
            # Check for new events
            events = monitor.get_recent_events(0.01)  # Last 36 seconds
            new_events = [
                e for e in events 
                if datetime.fromisoformat(e["timestamp"]) > last_check
            ]
            
            if new_events:
                for event in new_events:
                    yield f"data: {json.dumps(event)}\n\n"
                last_check = datetime.now()
            
            await asyncio.sleep(1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@app.post("/api/v1/record/event")
async def record_event(
    event_type: str,
    severity: str,
    file_path: str,
    message: str,
    metadata: Optional[Dict] = None
):
    """Record a governance event"""
    try:
        monitor.record_event(
            event_type=event_type,
            severity=severity,
            file_path=file_path,
            message=message,
            metadata=metadata or {}
        )
        
        # Trigger webhooks
        await trigger_webhooks(event_type, {
            "event_type": event_type,
            "severity": severity,
            "file_path": file_path,
            "message": message,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"status": "recorded", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def trigger_webhooks(event_type: str, event_data: Dict):
    """Trigger registered webhooks for an event"""
    import aiohttp
    
    for webhook in webhooks:
        if not webhook.active:
            continue
        
        if "all" in webhook.events or event_type in webhook.events:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {}
                    if webhook.secret:
                        # Add webhook signature
                        import hmac
                        import hashlib
                        signature = hmac.new(
                            webhook.secret.encode(),
                            json.dumps(event_data).encode(),
                            hashlib.sha256
                        ).hexdigest()
                        headers["X-Governance-Signature"] = signature
                    
                    async with session.post(
                        webhook.url,
                        json=event_data,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        pass  # Fire and forget
            except:
                pass  # Don't let webhook failures affect the system

@app.get("/api/v1/report/{report_type}")
async def get_report(report_type: str):
    """Get governance report"""
    from governance.core.governance_reporter import GovernanceReporter
    
    if report_type not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    try:
        reporter = GovernanceReporter()
        
        if report_type == "daily":
            report = reporter.generate_daily_report()
        elif report_type == "weekly":
            report = reporter.generate_weekly_report()
        else:
            report = reporter.generate_monthly_report()
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/config/phase")
async def get_governance_phase():
    """Get current governance phase"""
    import os
    phase = int(os.environ.get('GOVERNANCE_PHASE', '2'))
    
    phase_names = {
        1: "Learning",
        2: "Advisory",
        3: "Enforcement",
        4: "Mature"
    }
    
    return {
        "phase": phase,
        "name": phase_names.get(phase, "Unknown"),
        "description": get_phase_description(phase)
    }

def get_phase_description(phase: int) -> str:
    """Get description for governance phase"""
    descriptions = {
        1: "Gathering data with minimal enforcement",
        2: "Providing warnings but allowing commits",
        3: "Strict enforcement with flexibility",
        4: "Full enforcement with intelligent exemptions"
    }
    return descriptions.get(phase, "Unknown phase")

@app.post("/api/v1/config/phase")
async def set_governance_phase(phase: int):
    """Set governance phase"""
    if phase not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Invalid phase")
    
    import os
    os.environ['GOVERNANCE_PHASE'] = str(phase)
    
    # Record phase change
    monitor.record_event(
        event_type="phase_change",
        severity="INFO",
        file_path="",
        message=f"Governance phase changed to {phase}",
        metadata={"old_phase": 2, "new_phase": phase}
    )
    
    return await get_governance_phase()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize API on startup"""
    print("Governance API starting...")
    print(f"API available at: http://localhost:8001")
    print(f"Documentation at: http://localhost:8001/docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Governance API shutting down...")

# Run the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)