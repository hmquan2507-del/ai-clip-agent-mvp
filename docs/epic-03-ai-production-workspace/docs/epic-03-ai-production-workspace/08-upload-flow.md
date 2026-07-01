# Upload Flow

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace
Related Sprint: Sprint 3.2 Upload Experience

---

## Purpose

This document defines the step-by-step Upload flow inside the AI Production Workspace.

---

## Flow Summary

```text
User opens Upload
  ↓
User selects video
  ↓
System validates file
  ↓
User confirms upload
  ↓
System uploads file
  ↓
System creates Production
  ↓
System queues AI processing
  ↓
User moves to AI Queue
```

---

## Step 1 — Open Upload

Trigger sources:

- Home CTA
- Empty Production List CTA
- Workspace header upload button

System behavior:

- display upload dropzone
- display supported formats
- display max file guidance
- display short explanation of next step

---

## Step 2 — Select Video

Supported interactions:

- drag and drop
- click to browse
- keyboard accessible file picker

After selection, the system should display:

- file name
- file size
- detected type
- estimated duration if available

---

## Step 3 — Validate File

Validation should run before upload begins.

Validation checks:

- file exists
- supported video format
- file size within limit
- file is not empty
- file can be read by browser

Optional future checks:

- video duration limit
- resolution limit
- audio track presence
- duplicate upload detection

---

## Step 4 — Confirm Upload

If validation passes, show:

- selected file summary
- primary button: Start AI Production
- secondary action: Choose another file

The CTA should avoid editor language.

Preferred label:

```text
Start AI Production
```

Not preferred:

```text
Open Editor
```

---

## Step 5 — Upload File

During upload, show:

- progress percentage
- current file name
- upload status
- cancel action if supported

The user should not be able to start duplicate uploads from the same selected file while upload is active.

---

## Step 6 — Create Production

After file upload succeeds, the system creates a Production.

Minimum Production data:

- production id
- source asset id
- owner id
- workspace id
- initial status
- created timestamp

---

## Step 7 — Queue AI Processing

After Production creation, the system creates an AI processing job.

The user should be redirected to AI Queue or shown a strong CTA:

```text
View AI Progress
```

---

## Step 8 — Continue To AI Queue

The Upload flow completes when the Production is visible in the AI Queue.

---

## Failure Recovery

If upload fails before Production creation:

- keep user on Upload screen
- show actionable error
- allow retry

If upload succeeds but queue creation fails:

- create a recoverable Production state
- show retry queue action
- do not require re-upload if file is stored

---

## Exit Criteria

This flow is complete when the user can reliably move from file selection to AI Queue without manual configuration.
