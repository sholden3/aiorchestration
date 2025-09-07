# MASTER RUN FILE: Validator Plugin Architecture Implementation

## 🎯 MISSION
Implement a comprehensive, configurable, data-driven validator plugin architecture that seamlessly integrates with all Claude Code native hooks and Git hooks, following strict governance protocols from CLAUDE.md.

## 📁 AVAILABLE RESOURCES

### Research Documents
- `research/claude_code_hooks_implementation_guide.md` - All 9 native Claude Code hooks
- `research/claude-code-native-governance-architecture.md` - additional research
- `research/git_hooks_governance_guide.md` - Git hooks implementation patterns
- `research/workflow_governance_system.md` - Governance system overview

### GitHub Copilot Prompts (In prompts/ folder)
- `phase1-core-plugin-architecture.md` - 5 prompts for foundation
- `phase2-validator-plugin-adapter.md` - 5 prompts for adaptation
- `phase3-hook-integration-layer.md` - 5 prompts for integration
- `phase4-bridge-implementation.md` - 5 prompts for bridging
- `phase5-testing-documentation.md` - 5 prompts for quality

### Governance Documents
- `CLAUDE.md` - Master governance rules (MUST FOLLOW)
- `STATUS.md` - Update with progress
- `TRACKER.md` - Track phase completion
- `DECISIONS.md` - Log architectural decisions

### Current State
- Validators location: `libs/governance/validators/`
- Hooks location: `libs/governance/hooks/`
- Config location: `config/governance/`

## 🏗️ IMPLEMENTATION PLAN

### PHASE 1: Core Plugin Architecture (DAY 1 - TODAY)

#### Morning Standup (09:00 UTC)
1. Read this entire document
2. Review `CLAUDE.md` for governance rules
3. Read `research/claude_code_hooks_implementation_guide.md`
4. Update `STATUS.md` with phase start
5. Create TodoWrite list below

#### TodoWrite Checklist - Phase 1
```
[ ] Create directory structure libs/governance/plugins/
[ ] Implement IValidatorPlugin interface (libs/governance/plugins/base.py)
    - Use Prompt 1.1 from phase1-core-plugin-architecture.md
[ ] Implement PluginRegistry (libs/governance/plugins/registry.py)
    - Use Prompt 1.2 from phase1-core-plugin-architecture.md
[ ] Build PluginLifecycleManager (libs/governance/plugins/lifecycle.py)
    - Use Prompt 1.3 from phase1-core-plugin-architecture.md
[ ] Develop ConfigurationLoader (libs/governance/plugins/config.py)
    - Use Prompt 1.4 from phase1-core-plugin-architecture.md
[ ] Create PluginMessageBus (libs/governance/plugins/messaging.py)
    - Use Prompt 1.5 from phase1-core-plugin-architecture.md
[ ] Write unit tests in tests/unit/governance/plugins/
[ ] Achieve >85% test coverage
[ ] Create config/governance/validators.yaml with sample config
[ ] Create config/governance/plugin_registry.yaml
[ ] Update STATUS.md with progress
[ ] Update TRACKER.md with completion
[ ] Create PHASE_001_COMPLETION_SUMMARY.md
[ ] Commit with proper message format
```

#### Implementation Steps

1. **Create Plugin Interface**
   ```python
   # libs/governance/plugins/base.py
   from abc import ABC, abstractmethod
   from typing import Dict, Any, Optional
   from dataclasses import dataclass
   
   @dataclass
   class PluginMetadata:
       name: str
       version: str
       description: str
       author: str
       
   class IValidatorPlugin(ABC):
       """Base interface for all validator plugins"""
       
       @abstractmethod
       async def initialize(self, config: Dict[str, Any]) -> None:
           """Initialize plugin with configuration"""
           pass
           
       @abstractmethod
       async def validate(self, context: Dict[str, Any]) -> Dict[str, Any]:
           """Execute validation logic"""
           pass
           
       @abstractmethod
       async def configure(self, config: Dict[str, Any]) -> None:
           """Update plugin configuration"""
           pass
           
       @abstractmethod
       async def teardown(self) -> None:
           """Clean up resources"""
           pass
   ```

2. **Create Configuration Structure**
   ```yaml
   # config/governance/validators.yaml
   validators:
     security_validator:
       enabled: true
       plugin: SecurityValidatorPlugin
       version: "1.0.0"
       config:
         scan_secrets: true
         check_dependencies: true
         source: "config/security_rules.yaml"
         database: "sqlite:///validators.db"
       hooks:
         - pre-commit
         - PreToolUse
       priority: 100
   ```

3. **Test Everything**
   ```bash
   pytest tests/unit/governance/plugins/ -xvs --cov=libs/governance/plugins --cov-report=term-missing
   ```

#### Afternoon Checkpoint (13:00 UTC)
- [ ] Run full test suite
- [ ] Check coverage (must be >85%)
- [ ] Update progress in TRACKER.md
- [ ] Document any blockers in STATUS.md

#### Evening Closure (17:00 UTC)
- [ ] All TodoWrite items complete
- [ ] Create PHASE_001_COMPLETION_SUMMARY.md with:
  - Components created
  - Tests written
  - Coverage achieved
  - Any issues encountered
  - Ready for Phase 2

### PHASE 2: Validator Plugin Adapter (DAY 2)

**Prerequisites:** Phase 1 complete with all tests passing

#### TodoWrite Checklist - Phase 2
```
[ ] Read phase2-validator-plugin-adapter.md for prompts
[ ] Create ValidatorPluginAdapter (libs/governance/plugins/adapter.py)
[ ] Implement PluginDiscovery (libs/governance/plugins/discovery.py)
[ ] Build ValidatorFactory (libs/governance/plugins/factory.py)
[ ] Add HotReloadManager (libs/governance/plugins/hotreload.py)
[ ] Create PluginValidator (libs/governance/plugins/validator.py)
[ ] Convert security_validator.py to plugin
[ ] Convert code_doc_validator.py to plugin
[ ] Convert documentation_validator.py to plugin
[ ] Write integration tests
[ ] Update migration documentation
[ ] Create PHASE_002_COMPLETION_SUMMARY.md
```

### PHASE 3: Hook Integration Layer (DAY 3)

**Prerequisites:** Phase 2 complete with validators converted

#### TodoWrite Checklist - Phase 3
```
[ ] Read phase3-hook-integration-layer.md for prompts
[ ] Create HookValidatorOrchestrator (libs/governance/hooks/orchestrator.py)
[ ] Build PluginAssignmentManager (libs/governance/hooks/assignment.py)
[ ] Implement HookConfigurationManager (libs/governance/hooks/config_manager.py)
[ ] Add RuntimePluginSwitcher (libs/governance/hooks/switcher.py)
[ ] Create HookEventEmitter (libs/governance/hooks/events.py)
[ ] Configure hook assignments in config/governance/hook_assignments.yaml
[ ] Integrate with pre-commit.py hook
[ ] Integrate with claude_code_governance_hook.py
[ ] Write hook integration tests
[ ] Create PHASE_003_COMPLETION_SUMMARY.md
```

### PHASE 4: Bridge Implementation (DAY 4)

**Prerequisites:** Phase 3 complete with hook integration working

#### TodoWrite Checklist - Phase 4
```
[ ] Read phase4-bridge-implementation.md for prompts
[ ] Create UniversalHookBridge (libs/governance/bridge/universal.py)
[ ] Build UnifiedValidatorInterface (libs/governance/bridge/interface.py)
[ ] Implement CrossHookMessenger (libs/governance/bridge/messenger.py)
[ ] Add StatePersistenceManager (libs/governance/bridge/persistence.py)
[ ] Create BridgeMonitor (libs/governance/bridge/monitor.py)
[ ] Configure bridge settings in config/governance/bridge.yaml
[ ] Test Claude Code hooks with Git hooks
[ ] Write bridge integration tests
[ ] Create PHASE_004_COMPLETION_SUMMARY.md
```

### PHASE 5: Testing & Documentation (DAY 5)

**Prerequisites:** All previous phases complete

#### TodoWrite Checklist - Phase 5
```
[ ] Read phase5-testing-documentation.md for prompts
[ ] Create IntegrationTestSuite (tests/integration/test_plugin_system.py)
[ ] Build PerformanceBenchmark (benchmarks/plugin_performance.py)
[ ] Implement DocumentationGenerator (tools/docs/generator.py)
[ ] Add DeploymentValidator (deploy/validator.py)
[ ] Create PluginDevelopmentKit (sdk/development_kit.py)
[ ] Run full test suite (>85% coverage required)
[ ] Generate complete documentation
[ ] Perform security audit
[ ] Create PHASE_005_COMPLETION_SUMMARY.md
[ ] Final update to all tracking documents
```

## 🚨 CRITICAL RULES

### MANDATORY GOVERNANCE
1. **NEVER** skip phases or checklist items
2. **ALWAYS** maintain >85% test coverage
3. **NEVER** use hardcoded values - everything must be configurable
4. **ALWAYS** update tracking documents in real-time
5. **NEVER** commit failing tests
6. **ALWAYS** follow bug resolution protocol on failures

### Bug Resolution Protocol
If ANY test fails or error occurs:
1. **STOP** implementation immediately
2. **Document** in DECISIONS.md:
   ```markdown
   ## Bug: [Description]
   - **Error:** [Full error message]
   - **Stack Trace:** [Complete trace]
   - **Impact:** [What's affected]
   - **Resolution:** [How fixed]
   - **Prevention:** [How to avoid in future]
   ```
3. **Update** STATUS.md with blocker
4. **Create** isolated test reproducing bug
5. **Fix** with full test coverage
6. **Verify** all existing tests pass
7. **Continue** only when resolved

### Commit Message Format
```
feat(plugin-architecture): [Phase X] Component description

- Implemented [component] with [features]
- Added tests achieving X% coverage
- Updated configuration for [purpose]

Phase: X/5 (Plugin Architecture)
Progress: Y/Z tasks complete
Tests: XX% coverage, all passing
Docs: Updated TRACKER.md, STATUS.md
Next: [Next phase description]
```

## 📊 SUCCESS METRICS

### Per-Phase Metrics
- [ ] All TodoWrite items complete
- [ ] Test coverage >85%
- [ ] All tests passing (100% required)
- [ ] Documentation updated
- [ ] No hardcoded values
- [ ] Configuration externalized
- [ ] Governance score >95%

### Overall Success
- [ ] All 5 phases complete
- [ ] Plugin architecture operational
- [ ] All validators converted
- [ ] Bridge functioning
- [ ] Production ready
- [ ] SDK published

## 🔧 CONFIGURATION TEMPLATES

### validators.yaml
```yaml
validators:
  security_validator:
    enabled: true
    plugin: SecurityValidatorPlugin
    version: "1.0.0"
    config:
      scan_secrets: true
      check_dependencies: true
      severity_threshold: "HIGH"
      source: "config/security_rules.yaml"
      database: "sqlite:///validators.db"
    hooks:
      - pre-commit
      - PreToolUse
    priority: 100
    
  code_quality_validator:
    enabled: true
    plugin: CodeQualityValidatorPlugin
    version: "1.0.0"
    config:
      min_coverage: 85
      max_complexity: 10
      source: "config/quality_rules.yaml"
    hooks:
      - pre-commit
      - PostToolUse
    priority: 90
```

### hook_assignments.yaml
```yaml
assignments:
  pre-commit:
    validators:
      - security_validator
      - code_quality_validator
      - documentation_validator
    execution_mode: parallel
    fail_fast: true
    timeout: 30
    
  PreToolUse:
    validators:
      - security_validator
      - permission_validator
    execution_mode: sequential
    fail_fast: true
    timeout: 10
    
  PostToolUse:
    validators:
      - code_quality_validator
      - format_validator
    execution_mode: parallel
    fail_fast: false
    timeout: 60
```

## 🚀 IMMEDIATE ACTIONS

1. **START NOW**: Begin Phase 1 implementation
2. **USE PROMPTS**: Open `prompts/phase1-core-plugin-architecture.md`
3. **FOLLOW TODOS**: Work through checklist systematically
4. **TEST CONTINUOUSLY**: Run tests after each component
5. **UPDATE TRACKING**: Keep STATUS.md and TRACKER.md current
6. **ASK IF BLOCKED**: Don't guess - ask for clarification

## 📝 NOTES

- Each phase builds on the previous - no skipping
- Quality over speed - better to do less perfectly
- Configuration is key - no hardcoded values
- Tests are mandatory - no exceptions
- Documentation is part of the code

## ❓ QUESTIONS TO ANSWER BEFORE STARTING

1. Do you understand the 5-phase approach?
2. Have you read CLAUDE.md governance rules?
3. Do you have access to all prompt files?
4. Is the TodoWrite checklist clear?
5. Do you understand the bug resolution protocol?

## 🎯 READY TO BEGIN?

**CONFIRM**: "I understand the requirements and am ready to begin Phase 1 implementation following all governance rules."

Then start with:
1. Create `libs/governance/plugins/` directory
2. Open `prompts/phase1-core-plugin-architecture.md`
3. Begin implementing IValidatorPlugin interface
4. Follow TodoWrite checklist exactly
5. Update tracking documents continuously

---

**Generated:** January 6, 2025  
**Version:** 1.0  
**Purpose:** Master run file for Claude Code to implement validator plugin architecture  
**Phases:** 5 (one per day)  
**Total Prompts:** 25 (5 per phase)  
**Expected Completion:** 5 days from start
