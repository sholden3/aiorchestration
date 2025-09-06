@echo off
REM @fileoverview Environment setup script for Windows development
REM @author Dr. Sarah Chen & Alex Novak
REM @description Sets up Python paths and environment for Windows developers

REM Get the root directory of the monorepo
set MONOREPO_ROOT=%~dp0..\..
cd /d "%MONOREPO_ROOT%"

echo Setting up AI Orchestration Platform development environment...
echo Monorepo root: %MONOREPO_ROOT%

REM Export PYTHONPATH to include all necessary directories
set PYTHONPATH=%MONOREPO_ROOT%;%MONOREPO_ROOT%\libs;%MONOREPO_ROOT%\apps;%PYTHONPATH%
echo PYTHONPATH configured

REM Set NODE_PATH for TypeScript imports
set NODE_PATH=%MONOREPO_ROOT%\node_modules;%MONOREPO_ROOT%\libs
echo NODE_PATH configured

REM Create Python virtual environment if it doesn't exist
if not exist "%MONOREPO_ROOT%\.venv" (
    echo Creating Python virtual environment...
    python -m venv "%MONOREPO_ROOT%\.venv"
    echo Virtual environment created
)

REM Activate virtual environment
call "%MONOREPO_ROOT%\.venv\Scripts\activate.bat"
echo Virtual environment activated

REM Install Python dependencies in development mode
echo Installing Python packages in development mode...
cd /d "%MONOREPO_ROOT%"
pip install -e . -q
echo Python packages installed

REM Install git hooks for governance
echo Installing git pre-commit hooks...
python "%MONOREPO_ROOT%\tools\scripts\install_git_hooks.py" --force
echo Git hooks installed

echo.
echo Environment setup complete!
echo.
echo Available commands:
echo   python apps\api\main.py         - Start the FastAPI backend
echo   cd apps\web ^&^& npm start       - Start the Angular frontend  
echo   pytest tests\ -xvs              - Run all tests
echo.
echo Dr. Sarah Chen: "The Three Questions Framework is active"
echo Alex Novak: "All systems defensive and ready"