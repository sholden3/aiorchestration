# MCP Governance Server Architecture

**Component:** `apps/api/mcp/governance_server.py`  
**Version:** 1.0.0  
**Phase:** MCP-001 PHOENIX_RISE_FOUNDATION  
**Status:** Operational  

## Overview

The MCP Governance Server is the core intelligence component that provides proactive governance consultation through the Model Context Protocol. It orchestrates persona consultations, manages sessions, and provides governance decisions to Claude Code.

## Architecture

### Class Structure
```python
class GovernanceMCPServer:
    def __init__(self):
        self.config = get_config()
        self.server = Server('governance-intelligence')
        self.personas = PersonaManager()
        self.sessions = {}
        self.metrics = {}
        self.cache = {}
```

### Core Components

#### 1. Server Initialization
- Loads configuration from `mcp_config.yaml`
- Discovers available port (8001-8100)
- Initializes persona manager
- Sets up MCP protocol handlers

#### 2. Protocol Handlers

##### Tool: `consult_governance`
```python
async def consult_governance(operation: str, context: Dict) -> str:
    # Check cache first
    # Get persona guidance
    # Generate recommendations
    # Check warnings
    # Return decision
```

**Input:**
- `operation`: Type of operation (e.g., 'file_edit', 'command_execution')
- `context`: Contextual information about the operation

**Output:**
```json
{
  "approved": true,
  "confidence": 0.95,
  "persona_guidance": {...},
  "recommendations": [...],
  "warnings": [...]
}
```

##### Tool: `get_historical_decisions`
- Retrieves past governance decisions
- Enables learning from history
- Supports pattern matching

##### Tool: `consult_persona`
- Direct consultation with specific persona
- Domain-specific expertise
- Confidence scoring

##### Resource: `governance_config`
- Current governance configuration
- Rules and thresholds
- Active policies

### Data Flow

1. **Request Reception**
   - MCP protocol message received
   - Operation and context extracted
   - Correlation ID assigned

2. **Cache Check**
   - Generate cache key from operation+context
   - Return cached result if fresh (<5 min)
   - Otherwise proceed to consultation

3. **Persona Consultation**
   - Determine relevant personas based on patterns
   - Consult each persona asynchronously
   - Aggregate guidance with confidence scores

4. **Decision Generation**
   - Apply governance rules
   - Generate recommendations
   - Check for warnings/blocks
   - Calculate overall confidence

5. **Response Caching**
   - Store result with TTL
   - Update metrics
   - Return formatted response

## Configuration

### Server Configuration (`mcp_config.yaml`)
```yaml
server:
  name: governance-intelligence
  environment: production
  log_level: INFO
  
port:
  service_name: mcp-governance
  preferred: 8001
  range_start: 8001
  range_end: 8100
  fallback: 8001

database:
  type: sqlite  # or postgresql
  path: ./data/mcp_governance.db
  
cache:
  type: memory  # or redis
  ttl: 300  # 5 minutes
  max_size: 1000

governance:
  personas_config: libs/governance/personas.yaml
  rules_config: libs/governance/documentation_standards.yaml
  mode: proactive
  compliance_level: 0.95
```

### Environment Variables
```bash
GOVERNANCE_PORT=8001
DATABASE_URL=sqlite:///data/mcp_governance.db
CACHE_TYPE=memory
LOG_LEVEL=INFO
MCP_ENV=production
```

## Port Discovery System

### Implementation (`port_integration.py`)
```python
async def discover_backend_port(
    service_name: str, 
    fallback: int
) -> int:
    # Check if port already allocated
    # Find available port in range
    # Register allocation
    # Return port
```

### Port Allocation Strategy
1. Check preferred port (8001)
2. Scan range 8001-8100
3. Use fallback if no ports available
4. Register in `.ports.json`

## Session Management

### Session Tracking
```python
sessions = {
    "session_id": {
        "start_time": datetime,
        "correlation_ids": [],
        "decisions": [],
        "metrics": {}
    }
}
```

### Session Lifecycle
1. **Creation**: On first consultation
2. **Updates**: Each decision logged
3. **Metrics**: Performance tracked
4. **Cleanup**: After inactivity timeout

## Performance Optimization

### Caching Strategy
- **Key Generation**: Hash of operation+context
- **TTL**: 5 minutes default
- **Hit Rate Target**: >80%
- **Eviction**: LRU when size exceeded

### Response Time Optimization
- Parallel persona consultation
- Early cache returns
- Connection pooling
- Async throughout

### Metrics Tracking
```python
metrics = {
    'total_requests': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'avg_response_time': 0,
    'errors': 0
}
```

## Error Handling

### Error Categories
1. **Configuration Errors**: Missing config files
2. **Network Errors**: Port unavailable
3. **Persona Errors**: Consultation failures
4. **Cache Errors**: Cache unavailable

### Fallback Strategies
- Configuration: Use defaults
- Network: Try alternate ports
- Personas: Use core personas only
- Cache: Proceed without caching

### Error Response Format
```json
{
  "error": "Error description",
  "fallback": "Recommended action",
  "correlation_id": "uuid",
  "timestamp": "ISO-8601"
}
```

## Security Considerations

### Input Validation
- Sanitize operation names
- Validate context structure
- Check for injection attempts
- Size limits on context

### Access Control
- API key validation (future)
- Rate limiting per client
- IP allowlisting (production)

### Audit Logging
- All decisions logged
- Correlation IDs throughout
- Sensitive data redacted
- Retention policies applied

## Database Schema

### PostgreSQL Schema
```sql
CREATE TABLE governance_sessions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    correlation_ids JSONB,
    decisions JSONB,
    metrics JSONB
);

CREATE TABLE governance_decisions (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES governance_sessions(id),
    timestamp TIMESTAMP NOT NULL,
    operation VARCHAR(255),
    context JSONB,
    decision JSONB,
    personas_consulted JSONB,
    correlation_id UUID
);
```

## Testing

### Unit Tests
```python
# test_governance_server.py
def test_server_initialization()
def test_persona_consultation()
def test_cache_functionality()
def test_port_discovery()
def test_error_handling()
```

### Integration Tests
- MCP protocol compliance
- End-to-end consultation flow
- Multi-persona orchestration
- Performance under load

### Performance Tests
- Response time <100ms
- 100 concurrent requests
- Cache hit rate >80%
- Memory usage stable

## Deployment

### Local Development
```bash
python -m apps.api.mcp.governance_server
```

### Production Deployment
```bash
# With systemd
systemctl start mcp-governance

# With Docker
docker run -p 8001:8001 mcp-governance:latest

# With Kubernetes
kubectl apply -f k8s/mcp-governance.yaml
```

### Health Monitoring
- Endpoint: `/health`
- Checks: Database, cache, personas
- Frequency: Every 30 seconds
- Alerts: On failure

## Troubleshooting

### Server Won't Start
1. Check port availability
2. Verify configuration files exist
3. Check Python dependencies
4. Review log files

### Slow Response Times
1. Check cache hit rate
2. Review persona count
3. Analyze database queries
4. Check network latency

### High Error Rate
1. Review error logs
2. Check persona availability
3. Verify configuration
4. Test fallback patterns

## Future Improvements

### Phase 3 Enhancements
- Database persistence
- Session analytics
- Learning algorithms

### Phase 4 Enhancements
- ML-based decisions
- Cross-project learning
- Advanced caching

### Long-term Vision
- Distributed governance
- Real-time learning
- Predictive suggestions

---

**Author:** Alex Novak & Dr. Sarah Chen  
**Last Updated:** 2025-01-06  
**Next Review:** Post Phase MCP-003