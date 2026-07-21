$ErrorActionPreference = "Stop"
$PackageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Get-Location).Path

if (-not (Test-Path (Join-Path $RepoRoot "backend\app\review\editing"))) {
    throw "Hãy cd vào thư mục gốc ai-clip-agent-mvp trước khi chạy script."
}

Copy-Item -Path (Join-Path $PackageRoot "backend\*") -Destination (Join-Path $RepoRoot "backend") -Recurse -Force
Write-Host "Applied Sprint 16.7.8 overlay successfully." -ForegroundColor Green
