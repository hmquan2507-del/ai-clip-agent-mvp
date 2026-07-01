# State Machine

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define production, job, clip, render, and export states.

---

## Production States

```text
draft
  ↓
uploading
  ↓
uploaded
  ↓
analyzing
  ↓
generating
  ↓
ready_for_review
  ↓
exporting
  ↓
completed
```

Failure path:

```text
any running state
  ↓
failed
  ↓
retrying
```

---

## AI Job States

```text
pending
running
succeeded
failed
retrying
skipped
cancelled
```

---

## Generated Clip States

```text
pending_review
approved
rejected
needs_changes
regenerating
rendering
exported
```

---

## Render Job States

```text
pending
running
succeeded
failed
retrying
cancelled
```

---

## Export States

```text
pending
rendering
ready
downloaded
published
failed
expired
```

---

## State Rules

- Completed productions must have at least one successful export.
- Failed productions must preserve the failed stage.
- Regeneration should not destroy the previous clip version until a replacement succeeds.
- Retry should resume from the failed stage when possible.
