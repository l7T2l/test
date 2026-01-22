@echo off
chcp 65001 >nul
title Smart Keyboard - Run & Test

echo ════════════════════════════════════════════════════════════════
echo    Smart Keyboard .NET - Build and Run
echo ════════════════════════════════════════════════════════════════
echo.

cd /d "d:\Sandbox\MQ8M\DefaultBox\user\current\Downloads\Smart keyboard\SmartKeyboard.NET"

echo [1/2] Building project...
dotnet build --configuration Debug

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Build failed! Check errors above.
    pause
    exit /b 1
)

echo.
echo [2/2] Running application...
echo.
echo ════════════════════════════════════════════════════════════════
echo    Application is starting...
echo    Close this window to stop the application.
echo ════════════════════════════════════════════════════════════════
echo.

dotnet run --no-build

echo.
echo Application closed.
pause
