"""
@fileoverview Integration tests for APIs with governance
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Testing - Integration Layer
@business_logic Validate API operations with full system integration
"""

import pytest
from datetime import datetime
from uuid import uuid4

class TestRulesIntegration:
    """Integration tests for Rules API"""
    
    def test_create_rule_with_audit(self, client, sample_rule_data, test_session):
        """Test that creating a rule creates an audit log"""
        # Create rule
        response = client.post("/api/rules/", json=sample_rule_data)
        assert response.status_code == 200
        
        rule_data = response.json()
        assert rule_data["name"] == sample_rule_data["name"]
        
        # Check audit log was created
        from database.models import AuditLog
        audit = test_session.query(AuditLog).filter(
            AuditLog.event_type == "rule_created"
        ).first()
        
        assert audit is not None
        assert audit.entity_id == rule_data["id"]
        assert audit.action == "create"
    
    def test_rule_enforcement_updates_metrics(self, client, test_session):
        """Test that enforcing a rule updates enforcement metrics"""
        # Create active rule
        rule_data = {
            "name": "enforcement_test",
            "condition": '{"status": "active"}',
            "action": "allow",
            "status": "active"
        }
        create_response = client.post("/api/rules/", json=rule_data)
        rule_id = create_response.json()["id"]
        
        # Enforce rule multiple times
        for i in range(3):
            context = {"status": "active" if i < 2 else "inactive"}
            response = client.post(f"/api/rules/{rule_id}/enforce", json=context)
            assert response.status_code == 200
        
        # Check metrics updated
        from database.models import Rule
        from uuid import UUID
        rule = test_session.query(Rule).filter(Rule.id == UUID(rule_id)).first()
        
        assert rule.enforcement_count == 3
        assert rule.violation_count == 1  # One failed enforcement
        assert rule.effectiveness_score > 0
    
    def test_rule_soft_delete(self, client, sample_rule_data, test_session):
        """Test that deleting a rule performs soft delete"""
        # Create rule
        response = client.post("/api/rules/", json=sample_rule_data)
        rule_id = response.json()["id"]
        
        # Delete rule
        response = client.delete(f"/api/rules/{rule_id}")
        assert response.status_code == 200
        
        # Check rule still exists but is deprecated
        from database.models import Rule, RuleStatus
        from uuid import UUID
        rule = test_session.query(Rule).filter(Rule.id == UUID(rule_id)).first()
        
        assert rule is not None
        assert rule.status == RuleStatus.DEPRECATED

class TestPracticesIntegration:
    """Integration tests for Practices API"""
    
    def test_practice_voting_updates_effectiveness(self, client, sample_practice_data):
        """Test that voting updates practice effectiveness score"""
        # Create practice
        response = client.post("/api/practices/", json=sample_practice_data)
        practice_id = response.json()["id"]
        
        # Vote multiple times
        for vote_type in ["up", "up", "down", "up"]:
            vote_data = {"vote_type": vote_type}
            response = client.post(f"/api/practices/{practice_id}/vote", json=vote_data)
            assert response.status_code == 200
        
        # Check final score
        response = client.get(f"/api/practices/{practice_id}")
        practice = response.json()
        
        assert practice["votes_up"] == 3
        assert practice["votes_down"] == 1
        assert practice["effectiveness_score"] == 0.75  # 3/4
    
    def test_practice_application_tracking(self, client, sample_practice_data, test_session):
        """Test that practice applications are tracked"""
        # Create practice
        response = client.post("/api/practices/", json=sample_practice_data)
        practice_id = response.json()["id"]
        
        # Apply practice
        application_data = {
            "project_id": "test_project",
            "context": {"env": "production"},
            "effectiveness_rating": 4,
            "notes": "Worked well"
        }
        response = client.post(f"/api/practices/{practice_id}/apply", json=application_data)
        assert response.status_code == 200
        
        # Check application was recorded
        from database.models import PracticeApplication
        from uuid import UUID
        app = test_session.query(PracticeApplication).filter(
            PracticeApplication.practice_id == UUID(practice_id)
        ).first()
        
        assert app is not None
        assert app.project_id == "test_project"
        assert app.effectiveness_rating == 4

class TestTemplatesIntegration:
    """Integration tests for Templates API"""
    
    def test_template_rendering_with_validation(self, client, sample_template_data):
        """Test template rendering with variable validation"""
        # Create template
        response = client.post("/api/templates/", json=sample_template_data)
        template_id = response.json()["id"]
        
        # Render with valid variables
        render_data = {
            "variables": {
                "name": "Alice",
                "project": "Test Project"
            }
        }
        response = client.post(f"/api/templates/{template_id}/render", json=render_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "Hello Alice, welcome to Test Project!" in data["rendered_content"]
        assert len(data["validation_errors"]) == 0
        
        # Render with missing required variable
        render_data = {"variables": {"name": "Bob"}}
        response = client.post(f"/api/templates/{template_id}/render", json=render_data)
        
        data = response.json()
        assert len(data["validation_errors"]) > 0
        assert "Required variable 'project' is missing" in data["validation_errors"][0]
    
    def test_template_usage_tracking(self, client, sample_template_data, test_session):
        """Test that template usage is tracked"""
        # Create template
        response = client.post("/api/templates/", json=sample_template_data)
        template_id = response.json()["id"]
        
        # Use template
        render_data = {
            "variables": {
                "name": "Test",
                "project": "Project"
            }
        }
        client.post(f"/api/templates/{template_id}/render", json=render_data)
        
        # Check usage was tracked
        from database.models import Template, TemplateUsage
        from uuid import UUID
        
        template = test_session.query(Template).filter(
            Template.id == UUID(template_id)
        ).first()
        assert template.usage_count == 1
        
        usage = test_session.query(TemplateUsage).filter(
            TemplateUsage.template_id == UUID(template_id)
        ).first()
        assert usage is not None
        assert usage.success == True
    
    def test_template_cloning(self, client, sample_template_data):
        """Test template cloning creates proper parent relationship"""
        # Create original template
        response = client.post("/api/templates/", json=sample_template_data)
        original_id = response.json()["id"]
        
        # Clone template
        response = client.post(
            f"/api/templates/{original_id}/clone",
            params={"new_name": "Cloned Template"}
        )
        assert response.status_code == 200
        
        cloned = response.json()
        assert cloned["name"] == "Cloned Template"
        assert cloned["parent_id"] == original_id
        assert "Cloned from" in cloned["description"]

class TestSessionsIntegration:
    """Integration tests for Sessions API"""
    
    def test_session_duration_calculation(self, client, sample_session_data):
        """Test that session duration is calculated correctly"""
        # Create session
        response = client.post("/api/sessions/", json=sample_session_data)
        session_id = response.json()["id"]
        
        # End session
        end_data = {
            "metrics": {"tasks_completed": 5},
            "summary": "Test session completed"
        }
        response = client.post(f"/api/sessions/{session_id}/end", json=end_data)
        assert response.status_code == 200
        
        session = response.json()
        assert session["status"] == "ended"
        assert session["duration_minutes"] is not None
    
    def test_session_audit_trail(self, client, sample_session_data, test_session):
        """Test that sessions track all related audit logs"""
        # Create session
        response = client.post("/api/sessions/", json=sample_session_data)
        session_id = response.json()["id"]
        
        # Perform some actions that should create audit logs
        rule_data = {
            "name": f"session_rule_{uuid4().hex[:8]}",
            "condition": "test",
            "action": "test"
        }
        client.post("/api/rules/", json=rule_data)
        
        # Get session audit logs
        response = client.get(f"/api/sessions/{session_id}/audit-logs")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 1  # At least session creation log
    
    def test_session_metrics_aggregation(self, client):
        """Test session metrics endpoint"""
        # Create multiple sessions
        for i in range(3):
            session_data = {
                "session_id": f"test_session_{i}",
                "architects": ["Test User"],
                "status": "active" if i == 0 else "ended"
            }
            client.post("/api/sessions/", json=session_data)
        
        # Get metrics
        response = client.get("/api/sessions/metrics")
        assert response.status_code == 200
        
        metrics = response.json()
        assert metrics["total_sessions"] >= 3
        assert metrics["active_sessions"] >= 1

class TestCrossAPIIntegration:
    """Test interactions between different APIs"""
    
    def test_rule_stats_endpoint(self, client):
        """Test rule statistics aggregation"""
        # Create rules with different severities
        severities = ["info", "warning", "error", "critical"]
        for severity in severities:
            rule_data = {
                "name": f"stat_rule_{severity}",
                "condition": "test",
                "action": "test",
                "severity": severity,
                "status": "active"
            }
            client.post("/api/rules/", json=rule_data)
        
        # Get stats
        response = client.get("/api/rules/stats")
        assert response.status_code == 200
        
        stats = response.json()
        assert stats["total_rules"] >= 4
        assert stats["active_rules"] >= 4
        assert all(
            stats["severity_distribution"][sev] >= 1 
            for sev in severities
        )