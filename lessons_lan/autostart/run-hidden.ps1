<#
Project: Homeschool Lessons (Dream.OS)
File: autostart/run-hidden.ps1
Purpose: Start the server hidden at login (Startup folder / task runner).
Owner: Local family deployment (homeschool)
#>

param(
  [string]$AppDir = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

Set-Location $AppDir

# Ensure venv exists
if (!(Test-Path ".venv\Scripts\python.exe")) {
  python -m venv .venv
}

# Ensure deps are installed (idempotent)
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt | Out-Null

$logDir = Join-Path $AppDir "instance"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "server.log"

# Start server in background (no console window)
Start-Process -FilePath ".venv\Scripts\python.exe" `
  -ArgumentList @("run.py") `
  -WorkingDirectory $AppDir `
  -WindowStyle Hidden `
  -RedirectStandardOutput $logPath `
  -RedirectStandardError $logPath

