# Export Workflow

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define how approved clips become final rendered exports.

---

## Workflow

```text
Select Approved Clips
  ↓
Choose Export Format
  ↓
Create Render Jobs
  ↓
Render Queue
  ↓
Validate Output
  ↓
Download / Publish
```

---

## Inputs

- Approved generated clips
- Style settings
- Export platform
- Aspect ratio
- Resolution
- Caption/subtitle settings

---

## Output Formats

MVP should prioritize:

- 9:16 vertical video
- MP4
- 1080x1920

Later:

- 1:1 square
- 16:9 landscape
- Platform-specific presets

---

## Render Queue States

- pending
- running
- succeeded
- failed
- retrying
- cancelled

---

## Success State

The user receives final video files ready to download or publish.

---

## Failure States

- Render failed
- Storage failed
- Output validation failed
- Export expired

Failed exports should support retry.

---

## Non-goals

- Auto-publishing in MVP
- Advanced export analytics in MVP
- Multi-platform scheduling in MVP
