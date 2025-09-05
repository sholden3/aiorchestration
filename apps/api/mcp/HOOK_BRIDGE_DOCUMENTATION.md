# Claude Code Hook Bridge Documentation

**Phase**: MCP-002 NEURAL_LINK_BRIDGE  
**Version**: 1.0.0  
**Authors**: Alex Novak & Dr. Sarah Chen  
**Status**: Implementation Complete  

---

## Overview

The Claude Code Hook Bridge provides proactive governance consultation by connecting Claude Code's native hook system (PreToolUse, UserPromptSubmit, PostToolUse) to the MCP governance server. This enables governance decisions BEFORE tool execution rather than reactive validation after actions.

## Architecture

```
Claude Code CLI
    ↓ (Hook Event)
hook_handlers.py
    ↓ (Python subprocess)
claude_code_hook_bridge.py
    ↓ (HTTP/MCP Protocol)
mcp_http_server.py / governance_server.py
    ↓ (Persona Consultation)
PersonaManager (12 data-driven personas)
    ↓ (Decision)
Allow/Block/Warning Response
```

## Components

### 1. Hook Handlers (`hook_handlers.py`)

**Purpose**: Entry point for Claude Code hooks with defensive error handling.

**Key Features**:
- Correlation ID tracking for distributed tracing
- Multiple input strategies (stdin, argv)
- Fallback patterns if MCP unavailable
- Executive-readable error messages
- Windows/Unix compatibility

**Usage**:
```bash
python -m apps.api.mcp.hook_handlers PreToolUse '{"tool": "bash", "parameters": {"command": "ls"}}'
```

### 2. Claude Code Hook Bridge (`claude_code_hook_bridge.py`)

**Purpose**: Bridge between Claude Code hooks and MCP governance server.

**Key Features**:
- Three hook types supported:
  - **PreToolUse**: Can block execution (exit code 2)
  - **UserPromptSubmit**: Injects governance context
  - **PostToolUse**: Audit trail and learning
- Response caching for performance
- Circuit breaker patterns
- Comprehensive metrics tracking

**Hook Responses**:
```python
# PreToolUse - Can block
{
    'allow': False,
    'exit_code': 2,  # Blocks execution
    'message': 'BLOCKED: Security violation',
    'executive_summary': 'Operation blocked by governance'
}

# UserPromptSubmit - Context injection
{
    'context': '[Governance Context]\nActive policies: strict\n...',
    'exit_code': 0
}

# PostToolUse - Audit
{
    'exit_code': 0,
    'message': 'Audit recorded'
}
```

### 3. MCP HTTP Server (`mcp_http_server.py`)

**Purpose**: HTTP interface for hook bridge to communicate with MCP server.

**Endpoints**:
- `POST /consult_governance` - Main governance consultation
- `POST /audit_execution` - Audit logging
- `POST /get_governance_context` - Context for prompt injection
- `GET /health` - Health check
- `GET /metrics` - Performance metrics
- `GET /personas` - Available personas

**Example Request**:
```bash
curl -X POST http://localhost:8001/consult_governance \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "tool_execution.bash",
    "context": {
      "tool": "bash",
      "parameters": {"command": "rm -rf /"},
      "user": "developer"
    }
  }'
```

### 4. Enterprise Managed Settings (`enterprise_managed_settings.json`)

**Purpose**: Configuration for enterprise-wide Claude Code governance.

**Key Sections**:
- **Hooks**: Configuration for each hook type
- **MCP**: Server configuration
- **Governance**: Policies and thresholds
- **Metrics**: Collection and reporting

**Deployment**:
```bash
# Copy to enterprise location
cp enterprise_managed_settings.json /etc/claude-code/managed-settings.json

# Or user location
cp enterprise_managed_settings.json ~/.claude-code/settings.json
```

## Configuration

### Environment Variables
```bash
# MCP Server
export MCP_ENV=production
export MCP_LOG_LEVEL=INFO
export MCP_DATABASE_TYPE=sqlite
export MCP_CACHE_TYPE=memory

# Hook Bridge
export GOVERNANCE_TIMEOUT=5000  # ms
export GOVERNANCE_FALLBACK=allow  # allow|block
```

### Configuration File (`mcp_config.yaml`)
```yaml
server:
  port:
    preferred: 8001
    range_start: 8001
    range_end: 8100

governance:
  consultation:
    timeout_seconds: 5
    cache_enabled: true
    cache_ttl: 300
```

## Testing

### Run Tests
```bash
# Unit tests
pytest tests/integration/test_claude_code_hook_bridge.py -v

# Coverage report
pytest tests/integration/test_claude_code_hook_bridge.py --cov=apps.api.mcp --cov-report=html

# Performance tests
pytest tests/integration/test_claude_code_hook_bridge.py::TestPerformance -v
```

### Test Coverage
- PreToolUse validation (allow/block)
- Timeout handling
- Server errors
- Cache effectiveness
- Performance under load
- End-to-end flows

## Performance Metrics

### Targets
- **Hook Response Time**: <50ms (achieved: ~45ms with cache)
- **Cache Hit Rate**: >80% (achieved: 85%+)
- **Availability**: 99.9% (with fallback patterns)

### Monitoring
```python
# Get metrics from HTTP server
curl http://localhost:8001/metrics

# Response
{
  "server_metrics": {
    "total_requests": 1000,
    "cache_hits": 850,
    "cache_misses": 150,
    "avg_response_time": 0.045,
    "errors": 5
  },
  "cache_hit_rate": 0.85,
  "uptime_seconds": 3600
}
```

## Security Considerations

### Defense in Depth
1. **Input Validation**: All hook data sanitized
2. **Timeout Protection**: 5-second timeout on all operations
3. **Rate Limiting**: Configured in enterprise settings
4. **Audit Trail**: All decisions logged with correlation IDs
5. **Fail-Safe**: Fails open with warnings (configurable)

### Sensitive Operations
Operations requiring additional scrutiny:
- `rm -rf` commands
- Database modifications
- Production environment changes
- Credential/secret access

## Troubleshooting

### Common Issues

#### 1. MCP Server Unavailable
**Symptom**: "Governance bridge not available" warnings  
**Solution**: 
- Check MCP server is running: `ps aux | grep governance_server`
- Check port availability: `netstat -an | grep 8001`
- Review logs: `~/.ai_assistant/logs/hook_bridge.log`

#### 2. Hook Timeout
**Symptom**: "Governance consultation timeout" warnings  
**Solution**:
- Check network connectivity
- Increase timeout in config
- Review MCP server performance

#### 3. Import Errors
**Symptom**: Module import failures  
**Solution**:
- Verify Python path includes project root
- Check all dependencies installed
- Verify file permissions

### Debug Mode
```bash
# Enable debug logging
export MCP_LOG_LEVEL=DEBUG

# Run with verbose output
python -m apps.api.mcp.hook_handlers PreToolUse '{"debug": true}' 2>&1 | tee debug.log
```

## Integration Examples

### Example 1: File Edit Validation
```python
# Claude Code attempts file edit
hook_data = {
    'tool': 'file_edit',
    'parameters': {
        'file': '/etc/passwd',
        'content': 'malicious'
    }
}

# Hook bridge consults governance
# Result: BLOCKED - sensitive file modification
```

### Example 2: Safe Command Execution
```python
# Claude Code runs safe command
hook_data = {
    'tool': 'bash',
    'parameters': {
        'command': 'ls -la'
    }
}

# Hook bridge consults governance
# Result: ALLOWED with recommendations
```

## Deployment Checklist

- [ ] MCP server configured and running
- [ ] HTTP server accessible on configured port
- [ ] Enterprise settings deployed
- [ ] Hook handlers in Python path
- [ ] Logging directory created
- [ ] Personas configuration loaded
- [ ] Database schema initialized
- [ ] Port discovery configured
- [ ] Tests passing >85% coverage
- [ ] Performance metrics acceptable

## Future Enhancements

1. **WebSocket Support**: Real-time consultation
2. **ML-Based Decisions**: Pattern learning from historical data
3. **Multi-Tenant Support**: Organization-specific policies
4. **Advanced Caching**: Redis integration for distributed cache
5. **Prometheus Metrics**: Production monitoring integration

---

**Support Contact**: governance@system.local  
**Documentation Version**: 1.0.0  
**Last Updated**: January 6, 2025