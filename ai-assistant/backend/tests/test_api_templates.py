"""
@fileoverview API tests for Templates endpoints
@author Dr. Sarah Chen v1.0 - Backend/Systems Architect
@architecture Testing - API Layer
@business_logic Validate CRUD operations and rendering for templates
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import Base, TemplateType
from database.database import get_db
from main import AIBackendService

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api_templates.db"
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

class TestTemplatesAPI:
    """Test Templates API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test database"""
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)
    
    def test_create_template(self):
        """Test creating a new template"""
        template_data = {
            "name": "Test Template",
            "type": "code",
            "category": "testing",
            "template_content": "Hello {{name}}, welcome to {{project}}!",
            "description": "A test template",
            "variables": {
                "name": {"type": "string", "required": True},
                "project": {"type": "string", "required": True}
            }
        }
        
        response = client.post("/api/templates/", json=template_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Template"
        assert data["type"] == "code"
        assert "{{name}}" in data["template_content"]
        assert "variables" in data
    
    def test_render_template(self):
        """Test rendering a template with variables"""
        # Create a template
        template_data = {
            "name": "Render Test",
            "type": "documentation",
            "template_content": "# {{title}}\n\n{{#each items}}- {{this}}\n{{/each}}",
            "variables": {
                "title": {"type": "string", "required": True},
                "items": {"type": "array", "required": True}
            }
        }
        create_response = client.post("/api/templates/", json=template_data)
        template_id = create_response.json()["id"]
        
        # Render the template
        render_data = {
            "variables": {
                "title": "My List",
                "items": ["Item 1", "Item 2", "Item 3"]
            }
        }
        
        response = client.post(f"/api/templates/{template_id}/render", json=render_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "# My List" in data["rendered_content"]
        assert "- Item 1" in data["rendered_content"]
        assert "- Item 2" in data["rendered_content"]
        assert "- Item 3" in data["rendered_content"]
        assert len(data["validation_errors"]) == 0
    
    def test_render_template_missing_variables(self):
        """Test rendering template with missing required variables"""
        # Create a template
        template_data = {
            "name": "Validation Test",
            "type": "prompt",
            "template_content": "Hello {{name}}!",
            "variables": {
                "name": {"type": "string", "required": True}
            }
        }
        create_response = client.post("/api/templates/", json=template_data)
        template_id = create_response.json()["id"]
        
        # Try to render without required variable
        render_data = {"variables": {}}
        
        response = client.post(f"/api/templates/{template_id}/render", json=render_data)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["validation_errors"]) > 0
        assert "Required variable 'name' is missing" in data["validation_errors"][0]
    
    def test_list_templates_by_type(self):
        """Test listing templates filtered by type"""
        # Create templates of different types
        types = ["code", "documentation", "prompt"]
        for t in types:
            template_data = {
                "name": f"{t.capitalize()} Template",
                "type": t,
                "template_content": f"This is a {t} template"
            }
            client.post("/api/templates/", json=template_data)
        
        # List all templates
        response = client.get("/api/templates/")
        assert response.status_code == 200
        assert response.json()["total"] == 3
        
        # Filter by type
        response = client.get("/api/templates/?type=code")
        data = response.json()
        assert data["total"] == 1
        assert data["templates"][0]["type"] == "code"
    
    def test_clone_template(self):
        """Test cloning an existing template"""
        # Create original template
        template_data = {
            "name": "Original Template",
            "type": "code",
            "template_content": "Original content {{var}}",
            "variables": {"var": {"type": "string"}}
        }
        create_response = client.post("/api/templates/", json=template_data)
        template_id = create_response.json()["id"]
        
        # Clone the template
        response = client.post(f"/api/templates/{template_id}/clone?new_name=Cloned Template")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Cloned Template"
        assert data["parent_id"] == template_id
        assert data["template_content"] == "Original content {{var}}"
        assert "Cloned from" in data["description"]
    
    def test_update_template(self):
        """Test updating a template"""
        # Create a template
        template_data = {
            "name": "Update Test",
            "type": "documentation",
            "template_content": "Original"
        }
        create_response = client.post("/api/templates/", json=template_data)
        template_id = create_response.json()["id"]
        original_version = create_response.json()["version"]
        
        # Update the template
        update_data = {
            "template_content": "Updated content",
            "description": "Now with description",
            "tags": ["updated", "test"]
        }
        
        response = client.put(f"/api/templates/{template_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["template_content"] == "Updated content"
        assert data["description"] == "Now with description"
        assert data["version"] == original_version + 1
    
    def test_get_template_types(self):
        """Test getting available template types"""
        response = client.get("/api/templates/types")
        assert response.status_code == 200
        
        data = response.json()
        assert "types" in data
        
        # Check all enum types are present
        type_values = [t["value"] for t in data["types"]]
        assert "documentation" in type_values
        assert "code" in type_values
        assert "prompt" in type_values
        assert "persona" in type_values
        assert "workflow" in type_values
    
    def test_template_usage_tracking(self):
        """Test that template usage is tracked"""
        # Create a template
        template_data = {
            "name": "Usage Test",
            "type": "prompt",
            "template_content": "Test {{var}}"
        }
        create_response = client.post("/api/templates/", json=template_data)
        template_id = create_response.json()["id"]
        initial_count = create_response.json()["usage_count"]
        
        # Render the template
        render_data = {"variables": {"var": "value"}}
        client.post(f"/api/templates/{template_id}/render", json=render_data)
        
        # Check usage count increased
        response = client.get(f"/api/templates/{template_id}")
        assert response.json()["usage_count"] == initial_count + 1