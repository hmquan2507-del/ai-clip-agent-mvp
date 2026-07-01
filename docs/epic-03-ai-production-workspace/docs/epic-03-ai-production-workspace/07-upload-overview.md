# Upload Overview

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace
Related Sprint: Sprint 3.2 Upload Experience

---

## Purpose

This document defines the Upload experience for AI Clip Agent.

Upload is the first active production step. It turns a user's source video into a Production that can enter the AI processing queue.

---

## Product Intent

The Upload experience must be simple, fast, and confidence-building.

The user should not feel like they are configuring an editor. The user should feel like they are starting an AI production workflow.

Primary user intent:

```text
I have a video.
I want AI to turn it into usable clips or a finished production.
```

---

## Upload Position In Product Flow

```text
Home
  ↓
Upload
  ↓
AI Queue
  ↓
Review
  ↓
Export
```

Upload is not a standalone file manager. Upload exists to start a Production.

---

## Core Outcome

A successful upload creates:

- a Production
- a source Asset
- an initial Production state
- an AI processing job
- a visible queue item

---

## Primary Screen Responsibilities

The Upload screen should allow users to:

- drag and drop a video file
- select a video file from device
- understand accepted formats
- see file validation results
- see upload progress
- cancel before processing starts
- continue to AI Queue after upload

---

## Non-Goals

The Upload experience should not include:

- timeline editing
- advanced video trimming
- manual subtitle editing
- render settings
- billing configuration
- admin dashboard concepts

---

## Upload Entry Points

Users can start upload from:

- Home screen primary CTA
- Production list empty state
- Workspace header action
- Existing Production retry action

All entry points should lead to the same upload flow.

---

## Upload States

```text
Idle
  ↓
File Selected
  ↓
Validating
  ↓
Ready To Upload
  ↓
Uploading
  ↓
Uploaded
  ↓
Queued
```

Failure states:

```text
Invalid File
Upload Failed
Network Failed
User Cancelled
```

---

## User Expectations

The user should always know:

- what file is selected
- whether the file is valid
- upload progress
- what happens after upload
- whether AI processing has started

---

## Success Criteria

Upload is successful when:

- file is accepted
- file is stored
- Production is created
- Production enters AI Queue
- user can navigate to progress view

---

## Cross References

- specs/01-product/domain-model.md
- specs/02-workflows/upload-workflow.md
- specs/05-backend/api-specification.md
- specs/06-data/state-machine.md
- docs/epic-03-ai-production-workspace/01-workspace-overview.md
- docs/epic-03-ai-production-workspace/06-routing.md
