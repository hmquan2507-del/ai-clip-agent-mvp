# Routing

Status: Draft
Owner: Ho Quan
Version: 0.1
Last Updated: 2026-07-01
Related Epic: EPIC-03 AI Production Workspace
Depends On: 01-workspace-overview.md, 02-navigation.md

---

## Purpose

This document defines routing for the AI Production Workspace.

Routes should reflect the product workflow and keep URLs understandable.

---

## Routing Principle

Routes should be based on user-facing product concepts, not backend implementation details.

Use:

```text
/productions/:productionId/review
```

Avoid:

```text
/jobs/:jobId/worker-log
```

---

## Recommended MVP Routes

| Route | Screen |
|---|---|
| / | Home |
| /productions | Production List |
| /productions/new | New Production / Upload Start |
| /productions/:productionId | Production Overview |
| /productions/:productionId/upload | Upload |
| /productions/:productionId/queue | AI Queue |
| /productions/:productionId/review | Review |
| /productions/:productionId/export | Export |
| /settings | Settings |

---

## Production Route Model

Each Production route should load the Production context first.

```text
productionId
  ↓
Production context
  ↓
Current state
  ↓
Allowed screen
```

If the route is not allowed for the current state, redirect or show a blocked state.

---

## State-Based Access

| Production State | Allowed Primary Route |
|---|---|
| Draft | /upload |
| Uploading | /upload |
| Uploaded | /queue |
| Processing | /queue |
| Needs Review | /review |
| Approved | /export |
| Rendering | /export |
| Completed | /export |
| Failed | current failed step |

---

## Redirect Rules

Recommended redirects:

| Condition | Redirect |
|---|---|
| Unknown route | / |
| Missing Production | /productions |
| Production draft opened | /productions/:id/upload |
| Processing Production opened | /productions/:id/queue |
| Needs Review opened | /productions/:id/review |
| Completed Production opened | /productions/:id/export |

---

## Route Guards

Route guards should check:

- authentication
- workspace access
- Production ownership
- Production state
- required data availability

Route guards should not contain business logic beyond access and state validation.

---

## Deep Linking

Users should be able to open direct links to:

- a Production
- Review screen
- Export screen

Deep links should restore context and load the correct Production state.

---

## Error Routes

Recommended error handling:

| Error | Behavior |
|---|---|
| 404 Production not found | Show friendly not found screen |
| 403 Unauthorized | Show access denied |
| Invalid state | Show blocked step with explanation |
| API unavailable | Show retry state |

---

## Future Routes

Future routes may include:

| Route | Purpose |
|---|---|
| /styles | Style library |
| /billing | Billing and credits |
| /analytics | Usage analytics |
| /automations | Batch and scheduling |
| /workspace/settings | Workspace settings |

These should not be added until their EPICs are active.

---

## Anti-Patterns

Avoid:

- exposing backend job routes as primary product routes
- routing users into blocked steps without explanation
- using technical IDs in visible labels
- creating routes for features not yet defined
- using dashboard-first route naming

---

## Acceptance Criteria

Routing is complete when:

- all MVP screens have routes
- routes match product concepts
- blocked states are handled
- deep links work for major screens
- invalid routes fail gracefully

---

## Cross References

Related documents:

- 01-workspace-overview.md
- 02-navigation.md
- 03-layout.md
- 05-production-list.md
- specs/06-data/state-machine.md
- specs/05-backend/api-spec.md
