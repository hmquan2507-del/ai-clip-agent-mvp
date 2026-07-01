# Data Model - AI Production Workspace

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC 2.2

---

## Purpose

Define the data needed for the AI Production Workspace.

---

## Product Model

```text
Production
  ->
Source Video
  ->
AI Jobs
  ->
Generated Clips
  ->
Review State
  ->
Render Jobs
  ->
Exports
```

---

## MVP Mapping

Current backend:

- jobs
- suggestions
- render_tasks
- outputs

Product UI language:

- productions
- generated_clips
- render_jobs
- exports

---

## Production Fields

- id
- title
- status
- source_video
- style
- objective
- created_at
- updated_at

---

## Generated Clip Fields

- id
- production_id
- start
- duration
- hook
- caption
- cta
- score
- reason
- review_status
- render_status

---

## Review State

- pending_review
- approved
- rejected
- needs_changes
- regenerating

---

## Export State

- pending
- rendering
- ready
- failed
- downloaded
