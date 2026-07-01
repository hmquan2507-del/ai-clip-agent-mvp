# Upload Validation

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace
Related Sprint: Sprint 3.2 Upload Experience

---

## Purpose

This document defines validation rules for video uploads.

Validation protects user experience, backend processing, storage cost, and AI pipeline reliability.

---

## Validation Principles

Validation should be:

- clear
- early
- actionable
- consistent
- safe by default

Users should understand what is wrong and what they can do next.

---

## Required Validation Rules

| Rule | Description | User Message |
|---|---|---|
| File required | User must select a file | Please choose a video file. |
| Supported format | File must be a supported video type | This video format is not supported yet. |
| Non-empty file | File size must be greater than zero | This file appears to be empty. |
| Size limit | File must fit current upload limit | This file is too large for the current plan. |
| Browser readable | Browser must be able to access file metadata | We could not read this file. Please try another video. |

---

## Initial Supported Formats

Recommended MVP formats:

- mp4
- mov
- webm

Future formats:

- mkv
- avi
- m4v

---

## File Size Policy

MVP should define a conservative limit.

Recommended initial limit:

```text
500 MB per source video
```

This can be changed later by plan, workspace, or billing tier.

---

## Duration Policy

Recommended MVP duration limit:

```text
Up to 60 minutes per source video
```

If duration cannot be detected in browser, backend should validate after upload.

---

## Validation Timing

Client-side validation:

- file presence
- extension
- mime type
- file size

Backend validation:

- true media type
- duration
- corruption
- storage acceptance
- security checks

Client validation improves UX but backend validation is authoritative.

---

## Error Message Rules

Error messages must:

- be specific
- avoid technical stack traces
- suggest next action
- preserve selected file when possible

Bad:

```text
Upload failed with error 500.
```

Good:

```text
We could not upload this video. Please check your connection and try again.
```

---

## Security Considerations

Uploads must not be trusted.

Backend should validate:

- mime type
- extension
- file signature when possible
- file size
- storage path
- ownership

---

## Exit Criteria

Upload validation is complete when invalid files are blocked before processing and users receive clear recovery instructions.
