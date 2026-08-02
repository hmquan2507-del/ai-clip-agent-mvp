# Editor UX Principles

Sprint 17.1.5 — Desktop UX Blueprint
Date: 2026-07-25
Status: Blueprint — implementation contract for Sprints 17.2–17.8. No code changed by this document.

42 actionable, testable principles across 13 categories. Each has a statement, why it exists, its implementation implication, and how to verify it's actually true of a shipped surface.

---

## Product hierarchy

### P1 — Preview and Timeline are always the primary visual hierarchy.
**Why:** The product's core loop (review AI decisions → refine on the timeline) happens in these two surfaces; everything else supports that loop.
**Implication:** Preview and Manual Timeline never shrink to accommodate a secondary panel's preferred size.
**Verification:** At every supported viewport, Preview's rendered width/height and Timeline's rendered height meet or exceed their documented minimums (`desktop-editor-ux-blueprint.md` §Panel and Docking Rules) regardless of Asset Panel/Inspector state.

### P2 — Timeline receives more workspace priority than secondary panels.
**Why:** Editing precision requires vertical space; a cramped timeline actively degrades the product's core task.
**Implication:** When vertical space is constrained, Timeline Workspace height is defended before Asset Panel/Inspector width.
**Verification:** Resizing the window smaller narrows/collapses Asset Panel and Inspector before Timeline Workspace height is reduced below its documented minimum.

### P3 — Assets and Inspector must never reduce Preview below its usable minimum.
**Why:** A preview too small to judge framing/composition breaks the review step of the core workflow.
**Implication:** Asset Panel and Inspector have hard maximum widths (already established: 320px/340px) precisely so their combined footprint can never starve Preview below its floor.
**Verification:** Arithmetic check (already performed for 16.10.6.1/17.1): Tool Rail + Asset Panel(max) + Inspector(max) + dividers, subtracted from the smallest supported viewport width, always leaves Preview's documented minimum width or more.

### P4 — Secondary panels may collapse before Preview or Timeline becomes unusable.
**Why:** Collapse is the release valve for space pressure; Preview/Timeline are never candidates for collapse.
**Implication:** The collapse priority order (`frontend-responsive-system.md`, reaffirmed in this blueprint) always exhausts Asset Panel/Inspector narrowing and collapsing first.
**Verification:** No code path collapses or hides Preview or Manual Timeline at any supported viewport.

### P5 — The editor is a workspace, not a page.
**Why:** Directly opposes the "SaaS dashboard"/"landing page" anti-patterns named in the product context — a page has a beginning/end and marketing framing; a workspace is inhabited continuously.
**Implication:** No hero banners, no marketing headlines, no `display`/`pageTitle` typography roles anywhere inside the Editor shell (only `panelTitle`/`sectionTitle` and smaller).
**Verification:** Grep the Desktop Editor component tree for `.ce-text-display`/`.ce-text-page-title` usage — must return zero matches.

---

## Editing workflow

### P6 — The workflow is source → AI → review → refine → export, and the UI should make that sequence legible.
**Why:** Stated core product workflow; the UI is the workflow's visible shape.
**Implication:** AI Timeline (review) sits visually adjacent to and synchronized with Manual Timeline (refine) — never as a separate, disconnected tool.
**Verification:** AI Timeline and Manual Timeline share one `TimelineViewportContext` (already true) and are rendered in the same Timeline Workspace panel (already true) — this blueprint's job is to keep it true, not to introduce a new mechanism.

### P7 — AI does the first 80–90% of the work; the timeline is for refinement, not creation from scratch.
**Why:** Explicit, carried-forward product principle from every prior Desktop Editor sprint.
**Implication:** Manual Timeline is never presented as the "primary" starting point in onboarding/empty states — AI Timeline and AI Copilot/Director are the first thing a new project shows meaningful content in.
**Verification:** Empty-project state (Editor State Matrix) shows AI-oriented empty-state copy before manual-editing empty-state copy.

### P8 — Every step in the workflow must be reachable without leaving the Editor shell.
**Why:** Avoids the "collection of disconnected cards/pages" anti-pattern.
**Implication:** Export is a header action + a route transition (already the case via `ExportWorkspacePage`), not a context switch that abandons the Editor's mental model.
**Verification:** Export entry point remains in `DesktopEditorHeader` (already true); this blueprint does not add a competing entry point.

### P9 — Manual refinement never requires the user to first understand AI internals.
**Why:** AI Timeline is optional context, not a prerequisite for editing.
**Implication:** Every Manual Timeline interaction (select/drag/trim/split/etc.) functions identically whether or not the user has ever opened AI Timeline or Inspector's Decision tab.
**Verification:** Interaction Model's Manual Timeline section defines no interaction that depends on AI Timeline state.

---

## Preview

### P10 — Preview is the highest-fidelity, lowest-chrome surface in the Editor.
**Why:** Design direction principle "surface contrast before borders" applied most strongly where judgment of the actual footage matters most.
**Implication:** Preview's own chrome (not `ReviewPreviewStage`'s internals) uses `--ce-bg-canvas`, the darkest token, and idle-dims per `frontend-design-system.md` §Preview.
**Verification:** Preview canvas background computed value is `--ce-bg-canvas` at rest; chrome opacity reduces after a defined idle period (implemented in 17.3).

### P11 — Preview must never become a second selection owner.
**Why:** Explicit constraint (Task 8) — exactly one selection authority (Selection Runtime) must exist; a second one invites desync.
**Implication:** Clicking inside the preview canvas may seek playback or (if a future overlay-based clip-picking feature is added) forward a selection *intent* to the real Selection Runtime — it never sets a local "preview-selected" state that Inspector/Timeline don't know about.
**Verification:** No component under `EditorPreviewCanvas` holds its own `selectedClipId`-shaped state; any selection-adjacent interaction there calls the same `onSelectClip` path Timeline/AI Timeline already use.

### P12 — Preview time, timeline playhead, and AI decision time ranges are one shared time axis, never three.
**Why:** Prevents the "three clocks that occasionally agree" bug class.
**Implication:** `playheadTime` from `ReviewEditorViewModel` is the single value all three surfaces read (already true architecturally — this principle guards against ever changing that).
**Verification:** Grep for any locally-computed "current time" state outside the `TimelineViewportContext`/view-model chain — must return none.

---

## Manual Timeline

### P13 — Manual Timeline's runtime behavior (drag/trim/snap/split/clipboard/history) is authoritative and immutable by this program.
**Why:** Explicit, repeated constraint across every sprint to date.
**Implication:** Every UX decision in this blueprint about Manual Timeline describes *presentation of* that behavior, never a *change to* it.
**Verification:** `features/review/shell/timeline.tsx` byte-diff against the pre-blueprint commit is empty after every sprint that references this principle.

### P14 — Selected clip treatment must be immediately distinguishable from hovered, locked, and disabled clips.
**Why:** UX audit F14 (state inconsistency) named this gap directly.
**Implication:** Four visually distinct treatments (selected/hover/locked/disabled), each using a `--ce-state-*`/`--ce-decision-*` token, never color-only.
**Verification:** Design System's Timeline standards (§Task 6) are applied 1:1 once a runtime-boundary exception is separately approved (flagged as a Future Runtime Requirement below, not solved here).

### P15 — Timeline zoom and scroll belong to Timeline Runtime alone; nothing else may introduce a second scroll/zoom authority for the same content.
**Why:** Already the architecture (`useReviewTimelineViewport`); stated here so no future sprint "helpfully" adds a competing scrollbar.
**Implication:** Any new UI (AI Timeline, minimap, etc.) that needs zoom/scroll must observe Timeline Runtime's values (as `TimelineViewportContext` already does), never maintain its own independent value for the same timeline.
**Verification:** Exactly one `useReviewTimelineViewport` call site exists in the codebase (inside `ReviewTimelinePanel`).

---

## AI Timeline

### P16 — AI must assist the editing workflow, not visually dominate it.
**Why:** Explicit product-context anti-pattern ("decorative AI concept"), and design direction principle 2.
**Implication:** AI Timeline's default height (110–150px) is deliberately smaller than Manual Timeline's; AI Timeline never grows to dominate the Timeline Workspace by default.
**Verification:** AI Timeline height token (`--ce-dim-ai-timeline-height-default`) stays within its documented range across all redesign sprints.

### P17 — AI recommendations must explain what will change, not just that something will change.
**Why:** Trust in an AI-first tool depends on legible reasoning, not opaque magic.
**Implication:** Every AI Timeline block's tooltip/Explain action surfaces `reason` (already implemented) and every AI Copilot suggestion states its effect in its description (already implemented) — this principle guards against ever shipping an AI action with no stated reason.
**Verification:** Every `AiBlock`/`AiCopilotSuggestion` shape retains a required, non-empty `reason`/`description` field.

### P18 — AI operations must expose pending, processing, success, stale, and error states — never a silent no-op.
**Why:** Explicit "no interaction may imply success when backend execution is unavailable" constraint; matches the already-proven "Pending Runtime" honesty pattern.
**Implication:** Every future AI action UI (Copilot suggestions, AI Director) follows `AiDecisionActionRecord`'s existing state model rather than inventing a simpler (dishonest) one.
**Verification:** Any new AI-triggered UI element has a mapped state for each of: pending, processing, success, stale, error — verified against `AiDecisionLifecycleState`/`runtimeStatus`.

### P19 — AI Timeline and Manual Timeline share one editing time context and must never silently drift out of sync.
**Why:** Same reasoning as P12, restated for the AI Timeline specifically since it's the newest, most failure-prone synchronization point.
**Implication:** `TimelineViewportContext`'s DOM-observation bridge remains the sole synchronization mechanism; no sprint introduces a second one "to fix a bug," since a second mechanism is a worse bug.
**Verification:** Exactly one `TimelineViewportProvider` exists per Editor instance; its `connected` flag is monitored, not replaced.

### P20 — AI Timeline may never directly mutate Manual Timeline from a visual component.
**Why:** Explicit Task 10 constraint; prevents the AI layer from becoming a second, competing editing authority.
**Implication:** Every AI Timeline action (accept/reject/regenerate/pin/etc.) flows through `useAiDecisionActions()`'s typed action contract — never a direct call into `ReviewWorkspaceActions`.
**Verification:** `ai-timeline/components/*` contains zero direct imports of `ReviewWorkspaceActions`/`useReviewWorkspaceActions`.

### P21 — Every AI decision block remains legible at every zoom level, including icon-only compaction.
**Why:** UX audit F6.
**Implication:** Lifecycle state (processing/stale/disabled/etc.) uses a treatment that survives compaction to icon-only width (e.g. a corner indicator), not solely a body-opacity/dash change invisible at 16px.
**Verification:** At `COMPACT_WIDTH_THRESHOLD` (30px), a block's lifecycle state is still visually distinguishable from "normal" in a screenshot comparison.

---

## Inspector

### P22 — Inspector is one contextual system that changes content based on selection, not three unrelated panels sharing a tab strip.
**Why:** UX audit F7.
**Implication:** Properties/AI Copilot/Decision share one section-spacing rhythm, one empty-state pattern, one sticky-header/footer convention (Design System §Task 6) — data ownership stays separate (P24), only presentation is unified.
**Verification:** Section spacing (`--ce-space-md` between sections) and empty-state markup are identical across all three tab contents once 17.7 lands.

### P23 — Inspector reacts to selection; it does not originate selection.
**Why:** Explicit Task 6 critical rule.
**Implication:** No Inspector-internal control sets `selectedClipId`/`selectedBlockId`-equivalent state; it only reads the current selection and offers actions that, if taken, go through the same action boundaries every other surface uses.
**Verification:** `EditorInspector`/`AiDecisionInspector`/Properties tab contain no locally-owned "current selection" state distinct from what `useAiDecisionActions().selected` or the Timeline's own selection already report.

### P24 — Properties, AI Copilot, and Decision remain three separate data sources during this program; only their presentation is unified.
**Why:** Explicit instruction carried from 16.10.6.1 and restated in Task 11 — "describe the intended future consolidated experience without implementing it yet."
**Implication:** No sprint before a dedicated "Inspector architecture" sprint merges these three tabs' underlying state.
**Verification:** `useAiDecisionActions()`'s public API shape is unchanged by any Inspector-focused sprint through 17.8.

---

## AI Director

### P25 — AI Director is a command surface embedded in the editing context, not a general-purpose chat window.
**Why:** Explicit product-context anti-pattern ("ChatGPT clone").
**Implication:** AI Director always shows current selection/time-range context alongside the input (Task 12) — it never presents as a blank, context-free chat box.
**Verification:** AI Director's UI always renders a context indicator (even if that indicator says "No selection — applies to full timeline") whenever the input is focused.

### P26 — Every AI Director command clearly states what AI understood, what's affected, and whether it was actually applied.
**Why:** Same trust requirement as P18, specific to natural-language input where ambiguity risk is highest.
**Implication:** Submission produces a visible acknowledgment (already true — `ReviewAICommandBar`'s accepted-submission-id reset mechanism) that this blueprint extends conceptually to state "applied" vs. "pending runtime" explicitly, not just "accepted."
**Verification:** Every command submission result maps to one of: understood+applied, understood+pending-runtime, misunderstood/unsupported — never an unstated fourth outcome.

### P27 — AI Director never bypasses the natural-language command submission boundary.
**Why:** Explicit runtime-preservation constraint.
**Implication:** All future AI Director visual work continues to route exclusively through `ReviewAICommandBar` → `onAICommandSubmit` → `actions.submitAICommand`.
**Verification:** No new component introduces a second `fetch`/action call path for natural-language commands.

---

## Panels and docking

### P28 — Every resizable panel has a documented min/default/max and a keyboard-operable divider.
**Why:** Already proven correct in `PanelDivider`/`useLayoutResizer` — stated as a durable principle so it isn't lost in future rewrites.
**Implication:** Any new resizable panel (should one be added) reuses this exact pattern rather than a bespoke one.
**Verification:** Every `PanelDivider` instance has `min`/`max`/`defaultValue` props set and responds to arrow keys + double-click reset.

### P29 — Panel collapse never destroys panel state; it hides it.
**Why:** A collapsed Asset Panel/Inspector should restore exactly as the user left it.
**Implication:** Collapse toggles a boolean; it does not unmount/remount the panel's internal state (search query, selected asset, active tab).
**Verification:** Collapsing then expanding Asset Panel preserves its search query and view-mode (grid/list) state.

### P30 — Panel width/collapse state is session-local unless a runtime/adapter already persists it.
**Why:** Explicit Task 5 constraint — do not invent persistence.
**Implication:** `useDesktopEditorLayout`'s current reset-on-reload behavior is the accepted baseline; no sprint through 17.8 adds `localStorage`/backend persistence for layout state without a separate, explicit decision.
**Verification:** Reloading the Editor resets all panel widths/collapse states to their defaults (current, intentional behavior).

---

## Selection

### P31 — Selection is stable until the user explicitly changes it or the selected object is removed.
**Why:** Explicit Task 1 example principle; prevents jarring, unrequested selection changes.
**Implication:** No background process (AI decision arriving, timeline revision bump, panel resize) ever silently changes the current selection.
**Verification:** Selection Interaction Model's per-context table shows no "external event → selection changes" row without an explicit user action driving it.

### P32 — Contextual panels react to selection without themselves changing it.
**Why:** Restates P23 at the general (not Inspector-specific) level — applies to Asset Panel, AI Timeline, and any future panel too.
**Implication:** Any panel that "reacts" to selection (e.g. AI Timeline highlighting a linked clip) does so via a read-only derived highlight, never by calling a selection-setting action itself.
**Verification:** Context Propagation Matrix shows every "reacts to selection" row as `Derived visual state`, never `Write through existing action`, for panels other than the one the user directly interacted with.

### P33 — Selecting a timeline clip may highlight related AI decisions; it must not replace the primary clip selection with a decision selection.
**Why:** Explicit Task 6 critical rule — the two selection concepts (real clip selection, AI decision selection) are related but distinct and must not collapse into one.
**Implication:** `state.selectedBlockId` (AI Timeline's local decision-selection state) and `snapshot.selection`/`clipboard.selectedClipIds` (the real Selection Runtime) remain two separate, cross-referenced values, never merged into one variable.
**Verification:** `AiTimeline`'s `selectedBlockId` and the real timeline's selection remain independently readable and settable, exactly as implemented today.

### P34 — Removed or stale objects safely clear or recover selection rather than pointing at nothing.
**Why:** Explicit Task 6 critical rule.
**Implication:** Any surface holding a reference to a selected id must handle the case where that id no longer resolves to a live object, falling back to an explicit "no selection"/empty state rather than rendering broken data.
**Verification:** Interaction Model's "Unsupported or stale selection" context row defines this fallback explicitly for every consuming surface.

---

## Feedback and state

### P35 — No visual component may directly mutate authoritative runtime state.
**Why:** The single most repeated constraint across this entire program.
**Implication:** Every mutating interaction in every future sprint traces to an existing `ReviewWorkspaceActions`/`useAiDecisionActions().runAction` call — never a new `fetch`, a new direct state mutation, or a bypass of the provider tree.
**Verification:** The blueprint validation test (and every sprint's own regression script) greps every touched file for direct API calls and known mutation-function-name patterns.

### P36 — No interaction may imply success when backend execution is unavailable.
**Why:** Explicit constraint; matches the "Pending Runtime" honesty pattern already proven.
**Implication:** Any UI that cannot currently execute a real backend action (most AI Copilot/Director actions today) must show a state that honestly says so, never a fake "done" checkmark.
**Verification:** Every action button that has no connected adapter renders (directly or via its result state) a "Pending Runtime"-equivalent indicator when invoked.

### P37 — Color communicates state and category, not decoration.
**Why:** Design direction principle 4, restated as a testable rule.
**Implication:** Any new color usage must map to a named `--ce-state-*`/`--ce-decision-*`/`--ce-timeline-*` token or be rejected in review.
**Verification:** No component introduces a literal hex/RGB color value outside the token files.

### P38 — Borders are secondary to spacing and surface hierarchy.
**Why:** UX audit F11; design direction principle 3.
**Implication:** New UI defaults to background-contrast separation (`--ce-bg-panel` vs. `--ce-bg-panel-raised`) and reserves visible borders for interactive affordances (dividers, focus, selection).
**Verification:** Visual review checklist item; spot-checked per sprint, not automatable precisely, but any PR introducing a new bordered "separator" div where a background-contrast step would do is a documented anti-pattern to flag.

### P39 — Destructive actions require a visual distinction clearly different from neutral actions.
**Why:** Explicit Task 1 example principle; prevents accidental data loss.
**Implication:** Delete/reject/disable-adjacent actions use `--ce-state-error`-derived treatment, distinct from primary/neutral buttons, consistently across Manual Timeline, AI Timeline, and Inspector.
**Verification:** Every destructive action's button/menu-item uses the `danger` Button variant (Design System §Task 5), never `primary`/`secondary`/`ghost`.

---

## Accessibility

### P40 — Keyboard workflows remain first-class, not a secondary affordance bolted onto a mouse-first design.
**Why:** Explicit Task 1 example principle; professional creative tools are keyboard-heavy by nature.
**Implication:** Every new interactive surface introduced in 17.2–17.8 is reachable and operable via keyboard from day one, not "added later."
**Verification:** Accessibility System's per-sprint deferred-item table (`frontend-accessibility-system.md`) is fully closed by 17.11, and no sprint ships a mouse-only interaction.

### P41 — Existing editing keyboard shortcuts are authoritative and are never remapped, removed, or shadowed by new UI.
**Why:** Explicit, repeated constraint; Keyboard Runtime already owns this domain correctly.
**Implication:** Any new keyboard interaction (e.g. AI Timeline's future roving-tabindex) must be scoped to its own focus zone and never intercept a key combination Keyboard Runtime already claims globally.
**Verification:** Keyboard/Focus Blueprint (`editor-interaction-model.md`) explicitly enumerates focus zones so new shortcuts are added only within a zone, never globally, without a checked collision.

---

## Responsive desktop

### P42 — Empty space should improve focus, not make the editor feel unfinished.
**Why:** Explicit Task 1 example principle; directly guards against both "too dense to read" and "too sparse to feel intentional."
**Implication:** Negative space around Preview (P10) is a deliberate design choice communicating focus, not a leftover gap; conversely, Asset Panel/Inspector at minimum width must still feel complete, not truncated mid-thought.
**Verification:** Visual review at every documented viewport (`desktop-editor-ux-blueprint.md` §Responsive) confirms no panel appears to be "cut off" rather than intentionally compact.

---

## Summary

42 principles across 13 categories (Product hierarchy 5, Editing workflow 4, Preview 3, Manual Timeline 3, AI Timeline 6, Inspector 3, AI Director 3, Panels and docking 3, Selection 4, Feedback and state 5, Accessibility 2, Responsive desktop 1) — within the required 35–50 range. Every principle above states its statement, why it exists, its implementation implication, and a concrete verification method, per Task 1's requirement.
