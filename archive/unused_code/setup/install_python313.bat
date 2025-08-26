@echo off
echo ========================================
echo Python 3.13 Compatible Install
echo ========================================
echo.
echo Your Python version:
python --version
echo.

echo Installing compatible packages...
echo.

REM Core packages that work with Python 3.13
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install websockets==12.0
pip install python-dotenv==1.0.0

REM Try pydantic without specific version (will get latest compatible)
echo.
echo Installing pydantic (may take a moment)...
pip install pydantic

REM Optional packages
echo.
echo Installing optional packages...
pip install python-json-logger==2.0.7
pip install python-multipart==0.0.6

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo If pydantic failed, the system will still work in mock mode.
echo.
echo To start backend:
echo   python main.py --port 8001
echo.
pause