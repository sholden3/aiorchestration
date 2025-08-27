# Orchestrated Development Governance Framework
**Version**: 1.0  
**Architects**: Alex Novak & Dr. Sarah Chen  
**Purpose**: Ensure systematic quality enforcement across all development activities

---

## 🔄 SESSION MANAGEMENT PROTOCOL

### Session Initialization (MANDATORY)
Every development session MUST begin with this validation sequence:

```bash
# SESSION START CHECKLIST
echo "=== SESSION INITIALIZATION ==="
echo "Date: $(date)"
echo "Architects: Alex Novak & Dr. Sarah Chen active"
echo ""

# 1. SYSTEM STATE VALIDATION
echo "🔍 SYSTEM STATE VALIDATION"
cd ai-assistant/backend
python -c "import main; print('✅ Backend imports work')" || echo "❌ Backend import failure"
cd ../
npm run build --silent && echo "✅ Frontend builds" || echo "❌ Frontend build failure"
echo ""

# 2. TEST BASELINE VALIDATION  
echo "🧪 TEST BASELINE VALIDATION"
cd ai-assistant/backend
python -m pytest --co -q | wc -l | xargs echo "Backend tests available:"
cd ../
npm test -- --passWithNoTests --silent && echo "✅ Frontend tests pass" || echo "❌ Frontend test failure"
echo ""

# 3. CRITICAL SYSTEMS CHECK
echo "🚨 CRITICAL SYSTEMS CHECK"
curl -s http://localhost:8000/health > /dev/null && echo "✅ Backend responding" || echo "❌ Backend down"
ps aux | grep -q "python.*main.py" && echo "✅ Backend process running" || echo "❌ Backend process missing"
echo ""

# 4. DOCUMENTATION CURRENCY CHECK
echo "📚 DOCUMENTATION CURRENCY CHECK"
ls docs/fixes/ | wc -l | xargs echo "Fix documents available:"
grep -q "$(date +%Y-%m)" CLAUDE.md && echo "✅ CLAUDE.md current" || echo "❌ CLAUDE.md outdated"
echo ""

echo "=== SESSION READY ==="
echo "Sarah: Ready for failure mode analysis"
echo "Alex: Ready for integration validation"
```

### Session Termination (MANDATORY)
Every development session MUST end with this verification sequence:

```bash
# SESSION END CHECKLIST
echo "=== SESSION TERMINATION ==="
echo "Date: $(date)"
echo ""

# 1. CODE QUALITY VERIFICATION
echo "🔍 CODE QUALITY VERIFICATION"
cd ai-assistant/backend
python -m pytest -v --tb=short || echo "❌ Backend tests failing"
cd ../
npm test -- --passWithNoTests --watchAll=false || echo "❌ Frontend tests failing"
echo ""

# 2. INTEGRATION SMOKE TEST
echo "🔗 INTEGRATION SMOKE TEST" 
cd ai-assistant/backend
python main.py &
BACKEND_PID=$!
sleep 5
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ Backend health check" || echo "❌ Backend unhealthy"
kill $BACKEND_PID
echo ""

# 3. DOCUMENTATION VERIFICATION
echo "📚 DOCUMENTATION VERIFICATION"
find docs/fixes/ -name "*.md" -newer CLAUDE.md && echo "❌ Fix docs newer than CLAUDE.md" || echo "✅ CLAUDE.md current"
grep -q "$(date +%Y-%m)" CLAUDE.md && echo "✅ CLAUDE.md updated this month" || echo "❌ CLAUDE.md stale"
echo ""

# 4. COMMIT READINESS CHECK
echo "📦 COMMIT READINESS CHECK"
git status --porcelain | wc -l | xargs echo "Modified files:"
git log --oneline -1 | grep -q "$(date +%Y-%m-%d)" && echo "✅ Recent commits today" || echo "ℹ️ No commits today"
echo ""

echo "=== SESSION COMPLETE ==="
echo "Sarah: All failure modes documented and tested"
echo "Alex: All integrations verified and cleanup confirmed"
```

---

## 📝 STANDARDIZED PROMPT PROTOCOLS

### Task Initiation Prompt Template
Use this template for every development task:

```
[ORCHESTRATED TASK REQUEST]

**Architects**: Request both Alex Novak and Dr. Sarah Chen

**Task**: [Clear, specific task description]

**Context**: 
- Current system state: [working/broken/unknown]
- Related components: [backend/frontend/both]
- Expected complexity: [simple/medium/complex]

**Requirements**:
- Sarah: Analyze failure modes and backend implications
- Alex: Evaluate frontend integration and process coordination
- Both: Cross-validate assumptions and provide verification procedures

**Success Criteria**:
- [ ] All code passes both architects' review
- [ ] Comprehensive error handling implemented
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] 3 AM debugging procedures documented

**Verification Required**: Both architects must sign off on implementation
```

### Task Completion Verification Prompt
End every task with this verification:

```
[TASK COMPLETION VERIFICATION]

**Architects**: Alex Novak and Dr. Sarah Chen - please verify:

**Implementation Review**:
- Sarah: Does this pass your "Three Questions" framework?
  - What breaks first? [Answer required]
  - How do we know? [Answer required] 
  - What's Plan B? [Answer required]

- Alex: Does this pass the "3 AM Test"?
  - Can this be debugged at 3 AM without calling anyone? [Yes/No]
  - Are all integration points documented? [Yes/No]
  - Is cleanup/resource management verified? [Yes/No]

**Quality Gates**:
- [ ] All tests passing (show output)
- [ ] Error boundaries implemented
- [ ] Monitoring/logging in place
- [ ] Documentation updated
- [ ] Rollback procedures documented

**Sign-off Required**: Both architects must explicitly approve before task considered complete
```

### Emergency Fix Prompt Template
For critical issues:

```
[EMERGENCY FIX REQUEST]

**CRITICAL ISSUE DETECTED**

**Severity**: [CRITICAL/HIGH/MEDIUM]
**System Impact**: [Description of current failure]
**User Impact**: [How this affects users]

**Immediate Actions Needed**:
- Sarah: Identify blast radius and containment
- Alex: Determine frontend/process coordination impact
- Both: Provide emergency mitigation steps

**Requirements**:
1. Immediate containment procedure
2. Root cause analysis
3. Permanent fix implementation
4. Prevention strategy
5. Documentation update

**Time Constraint**: [Immediate/Hours/Days]
**Risk Tolerance**: [Low/Medium/High]

Both architects respond with emergency procedures first, detailed fix second.
```

---

## 📁 MANDATORY PROJECT STRUCTURE REQUIREMENTS

### Directory Structure Enforcement
This structure MUST be maintained:

```
ai-assistant/
├── backend/                 # Sarah's domain
│   ├── tests/              # MANDATORY - pytest tests for all modules
│   │   ├── test_cache_manager.py
│   │   ├── test_websocket_manager.py  
│   │   ├── test_orchestrator.py
│   │   ├── test_integration_*.py
│   │   └── test_failure_modes.py     # Sarah's failure scenario tests
│   ├── docs/               # MANDATORY - backend documentation
│   │   ├── api/            # API documentation
│   │   ├── architecture/   # System design docs
│   │   └── runbooks/       # 3 AM debugging procedures
│   └── [implementation files]
│
├── src/                    # Alex's domain  
│   ├── app/
│   │   ├── components/
│   │   │   └── [each component]/
│   │   │       ├── *.component.ts
│   │   │       ├── *.component.spec.ts  # MANDATORY tests
│   │   │       ├── *.component.html
│   │   │       └── *.component.scss
│   │   ├── services/
│   │   │   ├── *.service.ts
│   │   │   └── *.service.spec.ts       # MANDATORY tests
│   │   └── testing/        # MANDATORY - test utilities
│   │       ├── mocks/
│   │       ├── fixtures/
│   │       └── test-utils.ts
│   └── e2e/               # MANDATORY - integration tests
│       ├── app.e2e-spec.ts
│       ├── terminal.e2e-spec.ts
│       └── process-coordination.e2e-spec.ts
│
├── electron/              # Alex's domain - process coordination
│   ├── tests/            # MANDATORY - Electron-specific tests
│   │   ├── main-process.spec.ts
│   │   ├── preload.spec.ts
│   │   └── pty-integration.spec.ts
│   └── [implementation files]
│
├── docs/                 # Shared documentation
│   ├── fixes/           # MANDATORY - fix documentation
│   │   ├── critical/
│   │   ├── high/
│   │   ├── medium/
│   │   └── fixes-implementation-plan.md
│   ├── architecture/    # MANDATORY - system architecture
│   │   ├── backend-architecture.md
│   │   ├── frontend-architecture.md
│   │   ├── integration-patterns.md
│   │   └── failure-modes.md
│   ├── processes/       # MANDATORY - development processes
│   │   ├── session-protocols.md
│   │   ├── testing-standards.md
│   │   └── quality-gates.md
│   └── runbooks/        # MANDATORY - operational procedures
│       ├── 3am-debugging.md
│       ├── system-recovery.md
│       └── monitoring-playbooks.md
│
├── tests/               # MANDATORY - cross-system integration tests
│   ├── integration/
│   ├── performance/
│   └── failure-scenarios/
│
└── [configuration files]
```

### File Validation Script
```bash
#!/bin/bash
# File: validate-project-structure.sh

echo "🔍 PROJECT STRUCTURE VALIDATION"

# Check mandatory directories
REQUIRED_DIRS=(
    "backend/tests"
    "backend/docs/api"
    "backend/docs/architecture" 
    "backend/docs/runbooks"
    "src/app/testing"
    "src/e2e"
    "electron/tests"
    "docs/fixes/critical"
    "docs/fixes/high"
    "docs/architecture"
    "docs/processes"
    "docs/runbooks"
    "tests/integration"
    "tests/performance"
    "tests/failure-scenarios"
)

missing_dirs=0
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Missing required directory: $dir"
        missing_dirs=$((missing_dirs + 1))
    fi
done

# Check test files exist for all implementation files
echo ""
echo "🧪 TEST FILE VALIDATION"

# Backend test validation
backend_files=$(find backend -name "*.py" -not -path "*/tests/*" -not -name "__*" | wc -l)
backend_tests=$(find backend/tests -name "test_*.py" | wc -l)
echo "Backend: $backend_files implementation files, $backend_tests test files"

# Frontend test validation  
component_files=$(find src/app/components -name "*.component.ts" | wc -l)
component_tests=$(find src/app/components -name "*.component.spec.ts" | wc -l)
echo "Components: $component_files components, $component_tests tests"

service_files=$(find src/app/services -name "*.service.ts" | wc -l)
service_tests=$(find src/app/services -name "*.service.spec.ts" | wc -l)
echo "Services: $service_files services, $service_tests tests"

# Documentation validation
echo ""
echo "📚 DOCUMENTATION VALIDATION"
[ -f "CLAUDE.md" ] && echo "✅ CLAUDE.md exists" || echo "❌ CLAUDE.md missing"
[ -f "docs/fixes/fixes-implementation-plan.md" ] && echo "✅ Fix plan exists" || echo "❌ Fix plan missing"

if [ $missing_dirs -eq 0 ]; then
    echo ""
    echo "✅ PROJECT STRUCTURE VALID"
    exit 0
else
    echo ""
    echo "❌ PROJECT STRUCTURE INVALID - $missing_dirs missing directories"
    exit 1
fi
```

---

## 🧪 COMPREHENSIVE TESTING REQUIREMENTS

### Testing Standards by Layer

#### Backend Testing (Sarah's Domain)
```bash
# MANDATORY BACKEND TESTING COMMANDS
cd ai-assistant/backend

# 1. Unit Tests - All modules must have tests
python -m pytest tests/ -v --tb=short
python -m pytest tests/ --cov=. --cov-report=term-missing --cov-fail-under=85

# 2. Integration Tests - Cross-component validation  
python -m pytest tests/integration/ -v

# 3. Failure Mode Tests - Sarah's specialty
python -m pytest tests/test_failure_modes.py -v

# 4. Performance Tests - Resource limits and timing
python -m pytest tests/performance/ -v --timeout=30

# 5. API Contract Tests - Endpoint validation
python -m pytest tests/api/ -v
```

#### Frontend Testing (Alex's Domain)
```bash
# MANDATORY FRONTEND TESTING COMMANDS
cd ai-assistant

# 1. Unit Tests - All components and services
ng test --watch=false --browsers=ChromeHeadless --code-coverage

# 2. Memory Leak Tests - Alex's specialty
ng test --watch=false --browsers=ChromeHeadless src/app/testing/memory-leak.spec.ts

# 3. IPC Integration Tests - Electron communication
ng test --watch=false --browsers=ChromeHeadless src/app/testing/ipc-integration.spec.ts

# 4. E2E Tests - Full user workflow
ng e2e --suite=critical-path
ng e2e --suite=error-scenarios

# 5. Performance Tests - Bundle size and runtime
npm run analyze
ng test --watch=false --browsers=ChromeHeadless src/app/testing/performance.spec.ts
```

#### Cross-System Testing (Both Architects)
```bash
# MANDATORY INTEGRATION TESTING
cd ai-assistant

# 1. Process Coordination Tests
npm run test:electron-backend-coordination

# 2. WebSocket Integration Tests  
npm run test:websocket-integration

# 3. Cache Integration Tests
npm run test:cache-integration

# 4. Failure Cascade Tests
npm run test:failure-cascades

# 5. Recovery Scenario Tests
npm run test:recovery-scenarios
```

### Test Configuration Requirements

#### Backend pytest.ini
```ini
# File: backend/pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v 
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=.
    --cov-report=term-missing
    --cov-fail-under=85
    --timeout=30
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    failure_modes: Failure scenario tests
    slow: Slow-running tests
```

#### Frontend karma.conf.js additions
```javascript
// Required additions to karma.conf.js
module.exports = function (config) {
  config.set({
    // ... existing config
    
    // Code coverage requirements
    coverageIstanbulReporter: {
      reports: ['html', 'lcovonly', 'text-summary'],
      fixWebpackSourcePaths: true,
      thresholds: {
        statements: 80,
        lines: 80,
        branches: 70,
        functions: 80
      }
    },
    
    // Memory leak detection
    browserNoActivityTimeout: 60000,
    captureTimeout: 60000,
    
    // Custom test suites
    customLaunchers: {
      ChromeHeadlessMemory: {
        base: 'ChromeHeadless',
        flags: [
          '--no-sandbox',
          '--disable-web-security',
          '--disable-gpu',
          '--max-old-space-size=4096'
        ]
      }
    }
  });
};
```

---

## 📋 END-OF-TASK VALIDATION CHECKLIST

### Automated Validation Script
```bash
#!/bin/bash
# File: validate-task-completion.sh

echo "🔍 TASK COMPLETION VALIDATION"
echo "Architects: Alex Novak & Dr. Sarah Chen"
echo "Date: $(date)"
echo ""

# Initialize counters
tests_passed=0
tests_failed=0
validations_passed=0
validations_failed=0

# Function to check and report
check_requirement() {
    local description="$1"
    local command="$2"
    local requirement_type="$3"
    
    echo -n "Checking: $description... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo "✅ PASS"
        if [ "$requirement_type" = "test" ]; then
            tests_passed=$((tests_passed + 1))
        else
            validations_passed=$((validations_passed + 1))
        fi
        return 0
    else
        echo "❌ FAIL"
        if [ "$requirement_type" = "test" ]; then
            tests_failed=$((tests_failed + 1))
        else
            validations_failed=$((validations_failed + 1))
        fi
        return 1
    fi
}

echo "🧪 TESTING REQUIREMENTS"

# Backend Tests (Sarah's Domain)
cd ai-assistant/backend
check_requirement "Backend unit tests" "python -m pytest tests/ -x -q" "test"
check_requirement "Backend coverage >85%" "python -m pytest tests/ --cov=. --cov-fail-under=85 -q" "test"
check_requirement "Backend integration tests" "python -m pytest tests/integration/ -x -q" "test"
check_requirement "Backend failure mode tests" "python -m pytest tests/test_failure_modes.py -x -q" "test"

# Frontend Tests (Alex's Domain)
cd ../
check_requirement "Frontend unit tests" "ng test --watch=false --browsers=ChromeHeadless --progress=false" "test"
check_requirement "Frontend coverage >80%" "ng test --watch=false --browsers=ChromeHeadless --code-coverage --progress=false" "test"
check_requirement "E2E critical path tests" "ng e2e --suite=critical-path" "test"

# Cross-System Tests (Both Architects)
check_requirement "Process coordination tests" "npm run test:electron-backend-coordination" "test"
check_requirement "WebSocket integration tests" "npm run test:websocket-integration" "test"

echo ""
echo "🔍 VALIDATION REQUIREMENTS"

# Code Quality Validations
check_requirement "No TODO/FIXME in production code" "! grep -r 'TODO\|FIXME' --include='*.py' --include='*.ts' backend/ src/ electron/ --exclude-dir=tests" "validation"
check_requirement "No magic numbers/hardcoded values" "! grep -r '127\.0\.0\.1\|localhost\|8000\|8001' --include='*.py' --include='*.ts' backend/ src/ electron/ | grep -v test | grep -v spec" "validation"
check_requirement "All imports working" "cd backend && python -c 'import main; print(\"OK\")'" "validation"
check_requirement "Frontend builds without errors" "ng build --configuration=production" "validation"

# Documentation Validations
check_requirement "CLAUDE.md updated this month" "grep -q '$(date +%Y-%m)' CLAUDE.md" "validation"
check_requirement "Fix documentation exists" "[ -d docs/fixes ] && [ $(ls docs/fixes/*.md 2>/dev/null | wc -l) -gt 0 ]" "validation"
check_requirement "Architecture docs exist" "[ -f docs/architecture/backend-architecture.md ] && [ -f docs/architecture/frontend-architecture.md ]" "validation"

# Integration Validations
check_requirement "Backend starts successfully" "cd backend && timeout 10s python main.py & sleep 5 && curl -s http://localhost:8000/health | grep -q healthy" "validation"
check_requirement "Process coordination working" "ps aux | grep -q 'python.*main.py' || echo 'Backend process check skipped'" "validation"

echo ""
echo "📊 VALIDATION SUMMARY"
echo "Tests: $tests_passed passed, $tests_failed failed"
echo "Validations: $validations_passed passed, $validations_failed failed"

# Final determination
total_failed=$((tests_failed + validations_failed))
if [ $total_failed -eq 0 ]; then
    echo ""
    echo "✅ TASK COMPLETION VALIDATED"
    echo "Sarah: All failure modes tested and documented"
    echo "Alex: All integrations verified and cleanup confirmed"
    echo ""
    echo "🎯 READY FOR COMMIT/DEPLOYMENT"
    exit 0
else
    echo ""
    echo "❌ TASK COMPLETION FAILED VALIDATION"
    echo "Total failures: $total_failed"
    echo ""
    echo "🚫 NOT READY FOR COMMIT - FIX FAILURES FIRST"
    exit 1
fi
```

### Git Pre-Commit Hook
```bash
#!/bin/bash
# File: .git/hooks/pre-commit

echo "🔒 PRE-COMMIT VALIDATION"
echo "Orchestrated Quality Gate - Alex Novak & Dr. Sarah Chen"

# Run the task completion validation
if ./validate-task-completion.sh; then
    echo ""
    echo "✅ PRE-COMMIT VALIDATION PASSED"
    echo "Proceeding with commit..."
    exit 0
else
    echo ""
    echo "❌ PRE-COMMIT VALIDATION FAILED"
    echo ""
    echo "Sarah's Analysis: Fix failure modes before committing"
    echo "Alex's Analysis: Resolve integration issues before committing"
    echo ""
    echo "Run './validate-task-completion.sh' to see detailed failures"
    exit 1
fi
```

---

## 📖 README.md DOCUMENTATION SECTIONS

### Required README.md Structure
```markdown
# AI Development Assistant

## Quality Assurance & Development Standards

This project follows orchestrated development practices with comprehensive quality gates.

### Architects
- **Alex Novak**: Electron/Angular architecture, process coordination, frontend defensive programming
- **Dr. Sarah Chen**: Backend systems, caching strategies, failure mode analysis, WebSocket architecture

### Development Protocol
Every development session must follow the [Orchestrated Development Governance Framework](docs/processes/governance-framework.md).

#### Session Requirements
- **Start**: Run `./validate-session-start.sh` before any development
- **End**: Run `./validate-task-completion.sh` before commit
- **Testing**: All tests must pass with minimum coverage requirements
- **Documentation**: All changes must update relevant documentation

#### Quality Gates
```bash
# Required before any commit
./validate-project-structure.sh
./validate-task-completion.sh
```

### Testing Standards

#### Backend Testing (Sarah's Domain)
```bash
cd ai-assistant/backend
python -m pytest tests/ -v --cov=. --cov-fail-under=85
python -m pytest tests/integration/ -v
python -m pytest tests/test_failure_modes.py -v
```

#### Frontend Testing (Alex's Domain)  
```bash
cd ai-assistant
ng test --watch=false --browsers=ChromeHeadless --code-coverage
ng e2e --suite=critical-path
npm run test:memory-leaks
```

#### Cross-System Testing (Both Architects)
```bash
npm run test:electron-backend-coordination
npm run test:websocket-integration
npm run test:failure-cascades
```

### Documentation Requirements

#### Mandatory Documentation
- `CLAUDE.md` - System overview and current status (updated monthly)
- `docs/fixes/` - All issues and their solutions
- `docs/architecture/` - System architecture documentation  
- `docs/runbooks/` - 3 AM debugging procedures
- `README.md` - This file (updated with each major change)

#### Documentation Standards
- All fixes must include failure mode analysis
- All integrations must include 3 AM debugging procedures
- All architectural decisions must be documented with rationale

### Project Structure Enforcement

The project structure is validated automatically. Run `./validate-project-structure.sh` to verify compliance.

Required structure includes:
- Test files for all implementation files
- Documentation for all architectural decisions
- Runbooks for all operational procedures
- Fix documentation for all identified issues

### Failure Mode Analysis

Every component must address:
- **What breaks first?** (Weakest link identification)
- **How do we know?** (Monitoring and observability)
- **What's Plan B?** (Fallback and recovery procedures)

### Integration Validation

Cross-system integration points are validated through:
- Process coordination testing
- WebSocket integration testing
- Cache integration testing  
- Failure cascade scenario testing

### Commit Requirements

Before any commit:
1. All tests must pass with required coverage
2. All documentation must be current
3. All integration points must be validated
4. All failure modes must be tested
5. Pre-commit hook validation must pass

### Emergency Procedures

For critical issues:
1. Follow emergency fix prompt template
2. Implement containment before permanent fix
3. Document root cause and prevention
4. Update monitoring and alerting
5. Conduct post-incident review

---

This README enforces the governance framework through clear requirements and automated validation.
```

---

**Implementation Status**: COMPREHENSIVE GOVERNANCE FRAMEWORK COMPLETE  
**Enforcement Level**: AUTOMATED with manual validation checkpoints  
**Compliance**: MANDATORY for all development activities  

**Sarah's Process Analysis**: ✅ PASS - Systematic failure prevention with validation  
**Alex's Integration Verification**: ✅ PASS - Complete process coordination with automation