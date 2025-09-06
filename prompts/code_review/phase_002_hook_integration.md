# Phase CRA-002: MODULAR_ANALYSIS_HOOKS Orchestration Prompt

**Target**: Claude Code Implementation  
**Duration**: 6 hours  
**Lead**: Alex Novak (Hook Architecture) + Dr. Sarah Chen (Validation)  
**Phase Type**: Hook Integration & Plugin Architecture  

---

## 🎯 **PHASE OBJECTIVE**

Implement pluggable analysis hooks that integrate with existing governance infrastructure, enabling config-driven and database-driven validation with modular plugin architecture.

---

## 🏗️ **IMPLEMENTATION REQUIREMENTS**

### **CRITICAL: Extend Existing Hook System**
You MUST build upon these existing components:
- `libs/governance/hooks/` - Existing hook infrastructure
- `libs/governance/core/runtime_governance.py` - Main governance system
- `libs/governance/validators/` - Existing validator base classes
- Results from Phase CRA-001 stored in database

### **PLUGIN ARCHITECTURE REQUIREMENTS**
- Hook-based plugin registration system
- Database-driven validator configuration
- Config-file-driven rule management
- Runtime plugin enable/disable capability

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **1. Create Analysis Hook Registry** (`libs/governance/core/analysis_hook_registry.py`)

```python
# Template structure - follow existing hook patterns
class AnalysisHookRegistry:
    def __init__(self, governance_system, database_manager, config_manager):
        # Use EXISTING systems
        self.governance = governance_system
        self.db = database_manager
        self.config = config_manager
        self.registered_hooks = {}
        self.registered_validators = {}
        self.plugin_configs = {}
    
    def register_analysis_hook(self, hook_name: str, hook_class: Type[AnalysisHook]):
        # Plugin registration with database persistence
        pass
    
    def register_validator_plugin(self, validator_name: str, validator_class: Type[BaseValidator]):
        # Validator plugin registration
        pass
    
    async def load_plugins_from_database(self):
        # Load enabled plugins from database configuration
        pass
    
    async def execute_analysis_hooks(self, hook_type: str, context: AnalysisContext):
        # Execute registered hooks with full audit trail
        pass
```

### **2. Create Pre-Analysis Hook** (`libs/governance/hooks/pre_analysis_hook.py`)

```python
class PreAnalysisHook(BaseAnalysisHook):
    def __init__(self, database_manager, cache_manager, config_manager):
        # Use EXISTING systems
        pass
    
    async def execute(self, context: AnalysisContext) -> HookResult:
        """
        Pre-analysis validation and setup:
        - Validate analysis scope and permissions
        - Check database connection and cache availability  
        - Load analysis configuration from existing config system
        - Verify persona availability and consultation limits
        """
        pass
    
    async def validate_analysis_scope(self, scope: AnalysisScope) -> bool:
        # Use existing governance permission system
        pass
    
    async def check_system_readiness(self) -> SystemStatus:
        # Verify all required systems are operational
        pass
```

**Requirements**:
- [ ] Validate analysis permissions using existing governance system
- [ ] Check database connectivity and schema readiness
- [ ] Verify cache system availability and performance
- [ ] Confirm persona manager operational status
- [ ] Load plugin configurations from database
- [ ] Validate analysis scope against existing rules

### **3. Create Analysis Execution Hook** (`libs/governance/hooks/analysis_execution_hook.py`)

```python
class AnalysisExecutionHook(BaseAnalysisHook):
    def __init__(self, hook_registry, persona_manager, database_manager):
        # Use EXISTING systems
        pass
    
    async def execute(self, context: AnalysisContext) -> HookResult:
        """
        Main analysis execution:
        - Route analysis to appropriate validator plugins
        - Execute persona consultations based on issue types
        - Store progress and results in existing database
        - Update cache with analysis findings
        """
        pass
    
    async def route_to_validators(self, issues: List[Issue]) -> ValidationResults:
        # Route to appropriate validator plugins
        pass
    
    async def consult_personas(self, issues: List[Issue]) -> PersonaConsultations:
        # Use existing persona consultation system
        pass
```

**Requirements**:
- [ ] Execute validator plugins based on database configuration
- [ ] Route issues to appropriate personas using existing system
- [ ] Store all execution progress in database
- [ ] Update cache with intermediate and final results
- [ ] Handle plugin failures gracefully with fallbacks
- [ ] Maintain comprehensive audit trail

### **4. Create Post-Analysis Hook** (`libs/governance/hooks/post_analysis_hook.py`)

```python
class PostAnalysisHook(BaseAnalysisHook):
    def __init__(self, prompt_generator, database_manager, cache_manager):
        # Use EXISTING systems
        pass
    
    async def execute(self, context: AnalysisContext) -> HookResult:
        """
        Post-analysis processing:
        - Generate GitHub Copilot prompts using existing templates
        - Update analysis metrics in database
        - Trigger cache invalidation for related data
        - Prepare data for Phase CRA-003
        """
        pass
    
    async def generate_copilot_prompts(self, analysis_results: AnalysisResults) -> CopilotPrompts:
        # Generate prompts using existing template system
        pass
    
    async def update_metrics(self, session_id: str, results: AnalysisResults):
        # Update database metrics and cache
        pass
```

**Requirements**:
- [ ] Generate persona-specific Copilot prompts
- [ ] Update database with final analysis metrics
- [ ] Invalidate relevant cache entries
- [ ] Prepare structured data for prompt generation phase
- [ ] Generate analysis summary reports
- [ ] Update session status to completed

---

## 🔌 **PLUGIN SYSTEM IMPLEMENTATION**

### **5. Create Base Plugin Classes** (`libs/governance/plugins/base_plugin.py`)

```python
class BaseAnalysisPlugin:
    def __init__(self, config: dict, database_manager, cache_manager):
        self.config = config
        self.db = database_manager
        self.cache = cache_manager
        self.enabled = config.get('enabled', True)
    
    async def can_handle(self, issue: Issue) -> bool:
        # Determine if this plugin can handle the issue
        pass
    
    async def analyze(self, issue: Issue, context: AnalysisContext) -> PluginResult:
        # Main analysis method - override in subclasses
        pass
    
    async def get_configuration(self) -> dict:
        # Get plugin configuration from database
        pass

class ArchitectureAnalysisPlugin(BaseAnalysisPlugin):
    async def analyze(self, issue: Issue, context: AnalysisContext) -> PluginResult:
        # Architecture-specific analysis
        # Consults Sarah Chen persona
        pass

class PerformanceAnalysisPlugin(BaseAnalysisPlugin):
    async def analyze(self, issue: Issue, context: AnalysisContext) -> PluginResult:
        # Performance-specific analysis  
        # Consults Marcus Rodriguez persona
        pass

class TestingAnalysisPlugin(BaseAnalysisPlugin):
    async def analyze(self, issue: Issue, context: AnalysisContext) -> PluginResult:
        # Testing-specific analysis
        # Consults Emily Watson persona
        pass

class DocumentationAnalysisPlugin(BaseAnalysisPlugin):
    async def analyze(self, issue: Issue, context: AnalysisContext) -> PluginResult:
        # Documentation-specific analysis
        # Consults Rachel Torres persona
        pass
```

### **6. Create Plugin Configuration System** (`libs/governance/core/plugin_config_manager.py`)

```python
class PluginConfigManager:
    def __init__(self, database_manager, config_manager):
        # Use EXISTING systems
        pass
    
    async def load_plugin_configs(self) -> Dict[str, PluginConfig]:
        # Load plugin configurations from database and config files
        pass
    
    async def update_plugin_config(self, plugin_name: str, config: dict):
        # Update plugin configuration in database
        pass
    
    async def enable_plugin(self, plugin_name: str):
        # Enable plugin via database update
        pass
    
    async def disable_plugin(self, plugin_name: str):
        # Disable plugin via database update
        pass
```

---

## 🗄️ **DATABASE SCHEMA EXTENSIONS**

### **Plugin Configuration Tables** (Extend existing database)

```sql
-- Add to existing database schema
CREATE TABLE IF NOT EXISTS analysis_plugins (
    id SERIAL PRIMARY KEY,
    plugin_name VARCHAR(100) UNIQUE NOT NULL,
    plugin_type VARCHAR(50) NOT NULL, -- 'validator', 'analyzer', 'reporter'
    class_name VARCHAR(100) NOT NULL,
    module_path VARCHAR(200) NOT NULL,
    enabled BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0,
    configuration JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS plugin_execution_log (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    plugin_name VARCHAR(100) NOT NULL,
    execution_time_ms INTEGER,
    success BOOLEAN,
    error_message TEXT,
    input_data JSONB,
    output_data JSONB,
    executed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hook_execution_log (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    hook_name VARCHAR(100) NOT NULL,
    hook_type VARCHAR(50) NOT NULL, -- 'pre_analysis', 'execution', 'post_analysis'
    execution_time_ms INTEGER,
    success BOOLEAN,
    plugins_executed TEXT[],
    error_message TEXT,
    executed_at TIMESTAMP DEFAULT NOW()
);
```

---

## ⚙️ **CONFIGURATION INTEGRATION**

### **7. Config File Integration** (`config/analysis/plugin_config.yaml`)

```yaml
# Extend existing config structure
analysis_plugins:
  architecture:
    enabled: true
    class: "ArchitectureAnalysisPlugin"
    module: "libs.governance.plugins.architecture_plugin"
    priority: 10
    configuration:
      persona: "sarah_chen"
      severity_threshold: "high"
      file_patterns:
        - "apps/**/*.py"
        - "libs/**/*.py"
      checks:
        - "monolithic_files"
        - "circular_dependencies"
        - "god_objects"
  
  performance:
    enabled: true
    class: "PerformanceAnalysisPlugin"
    module: "libs.governance.plugins.performance_plugin"
    priority: 8
    configuration:
      persona: "marcus_rodriguez"
      severity_threshold: "medium"
      file_patterns:
        - "**/*.py"
        - "**/*.js"
        - "**/*.ts"
      checks:
        - "nested_loops"
        - "inefficient_queries"
        - "memory_leaks"

  testing:
    enabled: true
    class: "TestingAnalysisPlugin" 
    module: "libs.governance.plugins.testing_plugin"
    priority: 6
    configuration:
      persona: "emily_watson"
      severity_threshold: "medium"
      file_patterns:
        - "**/*.py"
        - "**/*.js"
        - "**/*.ts"
      checks:
        - "missing_tests"
        - "low_coverage"
        - "flaky_tests"

database_driven_config:
  enabled: true
  priority_override: true  # Database config overrides file config
  runtime_updates: true    # Allow runtime plugin enable/disable
```

---

## 🔗 **INTEGRATION POINTS**

### **Governance Integration**
- [ ] Register hooks with existing `RuntimeGovernanceSystem`
- [ ] Use existing permission validation methods
- [ ] Maintain existing audit logging format
- [ ] Follow existing error handling patterns

### **Database Integration**
- [ ] Use existing `DatabaseManager` transaction methods
- [ ] Follow existing connection pooling patterns
- [ ] Use existing query optimization techniques
- [ ] Maintain existing backup and recovery compatibility

### **Cache Integration**
- [ ] Use existing `IntelligentCache` hierarchical patterns
- [ ] Follow existing cache key naming conventions
- [ ] Use existing cache invalidation strategies
- [ ] Maintain existing cache metrics and monitoring

### **Persona Integration**
- [ ] Use existing `PersonaManager.consult_persona()` patterns
- [ ] Follow existing consultation rate limiting
- [ ] Use existing persona expertise routing
- [ ] Maintain existing response caching

---

## ⚡ **PERFORMANCE REQUIREMENTS**

### **Hook Execution Performance**
- [ ] Pre-analysis hook: <10 seconds
- [ ] Analysis execution: <2 minutes for full codebase
- [ ] Post-analysis hook: <30 seconds
- [ ] Plugin loading: <5 seconds

### **Database Performance**
- [ ] Plugin config queries: <50ms
- [ ] Execution logging: <10ms per entry
- [ ] Transaction rollback: <1 second
- [ ] Configuration updates: <100ms

### **Cache Performance**
- [ ] Plugin config cache hit ratio: >95%
- [ ] Result caching: <5ms write time
- [ ] Cache invalidation: <10ms
- [ ] Memory usage: <200MB additional

---

## 🛡️ **GOVERNANCE COMPLIANCE**

### **Safety Requirements**
- [ ] All plugins can be disabled via database configuration
- [ ] Complete rollback capability for any hook execution
- [ ] Comprehensive error logging with stack traces
- [ ] Graceful degradation when plugins fail

### **Security Requirements**
- [ ] Plugin execution isolation using existing security patterns
- [ ] Input validation for all plugin configurations
- [ ] Permission validation before plugin execution
- [ ] Audit trail for all plugin actions

### **Testing Requirements**
- [ ] Unit tests for all hook classes
- [ ] Integration tests with existing governance system
- [ ] Plugin loading and execution tests
- [ ] Database schema migration tests
- [ ] Cache integration validation tests

---

## 📊 **SUCCESS CRITERIA**

### **Functional Requirements**
- [ ] Hooks integrate seamlessly with existing governance system
- [ ] Plugins can be enabled/disabled via database configuration
- [ ] All analysis results stored in database with proper relationships
- [ ] Cache integration provides expected performance improvements
- [ ] Error handling maintains system stability

### **Performance Requirements**
- [ ] All hook execution times within specified limits
- [ ] Database operations meet latency requirements
- [ ] Cache hit ratios achieve targets
- [ ] Memory usage within acceptable bounds

### **Integration Requirements**
- [ ] Zero disruption to existing governance functionality
- [ ] All existing tests continue to pass
- [ ] New hooks follow existing governance patterns
- [ ] Plugin system extensible for future additions

---

## 🚀 **IMPLEMENTATION SEQUENCE**

### **Step 1: Hook Infrastructure** (2 hours)
1. Create `AnalysisHookRegistry` with plugin registration
2. Implement base hook classes following existing patterns
3. Add database schema extensions
4. Test hook registration and basic execution

### **Step 2: Plugin System** (2 hours)
1. Implement base plugin classes
2. Create specific analysis plugins (Architecture, Performance, Testing, Documentation)
3. Implement plugin configuration manager
4. Test plugin loading and execution

### **Step 3: Integration** (1.5 hours)
1. Integrate hooks with existing governance system
2. Connect to existing database and cache systems
3. Implement configuration file integration
4. Test end-to-end hook execution

### **Step 4: Validation** (30 minutes)
1. Run full test suite including new components
2. Verify performance requirements
3. Test plugin enable/disable functionality
4. Validate database and cache integration

---

## 📝 **COMPLETION DELIVERABLES**

### **Code Deliverables**
- [ ] `libs/governance/core/analysis_hook_registry.py` - Main hook registry
- [ ] `libs/governance/hooks/pre_analysis_hook.py` - Pre-analysis hook
- [ ] `libs/governance/hooks/analysis_execution_hook.py` - Main execution hook
- [ ] `libs/governance/hooks/post_analysis_hook.py` - Post-analysis hook
- [ ] `libs/governance/plugins/` - Plugin base classes and implementations
- [ ] `libs/governance/core/plugin_config_manager.py` - Plugin configuration management
- [ ] Database schema extensions
- [ ] Configuration file extensions

### **Documentation Updates**
- [ ] Update `TRACKER.md` with CRA-002 completion
- [ ] Update `STATUS.md` with new hook capabilities
- [ ] Add entries to `DECISIONS.md` for plugin architecture choices
- [ ] Update governance documentation with new hooks

### **Validation Outputs**
- [ ] Test coverage report >85%
- [ ] Performance benchmark results for all hooks
- [ ] Plugin execution verification tests
- [ ] Integration test results with existing systems

---

## ⚠️ **CRITICAL SUCCESS FACTORS**

1. **EXTEND, DON'T REPLACE**: Build upon existing hook infrastructure
2. **DATABASE DRIVEN**: All plugin configuration must be database-driven
3. **PLUGIN ISOLATION**: Plugins must not interfere with each other
4. **PERFORMANCE FIRST**: Meet all performance requirements
5. **GRACEFUL DEGRADATION**: System must work even if plugins fail

---

## 🎯 **NEXT PHASE PREPARATION**

Upon successful completion of CRA-002:
- [ ] Validate all hooks execute correctly
- [ ] Confirm plugin system works with database configuration
- [ ] Verify performance meets requirements
- [ ] Test plugin enable/disable functionality
- [ ] Prepare hook execution results for CRA-003 prompt generation

**Phase CRA-003 Input**: Hook execution logs and plugin results will be used for generating GitHub Copilot prompts with persona-specific expertise.

---

**Remember**: This phase creates the plugin infrastructure that makes the system truly modular and extensible. Focus on making plugins easy to add, configure, and manage through database-driven configuration.