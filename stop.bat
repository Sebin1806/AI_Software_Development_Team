@echo off
setlocal enabledelayedexpansion
echo ===================================================
echo   AI Software Development Team - Stopping Application
echo ===================================================
echo.

echo [INFO] Stopping FastAPI Backend and React Frontend processes...

:: Stop windows by title
taskkill /FI "WINDOWTITLE eq AI Team Backend*" /F /T >nul 2>&1
taskkill /FI "WINDOWTITLE eq AI Team Frontend*" /F /T >nul 2>&1

:: Stop processes listening on port 8000 (Backend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000"') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: Stop processes listening on port 5173 (Frontend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173"') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo [SUCCESS] All application servers have been stopped.
echo.
pause
