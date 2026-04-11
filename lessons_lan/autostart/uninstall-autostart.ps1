$ErrorActionPreference = "Stop"

<#
Project: Homeschool Lessons (Dream.OS)
File: autostart/uninstall-autostart.ps1
Purpose: Remove Scheduled Task auto-start entry.
Owner: Local family deployment (homeschool)
#>

$taskName = "HomeschoolLessons"

schtasks /Delete /F /TN $taskName | Out-Null
Write-Host "Removed auto-start task: $taskName"

