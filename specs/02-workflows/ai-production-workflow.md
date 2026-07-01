# AI Production Workflow

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define the end-to-end AI production workflow.

This is the main product workflow.

---

## Workflow

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

## Detailed Steps

```text
Create Production
  ↓
Upload Source Video
  ↓
Extract Metadata
  ↓
Generate Transcript
  ↓
Detect Scenes
  ↓
Detect Speakers
  ↓
Detect Highlights
  ↓
Select Clips
  ↓
Apply Style
  ↓
Generate Subtitles
  ↓
Plan B-roll
  ↓
Plan Music
  ↓
Plan Sound FX
  ↓
Render Preview / Output
  ↓
Review
  ↓
Export
```

---

## Inputs

- Source video
- Selected style
- User goal or content niche
- Optional brand settings
- Optional output platform

---

## Outputs

- Generated clips
- Hook, caption, CTA
- Subtitle plan
- B-roll plan
- Music plan
- Sound FX plan
- Rendered video outputs

---

## User Decisions

- Choose style
- Approve clips
- Reject clips
- Regenerate clips
- Export approved clips

---

## Failure States

- Upload failed
- Transcript failed
- AI analysis failed
- Clip generation failed
- Render failed
- Export failed

Failures should be recoverable by retrying the failed stage.

---

## Non-goals

- Manual timeline editing as the primary workflow
- Complex keyframe editing
- Professional NLE replacement
