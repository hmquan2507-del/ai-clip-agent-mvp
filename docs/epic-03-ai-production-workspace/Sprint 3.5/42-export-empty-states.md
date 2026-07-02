# Export Empty States

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.5 Export Experience

---


## Purpose

Define empty states for the Export Experience.

## Empty State Types

- Production not approved
- No export created yet
- Export history empty
- Render result unavailable
- Export expired

## Message Rules

Empty states should:

- explain why export is unavailable
- guide user to the next step
- link back to Review when approval is required

## Example

```text
This Production is not ready for export yet.

Review and approve the AI output before creating an export.
```

## Exit Criteria

Users should always understand why export is unavailable and what to do next.
