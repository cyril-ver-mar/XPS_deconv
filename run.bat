@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

for /f "delims=" %%A in ('echo prompt $E^| cmd') do set "ESC=%%A"
set "C_ACCENT=%ESC%[38;2;217;119;87m"
set "C_OK=%ESC%[38;2;61;154;110m"
set "C_ERR=%ESC%[38;2;196;74;74m"
set "C_DIM=%ESC%[2m"
set "C_BOLD=%ESC%[1m"
set "C_RESET=%ESC%[0m"

echo.
echo %C_ACCENT%%C_BOLD%  +----------------------------------------------+
echo   ^|                                              ^|
echo   ^|   XPS-Deconv                                 ^|
echo   ^|   Starting Streamlit...                      ^|
echo   ^|                                              ^|
echo   +----------------------------------------------+%C_RESET%
echo %C_DIM%  http://localhost:8501  ·  Ctrl+C to stop%C_RESET%
echo.
echo %C_BOLD%  If the browser does not open automatically:%C_RESET%
echo   %C_ACCENT%·%C_RESET% open http://localhost:8501 yourself
echo   %C_ACCENT%·%C_RESET% or try http://127.0.0.1:8501
echo   %C_ACCENT%·%C_RESET% if the port is busy, stop the other Streamlit and re-run
echo.

if not exist "venv\Scripts\python.exe" (
  echo.
  echo %C_ERR%+-- Error ------------------------------------------+%C_RESET%
  echo %C_ERR%^|%C_RESET% Virtual environment missing                      %C_ERR%^|%C_RESET%
  echo %C_ERR%+----------------------------------------------------+%C_RESET%
  echo.
  echo %C_BOLD%How to fix%C_RESET%
  echo   %C_ACCENT%·%C_RESET% Run: install.bat
  echo   %C_ACCENT%·%C_RESET% Then: run.bat
  echo.
  exit /b 1
)

if not exist app.py (
  echo.
  echo %C_ERR%+-- Error ------------------------------------------+%C_RESET%
  echo %C_ERR%^|%C_RESET% app.py not found                                  %C_ERR%^|%C_RESET%
  echo %C_ERR%+----------------------------------------------------+%C_RESET%
  echo.
  echo %C_BOLD%How to fix%C_RESET%
  echo   %C_ACCENT%·%C_RESET% cd into the XPS-Deconv project folder
  echo.
  exit /b 1
)

if not exist launch.py (
  echo.
  echo %C_ERR%+-- Error ------------------------------------------+%C_RESET%
  echo %C_ERR%^|%C_RESET% launch.py not found                               %C_ERR%^|%C_RESET%
  echo %C_ERR%+----------------------------------------------------+%C_RESET%
  echo.
  exit /b 1
)

if not exist requirements.txt (
  echo.
  echo %C_ERR%+-- Error ------------------------------------------+%C_RESET%
  echo %C_ERR%^|%C_RESET% requirements.txt not found                         %C_ERR%^|%C_RESET%
  echo %C_ERR%+----------------------------------------------------+%C_RESET%
  echo.
  echo %C_BOLD%How to fix%C_RESET%
  echo   %C_ACCENT%·%C_RESET% cd into the XPS-Deconv project folder
  echo.
  exit /b 1
)

call "venv\Scripts\activate.bat"
echo   %C_OK%✓%C_RESET% venv ready
echo   %C_ACCENT%-^>%C_RESET% checking packages (install missing from requirements.txt)...
set PYTHONPATH=%CD%
python -m src.utils.deps_check --ensure
if errorlevel 1 (
  echo.
  echo %C_ERR%+-- Error ------------------------------------------+%C_RESET%
  echo %C_ERR%^|%C_RESET% Could not install or verify required packages     %C_ERR%^|%C_RESET%
  echo %C_ERR%+----------------------------------------------------+%C_RESET%
  echo.
  echo %C_BOLD%How to fix%C_RESET%
  echo   %C_ACCENT%·%C_RESET% Check network / pip, then: install.bat
  echo   %C_ACCENT%·%C_RESET% Or: venv\Scripts\activate ^&^& pip install -r requirements.txt
  echo   %C_ACCENT%·%C_RESET% Then: run.bat
  echo.
  exit /b 1
)
echo   %C_OK%✓%C_RESET% all runtime packages ready
echo   %C_ACCENT%-^>%C_RESET% launching...
echo.

python launch.py
set "EC=%ERRORLEVEL%"
if not "%EC%"=="0" (
  echo.
  echo %C_ERR%Streamlit exited with code %EC%%C_RESET%
  echo %C_BOLD%How to fix%C_RESET%
  echo   %C_ACCENT%·%C_RESET% If port 8501 is busy, stop the other Streamlit process
  echo   %C_ACCENT%·%C_RESET% Re-run install.bat if packages are broken
  echo.
)
endlocal
exit /b %EC%
