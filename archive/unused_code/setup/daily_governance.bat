@echo off
REM Daily Governance Activation Script
REM Implements v4.0 enhanced governance with automation

echo ========================================
echo ENHANCED GOVERNANCE SYSTEM v4.0
echo ========================================
echo.

cd /d "%~dp0"

REM Morning startup (5 minutes)
if "%1"=="morning" (
    echo [MORNING] Activating enhanced three-persona governance...
    python -c "from governance_enforcer import EnhancedGovernanceEnforcer; e = EnhancedGovernanceEnforcer(); print(e.predict_governance_risks())"
    echo.
    echo [OK] Governance active with predictive analytics
    goto end
)

REM Pre-commit check (30 seconds)
if "%1"=="precommit" (
    echo [PRE-COMMIT] Running rapid governance validation...
    python governance_enforcer.py --quick
    goto end
)

REM End of day review (2 minutes)
if "%1"=="review" (
    echo [REVIEW] Analyzing daily governance patterns...
    python -c "from governance_enforcer import EnhancedGovernanceEnforcer; import asyncio; e = EnhancedGovernanceEnforcer(); asyncio.run(e.generate_governance_report({}))"
    echo.
    echo [OK] Learning metrics updated for tomorrow
    goto end
)

REM Default: Show menu
echo Usage:
echo   daily_governance.bat morning   - Morning startup check
echo   daily_governance.bat precommit - Pre-commit validation  
echo   daily_governance.bat review    - End of day review
echo.

:end