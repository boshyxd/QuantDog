@echo off
REM QuantDog Full Development Environment Starter

echo Starting QuantDog Development Environment...
echo ============================================

REM Check if UV is available
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: UV not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend && npm install
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
    cd ..
)

echo Starting both backend and frontend...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop all services
echo.

REM Start backend in background
start /b "QuantDog API" cmd /c "uv run uvicorn main:app --reload --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend (this will keep the window open)
cd frontend && npm run dev