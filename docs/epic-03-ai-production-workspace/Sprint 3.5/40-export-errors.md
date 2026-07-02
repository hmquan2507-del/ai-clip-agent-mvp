# Export Errors

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.5 Export Experience

---


## Purpose

Define error handling for export and render failures.

## Common Errors

- Render failed
- Source asset missing
- Subtitle asset missing
- Storage upload failed
- Export expired
- Insufficient credits
- Unsupported format
- Worker timeout

## Error Message Rules

Error messages should:

- explain the issue
- show whether retry is possible
- avoid technical blame
- provide next action

## User Actions

Possible actions:

- Retry export
- Change settings
- Return to Review
- Contact support
