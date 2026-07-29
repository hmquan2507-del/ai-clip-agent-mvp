# Frontend Architecture Audit

Sprint 17.1 — Frontend Audit & Design System
Date: 2026-07-25
Status: Audit only — no runtime code changed.

---

## 1. Route-by-route audit (`frontend/src/app/`)

| Route | Purpose | Layout | Shared shell | Feature deps | Runtime deps | Legacy status | Redesign priority | Recommendation |
|---|---|---|---|---|---|---|---|---|
| `/` | Historical home (hero, stats, production list) | `DashboardShell` | `Sidebar` | `features/production`, `features/workspace` (ActivityFeed/ContinueProductionCard), `lib/mock-productions` | none (mock data only) | Legacy, redundant with `/workspace` | Low | **Retire** — redirect to `/workspace` once Workspace covers its content (17.9) |
| `/workspace` | Stated "canonical product home" | `DashboardShell` | `Sidebar` | `features/workspace-v2` | none (mock data only) | Active but pre-redesign | High | **Redesign** (17.9) |
| `/editor/[productionId]` | The Desktop Editor — primary product surface | `DesktopEditorShell` (own docking grid) | none (self-contained) | `desktop-editor`, `ai-timeline`, `ai-decision-actions`, reuses `review` shell pieces | Timeline/Playback/History/Selection/Drag/Trim/Keyboard/Clipboard/AI-Decision Runtimes (all live) | Current-generation, most mature | **Highest** | **Redesign incrementally** (17.2–17.8) — this is the product |
| `/review` | Legacy full-page timeline editor, kept as a compatibility route | bare `<main>` (`ReviewEditorSurface`) | none | `features/review` (full stack) | Same runtimes as `/editor/:id`, via its own session instance | Legacy but fully live/functional | Low (compat only) | **Preserve as-is** — do not force onto new shell this sprint; revisit only once `/editor/:id` fully supersedes it |
| `/upload` | Media intake | `DashboardShell` | `Sidebar` | `features/upload/*` | none (simulated `setTimeout` progress, no real API) | Legacy chrome, real logic | Medium | **Redesign chrome only** (17.9) |
| `/export` | Render/export handoff from Review→Export contract | bare `<main>` | none | `features/export-workspace` | Real runtime (`api-client.ts`, `runtime.ts`) reading an immutable handoff contract | Under-styled but functionally real | Medium | **Redesign chrome only** (17.10) |
| `/productions` | Project list | `DashboardShell` | `Sidebar` | none — hard-coded 3-row array inline | none | Placeholder | Medium-High | **Rebuild as "Projects"** (17.9) |
| `/ai-queue` | AI processing status | `DashboardShell` | `Sidebar` | none — hard-coded stage list inline | none | Placeholder | Low | **Retire as standalone route** — fold "processing" into Projects/Workspace per-item state (17.9) |
| `/styles` | Style/template picker | `DashboardShell` | `Sidebar` | none — hard-coded array inline | none | Placeholder | Low-Medium | **Rebuild as "Templates"** (17.10) |
| `/settings` | App settings | `DashboardShell` | `Sidebar` | none — literal "Configuration placeholder" cards | none | Explicit placeholder | Low | **Rebuild** (17.10) |

**Root layout** (`app/layout.tsx`) is minimal: Geist Sans/Mono fonts only, no shared nav/theme wrapper — every route independently opts into `DashboardShell`, a bare `<main>`, or (for `/editor/:id`) its own fully self-contained shell. There is no root-level theme class applied in `layout.tsx`; theming happens per-feature (`.review-editor-theme`, `.desktop-editor-theme`, `.ai-timeline-theme` are applied deep in each feature's own surface component, not at the app shell).

## 2. Feature module audit

| Feature | Domain responsibility | Public exports (barrel) | Runtime ownership | UI ownership | Cross-feature deps | Duplicate responsibilities | Legacy deps | Migration risk |
|---|---|---|---|---|---|---|---|---|
| `features/review` | The authoritative editing runtime: session state, timeline mutation, selection, history, clipboard, AI suggestions, drag/trim/keyboard wiring, natural-language command submission | `ReviewWorkspace`, `ReviewWorkspaceProvider`, `useReviewWorkspaceState/Actions`, `buildReviewEditorViewModel`, `ReviewEditorShell`, `ReviewPreviewStage`, `ReviewTimelinePanel`, `ReviewAICommandBar`, design-system primitives, drag/trim/viewport/keyboard hooks | **Owns everything** — the single source of truth | Owns `ReviewEditorShell`'s legacy layout AND is reused (not forked) by Desktop Editor for Preview/Timeline/AI-command-input | none upward; `export-workspace` reads its output contract | None — this is the canonical implementation | None | **Highest** — any change here affects both `/review` and `/editor/:id` simultaneously |
| `features/playback` | Lower-level playback/timeline-command/history primitives (adapters, contracts, pure runtime models, a handful of standalone UI components) | Various `*-runtime.ts`, `*-contracts.ts`, and `ui/professional-timeline-ui.tsx` etc. | Owns low-level playback/timeline-command/history logic | Owns a few standalone UI components (`professional-timeline-ui.tsx`, `timeline-effects-inspector-ui.tsx`, etc.) that are **not currently wired into `/editor/:id` or `/review`** (confirmed in a prior sprint: no import sites from either route) | None found wired in; consumed only by its own ~50 regression scripts | Appears to be a parallel/earlier prototype of timeline logic that never got connected to the live UI — worth flagging, not touching | None | **Low for this sprint** (untouched), but **architecturally ambiguous** — see §4 |
| `features/desktop-editor` | The current-generation Editor Shell: docking grid layout, resizable/collapsible panels, header, tool rail, asset panel (mock data), inspector (tab composition), status bar | `DesktopEditorShell`, `DesktopEditorRuntimeAdapter`, `DesktopGrid`, `PanelDivider`, `useDesktopEditorLayout`, panel components | Owns only its own layout/collapse/resize UI state (`useDesktopEditorLayout`) — no editing/session state | Owns 100% of its own chrome | Reuses `features/review`'s runtime pieces directly (not forked); renders `features/ai-timeline`'s `AiTimeline` and `features/ai-decision-actions`' provider/inspector | Two workspace concepts exist app-wide (this is the *editor* workspace; `features/workspace-v2`/`workspace-shell` are the *project-browser* workspace) — different concerns, not truly duplicate, but the naming overlap ("workspace") is worth disambiguating in the redesign | None | **Medium** — actively evolving, well-tested by its own regression scripts, but still young (6 sprints old) |
| `features/ai-timeline` | Visualizes AI decisions as an overlay layer synchronized (via DOM observation, not shared state) with the real timeline's scroll/zoom/playhead/selection | `AiTimeline`, `TimelineViewportProvider`/`useTimelineViewportContext`, mock-data hook, state hook | Owns its own mock decision dataset + UI interaction state (hover/select/search/filter/collapse) — reads (never writes) real playhead/revision/selection via props | Owns 100% of its own chrome | Depends on `features/review`'s view-model shape (duration/playhead/revision/selection) via props threaded through `desktop-editor`; depends on `features/ai-decision-actions` for lifecycle actions | None | None | **Medium** — the DOM-observation bridge (`data-review-timeline-zoom`/native `scrollLeft`) is a documented, intentionally fragile seam; redesign must not change the DOM contract it observes |
| `features/ai-decision-actions` | AI decision lifecycle state machine (accept/reject/regenerate/pin/disable/duplicate/convert-to-manual/explain/compare), explicitly "Pending Runtime" when no backend adapter is connected | `AiDecisionActionProvider`, `useAiDecisionActions`, `AiDecisionInspector`, typed `AiDecisionActionAdapter` contract | Owns decision lifecycle state (session-local, resets on reload) | Owns `AiDecisionInspector`'s content only | Consumed by `ai-timeline` (block click/context-menu) and `desktop-editor`'s `EditorInspector` (Decision tab) | None | None | **Low** — small, self-contained, explicit about its own incompleteness (no adapter wired yet) |
| `features/export-workspace` | Reads an immutable Review→Export handoff contract and drives render/export UI | `ExportWorkspacePage`, runtime/api-client layer | Owns its own render-request runtime | Owns its own page chrome | Reads a contract written by `features/review`'s export button (`buildExportWorkspaceHref`/`storeReviewToExportContract`) | None | None | **Low** — isolated, real runtime, just needs a visual pass |
| `features/upload` | Media intake UI: dropzone, queue, progress, metadata form | `UploadDropzone`, `UploadQueue`, `UploadProgress`, `ProductionMetadataForm`, validation | Owns its own simulated upload state machine (real validation logic, faked network timing) | Owns its own components | None | None | None | **Low** — logic is sound, only chrome needs a pass |
| `features/production` | A single `ProductionCard` component | `ProductionCard` | none | Owns its own card markup | `components/ui/*` primitives, `lib/mock-productions` | **Duplicate** with `workspace-shell`'s `WorkspaceProjectCard` (different visual treatment, same purpose) | None | Low |
| `features/workspace-v2` | Currently-live `/workspace` implementation | `WorkspaceHome` | none | Owns its own markup (duplicates card markup rather than reusing `ProductionCard`) | `DashboardShell`, `lib/mock-productions` | Overlaps conceptually with the dead `workspace-shell` | `DashboardShell` | **To be superseded** in 17.9 |
| `features/workspace-shell` | An earlier, richer, fully-built workspace shell attempt | `WorkspaceShell`, `WorkspaceSidebar`, `WorkspaceProjectCard` | none | Fully built, never wired | none | **Confirmed dead code** — zero import sites anywhere in `src/` | None | **Zero risk to touch/retire** — not on any live code path |

## 3. Desktop Editor component hierarchy (as currently implemented)

```
app/editor/[productionId]/page.tsx
  └─ DesktopEditorRuntimeAdapter                         (features/desktop-editor/runtime-adapter.tsx)
       └─ ReviewWorkspaceProvider                         (features/review — UNCHANGED runtime)
            └─ DesktopEditorRuntimeContent                (mirrors runtime-workspace.tsx's wiring)
                 └─ DesktopEditorRuntimeEditor
                      └─ DesktopEditorShell                (features/desktop-editor/components)
                           ├─ AiDecisionActionProvider      (features/ai-decision-actions)
                           └─ DesktopGrid                   (pure CSS-grid layout primitive, memoized)
                                ├─ header      → DesktopEditorHeader
                                ├─ rail        → EditorToolRail
                                ├─ assets      → EditorAssetPanel        (mock data)
                                ├─ assetsDivider → PanelDivider
                                ├─ preview     → EditorPreviewCanvas → ReviewPreviewStage (Review runtime, reused)
                                ├─ timelineDivider → PanelDivider
                                ├─ timeline    → EditorTimelineWorkspace
                                │      ├─ TimelineViewportProvider        (features/ai-timeline/context)
                                │      │    ├─ AiTimeline                (features/ai-timeline — own tracks/blocks)
                                │      │    └─ TimelineViewportObservedRegion
                                │      │         └─ ReviewTimelinePanel  (Review runtime, reused, unmodified)
                                ├─ inspectorDivider → PanelDivider
                                ├─ inspector   → EditorInspector
                                │      ├─ "Properties" tab → PropertiesPlaceholder (static)
                                │      ├─ "AI Copilot" tab → EditorAiCopilot → ReviewAICommandBar (Review runtime, reused)
                                │      └─ "Decision" tab   → AiDecisionInspector (features/ai-decision-actions)
                                └─ statusBar   → EditorStatusBar
```

## 4. State ownership map

| State | Owned by | Consumed by | Notes |
|---|---|---|---|
| Session/timeline/selection/history/clipboard | `ReviewWorkspaceProvider` (`features/review/react` + `features/review/state`) | Both `/review` (directly) and `/editor/:id` (via its own separate provider instance) | **Two independent runtime instances exist** for the two routes — documented, intentional, but means `/review` and `/editor/:id` do not share a live session today. Not a bug to fix in 17.1; a fact to carry into any future "unify the two routes" decision. |
| Zoom/scroll/content-width (real timeline viewport) | Internal to `ReviewTimelinePanel` (`useReviewTimelineViewport`, one instance per mount, no external export) | Observed (read-only, via DOM attribute + native scroll properties) by `TimelineViewportContext` | Intentionally fragile seam, already documented; **do not attempt to "clean this up" by lifting state** — that would require editing Timeline Runtime. |
| Playhead time / revision / selected clip ids | `ReviewWorkspaceProvider` → `buildReviewEditorViewModel` (pure fn) | Passed as plain props into both `ReviewTimelinePanel` and `TimelineViewportProvider` | Single source of truth, correctly threaded — no duplication here. |
| AI decision mock data + lifecycle | `useAiTimelineMockData` (mock, session-local) + `AiDecisionActionProvider` (lifecycle, session-local) | `AiTimeline`, `AiDecisionInspector` | Explicitly not backed by any API yet — "Pending Runtime" everywhere by design. |
| Desktop Editor layout (panel widths/heights/collapse) | `useDesktopEditorLayout` (`features/desktop-editor/hooks`) | `DesktopEditorShell` | Pure UI state, not persisted across reloads (documented known limitation from 16.10.3). |
| Mock production data (`lib/mock-productions.ts`) | Module-level constant array | `/`, `/workspace` (`WorkspaceHome`), `features/production`, `features/workspace-shell` (dead) | One shared shape, good — but two different card components render it (`ProductionCard` vs. `WorkspaceProjectCard`), a genuine duplication to resolve in 17.9, not 17.1. |

**Ambiguous/duplicated state identified (documented only, not refactored per this sprint's scope):**
1. Two independent `ReviewWorkspaceProvider` instances for `/review` and `/editor/:id` (same code, different live sessions).
2. Two production-card visual implementations rendering the same `Production` shape.
3. Two "workspace" feature modules (`workspace-v2` live, `workspace-shell` dead) representing two abandoned/superseded attempts at the same page.

## 5. Existing regression test inventory (`frontend/scripts/*.cjs`)

~74 `.cjs` scripts exist, all following the same idiom (raw Node `require`, string/structural assertions against source files, no visual/screenshot tooling). Grouped by domain:

| Domain | Approx. count | Examples |
|---|---|---|
| Review workspace runtime (API client, session, selection, clipboard, AI suggestions, command state) | ~20 | `test-review-workspace-session-runtime.cjs`, `test-review-selection-api-state-runtime.cjs`, `test-review-ai-suggestion-*.cjs` |
| Review timeline UI (drag, trim, snap, zoom/scroll, keyboard, clipboard UI integration) | ~20 | `test-review-timeline-drag-session-runtime.cjs`, `test-review-runtime-clip-trim-handles.cjs`, `test-review-timeline-snap-runtime.cjs` |
| Playback/timeline-command/history (lower-level, `features/playback`) | ~20 | `test-timeline-history-*.cjs`, `test-timeline-clip-move-runtime.cjs`, `test-professional-*.cjs` |
| Export workspace | 2 | `test-export-workspace-frontend-runtime.cjs`, `test-export-workspace-page-navigation.cjs` |
| Master/aggregate regression | 2 | `test-review-workspace-regression.cjs` (the `npm run test:review` entry point — runs ~17 of the above scripts as subprocesses), `test-regression-runtime-foundation.cjs` |
| Desktop Editor / AI Decision / Workspace foundation (current generation) | 3 | `test-desktop-editor-ui-refinement.cjs`, `test-ai-decision-action-runtime.cjs`, `test-workspace-foundation.cjs` |

**This sprint adds one more**: `test-frontend-design-system.cjs`, following the exact same idiom (no new testing framework introduced).

## 6. Summary

- The app has one authoritative runtime (`features/review`) reused correctly by the current-generation Editor; that reuse pattern is sound and must not change.
- `features/playback` is a substantial, well-tested, but **currently unwired** parallel implementation — worth flagging for future architectural review, out of scope to touch or reconcile this sprint.
- The non-Editor surfaces (`/`, `/workspace`, `/upload`, `/export`, `/productions`, `/ai-queue`, `/styles`, `/settings`) sit on an older, un-tokenized visual system and, in four cases, are non-functional placeholders wearing production chrome.
- No duplicated *runtime* state was found inside the Editor stack itself — the ambiguity that exists (two workspace providers, two production cards, two workspace modules) is at the page/feature-composition level, not inside any single runtime, and is documented for a later sprint (17.9) rather than acted on here.
