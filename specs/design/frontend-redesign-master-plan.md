# Frontend Redesign — Implementation Master Plan

Sprint 17.1 — Frontend Audit & Design System
Date: 2026-07-25 (supersedes the 16.10.7–16.10.15 draft numbering from the prior planning pass)
Status: Planning only. Sprint 17.1 itself implements only the token foundation (see `specs/epics/17.1-frontend-audit-and-design-system.md`); no sprint below 17.2 has begun.

Companion documents: `frontend-architecture-audit.md`, `frontend-ux-visual-audit.md`, `frontend-design-direction.md`, `frontend-design-system.md`, `frontend-responsive-system.md`, `frontend-accessibility-system.md`.

## Standing constraints for every sprint below

- Preserve Timeline/Playback/History/Selection/Drag/Trim/Keyboard/Clipboard/AI-Decision-Action Runtimes and the natural-language command runtime exactly as documented in `frontend-architecture-audit.md` §5.
- No backend/database/worker/API path changes; no direct API calls from presentation components; no duplicated authoritative runtime state; no faked backend success.
- No sprint blindly rewrites a full screen — each is scoped to specific files/surfaces with an explicit exit criterion.
- Every sprint keeps `npx tsc --noEmit`, `npm run build`, `npm run test:review`, `node scripts/test-ai-decision-action-runtime.cjs`, and `node scripts/test-frontend-design-system.cjs` green, extending the regression suite with its own new script.

---

### 17.2 — Desktop Editor Shell Redesign

- **Goal:** Cut the Desktop Editor over from `--desktop-editor-*`/`--ai-timeline-*` (now alias layers, per 17.1) directly to `--ce-*` tokens and the consolidated primitives; apply "surface contrast before borders" (design direction principle 3) to the shell chrome.
- **Scope:** `features/desktop-editor/components/*`, `features/ai-timeline/components/*` class references only — no prop/behavior changes.
- **Dependencies:** 17.1 (tokens must exist and be alias-verified first).
- **Runtime boundaries:** Zero runtime files touched; visual-only diff, verifiable by confirming no changed file appears outside `components/`/`*.css`.
- **Expected files:** Every `desktop-editor`/`ai-timeline` component file (styling only), `globals.css` (remove now-redundant legacy aliases only if fully migrated).
- **Tests:** Extend `test-desktop-editor-ui-refinement.cjs` (or add `test-desktop-editor-token-cutover.cjs`) asserting `--ce-*` usage and zero remaining `--desktop-editor-*`/`--ai-timeline-*` literal references in migrated files.
- **Exit criteria:** Visually equivalent-or-better shell, all existing regression scripts green, responsive math re-verified at all 4 target widths.

### 17.3 — Preview & Playback Workspace

- **Goal:** Apply "Preview leads hierarchy" — quiet canvas chrome, idle-dim treatment for `EditorPreviewCanvas`'s own controls (not `ReviewPreviewStage`'s internals).
- **Scope:** `EditorPreviewCanvas` only.
- **Dependencies:** 17.2 (tokens live in the shell already).
- **Runtime boundaries:** Playback Runtime untouched; `ReviewPreviewStage` internals untouched — idle-dim is implemented as a sibling overlay `EditorPreviewCanvas` fully owns.
- **Expected files:** `editor-preview-canvas.tsx`, `globals.css` (canvas-specific utility if needed).
- **Tests:** New assertions in the design-system test or a dedicated `test-preview-workspace-chrome.cjs` confirming no changes to `features/review/shell/workspace-panels.tsx`.
- **Exit criteria:** Preview reads as the visual focal point at every target viewport; Fit/Zoom/fullscreen controls unchanged and still accessible.

### 17.4 — Asset Library Experience

- **Goal:** Carry forward 16.10.6.1's density work onto `--ce-*`; add real empty/loading/error states via the consolidated primitives (Design System Task 5).
- **Scope:** `editor-asset-panel.tsx`.
- **Dependencies:** 17.2.
- **Runtime boundaries:** None — mock data only, no new asset APIs, no upload runtime change (explicit constraint carried from 16.10.6.1).
- **Expected files:** `editor-asset-panel.tsx`.
- **Tests:** Extend the design-system test with Asset Panel-specific token-usage assertions.
- **Exit criteria:** Visually consistent with the rest of the shell; empty/loading states present and using shared primitives.

### 17.5 — Manual Timeline Visual System

- **Goal:** Apply as much of `frontend-design-system.md` §Task 6 "Timeline (Manual)" as is achievable **without editing `features/review/shell/timeline.tsx`** — i.e., the wrapping `EditorTimelineWorkspace` chrome only.
- **Scope:** `editor-timeline-workspace.tsx` chrome; **explicitly excludes** track lane height, in-runtime toolbar grouping, clip hover feedback, and playhead styling *inside* Timeline Runtime — these remain documented targets pending a separate, explicitly-approved runtime-boundary exception (UX audit F9).
- **Dependencies:** 17.2.
- **Runtime boundaries:** Timeline Runtime untouched — this is the sprint most likely to surface the "can't finish the job without touching the runtime" tension; if the product owner wants the full timeline visual system implemented, that requires a distinct, explicitly-scoped follow-up sprint with its own runtime-touch approval, not silently folded in here.
- **Expected files:** `editor-timeline-workspace.tsx` only.
- **Tests:** Assert `features/review/shell/timeline.tsx` is byte-identical before/after (explicit regression guard).
- **Exit criteria:** Wrapping chrome matches the design system; a clearly-written "Known Limitation" entry documents exactly what remains blocked on the runtime boundary.

### 17.6 — AI Timeline Experience

- **Goal:** Fix UX audit F5 (track density/spacing) and F6 (compact-tier lifecycle legibility); cut over to `--ce-decision-*` tokens; add keyboard-triggered tooltips (Accessibility System reference implementation) and Escape-to-close on the context menu.
- **Scope:** `features/ai-timeline/components/*`.
- **Dependencies:** 17.2.
- **Runtime boundaries:** `TimelineViewportContext`'s DOM-observation mechanism unchanged; decision lifecycle logic (`ai-decision-actions/context.tsx`) unchanged; no new actions.
- **Expected files:** `ai-block.tsx`, `ai-marker.tsx`, `ai-track.tsx`, `ai-track-header.tsx`, `ai-tooltip.tsx`, `ai-timeline.tsx`.
- **Tests:** Extend `test-ai-decision-action-runtime.cjs`'s companion checks or add `test-ai-timeline-visual-system.cjs`.
- **Exit criteria:** Every lifecycle state legible at every width tier; track density improved; a11y gaps from `frontend-accessibility-system.md` closed for this surface.

### 17.7 — Contextual Inspector

- **Goal:** Fix UX audit F7 — one consistent section-spacing/empty-state rhythm across Properties/AI Copilot/Decision; adopt canonical `role="tablist"` semantics.
- **Scope:** `editor-inspector.tsx`, `ai-decision-actions/components/decision-inspector.tsx` (styling only — do not merge their data/runtime, per the explicit "deeper Inspector architecture is a later concern" instruction carried from 16.10.6.1).
- **Dependencies:** 17.2, 17.6 (decision tokens).
- **Runtime boundaries:** `useAiDecisionActions` unchanged; Properties tab remains a placeholder (no new business feature).
- **Expected files:** `editor-inspector.tsx`, `editor-ai-copilot.tsx` (spacing only), `decision-inspector.tsx` (spacing only).
- **Tests:** Assert tab semantics present; assert `useAiDecisionActions()`'s public API shape is unchanged.
- **Exit criteria:** Switching tabs feels like one system; `role="tablist"`/`aria-selected` present and correct.

### 17.8 — AI Director & Copilot

- **Goal:** Fix UX audit F8 (AI-content visual marker) and the Accessibility System's dialog-focus-trap / processing-announcement gaps.
- **Scope:** `editor-ai-copilot.tsx`, `ai-regenerate-dialog.tsx`.
- **Dependencies:** 17.2, 17.7.
- **Runtime boundaries:** `ReviewAICommandBar` (natural-language command boundary) untouched and reused verbatim; no new AI actions; no backend calls.
- **Expected files:** `editor-ai-copilot.tsx`, `ai-regenerate-dialog.tsx`.
- **Tests:** Assert `ReviewAICommandBar` import unchanged; assert dialog focus-trap behavior (structural check, e.g. presence of a focus-trap utility usage).
- **Exit criteria:** AI-authored content visually distinguishable via one restrained marker; dialogs trap focus; async actions have paired `aria-live` announcements.

### 17.9 — Projects, Upload & Processing

- **Goal:** Real restructuring (not just re-skinning) — new shared app shell (replacing `DashboardShell`/`Sidebar`), new `/workspace` (superseding both `workspace-v2` and the dead `workspace-shell`), `/productions` → real "Projects", fold `/ai-queue`'s processing-status concept into per-project state, retire `/` (redirect to `/workspace`), reconcile `ProductionCard`/`WorkspaceProjectCard` into one component. Chrome-only pass on `/upload` (real logic preserved).
- **Scope:** New `features/workspace/` (or similarly named) module; `app/page.tsx`, `app/workspace/`, `app/productions/`, `app/ai-queue/`, `app/upload/`; retirement of `features/workspace-shell/`, `features/workspace-v2/`, `components/layout/dashboard-shell.tsx`, `components/navigation/sidebar.tsx` — **only after** the new shell/pages ship and are verified (never delete-then-build).
- **Dependencies:** 17.1–17.8 (shared design system fully proven on the Editor first).
- **Runtime boundaries:** None of these surfaces touch any authoritative runtime — `lib/mock-productions.ts` shape may gain fields but isn't replaced wholesale until a real API exists.
- **Expected files:** New Workspace feature module, new shared app-shell component, updated routes, `lib/mock-productions.ts` (additive only).
- **Tests:** New `test-workspace-redesign.cjs` (route existence, no `fetch(`, shared-shell usage, old dead modules confirmed unreferenced before deletion).
- **Exit criteria:** `/workspace` is the verified canonical home; `/productions` shows real project data (even if mock-backed, honestly labeled); `/` redirects; `workspace-shell` deleted; `test-workspace-foundation.cjs` still passes (route contracts it checks remain valid) or is explicitly updated with a documented reason.

### 17.10 — Export, Settings & Styles

- **Goal:** Chrome-only redesign of `/export` (real runtime, needs visual parity with the new system); rebuild `/settings` and `/styles`→"Templates" for real (honest mock-backed content, no more literal "Configuration placeholder").
- **Scope:** `features/export-workspace/components/*` (chrome only), new `/settings` and `/styles` (Templates) implementations.
- **Dependencies:** 17.9 (shared shell must exist).
- **Runtime boundaries:** `features/export-workspace/runtime/*` untouched; Settings persistence, if any is added, must be honestly labeled as not-yet-connected (same "Pending Runtime" pattern as AI Decision Actions) rather than faked.
- **Expected files:** `export-workspace-page.tsx` (chrome), new settings/templates page implementations.
- **Tests:** `test-export-workspace-frontend-runtime.cjs`/`test-export-workspace-page-navigation.cjs` remain green unmodified in behavior; new structural checks for Settings/Templates honesty pattern.
- **Exit criteria:** No route in the app is a non-functional placeholder wearing production chrome (resolves UX audit F3 completely).

### 17.11 — Responsive, Accessibility & Polish

- **Goal:** Full-app sweep: responsive verification at all 4 target widths for every surface (not just the Editor); full WCAG contrast audit; icon-only-button `aria-label` sweep; roving-tabindex for dense toolbars; close any remaining gaps listed in `frontend-accessibility-system.md`'s summary table.
- **Scope:** App-wide, but verification/fixes only — no new features.
- **Dependencies:** 17.2–17.10 (everything must exist to be swept).
- **Runtime boundaries:** None — this is a verification and small-fix sprint.
- **Expected files:** Small, targeted fixes wherever the sweep finds a gap; no large rewrites.
- **Tests:** A comprehensive `test-frontend-accessibility-sweep.cjs` and `test-frontend-responsive-sweep.cjs`.
- **Exit criteria:** Every item in the Accessibility System's "deferred" column is closed; every route verified at all 4 target widths with no horizontal overflow.

### 17.12 — Integration & Full Regression

- **Goal:** Final integration pass across every surface touched in 17.2–17.11; confirm the entire `--ce-*` migration is complete (legacy `--review-*`/`--desktop-editor-*`/`--ai-timeline-*` alias layer can be safely removed where nothing references the old names directly); full regression run.
- **Scope:** App-wide verification, alias-layer cleanup, final documentation update.
- **Dependencies:** All prior 17.x sprints.
- **Runtime boundaries:** None — this sprint touches no runtime, only confirms none were touched across the whole program.
- **Expected files:** `globals.css` (alias-layer removal, only where verified unreferenced), updated `specs/design/*` docs marking the migration complete.
- **Tests:** Full existing suite (`npm run test:review`, `test-ai-decision-action-runtime.cjs`, `test-desktop-editor-ui-refinement.cjs`, `test-frontend-design-system.cjs`, plus every script added in 17.2–17.11) all green in one run.
- **Exit criteria:** One coherent, fully-tokenized product; zero legacy placeholder pages; zero dead code from the pre-redesign era; every acceptance criterion from Sprint 17.1 through 17.11 verified still holding.

---

## Phase dependency graph

```
17.1 (this sprint — tokens)
  └─ 17.2 (Editor shell cutover)
       ├─ 17.3 (Preview)
       ├─ 17.4 (Asset Library)
       ├─ 17.5 (Manual Timeline chrome — runtime-bounded)
       ├─ 17.6 (AI Timeline) ──┐
       └─ 17.7 (Inspector) ←───┘
              └─ 17.8 (AI Director & Copilot)
                     └─ 17.9 (Workspace/Projects/Upload — biggest phase)
                            └─ 17.10 (Export/Settings/Templates)
                                   └─ 17.11 (Responsive/A11y/Polish sweep)
                                          └─ 17.12 (Integration & Full Regression)
```
