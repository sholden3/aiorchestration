@echo off
echo AI Development Assistant - PTY Setup
echo =====================================
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0setup-pty.ps1"
pause