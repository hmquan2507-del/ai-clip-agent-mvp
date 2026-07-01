# Navigation

Status: Draft
Owner: Ho Quan
Version: 0.1
Last Updated: 2026-07-01
Related Epic: EPIC-03 AI Production Workspace
Depends On: 01-workspace-overview.md

---

## Purpose

This document defines navigation for the AI Production Workspace.

Navigation should support the primary production flow and help users move between Home, Upload, AI Queue, Review, and Export without confusion.

---

## Navigation Principle

Navigation must prioritize the Production workflow over admin-style sections.

The user should not feel like they are managing a complex backend system.

The user should feel guided through a video production process.

---

## Primary Navigation Flow

```text
Home
  ↓
Production
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

## Recommended Top-Level Navigation

Initial workspace navigation:

| Item | Purpose |
|---|---|
| Home | Start or resume production work |
| Productions | View all Productions |
| Styles | Manage reusable production styles |
| Settings | Workspace/account configuration |

The first MVP may hide Styles and Settings if not implemented yet.

---

## Production-Level Navigation

Inside a Production, navigation should be step-based:

```text
Overview → Upload → AI Queue → Review → Export
```

Each step should show:

- current status
- completion state
- next recommended action
- unavailable states when blocked

---

## Navigation States

Navigation items may have these states:

| State | Meaning |
|---|---|
| Available | User can enter the section |
| Active | User is currently in this section |
| Completed | Section has been completed |
| Blocked | Section cannot be accessed yet |
| Error | Section contains a blocking issue |

---

## Sidebar Behavior

A sidebar may be used on desktop layouts.

The sidebar should include:

- product logo/name
- Home
- Productions
- optional Styles
- optional Settings
- user/workspace switcher if needed later

The sidebar should not contain low-level admin entities such as jobs, logs, database records, or worker nodes.

---

## Header Behavior

The header should include:

- current workspace title
- primary action button
- current Production name if applicable
- user/account menu

The primary action should usually be:

- New Production
- Continue Upload
- Review Output
- Export

depending on context.

---

## Breadcrumbs

Breadcrumbs are optional for MVP.

If used, they should follow:

```text
Home / Productions / Production Name / Review
```

Breadcrumbs should help orientation but must not replace the primary step flow.

---

## Mobile Navigation

On mobile or narrow screens:

- sidebar collapses
- top navigation becomes compact
- production steps may become a horizontal stepper
- primary action remains visible

Mobile should support monitoring and review basics, but heavy review may be optimized for desktop first.

---

## Navigation Anti-Patterns

Avoid:

- admin dashboard navigation as the main product surface
- exposing backend queue as a standalone technical page
- showing raw worker logs in primary navigation
- mixing settings and production actions
- forcing users to navigate through unrelated pages before upload

---

## Acceptance Criteria

Navigation is complete when:

- users can identify the current step
- users can move between allowed steps
- blocked steps are clearly explained
- primary action is visible
- navigation supports the Home → Upload → AI Queue → Review → Export flow

---

## Cross References

Related documents:

- 01-workspace-overview.md
- 03-layout.md
- 04-home-screen.md
- 05-production-list.md
- 06-routing.md
- specs/00-governance/product-principles.md
