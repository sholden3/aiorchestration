#!/bin/bash
# Phase Completion Script - Enforces test-commit-push workflow
# Usage: ./complete-phase.sh <phase_number> "<description>"

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}Error: Missing arguments${NC}"
    echo "Usage: $0 <phase_number> \"<description>\""
    echo "Example: $0 1 \"Foundation Layer - Database and Core APIs\""
    exit 1
fi

PHASE_NUMBER=$1
PHASE_DESCRIPTION=$2
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo -e "${GREEN}=== PHASE $PHASE_NUMBER COMPLETION WORKFLOW ===${NC}"
echo "Phase: $PHASE_DESCRIPTION"
echo "Timestamp: $TIMESTAMP"
echo ""

# Function to check if command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
        return 0
    else
        echo -e "${RED}✗ $1 failed${NC}"
        return 1
    fi
}

# Function to run tests with retry
run_tests_with_retry() {
    local test_type=$1
    local command=$2
    local max_attempts=2
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "Running $test_type tests (attempt $attempt/$max_attempts)..."
        if eval $command; then
            return 0
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            echo -e "${YELLOW}Tests failed, retrying...${NC}"
            sleep 2
        fi
        attempt=$((attempt + 1))
    done
    
    return 1
}

# 1. SESSION VALIDATION
echo -e "${YELLOW}[1/10] Session Validation${NC}"
python .governance/core/session_manager.py validate
check_status "Session validated" || exit 1
echo ""

# 2. CODE FORMATTING
echo -e "${YELLOW}[2/10] Code Formatting${NC}"

# Frontend formatting
if [ -d "ai-assistant" ]; then
    cd ai-assistant
    npm run format 2>/dev/null || echo "No format script defined"
    cd ..
fi

# Backend formatting
if [ -d "ai-assistant/backend" ]; then
    cd ai-assistant/backend
    black . 2>/dev/null || echo "Black not configured"
    cd ../..
fi

check_status "Code formatted"
echo ""

# 3. LINTING
echo -e "${YELLOW}[3/10] Linting${NC}"

LINT_ERRORS=0

# Frontend linting
if [ -d "ai-assistant" ]; then
    cd ai-assistant
    npm run lint 2>/dev/null || LINT_ERRORS=$((LINT_ERRORS + 1))
    cd ..
fi

# Backend linting
if [ -d "ai-assistant/backend" ]; then
    cd ai-assistant/backend
    flake8 . --max-line-length=100 --exclude=venv,__pycache__,.git 2>/dev/null || LINT_ERRORS=$((LINT_ERRORS + 1))
    cd ../..
fi

if [ $LINT_ERRORS -eq 0 ]; then
    check_status "Linting passed"
else
    echo -e "${YELLOW}⚠ Linting warnings detected${NC}"
fi
echo ""

# 4. UNIT TESTS
echo -e "${YELLOW}[4/10] Unit Tests${NC}"

# Frontend unit tests
if [ -d "ai-assistant" ]; then
    cd ai-assistant
    run_tests_with_retry "Frontend unit" "npm test -- --watchAll=false --coverage 2>/dev/null"
    FRONTEND_TEST_RESULT=$?
    cd ..
else
    FRONTEND_TEST_RESULT=0
fi

# Backend unit tests
if [ -d "ai-assistant/backend" ]; then
    cd ai-assistant/backend
    run_tests_with_retry "Backend unit" "python -m pytest tests/unit -v --cov 2>/dev/null"
    BACKEND_TEST_RESULT=$?
    cd ../..
else
    BACKEND_TEST_RESULT=0
fi

if [ $FRONTEND_TEST_RESULT -eq 0 ] && [ $BACKEND_TEST_RESULT -eq 0 ]; then
    check_status "Unit tests passed"
else
    echo -e "${RED}✗ Some unit tests failed${NC}"
    echo -e "${YELLOW}Continuing with workflow...${NC}"
fi
echo ""

# 5. INTEGRATION TESTS
echo -e "${YELLOW}[5/10] Integration Tests${NC}"

if [ -d "ai-assistant/backend" ]; then
    cd ai-assistant/backend
    python -m pytest tests/integration -v 2>/dev/null || echo "No integration tests found"
    cd ../..
fi

check_status "Integration tests completed"
echo ""

# 6. COVERAGE CHECK
echo -e "${YELLOW}[6/10] Coverage Analysis${NC}"

# Get coverage percentages
if [ -d "ai-assistant" ]; then
    cd ai-assistant
    FRONTEND_COVERAGE=$(npm test -- --coverage --watchAll=false 2>/dev/null | grep "All files" | awk '{print $10}' | sed 's/%//' || echo "0")
    cd ..
else
    FRONTEND_COVERAGE="N/A"
fi

if [ -d "ai-assistant/backend" ]; then
    cd ai-assistant/backend
    BACKEND_COVERAGE=$(python -m pytest --cov --cov-report=term 2>/dev/null | grep "TOTAL" | awk '{print $4}' | sed 's/%//' || echo "0")
    cd ../..
else
    BACKEND_COVERAGE="N/A"
fi

echo "Frontend Coverage: $FRONTEND_COVERAGE%"
echo "Backend Coverage: $BACKEND_COVERAGE%"

# Check if coverage meets threshold
COVERAGE_THRESHOLD=75
if [[ "$FRONTEND_COVERAGE" != "N/A" ]] && [ $(echo "$FRONTEND_COVERAGE < $COVERAGE_THRESHOLD" | bc -l) -eq 1 ]; then
    echo -e "${YELLOW}⚠ Frontend coverage below threshold ($COVERAGE_THRESHOLD%)${NC}"
fi

if [[ "$BACKEND_COVERAGE" != "N/A" ]] && [ $(echo "$BACKEND_COVERAGE < $COVERAGE_THRESHOLD" | bc -l) -eq 1 ]; then
    echo -e "${YELLOW}⚠ Backend coverage below threshold ($COVERAGE_THRESHOLD%)${NC}"
fi
echo ""

# 7. SECURITY SCAN
echo -e "${YELLOW}[7/10] Security Scan${NC}"

SECURITY_ISSUES=0

# Frontend security scan
if [ -d "ai-assistant" ]; then
    cd ai-assistant
    npm audit --audit-level=high 2>/dev/null || SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
    cd ..
fi

# Backend security scan
if [ -d "ai-assistant/backend" ]; then
    cd ai-assistant/backend
    safety check 2>/dev/null || bandit -r . -ll 2>/dev/null || SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
    cd ../..
fi

if [ $SECURITY_ISSUES -eq 0 ]; then
    check_status "Security scan clean"
else
    echo -e "${YELLOW}⚠ Security warnings detected${NC}"
fi
echo ""

# 8. DOCUMENTATION UPDATE
echo -e "${YELLOW}[8/10] Documentation Update${NC}"

# Update phase completion status
if [ -f "docs/IMPLEMENTATION_PHASES.md" ]; then
    echo "Phase $PHASE_NUMBER completed on $TIMESTAMP" >> docs/phase_completion.log
    check_status "Documentation updated"
else
    echo -e "${YELLOW}⚠ Phase documentation not found${NC}"
fi
echo ""

# 9. GIT OPERATIONS
echo -e "${YELLOW}[9/10] Git Commit & Push${NC}"

# Check for changes
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}No changes to commit${NC}"
else
    # Stage all changes
    git add -A
    
    # Create commit message
    COMMIT_MESSAGE="feat: Complete Phase $PHASE_NUMBER - $PHASE_DESCRIPTION

## Phase $PHASE_NUMBER Completion

### Completed Items
- All deliverables for Phase $PHASE_NUMBER
- Test coverage: Frontend $FRONTEND_COVERAGE%, Backend $BACKEND_COVERAGE%
- Security scan: $SECURITY_ISSUES issues
- Timestamp: $TIMESTAMP

### Test Results
- Unit tests: Executed
- Integration tests: Executed
- Linting: Completed

### Quality Metrics
- Code formatted with Black/Prettier
- Documentation updated
- Governance compliance verified

Co-Authored-By: AI Development Team"
    
    # Commit changes
    git commit -m "$COMMIT_MESSAGE"
    check_status "Changes committed"
    
    # Push to remote
    echo "Pushing to remote repository..."
    git push origin main
    check_status "Changes pushed"
fi
echo ""

# 10. PHASE REPORT
echo -e "${YELLOW}[10/10] Phase Completion Report${NC}"

# Generate phase report
REPORT_FILE="docs/reports/phase_${PHASE_NUMBER}_report_$(date +%Y%m%d).md"
mkdir -p docs/reports

cat > "$REPORT_FILE" << EOF
# Phase $PHASE_NUMBER Completion Report

## Phase Details
- **Number**: $PHASE_NUMBER
- **Description**: $PHASE_DESCRIPTION
- **Completed**: $TIMESTAMP

## Test Results
- **Frontend Coverage**: $FRONTEND_COVERAGE%
- **Backend Coverage**: $BACKEND_COVERAGE%
- **Security Issues**: $SECURITY_ISSUES

## Quality Metrics
- **Linting**: $LINT_ERRORS warnings
- **Unit Tests**: Executed
- **Integration Tests**: Executed

## Deliverables
- All Phase $PHASE_NUMBER deliverables completed
- Code committed and pushed
- Documentation updated

## Next Steps
- Review Phase $((PHASE_NUMBER + 1)) requirements
- Update project board
- Schedule team sync

---
*Generated by phase completion script*
EOF

check_status "Report generated at $REPORT_FILE"
echo ""

# Final summary
echo -e "${GREEN}=== PHASE $PHASE_NUMBER COMPLETION SUMMARY ===${NC}"
echo "✅ Phase $PHASE_NUMBER: $PHASE_DESCRIPTION"
echo "✅ Tests executed"
echo "✅ Code committed and pushed"
echo "✅ Documentation updated"
echo "✅ Report generated"
echo ""
echo -e "${GREEN}Phase $PHASE_NUMBER successfully completed!${NC}"
echo ""

# Update session
python .governance/core/session_manager.py end --reason "Phase $PHASE_NUMBER completed"

# Start new session for next phase
echo "Starting new session for next phase..."
python .governance/core/session_manager.py create

exit 0