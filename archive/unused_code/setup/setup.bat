@echo off
echo ========================================
echo AI Assistant Backend Setup
echo ========================================
echo.

echo Checking Python version...
python --version
echo.

echo Creating virtual environment (recommended)...
python -m venv venv
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Installing requirements...
pip install -r requirements.txt
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the backend:
echo   1. Activate venv: venv\Scripts\activate
echo   2. Run: python main.py --port 8001
echo.
pause