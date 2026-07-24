# App Router Audit — Sprint 16.10.2 Workspace Foundation Recovery

Date: 2026-07-23

## Root cause

Two prior refactor sprints applied incompatible strategies to the same tree without either completing:

- **16.10.2 Workspace Foundation** — add `/workspace` and `/editor/[productionId]` at plain paths, keep every legacy route (`review`, `upload`, `export`, `productions`, `ai-queue`, `styles`) fully intact at plain paths.
- **16.10.2 App Router Rebuild** — move canonical routes into route groups (`(product)/workspace`, `(editor)/editor/[productionId]`), replace every legacy page with a redirect stub under `(legacy)/*`.

The result on disk was a hybrid: legacy pages deleted from their plain paths but only replaced by redirect stubs in `(legacy)/`, a duplicate `/workspace` route (`app/workspace` and `app/(product)/workspace` both resolve to `/workspace`), an empty stale `(editor)/editor/[productionId]/` directory, and a regression script pointing at a route-group path that was never fully created. `npm run build` fails immediately on the duplicate `/workspace` route.

## Inventory: `frontend/src/app` (as found)

| Path | Kind | State |
|---|---|---|
| `layout.tsx` | root layout | unchanged |
| `page.tsx` | root page | modified — `redirect("/workspace")` |
| `globals.css` | styles | modified — dark theme tokens + geist font var |
| `settings/page.tsx` | route | unchanged, preserved |
| `workspace/page.tsx`, `workspace/loading.tsx` | route (plain) | new, renders `WorkspaceHome` from `@/features/workspace-v2` |
| `(product)/workspace/page.tsx`, `loading.tsx` | route group | new, duplicate of `workspace/` — **build-breaking collision** |
| `editor/[productionId]/page.tsx`, `loading.tsx`, `not-found.tsx` | route (plain) | new, renders `ReviewWorkspace` from `@/features/review` |
| `(editor)/editor/[productionId]/` | route group | empty directory, stale leftover, no files |
| `(legacy)/ai-queue/page.tsx` | route group | redirect stub → `/workspace?view=jobs` |
| `(legacy)/export/page.tsx` | route group | redirect stub → `/editor/:id?panel=export` or `/workspace?view=exports` |
| `(legacy)/productions/page.tsx` | route group | redirect stub → `/workspace` |
| `(legacy)/review/page.tsx` | route group | redirect stub → `/editor/:id` |
| `(legacy)/styles/page.tsx` | route group | redirect stub → `/workspace?view=templates` |
| `(legacy)/upload/page.tsx` | route group | redirect stub → `/workspace?intent=new` |
| `ai-queue/page.tsx`, `export/page.tsx`, `productions/page.tsx`, `review/page.tsx`, `styles/page.tsx`, `upload/page.tsx` | route (plain) | **deleted from working tree** (tracked in git as `D`) — full original content still recoverable via `git show HEAD:...` or `.sprint-backups/16.10.2-20260723-150905/` |

No `loading.tsx`/dynamic segment beyond the above; no other route groups present.

## Decision (this recovery sprint)

Per the sprint brief: no route groups, no redirects for legacy routes, no deletions. Restore all six legacy routes to plain paths with their full original content (recovered from `git show HEAD`), keep `workspace/` and `editor/[productionId]/` at their plain paths (already correct), delete the `(legacy)`, `(product)`, and empty `(editor)` directories, and reconcile the regression scripts to assert existence only (no `legacy_review_removed` / `route_migrated` / `redirect_exists` style assertions).

See `specs/refactor/workspace-foundation-report.md` for the completed changes and final status.
