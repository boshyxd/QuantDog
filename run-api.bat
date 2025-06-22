@echo off
REM QuantDog FastAPI Backend Starter

echo Starting QuantDog FastAPI Backend...
echo ====================================

REM Check if UV is available
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: UV not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Start the FastAPI backend
echo Starting server on http://localhost:8000
echo API docs available at http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.

uv run uvicorn main:app --reload --port 8000 --host 0.0.0.0