# Enterprise Monorepo Restructuring Plan
**Project:** AI Orchestration Platform  
**Date Created:** September 4, 2025  
**Timeline:** 9 Days (Sept 5-13, 2025)  
**Status:** 🔄 APPROVED - Ready for Execution

---

## Executive Summary

Following the successful recovery from power outage and zip archive extraction, this plan outlines the migration from our current fragmented structure to an enterprise-grade monorepo architecture. The restructuring will resolve governance import issues, eliminate duplicate directories, and establish scalable patterns for future growth.

## Current State Analysis

### Problems Identified
1. **Broken Imports**: Governance system split between `./governance/` and `./.governance/`
2. **Structural Fragmentation**: Applications nested under `apps/` instead of clear separation
3. **Recovery Artifacts**: 16+ archive folders cluttering the repository
4. **Missing Infrastructure**: No dedicated tools, libraries, or infrastructure directories
5. **Naming Inconsistencies**: Mixed conventions across the codebase

### Git Status Summary
- **Modified Files**: 10+ configuration files
- **Added Files**: 200+ new/recovered files
- **Renamed/Moved**: 50+ files from docs reorganization
- **Deleted**: Some governance files from old location

## Target Architecture

```
aiorchestration/
├── apps/                          # Application entry points
│   ├── api/                       # Python FastAPI backend
│   │   ├── main.py               # Entry point
│   │   ├── app/                  # Core application
│   │   ├── requirements.txt      
│   │   └── Dockerfile            
│   ├── web/                      # Angular frontend
│   │   ├── src/                  
│   │   ├── angular.json          
│   │   ├── package.json          
│   │   └── Dockerfile            
│   └── desktop/                  # Electron wrapper
│       └── main.js               
├── libs/                         # Shared libraries
│   ├── governance/               # Consolidated governance system
│   │   ├── validators/          
│   │   ├── core/                
│   │   └── hooks/               
│   ├── shared-types/            # TypeScript/Python shared models
│   └── shared-utils/            # Common utilities
├── tools/                        # Development tools
│   ├── scripts/                 # Dev scripts
│   ├── docker/                  # Container configs
│   └── ci/                      # CI/CD pipelines
├── infrastructure/               # Infrastructure as Code
├── tests/                        # Test suites
├── docs/                         # Documentation
└── [Root config files]
```

## Migration Phases

### Phase 1: Governance Consolidation (Days 1-2)
**Owner:** Dr. Sarah Chen  
**Priority:** CRITICAL

#### Tasks:
- [ ] Create `libs/governance/` directory structure
- [ ] Merge `.governance/` contents into `governance/`
- [ ] Move consolidated governance to `libs/governance/`
- [ ] Update all import statements:
  - From: `from governance.core.runtime_governance import ...`
  - To: `from libs.governance.core.runtime_governance import ...`
- [ ] Update PYTHONPATH in all scripts
- [ ] Test all 27 validator tests pass
- [ ] Verify pre-commit hooks function

#### Quality Gates:
- ✅ All governance tests passing
- ✅ Pre-commit hooks operational
- ✅ No import errors

### Phase 2: Core Structure Creation (Days 3-4)
**Owner:** Alex Novak & Dr. Sarah Chen  
**Priority:** HIGH

#### Tasks:
- [ ] Create directory structure:
  ```bash
  mkdir -p apps/{api,web,desktop}
  mkdir -p libs/{shared-types,shared-utils}
  mkdir -p tools/{scripts,docker,ci}
  mkdir -p infrastructure/{terraform,kubernetes}
  ```
- [ ] Move backend:
  - `apps/api/` → `apps/api/`
  - Update all Python import paths
  - Update Docker build contexts
- [ ] Move frontend:
  - `apps/web/src/` → `apps/web/src/`
  - Update angular.json workspace paths
  - Update tsconfig.json paths
- [ ] Move electron:
  - `apps/desktop/` → `apps/desktop/`
  - Update package.json paths

#### Quality Gates:
- ✅ Backend starts successfully
- ✅ Frontend builds without errors
- ✅ All import paths resolved

### Phase 3: Shared Libraries Extraction (Days 5-6)
**Owner:** Alex Novak  
**Priority:** MEDIUM

#### Tasks:
- [ ] Create `libs/shared-types/`:
  - Extract common TypeScript interfaces
  - Extract Python Pydantic models
  - Create index exports
- [ ] Create `libs/shared-utils/`:
  - Extract validation functions
  - Extract common helpers
  - Create unified constants
- [ ] Update all imports to use shared libraries
- [ ] Create library package.json/pyproject.toml files

#### Quality Gates:
- ✅ No circular dependencies
- ✅ All shared code properly typed
- ✅ Libraries independently buildable

### Phase 4: Tools Infrastructure (Days 7-8)
**Owner:** David Park  
**Priority:** MEDIUM

#### Tasks:
- [ ] Create `tools/scripts/`:
  - `setup-dev.sh` - Development environment setup
  - `reset-db.sh` - Database reset
  - `run-tests.sh` - Test execution
- [ ] Create `tools/docker/`:
  - `docker-compose.yml` - Development environment
  - `docker-compose.prod.yml` - Production config
  - Service configurations
- [ ] Create root `Makefile`:
  ```makefile
  setup: ## Setup development environment
  dev: ## Start development services
  test: ## Run all tests
  lint: ## Lint all code
  build: ## Build all applications
  ```
- [ ] Create `tools/ci/`:
  - GitHub Actions workflows
  - CI/CD pipeline configurations

#### Quality Gates:
- ✅ All scripts executable and tested
- ✅ Docker compose working
- ✅ Makefile commands functional

### Phase 5: Archive Cleanup (Day 9)
**Owner:** Marcus Thompson  
**Priority:** LOW

#### Tasks:
- [ ] Backup critical files from `.archive/`
- [ ] Remove `.archive/` directory
- [ ] Remove old `apps/` directory structure
- [ ] Clean up duplicate files
- [ ] Remove zip archives after verification
- [ ] Update .gitignore

#### Quality Gates:
- ✅ No critical files lost
- ✅ Repository size reduced
- ✅ Clean git status

## Documentation Updates

**Owner:** Isabella Martinez  
**Timeline:** Synchronized with each phase

### Required Updates:
- [ ] `CLAUDE.md` - Update all paths and structure
- [ ] `README.md` - Update installation instructions
- [ ] `DOCUMENTATION_INDEX.md` - Update file references
- [ ] `docs/architecture/*.md` - Update architecture diagrams
- [ ] `docs/processes/current-phase.md` - Update workflows
- [ ] All setup and development guides

### Validation Requirements:
- All markdown files must score >70%
- All code examples must be tested
- All paths must be verified

## Risk Mitigation

### Backup Strategy
1. Create full backup before migration: `git checkout -b pre-migration-backup`
2. Tag current working state: `git tag v2.1-pre-migration`
3. Archive recovery zips to external location

### Rollback Procedure
```bash
# If critical failure occurs:
git checkout main
git reset --hard v2.1-pre-migration
# Restore from backup branch if needed
```

### Testing Checkpoints
- After each phase completion
- Full test suite execution
- Governance validation
- Documentation validation

## Success Metrics

### Quantitative Metrics
- [ ] 100% of tests passing
- [ ] 0 import errors
- [ ] >95% governance compliance maintained
- [ ] >70% documentation validation scores
- [ ] <10% increase in build times

### Qualitative Metrics
- [ ] Improved developer navigation (Emergency Test <30 seconds)
- [ ] Clearer separation of concerns
- [ ] Reduced cognitive load
- [ ] Better IDE integration

## Communication Plan

### Daily Standups
- **Time:** 9:00 AM EST
- **Duration:** 15 minutes
- **Format:** Progress, Blockers, Next Steps

### Progress Tracking
- Update this document daily
- Create migration log in `temp/migration_log.md`
- Post updates to team channel

## Immediate Next Steps

1. **Create migration branch:**
   ```bash
   git checkout -b feature/enterprise-restructure
   ```

2. **Backup current state:**
   ```bash
   git add .
   git commit -m "chore: Pre-migration checkpoint"
   git tag v2.1-pre-migration
   ```

3. **Begin Phase 1:**
   - Start governance consolidation
   - Create initial directory structure
   - Update first set of imports

## Approval Signatures

- **Steven Holden (Owner):** ✅ Approved
- **Dr. Sarah Chen (Backend):** ✅ Approved
- **Alex Novak (Frontend):** ✅ Approved
- **Marcus Thompson (QA):** ✅ Approved
- **David Park (DevEx):** ✅ Approved
- **Isabella Martinez (Docs):** ✅ Approved

---

**Document Status:** APPROVED - Ready for execution  
**Next Review:** September 5, 2025 (Day 1 checkpoint)  
**Questions:** Contact Steven Holden or Dr. Sarah Chen

---

*"The best time to restructure is when you have clarity on both the problem and the solution. We have both."*