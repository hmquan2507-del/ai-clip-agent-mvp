# Sprint 16.7.8 — Ripple Edit Policy & Runtime

Backend-authoritative, atomic ripple editing foundation.

## Included
- Explicit policies: `disabled`, `track`, `all_unlocked_tracks`.
- Atomic ripple delete and close-range commands.
- Optimistic revision conflict protection.
- Locked-track exclusion for all-track ripple.
- Crossing-clip rejection to avoid implicit destructive trims.
- One successful store commit and one revision increment.
- Regression test script and PowerShell installer.

## Apply
Run from the repository root:

```powershell
Expand-Archive .\sprint-16.7.8-ripple-edit-policy-runtime.zip -DestinationPath .\_sprint-16.7.8 -Force
powershell -ExecutionPolicy Bypass -File .\_sprint-16.7.8\install-sprint-16.7.8.ps1
powershell -ExecutionPolicy Bypass -File .\_sprint-16.7.8\test-sprint-16.7.8.ps1
```
