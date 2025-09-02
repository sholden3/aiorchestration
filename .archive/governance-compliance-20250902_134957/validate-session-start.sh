#!/bin/bash
# Session Start Script - Data-driven version
# Uses centralized session manager

echo "=== SESSION INITIALIZATION ==="
echo "Date: $(date)"

# Use Python session manager to create session
python .governance/core/session_manager.py create

# Load configuration for checks
CONFIG_FILE=".governance/config/governance-config.json"

echo ""
echo "[CHECK] SYSTEM STATE VALIDATION"

# Backend health check
cd ai-assistant/backend 2>/dev/null && {
    python -c "import main; print('[PASS] Backend imports work')" 2>/dev/null || echo "[FAIL] Backend import failure"
    cd - > /dev/null
} || echo "[SKIP] Backend directory not found"

# Frontend build check
cd ai-assistant 2>/dev/null && {
    npm run build --silent 2>/dev/null && echo "[PASS] Frontend builds" || echo "[FAIL] Frontend build failure"
    cd - > /dev/null
} || echo "[SKIP] Frontend directory not found"

echo ""
echo "[CHECK] TEST BASELINE VALIDATION"

# Backend test discovery
cd ai-assistant/backend 2>/dev/null && {
    count=$(python -m pytest --co -q 2>/dev/null | wc -l)
    echo "Backend tests available: $count"
    cd - > /dev/null
} || echo "[SKIP] Backend tests not accessible"

# Frontend test check
cd ai-assistant 2>/dev/null && {
    npm test -- --passWithNoTests --silent 2>/dev/null && echo "[PASS] Frontend tests pass" || echo "[WARN] Frontend test issues"
    cd - > /dev/null
} || echo "[SKIP] Frontend tests not accessible"

echo ""
echo "[CHECK] CRITICAL SYSTEMS CHECK"

# Health endpoint check
curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "[PASS] Backend responding" || echo "[INFO] Backend not running"

# Process check (cross-platform)
if command -v pgrep > /dev/null 2>&1; then
    pgrep -f "python.*main.py" > /dev/null && echo "[PASS] Backend process running" || echo "[INFO] Backend process not found"
else
    ps aux 2>/dev/null | grep -q "python.*main.py" && echo "[PASS] Backend process running" || echo "[INFO] Backend process not found"
fi

echo ""
echo "[CHECK] DOCUMENTATION CURRENCY CHECK"

# Count fix documents
if [ -d "docs/fixes" ]; then
    count=$(ls docs/fixes/ 2>/dev/null | wc -l)
    echo "Fix documents available: $count"
else
    echo "[INFO] No fixes directory"
fi

# Check CLAUDE.md currency
current_month=$(date +%Y-%m)
grep -q "$current_month" CLAUDE.md 2>/dev/null && echo "[PASS] CLAUDE.md current" || echo "[INFO] CLAUDE.md may need update"

echo ""
echo "=== SESSION READY ==="

# Display session info
python .governance/core/session_manager.py info