@echo off
echo ========================================
echo Quick Install (No Virtual Environment)
echo ========================================
echo.
echo Installing backend dependencies...
echo.

pip install fastapi uvicorn asyncpg pydantic websockets
echo.

echo ========================================
echo Basic dependencies installed!
echo ========================================
echo.
echo To start: python main.py --port 8001
echo.
echo For full install with all dependencies:
echo   pip install -r requirements.txt
echo.
pause