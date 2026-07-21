$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendPath = Join-Path $ProjectRoot "backend"

if (-not (Test-Path $BackendPath)) {
    throw "Backend directory not found: $BackendPath"
}

Push-Location $BackendPath

try {
    $env:PYTHONPATH = $BackendPath

    python scripts\test_ripple_edit_policy_runtime.py

    if ($LASTEXITCODE -ne 0) {
        throw "Sprint 16.7.8 test failed."
    }

    Write-Host "Sprint 16.7.8 tests passed." -ForegroundColor Green
}
finally {
    Pop-Location
}
