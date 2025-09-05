"""
@fileoverview API tests for Practices endpoints
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Testing - API Layer
@business_logic Validate CRUD operations for practices
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import Base
from database.database import get_db
from main import AIBackendService

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api_practices.db"
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

class TestPracticesAPI:
    """Test Practices API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test database"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_create_practice(self):
        """Test creating a new practice"""
        practice_data = {
            "name": "Test Practice",
            "category": "testing",
            "description": "A test practice",
            "rationale": "Why this is important",
            "examples": ["Example 1", "Example 2"],
            "anti_patterns": ["Don't do this"],
            "score_weight": 1.5
        }
        
        response = client.post("/api/practices/", json=practice_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Practice"
        assert data["category"] == "testing"
        assert len(data["examples"]) == 2
        assert data["effectiveness_score"] == 0.5  # Initial score
    
    def test_list_practices(self):
        """Test listing practices"""
        # Create multiple practices
        for i in range(3):
            practice_data = {
                "name": f"Practice {i}",
                "category": "testing" if i < 2 else "development",
                "description": f"Practice {i} description"
            }
            client.post("/api/practices/", json=practice_data)
        
        # List all practices
        response = client.get("/api/practices/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 3
        assert len(data["practices"]) == 3
        
        # Filter by category
        response = client.get("/api/practices/?category=testing")
        data = response.json()
        assert data["total"] == 2
    
    def test_vote_practice(self):
        """Test voting on a practice"""
        # Create a practice
        practice_data = {
            "name": "Vote Test Practice",
            "category": "testing",
            "description": "Practice to test voting"
        }
        create_response = client.post("/api/practices/", json=practice_data)
        practice_id = create_response.json()["id"]
        
        # Vote up
        vote_data = {"vote_type": "up", "comment": "Great practice!"}
        response = client.post(f"/api/practices/{practice_id}/vote", json=vote_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["votes_up"] == 1
        assert data["votes_down"] == 0
        assert data["effectiveness_score"] == 1.0
        
        # Vote down
        vote_data = {"vote_type": "down", "comment": "Not helpful"}
        response = client.post(f"/api/practices/{practice_id}/vote", json=vote_data)
        
        data = response.json()
        assert data["votes_up"] == 1
        assert data["votes_down"] == 1
        assert data["effectiveness_score"] == 0.5
    
    def test_apply_practice(self):
        """Test recording practice application"""
        # Create a practice
        practice_data = {
            "name": "Application Test Practice",
            "category": "testing"
        }
        create_response = client.post("/api/practices/", json=practice_data)
        practice_id = create_response.json()["id"]
        
        # Apply the practice
        application_data = {
            "project_id": "project_123",
            "context": {"environment": "production"},
            "effectiveness_rating": 4,
            "notes": "Worked well in our project"
        }
        
        response = client.post(f"/api/practices/{practice_id}/apply", json=application_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "application_id" in data
        assert data["total_applications"] == 1
    
    def test_update_practice(self):
        """Test updating a practice"""
        # Create a practice
        practice_data = {
            "name": "Update Test Practice",
            "category": "testing"
        }
        create_response = client.post("/api/practices/", json=practice_data)
        practice_id = create_response.json()["id"]
        
        # Update the practice
        update_data = {
            "description": "Updated description",
            "rationale": "New rationale",
            "tags": ["test", "updated"]
        }
        
        response = client.put(f"/api/practices/{practice_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["rationale"] == "New rationale"
        assert data["tags"] == ["test", "updated"]
    
    def test_delete_practice(self):
        """Test deleting a practice"""
        # Create a practice
        practice_data = {
            "name": "Delete Test Practice",
            "category": "testing"
        }
        create_response = client.post("/api/practices/", json=practice_data)
        practice_id = create_response.json()["id"]
        
        # Delete the practice
        response = client.delete(f"/api/practices/{practice_id}")
        assert response.status_code == 200
        
        # Try to get deleted practice
        response = client.get(f"/api/practices/{practice_id}")
        assert response.status_code == 404