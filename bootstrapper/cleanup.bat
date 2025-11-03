@echo off
REM Bootstrap Cleanup Tool - Batch Wrapper
REM This script provides easy access to the cleanup tool

echo.
echo Bootstrap Cleanup Tool
echo =====================
echo.
echo Choose cleanup mode:
echo 1. GUI Mode (recommended)
echo 2. Console Mode
echo 3. Exit
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Starting GUI cleanup tool...
    python cleanup.py
) else if "%choice%"=="2" (
    echo Starting console cleanup tool...
    python cleanup.py --console
) else if "%choice%"=="3" (
    echo Goodbye!
    goto :end
) else (
    echo Invalid choice! Please enter 1, 2, or 3.
    pause
    goto :start
)

:end
pause