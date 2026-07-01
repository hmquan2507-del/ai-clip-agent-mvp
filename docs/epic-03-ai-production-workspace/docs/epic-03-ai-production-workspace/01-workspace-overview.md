# Workspace Overview

Status: Draft
Owner: Ho Quan
Version: 0.1
Last Updated: 2026-07-01
Related Epic: EPIC-03 AI Production Workspace
Depends On: EPIC-02 Product Specification

---

## Purpose

This document defines the AI Production Workspace for AI Clip Agent.

The workspace is the main product surface where users create, monitor, review, and export AI-generated video productions.

The workspace must not behave like a traditional admin dashboard or timeline editor.

It must guide the user through one clear production flow:

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

---

## Product Goal

The workspace exists to help users save 80–95% of video editing time.

The user should not start from a blank editor.

The user should start from AI-generated output and then review, approve, regenerate, or export.

---

## Core Object

The workspace is centered around one primary object:

```text
Production
```

A Production represents one complete AI video production workflow from source upload to final export.

The workspace should not be organized around generic admin concepts such as dashboards, reports, or manual projects.

---

## Primary User Flow

```text
User opens workspace
  ↓
User starts a new Production
  ↓
User uploads source video
  ↓
AI pipeline processes the video
  ↓
User reviews generated clips/output
  ↓
User approves or regenerates
  ↓
User exports final video
```

---

## Workspace Responsibilities

The workspace is responsible for:

- starting new Productions
- listing existing Productions
- showing Production status
- guiding users to the next action
- exposing upload, queue, review, and export states
- making AI output reviewable
- reducing manual editing decisions

---

## Non-Goals

The workspace is not:

- a traditional video timeline editor
- an admin dashboard
- a file manager
- a generic project management tool
- a fully manual editing suite

Manual editing may exist later, but only as a correction layer after AI output.

---

## Key Screens

The first workspace version includes:

1. Home Screen
2. Production List
3. Upload Entry
4. AI Queue Entry
5. Review Entry
6. Export Entry

Detailed screen specifications are defined in sibling documents.

---

## Production Status Overview

The workspace should display Production progress using clear status labels.

Recommended initial statuses:

| Status | Meaning | Primary User Action |
|---|---|---|
| Draft | Production exists but no file uploaded | Continue upload |
| Uploading | Source video is uploading | Wait or cancel |
| Uploaded | Source video uploaded successfully | Start AI processing |
| Processing | AI pipeline is running | Monitor progress |
| Needs Review | AI output is ready | Review output |
| Approved | Output has been approved | Export |
| Rendering | Final video is rendering | Monitor progress |
| Completed | Render is complete | Download/export |
| Failed | A step failed | Retry or inspect error |

---

## Workspace Success Criteria

The workspace is successful when:

- users always know the next action
- users can start a Production in under one minute
- users can understand AI progress without reading logs
- users can review AI output without opening a timeline editor
- users can export without manual rendering setup

---

## Design Principles

The workspace must follow these principles:

- AI first
- Production first
- Review instead of edit
- Automation over configuration
- One clear flow
- Human final approval
- Specification before implementation

---

## Future Expansion

Future workspace features may include:

- batch production
- team collaboration
- style presets
- auto publishing
- scheduling
- analytics
- billing and credits

These features must not break the core production flow.

---

## Cross References

Related documents:

- specs/00-governance/product-principles.md
- specs/00-governance/definition-of-done.md
- specs/01-product/core-domain.md
- specs/01-product/domain-model.md
- specs/02-workflows/ai-production-workflow.md
- specs/03-ai/ai-pipeline.md
- specs/04-frontend/workspace.md
- specs/06-data/state-machine.md
- specs/08-epics/traceability-matrix.md
