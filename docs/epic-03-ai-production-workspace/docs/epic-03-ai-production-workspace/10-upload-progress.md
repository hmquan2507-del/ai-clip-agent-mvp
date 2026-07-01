# Upload Progress

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace
Related Sprint: Sprint 3.2 Upload Experience

---

## Purpose

This document defines how upload progress should be displayed in the AI Production Workspace.

---

## User Goal

The user wants confidence that the video is being uploaded and that AI processing will begin after upload finishes.

---

## Progress States

```text
Preparing
Uploading
Processing Upload
Creating Production
Adding To Queue
Queued
```

---

## UI Requirements

The upload progress UI should show:

- file name
- progress percentage
- progress bar
- current phase label
- estimated status message
- cancel or retry action where applicable

---

## Phase Labels

Recommended labels:

| Phase | Label |
|---|---|
| Preparing | Preparing upload |
| Uploading | Uploading video |
| Processing Upload | Checking video |
| Creating Production | Creating production |
| Adding To Queue | Adding to AI queue |
| Queued | Ready for AI processing |

---

## Progress Behavior

Upload progress should represent actual network upload when possible.

After file transfer completes, progress can transition to system phases.

Example:

```text
0–90%: file transfer
90–100%: production creation and queue setup
```

---

## Cancel Behavior

Cancel is allowed when:

- upload is active
- production has not started AI processing

Cancel should not be allowed once AI processing has started unless queue cancellation is supported.

---

## Retry Behavior

Retry should be available when:

- network upload fails
- backend validation fails with recoverable error
- queue creation fails after upload

If upload succeeded but queue creation failed, retry should not require re-upload.

---

## Completion Behavior

When upload completes:

- show success state briefly
- redirect to AI Queue, or
- show CTA to view AI progress

Preferred behavior for MVP:

```text
Auto-navigate to AI Queue after success.
```

---

## Accessibility

Progress should be accessible to screen readers.

Requirements:

- progress bar has accessible label
- phase changes are announced
- actions are keyboard accessible

---

## Exit Criteria

Upload progress is complete when users can clearly understand whether upload is active, successful, failed, or queued.
