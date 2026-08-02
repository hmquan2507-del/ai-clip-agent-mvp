# Editor Interaction Model

Sprint 17.1.5 — Desktop UX Blueprint
Date: 2026-07-25
Status: Blueprint — implementation contract for Sprints 17.2–17.8. No code changed by this document.

Defines the selection model, context propagation, per-surface interaction behavior, and keyboard/focus blueprint. Documents real architecture (`features/review` Selection Runtime, `features/ai-decision-actions`, `features/ai-timeline`) — no runtime is redefined here.

---

## 1. Selection model

There are exactly **two** selection concepts in the system, and they must never merge (P33):

1. **Real selection** (Selection Runtime, owned by `features/review/state/runtime.ts`, exposed via `snapshot.selection`/clipboard-adjacent state) — governs which clip(s)/track region is the target of edit operations (trim, split, drag, delete, clipboard).
2. **AI decision selection** (`AiTimeline`'s local `selectedBlockId`) — governs which AI decision block is being inspected/acted upon in the Decision tab. Related to, but independent of, the real selection.

### 10 selection contexts

| # | Context | Owner | Notes |
|---|---|---|---|
| 1 | No selection | Selection Runtime | Default/idle state; Inspector shows "No selection" |
| 2 | Single clip selected (Manual Timeline) | Selection Runtime | Drives Inspector Properties tab |
| 3 | Multiple clips selected (Manual Timeline) | Selection Runtime | Drives multi-clip-aware Inspector state (batch properties, if supported by runtime) |
| 4 | Track-region selection (range, no specific clip) | Selection Runtime | Used by range-based operations (e.g. ripple delete), runtime-defined |
| 5 | AI decision block selected (AI Timeline) | `AiTimeline.selectedBlockId` | Drives Inspector Decision tab; independent of Selection Runtime |
| 6 | Asset selected (Asset Panel) | Asset Panel local state | Pre-insertion context only; does not touch Selection Runtime until inserted |
| 7 | Clipboard-held selection (copied, not yet pasted) | Selection Runtime / clipboard module | Persists across a copy action; visually distinct from "currently selected" |
| 8 | Linked/grouped selection (link groups) | Selection Runtime | Selecting one member visually indicates its linked group, runtime-defined |
| 9 | Stale/removed selection target | N/A (fallback) | Occurs when a selected id no longer resolves; must fall back to "no selection" (P34) |
| 10 | Cross-surface highlighted (derived, not owned) | Derived/read-only | E.g. AI Timeline dimming a decision related to the currently real-selected clip — a visual echo, not a selection state of its own |

---

## 2. Context propagation matrix

Rows = actions/events. Columns = which surface/runtime is affected and how. "Owns/Writes" = the single authoritative writer; "Reacts (derived)" = read-only visual response; "—" = not applicable.

| Action / Event | Selection Runtime | Manual Timeline | AI Timeline | Inspector | Preview | Asset Panel | AI Director | History |
|---|---|---|---|---|---|---|---|---|
| Click clip on Manual Timeline | Owns/Writes | Reacts (visual selected state) | Reacts (derived highlight of related decision) | Reacts (Properties tab) | Reacts (seeks to clip start, if applicable) | — | — | — |
| Click AI decision block | — | Reacts (derived highlight of related clip range) | Owns/Writes (`selectedBlockId`) | Reacts (Decision tab) | — | — | — | — |
| Drag clip (Manual Timeline) | Reacts (unchanged selection) | Owns/Writes (position/time) | Reacts (re-render if linked) | Reacts (Properties updates) | Reacts (playhead-relative preview if scrubbing) | — | — | Owns/Writes (undo entry) |
| Trim clip edge | Reacts (unchanged selection) | Owns/Writes (duration) | Reacts (re-render) | Reacts (Properties updates) | Reacts | — | — | Owns/Writes |
| Split clip | Owns/Writes (new selection = one resulting segment, runtime-defined) | Owns/Writes | Reacts | Reacts | Reacts | — | — | Owns/Writes |
| Delete clip | Owns/Writes (clears or moves to next, runtime-defined) | Owns/Writes | Reacts | Reacts (falls back per P34) | Reacts | — | — | Owns/Writes |
| Copy (clipboard) | Reacts (adds clipboard-held state) | — | — | — | — | — | — | — |
| Paste | Owns/Writes (new selection = pasted clip(s)) | Owns/Writes | Reacts | Reacts | Reacts | — | — | Owns/Writes |
| Undo / Redo | Owns/Writes (restored selection, runtime-defined) | Owns/Writes | Reacts | Reacts | Reacts | — | — | Owns/Writes |
| Accept AI decision | — | Reacts (if decision applies a timeline change, forwarded via existing action boundary) | Owns/Writes (lifecycle state) | Reacts (Decision tab updates) | Reacts (if resulting change affects current preview) | — | — | Owns/Writes (if applied) |
| Reject AI decision | — | Reacts (if applicable) | Owns/Writes (lifecycle state) | Reacts | — | — | — | Owns/Writes (if applied) |
| Regenerate AI decision | — | — | Owns/Writes (processing state) | Reacts | — | — | — | — |
| Pin AI decision | — | — | Owns/Writes | Reacts | — | — | — | — |
| Import asset | — | — | — | — | — | Owns/Writes | — | — |
| Insert asset onto timeline | Owns/Writes (new selection = inserted clip) | Owns/Writes | Reacts | Reacts | Reacts | Reacts (unchanged) | — | Owns/Writes |
| Zoom/scroll Manual Timeline | — | Owns/Writes | Reacts (via `TimelineViewportContext` bridge) | — | — | — | — | — |
| Resize/collapse Asset Panel | — | — | — | — | Reacts (available width) | Owns/Writes (own width state) | — | — |
| Resize/collapse Inspector | — | — | — | Owns/Writes (own width state) | Reacts (available width) | — | — | — |
| Collapse AI Timeline | — | Reacts (more vertical space) | Owns/Writes (collapsed flag) | — | — | — | — | — |
| Submit AI Director command | Reacts (if command results in selection change, forwarded via existing action) | Reacts (if applied) | Reacts (if applied) | Reacts | Reacts | — | Owns/Writes (submission/ack state) | Owns/Writes (if applied) |
| Playhead scrub (Preview or Timeline ruler) | — | Reacts (playhead position) | Reacts (playhead position) | — | Owns/Writes | — | — | — |
| Selection target removed/renamed | Owns/Writes (falls back to none) | Reacts | Reacts | Reacts (falls back per P34) | Reacts | — | — | — |
| Window resize below viewport breakpoint | — | Reacts (space) | Reacts (space, may auto-collapse) | Reacts (may auto-collapse) | Reacts (protected floor maintained) | Reacts (may auto-collapse) | — | — |

22 actions × 8 columns, as required.

---

## 3. Preview interaction

- Preview is playback/scrub-only in this program's scope. It does not originate selection (P11, FRR-4 deferred).
- Scrubbing the Preview's own transport control moves the single shared playhead (P12) — the same value Manual Timeline's ruler and AI Timeline's marker read.
- Preview never shows a competing "select this clip" affordance; selecting a clip happens on Manual Timeline (or, in the future, via FRR-4 if a runtime decision explicitly adds that capability).
- Preview's chrome (controls, transport) dims after an idle period (17.3 scope) but the canvas content itself is never obscured beyond that documented chrome behavior.

## 4. Manual Timeline interaction

- All manual editing gestures (select, drag, trim, split, delete, snap, link/group, multi-select, clipboard, undo/redo) are owned entirely by the existing Timeline/Selection/Drag/Trim/History/Clipboard runtimes and are not redefined by this document (P13).
- This blueprint documents only the *visual feedback* expected around these gestures: hover treatment on hoverable clip edges, a distinct cursor during drag/trim, a snap-guide line when Magnetic Snap Engine reports a snap candidate (existing runtime output, not new logic), and a selection-outline treatment matching Design System §Timeline standards.
- Zoom and scroll remain exclusively owned by Timeline Runtime (P15); AI Timeline observes rather than drives.

## 5. AI Timeline interaction

- Clicking a decision block sets `selectedBlockId` and opens/updates the Inspector's Decision tab; it does not alter the real Selection Runtime's selection (P33).
- Hovering a decision block surfaces its `reason` (tooltip or Explain affordance) per P17.
- Decision lifecycle actions (accept/reject/regenerate/pin) route exclusively through `useAiDecisionActions().runAction`-equivalent calls (P20) — never a direct Timeline/Selection Runtime mutation.
- A decision that results in an actual timeline change (e.g. "accept" applying a trim) still requires that change to flow through the existing Review Workspace action boundary — AI Timeline components never call `ReviewWorkspaceActions` directly.
- AI Timeline's own zoom/scroll is never independent — it is fully derived from `TimelineViewportContext` (P19); AI Timeline has no scrollbar/zoom control of its own.

## 6. Inspector interaction

- Inspector displays exactly one of three contexts based on the current selection state: Properties (real selection, clip context), AI Copilot (contextual suggestions relevant to current selection/time range), Decision (AI decision selection).
- Switching tabs does not change any selection — tabs are a view choice, not a selection-setting action (P23).
- If the current selection becomes stale (P34), Inspector falls back to its "No selection"/empty state for whichever tab is active, rather than rendering data for a nonexistent target.
- Properties/AI Copilot/Decision remain three separate data sources this program (P24); presentation only is unified.

## 7. AI Director interaction

- Always visible as a docked strip at the bottom of Timeline Workspace, never a full-screen or separate-route chat experience (P25).
- Always displays current context (selection summary or "applies to full timeline") alongside the input field.
- Submission → acknowledgment always resolves to one of: understood+applied, understood+pending-runtime, misunderstood/unsupported (P26) — the honest three-outcome model, never a bare "sent" with no resolution.
- All submissions flow through the existing `ReviewAICommandBar` → `onAICommandSubmit` → `actions.submitAICommand` path (P27); no parallel command channel is introduced.

## 8. Keyboard and focus blueprint

Existing Keyboard Runtime shortcuts (Manual Timeline editing: split/delete/undo/redo/nudge/etc.) are authoritative and are not restated or redefined here — exact keybindings are owned by `features/review/keyboard` and are intentionally not reproduced in this document to avoid drift (P41). This blueprint instead defines **focus zones**, so future interactive surfaces know where they may safely add zone-scoped keyboard behavior without colliding with Keyboard Runtime's global bindings:

| Focus zone | Scope | New shortcuts allowed? |
|---|---|---|
| Global (no zone focused) | App-wide, includes Keyboard Runtime's existing global bindings | No — authoritative, closed to new bindings |
| Manual Timeline | Clip/track editing | No — owned entirely by Keyboard Runtime |
| AI Timeline | Decision block navigation/selection | Yes, zone-scoped only (e.g. arrow-key roving tabindex among blocks), must not shadow any global binding |
| Inspector | Tab/field navigation within the panel | Yes, standard tab/arrow-key field navigation, zone-scoped |
| Asset Panel | Asset list navigation | Yes, zone-scoped list navigation (arrow keys, Enter to insert) |
| AI Director input | Text entry | Standard text-input behavior; Enter submits, Escape blurs — zone-scoped, no collision with global bindings since focus is inside a text field |
| Preview | Playback transport | No new bindings without an explicit collision check against Keyboard Runtime's existing playback shortcuts (space/play, arrow-seek, etc., if any are already claimed globally) |

Any new zone-scoped shortcut proposed in Sprints 17.2–17.8 must be checked against Keyboard Runtime's existing global bindings before being added; a collision blocks that specific shortcut, not the whole sprint.
