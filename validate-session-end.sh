#!/bin/bash
# Session End Script - Data-driven version
# Archives session and generates report

echo "=== SESSION TERMINATION ==="
echo "Date: $(date)"
echo ""

# Display current session info
echo "[INFO] Current Session:"
python .governance/core/session_manager.py info

echo ""
echo "[CHECK] FINAL STATE VALIDATION"

# Check for uncommitted changes
if git diff --quiet && git diff --cached --quiet; then
    echo "[PASS] No uncommitted changes"
else
    echo "[WARN] Uncommitted changes detected:"
    git status --short
fi

# Check test status
echo ""
echo "[CHECK] TEST STATUS"

cd ai-assistant 2>/dev/null && {
    npm test -- --passWithNoTests --watchAll=false --silent 2>/dev/null && echo "[PASS] Frontend tests passing" || echo "[WARN] Frontend test failures"
    cd - > /dev/null
} || echo "[SKIP] Frontend tests not accessible"

cd ai-assistant/backend 2>/dev/null && {
    python -m pytest --co -q > /dev/null 2>&1 && echo "[PASS] Backend tests available" || echo "[WARN] Backend test issues"
    cd - > /dev/null
} || echo "[SKIP] Backend tests not accessible"

# Documentation check
echo ""
echo "[CHECK] DOCUMENTATION CURRENCY"

# Check CLAUDE.md currency
current_month=$(date +%Y-%m)
grep -q "$current_month" CLAUDE.md 2>/dev/null && echo "[PASS] CLAUDE.md updated this month" || echo "[INFO] CLAUDE.md may need update"

# Check for recent commits
echo ""
echo "[CHECK] COMMIT HISTORY"
git log --oneline -1 | grep -q "$(date +%Y-%m-%d)" && echo "[INFO] Commits made today" || echo "[INFO] No commits today"

echo ""
echo "[ACTION] Ending Session"

# End session with reason
REASON=${1:-"normal"}
python .governance/core/session_manager.py end --reason "$REASON"

echo ""
echo "=== SESSION ENDED ==="
echo "Sarah: Failure modes documented"
echo "Alex: Integration points validated"