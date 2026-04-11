<#
Project: Homeschool Lessons (Dream.OS)
File: autostart/uninstall-startup-folder.ps1
Purpose: Remove Startup-folder launcher for auto-start.
Owner: Local family deployment (homeschool)
#>

$ErrorActionPreference = "Stop"

$startupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$cmdPath = Join-Path $startupDir "HomeschoolLessons.cmd"

if (Test-Path $cmdPath) {
  Remove-Item -Force $cmdPath
  Write-Host "Removed Startup-folder launcher:"
  Write-Host $cmdPath
} else {
  Write-Host "Nothing to remove (not found):"
  Write-Host $cmdPath
}

