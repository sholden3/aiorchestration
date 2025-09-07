# Deprecation Tracker - Plugin Architecture Migration

## Overview
This document tracks code that will become obsolete after the full implementation of the new validator plugin architecture (Phases 1-5).

## Timeline
- **Phase 1** (COMPLETED): Core plugin architecture
- **Phase 2** (PENDING): Validator plugin adapter
- **Phase 3** (PENDING): Hook integration layer
- **Phase 4** (PENDING): Bridge implementation
- **Phase 5** (PENDING): Testing & documentation

## Code to be Deprecated

### 1. Old Validator System (`libs/governance/validators/`)
**Status**: Will be deprecated after Phase 2
**Files**:
- `libs/governance/validators/documentation_validator.py`
- `libs/governance/validators/code_doc_validator.py`
- `libs/governance/validators/security_validator.py`
- `libs/governance/validators/` (entire directory)

**Replacement**: 
- New plugin-based validators in `libs/governance/plugins/validators/`
- Each validator becomes a plugin implementing `IValidatorPlugin`

**Migration Notes**:
- Existing validators need to be wrapped in plugin adapters (Phase 2)
- Configuration moves from hardcoded to `config/governance/validators.yaml`

### 2. Old Hook System (`libs/governance/hooks/`)
**Status**: Will be deprecated after Phase 3
**Files**:
- `libs/governance/hooks/pre_commit_hook.py`
- `libs/governance/hooks/claude_code_governance_hook.py`
- Individual validator imports in hooks

**Replacement**:
- Unified hook bridge using `PluginLifecycleManager`
- Hook assignments in `config/governance/validators.yaml`

**Migration Notes**:
- Hooks will call plugin system instead of individual validators
- Configuration-driven hook assignments

### 3. Old Governance Engine (`governance/`)
**Status**: Partially deprecated after Phase 4
**Files**:
- `governance/core/engine.py`
- `governance/core/enhanced_governance_engine.py`
- `governance/validators/` (if exists)

**Replacement**:
- `libs/governance/plugins/` (new unified system)
- `PluginRegistry` + `PluginLifecycleManager` replace engine

**Migration Notes**:
- Some core governance concepts remain
- Engine functionality distributed across plugin components

### 4. Hardcoded Configurations
**Status**: Already deprecated
**Files**:
- Hardcoded validator settings in Python files
- Inline configuration in hooks
- Static validator lists

**Replacement**:
- `config/governance/validators.yaml`
- `config/governance/plugin_registry.yaml`
- `config/governance/lifecycle.yaml`

### 5. Old Test Structure
**Status**: Needs reorganization (current cleanup)
**Files**:
- `tests/governance/test_*.py` (scattered tests)
- `tests/unit/test_plugin_*.py` (duplicate tests)
- Tests without proper structure

**Replacement**:
- `tests/unit/governance/plugins/` (organized structure)
- One test file per component
- Proper fixture management

## Code Bloat Analysis

### Duplicate Functionality
1. **Configuration Loading**:
   - OLD: Multiple config loaders in different modules
   - NEW: Single `ConfigurationLoader` in `libs/governance/plugins/config.py`

2. **Message Passing**:
   - OLD: Direct function calls between validators
   - NEW: `PluginMessageBus` for all inter-plugin communication

3. **State Management**:
   - OLD: Each validator manages its own state
   - NEW: `PluginLifecycleManager` handles all plugin states

### Files to Remove (After Full Migration)
```
# After Phase 2
rm -rf libs/governance/validators/

# After Phase 3
rm libs/governance/hooks/old_*.py

# After Phase 4
rm governance/core/engine.py
rm governance/core/enhanced_governance_engine.py

# After Phase 5
# Clean up old test files
```

## Migration Strategy

### Phase-by-Phase Removal
1. **Phase 1**: No removals (building foundation)
2. **Phase 2**: Mark old validators as deprecated
3. **Phase 3**: Mark old hooks as deprecated
4. **Phase 4**: Remove deprecated validators and hooks
5. **Phase 5**: Final cleanup and removal

### Backward Compatibility
- Maintain adapter layer during transition
- Configuration migration tools
- Deprecation warnings before removal

## Current Cleanup Tasks (Phase 1)

### Immediate Actions
1. **DO NOT DELETE** old validators yet (needed for Phase 2 migration)
2. **DO NOT DELETE** old hooks yet (needed for Phase 3 integration)
3. **DO** organize new test files properly
4. **DO** fix governance violations in new code
5. **DO** document deprecation plans

### Test File Consolidation
```bash
# Move scattered tests to proper location
tests/unit/governance/plugins/
├── test_base.py (from test_plugin_base*.py)
├── test_registry.py (from test_plugin_registry*.py)
├── test_lifecycle.py
├── test_config.py
├── test_messaging.py
└── test_integration.py
```

## Documentation Updates Needed

### Files to Update
1. **CLAUDE.md**: Add deprecation timeline
2. **STATUS.md**: Note deprecated components
3. **README.md**: Update architecture section
4. **TRACKER.md**: Add deprecation milestones

### New Documentation
1. **Migration Guide**: How to convert old validators to plugins
2. **Plugin Development Guide**: How to create new plugins
3. **Deprecation Timeline**: Clear schedule for removals

## Metrics

### Code Reduction Estimates
- **Lines of Code**: ~30% reduction after full migration
- **File Count**: ~40% fewer files
- **Complexity**: ~50% reduction in cyclomatic complexity
- **Configuration**: 100% externalized (no hardcoded values)

### Performance Improvements
- **Startup Time**: Lazy loading via plugin system
- **Memory Usage**: Plugins loaded on demand
- **Test Speed**: Parallel test execution
- **Maintenance**: Single point of configuration

## Risk Mitigation

### Backup Strategy
- Git branch for old code: `backup/pre-plugin-architecture`
- Archive old validators before deletion
- Document all removed functionality

### Rollback Plan
- Phase checkpoints for easy rollback
- Adapter layer maintains compatibility
- Configuration can switch between old/new

## Next Steps

1. **Complete Phase 1 Cleanup** (Current)
2. **Document deprecated code** in each file
3. **Add deprecation warnings** to old code
4. **Create migration scripts** for Phase 2
5. **Update all documentation** with deprecation notes

---

**Last Updated**: January 6, 2025
**Phase**: 1 of 5
**Status**: Tracking deprecations for cleanup