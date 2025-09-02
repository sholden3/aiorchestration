# AI Assistant Backend

## Overview
FastAPI-based backend for the AI Development Assistant platform. Provides comprehensive APIs for governance rules, best practices, templates, and session management.

## Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --port 8000
```

### Access the API
- API Base URL: http://localhost:8000
- Swagger Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc

## API Usage Examples

### Rules Management
```python
import requests

# Create a new rule
rule = {
    "name": "Code Review Required",
    "description": "All code must be reviewed before merge",
    "category": "development",
    "severity": "WARNING",
    "status": "ACTIVE",
    "condition": "has_review == True",
    "action": "block_merge"
}
response = requests.post("http://localhost:8000/api/rules/", json=rule)
rule_id = response.json()["id"]

# Enforce the rule
context = {"has_review": False, "author": "developer1"}
response = requests.post(f"http://localhost:8000/api/rules/{rule_id}/enforce", json=context)
print(response.json())  # {"passed": false, "message": "Rule failed", ...}
```

### Best Practices
```python
# Create a practice
practice = {
    "name": "Test-Driven Development",
    "description": "Write tests before implementation",
    "category": "development",
    "implementation_guide": "1. Write test\n2. Run test (fails)\n3. Write code\n4. Run test (passes)",
    "benefits": ["Better design", "Fewer bugs", "Documentation"]
}
response = requests.post("http://localhost:8000/api/practices/", json=practice)
practice_id = response.json()["id"]

# Vote on effectiveness
vote = {"vote_type": "up", "comment": "Very effective practice"}
requests.post(f"http://localhost:8000/api/practices/{practice_id}/vote", json=vote)
```

### Template Rendering
```python
# Create a template
template = {
    "name": "Python Class Template",
    "type": "CODE",
    "category": "python",
    "template_content": '''class {{class_name}}:
    """{{description}}"""
    
    def __init__(self{{params}}):
        {{init_body}}
    
    {{methods}}''',
    "variables": {
        "class_name": "string",
        "description": "string",
        "params": "string",
        "init_body": "string",
        "methods": "string"
    }
}
response = requests.post("http://localhost:8000/api/templates/", json=template)
template_id = response.json()["id"]

# Render the template
variables = {
    "class_name": "UserService",
    "description": "Service for user management",
    "params": ", repository",
    "init_body": "self.repository = repository",
    "methods": "def get_user(self, user_id):\n        return self.repository.find(user_id)"
}
response = requests.post(f"http://localhost:8000/api/templates/{template_id}/render", json={"variables": variables})
print(response.json()["rendered_content"])
```

### Session Management
```python
# Start a development session
session = {
    "session_id": "dev-2025-01-31",
    "architects": ["Dr. Sarah Chen", "Alex Novak"],
    "status": "ACTIVE",
    "environment": {"os": "Linux", "python": "3.10"},
    "metadata": {"project": "AI Assistant", "phase": "Development"}
}
response = requests.post("http://localhost:8000/api/sessions/", json=session)
session_id = response.json()["id"]

# End the session
end_data = {
    "metrics": {"lines_of_code": 500, "tests_written": 20},
    "summary": "Completed API implementation"
}
response = requests.post(f"http://localhost:8000/api/sessions/{session_id}/end", json=end_data)
print(f"Session duration: {response.json()['duration_minutes']} minutes")

# Get session metrics
response = requests.get("http://localhost:8000/api/sessions/metrics")
print(response.json())
```

## Features

### 🔒 Governance Framework
- **Rules Engine**: Define and enforce development rules
- **Audit Logging**: Complete traceability of all operations
- **Effectiveness Tracking**: Measure rule and practice effectiveness

### 📚 Knowledge Management
- **Best Practices**: Store and share development practices
- **Templates**: Reusable code and document templates
- **Version Control**: Template versioning with parent-child relationships

### 📊 Analytics
- **Session Metrics**: Track development session statistics
- **Rule Statistics**: Monitor rule effectiveness and violations
- **Usage Tracking**: Template and practice adoption rates

### 🔄 Real-time Updates
- **WebSocket Support**: Real-time notifications
- **Event Broadcasting**: System-wide event distribution
- **Cache Management**: Two-tier caching for performance

## Architecture

### Technology Stack
- **Framework**: FastAPI 0.109.0
- **Database**: SQLAlchemy 2.0 + PostgreSQL/SQLite
- **Validation**: Pydantic v2
- **Testing**: Pytest + TestClient
- **Documentation**: OpenAPI/Swagger

### Project Structure
```
backend/
├── api/              # API endpoints
│   ├── rules.py      # Rules management
│   ├── practices.py  # Best practices
│   ├── templates.py  # Template system
│   └── sessions.py   # Session tracking
├── core/             # Business logic
│   ├── governance.py # Rule engine
│   ├── template_engine.py
│   └── auth.py       # Authentication
├── database/         # Database layer
│   ├── models.py     # SQLAlchemy models
│   └── database.py   # Database connection
├── schemas/          # Pydantic schemas
├── tests/            # Test suite
└── main.py           # Application entry
```

## Testing

### Run Tests
```bash
# Run all API tests
python -m pytest tests/test_api_*.py -v

# Run integration tests
python -m pytest tests/test_api_integration.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Test Coverage
- ✅ 100% API endpoint coverage
- ✅ Integration tests for all CRUD operations
- ✅ Governance framework validation
- ✅ Cross-API functionality tests

## Database

### Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Models
- **Rule**: Governance rules with conditions
- **Practice**: Best practices with voting
- **Template**: Reusable templates
- **Session**: Development sessions
- **AuditLog**: Complete audit trail
- **AIDecision**: AI decision tracking

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Environment
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO

# Cache
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

## API Documentation

Full API documentation is available at:
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Detailed endpoint documentation
- http://localhost:8000/docs - Interactive Swagger UI
- http://localhost:8000/redoc - ReDoc documentation

## Contributing

### Development Workflow
1. Create feature branch
2. Write tests first (TDD)
3. Implement feature
4. Ensure all tests pass
5. Update documentation
6. Submit pull request

### Code Style
- Follow PEP 8
- Use type hints
- Document all functions
- Write comprehensive tests

## License
MIT License - See LICENSE file for details

## Support
For issues and questions, please refer to the project documentation or contact the development team.