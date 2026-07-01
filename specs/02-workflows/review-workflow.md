# Review Workflow

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define how users review AI-generated output.

Review is the core human workflow. Manual editing is secondary.

---

## Workflow

```text
Open Production
  ↓
View Generated Clips
  ↓
Review Clip
  ↓
Approve / Reject / Regenerate
  ↓
Export Approved Clips
```

---

## Review Screen Must Show

- Clip preview
- AI reason for selecting the clip
- Hook
- Caption
- CTA
- Subtitle preview
- Style applied
- B-roll plan
- Music plan
- Sound FX plan
- Render status

---

## User Actions

- Approve clip
- Reject clip
- Regenerate whole clip
- Regenerate hook
- Regenerate caption
- Regenerate CTA
- Regenerate subtitles
- Regenerate style layers
- Export approved clips

---

## Clip Statuses

- pending_review
- approved
- rejected
- needs_changes
- regenerating
- rendering
- exported

---

## Success State

At least one generated clip is approved and ready for export.

---

## Non-goals

- Full manual editing workflow
- Complex timeline as the main interface
- Advanced color grading
- Manual keyframe animation
