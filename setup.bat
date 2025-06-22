@echo off
setlocal EnableDelayedExpansion
REM QuantDog Setup Script for Windows with UV Package Manager

echo === QuantDog Setup Script ===

REM Check if UV is installed
where uv >nul 2>&1
if !errorlevel! neq 0 (
    echo UV not found. Installing UV...
    powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    REM Add UV to PATH for current session (UV installs to %USERPROFILE%\.local\bin)
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
    
    REM Verify UV installation
    where uv >nul 2>&1
    if !errorlevel! neq 0 (
        echo.
        echo UV was installed but not found in PATH. 
        echo Please restart your command prompt or manually add to PATH:
        echo set Path=%USERPROFILE%\.local\bin;%%Path%%
        echo.
        echo Then run setup.bat again.
        pause
        exit /b 1
    )
)

echo UV found: 
uv --version

REM Sync dependencies
echo Installing dependencies with UV...
uv sync --all-extras

REM Copy environment file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
)

REM Run linter check
echo Running linter check...
uv run ruff check . --fix

REM Run formatter
echo Formatting code...
uv run ruff format .

echo.
echo ✓ Setup complete!
echo.
echo To start the app, run:
echo    uv run uvicorn api:app --reload --port 8000
echo.
echo Other useful commands:
echo    uv run pytest tests/     # Run tests
echo    uv run ruff check . --fix   # Run linter
echo    uv run ruff format .     # Format code
pause