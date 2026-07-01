# AI Pipeline

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define the AI pipeline that powers AI Clip Agent.

This pipeline is the heart of the product.

---

## Pipeline

```text
Upload
  ↓
Transcript
  ↓
Scene Detection
  ↓
Speaker Detection
  ↓
Highlight Detection
  ↓
Clip Selection
  ↓
Apply Style
  ↓
Subtitle
  ↓
B-roll
  ↓
Music
  ↓
Sound FX
  ↓
Motion
  ↓
Render
  ↓
Review
  ↓
Export
```

---

## Pipeline Stages

### Transcript

Convert spoken audio into timestamped text.

Output:

- Segment text
- Start time
- End time
- Confidence when available

### Scene Detection

Detect visual scene boundaries and major changes.

Output:

- Scene segments
- Visual change points
- Candidate cut boundaries

### Speaker Detection

Detect speaker changes and speaker-heavy sections.

Output:

- Speaker segments
- Speaker change timestamps

### Highlight Detection

Find moments with strong content value.

Signals:

- Pain point
- Surprise
- Story
- Proof
- Money
- Result
- Emotion
- Urgency
- Teaching value

### Clip Selection

Choose short segments that can become social clips.

Output:

- Start
- End
- Duration
- Score
- Reason
- Hook direction

### Apply Style

Convert clip content into a style-specific edit plan.

### Subtitle

Generate subtitle text and timing.

### B-roll

Plan B-roll or visual overlay moments.

### Music

Select music direction by style, mood, and pacing.

### Sound FX

Plan emphasis sound effects.

### Motion

Plan zoom, crop, movement, and pacing.

---

## MVP Pipeline

MVP can start with:

- Transcript or transcript fallback
- Highlight Detection
- Clip Selection
- Hook, caption, CTA generation
- Basic Style Engine
- Render

Scene Detection, Speaker Detection, B-roll, Music, Sound FX, and Motion can begin as planned layers before becoming full automated systems.
