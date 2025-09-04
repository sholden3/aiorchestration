# 🔧 QUICK START (ACTUAL WORKING INSTRUCTIONS)

## Prerequisites
- Node.js 18+
- Python 3.10+  
- PostgreSQL 14+ (optional - falls back to mock)
- Git (for terminal emulation on Windows)

## Development Setup
```bash
# 1. Backend Setup (Sarah's domain)
cd ai-assistant/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Frontend Setup (Alex's domain)  
cd ai-assistant
npm install
npm rebuild node-pty  # Important for terminal support

# 3. Configuration Fix (Critical - addresses C3)
# Edit electron/main.js: Change backendPort from 8001 to 8000
```

## Running the System
```bash
# Terminal 1: Start Backend (port 8000)
cd ai-assistant/backend  
python main.py

# Terminal 2: Start Frontend
cd ai-assistant
npm run electron:dev
```

## Health Verification
```bash
# Backend Health Check
curl http://localhost:8000/health

# WebSocket Connection Test
# Open browser dev tools in Electron app, check WebSocket connection

# Database Status (if PostgreSQL available)
curl http://localhost:8000/db/status
```

## 🛠️ QUICK COMMAND REFERENCE

### Testing Commands
```bash
# Frontend Testing (Alex's Domain)
cd ai-assistant
npm test                              # Run all tests
npm test -- --testPathPattern=ipc     # Run specific test file pattern
npm test -- --testNamePattern="should handle"  # Run specific test by name
npm test -- --coverage                # Generate coverage report
npm test -- --passWithNoTests         # Run even if no tests found

# Backend Testing (Sarah's Domain)  
cd ai-assistant/backend
python -m pytest                      # Run all backend tests
python -m pytest -v                   # Verbose output
python -m pytest --cov=.              # With coverage
python -m pytest -k "test_cache"      # Run specific tests

# Integration Testing
npm run test:integration              # Cross-system tests
```

### Development Commands
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

### Debugging Commands
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

## Comprehensive Governance Framework
For complete governance procedures, see: `docs/processes/governance-framework.md`

**Key Framework Components:**
- **Session Management**: Mandatory start/end validation protocols
- **Quality Gates**: Automated testing and validation requirements  
- **Documentation Standards**: Currency requirements and templates
- **Emergency Procedures**: Critical issue response protocols
- **Process Enforcement**: Git hooks and automated validation

**Implementation Commands:**
```bash
# Install governance framework
curl -O docs/processes/governance-framework.md
chmod +x validate-*.sh

# Daily workflow integration
alias start-work='./validate-session-start.sh'
alias finish-work='./validate-task-completion.sh'  
alias check-ready='./validate-project-structure.sh'
```

**Enforcement Level**: MANDATORY - No exceptions for production commits