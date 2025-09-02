# AI Assistant Backend API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints require authentication via the `get_current_user` dependency. Currently returns a mock user for development.

## API Endpoints

### Rules API

#### GET /api/rules/
List all rules with filtering and pagination.

**Query Parameters:**
- `skip` (int): Number of items to skip (default: 0)
- `limit` (int): Maximum items to return (default: 100, max: 1000)
- `status` (enum): Filter by status [DRAFT, ACTIVE, DEPRECATED]
- `severity` (enum): Filter by severity [INFO, WARNING, ERROR, CRITICAL]
- `category` (string): Filter by category

**Response:** `RuleListResponse`
```json
{
  "rules": [...],
  "total": 100,
  "skip": 0,
  "limit": 100
}
```

#### GET /api/rules/stats
Get rule statistics.

**Response:** `RuleStats`
```json
{
  "total_rules": 50,
  "active_rules": 30,
  "average_effectiveness": 0.85,
  "severity_distribution": {...},
  "last_updated": "2025-01-31T12:00:00"
}
```

#### GET /api/rules/{rule_id}
Get a specific rule by ID.

**Response:** `RuleResponse`

#### POST /api/rules/
Create a new rule.

**Request Body:** `RuleCreate`
```json
{
  "name": "Code Review Required",
  "description": "All code must be reviewed",
  "category": "development",
  "severity": "WARNING",
  "status": "ACTIVE",
  "condition": "has_review == True",
  "action": "block_merge"
}
```

#### PUT /api/rules/{rule_id}
Update an existing rule.

**Request Body:** `RuleUpdate` (all fields optional)

#### DELETE /api/rules/{rule_id}
Soft delete a rule (sets status to DEPRECATED).

#### POST /api/rules/{rule_id}/enforce
Enforce a rule against given context.

**Request Body:**
```json
{
  "has_review": false,
  "author": "developer1"
}
```

**Response:**
```json
{
  "rule_id": "...",
  "rule_name": "Code Review Required",
  "passed": false,
  "severity": "WARNING",
  "message": "Rule failed",
  "action": "block_merge"
}
```

### Practices API

#### GET /api/practices/
List all practices with filtering and pagination.

**Query Parameters:**
- `skip` (int): Number of items to skip
- `limit` (int): Maximum items to return
- `category` (string): Filter by category
- `min_effectiveness` (float): Minimum effectiveness score (0-1)

**Response:** `PracticeListResponse`

#### GET /api/practices/{practice_id}
Get a specific practice by ID.

#### POST /api/practices/
Create a new best practice.

**Request Body:** `PracticeCreate`
```json
{
  "name": "Code Review",
  "description": "Peer review all code changes",
  "category": "development",
  "implementation_guide": "Steps to implement...",
  "benefits": ["Quality", "Knowledge sharing"],
  "examples": ["Example 1", "Example 2"]
}
```

#### PUT /api/practices/{practice_id}
Update an existing practice.

#### DELETE /api/practices/{practice_id}
Delete a practice.

#### POST /api/practices/{practice_id}/vote
Vote on a practice's effectiveness.

**Request Body:** `PracticeVote`
```json
{
  "vote_type": "up",
  "comment": "Very helpful practice"
}
```

#### POST /api/practices/{practice_id}/apply
Record an application of a practice.

**Request Body:** `PracticeApplication`
```json
{
  "applied_to": "Backend refactoring",
  "effectiveness_rating": 0.9,
  "notes": "Improved code quality significantly"
}
```

### Templates API

#### GET /api/templates/
List all templates with filtering and pagination.

**Query Parameters:**
- `skip` (int): Number of items to skip
- `limit` (int): Maximum items to return
- `type` (enum): Filter by type [CODE, CONFIG, DOCUMENT, WORKFLOW, ANALYSIS]
- `category` (string): Filter by category

**Response:** `TemplateListResponse`

#### GET /api/templates/types
Get all available template types.

#### GET /api/templates/{template_id}
Get a specific template by ID.

#### POST /api/templates/
Create a new template.

**Request Body:** `TemplateCreate`
```json
{
  "name": "Python Function Template",
  "type": "CODE",
  "category": "python",
  "template_content": "def {{function_name}}({{params}}):\n    {{body}}",
  "description": "Template for Python functions",
  "variables": {
    "function_name": "string",
    "params": "string",
    "body": "string"
  }
}
```

#### PUT /api/templates/{template_id}
Update an existing template.

#### DELETE /api/templates/{template_id}
Delete a template.

#### POST /api/templates/{template_id}/render
Render a template with provided variables.

**Request Body:** `TemplateRender`
```json
{
  "variables": {
    "function_name": "calculate_sum",
    "params": "a, b",
    "body": "return a + b"
  }
}
```

**Response:** `TemplateRenderResponse`
```json
{
  "rendered_content": "def calculate_sum(a, b):\n    return a + b",
  "validation_errors": [],
  "metadata": {...}
}
```

#### POST /api/templates/{template_id}/clone
Clone an existing template.

**Query Parameters:**
- `new_name` (string, required): Name for the cloned template

### Sessions API

#### GET /api/sessions/
List all sessions with filtering and pagination.

**Query Parameters:**
- `skip` (int): Number of items to skip
- `limit` (int): Maximum items to return
- `status` (enum): Filter by status [ACTIVE, WARNING, EXPIRED, ENDED]
- `architect` (string): Filter by architect name

**Response:** `SessionListResponse`

#### GET /api/sessions/active
Get all currently active sessions.

#### GET /api/sessions/metrics
Get session metrics and statistics.

**Response:** `SessionMetrics`
```json
{
  "total_sessions": 100,
  "active_sessions": 5,
  "average_duration_minutes": 45.5,
  "total_decisions": 500,
  "total_audit_logs": 2000,
  "sessions_by_status": {...}
}
```

#### GET /api/sessions/{session_id}
Get a specific session by ID.

#### POST /api/sessions/
Create a new development session.

**Request Body:** `SessionCreate`
```json
{
  "session_id": "dev-session-001",
  "architects": ["Dr. Sarah Chen", "Alex Novak"],
  "status": "ACTIVE",
  "environment": {
    "os": "Linux",
    "python_version": "3.10"
  },
  "metadata": {
    "project": "AI Assistant",
    "phase": "Development"
  }
}
```

#### PUT /api/sessions/{session_id}
Update an existing session.

#### POST /api/sessions/{session_id}/end
End a development session.

**Request Body:** `SessionEnd`
```json
{
  "end_time": "2025-01-31T15:00:00",
  "metrics": {
    "lines_of_code": 500,
    "tests_written": 20
  },
  "summary": "Completed API implementation"
}
```

#### GET /api/sessions/{session_id}/audit-logs
Get all audit logs for a session.

**Query Parameters:**
- `skip` (int): Number of items to skip
- `limit` (int): Maximum items to return

#### GET /api/sessions/{session_id}/decisions
Get all AI decisions for a session.

**Query Parameters:**
- `skip` (int): Number of items to skip
- `limit` (int): Maximum items to return

#### DELETE /api/sessions/{session_id}
Soft delete a session (sets status to EXPIRED).

## Response Models

### Common Fields
Most response models include:
- `id` (UUID): Unique identifier
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

### Error Responses
All endpoints return standard HTTP error codes:
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `422`: Unprocessable Entity (Pydantic validation errors)
- `500`: Internal Server Error

Example error response:
```json
{
  "detail": "Rule not found"
}
```

## Database Schema

### Rule Model
- Tracks governance rules with conditions and actions
- Includes enforcement metrics and effectiveness scoring
- Supports soft deletion via status

### Practice Model
- Stores best practices with implementation guides
- Tracks adoption rate and effectiveness through voting
- Includes application history

### Template Model
- Stores reusable templates with variable substitution
- Supports versioning with parent-child relationships
- Tracks usage statistics

### Session Model
- Tracks development sessions with timing and metrics
- Links to audit logs and AI decisions
- Calculates duration automatically

### AuditLog Model
- Records all system events
- Stores before/after states for changes
- Links to sessions for traceability

### AIDecision Model
- Tracks AI-made decisions
- Includes confidence levels and reasoning
- Links to sessions and rules

## Testing

The API includes comprehensive integration tests covering:
- CRUD operations for all entities
- Governance integration (audit logging)
- Cross-API functionality
- Metrics and statistics endpoints

Run tests with:
```bash
cd ai-assistant/backend
python -m pytest tests/test_api_integration.py -v
```

## Running the API

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up the database (optional, uses SQLite by default):
```bash
alembic upgrade head
```

3. Run the development server:
```bash
uvicorn main:app --reload --port 8000
```

4. Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

- `DATABASE_URL`: Database connection string (default: sqlite:///./test.db)
- `ENVIRONMENT`: Environment name (development/staging/production)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)