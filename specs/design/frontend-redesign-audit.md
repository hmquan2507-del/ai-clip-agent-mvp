# Frontend Redesign Audit

Date: 2026-07-24
Status: Research only — no code changed as part of this document.

This audit inventories the current state of the AI Clip Agent frontend (`frontend/src`) ahead of a full visual redesign. It covers architecture, UI/UX problems, what must be preserved vs. refactored, and the runtime boundaries that cannot change.

---

## 1. Current frontend architecture

### 1.1 App Router surface (`frontend/src/app/`)

```
app/
  layout.tsx            root layout — Geist fonts only, no shared nav/shell
  page.tsx               →  "/"                 DashboardShell + hero/stats/production list
  workspace/             →  "/workspace"        DashboardShell + WorkspaceHome (features/workspace-v2)
  editor/[productionId]/ →  "/editor/:id"        DesktopEditorRuntimeAdapter (the new Desktop Editor)
  review/                →  "/review"            ReviewWorkspace (legacy full-page editor)
  upload/                →  "/upload"            DashboardShell + real (but simulated) upload flow
  export/                →  "/export"            ExportWorkspacePage (real runtime, plain shell)
  productions/           →  "/productions"       DashboardShell + static hard-coded list (placeholder)
  ai-queue/               →  "/ai-queue"          DashboardShell + static hard-coded stage list (placeholder)
  styles/                 →  "/styles"            DashboardShell + static hard-coded style cards (placeholder)
  settings/               →  "/settings"          DashboardShell + literal "Configuration placeholder" cards
```

No root-level shell wraps these — every page independently chooses `DashboardShell` (7 of 10 routes), a bare `<main>` (`/review`, `/export`, `/editor/:id`), or nothing. There is exactly one CSS file (`globals.css`) and no CSS Modules/CSS-in-JS anywhere.

### 1.2 The three parallel "product eras" living in this codebase today

1. **Legacy dashboard era** (`/`, `/upload`, `/ai-queue`, `/productions`, `/styles`, `/settings`, plus `/workspace` via `WorkspaceHome`): `DashboardShell` + `components/navigation/sidebar.tsx` + `components/ui/*` primitives. Raw Tailwind slate/violet palette, no CSS variables, `rounded-xl`/`rounded-3xl` radius inconsistency. Four of these seven pages are static placeholders with hard-coded arrays and non-functional buttons.
2. **Review era** (`/review`): a fully-built, CSS-variable-driven (`--review-*`) full-page timeline editor — `ReviewWorkspace` → `ReviewRuntimeWorkspace` → `ReviewEditorShell` (topbar/rail/preview/inspector/timeline/AI-command-bar). This is the most mature runtime in the app and owns real drag/trim/selection/history/clipboard/keyboard behavior.
3. **Desktop Editor era** (`/editor/[productionId]`, current focus of all recent sprints): `DesktopEditorRuntimeAdapter` → `DesktopEditorShell` → a resizable/collapsible CSS-grid docking layout (`--desktop-editor-*` tokens) that **reuses** Review's runtime pieces (`ReviewPreviewStage`, `ReviewTimelinePanel`, `ReviewAICommandBar`) inside new chrome (header, tool rail, asset panel, inspector with Properties/AI Copilot/Decision tabs, AI Timeline overlay, status bar). A separate `AiTimeline` feature (own `--ai-timeline-*` tokens) sits synchronized above the real timeline via a DOM-observation bridge (`TimelineViewportContext`), and an `AiDecisionActions` feature layers decision lifecycle (accept/reject/regenerate/pin/etc.) on top, all currently running with no backend adapter ("Pending Runtime" everywhere).

Three theme scopes exist side by side (`--review-*`, `--desktop-editor-*`, `--ai-timeline-*`), reusing largely the same hex values under different variable prefixes, plus a fourth, un-tokenized visual language (`components/ui/*`) for everything not yet migrated to Desktop Editor.

### 1.3 Data flow (already correct, must be preserved)

```
ReviewWorkspaceProvider (session runtime, revision, playhead, selection, history, clipboard)
  └─ buildReviewEditorViewModel(state)  — pure, exported adapter fn
       └─ ReviewEditorViewModel (header/preview/timeline/inspector view slices)
            ├─ consumed by ReviewEditorShell (legacy /review page)
            └─ consumed by DesktopEditorRuntimeAdapter (mirrors the same wiring for /editor/:id)
                 ├─ ReviewPreviewStage, ReviewTimelinePanel, ReviewAICommandBar (reused, unmodified)
                 ├─ AiTimeline (own mock decision data + TimelineViewportContext sync)
                 └─ AiDecisionActionProvider (own lifecycle state, no backend adapter yet)
```

Two independent runtime instances exist for `/review` and `/editor/:id` — they are **not** the same live session; `DesktopEditorRuntimeAdapter` establishes its own `ReviewWorkspaceProvider`. This is intentional (documented in `specs/epics/16.10.2-desktop-editor-foundation.md`) but is worth knowing for the redesign: the two routes cannot share in-memory state today, only the same runtime *code*.

### 1.4 No design/component library

No Radix, shadcn, MUI, Chakra, or Headless UI. All primitives are hand-rolled (`components/ui/*`, `features/review/design-system/*`). Styling is Tailwind v4 (no `tailwind.config.*` — tokens live in `globals.css`'s `@theme inline` block) plus CSS custom properties. No Storybook, no visual regression tooling, no existing screenshots.

---

## 2. Current UI/UX problems

Ranked roughly by redesign impact:

1. **Three token systems, one visual intent.** `--review-*`, `--desktop-editor-*`, `--ai-timeline-*` duplicate the same colors (`#7c5cff` accent almost everywhere except AI Timeline's `#a855f7`) under different names, with different radii (14px/12px/10px panel radius) and inconsistent surface darkness. A visitor moving between `/review` and `/editor/:id` sees two subtly different "same" dark themes.
2. **A fourth, un-tokenized visual language for everything else.** `components/ui/*` and the seven `DashboardShell`-based pages use literal Tailwind slate/violet, not CSS variables — they cannot pick up a token-system-wide change and visually clash with the editor surfaces today (different radius scale, different accent hue treatment, no shared elevation/shadow language).
3. **Four placeholder pages presented as if real.** `/productions`, `/ai-queue`, `/styles`, `/settings` are static, hard-coded, non-functional mockups wearing the same chrome as real pages — a user cannot tell they're inert until clicking.
4. **Two competing "workspace" implementations, one dead.** `features/workspace-v2` (live, wired to `/workspace`) and `features/workspace-shell` (fully built, richer, but never imported anywhere) — genuinely orphaned code from an abandoned earlier attempt.
5. **Two competing "production card" designs** (`ProductionCard` in `features/production`, `WorkspaceProjectCard` in the dead `workspace-shell`) with different visual maturity.
6. **The legacy dashboard nav (`Sidebar`) still lists 9 routes flatly**, including two that are pure placeholders and one (`/`) that duplicates what `/workspace` already does — the IA doesn't yet reflect "Workspace is canonical home" despite that being stated intent in `workspace-v2`.
7. **Every non-Desktop-Editor surface is a SaaS-dashboard visual language** (hero banners, stat-card grids, sidebar nav) — this is explicitly the wrong product metaphor per this redesign's brief ("not a SaaS dashboard, not a generic AI application"). Only `/editor/:id` currently reads as a professional desktop tool.
8. **Upload, Export, and the Editor are three visually disconnected experiences** with no shared chrome or transition — a user's mental model of "one continuous production pipeline" isn't supported by the UI today.
9. **No accessibility parity between theme scopes.** The `prefers-reduced-motion` override only targets `.review-editor-theme` — `.desktop-editor-theme`/`.ai-timeline-theme` animations (pulse states, etc.) don't respect it.
10. **Inconsistent radius scale everywhere**: buttons 12px, cards 24px, review panels 14px, desktop-editor panels 12px, ai-timeline 10px — no single scale.

---

## 3. Components that should be preserved

These are correct, working, and must not be forked, rewritten, or have their contracts changed:

| Component/module | Why preserve |
|---|---|
| `ReviewWorkspaceProvider`, `useReviewWorkspaceState`, `useReviewWorkspaceActions` (`features/review/react`, `features/review/state`) | The single source of truth for session/timeline/selection/history/clipboard/AI-suggestion state. |
| `buildReviewEditorViewModel` (`features/review/integration/adapters.ts`) | The one pure function translating runtime state → view model; both `/review` and `/editor/:id` depend on its exact shape. |
| `ReviewPreviewStage`, `ReviewTimelinePanel`, `ReviewAICommandBar` (`features/review/shell`) | The actual preview rendering, timeline track/clip rendering with drag/trim/snap/keyboard wiring, and AI command submission boundary. These are reused, not modified, by the Desktop Editor. |
| `useReviewRuntimeClipDrag`, `useReviewRuntimeClipTrim`, `useReviewRuntimeKeyboardEditing` (`features/review/integration`) | Drag/Trim/Keyboard Runtime hooks — copied-by-reference into `DesktopEditorRuntimeAdapter`, must keep the same call contract. |
| `useReviewTimelineViewport` (`features/review/viewport`) | Timeline Runtime's own internal zoom/scroll — deliberately NOT touched; `TimelineViewportContext` only observes its DOM output. |
| `DesktopEditorRuntimeAdapter` / `runtime-adapter.tsx` (`features/desktop-editor`) | Mirrors `runtime-workspace.tsx`'s wiring pattern faithfully; any redesign must keep feeding it the same view-model shape. |
| `TimelineViewportContext` (`features/ai-timeline/context`) | The DOM-observation bridge that lets AI Timeline share scroll/zoom/playhead/selection with the real timeline without editing it. |
| `AiDecisionActionProvider`/`useAiDecisionActions` (`features/ai-decision-actions`) | Decision lifecycle state machine + the explicit "Pending Runtime" honesty pattern — must not be replaced with a faked backend. |
| `ExportWorkspacePage`'s runtime layer (`features/export-workspace/runtime/*`) | Real immutable Review→Export handoff-contract reading, a real (if currently unconnected) runtime/api-client layer. |
| `features/upload/*` components (`UploadDropzone`, `UploadQueue`, `UploadProgress`, `ProductionMetadataForm`) | Real, well-decomposed state/validation logic — only the simulated `setTimeout` backing and visual chrome need to change, not the component contracts. |
| `lib/mock-productions.ts` shape (`Production`, `ProductionStatus`, `statusLabel`/`statusTone`) | The type contract multiple surfaces depend on — can gain fields, shouldn't be replaced wholesale until a real API exists. |

---

## 4. Components that should be refactored (or retired)

| Component/module | Disposition | Why |
|---|---|---|
| `components/ui/*` (Button, Badge, Card, Input, Textarea, Progress, EmptyState, LoadingState, SectionHeader) | **Refactor onto the new unified token system.** | Currently hardcoded Tailwind colors with no theme awareness; inconsistent radii vs. everything else. These primitives are still useful shapes (Button/Badge/Card concepts are sound) — port them to CSS-variable-driven classes matching the new design system, don't reinvent from scratch. |
| `components/layout/dashboard-shell.tsx` + `components/navigation/sidebar.tsx` | **Refactor into the new Workspace shell.** | Simple title-bar + flat 9-item sidebar doesn't reflect "Workspace is home" IA; needs replacing with a shell consistent with the new design system and pared-down nav (see master plan §15). |
| `/productions`, `/ai-queue`, `/styles`, `/settings` pages | **Rebuild for real, on the new visual system** (not necessarily this redesign's first phase — see migration strategy) — currently non-functional placeholders that actively misrepresent the product's maturity. |
| `features/workspace-shell/*` | **Retire (delete) once `/workspace` is redesigned** — confirmed zero import sites; keeping it around is only useful as a reference for its (better) visual ideas (rich header, `WorkspaceProjectCard` thumbnail treatment), which should be cherry-picked into the new Workspace design, then the module deleted. Do not delete until the new Workspace has shipped and been verified (per migration constraints). |
| `features/workspace-v2/workspace-home.tsx` | **Refactor** — currently duplicates card markup rather than reusing `ProductionCard`, and depends on `DashboardShell`; needs to become the actual, redesigned `/workspace` page. |
| `features/production/production-card.tsx` | **Refactor onto new tokens** — keep the component, restyle it; reconcile with `WorkspaceProjectCard`'s richer thumbnail treatment (pick one final design, retire the other). |
| `/upload`, `/export` page chrome (not their runtime) | **Refactor visual chrome only** — real logic underneath is sound (see §3), but presentation predates the new token system. |
| `/` (root page) | **Likely retire as a distinct page** — its content (hero, stats, production list) is redundant with `/workspace`, which the codebase itself already documents as "the canonical product home." Root should probably just redirect or become an even lighter landing point — a call the master plan addresses explicitly (§15). |

---

## 5. Runtime boundaries that must not change

These match the constraints already enforced across every Desktop Editor sprint to date, and the redesign must continue to respect them exactly:

- **Timeline Runtime** (`features/review/shell/timeline.tsx`, `features/review/viewport/*`) — track/clip rendering, zoom/scroll internals. Redesign may restyle `ReviewTimelinePanel`'s CSS classes only if changes stay presentational and don't touch its prop contract or internal state; if the master plan calls for lane-height/toolbar changes that require editing this file's logic, that must be called out as an explicit, separately-approved exception — not a silent side effect of "redesign."
- **Playback Runtime** (`features/playback/*`, `ReviewPreviewStage` internals) — preview rendering/sync.
- **History Runtime** (`features/review/state` undo/redo stack, `TimelineHistory*` in `features/playback`).
- **Selection Runtime** (`snapshot.selection`, `ReviewTimelineView.tracks[].clips[].selected`, `clipboard.selectedClipIds`).
- **Drag Runtime** / **Trim Runtime** (`use-runtime-clip-drag.ts`, `use-runtime-clip-trim.ts`, `features/review/drag`, `features/review/trim`).
- **Keyboard Runtime** (`use-runtime-keyboard-editing.ts`, `features/review/keyboard`).
- **Clipboard Runtime** (copy/cut/paste/history inside `ReviewWorkspaceActions`).
- **AI Decision Runtime** (`features/ai-decision-actions/context.tsx`) — lifecycle states, typed action contract, "Pending Runtime" honesty pattern.
- **Backend, workers, database, API paths** — untouched; no direct `fetch()` from presentation components (enforced today by regression scripts and must remain enforced).
- **The natural-language AI command submission boundary** (`ReviewAICommandBar` → `onAICommandSubmit` → `actions.submitAICommand`) — must remain the only path a command reaches the runtime through.

All of the above are exercised by the existing regression suite (`npm run test:review`, `test-ai-decision-action-runtime.cjs`, `test-desktop-editor-ui-refinement.cjs`, `test-workspace-foundation.cjs`) — any redesign phase must keep these green, and the migration/regression strategy (master plan §22–23) should extend this pattern to new surfaces rather than replace it.

---

## 6. Reference data collected during this audit

Full raw findings (component-by-component code snippets, exact CSS token values, route-by-route maturity ranking) are preserved in this session's research and summarized inline throughout this document and the design-system/master-plan documents. Key numbers worth carrying forward:

- 3 CSS theme scopes exist today: `.review-editor-theme`, `.desktop-editor-theme`, `.ai-timeline-theme` — confirmed exhaustive via grep.
- 1 CSS file total in the app (`globals.css`, 352 lines) — no CSS Modules, no styled-components, no inline `<style>` tags anywhere.
- No Storybook/Chromatic/visual-regression tooling exists — any redesign verification will be manual + the existing `.cjs` string-based regression scripts + build/typecheck, consistent with this codebase's established testing idiom.
- Radius values in use today: 8px/10px/12px/14px/24px, all for conceptually similar "panel/card" surfaces — the design system should collapse this to a deliberate 2–3-step scale.
