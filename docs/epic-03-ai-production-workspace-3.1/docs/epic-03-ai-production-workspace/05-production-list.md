# Production List

Status: Draft
Owner: Ho Quan
Version: 0.1
Last Updated: 2026-07-01
Related Epic: EPIC-03 AI Production Workspace
Depends On: 01-workspace-overview.md

---

## Purpose

The Production List allows users to view, filter, and continue their Productions.

It should help users quickly identify what needs action.

---

## Primary Goal

The Production List should answer:

```text
What Productions exist?
What state is each Production in?
What should I do next?
```

---

## List Item Data

Each Production item should display:

- Production title
- status
- thumbnail if available
- created date
- updated date
- selected style if available
- source duration if available
- next action

---

## Recommended Card Layout

```text
[Thumbnail]
Title
Status badge
Style / Source duration
Updated date
Next action button
```

Cards are preferred for MVP because they are more understandable than dense tables.

---

## Status Badges

Recommended badges:

| Status | Label |
|---|---|
| Draft | Draft |
| Uploading | Uploading |
| Uploaded | Ready for AI |
| Processing | Processing |
| Needs Review | Needs Review |
| Approved | Approved |
| Rendering | Rendering |
| Completed | Completed |
| Failed | Failed |

---

## Next Actions

Each Production should expose one primary next action.

| Status | Next Action |
|---|---|
| Draft | Continue Upload |
| Uploading | View Upload |
| Uploaded | Start AI |
| Processing | View Progress |
| Needs Review | Review |
| Approved | Export |
| Rendering | View Render |
| Completed | Download |
| Failed | Retry |

---

## Filters

MVP filters:

- All
- Needs Review
- Processing
- Completed
- Failed

Advanced filters can be added later.

---

## Sorting

Default sorting:

```text
Updated recently first
```

Optional future sorting:

- created date
- status
- style
- duration

---

## Empty State

If there are no Productions:

```text
No Productions yet.
Start by uploading a video and AI will generate an editable production output.
```

Primary action:

```text
New Production
```

---

## Empty Filter State

If a filter has no results:

```text
No Productions match this filter.
```

Secondary action:

```text
View all Productions
```

---

## Error State

If the list fails to load:

- show retry button
- preserve filters if possible
- do not clear user context unnecessarily

---

## Pagination

MVP may use simple pagination or infinite loading.

Recommended MVP approach:

```text
Load first 20 Productions
Load more on demand
```

---

## User Actions

| Action | Result |
|---|---|
| Open Production | Opens Production workspace |
| New Production | Starts upload flow |
| Filter Status | Filters list |
| Retry Failed | Re-runs failed step if allowed |
| Download Export | Downloads completed export |

---

## Anti-Patterns

Avoid:

- showing raw database IDs
- exposing worker/job internals
- making users choose technical queue steps
- hiding failed Productions
- presenting list as an admin audit table first

---

## Acceptance Criteria

Production List is complete when:

- all Productions can be viewed
- status is clear
- next action is clear
- filters exist for important states
- empty, loading, and error states are defined

---

## Cross References

Related documents:

- 01-workspace-overview.md
- 03-layout.md
- 04-home-screen.md
- 06-routing.md
- specs/06-data/entities.md
- specs/06-data/state-machine.md
