# AI Orchestration System API Documentation

## Base URL
`http://localhost:8001`

## Available Endpoints

### 1. Health Check
**GET** `/health`
```bash
curl http://localhost:8001/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-23T01:37:25.887307",
  "cache_enabled": true,
  "personas_available": 3
}
```

### 2. Execute Orchestrated Task (with Assumption Fighting)
**POST** `/ai/orchestrated`
```bash
curl -X POST http://localhost:8001/ai/orchestrated \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Your question or task here",
    "persona": "architect",
    "context": {
      "team_size": 5,
      "budget": "limited"
    },
    "use_cache": false
  }'
```
**Request Body:**
- `prompt` (string, required): The task or question
- `persona` (string, optional): Preferred persona type
- `context` (object, optional): Additional context
- `use_cache` (boolean, optional): Use cached responses

**Response:**
```json
{
  "success": true,
  "response": "Consensus decision after persona debate",
  "cached": false,
  "tokens_saved": 0,
  "persona_used": "orchestrated_consensus",
  "execution_time_ms": 2000
}
```

### 3. Execute Regular Task (without orchestration)
**POST** `/ai/execute`
```bash
curl -X POST http://localhost:8001/ai/execute \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Simple question",
    "persona": null,
    "context": {},
    "use_cache": true
  }'
```

### 4. Orchestration Status
**GET** `/orchestration/status`
```bash
curl http://localhost:8001/orchestration/status
```
**Response:**
```json
{
  "is_running": true,
  "agents": {
    "total": 6,
    "active": 6,
    "idle": 6,
    "busy": 0
  },
  "tasks": {
    "queued": 0,
    "active": 0,
    "completed": 10,
    "failed": 2
  },
  "performance": {
    "total_tokens_used": 5000,
    "average_response_time": 1.5,
    "overall_success_rate": 0.83
  },
  "governance_active": true,
  "persona_orchestration_active": true
}
```

### 5. Cache Metrics
**GET** `/metrics/cache`
```bash
curl http://localhost:8001/metrics/cache
```

### 6. Clear Cache
**POST** `/cache/clear`
```bash
curl -X POST http://localhost:8001/cache/clear
```

### 7. Suggest Persona
**POST** `/persona/suggest`
```bash
curl -X POST http://localhost:8001/persona/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "description": "I need help with database optimization"
  }'
```

### 8. Resolve Persona Conflict
**POST** `/persona/resolve-conflict`
```bash
curl -X POST http://localhost:8001/persona/resolve-conflict \
  -H "Content-Type: application/json" \
  -d '{
    "opinions": [
      {"persona": "sarah_chen", "opinion": "Use microservices"},
      {"persona": "marcus_rodriguez", "opinion": "Keep monolithic"}
    ]
  }'
```

## Python Client Examples

```python
import requests
import json

class AIOrchestrationClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
    
    def orchestrated_request(self, prompt, context=None):
        """Send request through full orchestration"""
        response = requests.post(
            f"{self.base_url}/ai/orchestrated",
            json={
                "prompt": prompt,
                "context": context or {},
                "use_cache": False
            }
        )
        return response.json()
    
    def get_status(self):
        """Get orchestration status"""
        response = requests.get(f"{self.base_url}/orchestration/status")
        return response.json()

# Usage
client = AIOrchestrationClient()
result = client.orchestrated_request(
    "Should we use Kubernetes?",
    context={"team_size": 5}
)
print(result["response"])
```