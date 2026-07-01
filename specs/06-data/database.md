# Database Model

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define the database direction for AI Clip Agent.

---

## MVP Tables

Current MVP tables include:

- accounts
- jobs
- suggestions
- transcript_segments
- editor_assets
- editor_steps
- render_tasks
- outputs

---

## Future Tables

Production-ready schema should move toward:

- workspaces
- users
- workspace_members
- productions
- source_videos
- ai_jobs
- generated_clips
- reviews
- styles
- render_jobs
- exports
- credit_ledger
- subscriptions

---

## Migration Direction

Keep current MVP tables while the local app is useful.

Gradually introduce product language:

```text
jobs -> productions
suggestions -> generated_clips
outputs -> exports
render_tasks -> render_jobs
```

---

## Data Rules

- Store video files in filesystem or object storage, not database.
- Store metadata and storage keys in database.
- Keep production stage status queryable.
- Preserve failed states for retry and debugging.
- Track usage for future credits and billing.

---

## Required Indexes Later

- productions.workspace_id
- productions.status
- ai_jobs.production_id
- ai_jobs.status
- generated_clips.production_id
- generated_clips.review_status
- render_jobs.status
- exports.production_id
