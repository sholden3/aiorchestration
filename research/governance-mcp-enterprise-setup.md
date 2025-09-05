# Enterprise MCP Server Setup Guide

Complete setup guide for integrating your governance system with Claude Code through MCP servers and enterprise managed policies.

## Prerequisites

- Your governance system deployed and running
- Backend API accessible at `http://localhost:8001`
- Database and cache systems operational
- Claude Code CLI installed

## 1. MCP Server Implementation

### Create MCP Server Module

```bash
# Create MCP server directory
mkdir -p governance/mcp
touch governance/mcp/__init__.py
```

### Core MCP Server

```python
# governance/mcp/governance_server.py
import asyncio
import json
import sys
from mcp import Server
from mcp.server.models import InitializationOptions
from pathlib import Path

# Import your governance components
sys.path.append(str(Path(__file__).parent.parent.parent))
from governance.core.runtime_governance import RuntimeGovernanceSystem
from governance.personas.persona_manager import PersonaManager
from ai_assistant.backend.database_manager import DatabaseManager
from ai_assistant.backend.cache_manager import CacheManager

class GovernanceServer:
    def __init__(self):
        self.server = Server("governance-server")
        self.governance = RuntimeGovernanceSystem()
        self.personas = PersonaManager()
        self.db = DatabaseManager()
        self.cache = CacheManager()
        self._setup_tools()
    
    def _setup_tools(self):
        """Register all governance tools"""
        self.server.register_tool("validate_operation", self._validate_operation)
        self.server.register_tool("consult_persona", self._consult_persona)
        self.server.register_tool("check_best_practices", self._check_best_practices)
        self.server.register_tool("audit_decision", self._audit_decision)
        self.server.register_tool("get_governance_rules", self._get_governance_rules)
        self.server.register_tool("analyze_risk", self._analyze_risk)
    
    async def _validate_operation(self, operation: str, context: dict) -> dict:
        """Validate operation against governance rules"""
        # Log the validation request
        await self._log_governance_action("validate_operation", {
            "operation": operation,
            "context": context
        })
        
        # Use your existing governance validation
        result = await self.governance.validate_operation(operation, context)
        
        return {
            "approved": result.approved,
            "risk_level": result.risk_level,
            "reason": result.reason,
            "recommendations": result.recommendations,
            "audit_id": result.audit_id
        }
    
    async def _consult_persona(self, persona_name: str, question: str, context: dict = None) -> dict:
        """Consult specific persona for guidance"""
        # Validate persona exists
        if persona_name not in ["sarah_chen", "marcus_rodriguez", "emily_watson", "rachel_torres"]:
            return {"error": f"Unknown persona: {persona_name}"}
        
        # Log consultation request
        await self._log_governance_action("consult_persona", {
            "persona": persona_name,
            "question": question[:100]  # Truncate for logs
        })
        
        # Get persona consultation
        result = await self.personas.consult_persona(persona_name, question, context or {})
        
        return {
            "persona": persona_name,
            "guidance": result.guidance,
            "confidence": result.confidence,
            "evidence": result.evidence,
            "recommendations": result.recommendations
        }
    
    async def _check_best_practices(self, technology: str, context: dict = None) -> dict:
        """Get best practices from database and personas"""
        # Check cache first
        cache_key = f"best_practices:{technology}"
        cached = await self.cache.get_warm(cache_key)
        if cached:
            return cached
        
        # Query database for practices
        practices = await self.db.execute("""
            SELECT practice_name, description, success_rate 
            FROM best_practices 
            WHERE technology = %s 
            ORDER BY success_rate DESC
        """, [technology])
        
        # Get persona recommendations
        sarah_advice = await self.personas.consult_persona("sarah_chen", 
            f"What are the best practices for {technology}?", context or {})
        
        result = {
            "technology": technology,
            "database_practices": practices,
            "expert_advice": sarah_advice.guidance,
            "combined_recommendations": self._combine_practices(practices, sarah_advice)
        }
        
        # Cache result
        await self.cache.set_warm(cache_key, result, ttl=3600)
        return result
    
    async def _audit_decision(self, decision_type: str, decision_data: dict) -> dict:
        """Audit and log governance decisions"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "decision_type": decision_type,
            "decision_data": decision_data,
            "correlation_id": str(uuid.uuid4())
        }
        
        # Store in database
        await self.db.execute("""
            INSERT INTO governance_audit (decision_type, decision_data, correlation_id, created_at)
            VALUES (%s, %s, %s, %s)
        """, [decision_type, json.dumps(decision_data), audit_entry["correlation_id"], audit_entry["timestamp"]])
        
        return audit_entry
    
    async def _log_governance_action(self, action: str, data: dict):
        """Log all governance actions for audit trail"""
        await self.db.execute("""
            INSERT INTO governance_actions (action_type, action_data, timestamp)
            VALUES (%s, %s, NOW())
        """, [action, json.dumps(data)])

async def main():
    """Start the MCP server"""
    server = GovernanceServer()
    await server.server.serve_stdio()

if __name__ == "__main__":
    asyncio.run(main())
```

### MCP Server Launcher

```python
# governance/mcp/__main__.py
import asyncio
from .governance_server import main

if __name__ == "__main__":
    asyncio.run(main())
```

## 2. Enterprise Managed Policy Setup

### Create Enterprise Policy Directory

```bash
# Linux
sudo mkdir -p /etc/claude-code
# macOS  
sudo mkdir -p "/Library/Application Support/ClaudeCode"
```

### Enterprise Policy Configuration

```json
# /etc/claude-code/managed-settings.json (Linux)
# /Library/Application Support/ClaudeCode/managed-settings.json (macOS)
{
  "version": "1.0",
  "organization": "Your Organization",
  "permissions": {
    "allowList": [
      "Bash(npm run test:*)",
      "Bash(npm run build:*)",
      "Bash(git status)",
      "Bash(git add *)",
      "Bash(git commit -m *)",
      "Edit(src/**/*.{js,ts,py,md})",
      "Write(src/**/*.{js,ts,py})",
      "Write(docs/**/*.md)",
      "Read(**/package.json)",
      "Read(**/requirements.txt)"
    ],
    "denyList": [
      "Bash(rm -rf *)",
      "Bash(*sudo*)",
      "Bash(*chmod 777*)",
      "Write(.env*)",
      "Write(config/production.*)",
      "Edit(.git/*)",
      "Bash(curl *|bash)",
      "Bash(wget *|bash)"
    ]
  },
  "hooks": {
    "PreToolUse": "/path/to/your/governance/hooks/enterprise_pre_hook.sh",
    "PostToolUse": "/path/to/your/governance/hooks/enterprise_post_hook.sh",
    "SessionStart": "/path/to/your/governance/hooks/session_start_hook.sh"
  },
  "environmentVariables": {
    "GOVERNANCE_API_URL": "http://localhost:8001",
    "GOVERNANCE_MODE": "enterprise",
    "GOVERNANCE_AUDIT_LEVEL": "full",
    "CLAUDE_PROJECT_DIR": "${workspaceRoot}"
  },
  "mcp": {
    "servers": {
      "governance": {
        "command": "python",
        "args": ["-m", "governance.mcp"],
        "env": {
          "GOVERNANCE_CONFIG": "/path/to/governance/config.json"
        }
      }
    }
  },
  "settings": {
    "requireConfirmation": ["Bash(*rm*)", "Write(.env*)"],
    "autoApprove": ["Read(*)", "Bash(git status)"],
    "maxConcurrentOperations": 5
  }
}
```

## 3. Hook Scripts Implementation

### Pre-Tool Hook

```bash
#!/bin/bash
# governance/hooks/enterprise_pre_hook.sh
set -euo pipefail

# Governance protocol: Log all operations
echo "[$(date -Iseconds)] GOVERNANCE: Pre-tool validation started" >> /var/log/governance.log

# Set environment variables
export GOVERNANCE_ENTERPRISE=true
export GOVERNANCE_HOOK_TYPE="PreToolUse"

# Read Claude Code data from stdin
CLAUDE_DATA=$(cat)

# Call your governance system
RESULT=$(python3 -c "
import sys
import json
import asyncio
from governance.bridge.enterprise_bridge import enterprise_validate

async def main():
    claude_data = json.loads('''$CLAUDE_DATA''')
    result = await enterprise_validate(claude_data)
    print(result)

asyncio.run(main())
")

# Log result
echo "[$(date -Iseconds)] GOVERNANCE: Pre-tool result: $RESULT" >> /var/log/governance.log

# Exit with governance decision (0=allow, 2=block)
exit $RESULT
```

### Post-Tool Hook

```bash
#!/bin/bash
# governance/hooks/enterprise_post_hook.sh
set -euo pipefail

# Governance protocol: Audit completed operations
echo "[$(date -Iseconds)] GOVERNANCE: Post-tool audit started" >> /var/log/governance.log

# Read Claude Code data from stdin
CLAUDE_DATA=$(cat)

# Audit the completed operation
python3 -c "
import sys
import json
import asyncio
from governance.bridge.enterprise_bridge import audit_completed_operation

async def main():
    claude_data = json.loads('''$CLAUDE_DATA''')
    await audit_completed_operation(claude_data)

asyncio.run(main())
"

echo "[$(date -Iseconds)] GOVERNANCE: Post-tool audit completed" >> /var/log/governance.log
exit 0
```

### Session Start Hook

```bash
#!/bin/bash
# governance/hooks/session_start_hook.sh
set -euo pipefail

# Governance protocol: Initialize session governance
echo "[$(date -Iseconds)] GOVERNANCE: Session started with enterprise governance" >> /var/log/governance.log

# Initialize governance session
python3 -c "
import asyncio
from governance.core.session_manager import SessionManager

async def main():
    session_manager = SessionManager()
    await session_manager.initialize_enterprise_session()

asyncio.run(main())
"

# Output governance rules for Claude's context
cat << EOF
# Enterprise Governance Active

Your actions are governed by enterprise policies. Key rules:
- All code changes require validation
- Security-sensitive operations need approval  
- Audit trail maintained for all actions
- Personas available for consultation: Sarah Chen (Performance), Marcus Rodriguez (Security), Emily Watson (UX), Rachel Torres (Business)

Use the governance MCP server for guidance: consult_persona, validate_operation, check_best_practices
EOF

exit 0
```

## 4. Enterprise Bridge Implementation

```python
# governance/bridge/enterprise_bridge.py
import asyncio
import json
import logging
from typing import Dict, Any
from governance.core.runtime_governance import RuntimeGovernanceSystem
from governance.core.audit_logger import AuditLogger

# Initialize components
governance = RuntimeGovernanceSystem()
audit_logger = AuditLogger()
logger = logging.getLogger(__name__)

async def enterprise_validate(claude_data: Dict[str, Any]) -> int:
    """Enterprise validation with full governance"""
    try:
        # Extract operation details
        tool_name = claude_data.get('tool_name')
        parameters = claude_data.get('parameters', {})
        file_paths = claude_data.get('file_paths', [])
        
        # Log validation request
        await audit_logger.log_enterprise_action({
            "action": "pre_validate",
            "tool": tool_name,
            "file_paths": file_paths,
            "session_id": claude_data.get('session_id')
        })
        
        # Run enterprise governance validation
        result = await governance.enterprise_validate(
            tool_name=tool_name,
            parameters=parameters,
            file_paths=file_paths,
            context=claude_data
        )
        
        # Log decision
        await audit_logger.log_governance_decision(result)
        
        # Return exit code
        return 0 if result.approved else 2
        
    except Exception as e:
        logger.error(f"Enterprise validation failed: {e}")
        await audit_logger.log_error("enterprise_validation_error", str(e))
        return 2  # Block on error

async def audit_completed_operation(claude_data: Dict[str, Any]):
    """Audit completed operations"""
    try:
        # Log completion
        await audit_logger.log_enterprise_action({
            "action": "post_audit",
            "tool": claude_data.get('tool_name'),
            "success": claude_data.get('success', False),
            "output_size": len(str(claude_data.get('output', ''))),
            "session_id": claude_data.get('session_id')
        })
        
        # Update metrics
        await governance.update_usage_metrics(claude_data)
        
    except Exception as e:
        logger.error(f"Post-operation audit failed: {e}")
```

## 5. Project Configuration

### Claude Code MCP Configuration

```json
# .mcp.json (project root)
{
  "servers": {
    "governance": {
      "command": "python",
      "args": ["-m", "governance.mcp"],
      "env": {
        "GOVERNANCE_CONFIG": "./governance/config/governance_config.json",
        "DATABASE_URL": "postgresql://localhost:5432/governance",
        "CACHE_URL": "redis://localhost:6379"
      }
    }
  }
}
```

### Governance Configuration

```json
# governance/config/governance_config.json
{
  "enterprise_mode": true,
  "audit_level": "full",
  "personas": {
    "sarah_chen": {
      "domain": "performance",
      "decision_weight": 0.3
    },
    "marcus_rodriguez": {
      "domain": "security", 
      "decision_weight": 0.3
    },
    "emily_watson": {
      "domain": "ux",
      "decision_weight": 0.2
    },
    "rachel_torres": {
      "domain": "business",
      "decision_weight": 0.2
    }
  },
  "validation_rules": {
    "require_persona_consensus": true,
    "minimum_confidence": 0.8,
    "block_on_security_risk": true
  }
}
```

## 6. Installation and Startup

### Make Hook Scripts Executable

```bash
chmod +x governance/hooks/*.sh
```

### Install MCP Server

```bash
# In your project root
pip install -e .  # Install your governance package
```

### Start Backend Services

```bash
# Start your backend API
cd ai-assistant/backend
python main.py

# Verify governance is loaded
curl http://localhost:8001/health
```

### Test MCP Server

```bash
# Test MCP server directly
python -m governance.mcp
```

### Verify Enterprise Policies

```bash
# Check policies are loaded (will vary by OS)
# Linux
ls -la /etc/claude-code/
# macOS
ls -la "/Library/Application Support/ClaudeCode/"
```

## 7. Usage Protocol

### Starting Claude Code Session

1. Navigate to your project directory
2. Run `claude` - enterprise policies auto-load
3. Session start hook initializes governance
4. All operations now validated through your system

### Using Governance Tools

```bash
# Ask Claude to consult your personas
"Please consult Sarah Chen about the performance implications of this caching strategy"

# Request validation
"Please validate this database schema change using our governance system"

# Get best practices
"What are our enterprise best practices for React component structure?"
```

## 8. Monitoring and Logs

### View Governance Logs

```bash
tail -f /var/log/governance.log
```

### Database Audit Trail

```sql
SELECT * FROM governance_audit ORDER BY created_at DESC LIMIT 10;
SELECT * FROM governance_actions WHERE action_type = 'pre_validate' ORDER BY timestamp DESC;
```

### Monitor MCP Server

```bash
# Check MCP server status
ps aux | grep governance.mcp
```

## 9. Troubleshooting

### Common Issues

1. **MCP Server Not Found**
   - Verify `.mcp.json` in project root
   - Check Python path includes governance module

2. **Hooks Not Executing**
   - Verify executable permissions
   - Check hook script paths in enterprise policy

3. **Database Connection Errors**
   - Verify database is running
   - Check connection string in config

4. **Permission Denied**
   - Verify enterprise policy file permissions
   - Check hook script execution permissions

### Debug Mode

```bash
# Enable debug logging
export GOVERNANCE_DEBUG=true
export CLAUDE_CODE_DEBUG=true
claude
```

## 10. Governance Compliance Checklist

- [ ] Enterprise policies installed system-wide
- [ ] All hook scripts executable and tested
- [ ] MCP server responds to test queries
- [ ] Audit logging operational
- [ ] Database storing governance decisions
- [ ] Personas accessible through MCP
- [ ] Session initialization working
- [ ] No governance bypass mechanisms enabled
- [ ] Monitoring logs active
- [ ] Rollback procedures documented

Your governance system is now fully integrated with Claude Code through both enterprise policies and intelligent MCP server capabilities.