@echo off
REM Complete Hook Installation Script for Full Governance
REM Installs all hooks and validates the system

echo ========================================
echo INSTALLING FULL GOVERNANCE HOOKS
echo ========================================
echo.

cd /d "%~dp0"

REM Step 1: Install required packages
echo [1/5] Installing required packages...
pip install pre-commit coverage pytest black flake8 mypy >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install packages. Installing individually...
    pip install pre-commit
    pip install coverage
    pip install pytest
)

REM Step 2: Test governance enforcer
echo [2/5] Testing governance enforcer...
python governance_enforcer.py --quick >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Governance enforcer needs configuration
) else (
    echo [OK] Governance enforcer working
)

REM Step 3: Install pre-commit hooks
echo [3/5] Installing pre-commit hooks...
if exist .git (
    pre-commit install >nul 2>&1
    echo [OK] Pre-commit hooks installed
) else (
    echo [INFO] Not in a git repository, skipping pre-commit
)

REM Step 4: Create git hooks directory if needed
echo [4/5] Setting up git hooks...
if not exist ..\..\hooks mkdir ..\..\hooks

REM Create pre-commit hook
echo Creating pre-commit hook...
(
echo #!/bin/sh
echo # Full Governance Pre-commit Hook
echo cd ai-assistant/backend
echo python governance_enforcer.py --quick
echo exit $?
) > ..\..\hooks\pre-commit

REM Step 5: Validate installation
echo [5/5] Validating installation...
python -c "import sys; sys.path.append('.'); from governance_enforcer import EnhancedGovernanceEnforcer; print('[OK] Governance system imported successfully')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Import failed, checking dependencies...
    python -c "import persona_manager; print('[OK] persona_manager')" 2>nul || echo [MISSING] persona_manager
    python -c "import rules_enforcement; print('[OK] rules_enforcement')" 2>nul || echo [MISSING] rules_enforcement
    python -c "import cache_manager; print('[OK] cache_manager')" 2>nul || echo [MISSING] cache_manager
)

echo.
echo ========================================
echo INSTALLATION COMPLETE
echo ========================================
echo.
echo Next steps:
echo   1. Test with: python governance_enforcer.py --quick
echo   2. Daily use: daily_governance.bat morning
echo   3. Pre-commit: Will auto-run on git commit
echo.