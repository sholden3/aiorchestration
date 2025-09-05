# Enterprise Managed Policies Implementation Guide

**Version:** 1.0  
**Date:** January 2025  
**Status:** Implementation Ready  
**Authors:** AI Governance Team  

---

## Executive Summary

This document outlines the integration of our existing AI Governance System with Claude Code's Enterprise Managed Policies. This integration transforms our governance from project-level guidance to enterprise-wide enforcement, providing unoverridable policies across all development teams while leveraging our sophisticated persona-based validation system.

**Key Benefits:**
- Unoverridable security policies across all Claude Code instances
- Centralized governance leveraging our existing persona system
- Complete audit trails for enterprise compliance
- Zero additional infrastructure requirements

---

## 1. Architecture Overview

### Current System Integration
Our existing governance system components integrate seamlessly:
- **Runtime Governance System** → Enterprise validation engine
- **Persona Manager** → Expert consultation for policy decisions  
- **Database Manager** → Historical context and audit logging
- **Cache Manager** → Performance optimization for policy checks
- **MCP Server** → Real-time governance consultation

### Policy Hierarchy
```
Enterprise Managed Policies (Unoverridable)
    ↓
Project-Level Policies (.claude/settings.json)
    ↓
User-Level Policies (~/.claude/settings.json)
    ↓
CLI Flags (can be disabled by enterprise policies)
```

---

## 2. Implementation Steps

### Step 1: Create Enterprise Policy Configuration

**File Location:** `/etc/claude-code/managed-settings.json` (Linux) or `/Library/Application Support/ClaudeCode/managed-settings.json` (macOS)

```json
{
  "version": "1.0",
  "organization": "YOUR_ORGANIZATION",
  "enforced_at": "2025-01-27T00:00:00Z",
  "permissions": {
    "allowList": [
      "Bash(npm run {test,build,typecheck}:*)",
      "Bash(git {status,diff,log,add,commit,push})",
      "Edit(src/**/*.{js,ts,py,md})",
      "Write(src/**/*.{js,ts,py})",
      "Write(docs/**/*.md)",
      "Read(**/*.{json,yml,yaml,toml,md})",
      "mcp__governance-server__*"
    ],
    "denyList": [
      "Bash(*rm -rf*)",
      "Bash(*sudo*)",
      "Bash(*chmod 777*)",
      "Write(.env*)",
      "Write(config/production*)",
      "Bash(*npm publish*)",
      "Bash(*docker run --privileged*)"
    ],
    "conditionalRules": [
      {
        "condition": "file_path.endsWith('.py')",
        "allow": ["Bash(python -m pytest *)"],
        "require_validation": true
      }
    ]
  },
  "hooks": {
    "PreToolUse": "/opt/governance/hooks/enterprise_pre_validation.sh",
    "PostToolUse": "/opt/governance/hooks/enterprise_post_audit.sh",
    "UserPromptSubmit": "/opt/governance/hooks/enterprise_context_injection.sh"
  },
  "environmentVariables": {
    "GOVERNANCE_MODE": "enterprise",
    "GOVERNANCE_API_URL": "http://localhost:8001",
    "ENTERPRISE_AUDIT_ENABLED": "true",
    "GOVERNANCE_REQUIRE_CONSENSUS": "true"
  },
  "mcp": {
    "servers": {
      "governance-server": {
        "command": "python",
        "args": ["-m", "governance.mcp.enterprise_governance_server"],
        "env": {
          "GOVERNANCE_CONFIG_PATH": "/opt/governance/config",
          "ENTERPRISE_MODE": "true"
        }
      }
    }
  },
  "settings": {
    "dangerouslySkipPermissions": false,
    "maxConcurrentSessions": 3,
    "sessionTimeout": 3600,
    "auditLevel": "comprehensive"
  }
}
```

### Step 2: Create Enterprise Hook Scripts

**Pre-validation Hook:**
```bash
#!/bin/bash
# /opt/governance/hooks/enterprise_pre_validation.sh

set -euo pipefail

# Set governance context
export GOVERNANCE_MODE="enterprise"
export HOOK_TYPE="PreToolUse"

# Call our governance system
exec python -m governance.bridge.enterprise_bridge \
    --action="pre_validate" \
    --data="$(cat)" \
    --context="${CLAUDE_TOOL_NAME:-unknown}" \
    --session="${CLAUDE_SESSION_ID:-unknown}"
```

**Post-audit Hook:**
```bash
#!/bin/bash
# /opt/governance/hooks/enterprise_post_audit.sh

set -euo pipefail

export GOVERNANCE_MODE="enterprise"
export HOOK_TYPE="PostToolUse"

exec python -m governance.bridge.enterprise_bridge \
    --action="post_audit" \
    --data="$(cat)" \
    --context="${CLAUDE_TOOL_NAME:-unknown}" \
    --session="${CLAUDE_SESSION_ID:-unknown}"
```

### Step 3: Enterprise Bridge Implementation

```python
# governance/bridge/enterprise_bridge.py
import asyncio
import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any
import logging

from governance.core.runtime_governance import RuntimeGovernanceSystem
from governance.middleware.ai_decision_injector import AIDecisionInjector
from governance.personas.persona_manager import PersonaManager
from governance.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class EnterpriseBridge:
    def __init__(self):
        self.governance = RuntimeGovernanceSystem(
            config_path=Path("/opt/governance/config"),
            enable_monitor=True
        )
        self.personas = PersonaManager()
        self.db = DatabaseManager()
        
    async def pre_validate(self, data: Dict[str, Any], context: str) -> int:
        """Enterprise pre-validation with persona consultation"""
        
        try:
            # Extract Claude Code context
            tool_name = data.get('tool_name', 'unknown')
            parameters = data.get('parameters', {})
            file_paths = data.get('file_paths', [])
            
            # Enterprise validation
            result = await self.governance.enterprise_validate(
                tool_name=tool_name,
                parameters=parameters,
                file_paths=file_paths,
                require_consensus=True
            )
            
            # Audit logging
            await self._log_enterprise_decision(
                action="pre_validate",
                tool_name=tool_name,
                result=result,
                context=context
            )
            
            if result.approved:
                # Inject governance guidance
                if result.recommendations:
                    print(json.dumps({
                        "additionalContext": f"Governance recommendations: {'; '.join(result.recommendations)}"
                    }))
                return 0
            else:
                # Block with detailed reason
                print(f"ENTERPRISE POLICY VIOLATION: {result.reason}", file=sys.stderr)
                if result.recommendations:
                    print(f"Recommendations: {'; '.join(result.recommendations)}", file=sys.stderr)
                return 2
                
        except Exception as e:
            logger.error(f"Enterprise validation error: {e}")
            print(f"GOVERNANCE ERROR: {str(e)}", file=sys.stderr)
            return 2
    
    async def post_audit(self, data: Dict[str, Any], context: str) -> int:
        """Enterprise post-execution audit"""
        
        try:
            tool_name = data.get('tool_name', 'unknown')
            output = data.get('output', '')
            exit_code = data.get('exit_code', 0)
            
            # Post-execution analysis
            audit_result = await self.governance.post_execution_audit(
                tool_name=tool_name,
                output=output,
                exit_code=exit_code,
                enterprise_mode=True
            )
            
            # Store audit trail
            await self._log_enterprise_decision(
                action="post_audit",
                tool_name=tool_name,
                result=audit_result,
                context=context
            )
            
            return 0
            
        except Exception as e:
            logger.error(f"Enterprise audit error: {e}")
            return 0  # Don't block on audit failures
    
    async def _log_enterprise_decision(self, action: str, tool_name: str, 
                                     result: Any, context: str):
        """Log enterprise governance decisions"""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "tool_name": tool_name,
            "approved": getattr(result, 'approved', True),
            "reason": getattr(result, 'reason', ''),
            "risk_level": getattr(result, 'risk_level', 'LOW'),
            "context": context,
            "personas_consulted": getattr(result, 'personas_consulted', []),
            "governance_mode": "enterprise"
        }
        
        await self.db.store_audit_entry(audit_entry)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', required=True)
    parser.add_argument('--data', default='{}')
    parser.add_argument('--context', default='unknown')
    parser.add_argument('--session', default='unknown')
    
    args = parser.parse_args()
    
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError:
        data = {}
    
    bridge = EnterpriseBridge()
    
    if args.action == 'pre_validate':
        exit_code = await bridge.pre_validate(data, args.context)
    elif args.action == 'post_audit':
        exit_code = await bridge.post_audit(data, args.context)
    else:
        exit_code = 1
    
    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 4: Extend Runtime Governance System

```python
# governance/core/runtime_governance.py - Add enterprise methods

async def enterprise_validate(self, tool_name: str, parameters: dict, 
                            file_paths: list, require_consensus: bool = True) -> GovernanceResult:
    """Enterprise-level validation with mandatory persona consultation"""
    
    # Check basic enterprise permissions first
    if not self._check_enterprise_permissions(tool_name, parameters):
        return GovernanceResult(
            approved=False,
            reason="Enterprise permission policy violation",
            risk_level="HIGH"
        )
    
    # Mandatory persona consultation for enterprise mode
    personas_to_consult = self._determine_required_personas(tool_name, parameters)
    
    consensus_results = []
    for persona in personas_to_consult:
        result = await self.persona_manager.consult_persona(
            persona_type=persona,
            scenario={
                "tool_name": tool_name,
                "parameters": parameters,
                "file_paths": file_paths,
                "enterprise_mode": True
            }
        )
        consensus_results.append(result)
    
    # Analyze consensus
    if require_consensus:
        consensus = self._analyze_consensus(consensus_results)
        if not consensus.approved:
            return consensus
    
    # Additional enterprise checks
    security_check = await self._enterprise_security_scan(tool_name, parameters)
    if not security_check.approved:
        return security_check
    
    return GovernanceResult(
        approved=True,
        reason="Enterprise validation passed",
        risk_level="LOW",
        personas_consulted=[r.persona for r in consensus_results],
        recommendations=self._compile_recommendations(consensus_results)
    )

def _determine_required_personas(self, tool_name: str, parameters: dict) -> list:
    """Determine which personas must be consulted for enterprise decisions"""
    
    required = ["sarah_chen"]  # Always consult technical architect
    
    # Security-sensitive operations
    if any(pattern in str(parameters) for pattern in ["rm", "sudo", "chmod", "docker"]):
        required.append("marcus_rodriguez")
    
    # File modifications
    if tool_name in ["Write", "Edit"] and any(fp.endswith(('.py', '.js', '.ts')) for fp in parameters.get('file_paths', [])):
        required.append("emily_watson")
    
    # Database or config changes
    if any(pattern in str(parameters) for pattern in ["database", "config", "env"]):
        required.append("rachel_torres")
    
    return list(set(required))
```

---

## 3. Benefits Analysis

### Security Benefits
- **Unoverridable Protection**: Prevents `--dangerously-skip-permissions` bypass
- **Centralized Control**: Single policy source across entire organization
- **Defense in Depth**: Combines Claude's native controls with our governance
- **Real-time Threat Response**: Can update policies without Claude Code restarts

### Operational Benefits
- **Consistent Standards**: Same governance rules across all development teams
- **Audit Compliance**: Complete audit trails for regulatory requirements
- **Expert Validation**: Leverages our persona system for intelligent decisions
- **Performance Optimized**: Uses our existing cache layer for fast responses

### Development Benefits
- **Intelligent Guidance**: Not just blocking, but providing recommendations
- **Context Awareness**: Uses project history and patterns for decisions
- **Minimal Disruption**: Works transparently with existing workflows
- **Educational**: Developers learn best practices through governance feedback

---

## 4. Usage Guidelines

### For Development Teams

**Daily Usage:**
- Enterprise policies are automatically enforced
- Developers receive guidance through MCP server consultation
- Blocked operations include clear explanations and alternatives
- No additional commands or setup required

**Policy Violations:**
```bash
# Example of blocked operation
$ claude "Delete all log files"
ENTERPRISE POLICY VIOLATION: Bulk file deletion operations require approval
Recommendations: 
- Use specific file patterns instead of wildcards
- Consult with Marcus Rodriguez for security review
- Consider using log rotation instead
```

### For Administrators

**Policy Updates:**
```bash
# Deploy new enterprise policy
sudo cp enterprise-policy-v2.json /etc/claude-code/managed-settings.json
# Policy takes effect immediately for new sessions
```

**Monitoring:**
```bash
# View enterprise governance metrics
curl http://localhost:8001/governance/enterprise/metrics
# Check policy compliance
curl http://localhost:8001/governance/enterprise/compliance-report
```

### For Security Teams

**Audit Access:**
- Complete audit trails in governance database
- Real-time monitoring through WebSocket API
- Compliance reports available via REST API
- Integration with existing SIEM systems

**Incident Response:**
- Immediate policy updates without service restart
- Granular blocking by user, team, or operation type
- Historical analysis of governance decisions

---

## 5. Deployment Strategy

### Phase 1: Pilot Deployment (Week 1)
- Deploy to development team (5-10 developers)
- Monitor performance and usability
- Collect feedback on policy effectiveness
- Refine persona consultation logic

### Phase 2: Department Rollout (Week 2-3)
- Extend to entire engineering department
- Implement monitoring dashboard
- Train team leads on policy management
- Establish incident response procedures

### Phase 3: Organization-wide (Week 4)
- Deploy to all Claude Code users
- Integration with existing compliance systems
- Comprehensive audit reporting
- Performance optimization based on usage patterns

---

## 6. Monitoring and Maintenance

### Key Metrics
- Policy violation rates by team/operation
- Governance decision response times
- Persona consultation accuracy
- Developer satisfaction scores

### Maintenance Tasks
- Weekly policy effectiveness review
- Monthly persona accuracy tuning
- Quarterly compliance audits
- Annual policy framework review

### Performance Targets
- Governance decision latency: <200ms
- Policy violation false positive rate: <5%
- Developer workflow disruption: <10%
- Audit trail completeness: 100%

---

## 7. Risk Assessment

### Implementation Risks
- **Low**: Leverages existing, tested governance system
- **Mitigation**: Gradual rollout with rollback capabilities
- **Monitoring**: Real-time performance and error tracking

### Operational Risks
- **Medium**: Overly restrictive policies could hinder productivity
- **Mitigation**: Persona-based intelligent guidance vs. hard blocking
- **Resolution**: Rapid policy adjustment capabilities

### Security Risks
- **Low**: Enhanced security through unoverridable policies
- **Benefit**: Eliminates bypass mechanisms and provides audit trails

---

## 8. Success Criteria

### Technical Success
- [ ] 100% policy enforcement across all Claude Code instances
- [ ] <200ms average governance decision time
- [ ] Zero governance system downtime
- [ ] Complete audit trail coverage

### Business Success
- [ ] Reduced security incidents by 80%
- [ ] Improved compliance audit scores
- [ ] Maintained developer productivity
- [ ] Enhanced code quality metrics

### User Success
- [ ] Positive developer feedback (>4/5 rating)
- [ ] Reduced support tickets for governance questions
- [ ] Improved adherence to coding standards
- [ ] Faster onboarding of new team members

---

## 9. Next Steps

1. **Week 1**: Implement enterprise bridge and policy configuration
2. **Week 2**: Deploy to pilot group and collect feedback
3. **Week 3**: Refine policies based on usage data
4. **Week 4**: Full organizational deployment
5. **Week 5+**: Ongoing optimization and monitoring

---

**Approval Required From:**
- [ ] Security Team Lead
- [ ] Engineering Director  
- [ ] Compliance Officer
- [ ] Development Team Leads

**Estimated Implementation Time:** 2-3 weeks  
**Resource Requirements:** 1 senior engineer, existing infrastructure  
**Risk Level:** Low to Medium  
**Business Impact:** High positive impact on security and compliance