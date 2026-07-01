# Layout

Status: Draft
Owner: Ho Quan
Version: 0.1
Last Updated: 2026-07-01
Related Epic: EPIC-03 AI Production Workspace
Depends On: 01-workspace-overview.md, 02-navigation.md

---

## Purpose

This document defines the layout structure for the AI Production Workspace.

The layout should make the production flow obvious, reduce cognitive load, and keep the user focused on the next useful action.

---

## Layout Principle

The layout should support review and decision-making, not manual timeline editing.

Every screen should answer:

```text
What is the Production status?
What should the user do next?
What did AI produce?
What can be approved, regenerated, or exported?
```

---

## Desktop Layout

Recommended desktop structure:

```text
┌───────────────────────────────────────────────┐
│ Header                                        │
├───────────────┬───────────────────────────────┤
│ Sidebar       │ Main Content                  │
│               │                               │
│ Navigation    │ Step Header                   │
│               │ Workspace Content             │
│               │                               │
└───────────────┴───────────────────────────────┘
```

---

## Main Content Structure

Each main screen should follow:

```text
Screen Title
Description / Context
Primary Action
Main Content
Secondary Actions
Status / Feedback
```

---

## Production Step Layout

Inside a Production:

```text
Production Header
  ↓
Step Indicator
  ↓
Current Step Content
  ↓
Next Action
```

Example:

```text
Production: Podcast Clip #12
Status: Needs Review

[Upload ✓] [AI Queue ✓] [Review •] [Export]

Review generated clips
[Approve] [Regenerate]
```

---

## Content Density

The workspace should avoid dense admin-style tables as the default experience.

Use cards for:

- recent Productions
- production status
- next actions
- generated outputs
- AI queue progress

Tables may be used for advanced views later.

---

## Empty States

Every major screen must define an empty state.

Examples:

- no Productions yet
- no uploads yet
- no AI output yet
- no exports yet

Empty states should guide users toward the next action.

---

## Loading States

Loading states should be explicit and reassuring.

Examples:

- uploading file
- analyzing video
- detecting highlights
- rendering export

Avoid generic spinners without context.

---

## Error States

Error states should include:

- what failed
- why it likely failed
- what the user can do
- retry option where possible

Do not expose raw backend errors as primary UI messages.

---

## Responsive Layout

Desktop is the primary target for MVP.

Responsive behavior:

| Screen Size | Behavior |
|---|---|
| Desktop | Sidebar + header + main content |
| Tablet | Collapsible sidebar |
| Mobile | Compact navigation, stacked content |

---

## Layout Anti-Patterns

Avoid:

- timeline-first layout
- admin dashboard grid as the main screen
- showing too many metrics before user has Productions
- hiding the primary action
- mixing review and export controls before review is complete

---

## Acceptance Criteria

Layout is complete when:

- each screen has a clear primary action
- Production status is visible
- step progression is understandable
- layout supports all required states
- desktop and responsive behavior are defined

---

## Cross References

Related documents:

- 01-workspace-overview.md
- 02-navigation.md
- 04-home-screen.md
- 05-production-list.md
- specs/04-frontend/design-system.md
- specs/04-frontend/workspace.md
