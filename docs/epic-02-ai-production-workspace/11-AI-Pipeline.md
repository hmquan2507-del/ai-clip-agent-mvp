# AI Pipeline - AI Production Workspace

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC 2.2

---

## Purpose

Define how AI pipeline stages appear inside the workspace.

---

## Visible Pipeline

For users, show simple stages:

```text
Uploading
  ->
Transcribing
  ->
Finding Highlights
  ->
Generating Clips
  ->
Applying Style
  ->
Rendering Preview
  ->
Ready For Review
```

---

## Internal Pipeline

The internal pipeline can include:

- Transcript
- Scene Detection
- Speaker Detection
- Highlight Detection
- Clip Selection
- Apply Style
- Subtitle
- B-roll
- Music
- Sound FX
- Motion
- Render

---

## Workspace Rules

- AI Queue should show user-friendly stages.
- Review should show useful AI reasoning.
- Errors should show the failed stage and retry action.
- Technical model/provider details should stay hidden from normal users.

---

## MVP Behavior

Use current AI suggestions backend where available.

If AI provider is missing or fails, use heuristic fallback so the flow does not break.
