@echo off
REM QuantDog React Frontend Starter

echo Starting QuantDog React Frontend...
echo ===================================

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

REM Start the React frontend
echo Starting development server on http://localhost:5173
echo Press Ctrl+C to stop the server
echo.

cd frontend && npm run dev