# Workspace Layout

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define the AI Production Workspace layout.

The workspace is review-first, not timeline-first.

---

## Main Workspace Flow

```text
Production Summary
  ↓
AI Output
  ↓
Review Panel
  ↓
Regeneration / Approval
  ↓
Export
```

---

## Review Workspace Layout

Recommended layout:

```text
Header: Production title, status, export action

Left: Generated clip list
Center: Clip preview
Right: AI edit plan and review actions
Bottom: Optional compact timeline/steps
```

---

## Required Panels

### Clip List

Shows generated clips and statuses.

### Preview

Shows rendered or previewable output.

### AI Plan

Shows:

- Why AI selected the clip
- Hook
- Caption
- CTA
- Subtitle plan
- B-roll plan
- Music plan
- Sound FX plan

### Review Actions

Actions:

- Approve
- Reject
- Regenerate
- Export

---

## Timeline Role

Timeline is optional and secondary.

It can help explain the AI edit plan, but it should not be the main editing surface.

---

## Empty State

If no production exists:

- Show Start Production
- Explain upload flow briefly
- Avoid showing an empty admin dashboard

---

## Loading State

When AI is processing:

- Show pipeline stage
- Show current progress
- Show estimated next step when possible

---

## Error State

Show:

- Failed stage
- Reason when available
- Retry action
- Safe return path
