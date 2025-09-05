# Governance Hooks and MCP Server Implementation

This guide implements governance hooks and MCP server integration with your existing FastAPI backend, leveraging current port discovery, database, cache, and persona systems.

## Architecture Overview

```
Claude Code CLI
    ↓ (hooks)
Native Hooks → Bridge Scripts → Your Governance System
    ↓ (mcp)
MCP Server → FastAPI Backend → Database/Cache/Personas
```

## 1. Governance Hook Bridge System

### Hook Bridge Architecture

Your governance system already has `RuntimeGovernanceSystem` - we create bridge scripts that connect Claude Code hooks to it.

```python
# ai-assistant/backend/hooks/governance_bridge.py
import asyncio
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from governance.core.runtime_governance import RuntimeGovernanceSystem
from database_manager import DatabaseManager
from cache_manager import IntelligentCache

class GovernanceHookBridge:
    def __init__(self):
        self.governance = RuntimeGovernanceSystem()
        self.db = DatabaseManager()
        self.cache = IntelligentCache()
    
    async def validate_operation(self, claude_data: dict) -> int:
        """Bridge Claude Code data to governance system"""
        # Map Claude Code events to governance events
        operation_map = {
            "Bash": "command_execution",
            "Edit": "file_modification", 
            "Write": "file_creation",
            "Read": "file_access"
        }
        
        tool_name = claude_data.get('tool_name')
        operation_type = operation_map.get(tool_name, 'unknown')
        
        # Use existing governance validation
        result = await self.governance.validate_operation(operation_type, {
            "tool": tool_name,
            "parameters": claude_data.get('parameters', {}),
            "file_paths": claude_data.get('file_paths', []),
            "session_id": claude_data.get('session_id')
        })
        
        # Log to database
        await self._audit_decision(claude_data, result)
        
        return 0 if result.approved else 2
    
    async def _audit_decision(self, claude_data, result):
        """Audit decisions using existing database"""
        audit_data = {
            "operation_type": claude_data.get('tool_name'),
            "decision": result.decision,
            "risk_level": result.risk_level,
            "session_id": claude_data.get('session_id'),
            "timestamp": datetime.utcnow()
        }
        
        await self.db.execute(
            "INSERT INTO governance_audit (data) VALUES (%s)",
            [json.dumps(audit_data)]
        )

async def main():
    bridge = GovernanceHookBridge()
    claude_data = json.loads(sys.stdin.read())
    exit_code = await bridge.validate_operation(claude_data)
    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())
```

**Reasoning**: Reuses your existing `RuntimeGovernanceSystem` instead of rebuilding. Maps Claude Code tool types to your governance operations.

### Hook Scripts

```bash
#!/bin/bash
# ai-assistant/backend/hooks/pre_tool_hook.sh
python -m ai_assistant.backend.hooks.governance_bridge
```

```bash
#!/bin/bash  
# ai-assistant/backend/hooks/post_tool_hook.sh
python -c "
import asyncio
import json
import sys
from ai_assistant.backend.hooks.governance_bridge import GovernanceHookBridge

async def post_audit():
    bridge = GovernanceHookBridge()
    claude_data = json.loads(sys.stdin.read())
    await bridge._audit_decision(claude_data, {'decision': 'completed'})

asyncio.run(post_audit())
"
```

**Reasoning**: Minimal shell scripts that call your Python governance system. Pre-hook blocks, post-hook audits.

## 2. MCP Server Implementation

### Core MCP Server

```python
# ai-assistant/backend/mcp/governance_mcp_server.py
import asyncio
from mcp import Server
from mcp.server.models import InitializationOptions
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from governance.core.runtime_governance import RuntimeGovernanceSystem
from persona_manager import PersonaManager
from database_manager import DatabaseManager
from cache_manager import IntelligentCache
from core.port_discovery import discover_backend_port

class GovernanceMCPServer:
    def __init__(self):
        self.server = Server("governance-server")
        self.port = discover_backend_port("mcp-governance")
        
        # Use existing system components
        self.governance = RuntimeGovernanceSystem()
        self.personas = PersonaManager()
        self.db = DatabaseManager()
        self.cache = IntelligentCache()
        
        self._setup_tools()
    
    def _setup_tools(self):
        """Register MCP tools using existing systems"""
        self.server.register_tool("validate_code", self._validate_code)
        self.server.register_tool("consult_persona", self._consult_persona)
        self.server.register_tool("get_best_practices", self._get_best_practices)
        self.server.register_tool("check_governance_status", self._governance_status)
    
    async def _validate_code(self, code: str, file_path: str, context: dict = None) -> dict:
        """Validate code using existing governance system"""
        cache_key = f"validate:{hash(code + file_path)}"
        
        # Check cache first
        cached = await self.cache.get_hot(cache_key)
        if cached:
            return cached
        
        # Use existing governance validation
        result = await self.governance.validate_operation("code_validation", {
            "code": code,
            "file_path": file_path,
            "context": context or {}
        })
        
        response = {
            "approved": result.approved,
            "risk_level": result.risk_level,
            "violations": result.violations,
            "recommendations": result.recommendations,
            "confidence": result.confidence
        }
        
        # Cache result
        await self.cache.set_hot(cache_key, response, ttl=3600)
        return response
    
    async def _consult_persona(self, persona_name: str, question: str, context: dict = None) -> dict:
        """Consult persona using existing PersonaManager"""
        valid_personas = ["sarah_chen", "marcus_rodriguez", "emily_watson", "rachel_torres"]
        
        if persona_name not in valid_personas:
            return {"error": f"Invalid persona. Available: {valid_personas}"}
        
        # Use existing persona system
        result = await self.personas.consult_persona(persona_name, question, context or {})
        
        return {
            "persona": persona_name,
            "response": result.get("response", ""),
            "confidence": result.get("confidence", 0.0),
            "reasoning": result.get("reasoning", ""),
            "recommendations": result.get("recommendations", [])
        }
    
    async def _get_best_practices(self, domain: str, technology: str = None) -> dict:
        """Get best practices from database and personas"""
        cache_key = f"practices:{domain}:{technology or 'general'}"
        
        cached = await self.cache.get_warm(cache_key)
        if cached:
            return cached
        
        # Query existing database
        practices = await self.db.execute("""
            SELECT practice_name, description, success_rate 
            FROM best_practices 
            WHERE domain = %s AND (technology = %s OR technology IS NULL)
            ORDER BY success_rate DESC
        """, [domain, technology])
        
        # Get Sarah's technical perspective
        sarah_advice = await self._consult_persona("sarah_chen", 
            f"What are best practices for {domain} with {technology or 'any technology'}?")
        
        result = {
            "domain": domain,
            "technology": technology,
            "database_practices": practices,
            "expert_advice": sarah_advice,
            "combined_score": len(practices) + (sarah_advice.get("confidence", 0) * 10)
        }
        
        await self.cache.set_warm(cache_key, result, ttl=7200)
        return result
    
    async def _governance_status(self) -> dict:
        """Get governance system status"""
        return {
            "governance_active": True,
            "database_connected": self.db.is_connected(),
            "cache_stats": await self.cache.get_metrics(),
            "personas_available": list(self.personas.personas.keys()),
            "port": self.port
        }

async def main():
    server = GovernanceMCPServer()
    await server.server.serve_stdio()

if __name__ == "__main__":
    asyncio.run(main())
```

**Reasoning**: Reuses all existing components (governance, personas, database, cache) instead of rebuilding. Uses port discovery for dynamic allocation. Caches MCP responses for performance.

### MCP Launcher Module

```python
# ai-assistant/backend/mcp/__main__.py
import asyncio
from .governance_mcp_server import main

if __name__ == "__main__":
    asyncio.run(main())
```

## 3. Integration with Existing FastAPI

### Update Main Backend

```python
# Add to ai-assistant/backend/main.py
@self.app.on_event("startup")
async def startup_event():
    # ... existing initialization ...
    
    # Initialize governance MCP server
    await self._setup_mcp_server()
    
async def _setup_mcp_server(self):
    """Setup MCP server with port discovery"""
    from mcp.governance_mcp_server import GovernanceMCPServer
    
    self.mcp_server = GovernanceMCPServer()
    
    # Start MCP server as background task
    self.mcp_task = asyncio.create_task(self.mcp_server.server.serve_stdio())
    
    # Update shared configuration
    await self._update_mcp_config()
    
async def _update_mcp_config(self):
    """Update .mcp.json with discovered port"""
    config = {
        "servers": {
            "governance": {
                "command": "python",
                "args": ["-m", "ai_assistant.backend.mcp"],
                "env": {
                    "PYTHONPATH": ".",
                    "DATABASE_URL": os.getenv("DATABASE_URL"),
                    "CACHE_ENABLED": "true"
                }
            }
        }
    }
    
    with open(".mcp.json", "w") as f:
        json.dump(config, f, indent=2)

# Add MCP status endpoint
@self.app.get("/mcp/status")
async def mcp_status():
    """Get MCP server status"""
    if hasattr(self, 'mcp_server'):
        return await self.mcp_server._governance_status()
    return {"error": "MCP server not initialized"}
```

## 4. Configuration Setup

### Enterprise Policies

```json
# /etc/claude-code/managed-settings.json
{
  "permissions": {
    "allowList": [
      "Bash(npm run test:*)",
      "Edit(src/**/*.{js,ts,py})",
      "Write(docs/**/*.md)"
    ],
    "denyList": [
      "Bash(rm -rf *)",
      "Write(.env*)"
    ]
  },
  "hooks": {
    "PreToolUse": "/path/to/ai-assistant/backend/hooks/pre_tool_hook.sh",
    "PostToolUse": "/path/to/ai-assistant/backend/hooks/post_tool_hook.sh"
  },
  "environmentVariables": {
    "GOVERNANCE_API_URL": "http://localhost:8001",
    "GOVERNANCE_MODE": "enterprise"
  }
}
```

### Project MCP Config

```json
# .mcp.json (auto-generated)
{
  "servers": {
    "governance": {
      "command": "python",
      "args": ["-m", "ai_assistant.backend.mcp"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## 5. Implementation Steps

### Step 1: Create Hook Bridge

```bash
mkdir -p ai-assistant/backend/hooks
# Create governance_bridge.py and hook scripts
chmod +x ai-assistant/backend/hooks/*.sh
```

### Step 2: Create MCP Module

```bash
mkdir -p ai-assistant/backend/mcp
# Create governance_mcp_server.py and __main__.py
```

### Step 3: Install Enterprise Policies

```bash
# Linux
sudo mkdir -p /etc/claude-code
sudo cp managed-settings.json /etc/claude-code/

# Update hook paths in managed-settings.json
```

### Step 4: Test Integration

```bash
# Start your existing backend
cd ai-assistant/backend  
python main.py

# Test MCP server
python -m mcp.governance_mcp_server

# Test hooks
echo '{"tool_name":"Edit","parameters":{},"session_id":"test"}' | python hooks/governance_bridge.py
```

## 6. Usage Examples

### Claude Code Commands

```bash
# Claude will automatically consult your governance system
claude "Please validate this code change"

# Claude can consult your personas directly  
claude "Ask Sarah Chen about this caching strategy"

# All operations are logged in your database
claude "Edit this file" # → Pre-hook validates → Post-hook audits
```

### MCP Tool Usage

Claude Code can now:
- `validate_code` - Uses your governance engine
- `consult_persona` - Talks to Sarah, Marcus, Emily, Rachel
- `get_best_practices` - Queries your database + personas
- `check_governance_status` - Shows system health

## Benefits

1. **Reuses Existing System**: Leverages your FastAPI, database, cache, personas
2. **Port Discovery**: Dynamic port allocation using your existing system
3. **Performance**: Caches MCP responses, uses existing cache system
4. **Audit Trail**: All decisions logged in your database
5. **Minimal Changes**: Extends rather than replaces current architecture

This implementation connects Claude Code to your governance system through both hooks (mandatory enforcement) and MCP (intelligent consultation) while preserving your existing architecture.