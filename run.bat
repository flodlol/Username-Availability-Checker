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

:: Create virtual environment if needed
if not exist .venv\Scripts\python.exe (
    echo  📦 Creating virtual environment...
    python -m venv .venv
    echo.
)

set PYTHON=.venv\Scripts\python.exe

:: Install dependencies if needed
%PYTHON% -c "import colorama" >nul 2>&1
if errorlevel 1 (
    echo  📦 Installing dependencies...
    %PYTHON% -m pip install -r requirements.txt
    echo.
)

echo  ✅ Starting terminal app
echo     Press Ctrl+C to stop
echo.

%PYTHON% cli.py
pause
