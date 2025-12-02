@echo off
title Multi-Sport Parlay Generator
echo ========================================
echo 🏆 Multi-Sport Parlay Generator
echo    NFL ^| NBA ^| NHL
echo ========================================
echo.
echo Starting application...
echo.

python Multi_Sport_Parlay_Generator.py

if errorlevel 1 (
    echo.
    echo ❌ Error launching application
    echo.
    pause
)
