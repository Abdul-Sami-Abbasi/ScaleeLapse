@echo off
setlocal
rem ExecutionPolicy applies only to this child process, not to Windows settings.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start.ps1"
set "startupExitCode=%ERRORLEVEL%"
if not "%startupExitCode%"=="0" (
    echo.
    echo ScaleeLapse could not start. See the error above and README.md.
    pause
)
exit /b %startupExitCode%
