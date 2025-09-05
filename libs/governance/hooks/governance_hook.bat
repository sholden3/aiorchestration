@echo off
REM Claude Code Governance Hook for Windows
REM This script is called by Claude Code to enforce governance

echo.
echo ============================================================
echo          GOVERNANCE SYSTEM INTERCEPTING OPERATION          
echo ============================================================
echo.

REM Get timestamp
for /f "tokens=1-3 delims=:." %%a in ("%time%") do (
    set TIMESTAMP=%%a:%%b:%%c
)

REM Set hook type
set CLAUDE_HOOK_TYPE=%1
if "%CLAUDE_HOOK_TYPE%"=="" set CLAUDE_HOOK_TYPE=decision

REM Log the governance action
echo [%TIMESTAMP%] GOVERNANCE: Validating AI operation...
echo   Type: %CLAUDE_HOOK_TYPE%
echo   Working Dir: %CD%
echo.

REM Run the Python governance hook
python "%~dp0claude_code_governance_hook.py" %*

REM Check for specific operations
if "%CLAUDE_HOOK_TYPE%"=="pre-write" (
    echo [GOVERNANCE] Pre-write validation: Checking for dangerous patterns...
)
if "%CLAUDE_HOOK_TYPE%"=="post-write" (
    echo [GOVERNANCE] Post-write audit: Logging changes...
)
if "%CLAUDE_HOOK_TYPE%"=="pre-execute" (
    echo [GOVERNANCE] Pre-execution check: Validating command safety...
)

echo.
echo Governance check complete - Operation monitored and logged
echo.