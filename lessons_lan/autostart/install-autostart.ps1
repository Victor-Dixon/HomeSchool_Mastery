$ErrorActionPreference = "Stop"

<#
Project: Homeschool Lessons (Dream.OS)
File: autostart/install-autostart.ps1
Purpose: Install Scheduled Task auto-start (may require elevation).
Owner: Local family deployment (homeschool)
#>

$taskName = "HomeschoolLessons"
$appDir = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $PSScriptRoot "run-hidden.ps1"

if (!(Test-Path $runner)) {
  throw "Missing runner script: $runner"
}

# Create/replace scheduled task to run at logon (CURRENT USER, no admin)
$action = "powershell.exe"
$args = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$runner`" -AppDir `"$appDir`""
$user = "$env:USERDOMAIN\$env:USERNAME"

schtasks /Create /F /SC ONLOGON /TN $taskName /TR "`"$action`" $args" /RU $user | Out-Null

Write-Host "Installed auto-start task: $taskName"
Write-Host "It will start when you log in."

