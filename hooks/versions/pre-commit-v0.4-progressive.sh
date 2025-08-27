#!/bin/bash

###############################################################################
# Pre-Commit Hook v0.4 - Progressive Standards (Week 2)
# 
# Purpose: Increase quality requirements while allowing continued progress
# Phase: 2.5 Implementation - Week 2
# Expires: Automatically upgrades to v0.8 after Week 2
# 
# Changes from v0.1:
# - Documentation now required (blocking)
# - Coverage tracked and warned if below 40%
# - More comprehensive linting
###############################################################################

echo "================================================"
echo "🚧 PRE-COMMIT HOOK v0.4 - PROGRESSIVE MODE 🚧"
echo "Phase 2.5 - Week 2: Progressive Standards"
echo "================================================"

# Track standards version
echo "$(date): Commit with v0.4 standards" >> .git/progressive-standards.log

# Initialize counters
ERRORS=0
WARNINGS=0

# LEVEL 1: CRITICAL CHECKS (BLOCKING)
echo ""
echo "🔴 Running Critical Checks (Blocking)..."
echo "----------------------------------------"

# All checks from v0.1
source hooks/versions/pre-commit-v0.1-minimal.sh --critical-only 2>/dev/null || {
    # Inline critical checks if sourcing fails
    
    # Python syntax
    for file in $(git diff --cached --name-only --diff-filter=ACM | grep "\.py$"); do
        if [ -f "$file" ]; then
            python -m py_compile "$file" 2>/dev/null
            if [ $? -ne 0 ]; then
                echo "  ❌ Python syntax error in $file"
                ((ERRORS++))
            fi
        fi
    done
    
    # Check for secrets
    for file in $(git diff --cached --name-only --diff-filter=ACM); do
        if [ -f "$file" ] && grep -E "(api_key|secret|password|token|private_key)" "$file" | grep -v "example\|test" > /dev/null; then
            echo "  ❌ Possible secret in $file"
            ((ERRORS++))
        fi
    done
}

# NEW IN v0.4: Documentation is now REQUIRED
echo "Checking documentation standards (REQUIRED)..."
MISSING_DOCS=0
for file in $(git diff --cached --name-only --diff-filter=ACM | grep -E "\.(py|ts|js)$"); do
    if [ -f "$file" ]; then
        # Check for file header documentation
        if ! head -20 "$file" | grep -E "@(author|specialist|fileoverview|description)" > /dev/null; then
            echo "  ❌ Missing documentation header in $file"
            ((ERRORS++))
            ((MISSING_DOCS++))
        fi
    fi
done

if [ $MISSING_DOCS -gt 0 ]; then
    echo "    Please add documentation headers. Template:"
    echo "    /**"
    echo "     * @fileoverview [Description]"
    echo "     * @author [Name] - $(date +%Y-%m-%d)"
    echo "     * @hooks [Integration points]"
    echo "     */"
fi

# LEVEL 2: QUALITY CHECKS (WARNINGS BUT TRACKING)
echo ""
echo "🟡 Running Quality Checks (Warnings)..."
echo "----------------------------------------"

# Test Coverage Check (WARNING at <40%)
echo "Checking test coverage..."
COVERAGE=0
if [ -d "ai-assistant" ]; then
    cd ai-assistant
    # Try to get coverage percentage
    npm test -- --coverage --silent > /tmp/coverage.log 2>&1 || true
    COVERAGE=$(grep "All files" /tmp/coverage.log | grep -oE "[0-9]+\.[0-9]+" | head -1 || echo "0")
    cd ..
    
    if (( $(echo "$COVERAGE < 40" | bc -l) )); then
        echo "  ⚠️  Coverage is ${COVERAGE}% (target: 40% for Week 2)"
        ((WARNINGS++))
        
        # Log coverage debt
        echo "$(date): Coverage at ${COVERAGE}%, need 40%" >> TECHNICAL_DEBT.md
    else
        echo "  ✅ Coverage is ${COVERAGE}% (meets Week 2 target)"
    fi
fi

# Linting Checks (WARNING)
echo "Running linters..."

# Python linting with pylint (if available)
if command -v pylint &> /dev/null; then
    for file in $(git diff --cached --name-only --diff-filter=ACM | grep "\.py$"); do
        if [ -f "$file" ]; then
            pylint --errors-only "$file" > /tmp/pylint.log 2>&1
            if [ $? -ne 0 ]; then
                echo "  ⚠️  Linting issues in $file"
                ((WARNINGS++))
            fi
        fi
    done
fi

# TypeScript/JavaScript linting
if [ -f "ai-assistant/node_modules/.bin/eslint" ]; then
    for file in $(git diff --cached --name-only --diff-filter=ACM | grep -E "\.(ts|js)$"); do
        if [ -f "$file" ]; then
            ai-assistant/node_modules/.bin/eslint "$file" > /tmp/eslint.log 2>&1
            if [ $? -ne 0 ]; then
                echo "  ⚠️  ESLint issues in $file"
                ((WARNINGS++))
            fi
        fi
    done
fi

# Check for console.log statements (WARNING)
CONSOLE_COUNT=$(git diff --cached | grep -c "console\.log" || echo "0")
if [ "$CONSOLE_COUNT" -gt 0 ]; then
    echo "  ⚠️  Found $CONSOLE_COUNT console.log statements (consider using proper logging)"
    ((WARNINGS++))
fi

# LEVEL 3: ENHANCED TRACKING
echo ""
echo "📊 Enhanced Metrics Tracking..."
echo "--------------------------------"

# Track test file ratio
TEST_FILES=$(git diff --cached --name-only | grep -c "test\|spec" || echo "0")
CODE_FILES=$(git diff --cached --name-only | grep -E "\.(py|ts|js)$" | grep -vc "test\|spec" || echo "0")
echo "  Test files: $TEST_FILES"
echo "  Code files: $CODE_FILES"

if [ $CODE_FILES -gt 0 ] && [ $TEST_FILES -eq 0 ]; then
    echo "  ⚠️  No test files in this commit"
    ((WARNINGS++))
fi

# Track assumption discoveries
if [ -f "docs/testing/assumption-discovery-log.md" ]; then
    ASSUMPTIONS=$(grep -c "^### 2025" docs/testing/assumption-discovery-log.md || echo "0")
    echo "  Assumptions discovered: $ASSUMPTIONS"
fi

# Update Technical Debt with more detail
if [ -f "TECHNICAL_DEBT.md" ]; then
    echo "" >> TECHNICAL_DEBT.md
    echo "## $(date '+%Y-%m-%d %H:%M') - v0.4 Commit" >> TECHNICAL_DEBT.md
    echo "- Coverage: ${COVERAGE}% (target: 40%)" >> TECHNICAL_DEBT.md
    echo "- Test/Code ratio: $TEST_FILES/$CODE_FILES" >> TECHNICAL_DEBT.md
    echo "- Warnings: $WARNINGS" >> TECHNICAL_DEBT.md
    echo "- Documentation: $((MISSING_DOCS == 0 ? 'Complete' : 'Incomplete'))" >> TECHNICAL_DEBT.md
fi

# FINAL DECISION
echo ""
echo "================================================"
echo "SUMMARY:"
echo "  Critical Errors: $ERRORS"
echo "  Warnings: $WARNINGS"
echo "  Coverage: ${COVERAGE}%"
echo "  Standards Version: 0.4 (Week 2 - Progressive)"

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "❌ COMMIT BLOCKED: Critical errors must be fixed"
    echo "  - Fix syntax errors"
    echo "  - Add documentation headers"
    echo "  - Remove exposed secrets"
    echo "================================================"
    exit 1
else
    echo ""
    echo "✅ COMMIT ALLOWED (Progressive Standards)"
    
    if [ $WARNINGS -gt 5 ]; then
        echo ""
        echo "⚠️  HIGH WARNING COUNT: Consider addressing some warnings"
    fi
    
    echo ""
    echo "📅 Standards Schedule:"
    echo "  Week 1: Minimal standards ✓"
    echo "  Week 2: Progressive standards (current) ← You are here"
    echo "  Week 3: Maturing standards (coming soon)"
    echo "  Week 4: Full standards"
    echo ""
    echo "Next upgrade: Coverage requirement increases to 40% (blocking)"
    echo "================================================"
    
    exit 0
fi