# Sprint 16.10.2 — App Router Rebuild

## Goal
Replace the old page-per-feature navigation with a workspace/editor product surface while preserving backend and editor runtimes.

## Canonical routes
- `/workspace`
- `/editor/[productionId]`
- `/settings`

## Legacy redirects
- `/` → `/workspace`
- `/review?production_id=:id` → `/editor/:id`
- `/upload` → `/workspace?intent=new`
- `/productions` → `/workspace`
- `/ai-queue` → `/workspace?view=jobs`
- `/styles` → `/workspace?view=templates`
- `/export?production_id=:id` → `/editor/:id?panel=export`

## Runtime boundary
`ReviewWorkspace` remains the editor runtime integration boundary. No playback, timeline, history, keyboard, AI, API, or backend runtime is moved or rewritten in this sprint.
