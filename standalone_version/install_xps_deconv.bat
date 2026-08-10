@echo off
setlocal EnableExtensions
REM Thin launcher — real logic is in install_xps_deconv.ps1 (same folder).

set "SCRIPT_DIR=%~dp0"
set "PS1=%SCRIPT_DIR%install_xps_deconv.ps1"

if not exist "%PS1%" (
  echo.
  echo   ERROR: install_xps_deconv.ps1 not found next to this .bat
  echo   Keep both files in the same folder.
  echo.
  exit /b 1
)

where powershell >nul 2>&1
if errorlevel 1 (
  echo.
  echo   ERROR: PowerShell is required.
  echo   Fix: use Windows 10+ or install PowerShell, then re-run.
  echo.
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
exit /b %ERRORLEVEL%
