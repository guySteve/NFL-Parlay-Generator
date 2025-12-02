@echo off
REM Launcher for NFL Parlay Generator Pro Desktop Edition
REM This batch file launches the Python GUI application

title NFL Parlay Generator Pro - Launcher

echo.
echo ========================================
echo   NFL PARLAY GENERATOR PRO
echo   Desktop Edition v2.0
echo ========================================
echo.
echo Starting application...
echo.

REM Try to run with python3 first, then python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python "%~dp0NFL_Parlay_Desktop_Pro.py"
) else (
    py -3 "%~dp0NFL_Parlay_Desktop_Pro.py"
)

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Could not launch application.
    echo Make sure Python 3.12+ is installed.
    echo.
    pause
)
