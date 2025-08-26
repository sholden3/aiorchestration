@echo off
echo ========================================
echo AI ORCHESTRATION SYSTEM - QUICK START
echo ========================================
echo.

REM Set environment variables for immediate use
set MAX_HOT_CACHE_ITEMS=100
set DB_HOST=localhost
set ANTHROPIC_API_KEY=%ANTHROPIC_API_KEY%

REM Create cache directories if they don't exist
if not exist cache\warm mkdir cache\warm

echo [1/3] Setting up environment...
pip install -q -r requirements.txt 2>nul

echo [2/3] Initializing cache directories...
python -c "from pathlib import Path; Path('cache/warm').mkdir(parents=True, exist_ok=True); Path('cache/cold').mkdir(parents=True, exist_ok=True)"

echo [3/3] Starting AI Orchestration CLI...
echo.
python persona_cli.py %*