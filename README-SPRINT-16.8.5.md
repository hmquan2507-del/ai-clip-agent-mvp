# Sprint 16.8.5 — Export Workspace Frontend Runtime

Run from the repository root:

```powershell
Expand-Archive "$HOME\Downloads\sprint-16.8.5-export-workspace-frontend-runtime.zip" "$env:TEMP\sprint-16.8.5" -Force
```

```powershell
& "$env:TEMP\sprint-16.8.5\sprint-16.8.5-export-workspace-frontend-runtime\apply-and-test-sprint-16.8.5.ps1" -ProjectRoot (Get-Location).Path
```
