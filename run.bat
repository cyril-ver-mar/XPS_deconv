@echo off
setlocal
cd /d "%~dp0"
if not exist venv (
  echo venv missing — run install.bat first
  exit /b 1
)
call venv\Scripts\activate.bat
python launch.py
