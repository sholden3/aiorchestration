@echo off
echo ========================================
echo AI Development Assistant - Feature Test
echo ========================================
echo.

echo [1/8] Testing Backend Health...
curl -s http://localhost:8001/health > nul
if %errorlevel% == 0 (
    echo [OK] Backend is running
) else (
    echo [FAIL] Backend not responding - start with: python main.py --port 8001
    exit /b 1
)
echo.

echo [2/8] Testing Basic AI Execution...
curl -s -X POST "http://localhost:8001/ai/execute" -H "Content-Type: application/json" -d "{\"prompt\": \"Test prompt for validation\", \"use_cache\": false}" > test_result.tmp
findstr "success" test_result.tmp > nul
if %errorlevel% == 0 (
    echo [OK] AI execution working
) else (
    echo [FAIL] AI execution failed
)
del test_result.tmp
echo.

echo [3/8] Testing Cache System...
echo   First request (should cache)...
curl -s -X POST "http://localhost:8001/ai/execute" -H "Content-Type: application/json" -d "{\"prompt\": \"Cache test prompt\", \"use_cache\": true}" > nul
echo   Second request (should hit cache)...
curl -s -X POST "http://localhost:8001/ai/execute" -H "Content-Type: application/json" -d "{\"prompt\": \"Cache test prompt\", \"use_cache\": true}" > test_cache.tmp
findstr "\"cached\":true" test_cache.tmp > nul
if %errorlevel% == 0 (
    echo [OK] Cache system working
) else (
    echo [WARN] Cache not hitting - may need more requests
)
del test_cache.tmp
echo.

echo [4/8] Testing Three-Persona Governance...
curl -s -X POST "http://localhost:8001/ai/orchestrated" -H "Content-Type: application/json" -d "{\"prompt\": \"Governance test\", \"context\": {}}" > test_gov.tmp
findstr "success" test_gov.tmp > nul
if %errorlevel% == 0 (
    echo [OK] Governance system active
    echo   Check backend terminal for persona decisions
) else (
    echo [FAIL] Governance system error
)
del test_gov.tmp
echo.

echo [5/8] Testing WebSocket Status...
curl -s http://localhost:8001/ws/status > test_ws.tmp
findstr "active_connections" test_ws.tmp > nul
if %errorlevel% == 0 (
    echo [OK] WebSocket endpoint available
) else (
    echo [FAIL] WebSocket not configured
)
del test_ws.tmp
echo.

echo [6/8] Testing Orchestration Status...
curl -s http://localhost:8001/orchestration/status > test_orch.tmp
findstr "is_running" test_orch.tmp > nul
if %errorlevel% == 0 (
    echo [OK] Orchestration status available
) else (
    echo [FAIL] Orchestration status error
)
del test_orch.tmp
echo.

echo [7/8] Checking Cache Metrics...
curl -s http://localhost:8001/metrics/cache
echo.
echo.

echo [8/8] Final Cache Performance Test...
echo Running 5 identical requests...
for /L %%i in (1,1,5) do (
    curl -s -X POST "http://localhost:8001/ai/execute" -H "Content-Type: application/json" -d "{\"prompt\": \"Performance test\", \"use_cache\": true}" > nul
    echo   Request %%i complete
)
echo.
echo Final cache metrics:
curl -s http://localhost:8001/metrics/cache
echo.
echo.

echo ========================================
echo Test Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Check dashboard at http://localhost:4200 (if Electron running)
echo 2. Monitor backend terminal for governance decisions
echo 3. Run USE_GUIDE.md tests for detailed validation
echo.
pause