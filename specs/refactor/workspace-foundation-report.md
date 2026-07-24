# Sprint 16.10.2 — Workspace Foundation Recovery Report

Date: 2026-07-23

See `specs/refactor/app-router-audit.md` for the pre-recovery inventory and root-cause analysis.

## Files restored (git-tracked, brought back to HEAD content at plain paths)

- `frontend/src/app/ai-queue/page.tsx`
- `frontend/src/app/export/page.tsx`
- `frontend/src/app/productions/page.tsx`
- `frontend/src/app/review/page.tsx`
- `frontend/src/app/styles/page.tsx`
- `frontend/src/app/upload/page.tsx`
- `frontend/src/app/page.tsx` (root Home dashboard — was a `redirect("/workspace")` stub, restored to the original full page so `/` renders directly with a 200, no redirect)
- `frontend/src/features/review/shell/editor-topbar.tsx` (Review Runtime file; back-link had been repointed to `/workspace` — reverted to original `/productions` back-link since Review Runtime is out of scope for this sprint)

## Directories removed

- `frontend/src/app/(legacy)/` — six redirect-stub pages that had replaced the real legacy pages
- `frontend/src/app/(product)/` — duplicate `/workspace` route, the direct cause of the `next build` failure
- `frontend/src/app/(editor)/` — empty stale leftover directory, no files

No route groups remain under `frontend/src/app`.

## Files created (kept from the Workspace Foundation attempt, already at plain paths)

- `frontend/src/app/workspace/page.tsx`, `loading.tsx` — renders `WorkspaceHome`
- `frontend/src/app/editor/[productionId]/page.tsx`, `loading.tsx`, `not-found.tsx` — renders `ReviewWorkspace` directly, no duplicated provider/timeline/runtime
- `frontend/src/features/workspace-v2/` — `WorkspaceHome` component, wired into `/workspace`

## Files modified (this recovery)

- `frontend/src/components/navigation/sidebar.tsx` — restored the original flat nav list (Home, Upload, AI Queue, Review, Export, Productions, Styles, Settings) and added a new **Workspace** entry at the top. No existing menu items were removed, per Phase 7.
- `frontend/src/features/production/production-card.tsx` — restored the card's title link to `/productions/:id` (original behavior) and added a separate **"Open in Editor"** button linking to `/editor/:id`, per Phase 6 ("only add a button, don't redirect/replace the existing route").
- `frontend/src/app/globals.css` — kept the dark-theme token change (`--background`/`--foreground`) and Geist font wiring from the Workspace Foundation attempt; this is presentational only and doesn't touch any runtime.
- `frontend/scripts/test-review-workspace-regression.cjs` — fixed a stale path reference from the abandoned route-group scheme (`src/app/(editor)/editor/[productionId]/page.tsx`, which never existed as real files) to the actual plain path `src/app/editor/[productionId]/page.tsx`.

## Files deleted

- `frontend/scripts/test-app-router-rebuild.cjs` — encoded the abandoned/incompatible strategy (route groups, redirect stubs for legacy routes, `root_redirects_to_workspace`). Directly contradicted the "no route groups, no redirects, no deletions" recovery goal and could never pass alongside `test-workspace-foundation.cjs`. Not wired into `package.json` scripts, so removing it has no effect on `npm run test:review`.

## Regression / acceptance status

| Check | Result |
|---|---|
| `npm run lint` | 78 pre-existing errors / 10 warnings, all inside `playback` runtime, `export-workspace`, and unrelated `scripts/*.cjs` files. Confirmed via `git stash` that these errors exist identically on clean `HEAD` before any refactor sprint touched the tree — pre-existing technical debt in Playback/Timeline runtime, out of scope (explicitly listed as do-not-touch). No new lint errors introduced by this recovery. |
| `npm run build` | **PASS** — 12 routes generated (`/`, `/ai-queue`, `/editor/[productionId]`, `/export`, `/productions`, `/review`, `/settings`, `/styles`, `/upload`, `/workspace`, plus `/_not-found`), no route collisions. |
| `npm run test:review` | **PASS** — all `Review Workspace Integration & Regression` checks green, including `route_accepts_production_id`. |
| `node scripts/test-workspace-foundation.cjs` | **PASS** — workspace/editor routes exist, all legacy pages preserved, editor reuses `ReviewWorkspace`, nav promotes workspace, production cards open the editor. |
| `npx tsc --noEmit` | **PASS**, no errors. |
| `npm run dev` + manual route check | **PASS** — `/`, `/workspace`, `/review`, `/upload`, `/export`, `/productions`, `/settings`, `/styles`, `/ai-queue`, `/editor/:id` all return `200`. No 404, 500, or redirect loops. |

## Remaining technical debt (not fixed — out of scope for this recovery)

- `frontend/src/features/workspace-shell/` is an unused, fully-built alternate workspace implementation (`WorkspaceShell`/`WorkspaceSidebar`/`WorkspaceProjectCard`) left over from the first Workspace Foundation attempt before it was superseded by `workspace-v2`. It compiles cleanly and isn't imported anywhere under `src/app`, so it doesn't affect build/routing, but it's dead code that a future sprint should either wire in or delete.
- The 78 pre-existing lint errors in Playback/Timeline runtime and `export-workspace` (e.g. `setState` inside effects, `any` types, `prefer-const`) predate all three refactor sprints and are unrelated to App Router structure — flagged here for a future, explicitly-scoped runtime cleanup sprint, since fixing them here would mean touching prohibited runtime files.
- `.sprint-backups/16.10.1-*`, `.sprint-backups/16.10.2-*`, `.sprint-backups/16.10.2-workspace-foundation-*` at the repo root are untracked snapshot directories left by the two prior sprints' tooling. They were useful for this recovery's diffing/verification but are not part of the source tree; left untouched since deleting them wasn't requested and they're harmless (untracked, ignorable).
- `specs/audit/*` and `specs/epics/SPRINT-16.10.2-*` documents describe the two now-abandoned, mutually incompatible strategies. They're left in place as historical record; a future sprint may want to mark them superseded once workspace/editor consolidation actually proceeds past this recovery.
