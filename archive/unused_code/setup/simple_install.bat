@echo off
echo ========================================
echo Simple Install - Guaranteed to Work
echo ========================================
echo.

echo Installing only essential packages...
echo.

echo [1/4] Installing FastAPI...
pip install fastapi
if %errorlevel% neq 0 (
    echo FastAPI installation failed, trying without version...
    pip install --no-deps fastapi
)

echo.
echo [2/4] Installing Uvicorn...
pip install uvicorn
if %errorlevel% neq 0 (
    echo Uvicorn installation failed, trying standard version...
    pip install --no-deps uvicorn
)

echo.
echo [3/4] Installing WebSockets...
pip install websockets

echo.
echo [4/4] Installing other essentials...
pip install python-dotenv
pip install typing-extensions

echo.
echo ========================================
echo Basic Installation Complete!
echo ========================================
echo.
echo Note: Some features may be limited without full dependencies.
echo The mock mode will work fine for testing.
echo.
echo To start the backend:
echo   cd backend
echo   python main.py --port 8001
echo.
echo If you get import errors, we'll fix them as we go.
echo.
pause