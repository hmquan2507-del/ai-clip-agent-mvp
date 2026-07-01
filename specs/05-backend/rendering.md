# Rendering Architecture

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define the render engine direction for AI Clip Agent.

Render should turn approved AI edit plans into final video outputs.

---

## Render Inputs

- Source video
- Clip start/end
- Style
- Subtitle plan
- Hook
- Caption
- CTA
- B-roll plan
- Music plan
- Sound FX plan
- Motion plan
- Export format

---

## MVP Render Output

Prioritize:

- MP4
- 9:16 vertical
- 1080x1920
- Social-ready short clips

---

## Render Job Lifecycle

```text
pending
  ↓
running
  ↓
succeeded / failed
```

With retries:

```text
failed
  ↓
retrying
  ↓
running
```

---

## Render Engine Direction

MVP can use FFmpeg directly.

Future render engine should support:

- Style-based templates
- Subtitle rendering
- Motion presets
- B-roll compositing
- Sound FX
- Music
- Progress reporting
- Output validation

---

## Output Validation

Validate:

- File exists
- Duration is reasonable
- Resolution matches export preset
- File is playable
- Output size is not zero

---

## Non-goals

- Full NLE engine in MVP
- Manual keyframe editor in MVP
- Cloud render farm before product flow is proven
