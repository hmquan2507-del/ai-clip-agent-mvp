# Upload Errors

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace
Related Sprint: Sprint 3.2 Upload Experience

---

## Purpose

This document defines upload error handling for AI Clip Agent.

Upload errors should be recoverable whenever possible.

---

## Error Categories

| Category | Example | Recovery |
|---|---|---|
| Validation | Unsupported format | Choose another file |
| Network | Connection lost | Retry upload |
| Storage | Storage failed | Retry later |
| Backend | Production creation failed | Retry creation |
| Queue | AI queue failed | Retry queue |
| Permission | User not allowed | Login or upgrade |

---

## Error Message Principles

Upload errors must be:

- human-readable
- specific
- non-technical
- actionable
- consistent

---

## Validation Errors

Validation errors occur before upload begins.

Examples:

```text
This video format is not supported yet. Please upload an MP4, MOV, or WEBM file.
```

```text
This file is too large for the current upload limit.
```

---

## Network Errors

Network errors occur during upload.

Recommended message:

```text
Upload was interrupted. Please check your connection and try again.
```

Actions:

- Retry
- Choose another file

---

## Storage Errors

Storage errors occur when the backend cannot store the file.

Recommended message:

```text
We could not save this video. Please try again in a moment.
```

Actions:

- Retry
- Contact support in future SaaS version

---

## Production Creation Errors

This occurs when file upload succeeds but Production creation fails.

The system should avoid requiring another full upload if the asset already exists.

Recommended message:

```text
The video uploaded, but we could not create the production. Please retry.
```

---

## Queue Errors

This occurs when Production exists but AI job cannot be queued.

Recommended message:

```text
The production was created, but AI processing could not start. Please retry adding it to the queue.
```

---

## Permission Errors

Permission errors occur when user limits or authentication block upload.

Examples:

- unauthenticated user
- plan limit reached
- workspace permission denied
- credit limit reached

---

## Error Recovery Rules

Do not lose user progress unnecessarily.

If possible:

- preserve selected file
- preserve uploaded asset
- preserve created Production
- allow retry from failed step

---

## Logging

Every upload failure should be logged with:

- user id if available
- workspace id if available
- production id if available
- asset id if available
- error category
- timestamp

---

## Exit Criteria

Upload error handling is complete when every known failure path provides a clear message and recovery action.
