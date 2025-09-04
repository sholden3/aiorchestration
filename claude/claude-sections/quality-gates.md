# 🔒 QUALITY GATES & ENFORCEMENT

## Pre-Commit Requirements (MANDATORY)
All changes must pass these automated checks:

```bash
# Critical quality gates - must pass for any commit
./validate-task-completion.sh

# Code documentation validation (MANDATORY)
./validate-code-documentation.sh

# Project structure validation  
./validate-project-structure.sh

# Cross-system integration validation
npm run test:integration-critical
```

## Testing Coverage Requirements

### Minimum Test Coverage Standards
- **Backend**: 85% line coverage, 90% for critical modules
- **Frontend**: 80% line coverage, 85% for services
- **Integration**: 100% coverage of cross-system boundaries
- **Failure Scenarios**: All identified failure modes must have tests

### Required Test Categories
```bash
# Backend (Sarah's Domain)
python -m pytest tests/ --cov=. --cov-fail-under=85
python -m pytest tests/integration/ -v  
python -m pytest tests/test_failure_modes.py -v

# Frontend (Alex's Domain)
ng test --watch=false --code-coverage
ng e2e --suite=critical-path
npm run test:memory-leaks

# Cross-System (Both Architects)
npm run test:electron-backend-coordination
npm run test:websocket-integration
npm run test:failure-cascades
```

## Documentation Currency Requirements
- **CLAUDE.md**: Updated within 7 days of any major change
- **Fix Documentation**: Created within 24 hours of issue identification  
- **Architecture Docs**: Updated within 48 hours of system changes
- **Runbooks**: Verified monthly and after any production incident

## Archival Rules (Mandatory)
**All file replacements must follow this protocol:**

### 1. Pre-Archival Approval
Both Alex and Sarah must approve before any file is archived

### 2. Archive Structure
```
archive/
├── test_infrastructure/     # Test-related files
├── backend_components/       # Backend service files  
├── frontend_components/      # Frontend/Angular files
└── documentation/           # Superseded documentation
```

### 3. Archive Naming Convention
`YYYY-MM-DD_original-filename_v{version}_issue{issue-number}.ext`
Example: `2025-08-26_test-setup-electron_v1_issueH2.ts`

### 4. Required Metadata (in accompanying README.md)
- **Approved By**: Both architects' sign-off
- **Related Issue**: C1-C3, H1-H3, or feature reference
- **Reason for Replacement**: Specific bugs or enhancements
- **Performance Metrics**: Before/after if applicable
- **Rollback Instructions**: How to restore if needed
- **Dependencies**: What else might be affected

### 5. Rollback Strategy
- Archived files must remain functional
- Test suite must validate archived version compatibility
- Maximum 5-minute rollback time requirement

## Project Structure Enforcement
Required directory structure (validated automatically):
```
docs/
├── fixes/              # All issues and solutions
├── architecture/       # System design documentation
├── processes/          # Development processes
└── runbooks/          # 3 AM debugging procedures

tests/
├── integration/        # Cross-system tests
├── performance/        # Performance validation
└── failure-scenarios/  # Failure mode tests
```

## Development Commands

```bash
# Start Backend
cd ai-assistant/backend && python main.py

# Start Frontend
cd ai-assistant && npm run electron:dev

# Build Production
npm run build && npm run electron:build

# Check for Issues
npm run lint
npm run typecheck
```

## Debugging Commands

```bash
# Find magic numbers
grep -rn "\b[0-9]\{3,\}\b" src/ --include="*.ts"

# Check memory usage
ps -o pid,vsz,rss,comm -p $(pgrep -f "electron")

# Find IPC listeners
grep -r "addEventListener\|on\|once" src/ --include="*.ts" | grep -i ipc

# Check for cleanup
grep -r "removeEventListener\|off\|removeAllListeners" src/ --include="*.ts"
```

## 🆘 EMERGENCY DEBUGGING (3 AM PROCEDURES)

### Backend Down
```bash
# Check Python process
ps aux | grep python | grep main.py

# Check port conflicts
netstat -an | grep :8000

# Check logs
tail -f ai-assistant/backend/logs/app.log

# Emergency restart
cd ai-assistant/backend && python main.py
```

### Frontend Unresponsive
```bash
# Check Electron processes
ps aux | grep electron

# Check IPC connectivity
# In Electron DevTools: window.electronAPI

# Memory usage check
# DevTools → Memory tab → Heap Snapshots

# Emergency restart
npm run electron:dev
```

### Memory Leak Investigation
```bash
# Backend memory check
ps -o pid,vsz,rss,comm -p $(pgrep -f "python.*main.py")

# Frontend memory check  
# Electron DevTools → Performance → Memory

# Specific leak patterns to check
grep -r "addEventListener\|removeEventListener" src/
grep -r "setInterval\|setTimeout" src/
```