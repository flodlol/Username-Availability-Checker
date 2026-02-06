@echo off
title Handle Scout

echo.
echo  🔎 Starting Handle Scout...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ Python is not installed.
    echo.
    echo  Please download Python from: https://python.org/downloads
    echo  Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

:: Install dependencies if needed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo  📦 Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo  ✅ Starting server at http://localhost:8000
echo     Press Ctrl+C to stop
echo.

python app.py
pause
