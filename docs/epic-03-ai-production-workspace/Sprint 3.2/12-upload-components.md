# Upload Components

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace
Related Sprint: Sprint 3.2 Upload Experience

---

## Purpose

This document defines the UI components required for the Upload experience.

---

## Component List

Required components:

- UploadDropzone
- FileSummary
- ValidationMessage
- UploadProgress
- UploadError
- UploadSuccess
- UploadActions

---

## UploadDropzone

Purpose:

Allows users to drag and drop or select a source video.

States:

- idle
- drag active
- file selected
- disabled
- error

Content:

- primary instruction
- supported formats
- size guidance
- browse button

Recommended copy:

```text
Drop your video here or choose a file
```

---

## FileSummary

Purpose:

Displays selected file information before upload.

Fields:

- file name
- file size
- file type
- estimated duration if available

Actions:

- remove file
- choose another file

---

## ValidationMessage

Purpose:

Displays validation result.

Types:

- info
- success
- warning
- error

Validation messages should be placed near the selected file summary.

---

## UploadProgress

Purpose:

Displays active upload progress.

Elements:

- progress bar
- percentage
- phase label
- current action text
- cancel button if available

---

## UploadError

Purpose:

Shows upload failure and recovery actions.

Elements:

- title
- short explanation
- recovery action
- secondary action

Common actions:

- Retry
- Choose another file
- Go back home

---

## UploadSuccess

Purpose:

Confirms upload completion and transition to AI Queue.

Recommended copy:

```text
Video uploaded. AI production is starting.
```

Primary action:

```text
View AI Progress
```

---

## UploadActions

Purpose:

Controls upload flow actions.

Actions:

- Start AI Production
- Cancel
- Retry
- Choose another file

---

## Component Ownership

Upload components belong to the AI Production Workspace.

They should not contain business rules.

Validation and workflow decisions should come from API and domain logic.

---

## Empty State

When no file is selected, the upload area should clearly invite action.

Suggested empty state:

```text
Upload a source video to start an AI production.
```

---

## Responsive Behavior

Desktop:

- large dropzone
- file summary beside or below dropzone

Mobile:

- compact file picker
- stacked layout
- no reliance on drag and drop

---

## Exit Criteria

Upload components are complete when the upload experience can support idle, validation, progress, success, and error states consistently.
