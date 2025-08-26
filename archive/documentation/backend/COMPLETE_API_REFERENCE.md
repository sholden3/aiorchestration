# Complete AI Orchestration System API Reference

## System Status: ✅ FULLY OPERATIONAL

- **Base URL**: `http://localhost:8001`
- **Interactive Documentation**: http://localhost:8001/docs
- **OpenAPI Spec**: http://localhost:8001/openapi.json

## Core Orchestration APIs

### 1. Health & Status
- `GET /health` - Service health check
- `GET /orchestration/status` - Full orchestration engine status
- `GET /api/v1/discover` - Discover all available endpoints

### 2. AI Task Execution
- `POST /ai/orchestrated` - Execute with full persona orchestration & assumption fighting
- `POST /ai/execute` - Execute simple task without orchestration

### 3. Metrics & Performance
- `GET /metrics/cache` - Cache performance metrics
- `GET /metrics/performance` - Overall system performance
- `POST /cache/clear` - Clear cache

## Persona Management APIs

### 4. Persona Information
- `GET /personas/` - List all personas with details
- `GET /personas/{persona_id}` - Get specific persona details
- `POST /personas/{persona_id}/challenge` - Challenge persona assumption

### 5. Persona Interaction
- `POST /persona/suggest` - Get persona suggestion for task
- `POST /persona/resolve-conflict` - Resolve conflicts between personas

## AI Agent Management APIs

### 6. Agent Information
- `GET /agents/` - List all AI agents
- `GET /agents/{agent_id}` - Get specific agent details
- `GET /agents/status` - Current status of all agents

### 7. Agent Operations
- `POST /agents/{agent_id}/assign` - Manually assign task to agent
- `GET /agents/{agent_id}/performance` - Get agent performance metrics

## Rules & Best Practices APIs

### 8. Rules Management
- `GET /rules/` - Get all business rules
- `POST /rules/` - Create new rule
- `GET /rules/validate` - Validate code against rules
- `GET /rules/best-practices` - Get best practices

## Assumption Management APIs

### 9. Assumptions Tracking
- `GET /assumptions/` - List all assumptions
- `POST /assumptions/` - Create new assumption
- `POST /assumptions/{id}/validate` - Validate assumption with evidence
- `GET /assumptions/validation-history` - Get validation history

## Governance APIs

### 10. Decision Management
- `POST /governance/request-decision` - Request governance decision
- `GET /governance/decisions` - Get decision history
- `GET /governance/consensus-level` - Check consensus on topic
- `POST /governance/escalate` - Escalate unresolved issues

## Usage Examples

### Example 1: Execute Task with Full Orchestration
```python
import requests

response = requests.post(
    "http://localhost:8001/ai/orchestrated",
    json={
        "prompt": "Should we adopt microservices?",
        "context": {"team_size": 10},
        "use_cache": False
    }
)
result = response.json()
print(f"Decision: {result['response']}")
```

### Example 2: Check Persona Consensus
```python
# Get all personas
personas = requests.get("http://localhost:8001/personas/").json()

# Check consensus on a topic
consensus = requests.get(
    "http://localhost:8001/governance/consensus-level",
    params={"topic": "kubernetes_adoption"}
).json()

print(f"Consensus Level: {consensus['consensus_level']}")
print(f"Agreeing: {consensus['agreeing_personas']}")
print(f"Disagreeing: {consensus['disagreeing_personas']}")
```

### Example 3: Validate Assumptions
```python
# Create assumption
assumption = {
    "assumption_id": "TECH-001",
    "category": "technical",
    "statement": "Our database can handle 1M requests/day",
    "confidence_level": 0.7,
    "impact_if_wrong": "System failure",
    "owner": "marcus_rodriguez"
}

requests.post("http://localhost:8001/assumptions/", json=assumption)

# Validate with evidence
validation = requests.post(
    f"http://localhost:8001/assumptions/TECH-001/validate",
    json={
        "validation_method": "load_testing",
        "evidence": ["Test showed 1.2M requests handled successfully"]
    }
)
```

## Key Features

### Persona Orchestration
- **Sarah Chen**: AI/ML expertise, innovative but may over-engineer
- **Marcus Rodriguez**: Performance focus, pragmatic, conservative
- **Emily Watson**: UX focus, user-centric, empathetic

### Assumption Fighting Process
1. Each persona forms independent opinions
2. Assumptions are extracted and catalogued
3. Personas challenge each other's assumptions
4. Evidence is gathered and evaluated
5. Structured debate occurs
6. Consensus is built (or dissent documented)
7. Final decision is validated against evidence

### Governance Levels
- **UNANIMOUS**: All personas agree
- **HIGH**: Strong agreement with minor dissent
- **MEDIUM**: Mixed opinions but workable consensus
- **LOW**: Significant disagreement
- **NONE**: No consensus, escalation required

## System Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI REST API Layer          │
├─────────────────────────────────────────┤
│     Persona Orchestration Enhanced      │
│         (Assumption Fighting)           │
├─────────────────────────────────────────┤
│      AI Orchestration Engine            │
│         (Agent Management)              │
├─────────────────────────────────────────┤
│    Unified Governance Orchestrator      │
│         (Decision Making)              │
├─────────────────────────────────────────┤
│   Cache Manager │ Database │ Metrics    │
└─────────────────────────────────────────┘
```

## Benefits of This System

1. **Prevents Hallucinations**: Multiple personas validate each assumption
2. **Evidence-Based Decisions**: All decisions require supporting evidence
3. **Balanced Perspectives**: Technical, performance, and UX views considered
4. **Audit Trail**: Complete history of decisions and validations
5. **Flexible Governance**: Configurable consensus requirements
6. **Performance Optimized**: Intelligent caching and agent selection
7. **Extensible**: Easy to add new personas, agents, and rules

## Monitoring & Observability

- Real-time metrics at `/metrics/performance`
- Agent performance tracking
- Assumption validation history
- Governance decision audit trail
- Cache hit rates and optimization metrics

## Next Steps for Enhancement

1. Add WebSocket support for real-time updates
2. Implement GraphQL API for complex queries
3. Add machine learning for agent selection optimization
4. Create dashboard UI for visualization
5. Add more sophisticated evidence gathering mechanisms
6. Implement A/B testing for decision validation
7. Add support for custom persona definitions