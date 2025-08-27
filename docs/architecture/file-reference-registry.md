# File Reference Registry & Cross-Reference Tracking

**Version**: 1.0  
**Date**: 2025-01-27  
**Author**: Alex Novak v3.0 & Dr. Sarah Chen v1.2  
**Reviewers**: Quinn Roberts v1.1, Sam Martinez v3.2.0  
**Status**: Active Registry  
**Purpose**: Track mandatory architecture references and cross-file dependencies  
**Audience**: All developers, AI personas  

---

## Critical Issue Identified

Without a centralized registry, developers and AI personas cannot know which architecture documents must be referenced when working on specific files. This creates risk of:
- Missing critical security boundaries
- Violating established patterns
- Duplicating solved problems
- Breaking integration contracts

## File Reference Registry

### Frontend Components → Required Architecture References

| Component/Service | Must Reference | Validation Rules | Specialist Owner |
|------------------|----------------|------------------|------------------|
| `src/app/services/ipc.service.ts` | • `ipc-communication.md#secure-ipc-patterns`<br>• `security-boundaries.md#ipc-security-boundary`<br>• `frontend-architecture.md#ipc-service` | • All IPC channels must be whitelisted<br>• Payload size limits enforced<br>• Circuit breaker required | Alex Novak v3.0 |
| `src/app/services/websocket.service.ts` | • `backend-architecture.md#websocket-manager`<br>• `api-contracts.md#websocket-protocol`<br>• `frontend-architecture.md#websocket-service` | • Automatic reconnection required<br>• Message queuing during disconnection<br>• Backpressure handling | Alex Novak v3.0 |
| `src/app/services/terminal.service.ts` | • `frontend-architecture.md#terminal-service`<br>• `ipc-communication.md#terminal-operations`<br>• `security-boundaries.md#terminal-security` | • Memory leak prevention (C1 fix)<br>• PTY session limits<br>• Command sanitization | Alex Novak v3.0 |
| `src/app/services/agent.service.ts` | • `ai-governance-architecture.md#agent-lifecycle`<br>• `api-contracts.md#agent-management-api`<br>• `frontend-architecture.md#agent-service` | • Governance validation required<br>• Token cost tracking<br>• Persona orchestration | Dr. Avery Chen v1.0 |
| `src/app/services/cache.service.ts` | • `api-contracts.md#cache-management-api`<br>• `frontend-architecture.md#cache-service` | • Cache key validation<br>• TTL limits<br>• Size restrictions | Alex Novak v3.0 |

### Backend Services → Required Architecture References

| Service/Module | Must Reference | Validation Rules | Specialist Owner |
|---------------|----------------|------------------|------------------|
| `backend/cache_manager.py` | • `backend-architecture.md#cache-manager-critical-c2`<br>• `security-boundaries.md#cache-security`<br>• `database-schema.md#cache-tables` | • Two-tier fallback required<br>• Circuit breaker for failures<br>• Memory limits enforced | Dr. Sarah Chen v1.2 |
| `backend/websocket_manager.py` | • `backend-architecture.md#websocket-manager`<br>• `api-contracts.md#websocket-protocol`<br>• `security-boundaries.md#websocket-security` | • Connection limits (H1 fix)<br>• Cleanup timeouts<br>• Resource monitoring | Dr. Sarah Chen v1.2 |
| `backend/database_manager.py` | • `database-schema.md`<br>• `backend-architecture.md#database-manager`<br>• `security-boundaries.md#database-security` | • Connection pooling<br>• Race condition prevention (H3)<br>• Transaction management | Dr. Jamie Rodriguez v3.2 |
| `backend/agent_manager.py` | • `ai-governance-architecture.md`<br>• `api-contracts.md#agent-management-api`<br>• `backend-architecture.md#agent-manager` | • Governance hooks required<br>• Persona orchestration<br>• Cost validation | Dr. Avery Chen v1.0 |
| `backend/governance_engine.py` | • `ai-governance-architecture.md#governance-hooks`<br>• `persona-configurations.md`<br>• `security-boundaries.md#ai-integration-security` | • All 4 validation gates<br>• Dual framework approval<br>• Audit trail | Morgan Hayes v2.0 |

### Critical Integration Points → Cross-References

| Integration Point | Files Involved | Required References | Critical Constraints |
|------------------|----------------|-------------------|---------------------|
| **IPC Communication** | • `electron/main.js`<br>• `electron/preload.js`<br>• All Angular services | • `ipc-communication.md`<br>• `security-boundaries.md#ipc-security` | • Context isolation mandatory<br>• Channel whitelisting enforced |
| **API Integration** | • All backend endpoints<br>• All frontend API services | • `api-contracts.md`<br>• `security-boundaries.md#api-security` | • OpenAPI 3.0 compliance<br>• JWT authentication required |
| **Database Access** | • All backend services<br>• Migration scripts | • `database-schema.md`<br>• `security-boundaries.md#database-security` | • Row-level security<br>• Prepared statements only |
| **AI Integration** | • `backend/claude_integration.py`<br>• `backend/agent_manager.py` | • `ai-governance-architecture.md`<br>• `security-boundaries.md#ai-integration-security` | • Governance validation required<br>• Token limits enforced |

## Automated Reference Validation

### Reference Check Implementation
```python
"""
File reference validation system - ensures all required architecture references are present
"""

import os
import re
from typing import Dict, List, Set

class FileReferenceValidator:
    def __init__(self):
        self.reference_registry = self._load_reference_registry()
    
    def validate_file_references(self, file_path: str, file_content: str) -> Dict[str, any]:
        """Validate that file contains all required architecture references"""
        
        # Normalize file path for registry lookup
        normalized_path = self._normalize_path(file_path)
        
        # Get required references for this file
        required_refs = self.reference_registry.get(normalized_path, {})
        if not required_refs:
            return {"valid": True, "message": "No references required"}
        
        # Extract references from file content
        found_refs = self._extract_references(file_content)
        
        # Validate all required references are present
        missing_refs = required_refs['must_reference'] - found_refs
        
        if missing_refs:
            return {
                "valid": False,
                "missing_references": list(missing_refs),
                "message": f"Missing required architecture references: {missing_refs}",
                "specialist_owner": required_refs.get('specialist_owner'),
                "validation_rules": required_refs.get('validation_rules')
            }
        
        return {
            "valid": True,
            "found_references": list(found_refs),
            "specialist_owner": required_refs.get('specialist_owner')
        }
    
    def _extract_references(self, content: str) -> Set[str]:
        """Extract architecture document references from file content"""
        references = set()
        
        # Pattern 1: @architecture_reference docs/...
        pattern1 = r'@architecture_reference\s+([\w\-/\.#]+)'
        
        # Pattern 2: References backend-architecture.md#section
        pattern2 = r'References?\s+([\w\-]+\.md(?:#[\w\-]+)?)'
        
        # Pattern 3: * architecture_reference (in comments)
        pattern3 = r'\*\s+architecture_reference:\s+([\w\-/\.#]+)'
        
        for pattern in [pattern1, pattern2, pattern3]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            references.update(matches)
        
        return references
```

## Manual Reference Lookup Process

Until automated system is in place, use this process:

### Step 1: Identify Component Type
- Frontend Service? → Check Frontend Components table
- Backend Service? → Check Backend Services table
- Integration Code? → Check Critical Integration Points table

### Step 2: Find Required References
Locate your file/component and note all documents in "Must Reference" column

### Step 3: Apply Validation Rules
Ensure your implementation follows all rules in "Validation Rules" column

### Step 4: Contact Specialist Owner
For architectural decisions, consult the listed Specialist Owner

## Enforcement Mechanism

### Pre-Commit Hook Addition
```bash
#!/bin/bash
# Add to validate-code-documentation.sh

# Check for required architecture references
echo "Checking required architecture references..."

# For each modified file
for file in $(git diff --cached --name-only); do
    # Look up required references in registry
    required_refs=$(grep -A 2 "$file" docs/architecture/file-reference-registry.md | grep "Must Reference")
    
    if [ ! -z "$required_refs" ]; then
        # Extract reference list and validate each is present in file
        while IFS= read -r ref; do
            if ! grep -q "$ref" "$file"; then
                echo "ERROR: $file missing required reference: $ref"
                exit 1
            fi
        done <<< "$required_refs"
    fi
done
```

## Future Enhancement: Database-Driven Registry

### Proposed Schema
```sql
CREATE TABLE file_reference_registry (
    file_path VARCHAR(500) PRIMARY KEY,
    component_type VARCHAR(50),
    specialist_owner VARCHAR(100),
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE TABLE required_references (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(500) REFERENCES file_reference_registry(file_path),
    reference_document VARCHAR(200) NOT NULL,
    reference_section VARCHAR(100),
    is_mandatory BOOLEAN DEFAULT true,
    validation_rule TEXT
);

CREATE TABLE reference_validation_log (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(500),
    validation_timestamp TIMESTAMP DEFAULT NOW(),
    validation_passed BOOLEAN,
    missing_references JSONB,
    correlation_id UUID
);
```

### API for Reference Lookup
```python
@app.get("/api/references/{file_path}")
async def get_required_references(file_path: str):
    """API endpoint for AI personas to query required references"""
    
    # Query database for file's required references
    query = """
        SELECT rr.reference_document, rr.reference_section, rr.validation_rule
        FROM required_references rr
        JOIN file_reference_registry frr ON rr.file_path = frr.file_path
        WHERE frr.file_path = %s AND rr.is_mandatory = true
    """
    
    references = await db.fetch_all(query, [file_path])
    
    return {
        "file_path": file_path,
        "required_references": references,
        "specialist_owner": await get_specialist_owner(file_path)
    }
```

## Registry Maintenance

### Update Frequency
- Weekly review during architecture sync
- Immediate updates for new components
- Version tracking for reference changes

### Ownership
- **Frontend Registry**: Alex Novak v3.0
- **Backend Registry**: Dr. Sarah Chen v1.2
- **Integration Points**: Both architects jointly
- **Enforcement**: Quinn Roberts v1.1

---

**Next Steps**:
1. Implement database-driven registry (Phase 3)
2. Add API endpoints for dynamic lookup
3. Integrate with AI persona context
4. Add automatic registry updates from architecture changes