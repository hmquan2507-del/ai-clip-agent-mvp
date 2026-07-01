# User Journeys

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define the primary user journeys for AI Clip Agent.

These journeys guide workflow, UX, UI, API, data, queue, and AI pipeline decisions.

---

## Primary Journey - Produce Short Videos From One Source Video

### User

Solo creator, business owner, marketer, or agency operator.

### Goal

Turn one long-form or raw video into multiple ready-to-review short videos with minimal manual editing.

### Journey

```text
Home
  ↓
Start New Production
  ↓
Upload Source Video
  ↓
Choose Style
  ↓
AI Queue
  ↓
Review Generated Clips
  ↓
Approve or Regenerate
  ↓
Export
```

### Desired Outcome

The user receives multiple short-form clips with subtitle, hook, caption, CTA, motion, music, B-roll, and render-ready output.

### Success Criteria

- User can start without understanding video editing.
- AI generates useful clips before the user edits anything.
- User can approve, reject, or regenerate clips quickly.
- Exported videos are ready for social platforms.

---

## Journey 2 - Review AI Output

### Trigger

AI pipeline finishes generating clips.

### Journey

```text
Open Production
  ↓
View AI Output
  ↓
Review Clip
  ↓
Approve / Reject / Regenerate
  ↓
Export Approved Clips
```

### Review Actions

- Approve clip
- Reject clip
- Regenerate hook
- Regenerate subtitle
- Regenerate B-roll plan
- Regenerate whole clip
- Edit small text details

### Non-goal

This journey is not a full manual timeline editing workflow.

---

## Journey 3 - Choose Or Reuse A Style

### Trigger

User starts a production or reviews output.

### Journey

```text
Choose Style
  ↓
AI Applies Style Rules
  ↓
Review Styled Clips
  ↓
Reuse Style For Future Productions
```

### Style Controls

- Subtitle behavior
- Motion
- Zoom
- B-roll
- Sound FX
- Music
- CTA
- Pacing

---

## Journey 4 - Production Recovery

### Trigger

Upload, AI processing, render, or export fails.

### Journey

```text
Failure Detected
  ↓
Show Clear Status
  ↓
Retry Step
  ↓
Resume Production
```

### Requirements

- Failure must not destroy the production.
- User should know which step failed.
- Retry should resume from the failed stage when possible.

---

## MVP Journey Priority

1. Produce Short Videos From One Source Video
2. Review AI Output
3. Choose Or Reuse A Style
4. Production Recovery

Batch production, auto-publish, scheduling, analytics, and team workflows are later epics.
