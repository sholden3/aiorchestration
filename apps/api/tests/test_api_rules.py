"""
@fileoverview API tests for Rules endpoints
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Testing - API Layer
@business_logic Validate CRUD operations for rules
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import Base
from libs.shared_types.python import RuleSeverity, RuleStatus
from database.database import get_db
from main import AIBackendService

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Create test app
app = AIBackendService().app
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestRulesAPI:
    """Test Rules API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test database"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_create_rule(self):
        """Test creating a new rule"""
        rule_data = {
            "name": "test_rule",
            "description": "Test rule description",
            "category": "testing",
            "severity": "warning",
            "status": "active",
            "condition": '{"key": "value"}',
            "action": "block",
            "parameters": {"threshold": 10}
        }
        
        response = client.post("/api/rules/", json=rule_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "test_rule"
        assert data["severity"] == "warning"
        assert data["status"] == "active"
        assert "id" in data
    
    def test_get_rule(self):
        """Test getting a specific rule"""
        # Create a rule first
        rule_data = {
            "name": "get_test_rule",
            "condition": "test",
            "action": "test"
        }
        create_response = client.post("/api/rules/", json=rule_data)
        rule_id = create_response.json()["id"]
        
        # Get the rule
        response = client.get(f"/api/rules/{rule_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == rule_id
        assert data["name"] == "get_test_rule"
    
    def test_list_rules(self):
        """Test listing rules with pagination"""
        # Create multiple rules
        for i in range(5):
            rule_data = {
                "name": f"list_test_rule_{i}",
                "condition": "test",
                "action": "test",
                "severity": "info" if i % 2 == 0 else "warning"
            }
            client.post("/api/rules/", json=rule_data)
        
        # List all rules
        response = client.get("/api/rules/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 5
        assert len(data["rules"]) == 5
        
        # List with pagination
        response = client.get("/api/rules/?skip=2&limit=2")
        data = response.json()
        assert len(data["rules"]) == 2
        assert data["skip"] == 2
        assert data["limit"] == 2
        
        # List with filtering
        response = client.get("/api/rules/?severity=warning")
        data = response.json()
        assert data["total"] == 2  # Only warning severity rules
    
    def test_update_rule(self):
        """Test updating a rule"""
        # Create a rule
        rule_data = {
            "name": "update_test_rule",
            "condition": "test",
            "action": "test"
        }
        create_response = client.post("/api/rules/", json=rule_data)
        rule_id = create_response.json()["id"]
        
        # Update the rule
        update_data = {
            "description": "Updated description",
            "severity": "error",
            "status": "disabled"
        }
        response = client.put(f"/api/rules/{rule_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["severity"] == "error"
        assert data["status"] == "disabled"
        assert data["version"] == 2  # Version should increment
    
    def test_delete_rule(self):
        """Test deleting (soft delete) a rule"""
        # Create a rule
        rule_data = {
            "name": "delete_test_rule",
            "condition": "test",
            "action": "test"
        }
        create_response = client.post("/api/rules/", json=rule_data)
        rule_id = create_response.json()["id"]
        
        # Delete the rule
        response = client.delete(f"/api/rules/{rule_id}")
        assert response.status_code == 200
        
        # Check that it's soft deleted (status = deprecated)
        get_response = client.get(f"/api/rules/{rule_id}")
        assert get_response.json()["status"] == "deprecated"
    
    def test_enforce_rule(self):
        """Test enforcing a rule"""
        # Create an active rule
        rule_data = {
            "name": "enforce_test_rule",
            "condition": '{"status": "active"}',
            "action": "allow",
            "status": "active"
        }
        create_response = client.post("/api/rules/", json=rule_data)
        rule_id = create_response.json()["id"]
        
        # Enforce the rule with matching context
        context = {"status": "active"}
        response = client.post(f"/api/rules/{rule_id}/enforce", json=context)
        assert response.status_code == 200
        
        data = response.json()
        assert data["passed"] == True
        assert data["rule_name"] == "enforce_test_rule"
        
        # Enforce with non-matching context
        context = {"status": "inactive"}
        response = client.post(f"/api/rules/{rule_id}/enforce", json=context)
        data = response.json()
        assert data["passed"] == False
    
    def test_rule_stats(self):
        """Test getting rule statistics"""
        # Create some rules
        for i in range(3):
            rule_data = {
                "name": f"stats_test_rule_{i}",
                "condition": "test",
                "action": "test",
                "severity": ["info", "warning", "error"][i],
                "status": "active" if i < 2 else "draft"
            }
            client.post("/api/rules/", json=rule_data)
        
        response = client.get("/api/rules/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_rules"] == 3
        assert data["active_rules"] == 2
        assert "severity_distribution" in data
        assert data["severity_distribution"]["info"] == 1
        assert data["severity_distribution"]["warning"] == 1
        assert data["severity_distribution"]["error"] == 1
    
    def test_invalid_rule_condition(self):
        """Test creating rule with invalid condition"""
        rule_data = {
            "name": "invalid_rule",
            "condition": "invalid json {",
            "action": "test"
        }
        
        response = client.post("/api/rules/", json=rule_data)
        assert response.status_code == 400
        assert "Invalid rule condition" in response.json()["detail"]
    
    def test_duplicate_rule_name(self):
        """Test creating rule with duplicate name"""
        rule_data = {
            "name": "duplicate_rule",
            "condition": "test",
            "action": "test"
        }
        
        # Create first rule
        response1 = client.post("/api/rules/", json=rule_data)
        assert response1.status_code == 200
        
        # Try to create duplicate
        response2 = client.post("/api/rules/", json=rule_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]