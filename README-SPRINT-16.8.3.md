# Sprint 16.8.3 — Export Workspace API Contracts & Controller

This package adds the Export Workspace HTTP contracts, application service, FastAPI controller, dependency factory, tests, documentation, and roadmap update.

## Apply and test

Run from the repository root:

```powershell
Expand-Archive "$HOME\Downloads\sprint-16.8.3-export-workspace-api-contracts-controller.zip" "$env:TEMP\sprint-16.8.3" -Force
```

```powershell
& "$env:TEMP\sprint-16.8.3\sprint-16.8.3-export-workspace-api-contracts-controller\apply-and-test-sprint-16.8.3.ps1" -ProjectRoot (Get-Location).Path
```

The installer copies complete source files. It does not patch Python code with PowerShell string replacement.
