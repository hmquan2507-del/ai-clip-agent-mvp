# PRD - AI Production Workspace

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC 2.2

---

## Purpose

Define the first real product workspace for AI Clip Agent.

The workspace turns the project from a render tool into an AI Video Production Platform.

---

## Problem

Creators and businesses spend hours manually editing videos.

They need to:

- Watch full videos
- Find highlights
- Cut clips
- Write hooks
- Add subtitles
- Add B-roll
- Add music
- Render outputs

This is slow and repetitive.

---

## Product Promise

Upload once.

AI edits everything.

Review.

Export.

---

## Primary Flow

```text
Home
  ->
Upload
  ->
AI Queue
  ->
Review
  ->
Export
```

---

## Target Users

Primary:

- Solo content creator
- Business owner / personal brand
- Small marketing team

Secondary:

- Agency
- Educator
- Course creator

---

## Core Requirements

- User can start a new production from Home.
- User can upload a source video.
- System can show AI processing progress.
- System can show generated clips for review.
- User can approve, reject, or regenerate clips.
- User can export approved clips.
- Interface must be route/page based, not one long dashboard.

---

## Non-goals

- Full admin dashboard
- Timeline-first manual editor
- Advanced team billing
- Auto publish
- Deep analytics

---

## Success Criteria

- User understands the production flow within one screen.
- User can move from upload to AI queue to review to export.
- Dashboard clutter is removed.
- Existing backend MVP logic can still be reused during migration.
- The workspace clearly supports future AI pipeline expansion.
