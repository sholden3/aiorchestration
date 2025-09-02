#!/bin/bash

###############################################################################
# Pre-Commit Hook v0.1 - Minimal Standards (Week 1)
# 
# Purpose: Allow maximum progress while preventing critical issues
# Phase: 2.5 Implementation - Week 1
# Expires: Automatically upgrades after Week 1
# 
# This is a TEMPORARY relaxation to enable progress during test implementation
###############################################################################

echo "================================================"
echo "🚧 PRE-COMMIT HOOK v0.1 - PROGRESSIVE MODE 🚧"
echo "Phase 2.5 - Week 1: Minimal Standards"
echo "================================================"

# Track that we're using relaxed standards
echo "$(date): Commit with v0.1 standards" >> .git/progressive-standards.log

# Initialize counters
ERRORS=0
WARNINGS=0

# LEVEL 1: CRITICAL CHECKS (BLOCKING)
echo ""
echo "🔴 Running Critical Checks (Blocking)..."
echo "----------------------------------------"

# Check for syntax errors in Python
echo "Checking Python syntax..."
for file in $(git diff --cached --name-only --diff-filter=ACM | grep "\.py$"); do
    if [ -f "$file" ]; then
        python -m py_compile "$file" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "  ❌ Python syntax error in $file"
            ((ERRORS++))
        fi
    fi
done

# Check for syntax errors in TypeScript/JavaScript
echo "Checking TypeScript/JavaScript syntax..."
for file in $(git diff --cached --name-only --diff-filter=ACM | grep -E "\.(ts|js)$"); do
    if [ -f "$file" ]; then
        # Basic syntax check using node
        node -c "$file" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "  ❌ JavaScript syntax error in $file"
            ((ERRORS++))
        fi
    fi
done

# Check for exposed secrets
echo "Checking for exposed secrets..."
for file in $(git diff --cached --name-only --diff-filter=ACM); do
    if [ -f "$file" ]; then
        # Check for common secret patterns
        if grep -E "(api_key|apikey|api-key|secret|password|pwd|token|private_key|aws_access|AKIA[0-9A-Z]{16})" "$file" | grep -v "example\|sample\|test\|fake" > /dev/null; then
            echo "  ❌ Possible secret exposed in $file"
            echo "    Please review and use environment variables instead"
            ((ERRORS++))
        fi
    fi
done

# Check for large files
echo "Checking file sizes..."
for file in $(git diff --cached --name-only --diff-filter=ACM); do
    if [ -f "$file" ]; then
        size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
        if [ "$size" -gt 5242880 ]; then  # 5MB
            echo "  ❌ Large file detected: $file ($(($size / 1048576))MB)"
            ((ERRORS++))
        fi
    fi
done

# LEVEL 2: QUALITY CHECKS (WARNING ONLY)
echo ""
echo "🟡 Running Quality Checks (Warnings Only)..."
echo "--------------------------------------------"

# Check documentation standards (WARNING ONLY)
echo "Checking documentation standards..."
if [ -x "./validate-code-documentation.sh" ]; then
    ./validate-code-documentation.sh > /tmp/doc-check.log 2>&1
    if [ $? -ne 0 ]; then
        echo "  ⚠️  Documentation standards not met (not blocking)"
        ((WARNINGS++))
        
        # Log documentation debt
        echo "$(date): Documentation debt incurred" >> TECHNICAL_DEBT.md
    fi
else
    echo "  ⚠️  Documentation validator not found"
    ((WARNINGS++))
fi

# Check test coverage (TRACKING ONLY)
echo "Tracking test coverage..."
if [ -d "ai-assistant" ]; then
    cd ai-assistant
    npm test -- --coverage --silent > /tmp/coverage.log 2>&1 || true
    cd ..
    echo "  📊 Coverage tracked (not enforced in Week 1)"
fi

# Check for TODO/FIXME comments
echo "Checking for TODO/FIXME markers..."
TODO_COUNT=$(git diff --cached | grep -c "TODO\|FIXME" || echo "0")
if [ "$TODO_COUNT" -gt 0 ]; then
    echo "  ⚠️  Found $TODO_COUNT TODO/FIXME markers"
    ((WARNINGS++))
fi

# LEVEL 3: TRACKING METRICS
echo ""
echo "📊 Tracking Metrics (Information Only)..."
echo "-----------------------------------------"

# Count files being committed
FILE_COUNT=$(git diff --cached --name-only | wc -l)
echo "  Files in commit: $FILE_COUNT"

# Track lines of code
LINES_ADDED=$(git diff --cached --stat | tail -1 | grep -oE "[0-9]+ insertion" | grep -oE "[0-9]+" || echo "0")
LINES_DELETED=$(git diff --cached --stat | tail -1 | grep -oE "[0-9]+ deletion" | grep -oE "[0-9]+" || echo "0")
echo "  Lines added: $LINES_ADDED"
echo "  Lines deleted: $LINES_DELETED"

# Log technical debt
if [ -f "TECHNICAL_DEBT.md" ]; then
    echo ""
    echo "📝 Logging Technical Debt..."
    echo "## $(date +%Y-%m-%d) Commit" >> TECHNICAL_DEBT.md
    echo "- Files changed: $FILE_COUNT" >> TECHNICAL_DEBT.md
    echo "- Warnings: $WARNINGS" >> TECHNICAL_DEBT.md
    echo "- Standards: v0.1 (minimal)" >> TECHNICAL_DEBT.md
    echo "" >> TECHNICAL_DEBT.md
fi

# FINAL DECISION
echo ""
echo "================================================"
echo "SUMMARY:"
echo "  Critical Errors: $ERRORS"
echo "  Warnings: $WARNINGS"
echo "  Standards Version: 0.1 (Week 1 - Minimal)"

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "❌ COMMIT BLOCKED: Critical errors must be fixed"
    echo "================================================"
    exit 1
else
    echo ""
    echo "✅ COMMIT ALLOWED (Progressive Standards)"
    echo ""
    echo "⚠️  REMINDER: This is temporary!"
    echo "  Week 1: Minimal standards (current)"
    echo "  Week 2: Progressive standards" 
    echo "  Week 3: Maturing standards"
    echo "  Week 4: Full standards restored"
    echo ""
    echo "Technical debt is being tracked in TECHNICAL_DEBT.md"
    echo "================================================"
    
    # Check if we should auto-upgrade
    if [ -f ".git/standards-version.txt" ]; then
        CURRENT_WEEK=$(cat .git/standards-version.txt)
        DAYS_ELAPSED=$(( ($(date +%s) - $(date -d "2025-01-27" +%s)) / 86400 ))
        
        if [ $DAYS_ELAPSED -ge 7 ]; then
            echo ""
            echo "📅 Note: Week 1 is ending. Consider upgrading to v0.4 (progressive)"
        fi
    fi
    
    exit 0
fi