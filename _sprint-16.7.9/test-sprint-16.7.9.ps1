$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendPath = Join-Path $ProjectRoot "backend"
Push-Location $BackendPath
try {
  $env:PYTHONPATH = $BackendPath
  $tests = @(
    "scripts\test_ripple_edit_policy_runtime.py",
    "scripts\test_manual_editing_integration_regression.py",
    "scripts\test_timeline_mutation_runtime.py",
    "scripts\test_timeline_history_runtime.py",
    "scripts\test_timeline_runtime_integration.py",
    "scripts\test_timeline_clipboard_edge_cases.py"
  )
  foreach ($test in $tests) {
    if (Test-Path $test) {
      Write-Host "Running $test" -ForegroundColor Cyan
      python $test
      if ($LASTEXITCODE -ne 0) { throw "Regression failed: $test" }
    } else {
      Write-Host "Skipping missing optional test: $test" -ForegroundColor Yellow
    }
  }
  Write-Host "Sprint 16.7.9 regression suite passed." -ForegroundColor Green
} finally { Pop-Location }
