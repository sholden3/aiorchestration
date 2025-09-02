# 🎯 ACTIVE CODE MANIFEST
## Operation Phoenix - Critical Files to Preserve

**Generated**: 2025-09-02 12:25:00  
**Purpose**: Identify ONLY essential files to keep  
**Everything else**: DELETE (with backup)  

---

## ✅ KEEPER FILES - Backend (Python)

### Core API Files
```yaml
backend/main.py                     # FastAPI main application
backend/database_service.py         # Database connection service
backend/circuit_breaker.py          # New resilience pattern
backend/config.py                    # Configuration management
backend/updated_api_endpoints.py    # Current API routes
backend/websocket_manager.py        # WebSocket connections
backend/cache_service.py             # Caching layer
backend/metrics_service.py           # Metrics collection
backend/persona_manager.py          # Persona management
backend/governance_service.py       # Governance integration
```

### Backend Models & Types
```yaml
backend/models.py                   # Data models
backend/schemas.py                   # Pydantic schemas
backend/types.py                     # Type definitions
```

### Backend Requirements
```yaml
backend/requirements.txt            # Python dependencies
backend/pytest.ini                   # Test configuration
```

---

## ✅ KEEPER FILES - Frontend (Angular/TypeScript)

### Core Angular Application
```yaml
src/app/app.component.ts            # Main app component
src/app/app.component.html          # Main app template
src/app/app.component.css           # Main app styles
src/app/app.module.ts               # App module
src/app/app-routing.module.ts      # Routing configuration
```

### Active Components
```yaml
src/app/components/dashboard/       # Dashboard component
src/app/components/chat/            # Chat interface
src/app/components/settings/        # Settings panel
src/app/components/terminal/        # Terminal component
src/app/components/file-explorer/   # File explorer
```

### Core Services
```yaml
src/app/services/api.service.ts     # API communication
src/app/services/websocket.service.ts # WebSocket service
src/app/services/auth.service.ts    # Authentication
src/app/services/ipc.service.ts     # IPC communication
src/app/services/terminal.service.ts # Terminal service
```

### Models & Interfaces
```yaml
src/app/models/                     # All TypeScript interfaces
src/app/types/                      # Type definitions
```

### Configuration Files
```yaml
src/angular.json                    # Angular configuration
src/tsconfig.json                   # TypeScript config
src/package.json                    # NPM dependencies
src/package-lock.json              # Dependency lock file
```

---

## ✅ KEEPER FILES - Electron

### Main Process
```yaml
electron/main.js                    # Electron main process
electron/preload.js                 # Preload script
electron/ipc-handlers.js           # IPC handlers
electron/window-manager.js         # Window management
```

---

## ✅ KEEPER FILES - Tests (Consolidated)

### Backend Tests
```yaml
tests/backend/unit/                 # Unit tests
tests/backend/integration/          # Integration tests
tests/backend/conftest.py          # Pytest fixtures
```

### Frontend Tests
```yaml
tests/frontend/unit/                # Component tests
tests/frontend/integration/         # Integration tests
tests/frontend/e2e/                # E2E tests
```

---

## ✅ KEEPER FILES - Documentation

### Critical Documentation
```yaml
CLAUDE.md                           # Project instructions
README.md                           # Main readme
DECISIONS.md                        # Architectural decisions
PERSONAS.md                         # Persona definitions
DOCUMENTATION_INDEX.md              # Documentation map
OPERATION_PHOENIX_TRACKER.md       # Current operation tracker
PROJECT_ARCHAEOLOGY_INVENTORY.md    # Archaeology findings
ACTIVE_CODE_MANIFEST.md            # This file
```

### Architecture Documentation
```yaml
docs/architecture/                  # Architecture decisions
docs/claude-sections/               # CLAUDE.md sections
docs/processes/                     # Process documentation
```

---

## ✅ KEEPER FILES - Governance

### Governance System (KEEP AS-IS)
```yaml
.governance/                        # Entire governance system
governance/                         # Governance modules
governance-config/                  # Governance configuration
```

---

## ✅ KEEPER FILES - Configuration

### Root Configuration
```yaml
.gitignore                          # Git ignore rules
.env.example                        # Environment template
pyproject.toml                      # Python project config
jest.config.js                      # Jest configuration
```

---

## 🗑️ DELETE EVERYTHING ELSE

### Specifically DELETE:
- ALL of `/archive` directory (already archived!)
- ALL test directories except `/tests`
- ALL example code
- ALL nested projects
- ALL duplicate implementations
- ALL experimental features not in production
- ALL old API versions
- ALL deprecated components
- ALL unused migrations
- ALL cache directories
- ALL build artifacts
- ALL log files
- ALL temporary files

### DELETE Patterns:
```yaml
**/__pycache__/                    # Python cache
**/node_modules/                   # Node modules
**/dist/                          # Build output
**/build/                         # Build output
**/coverage/                      # Coverage reports
**/htmlcov/                       # HTML coverage
**/.pytest_cache/                 # Pytest cache
**/*.pyc                          # Python compiled
**/*.pyo                          # Python optimized
**/*.log                          # Log files
**/tmp/                           # Temporary files
**/temp/                          # Temporary files
```

---

## 📊 Summary Statistics

### Files to Keep
```yaml
Backend:        ~25 files
Frontend:       ~40 files
Electron:       ~5 files
Tests:          ~30 files
Documentation:  ~20 files
Governance:     ~30 files
Configuration:  ~10 files
TOTAL KEEP:     ~160 files
```

### Files to Delete
```yaml
Current Total:  ~2000 files
Keep:           ~160 files
DELETE:         ~1840 files
Reduction:      92%
```

---

## ⚠️ VALIDATION CHECKLIST

Before deleting, verify:
- [ ] Full backup completed
- [ ] All keeper files identified
- [ ] Dependencies documented
- [ ] Import paths mapped
- [ ] No active PR dependencies
- [ ] Team notification sent

---

## 🚀 EXECUTION PLAN

1. **Backup** - Complete project backup
2. **Copy Keepers** - Copy keeper files to temp location
3. **Nuclear Delete** - Delete everything except governance
4. **Restore Keepers** - Move keeper files back
5. **Validate** - Test all functionality
6. **Commit** - Commit the cleanup

---

**Manifest Status**: COMPLETE  
**Keeper Files**: ~160  
**Delete Files**: ~1840  
**Reduction**: 92%  

*"Keep only what sparks joy... or compiles"* - Marie Kondo, if she were a developer