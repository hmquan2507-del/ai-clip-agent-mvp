# Entities

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define the main data entities for AI Clip Agent.

---

## Core Entities

### Workspace

Groups users, productions, styles, assets, billing, credits, and settings.

### User

Person who uses the product.

### Production

Main aggregate root.

Represents one complete AI video production workflow.

### Source Video

Uploaded original video.

### AI Job

One processing stage in the AI pipeline.

### Generated Clip

AI-created short video candidate.

### Review

Human review state for generated clips.

### Style

Reusable production recipe.

### Render Job

Background job that creates output video files.

### Export

Final rendered output ready for download or publishing.

### Credit Ledger

Tracks usage cost by workspace and production.

---

## Entity Ownership

```text
Workspace
  ├─ Users
  ├─ Productions
  │   ├─ Source Video
  │   ├─ AI Jobs
  │   ├─ Generated Clips
  │   ├─ Render Jobs
  │   └─ Exports
  ├─ Styles
  └─ Credit Ledger
```

---

## MVP Mapping

Current MVP names use `jobs` and `suggestions`.

Future product language should migrate toward:

- jobs -> productions
- suggestions -> generated clips
- render_tasks -> render jobs
- outputs -> exports
