@echo off
setlocal enabledelayedexpansion
echo ===================================================
echo   AI Software Development Team - Automated Setup
echo ===================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Setup Failed! Python is not installed or not added to your PATH environment variable.
    echo Please install Python 3.11 or higher from https://www.python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

echo [SETUP 1/6] Checking Python installation...
python --version

:: 2. Check & Copy .env files
echo.
echo [SETUP 2/6] Checking Environment Configuration (.env)...
if not exist "backend\.env" (
    if exist "backend\.env.example" (
        echo [INFO] Copying backend\.env.example to backend\.env...
        copy "backend\.env.example" "backend\.env" >nul
    ) else if exist ".env.example" (
        echo [INFO] Copying .env.example to backend\.env...
        copy ".env.example" "backend\.env" >nul
    )
)

if not exist "backend\.env" (
    echo [ERROR] Setup Failed! backend\.env configuration file could not be created.
    echo Please create backend\.env manually from backend\.env.example.
    pause
    exit /b 1
) else (
    echo [SUCCESS] backend\.env configuration file verified.
)

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
    )
)

:: 3. Create Python Virtual Environment
echo.
echo [SETUP 3/6] Setting up Python Virtual Environment (backend\venv)...
if not exist "backend\venv" (
    echo [INFO] Creating Python virtual environment in backend\venv...
    python -m venv backend\venv
    if %errorlevel% neq 0 (
        echo [ERROR] Setup Failed! Failed to create Python virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] Python virtual environment exists.
)

:: 4. Install Backend Dependencies
echo.
echo [SETUP 4/6] Installing Backend Python Dependencies...
call backend\venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
call backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt pytest httpx
if %errorlevel% neq 0 (
    echo [ERROR] Setup Failed! Failed to install backend dependencies. Please check your internet connection.
    pause
    exit /b 1
)
echo [SUCCESS] Backend dependencies installed successfully.

:: 5. Install Frontend Dependencies
echo.
echo [SETUP 5/6] Checking Node.js and Frontend Dependencies...
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Node.js or npm is not installed or not in PATH.
    echo Please install Node.js v18 or higher to run the frontend interface.
) else (
    echo [INFO] Installing frontend npm packages...
    cd frontend
    call npm install
    if %errorlevel% neq 0 (
        cd ..
        echo [ERROR] Setup Failed! Failed to install frontend npm packages.
        pause
        exit /b 1
    )
    cd ..
    echo [SUCCESS] Frontend dependencies installed successfully.
)

:: 6. Database Auto-Check & Alembic Migrations
echo.
echo [SETUP 6/6] Checking Database and Running Alembic Migrations...
call backend\venv\Scripts\python.exe scripts\check_env.py
if %errorlevel% neq 0 (
    echo.
    echo ===================================================
    echo   [ERROR] Setup Failed! Database check failed.
    echo ===================================================
    echo Please check database credentials in backend\.env and ensure PostgreSQL is running.
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Running Alembic Database Migrations...
set PYTHONPATH=.
cd backend
..\backend\venv\Scripts\python.exe -m alembic upgrade head
if %errorlevel% neq 0 (
    echo.
    echo ===================================================
    echo   [ERROR] Setup Failed! Alembic Database Migration Failed.
    echo ===================================================
    echo Please verify PostgreSQL is running and credentials in backend\.env are correct.
    echo.
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo ===================================================
echo   Setup Completed Successfully!
echo ===================================================
echo.
echo To start the application, run:
echo   start.bat
echo.
pause
