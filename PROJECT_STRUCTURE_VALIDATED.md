# Project Structure Validation Map

**Last Updated:** September 7, 2025  
**Purpose:** Track which files/folders are necessary vs deprecated  
**Legend:**  
- ✅ VALIDATED - Required and actively used
- ⚠️ REVIEW - May need refactoring or consolidation  
- ❌ DEPRECATED - Marked for removal
- 🔄 MIGRATING - In process of migration

## Root Directory
```
ClaudeResearchAndDevelopment/
├── .archive/                           ⚠️ REVIEW - Contains old code, may need cleanup
├── .docs-metadata/                     ✅ VALIDATED - Documentation metadata
├── .governance/                        ✅ VALIDATED - Governance audit logs
│   ├── audit/                          ✅ VALIDATED - Audit trail
│   └── correlations/                   ✅ VALIDATED - Correlation tracking
├── .vscode/                            ✅ VALIDATED - VS Code settings
├── apps/                               ✅ VALIDATED - Application layer
│   ├── api/                            ✅ VALIDATED - Backend API
│   │   ├── core/                       ✅ VALIDATED - Core backend services
│   │   └── mcp/                        ✅ VALIDATED - MCP governance server
│   ├── desktop/                        ✅ VALIDATED - Electron wrapper
│   └── web/                            ✅ VALIDATED - Angular frontend
├── config/                             ✅ VALIDATED - Centralized configuration
│   ├── governance/                     ✅ VALIDATED - Governance configs
│   │   ├── validators.yaml             ✅ VALIDATED - Plugin validator config
│   │   ├── plugin_registry.yaml        ✅ VALIDATED - Registry config
│   │   ├── lifecycle.yaml              ✅ VALIDATED - Lifecycle settings
│   │   ├── personas.yaml               ✅ VALIDATED - AI personas
│   │   ├── rules.yaml                  ✅ VALIDATED - Governance rules
│   │   └── standards.yaml              ✅ VALIDATED - Documentation standards
│   └── schemas/                        ✅ VALIDATED - JSON/YAML schemas
├── docs/                               ✅ VALIDATED - Documentation
│   ├── architecture/                   ✅ VALIDATED - Architecture docs
│   │   ├── plugin-system.md            ✅ VALIDATED - NEW plugin architecture
│   │   ├── api-contracts.md            ✅ VALIDATED - API specifications
│   │   ├── backend.md                  ✅ VALIDATED - Backend architecture
│   │   ├── database.md                 ✅ VALIDATED - Database design
│   │   ├── frontend.md                 ✅ VALIDATED - Frontend architecture
│   │   └── security.md                 ✅ VALIDATED - Security patterns
│   ├── fixes/                          ✅ VALIDATED - Bug fix documentation
│   │   └── message-comparison-fix.md   ✅ VALIDATED - Message class fix
│   ├── migration-reports/              ✅ VALIDATED - Migration history
│   └── testing/                        ✅ VALIDATED - Test documentation
├── examples/                           ✅ VALIDATED - Example implementations
│   └── messaging_example.py            ✅ VALIDATED - Message bus example
├── governance/                         🔄 MIGRATING - Old governance system
│   ├── audit/                          ⚠️ REVIEW - May be duplicate of .governance
│   ├── config.yaml                     ❌ DEPRECATED - Moved to config/governance/
│   ├── core/                           ❌ DEPRECATED - Being replaced by plugin system
│   │   ├── engine.py                   ❌ DEPRECATED - Old governance engine
│   │   ├── context.py                  ⚠️ REVIEW - May still be needed
│   │   ├── correlation_tracker.py      ⚠️ REVIEW - May still be needed
│   │   └── session_manager.py          ⚠️ REVIEW - May still be needed
│   ├── hooks/                          ❌ DEPRECATED - Replaced by plugin hooks
│   ├── middleware/                     ⚠️ REVIEW - May need migration
│   ├── personas.py                     ❌ DEPRECATED - Use config/governance/personas.yaml
│   ├── rules/                          ❌ DEPRECATED - Replaced by plugin rules
│   └── validators/                     ❌ DEPRECATED - Replaced by plugin validators
├── libs/                               ✅ VALIDATED - Shared libraries
│   ├── governance/                     🔄 MIGRATING - Governance library
│   │   ├── plugins/                    ✅ VALIDATED - NEW plugin system
│   │   │   ├── base.py                 ✅ VALIDATED (91.80% coverage)
│   │   │   ├── registry.py             ✅ VALIDATED (88.20% coverage)
│   │   │   ├── lifecycle.py            ✅ VALIDATED (75.84% coverage)
│   │   │   ├── config.py               ✅ VALIDATED (91.22% coverage)
│   │   │   ├── messaging.py            ✅ VALIDATED (88.49% coverage)
│   │   │   └── validators/             ✅ VALIDATED - Plugin validators
│   │   ├── core/                       ❌ DEPRECATED - Old core system
│   │   ├── hooks/                      ❌ DEPRECATED - Old hooks
│   │   ├── middleware/                 ⚠️ REVIEW - May need migration
│   │   ├── rules/                      ❌ DEPRECATED - Old rules
│   │   └── validators/                 ❌ DEPRECATED - Old validators
│   ├── shared-types/                   ✅ VALIDATED - Shared TypeScript/Python types
│   └── shared-utils/                   ✅ VALIDATED - Shared utilities
├── prompts/                            ✅ VALIDATED - GitHub Copilot prompts
│   ├── phase1-core-plugin-architecture.md     ✅ VALIDATED
│   ├── fix-plugin-base-test-timing.md         ✅ VALIDATED
│   └── fix-message-comparison-issue.md        ✅ VALIDATED
├── reports/                            ✅ VALIDATED - System reports
├── research/                           ✅ VALIDATED - MCP research
├── tests/                              ✅ VALIDATED - Test suites
│   ├── integration/                    ✅ VALIDATED - Integration tests
│   └── unit/                           ✅ VALIDATED - Unit tests
│       └── governance/                 
│           └── plugins/                ✅ VALIDATED - Plugin tests (167 passing)
│               ├── test_plugin_base.py         ✅ VALIDATED
│               ├── test_config.py              ✅ VALIDATED
│               ├── test_lifecycle.py           ✅ VALIDATED
│               ├── test_messaging.py           ✅ VALIDATED
│               ├── test_plugin_registry.py     ✅ VALIDATED
│               └── test_plugin_registry_integration.py  ✅ VALIDATED
├── tools/                              ✅ VALIDATED - Development tools
│   ├── ci/                             ✅ VALIDATED - CI/CD pipelines
│   ├── docker/                         ✅ VALIDATED - Docker configs
│   └── scripts/                        ✅ VALIDATED - Utility scripts
├── CLAUDE.md                           ✅ VALIDATED - AI assistant instructions
├── DECISIONS.md                        ✅ VALIDATED - Architecture decisions
├── DEPRECATION_TRACKER.md              ✅ VALIDATED - Deprecation tracking
├── DOCUMENTATION_INDEX.md              ✅ VALIDATED - Doc index
├── Makefile                            ✅ VALIDATED - Build automation
├── PHASE_001_COMPLETION_SUMMARY.md     ✅ VALIDATED - Phase 001 completion
├── PROJECT_STRUCTURE_VALIDATED.md      ✅ VALIDATED - This file
├── README.md                           ✅ VALIDATED - Project overview
├── STATUS.md                           ✅ VALIDATED - System health
├── TRACKER.md                          ✅ VALIDATED - Task tracking
├── package.json                        ✅ VALIDATED - Node dependencies
├── project.yaml                        ✅ VALIDATED - Project metadata
├── pytest.ini                          ✅ VALIDATED - Test configuration
├── requirements.txt                    ✅ VALIDATED - Python dependencies
└── setup.py                            ✅ VALIDATED - Python setup

## Summary Statistics

### Validation Status
- ✅ **VALIDATED:** 75 items (65%)
- ⚠️ **REVIEW:** 8 items (7%)
- ❌ **DEPRECATED:** 28 items (24%)
- 🔄 **MIGRATING:** 5 items (4%)

### Key Findings
1. **30% of codebase marked for deprecation** (mainly old governance system)
2. **New plugin system fully validated** with >85% test coverage
3. **Configuration successfully centralized** in config/ directory
4. **Documentation structure validated** and up-to-date

### Deprecated Components to Remove
```
Total files to remove: ~50
Estimated code reduction: 30%
Main targets:
- governance/core/* (old engine)
- governance/validators/* (15+ old validators)
- governance/hooks/* (old hooks system)
- governance/rules/* (old rules)
- libs/governance/core/* (duplicate of governance/core)
- libs/governance/validators/* (old validators)
- libs/governance/hooks/* (old hooks)
- libs/governance/rules/* (old rules)
```

### Active Components (Critical Path)
```
Core System:
- libs/governance/plugins/* (NEW - plugin architecture)
- apps/api/core/* (backend services)
- apps/api/mcp/* (MCP governance)
- config/governance/* (all configuration)
- tests/unit/governance/plugins/* (plugin tests)
```

### Migration Priority
1. **Immediate:** Remove test files already archived
2. **Phase 2:** Migrate remaining validators to plugins
3. **Phase 3:** Remove old governance/core
4. **Phase 4:** Clean up governance/validators
5. **Phase 5:** Remove all deprecated components

## Usage

This document should be updated whenever:
- New files/folders are added
- Components are deprecated
- Migration status changes
- Validation status changes

Use this as a reference for:
- Refactoring decisions
- Code cleanup tasks
- Import path updates
- Dependency analysis