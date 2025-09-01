# SESSION START CHECKLIST
echo "=== SESSION INITIALIZATION ==="
echo "Date: $(date)"
echo "Architects: Alex Novak & Dr. Sarah Chen active"
echo ""

# 1. SYSTEM STATE VALIDATION
echo "[CHECK] SYSTEM STATE VALIDATION"
cd ai-assistant/backend
python -c "import main; print('[PASS] Backend imports work')" || echo "[FAIL] Backend import failure"
cd ../
npm run build --silent && echo "[PASS] Frontend builds" || echo "[FAIL] Frontend build failure"
echo ""

# 2. TEST BASELINE VALIDATION  
echo "[CHECK] TEST BASELINE VALIDATION"
cd ai-assistant/backend
python -m pytest --co -q | wc -l | xargs echo "Backend tests available:"
cd ../
npm test -- --passWithNoTests --silent && echo "[PASS] Frontend tests pass" || echo "[FAIL] Frontend test failure"
echo ""

# 3. CRITICAL SYSTEMS CHECK
echo "[CHECK] CRITICAL SYSTEMS CHECK"
curl -s http://localhost:8000/health > /dev/null && echo "[PASS] Backend responding" || echo "[FAIL] Backend down"
ps aux | grep -q "python.*main.py" && echo "[PASS] Backend process running" || echo "[FAIL] Backend process missing"
echo ""

# 4. DOCUMENTATION CURRENCY CHECK
echo "[CHECK] DOCUMENTATION CURRENCY CHECK"
ls docs/fixes/ | wc -l | xargs echo "Fix documents available:"
grep -q "$(date +%Y-%m)" CLAUDE.md && echo "[PASS] CLAUDE.md current" || echo "[FAIL] CLAUDE.md outdated"
echo ""

echo "=== SESSION READY ==="
echo "Sarah: Ready for failure mode analysis"
echo "Alex: Ready for integration validation"