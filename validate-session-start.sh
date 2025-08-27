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