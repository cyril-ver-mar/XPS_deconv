@echo off
setlocal EnableExtensions
REM XPS-Deconv Windows bootstrap (ONE file is enough).
REM Always downloads the latest install_xps_deconv.ps1 from GitHub master,
REM then runs it with ExecutionPolicy Bypass.
REM
REM Usage (PowerShell or cmd), from the folder where you want the app:
REM   .\install_xps_deconv.bat

where powershell >nul 2>&1
if errorlevel 1 (
  echo ERROR: PowerShell not found.
  exit /b 1
)

set "PS1=%TEMP%\xps_deconv_install_fresh.ps1"
set "RAW=https://raw.githubusercontent.com/cyril-ver-mar/XPS_deconv/master/standalone_version/install_xps_deconv.ps1"

echo.
echo   XPS-Deconv bootstrap launcher
echo   Downloading latest installer script from GitHub...
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { $u='%RAW%?t=' + [guid]::NewGuid().ToString(); Invoke-WebRequest -UseBasicParsing -Uri $u -OutFile '%PS1%'; if (-not (Test-Path '%PS1%')) { exit 1 }; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }"
if errorlevel 1 (
  echo.
  echo   Download from GitHub failed.
  echo   If you have install_xps_deconv.ps1 next to this .bat, trying local copy...
  if exist "%~dp0install_xps_deconv.ps1" (
    copy /Y "%~dp0install_xps_deconv.ps1" "%PS1%" >nul
  ) else (
    echo   No local install_xps_deconv.ps1 found. Check network / GitHub.
    exit /b 1
  )
)

echo   Running installer...
echo.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
set "ERR=%ERRORLEVEL%"
del "%PS1%" >nul 2>&1
exit /b %ERR%
