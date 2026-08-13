@echo off
setlocal enabledelayedexpansion
echo ===================================================
echo   AI Software Development Team - Starting Application
echo ===================================================
echo.

if not exist "backend\venv" (
    echo [ERROR] Virtual environment not found. Please run setup.bat first!
    pause
    exit /b 1
)

if not exist "backend\.env" (
    if exist "backend\.env.example" (
        copy "backend\.env.example" "backend\.env" >nul
    )
)

echo [1/2] Launching FastAPI Backend Server on http://localhost:8000 ...
start "AI Team Backend" cmd /k "title AI Team Backend && cd backend && set PYTHONPATH=. && venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

echo [2/2] Launching React Frontend Interface on http://localhost:5173 ...
start "AI Team Frontend" cmd /k "title AI Team Frontend && cd frontend && npm run dev"

echo.
echo ===================================================
echo   Application Servers Launched Successfully!
echo ===================================================
echo.
echo 🌐 Web Application Interface: http://localhost:5173
echo ⚙️ Backend API Documentation: http://localhost:8000/docs
echo.
echo To stop all servers cleanly, run:
echo   stop.bat
echo.
pause
