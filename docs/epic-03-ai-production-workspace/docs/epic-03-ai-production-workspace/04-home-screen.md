# Home Screen

Status: Draft
Owner: Ho Quan
Version: 0.1
Last Updated: 2026-07-01
Related Epic: EPIC-03 AI Production Workspace
Depends On: 01-workspace-overview.md

---

## Purpose

The Home Screen is the entry point of the AI Production Workspace.

Its purpose is to help users start a new Production or continue an existing one as quickly as possible.

---

## Primary Goal

The Home Screen should answer:

```text
What can I create now?
What Productions need my attention?
What is the next useful action?
```

---

## Primary Action

The primary action is:

```text
New Production
```

This action should be visually prominent.

---

## Recommended Structure

```text
Header
  ↓
Welcome / Workspace Summary
  ↓
Primary Action: New Production
  ↓
Continue Work Section
  ↓
Recent Productions
  ↓
Optional Tips / Style Suggestions
```

---

## Continue Work Section

This section highlights Productions that need action.

Priority order:

1. Needs Review
2. Failed
3. Rendering
4. Processing
5. Draft
6. Recently Completed

---

## Recent Productions

Recent Productions should show:

- title
- status
- created date
- source type
- style if available
- next action

Example card:

```text
Podcast Episode 12
Status: Needs Review
Style: Podcast
Action: Review clips
```

---

## Empty State

If the user has no Productions:

```text
Create your first AI video production.
Upload a video and let AI generate clips, subtitles, motion, and export-ready output.
```

Primary action:

```text
Start New Production
```

---

## Loading State

When loading Home data:

- show skeleton cards
- keep New Production action visible if possible
- avoid blocking the full page unless necessary

---

## Error State

If Home data fails to load:

Show:

- friendly error message
- retry action
- link to start new Production if available

Do not show raw API errors.

---

## Metrics

The MVP Home Screen may avoid complex analytics.

Optional lightweight summary:

- Productions this month
- Total exports
- Time saved estimate

Analytics should not distract from starting or continuing work.

---

## User Actions

Home Screen actions:

| Action | Result |
|---|---|
| New Production | Opens upload/start flow |
| Continue Review | Opens Review screen |
| Retry Failed | Opens failed Production state |
| View Production | Opens Production detail |
| Export Completed | Opens Export screen |

---

## Anti-Patterns

Avoid:

- starting with admin metrics
- hiding New Production
- showing backend queue details
- requiring configuration before upload
- overwhelming first-time users

---

## Acceptance Criteria

Home Screen is complete when:

- user can start a new Production
- user can resume existing work
- Productions needing attention are prioritized
- empty state is useful
- loading and error states are defined

---

## Cross References

Related documents:

- 01-workspace-overview.md
- 02-navigation.md
- 03-layout.md
- 05-production-list.md
- specs/01-product/user-journeys.md
- specs/02-workflows/upload-workflow.md
