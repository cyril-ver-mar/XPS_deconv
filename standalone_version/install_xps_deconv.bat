@echo off
setlocal EnableExtensions
REM XPS-Deconv bootstrap launcher for Windows.
REM Run from cmd or PowerShell:
REM   .\install_xps_deconv.bat
REM Do NOT run the .ps1 directly if Execution Policy is Restricted —
REM this .bat starts PowerShell with -ExecutionPolicy Bypass.

set "SCRIPT_DIR=%~dp0"
set "PS1=%SCRIPT_DIR%install_xps_deconv.ps1"

if not exist "%PS1%" (
  echo.
  echo   ERROR: install_xps_deconv.ps1 not found next to this .bat
  echo   Keep BOTH files in the same folder, then run:
  echo     .\install_xps_deconv.bat
  echo.
  exit /b 1
)

where powershell >nul 2>&1
if errorlevel 1 (
  echo.
  echo   ERROR: PowerShell is required.
  echo.
  exit /b 1
)

echo.
echo   Starting bootstrap via PowerShell Bypass...
echo.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
  echo.
  echo   Bootstrap failed with code %ERR%.
  echo   Re-download BOTH install_xps_deconv.bat and install_xps_deconv.ps1
  echo   from the latest GitHub Release, then run:  .\install_xps_deconv.bat
  echo.
)
exit /b %ERR%
