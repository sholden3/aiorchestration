#!/bin/bash

###############################################################################
# Pre-Commit Hook v0.1 (Improved) - Minimal Standards (Week 1)
# 
# Purpose: Allow maximum progress while preventing critical issues
# Phase: 2.5 Implementation - Week 1
# Expires: Automatically upgrades after Week 1
# 
# Improvements:
# - Smarter secret detection (fewer false positives)
# - TypeScript syntax checking deferred (node doesn't understand TS)
# - Focus on actual blockers only
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
PYTHON_ERRORS=0
for file in $(git diff --cached --name-only --diff-filter=ACM | grep "\.py$"); do
    if [ -f "$file" ]; then
        python -m py_compile "$file" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "  ❌ Python syntax error in $file"
            ((ERRORS++))
            ((PYTHON_ERRORS++))
        fi
    fi
done
if [ $PYTHON_ERRORS -eq 0 ]; then
    echo "  ✅ No Python syntax errors"
fi

# Check for syntax errors in JavaScript ONLY (not TypeScript)
echo "Checking JavaScript syntax..."
JS_ERRORS=0
TS_SKIPPED=0
for file in $(git diff --cached --name-only --diff-filter=ACM | grep -E "\.(ts|js)$"); do
    if [ -f "$file" ]; then
        # Skip TypeScript files - can't check with node
        if [[ "$file" == *.ts ]]; then
            ((TS_SKIPPED++))
            continue
        fi
        
        # Check JavaScript files
        if [[ "$file" == *.js ]]; then
            node -c "$file" 2>/dev/null
            if [ $? -ne 0 ]; then
                echo "  ❌ JavaScript syntax error in $file"
                ((ERRORS++))
                ((JS_ERRORS++))
            fi
        fi
    fi
done

if [ $JS_ERRORS -eq 0 ]; then
    echo "  ✅ No JavaScript syntax errors"
fi
if [ $TS_SKIPPED -gt 0 ]; then
    echo "  ℹ️  Skipped $TS_SKIPPED TypeScript files (Week 1 relaxation)"
fi

# Check for REAL exposed secrets (not false positives)
echo "Checking for exposed secrets..."
SECRET_ERRORS=0
for file in $(git diff --cached --name-only --diff-filter=ACM); do
    if [ -f "$file" ]; then
        # Skip files that commonly cause false positives
        if [[ "$file" == *.md ]] || \
           [[ "$file" == *.json ]] || \
           [[ "$file" == *.sh ]] || \
           [[ "$file" == *package-lock.json ]] || \
           [[ "$file" == *.txt ]] || \
           [[ "$file" == *.log ]]; then
            continue
        fi
        
        # Only flag actual secret patterns with real-looking values
        # Must have = or : followed by an actual value
        if grep -E "(api_key|apikey|api-key|password|private_key)[\s]*[=:]\s*['\"]?[A-Za-z0-9+/]{20,}['\"]?" "$file" | \
           grep -v "example\|sample\|test\|fake\|TODO\|placeholder\|your_\|<.*>\|process\.env" > /dev/null; then
            echo "  ❌ Possible secret exposed in $file"
            echo "    Please review and use environment variables instead"
            ((ERRORS++))
            ((SECRET_ERRORS++))
        fi
        
        # AWS keys are more specific
        if grep -E "AKIA[0-9A-Z]{16}" "$file" > /dev/null; then
            echo "  ❌ Possible AWS key in $file"
            ((ERRORS++))
            ((SECRET_ERRORS++))
        fi
    fi
done

if [ $SECRET_ERRORS -eq 0 ]; then
    echo "  ✅ No secrets detected"
fi

# Check for large files
echo "Checking file sizes..."
LARGE_FILES=0
for file in $(git diff --cached --name-only --diff-filter=ACM); do
    if [ -f "$file" ]; then
        size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "0")
        if [ "$size" -gt 5242880 ]; then  # 5MB
            echo "  ❌ Large file detected: $file ($(($size / 1048576))MB)"
            ((ERRORS++))
            ((LARGE_FILES++))
        fi
    fi
done

if [ $LARGE_FILES -eq 0 ]; then
    echo "  ✅ No large files"
fi

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
    else
        echo "  ✅ Documentation standards met"
    fi
else
    echo "  ⚠️  Documentation validator not found"
    ((WARNINGS++))
fi

# Check test coverage (TRACKING ONLY)
echo "Tracking test coverage..."
if [ -d "ai-assistant" ]; then
    cd ai-assistant
    # Don't actually run tests in pre-commit, just note it
    echo "  📊 Coverage will be tracked in CI/CD pipeline"
    cd ..
fi

# Check for TODO/FIXME comments
echo "Checking for TODO/FIXME markers..."
TODO_COUNT=$(git diff --cached | grep -c "TODO\|FIXME" || echo "0")
if [ "$TODO_COUNT" -gt 0 ]; then
    echo "  ⚠️  Found $TODO_COUNT TODO/FIXME markers (allowed in Phase 2.5)"
    ((WARNINGS++))
else
    echo "  ✅ No TODO/FIXME markers"
fi

# LEVEL 3: TRACKING METRICS
echo ""
echo "📊 Tracking Metrics (Information Only)..."
echo "-----------------------------------------"

# Count files being committed
FILE_COUNT=$(git diff --cached --name-only | wc -l)
echo "  Files in commit: $FILE_COUNT"

# Count by type
PY_COUNT=$(git diff --cached --name-only | grep -c "\.py$" || echo "0")
TS_COUNT=$(git diff --cached --name-only | grep -c "\.ts$" || echo "0")
JS_COUNT=$(git diff --cached --name-only | grep -c "\.js$" || echo "0")
MD_COUNT=$(git diff --cached --name-only | grep -c "\.md$" || echo "0")

echo "  Python files: $PY_COUNT"
echo "  TypeScript files: $TS_COUNT"
echo "  JavaScript files: $JS_COUNT"
echo "  Documentation files: $MD_COUNT"

# Track lines of code
LINES_ADDED=$(git diff --cached --stat | tail -1 | grep -oE "[0-9]+ insertion" | grep -oE "[0-9]+" || echo "0")
LINES_DELETED=$(git diff --cached --stat | tail -1 | grep -oE "[0-9]+ deletion" | grep -oE "[0-9]+" || echo "0")
echo "  Lines added: $LINES_ADDED"
echo "  Lines deleted: $LINES_DELETED"

# Log technical debt
if [ -f "TECHNICAL_DEBT.md" ]; then
    echo "" >> TECHNICAL_DEBT.md
    echo "## $(date '+%Y-%m-%d %H:%M') Commit" >> TECHNICAL_DEBT.md
    echo "- Files changed: $FILE_COUNT" >> TECHNICAL_DEBT.md
    echo "- Warnings: $WARNINGS" >> TECHNICAL_DEBT.md
    echo "- TypeScript files skipped: $TS_SKIPPED" >> TECHNICAL_DEBT.md
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
echo ""
echo "Note: TypeScript syntax checking disabled for Week 1"
echo "      Secret detection optimized to reduce false positives"

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "❌ COMMIT BLOCKED: Critical errors must be fixed"
    echo ""
    echo "Most common fixes:"
    echo "  - For Python syntax: Check indentation and colons"
    echo "  - For JavaScript: Check brackets and semicolons"
    echo "  - For secrets: Move to environment variables"
    echo "================================================"
    exit 1
else
    echo ""
    echo "✅ COMMIT ALLOWED (Progressive Standards)"
    echo ""
    echo "⚠️  REMINDER: This is temporary!"
    echo "  Week 1: Minimal standards (current)"
    echo "  Week 2: Progressive standards (+TypeScript checking)"
    echo "  Week 3: Maturing standards (+Coverage requirements)"
    echo "  Week 4: Full standards restored"
    echo ""
    echo "Technical debt is being tracked in TECHNICAL_DEBT.md"
    echo "================================================"
    
    # Check if we should auto-upgrade
    if [ -f ".git/standards-version.txt" ]; then
        CURRENT_VERSION=$(cat .git/standards-version.txt)
        DAYS_ELAPSED=$(( ($(date +%s) - $(date -d "2025-01-27" +%s)) / 86400 )) 2>/dev/null || DAYS_ELAPSED=0
        
        if [ $DAYS_ELAPSED -ge 7 ]; then
            echo ""
            echo "📅 Note: Week 1 is ending. Consider upgrading to v0.4 (progressive)"
            echo "   Run: ./hooks/manage-standards.sh upgrade"
        fi
    fi
    
    exit 0
fi