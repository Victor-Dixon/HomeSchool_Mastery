<#
Project: Homeschool Lessons (Dream.OS)
File: autostart/install-startup-folder.ps1
Purpose: Install Startup-folder launcher for auto-start at user login.
Owner: Local family deployment (homeschool)
#>

$ErrorActionPreference = "Stop"

$appDir = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $PSScriptRoot "run-hidden.ps1"

$startupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
New-Item -ItemType Directory -Force -Path $startupDir | Out-Null

$cmdPath = Join-Path $startupDir "HomeschoolLessons.cmd"

$cmd = @"
@echo off
cd /d "$appDir"
powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "$runner" -AppDir "$appDir"
"@

Set-Content -Path $cmdPath -Value $cmd -Encoding ASCII

Write-Host "Installed Startup-folder launcher:"
Write-Host $cmdPath
Write-Host "It will start when you log in."

