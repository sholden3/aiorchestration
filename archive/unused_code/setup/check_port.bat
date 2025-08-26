@echo off
echo Checking port 8001...
echo.

netstat -ano | findstr :8001
if %errorlevel% == 0 (
    echo.
    echo Port 8001 is in use!
    echo.
    echo To kill the process, find the PID above and run:
    echo   taskkill /PID [number] /F
    echo.
    echo Or kill all Python processes:
    echo   taskkill /F /IM python.exe
) else (
    echo Port 8001 is free!
)
echo.
pause