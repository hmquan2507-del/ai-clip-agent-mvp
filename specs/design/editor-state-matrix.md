# Editor State Matrix

Sprint 17.1.5 — Desktop UX Blueprint
Date: 2026-07-25
Status: Blueprint — implementation contract for Sprints 17.2–17.8. No code changed by this document.

For each surface: state name, visible UI, available interactions, disabled interactions, feedback, exit conditions.

---

## 1. Editor shell

| State | Visible UI | Available interactions | Disabled interactions | Feedback | Exit condition |
|---|---|---|---|---|---|
| Loading | Skeleton/spinner shell, Header visible with project title if known | None (all panels inert) | All editing interactions | Loading indicator in place of panel content | Runtime adapter resolves initial snapshot → Ready |
| Ready (empty project) | Full shell, empty-state copy in Asset Panel / Manual Timeline / AI Timeline (W8) | Import Media, resize/collapse panels | Clip-targeted actions (trim/split/delete — nothing to target) | Empty-state copy explaining next step | User imports an asset → Ready (populated) |
| Ready (populated) | Full shell, real content in all panels | All standard editing/review interactions | None beyond per-surface rules below | Standard | User navigates away / closes project |
| Saving / sync in progress | Header shows saving indicator in place of "Saved ✓" | All editing interactions remain available (non-blocking) | None | Header status text/icon change only | Save resolves → Ready, or fails → Error |
| Error (adapter/runtime failure) | Error banner in Header or shell-level fallback | Retry action | All editing interactions until retried successfully | Explicit error message, never silent | Retry succeeds → Ready; unresolved → stays in Error |

## 2. Preview

| State | Visible UI | Available interactions | Disabled interactions | Feedback | Exit condition |
|---|---|---|---|---|---|
| Idle (paused) | Full chrome visible, frame at current playhead | Play, scrub, volume, fullscreen toggle | — | Standard | Play pressed → Playing |
| Playing | Chrome begins idle-dim after timeout (17.3 scope) | Pause, scrub, volume | — | Playhead advances; chrome dims after idle period | Pause pressed / scrub interaction → Idle |
| Scrubbing | Chrome fully visible, frame updates live | Release to seek | Play (until released) | Frame updates in real time with drag position | Pointer released → Idle at new position |
| No content (empty project) | Placeholder frame / "Drop source video here" (W8) | Import Media | Play, scrub, volume | Empty-state placeholder, no transport controls implied as functional | Asset inserted onto timeline → Idle |
| Buffering/loading frame | Loading indicator over canvas | None (transport disabled while loading) | Play, scrub | Spinner/indicator, never a frozen blank frame with no explanation | Frame loads → Idle or Playing (whichever preceded) |

## 3. Manual Timeline

| State | Visible UI | Available interactions | Disabled interactions | Feedback | Exit condition |
|---|---|---|---|---|---|
| Idle | Tracks/clips rendered at current zoom/scroll | Select, drag, trim, split, zoom, scroll, paste | — | Standard | Any gesture begins → corresponding active state |
| Clip selected | Selected clip shows outline treatment (P14) distinct from hover/locked/disabled | Drag, trim, split, delete, copy, all standard ops on selection | — | Selection outline; Inspector Properties tab opens | Deselect (click empty area) → Idle; selection target removed → Idle (P34) |
| Dragging | Drag cursor, ghost/preview of new position, snap-guide line if a snap candidate exists (existing Magnetic Snap Engine output) | Release to commit, Escape to cancel (if supported by Drag runtime) | Other timeline gestures until drag ends | Live position feedback, snap indicator | Pointer released → Idle (position committed) or cancelled |
| Trimming | Trim cursor on clip edge, live duration feedback | Release to commit | Other gestures until trim ends | Live duration/time feedback | Pointer released → Idle |
| Multi-select | Multiple clips show selected-outline treatment | Batch operations supported by Selection Runtime | Single-clip-only operations, if any | Multiple outlines simultaneously | Deselect or new single click → Idle/Clip selected |
| Empty (no clips) | Empty track lanes, ready-to-receive styling | Paste, drag-insert from Asset Panel | Clip-targeted operations | Empty-lane placeholder, not blank/broken-looking | First clip inserted → Idle |

## 4. AI Decision (AI Timeline block + Decision lifecycle)

| State | Visible UI | Available interactions | Disabled interactions | Feedback | Exit condition |
|---|---|---|---|---|---|
| Draft / pending | Block shown with pending treatment (`--ce-decision-draft`) | Accept, Reject, Explain, Regenerate | Pin (until accepted, if runtime-defined that way) | Reason tooltip available | Accept/Reject/Regenerate invoked → Processing |
| Processing | Block shown with processing treatment (`--ce-decision-processing`), spinner/indicator | Cancel, if supported | Accept/Reject/Regenerate (already in flight) | Explicit processing indicator, never silent | Adapter resolves → Applied/Accepted/Rejected/Error, or no adapter → Pending Runtime |
| Applied / Accepted | Block shown with accepted treatment (`--ce-decision-accepted`) | Reject (undo the acceptance, if runtime-defined), Pin, Explain | Accept (already accepted) | Confirmation treatment | Underlying decision changes → Stale; user rejects → Rejected |
| Rejected | Block shown with rejected treatment (`--ce-decision-rejected`), dimmed | Regenerate, Accept (reconsider) | — | Dimmed/muted visual | Regenerate/Accept invoked → Processing |
| Stale | Block shown with stale treatment (`--ce-decision-stale`) | Regenerate, Accept anyway, Dismiss | — | Explicit "this decision may no longer reflect current edits" indicator | Regenerate → Processing; Dismiss → Rejected/removed |
| Error | Block shown with error treatment (`--ce-decision-error`) | Retry | Accept/Reject (until retried) | Explicit error message | Retry succeeds → Draft/Processing; still failing → stays Error |
| Disabled (no adapter / Pending Runtime) | Block shown with disabled treatment (`--ce-decision-disabled`), action buttons present but clearly non-final | Attempt action (surfaces "Pending Runtime" honestly) | Nothing hard-blocked, but no action produces a real backend effect | "Pending Runtime" indicator on any attempted action (P36) | Adapter becomes connected (future) → Draft/pending behaves normally |
| Manual override | Block shown with manual treatment (`--ce-decision-manual`) — user edited the underlying clip directly, bypassing AI | Same as Applied, plus indication the current state diverges from the original AI suggestion | — | Distinct manual-origin visual marker | Any further AI action on this decision → Processing |

## 5. Inspector

| State | Visible UI | Available interactions | Disabled interactions | Feedback | Exit condition |
|---|---|---|---|---|---|
| No selection | "No selection" empty state per active tab | Switch tabs | All selection-dependent actions | Explicit empty-state copy, never blank panel | A selection is made on Manual Timeline or AI Timeline → corresponding populated state |
| Properties (clip selected) | Clip properties (duration, speed, etc.) and clip-targeted actions | Trim, split, adjust properties (as supported by runtime) | N/A | Standard | Selection changes/clears → No selection or new Properties |
| AI Copilot (contextual) | Suggestions relevant to current selection/time range | Invoke suggestion (routes through existing action boundary; Pending Runtime if unconnected) | N/A | Pending Runtime indicator per P36 where applicable | Selection changes → suggestions refresh |
| Decision (AI decision selected) | Decision detail matching AI Timeline's `selectedBlockId` lifecycle state | Accept/Reject/Regenerate/Pin/Explain (mirrors AI Timeline state table above) | Per lifecycle state above | Mirrors AI Decision state feedback | `selectedBlockId` cleared/changes → updates or returns to No selection |
| Stale selection fallback | Whichever tab is active shows its own empty state | Switch tabs, make new selection | Selection-dependent actions for the stale target | Explicit fallback, not broken/frozen data (P34) | New valid selection made |

## 6. AI Director

| State | Visible UI | Available interactions | Disabled interactions | Feedback | Exit condition |
|---|---|---|---|---|---|
| Idle | Input field empty, context indicator shows current selection/time-range context | Type command, focus input | — | Context indicator always present (P25) | User submits → Submitted |
| Composing | Input field has text | Submit, clear, continue typing | — | Standard text input feedback | Submit → Submitted; clear → Idle |
| Submitted / pending acknowledgment | Input clears or shows submitted command, awaiting result | Cancel (if supported) | Resubmitting same command until acknowledged | Visible "processing" indicator | Result resolves → Applied / Pending Runtime / Unsupported |
| Applied | Confirmation that the command's effect was applied, context indicator updates if selection/state changed as a result | Compose next command | — | Explicit "applied" confirmation (P26) | New command typed → Composing |
| Pending Runtime | Confirmation that AI understood the command but no backend execution occurred (W9) | Compose next command | — | Explicit "Pending Runtime" indicator (P36) | New command typed → Composing |
| Unsupported / misunderstood | Explicit message that the command could not be interpreted or is out of scope | Compose next command, view suggestions if offered | — | Explicit, never a silent no-op | New command typed → Composing |
