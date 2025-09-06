# Phase CRA-001: DISCOVERY_AND_MAPPING Orchestration Prompt

**Target**: Claude Code Implementation  
**Duration**: 4 hours  
**Lead**: Dr. Sarah Chen (Architecture Review)  
**Phase Type**: Research & Discovery  

---

## 🎯 **PHASE OBJECTIVE**

Implement comprehensive codebase discovery using existing governance infrastructure, with intelligent issue classification and persona-driven routing.

---

## 🏗️ **IMPLEMENTATION REQUIREMENTS**

### **CRITICAL: Use Existing Systems**
You MUST integrate with these existing components:
- `libs/governance/core/runtime_governance.py` - Main governance system
- `apps/api/database_manager.py` - Database operations
- `apps/api/cache_manager.py` - Cache operations  
- `apps/api/persona_manager.py` - Persona consultations
- `libs/governance/validators/` - Existing validator framework

### **NO NEW DATABASES OR CACHES**
- Extend existing database schema only
- Use existing cache patterns and keys
- Follow current connection management
- Maintain existing performance optimizations

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **1. Create Discovery Engine** (`libs/governance/core/code_discovery.py`)

```python
# Template structure - implement following existing patterns
class CodebaseDiscoveryEngine:
    def __init__(self, governance_system, database_manager, cache_manager):
        # Use EXISTING systems - do not create new ones
        self.governance = governance_system  # From RuntimeGovernanceSystem
        self.db = database_manager           # From existing DatabaseManager  
        self.cache = cache_manager           # From existing IntelligentCache
        self.personas = PersonaManager()     # From existing PersonaManager
    
    async def discover_codebase(self, scan_config: dict) -> DiscoveryResult:
        # Implement using existing validator patterns
        pass
    
    async def classify_issues(self, files_data: list) -> IssueClassification:
        # Route to appropriate personas using existing consultation system
        pass
```

**Requirements**:
- [ ] Scan all directories specified in user request
- [ ] Use existing file system validators from `libs/governance/validators/`
- [ ] Store results in existing database using current schema patterns
- [ ] Cache scan results using existing cache key patterns
- [ ] Route architectural issues to Sarah Chen persona
- [ ] Route performance issues to Marcus Rodriguez persona
- [ ] Route testing issues to Emily Watson persona
- [ ] Route documentation issues to Rachel Torres persona

### **2. Create Issue Mapper** (`libs/governance/core/issue_mapper.py`)

```python
class IssueMapper:
    def __init__(self, persona_manager, database_manager):
        # Use EXISTING persona and database systems
        pass
    
    async def map_issue_to_persona(self, issue: Issue) -> PersonaAssignment:
        # Use existing persona consultation patterns
        pass
    
    async def generate_severity_classification(self, issues: List[Issue]) -> SeverityMap:
        # Use existing severity patterns from governance config
        pass
```

**Requirements**:
- [ ] Map issues to personas based on existing expertise domains
- [ ] Use existing persona consultation API
- [ ] Store mappings in existing database tables
- [ ] Follow existing severity classification from `libs/governance/config.yaml`

### **3. Database Schema Extension** (Extend existing schema)

Add to existing database schema:
```sql
-- Add to existing database (do NOT create new database)
CREATE TABLE IF NOT EXISTS code_analysis_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    scan_config JSONB,
    total_files INTEGER,
    total_issues INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'in_progress'
);

CREATE TABLE IF NOT EXISTS discovered_issues (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES code_analysis_sessions(session_id),
    file_path TEXT NOT NULL,
    issue_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    persona_assigned VARCHAR(50),
    line_numbers INTEGER[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **4. Cache Integration** (Use existing cache system)

```python
# Use existing cache patterns - do NOT create new cache system
class DiscoveryCache:
    def __init__(self, intelligent_cache):
        self.cache = intelligent_cache  # Use EXISTING IntelligentCache
    
    async def cache_scan_results(self, session_id: str, results: dict):
        # Use existing cache key patterns
        cache_key = f"code_analysis:{session_id}"
        await self.cache.set_hot(cache_key, results, ttl=3600)
    
    async def get_cached_scan(self, session_id: str) -> dict:
        # Use existing cache retrieval patterns
        cache_key = f"code_analysis:{session_id}"
        return await self.cache.get_hot(cache_key)
```

---

## 🔧 **INTEGRATION POINTS**

### **Governance Integration**
- [ ] Use existing `RuntimeGovernanceSystem.validate_operation()` 
- [ ] Follow existing permission and hook patterns
- [ ] Maintain existing audit logging
- [ ] Use existing configuration loading

### **Database Integration**  
- [ ] Use existing `DatabaseManager.execute()` methods
- [ ] Follow existing transaction patterns
- [ ] Use existing connection pooling
- [ ] Maintain existing error handling

### **Cache Integration**
- [ ] Use existing `IntelligentCache.set_hot()` and `get_hot()` methods
- [ ] Follow existing cache key naming conventions  
- [ ] Use existing TTL patterns
- [ ] Maintain existing cache metrics

### **Persona Integration**
- [ ] Use existing `PersonaManager.consult_persona()` method
- [ ] Follow existing persona consultation patterns
- [ ] Use existing persona expertise mappings
- [ ] Maintain existing response formatting

---

## ⚡ **PERFORMANCE REQUIREMENTS**

### **Scan Performance**
- [ ] Full codebase scan in <2 minutes
- [ ] Cache hit ratio >80% for repeat scans
- [ ] Database queries <100ms response time
- [ ] Memory usage <500MB during scan

### **Classification Performance**  
- [ ] Issue classification <30 seconds
- [ ] Persona routing <10 seconds per issue type
- [ ] Cache persona responses for 1 hour
- [ ] Batch database inserts for efficiency

---

## 🛡️ **GOVERNANCE COMPLIANCE**

### **Follow Existing Patterns**
- [ ] Use existing validator base classes
- [ ] Follow existing error handling patterns
- [ ] Maintain existing logging format
- [ ] Use existing configuration structure

### **Safety Requirements**
- [ ] No modification of existing governance rules
- [ ] No disruption to existing validators
- [ ] Full rollback capability if issues occur
- [ ] Comprehensive error logging

### **Testing Requirements**
- [ ] Unit tests for all new classes
- [ ] Integration tests with existing systems
- [ ] Performance tests for scan operations
- [ ] Cache behavior validation tests

---

## 📊 **SUCCESS CRITERIA**

### **Functional Requirements**
- [ ] Successfully scans all specified directories
- [ ] Correctly identifies architectural, performance, testing, and documentation issues
- [ ] Properly routes issues to appropriate personas
- [ ] Stores all data in existing database
- [ ] Caches results using existing cache system

### **Performance Requirements**
- [ ] Scan completes within time limits
- [ ] Database operations within latency limits
- [ ] Cache hit ratios meet targets
- [ ] Memory usage within bounds

### **Integration Requirements**
- [ ] Zero disruption to existing governance system
- [ ] All existing tests still pass
- [ ] No modification of existing core systems
- [ ] Backward compatibility maintained

---

## 🚀 **IMPLEMENTATION SEQUENCE**

### **Step 1: Environment Setup** (30 minutes)
1. Verify existing system connections
2. Test database schema additions
3. Validate cache integration
4. Confirm persona manager access

### **Step 2: Core Implementation** (2.5 hours)
1. Implement `CodebaseDiscoveryEngine` 
2. Implement `IssueMapper`
3. Add database schema extensions
4. Integrate cache patterns

### **Step 3: Integration Testing** (45 minutes)
1. Test with existing governance system
2. Validate database operations
3. Confirm cache behavior
4. Test persona routing

### **Step 4: Validation** (15 minutes)
1. Run full test suite
2. Verify performance metrics
3. Confirm governance compliance
4. Document completion

---

## 📝 **COMPLETION DELIVERABLES**

### **Code Deliverables**
- [ ] `libs/governance/core/code_discovery.py` - Main discovery engine
- [ ] `libs/governance/core/issue_mapper.py` - Issue classification and routing
- [ ] Database schema additions - Extend existing schema
- [ ] Integration tests - Validate with existing systems

### **Documentation Updates**
- [ ] Update `TRACKER.md` with phase completion
- [ ] Update `STATUS.md` with new capabilities  
- [ ] Add entry to `DECISIONS.md` with implementation choices
- [ ] Update `README.md` if public API changes

### **Validation Outputs**
- [ ] Test coverage report >85%
- [ ] Performance benchmark results
- [ ] Integration test results
- [ ] Governance compliance verification

---

## ⚠️ **CRITICAL SUCCESS FACTORS**

1. **REUSE EXISTING SYSTEMS**: Do not create new databases, caches, or core systems
2. **MAINTAIN COMPATIBILITY**: All existing functionality must continue working
3. **FOLLOW PATTERNS**: Use established code patterns and conventions
4. **PERFORMANCE FIRST**: Meet all performance requirements
5. **SAFETY NET**: Comprehensive error handling and rollback capability

---

## 🎯 **NEXT PHASE PREPARATION**

Upon successful completion of CRA-001:
- [ ] Validate all scan results in database
- [ ] Confirm persona assignments are accurate
- [ ] Verify cache performance meets targets
- [ ] Prepare CRA-002 hook integration data

**Phase CRA-002 Input**: Session ID and discovered issues from this phase will be used for hook integration implementation.

---

**Remember**: This is a discovery and mapping phase. Focus on comprehensive analysis and accurate classification. The implementation will come in subsequent phases.