# Phase CRA-004: DATABASE_DRIVEN_CONFIGURATION Orchestration Prompt

**Target**: Claude Code Implementation with Database Integration  
**Duration**: 4 hours  
**Lead**: Database-driven Configuration + UI Preparation  
**Phase Type**: Configuration Management & UI Foundation  

---

## 🎯 **PHASE OBJECTIVE**

Implement comprehensive database-driven configuration management system that enables dynamic rule management, persona assignment, and UI-ready interfaces for the complete code review system.

---

## 🏗️ **IMPLEMENTATION REQUIREMENTS**

### **CRITICAL: Complete the Modular System**
You MUST finalize the modular architecture:
- Database-driven analysis rules and validator configuration
- Dynamic persona assignment via database queries
- UI-ready configuration management interfaces
- Complete plugin system with runtime enable/disable capability

### **SYSTEM INTEGRATION REQUIREMENTS**
- All configuration stored in existing database
- Real-time configuration updates without restarts
- UI-ready API endpoints for configuration management
- Complete audit trail for all configuration changes

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **1. Create Database Configuration Manager** (`libs/governance/core/db_config_manager.py`)

```python
# Template structure - integrate with existing database
class DatabaseConfigurationManager:
    def __init__(self, database_manager, cache_manager, governance_system):
        # Use EXISTING systems
        self.db = database_manager
        self.cache = cache_manager
        self.governance = governance_system
        self.config_cache = {}
        self.watchers = []
    
    async def load_analysis_configuration(self) -> AnalysisConfiguration:
        """
        Load complete analysis configuration from database:
        - Analysis rules and validators
        - Persona assignments and routing
        - Plugin configurations and status
        - Governance rule overrides
        """
        pass
    
    async def update_analysis_rule(self, rule_id: int, updates: dict) -> bool:
        """Update analysis rule with validation and cache invalidation"""
        pass
    
    async def toggle_plugin(self, plugin_name: str, enabled: bool) -> bool:
        """Enable/disable plugins at runtime"""
        pass
    
    async def assign_persona_to_rule(self, rule_id: int, persona: str) -> bool:
        """Dynamically assign personas to analysis rules"""
        pass
    
    async def watch_configuration_changes(self, callback: Callable):
        """Register callback for configuration changes"""
        pass
```

**Requirements**:
- [ ] Load all configuration from database tables created in previous phases
- [ ] Provide real-time configuration updates without system restart
- [ ] Cache configuration for performance with intelligent invalidation
- [ ] Validate all configuration changes against governance rules
- [ ] Support configuration watching for real-time UI updates
- [ ] Maintain complete audit trail for configuration changes

### **2. Create Dynamic Rule Management System** (`libs/governance/core/dynamic_rule_manager.py`)

```python
class DynamicRuleManager:
    def __init__(self, db_config_manager, governance_system, persona_manager):
        # Use EXISTING systems
        pass
    
    async def create_analysis_rule(self, rule_config: RuleConfig) -> int:
        """
        Create new analysis rule with:
        - Validation against existing governance
        - Automatic persona assignment based on rule type
        - Plugin compatibility checking
        - Database storage with audit trail
        """
        pass
    
    async def update_rule_configuration(self, rule_id: int, config: dict) -> bool:
        """Update rule configuration with validation"""
        pass
    
    async def get_rules_for_file_type(self, file_extension: str) -> List[AnalysisRule]:
        """Get applicable rules for specific file types"""
        pass
    
    async def get_rules_by_severity(self, min_severity: str) -> List[AnalysisRule]:
        """Get rules filtered by minimum severity"""
        pass
    
    async def bulk_update_rules(self, updates: List[RuleUpdate]) -> BulkUpdateResult:
        """Perform bulk rule updates with transaction safety"""
        pass
```

### **3. Create UI-Ready Configuration API** (`apps/api/configuration_api.py`)

```python
# Extend existing FastAPI application
class ConfigurationAPI:
    def __init__(self, app: FastAPI, db_config_manager, governance_system):
        # Integrate with EXISTING FastAPI app
        self.app = app
        self.db_config = db_config_manager
        self.governance = governance_system
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup configuration management routes"""
        
        @self.app.get("/api/v1/config/analysis-rules")
        async def get_analysis_rules(skip: int = 0, limit: int = 100):
            """Get paginated analysis rules for UI"""
            pass
        
        @self.app.post("/api/v1/config/analysis-rules")
        async def create_analysis_rule(rule: CreateRuleRequest):
            """Create new analysis rule via UI"""
            pass
        
        @self.app.put("/api/v1/config/analysis-rules/{rule_id}")
        async def update_analysis_rule(rule_id: int, updates: UpdateRuleRequest):
            """Update analysis rule via UI"""
            pass
        
        @self.app.delete("/api/v1/config/analysis-rules/{rule_id}")
        async def delete_analysis_rule(rule_id: int):
            """Delete analysis rule via UI"""
            pass
        
        @self.app.get("/api/v1/config/plugins")
        async def get_plugin_status():
            """Get current plugin status for UI"""
            pass
        
        @self.app.post("/api/v1/config/plugins/{plugin_name}/toggle")
        async def toggle_plugin(plugin_name: str, enabled: bool):
            """Enable/disable plugin via UI"""
            pass
        
        @self.app.get("/api/v1/config/personas")
        async def get_persona_assignments():
            """Get current persona assignments for UI"""
            pass
        
        @self.app.put("/api/v1/config/personas/assign")
        async def assign_persona(assignment: PersonaAssignmentRequest):
            """Assign persona to rule via UI"""
            pass
        
        @self.app.get("/api/v1/config/governance-overrides")
        async def get_governance_overrides():
            """Get governance rule overrides for UI"""
            pass
        
        @self.app.get("/api/v1/config/audit-trail")
        async def get_configuration_audit_trail(
            skip: int = 0, 
            limit: int = 50,
            filter_type: str = None
        ):
            """Get configuration change audit trail for UI"""
            pass
```

**Requirements**:
- [ ] Integrate with existing FastAPI application structure
- [ ] Provide complete CRUD operations for analysis rules
- [ ] Support real-time plugin enable/disable
- [ ] Enable dynamic persona assignment via API
- [ ] Provide governance rule override management
- [ ] Include comprehensive audit trail access
- [ ] Follow existing API patterns and authentication

---

## 🗄️ **COMPLETE DATABASE SCHEMA**

### **Configuration Management Tables** (Complete the schema)

```sql
-- Complete database schema for configuration management
CREATE TABLE IF NOT EXISTS governance_rule_overrides (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    original_config JSONB NOT NULL,
    override_config JSONB NOT NULL,
    reason TEXT NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    approved_by VARCHAR(100),
    enabled BOOLEAN DEFAULT false,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS persona_rule_assignments (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES analysis_rules(id),
    persona_name VARCHAR(50) NOT NULL,
    assignment_reason TEXT,
    confidence_score DECIMAL(3,2) DEFAULT 1.0,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS configuration_audit_log (
    id SERIAL PRIMARY KEY,
    change_type VARCHAR(50) NOT NULL, -- 'rule_created', 'rule_updated', 'plugin_toggled', etc.
    entity_type VARCHAR(50) NOT NULL, -- 'analysis_rule', 'plugin', 'persona_assignment'
    entity_id VARCHAR(100) NOT NULL,
    old_config JSONB,
    new_config JSONB,
    changed_by VARCHAR(100) NOT NULL,
    change_reason TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ui_configuration_state (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    component_name VARCHAR(100) NOT NULL,
    configuration JSONB NOT NULL,
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, component_name)
);

-- Indexes for performance
CREATE INDEX idx_analysis_rules_enabled ON analysis_rules(enabled);
CREATE INDEX idx_analysis_rules_type ON analysis_rules(rule_type);
CREATE INDEX idx_discovered_issues_session ON discovered_issues(session_id);
CREATE INDEX idx_copilot_prompts_status ON copilot_prompts(status);
CREATE INDEX idx_config_audit_log_type ON configuration_audit_log(change_type);
CREATE INDEX idx_config_audit_log_entity ON configuration_audit_log(entity_type, entity_id);
```

### **4. Create Configuration Validation System** (`libs/governance/core/config_validator.py`)

```python
class ConfigurationValidator:
    def __init__(self, governance_system, database_manager):
        # Use EXISTING systems
        pass
    
    async def validate_rule_config(self, rule_config: dict) -> ValidationResult:
        """
        Validate analysis rule configuration:
        - Check file patterns are valid regex
        - Verify persona assignments are valid
        - Ensure severity levels are acceptable
        - Validate against existing governance rules
        """
        pass
    
    async def validate_plugin_config(self, plugin_name: str, config: dict) -> ValidationResult:
        """Validate plugin configuration changes"""
        pass
    
    async def validate_persona_assignment(self, rule_id: int, persona: str) -> ValidationResult:
        """Validate persona assignment for rule type"""
        pass
    
    async def validate_governance_override(self, override: dict) -> ValidationResult:
        """Validate governance rule override requests"""
        pass
```

### **5. Create Real-Time Configuration Watcher** (`libs/governance/core/config_watcher.py`)

```python
class ConfigurationWatcher:
    def __init__(self, database_manager, cache_manager):
        # Use EXISTING systems
        pass
    
    async def start_watching(self):
        """Start watching for configuration changes"""
        pass
    
    async def notify_configuration_change(self, change_type: str, entity_id: str, old_config: dict, new_config: dict):
        """Notify all watchers of configuration changes"""
        pass
    
    async def register_watcher(self, callback: Callable, filter_types: List[str] = None):
        """Register configuration change callback"""
        pass
    
    async def invalidate_caches(self, change_type: str, entity_id: str):
        """Invalidate relevant caches on configuration change"""
        pass
```

---

## 🔗 **INTEGRATION POINTS**

### **Complete System Integration**
- [ ] Integrate with all previous phase components
- [ ] Connect to existing FastAPI application
- [ ] Use existing database and cache systems
- [ ] Maintain existing governance patterns

### **UI Foundation Integration**
- [ ] Provide JSON APIs for all configuration operations
- [ ] Support real-time updates via WebSocket (use existing WebSocket manager)
- [ ] Enable configuration export/import functionality
- [ ] Support configuration templates and presets

### **Plugin System Integration**
- [ ] Complete plugin enable/disable functionality
- [ ] Support plugin configuration updates
- [ ] Enable plugin dependency management
- [ ] Provide plugin health monitoring

---

## ⚡ **PERFORMANCE REQUIREMENTS**

### **Configuration Management Performance**
- [ ] Configuration loading: <200ms for full config
- [ ] Rule updates: <100ms per rule change
- [ ] Plugin toggling: <50ms response time
- [ ] Persona assignment: <30ms per assignment

### **API Performance**
- [ ] Configuration API endpoints: <150ms response time
- [ ] Real-time updates: <100ms propagation time
- [ ] Audit trail queries: <300ms for 50 records
- [ ] Bulk operations: <2 seconds for 100 rules

### **Cache Performance**
- [ ] Configuration cache hit ratio: >95%
- [ ] Cache invalidation: <10ms
- [ ] Configuration reload: <500ms
- [ ] Memory usage: <100MB additional

---

## 🛡️ **GOVERNANCE COMPLIANCE**

### **Configuration Security**
- [ ] All configuration changes require authentication
- [ ] Configuration change audit trail maintained
- [ ] Governance rule overrides require approval workflow
- [ ] Sensitive configuration values encrypted

### **Data Integrity**
- [ ] All configuration changes validated before storage
- [ ] Database constraints prevent invalid configurations
- [ ] Configuration rollback capability
- [ ] Backup and recovery for configuration data

### **Access Control**
- [ ] Role-based access to configuration management
- [ ] Configuration change permissions enforced
- [ ] UI access controls based on user roles
- [ ] API endpoint security and rate limiting

---

## 📊 **SUCCESS CRITERIA**

### **Functional Requirements**
- [ ] Complete configuration management via database
- [ ] Dynamic rule and plugin management
- [ ] Real-time configuration updates without restart
- [ ] UI-ready API endpoints for all operations
- [ ] Comprehensive audit trail and monitoring

### **Integration Requirements**
- [ ] Seamless integration with all previous phases
- [ ] No disruption to existing functionality
- [ ] Complete plugin system functionality
- [ ] UI foundation ready for frontend development

### **Performance Requirements**
- [ ] All configuration operations within time limits
- [ ] Cache utilization meets targets
- [ ] API response times within specifications
- [ ] Real-time updates perform efficiently

---

## 🚀 **IMPLEMENTATION SEQUENCE**

### **Step 1: Database Configuration Core** (1.5 hours)
1. Implement `DatabaseConfigurationManager`
2. Create `DynamicRuleManager`
3. Complete database schema with indexes
4. Test configuration loading and caching

### **Step 2: UI API Implementation** (1.5 hours)
1. Implement `ConfigurationAPI` endpoints
2. Create configuration validation system
3. Test all CRUD operations
4. Validate API response formats

### **Step 3: Real-Time Features** (1 hour)
1. Implement `ConfigurationWatcher`
2. Add real-time update capabilities
3. Test configuration change propagation
4. Validate cache invalidation

### **Step 4: Integration and Testing** (1 hour)
1. Integration test with all previous phases
2. Test complete end-to-end configuration workflow
3. Validate UI API functionality
4. Performance testing and optimization

---

## 📝 **COMPLETION DELIVERABLES**

### **Code Deliverables**
- [ ] `libs/governance/core/db_config_manager.py` - Database configuration management
- [ ] `libs/governance/core/dynamic_rule_manager.py` - Dynamic rule management
- [ ] `apps/api/configuration_api.py` - UI-ready configuration API
- [ ] `libs/governance/core/config_validator.py` - Configuration validation
- [ ] `libs/governance/core/config_watcher.py` - Real-time configuration watching
- [ ] Complete database schema with indexes
- [ ] Integration with existing FastAPI application

### **Documentation Updates**
- [ ] Update `TRACKER.md` with CRA-004 completion and overall system completion
- [ ] Update `STATUS.md` with complete system capabilities
- [ ] Add final entries to `DECISIONS.md` for configuration architecture
- [ ] Create comprehensive API documentation for configuration endpoints
- [ ] Document complete plugin system usage

### **Validation Outputs**
- [ ] Complete configuration management test suite
- [ ] API endpoint testing results
- [ ] Performance benchmark results for all operations
- [ ] Integration test results with all system components
- [ ] UI readiness validation report

---

## ⚠️ **CRITICAL SUCCESS FACTORS**

1. **COMPLETE MODULARITY**: Full plugin-based architecture with database-driven configuration
2. **UI READY**: All APIs ready for frontend implementation
3. **REAL-TIME UPDATES**: Configuration changes propagate without restart
4. **PERFORMANCE OPTIMIZED**: All operations meet performance requirements
5. **GOVERNANCE COMPLIANT**: Complete audit trail and security controls

---

## 🎯 **SYSTEM COMPLETION VALIDATION**

### **Complete Code Review System Validation**
Upon successful completion of CRA-004, validate:
- [ ] Full codebase discovery and analysis capability
- [ ] Modular plugin system with database-driven configuration
- [ ] Persona-specific GitHub Copilot prompt generation
- [ ] Real-time configuration management via UI-ready APIs
- [ ] Complete integration with existing governance infrastructure
- [ ] Performance targets met for all operations
- [ ] Comprehensive audit trail and monitoring

### **Ready for Production Use**
- [ ] `code-review` command fully functional
- [ ] Database-driven rule management operational
- [ ] Plugin system extensible for future additions
- [ ] UI integration foundation complete
- [ ] All governance compliance requirements met

### **Future UI Development Ready**
- [ ] All necessary APIs implemented and documented
- [ ] Real-time update capabilities functional
- [ ] Configuration management workflows tested
- [ ] Plugin management interfaces ready
- [ ] Audit trail and monitoring accessible via API

---

**Remember**: This phase completes the entire modular code review system. Focus on ensuring all components work together seamlessly and that the system is ready for both immediate use and future UI development.