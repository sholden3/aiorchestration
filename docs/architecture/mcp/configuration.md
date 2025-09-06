# MCP Configuration Management

**Component:** Configuration System  
**Version:** 1.0.0  
**Phase:** MCP-001 PHOENIX_RISE_FOUNDATION  
**Status:** Operational  
**Authors:** Alex Novak & Dr. Sarah Chen  

## Overview

The MCP configuration system provides a hierarchical, environment-aware configuration management solution for all MCP components. It supports multiple configuration sources, environment variable substitution, validation, and runtime reloading.

## Configuration Philosophy

### Design Principles
1. **Convention Over Configuration**: Sensible defaults that work out of the box
2. **Environment-Aware**: Different settings for dev/staging/production
3. **Security First**: No secrets in configuration files
4. **Validation**: Schema validation prevents invalid configurations
5. **Hot Reload**: Configuration changes without restart (where safe)

### Configuration Hierarchy
```
1. Default Values (Hardcoded)
    ↓ Overridden by
2. Configuration Files (YAML/JSON)
    ↓ Overridden by
3. Environment Variables
    ↓ Overridden by
4. Command Line Arguments
    ↓ Overridden by
5. Runtime Updates (Via API)
```

## Configuration Files

### 1. MCP Server Configuration (`mcp_config.yaml`)
```yaml
# MCP Governance Server Configuration
server:
  name: governance-intelligence
  environment: ${MCP_ENV:development}
  log_level: ${LOG_LEVEL:INFO}
  debug: ${DEBUG:false}

port:
  service_name: mcp-governance
  preferred: ${MCP_PORT:8001}
  range_start: 8001
  range_end: 8100
  fallback: 8001
  discovery:
    enabled: ${PORT_DISCOVERY_ENABLED:true}
    registry_file: ${PORT_REGISTRY:.ports.json}

database:
  type: ${DATABASE_TYPE:sqlite}  # sqlite or postgresql
  
  # SQLite configuration
  sqlite:
    path: ${SQLITE_PATH:./data/mcp_governance.db}
    
  # PostgreSQL configuration  
  postgresql:
    host: ${DB_HOST:localhost}
    port: ${DB_PORT:5432}
    database: ${DB_NAME:mcp_governance}
    user: ${DB_USER:mcp_user}
    password: ${DB_PASSWORD}  # Required from environment
    pool_size: ${DB_POOL_SIZE:10}
    
cache:
  type: ${CACHE_TYPE:memory}  # memory or redis
  
  memory:
    max_size: ${CACHE_MAX_SIZE:1000}
    ttl: ${CACHE_TTL:300}
    
  redis:
    host: ${REDIS_HOST:localhost}
    port: ${REDIS_PORT:6379}
    db: ${REDIS_DB:0}
    password: ${REDIS_PASSWORD}
    ttl: ${CACHE_TTL:300}

governance:
  personas_config: ${PERSONAS_CONFIG:libs/governance/personas.yaml}
  rules_config: ${RULES_CONFIG:libs/governance/documentation_standards.yaml}
  mode: ${GOVERNANCE_MODE:proactive}  # proactive, reactive, hybrid
  compliance_level: ${COMPLIANCE_LEVEL:0.95}
  
  consultation:
    timeout_seconds: ${CONSULTATION_TIMEOUT:5}
    cache_enabled: ${CONSULTATION_CACHE:true}
    fallback_behavior: ${FALLBACK_BEHAVIOR:allow}  # allow, block, warn
    
  audit:
    enabled: ${AUDIT_ENABLED:true}
    retention_days: ${AUDIT_RETENTION:30}
    
performance:
  max_concurrent_consultations: ${MAX_CONCURRENT:100}
  circuit_breaker:
    enabled: ${CIRCUIT_BREAKER_ENABLED:true}
    failure_threshold: ${CB_FAILURE_THRESHOLD:5}
    timeout_seconds: ${CB_TIMEOUT:60}
    half_open_requests: ${CB_HALF_OPEN:3}
```

### 2. Hook Bridge Configuration (`enterprise_managed_settings.json`)
```json
{
  "version": "1.0.0",
  "environment": "${NODE_ENV:development}",
  
  "hooks": {
    "preToolUse": {
      "enabled": true,
      "handler": "apps.api.mcp.hook_handlers",
      "args": ["PreToolUse"],
      "timeout": 5000,
      "fallback": "allow",
      "cache": {
        "enabled": true,
        "ttl": 300,
        "maxSize": 500
      },
      "retry": {
        "enabled": true,
        "attempts": 3,
        "delay": 100,
        "backoff": 2
      }
    },
    
    "userPromptSubmit": {
      "enabled": true,
      "handler": "apps.api.mcp.hook_handlers",
      "args": ["UserPromptSubmit"],
      "contextInjection": true,
      "maxContextSize": 1024
    },
    
    "postToolUse": {
      "enabled": true,
      "handler": "apps.api.mcp.hook_handlers",
      "args": ["PostToolUse"],
      "audit": true,
      "async": true
    }
  },
  
  "mcp": {
    "server": {
      "protocol": "http",
      "host": "${MCP_HOST:127.0.0.1}",
      "port": "${MCP_PORT:8001}",
      "timeout": 5000,
      "healthCheck": {
        "enabled": true,
        "interval": 30000,
        "timeout": 5000
      }
    }
  },
  
  "governance": {
    "mode": "proactive",
    "strictMode": false,
    "blockPatterns": [
      "rm -rf /",
      ":(){ :|:& };:",
      "DROP DATABASE",
      "DELETE FROM users WHERE 1=1"
    ],
    "warningPatterns": [
      "sudo",
      "chmod 777",
      "eval",
      "exec"
    ],
    "exemptions": {
      "users": ["admin", "system"],
      "tools": ["test_runner"],
      "projects": ["sandbox"]
    }
  },
  
  "logging": {
    "level": "${LOG_LEVEL:INFO}",
    "file": "${LOG_FILE:~/.ai_assistant/logs/hook_bridge.log}",
    "maxSize": "10MB",
    "maxFiles": 5,
    "format": "json"
  },
  
  "metrics": {
    "enabled": true,
    "endpoint": "/metrics",
    "interval": 60000,
    "detailed": false
  }
}
```

### 3. Claude Code MCP Configuration (`.mcp.json`)
```json
{
  "version": "1.0.0",
  "mcpServers": {
    "governance": {
      "name": "Governance Intelligence",
      "description": "Proactive governance consultation for Claude Code",
      "command": "python",
      "args": [
        "-m",
        "apps.api.mcp.governance_server"
      ],
      "env": {
        "PYTHONPATH": "${PROJECT_ROOT}",
        "GOVERNANCE_PORT": "${MCP_PORT:8001}",
        "DATABASE_URL": "${DATABASE_URL:sqlite:///data/mcp.db}",
        "CACHE_TYPE": "${CACHE_TYPE:memory}",
        "LOG_LEVEL": "${LOG_LEVEL:INFO}",
        "MCP_ENV": "${MCP_ENV:production}"
      },
      "capabilities": [
        "consultation",
        "audit",
        "personas",
        "history"
      ],
      "autoStart": true,
      "restartOnFailure": true,
      "maxRestarts": 3
    }
  },
  
  "client": {
    "timeout": 5000,
    "retries": 3,
    "cache": {
      "enabled": true,
      "ttl": 300
    }
  }
}
```

## Configuration Loading

### Configuration Loader (`config_loader.py`)
```python
class ConfigLoader:
    """Hierarchical configuration loader with environment substitution."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        self._substitute_env_vars()
        self._validate_config()
```

### Environment Variable Substitution
```python
def _substitute_env_vars(self, value: str) -> Any:
    """
    Replace ${VAR:default} with environment value.
    
    Examples:
        ${PORT:8000} -> os.getenv('PORT', '8000')
        ${DATABASE_URL} -> os.getenv('DATABASE_URL') or raise
    """
    pattern = r'\${([^:}]+)(:([^}]+))?}'
    
    def replacer(match):
        var_name = match.group(1)
        default = match.group(3)
        
        value = os.getenv(var_name)
        if value is None:
            if default is None:
                raise ValueError(f"Required env var {var_name} not set")
            return default
        return value
    
    return re.sub(pattern, replacer, value)
```

### Configuration Validation
```python
def _validate_config(self):
    """Validate configuration against schema."""
    schema = {
        "type": "object",
        "required": ["server", "port", "governance"],
        "properties": {
            "server": {
                "type": "object",
                "required": ["name", "environment"]
            },
            "port": {
                "type": "object",
                "required": ["preferred", "fallback"]
            },
            "governance": {
                "type": "object",
                "required": ["mode", "compliance_level"]
            }
        }
    }
    
    jsonschema.validate(self.config, schema)
```

## Environment-Specific Configuration

### Development Environment
```bash
# .env.development
MCP_ENV=development
LOG_LEVEL=DEBUG
DATABASE_TYPE=sqlite
CACHE_TYPE=memory
GOVERNANCE_MODE=proactive
COMPLIANCE_LEVEL=0.80
DEBUG=true
```

### Production Environment
```bash
# .env.production
MCP_ENV=production
LOG_LEVEL=WARNING
DATABASE_TYPE=postgresql
DB_HOST=db.production.internal
DB_PASSWORD=<from-secrets-manager>
CACHE_TYPE=redis
REDIS_HOST=redis.production.internal
GOVERNANCE_MODE=strict
COMPLIANCE_LEVEL=0.99
DEBUG=false
```

### Testing Environment
```bash
# .env.test
MCP_ENV=test
LOG_LEVEL=ERROR
DATABASE_TYPE=sqlite
SQLITE_PATH=:memory:
CACHE_TYPE=memory
GOVERNANCE_MODE=permissive
COMPLIANCE_LEVEL=0.50
```

## Runtime Configuration

### Configuration API
```python
@app.put("/config")
async def update_config(
    section: str,
    key: str,
    value: Any,
    auth: str = Header(...)
):
    """Update configuration at runtime."""
    if not is_safe_to_update(section, key):
        raise HTTPException(400, "Cannot update this config at runtime")
    
    config.update(section, key, value)
    await config.persist()
    
    # Trigger reload in affected components
    await notify_config_change(section, key, value)
    
    return {"status": "updated", "section": section, "key": key}
```

### Safe Runtime Updates
```python
RUNTIME_SAFE_CONFIGS = {
    "governance.compliance_level",
    "cache.ttl",
    "performance.max_concurrent_consultations",
    "logging.level"
}

RUNTIME_UNSAFE_CONFIGS = {
    "database.*",  # Database changes require restart
    "port.*",      # Port changes require restart
    "server.name"  # Identity changes require restart
}
```

## Configuration Best Practices

### 1. Never Store Secrets in Config Files
```yaml
# Bad
database:
  password: "my-secret-password"

# Good
database:
  password: ${DB_PASSWORD}  # From environment/secrets manager
```

### 2. Use Descriptive Environment Variables
```yaml
# Bad
port: ${P}

# Good
port: ${MCP_GOVERNANCE_PORT}
```

### 3. Provide Sensible Defaults
```yaml
# Good - works without configuration
cache:
  ttl: ${CACHE_TTL:300}  # Default 5 minutes
  
# Bad - requires configuration
cache:
  ttl: ${CACHE_TTL}  # Fails if not set
```

### 4. Validate Early
```python
# Validate on startup
def __init__(self):
    self.config = load_config()
    self.validate_config()  # Fail fast
```

### 5. Document Configuration
```yaml
governance:
  # Controls how strictly governance rules are enforced
  # Range: 0.0 (permissive) to 1.0 (strict)
  # Recommended: 0.95 for production
  compliance_level: ${COMPLIANCE_LEVEL:0.95}
```

## Configuration Deployment

### Local Development
```bash
# Use .env file
cp .env.example .env
vim .env  # Edit as needed

# Or export directly
export MCP_ENV=development
export LOG_LEVEL=DEBUG

# Start with config
python -m apps.api.mcp.governance_server --config mcp_config.yaml
```

### Docker Deployment
```dockerfile
FROM python:3.10

# Copy configuration
COPY mcp_config.yaml /app/config/
COPY .env.production /app/.env

# Use environment variables
ENV MCP_ENV=production
ENV CONFIG_PATH=/app/config/mcp_config.yaml

# Start server
CMD ["python", "-m", "apps.api.mcp.governance_server"]
```

### Kubernetes Deployment
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-config
data:
  mcp_config.yaml: |
    server:
      name: governance-intelligence
      environment: production
---
apiVersion: v1
kind: Secret
metadata:
  name: mcp-secrets
data:
  DB_PASSWORD: <base64-encoded>
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: mcp-server
        envFrom:
        - secretRef:
            name: mcp-secrets
        - configMapRef:
            name: mcp-config
```

## Monitoring Configuration

### Configuration Metrics
```python
config_metrics = {
    "config_loads_total": 100,
    "config_load_failures": 2,
    "config_updates_total": 10,
    "config_validation_errors": 1,
    "env_vars_missing": 0,
    "runtime_updates": 5
}
```

### Health Checks
```python
@app.get("/health/config")
async def config_health():
    """Check configuration health."""
    issues = []
    
    # Check required env vars
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            issues.append(f"Missing required env var: {var}")
    
    # Validate current config
    try:
        validate_config(current_config)
    except ValidationError as e:
        issues.append(f"Invalid config: {e}")
    
    if issues:
        return {"status": "unhealthy", "issues": issues}
    return {"status": "healthy"}
```

## Troubleshooting

### Configuration Not Loading
```bash
# Check file exists
ls -la mcp_config.yaml

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('mcp_config.yaml'))"

# Check environment variables
env | grep MCP_

# Enable debug logging
export LOG_LEVEL=DEBUG
python -m apps.api.mcp.governance_server
```

### Environment Variables Not Substituting
```bash
# Check variable is exported
echo $MCP_PORT

# Ensure variable is in environment
export MCP_PORT=8001

# Check for typos in variable names
grep -r "MCP_PORT" *.yaml
```

### Validation Errors
```python
# Test configuration
python -c "
from apps.api.mcp.config_loader import ConfigLoader
config = ConfigLoader('mcp_config.yaml')
print('Config valid!')
"
```

## Security Considerations

### Secrets Management
1. Never commit secrets to version control
2. Use environment variables for sensitive data
3. Consider secrets management tools (Vault, AWS Secrets Manager)
4. Rotate secrets regularly
5. Audit secret access

### Configuration Access Control
1. Restrict configuration file permissions
2. Use RBAC for runtime configuration API
3. Audit configuration changes
4. Validate all configuration inputs
5. Sanitize configuration values

## Future Enhancements

### Phase 3 Improvements
- Dynamic configuration from database
- Configuration versioning and rollback
- A/B testing configuration variants

### Phase 4 Improvements
- Distributed configuration with etcd/Consul
- Configuration encryption at rest
- Automatic configuration optimization

### Long-term Vision
- AI-driven configuration tuning
- Self-healing configuration
- Cross-project configuration sharing

## References

- [12-Factor App Configuration](https://12factor.net/config)
- [Configuration Best Practices](https://docs.python.org/3/library/configparser.html)
- [Environment Variables](https://docs.python.org/3/library/os.html#os.environ)
- [YAML Specification](https://yaml.org/spec/)

---

**Reviewed By:** Alex Novak, Dr. Sarah Chen  
**Last Updated:** 2025-01-06  
**Next Review:** Post Phase MCP-003 Implementation