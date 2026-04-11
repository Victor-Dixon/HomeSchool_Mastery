@echo off
REM Project: Homeschool Lessons (Dream.OS)
REM File: START.bat
REM Purpose: One-click launcher (creates venv, installs deps, starts server).
REM Owner: Local family deployment (homeschool)
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv .venv
)

echo Installing/updating dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Starting Homeschool Lessons...
echo Keep this window open while the app is running.
echo.
".venv\Scripts\python.exe" main.py

endlocal
