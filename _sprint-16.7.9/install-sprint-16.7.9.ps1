$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Copy-Item "$PSScriptRoot\backend\*" "$ProjectRoot\backend" -Recurse -Force
Write-Host "Applied Sprint 16.7.9 overlay successfully." -ForegroundColor Green
