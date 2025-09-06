# Code Review Command - Master Orchestration Prompt

**Target**: Claude Code Complete System Implementation  
**Duration**: 4 days (16-20 hours total)  
**Methodology**: Phased Implementation with Daily Execution Cycles  
**Lead**: Full Team Coordination (Claude Desktop → Claude Code → GitHub Copilot)  

---

## 🎯 **MASTER ORCHESTRATION OBJECTIVE**

Implement complete modular code review system following the established phased implementation methodology, integrating with existing governance infrastructure while creating a plugin-based architecture ready for UI integration.

---

## 📋 **EXECUTION WORKFLOW**

### **Phase Progression Protocol**

Execute phases in strict sequence following the phased implementation methodology:

1. **Phase CRA-001: DISCOVERY_AND_MAPPING** (Day 1)
   - Load prompt: `prompts/code_review/phase_001_discovery.md`
   - Execute discovery using existing governance validators
   - Store results in existing database using current patterns
   - Cache analysis results using existing cache system
   - Route issues to appropriate personas

2. **Phase CRA-002: MODULAR_ANALYSIS_HOOKS** (Day 2)
   - Load prompt: `prompts/code_review/phase_002_hook_integration.md`
   - Build pluggable analysis hooks on existing hook infrastructure
   - Create database-driven validator configuration
   - Implement runtime plugin enable/disable capability
   - Integrate with existing governance system

3. **Phase CRA-003: COPILOT_PROMPT_ENGINE** (Day 3)
   - Load prompt: `prompts/code_review/phase_003_prompt_generation.md`
   - Generate persona-specific GitHub Copilot prompts
   - Embed governance rules and safety protocols
   - Store prompts in database for tracking
   - Prepare for implementation orchestration

4. **Phase CRA-004: DATABASE_DRIVEN_CONFIGURATION** (Day 4)
   - Load prompt: `prompts/code_review/phase_004_config_integration.md`
   - Complete modular architecture with database-driven configuration
   - Implement UI-ready API endpoints
   - Enable real-time configuration updates
   - Finalize plugin system architecture

---

## 🚀 **DAILY EXECUTION PROTOCOL**

### **Morning Phase Initiation** (09:00 UTC)
```bash
# Claude Code execution pattern
1. Load current phase prompt from prompts/code_review/
2. Review CURRENT_PHASE_IMPLEMENTATION.md 
3. Check STATUS.md for system health
4. Update TRACKER.md with phase start
5. Verify all required systems operational
```

### **Implementation Cycle** (09:30-15:30 UTC)
```bash
# 6-hour implementation window per phase
1. Execute phase requirements following prompt guidance
2. Use EXISTING systems (database, cache, governance, personas)
3. Test continuously during development
4. Update documentation in real-time
5. Commit frequently with structured messages
```

### **Evening Phase Completion** (16:00-17:00 UTC)
```bash
# Phase closure protocol
1. Run complete test suite
2. Update TRACKER.md with completion
3. Update STATUS.md with new capabilities
4. Document decisions in DECISIONS.md
5. Create phase completion summary
6. Prepare next phase transition
```

---

## 🏗️ **SYSTEM INTEGRATION REQUIREMENTS**

### **CRITICAL: Reuse Existing Infrastructure**

**Database Integration**:
- Use existing `apps/api/database_manager.py`
- Extend current database schema (do NOT create new database)
- Follow existing connection pooling and transaction patterns
- Maintain existing backup and recovery compatibility

**Cache Integration**:
- Use existing `apps/api/cache_manager.py` (IntelligentCache)
- Follow existing cache key naming conventions
- Use existing TTL patterns and cache hierarchies
- Maintain existing cache metrics and monitoring

**Governance Integration**:
- Use existing `libs/governance/core/runtime_governance.py`
- Extend existing validator framework in `libs/governance/validators/`
- Follow existing configuration patterns in `libs/governance/config.yaml`
- Maintain existing audit logging and compliance scoring

**Persona Integration**:
- Use existing `apps/api/persona_manager.py`
- Follow existing persona consultation patterns
- Use existing expertise routing and response caching
- Maintain existing persona response formatting

---

## 📊 **QUALITY ASSURANCE GATES**

### **Per-Phase Quality Gates**
Each phase must pass:
- [ ] All existing tests still pass (100% required)
- [ ] New test coverage >85%
- [ ] Performance benchmarks within limits
- [ ] Integration with existing systems validated
- [ ] Documentation updated per governance standards
- [ ] Database operations within latency requirements
- [ ] Cache performance targets met
- [ ] Governance compliance maintained

### **System-Wide Quality Gates**
Before final completion:
- [ ] End-to-end code review workflow functional
- [ ] Plugin system enables/disables without restart
- [ ] Database-driven configuration operational
- [ ] UI-ready APIs functional and documented
- [ ] Complete audit trail and monitoring
- [ ] Performance targets met for all operations
- [ ] Security and access controls implemented

---

## 🔧 **PLUGIN SYSTEM ARCHITECTURE**

### **Modular Plugin Framework**
```python
# Plugin registration and management
class PluginRegistry:
    - register_validator_plugin(name, class)
    - register_analysis_plugin(name, class) 
    - enable_plugin(name)
    - disable_plugin(name)
    - load_plugins_from_database()
    - execute_plugins_for_issue(issue)

# Database-driven configuration
class DatabaseConfigManager:
    - load_analysis_configuration()
    - update_analysis_rule(rule_id, updates)
    - toggle_plugin(plugin_name, enabled)
    - assign_persona_to_rule(rule_id, persona)
    - watch_configuration_changes(callback)
```

### **Hook System Integration**
```python
# Analysis hooks that integrate with existing governance
class AnalysisHookRegistry:
    - register_analysis_hook(hook_name, hook_class)
    - execute_analysis_hooks(hook_type, context)
    - load_hook_configs_from_database()
    - validate_hook_execution(result)
```

---

## 🗄️ **DATABASE SCHEMA ARCHITECTURE**

### **Complete Schema Design**
```sql
-- Core analysis tables
analysis_rules          -- Database-driven rule configuration
discovered_issues       -- Analysis results and classifications
code_analysis_sessions  -- Session tracking and metrics

-- Plugin system tables  
analysis_plugins        -- Plugin registry and configuration
plugin_execution_log    -- Plugin execution tracking
hook_execution_log      -- Hook execution audit trail

-- Prompt system tables
copilot_prompts        -- Generated prompts and metadata
copilot_executions     -- Implementation tracking
implementation_tracking -- Overall success metrics

-- Configuration management
governance_rule_overrides  -- Governance customization
persona_rule_assignments   -- Dynamic persona routing
configuration_audit_log    -- Configuration change tracking
ui_configuration_state     -- UI state persistence
```

---

## 🎛️ **UI-READY API ENDPOINTS**

### **Configuration Management APIs**
```http
GET    /api/v1/config/analysis-rules      # List analysis rules
POST   /api/v1/config/analysis-rules      # Create new rule
PUT    /api/v1/config/analysis-rules/{id} # Update rule
DELETE /api/v1/config/analysis-rules/{id} # Delete rule

GET    /api/v1/config/plugins             # List plugins status
POST   /api/v1/config/plugins/{name}/toggle # Enable/disable plugin

GET    /api/v1/config/personas            # List persona assignments
PUT    /api/v1/config/personas/assign     # Assign persona to rule

GET    /api/v1/config/audit-trail         # Configuration audit trail
```

### **Code Review Execution APIs**
```http
POST   /api/v1/code-review/start          # Start analysis session
GET    /api/v1/code-review/sessions/{id}  # Get session status
GET    /api/v1/code-review/sessions/{id}/issues # Get discovered issues
GET    /api/v1/code-review/sessions/{id}/prompts # Get generated prompts
POST   /api/v1/code-review/sessions/{id}/execute # Execute prompts
```

---

## ⚡ **PERFORMANCE TARGETS**

### **Analysis Performance**
- Full codebase scan: <2 minutes
- Issue classification: <30 seconds  
- Plugin execution: <1 minute total
- Database operations: <100ms per query
- Cache hit ratio: >80%

### **API Performance**
- Configuration endpoints: <150ms
- Analysis status queries: <100ms
- Real-time updates: <100ms propagation
- Bulk operations: <2 seconds

### **System Performance**
- Memory usage: <500MB additional
- Startup time: <30 seconds
- Plugin toggle: <5 seconds
- Configuration reload: <10 seconds

---

## 🛡️ **GOVERNANCE COMPLIANCE**

### **Follow Existing Patterns**
- [ ] Use existing validator base classes and patterns
- [ ] Follow existing error handling and logging
- [ ] Maintain existing configuration hierarchy
- [ ] Use existing audit trail formats
- [ ] Follow existing database transaction patterns

### **Safety Requirements**
- [ ] Complete rollback capability for all operations
- [ ] Comprehensive error handling with graceful degradation
- [ ] Configuration validation before any changes
- [ ] Plugin isolation to prevent system interference
- [ ] Database integrity constraints and validation

### **Security Requirements**
- [ ] Authentication required for configuration changes
- [ ] Authorization based on existing role patterns
- [ ] Input validation for all configuration data
- [ ] Audit logging for all security-relevant operations
- [ ] Rate limiting on API endpoints

---

## 📝 **COMPLETION VALIDATION**

### **System Functionality Validation**
Execute complete workflow:
```bash
# 1. Start code review analysis
claude-code "Execute code-review for apps/ and libs/ directories"

# 2. Verify database storage
# Check analysis_rules, discovered_issues, copilot_prompts tables

# 3. Test plugin management
# Enable/disable plugins via database configuration

# 4. Validate persona routing
# Confirm issues routed to appropriate personas

# 5. Generate and execute prompts
# Verify GitHub Copilot prompts generated and executable

# 6. Test configuration management
# Modify rules via API endpoints

# 7. Validate UI readiness
# Confirm all APIs return proper JSON for UI consumption
```

### **Documentation Validation**
- [ ] TRACKER.md updated with complete system status
- [ ] STATUS.md reflects all new capabilities
- [ ] DECISIONS.md documents all architectural choices
- [ ] API documentation complete and accurate
- [ ] Plugin development guide created
- [ ] Configuration management guide documented

---

## 🎯 **SUCCESS CRITERIA**

### **Functional Success**
- [ ] Complete `code-review` command operational
- [ ] Modular plugin system with database-driven configuration
- [ ] Persona-specific GitHub Copilot prompt generation
- [ ] Real-time configuration management without restart
- [ ] UI-ready API endpoints functional

### **Integration Success**
- [ ] Zero disruption to existing governance system
- [ ] All existing functionality preserved
- [ ] Performance targets met for all operations
- [ ] Complete audit trail and monitoring
- [ ] Security and compliance maintained

### **Architecture Success**
- [ ] Plugin system extensible for future additions
- [ ] Database schema scalable and maintainable
- [ ] Configuration system flexible and user-friendly
- [ ] API design suitable for UI development
- [ ] Codebase follows all established patterns

---

## 🚀 **EXECUTION COMMAND**

### **Start Implementation**
```bash
# Claude Code execution
claude-code "Implement complete code-review system following phased methodology. Start with Phase CRA-001 from prompts/code_review/phase_001_discovery.md. Follow daily execution protocol with morning initiation, 6-hour implementation cycle, and evening completion validation."
```

### **Phase Transition Commands**
```bash
# After each phase completion
claude-code "Transition to next phase. Load prompts/code_review/phase_00X_[phase_name].md and execute following phased implementation methodology."
```

### **Final Validation Command**
```bash
# After all phases complete
claude-code "Execute complete code-review system validation. Test end-to-end workflow, validate all integrations, confirm UI readiness, and document system completion."
```

---

## ⚠️ **CRITICAL REMINDERS**

1. **PHASED EXECUTION**: Complete each phase fully before moving to the next
2. **EXISTING SYSTEMS**: Build upon existing infrastructure, do not replace
3. **DATABASE DRIVEN**: All configuration must be database-driven for UI integration
4. **PERFORMANCE FIRST**: Meet all performance requirements during implementation
5. **GOVERNANCE COMPLIANCE**: Maintain existing governance patterns and standards
6. **COMPREHENSIVE TESTING**: Test continuously and validate all integrations
7. **DOCUMENTATION SYNC**: Update documentation in real-time during implementation

---

**This master orchestration prompt provides Claude Code with complete guidance for implementing the entire modular code review system following your established phased methodology and governance requirements.**