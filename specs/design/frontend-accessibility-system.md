# Frontend Accessibility System

Sprint 17.1 — Frontend Audit & Design System
Date: 2026-07-25

This sprint **defines** the accessibility standard below and fixes the one gap that's pure CSS (reduced-motion coverage, §Implementation). Component-level accessibility work (auditing every icon-only button across every surface, adding roving-tabindex to toolbars, etc.) is scheduled into 17.2–17.11 as each surface is touched — not done wholesale in 17.1.

**Hard constraint carried from every prior sprint and restated here: no existing editor keyboard shortcut is removed, remapped, or reinterpreted by this or any future sprint in this program without explicit separate approval.** Keyboard Runtime (`features/review/keyboard`, `use-runtime-keyboard-editing.ts`) is authoritative and untouched.

## Keyboard navigation

- Standard tab order follows DOM order; the Desktop Editor's docking grid (header → rail → assets → preview → inspector → timeline → status bar) already reads in a sensible visual/logical order and is preserved.
- Dense toolbars (Timeline toolbar, Tool Rail, AI Timeline filter chips) should adopt a **roving-tabindex** pattern (one tab stop per group, arrow keys move within it) once touched by a redesign sprint — not implemented anywhere today; flagged for 17.5 (Timeline)/17.11 (sweep), not retrofitted in 17.1.
- All existing Review/Timeline keyboard shortcuts (undo/redo, clipboard, clip nudge, etc., owned by Keyboard Runtime) are unaffected by anything in this document.

## Focus rings

- One token: `--ce-border-focus` / `--ce-state-focus` (both alias `--ce-accent-primary`), applied via `:focus-visible` (never bare `:focus`, to avoid showing rings on mouse clicks) — matches the existing `ReviewButton`/`ReviewIconButton` convention (`focus-visible:ring-2 focus-visible:ring-[var(--review-focus)]`), now generalized app-wide.
- Focus rings must remain visible against every background token (`--ce-bg-app` through `--ce-bg-canvas`) — the accent purple at full opacity against the darkest canvas background already passes a basic contrast check; a full WCAG contrast sweep is scheduled for 17.11.

## Tab semantics

- Every tab strip (Inspector's Properties/AI Copilot/Decision, Asset Panel's collection chips) should expose `role="tablist"`/`role="tab"`/`aria-selected"`/`aria-controls` once consolidated onto the shared `Tabs` primitive (§Design System Task 5). Today's implementation uses `aria-pressed` buttons, which is a functional but non-canonical pattern — flagged for correction when each tab strip is next touched, not retrofitted blindly in 17.1 (per the "do not blindly rewrite" constraint).

## Menu semantics

- Context menus (AI Timeline's right-click menu) and dropdown menus (Asset Panel's "More" collections menu) already use `role="menu"`/`role="menuitem"` — this is the correct, canonical pattern and becomes the standard for every future menu (§Design System `DropdownMenu`).

## Dialog focus trapping

- `AiRegenerateDialog` already uses `role="dialog"`/`aria-modal="true"` with a backdrop-click-to-close pattern, but **does not yet trap focus** (Tab can currently escape to the underlying page) — this is a real, fixable gap, scheduled for the sprint that next touches that component (17.8, since it's part of AI Copilot/Director's surface) rather than fixed incidentally here.
- Standard going forward: every `Dialog`/`Sheet` traps focus for its lifetime and returns focus to the triggering element on close.

## Escape behavior

- Already correct in: AI Timeline's context menu (backdrop click closes; Escape should be added as an equivalent — same gap as focus trapping, same deferred fix), tooltips (dismiss on mouse-leave/blur).
- Standard going forward: Escape closes the topmost open menu/dialog/popover/tooltip and returns focus to its trigger, without closing anything beneath it.

## Tooltip accessibility

- `AiTooltip` is the reference implementation: `role="tooltip"`, viewport-edge-clamped (already fixed in 16.10.6.1). Gap: it currently only shows on `onMouseEnter`/`onMouseLeave` (hover-only) — keyboard/focus-triggered tooltips are not yet implemented anywhere in the app. Standard: any future `Tooltip` primitive must show on `:focus-visible` of its trigger as well as hover, per §Design System Task 5.

## Icon-only button labels

- Already consistent in Desktop Editor (`HeaderIconButton`, `PanelCollapseButton`, `AiTrackHeader`'s visibility/lock/mute toggles all pass `aria-label`). Not yet verified across legacy pages (`components/ui/*` consumers) — scheduled as a verification sweep in **17.11**, fixed per-surface as each legacy page is rebuilt (17.9/17.10).

## Color contrast

- The `--ce-*` token values are carried over verbatim from the existing, already-shipped `--review-*`/`--desktop-editor-*` palettes (not new colors), so no regression is introduced by this sprint's token work. A full WCAG AA contrast audit across the new unified token set (particularly `--ce-text-muted`/`--ce-text-disabled` against `--ce-bg-canvas`, the darkest background) is scheduled for **17.11**, not performed in 17.1.
- Standard: state must never be communicated by color alone — every colored state (selected/error/processing/decision lifecycle) pairs with a text label, icon, or shape change, per design direction principle 4 and the `StatusBadge` standard.

## Reduced motion

- **Fixed in this sprint**: the existing gap (`prefers-reduced-motion` only covered `.review-editor-theme`) is closed by a single, root-level media query covering all `--ce-motion-*`-driven transitions/animations app-wide (see §Implementation in `frontend-design-system.md`/`globals.css`). Existing `.review-editor-theme`-scoped rule is left in place (harmless overlap) rather than removed, per "do not blindly rewrite."

## Disabled-state clarity

- Standard: disabled state is always `--ce-text-disabled` color + `--ce-opacity-disabled` (0.45) + `cursor: not-allowed` + `pointer-events: none` — never opacity alone (which can be too subtle at low percentages) and never color alone (insufficient for color-blind users). Matches the existing Desktop Editor `HeaderIconButton`/`Button` pattern (`disabled:opacity-40`/`disabled:cursor-not-allowed`), now with a shared token value instead of a magic number.

## Processing announcements

- AI Decision Actions' lifecycle changes (regenerating, processing, error) should be announced via a polite live region (`aria-live="polite"`) so a screen-reader user knows a background action completed — **not implemented today** (the "Pending Runtime" banner and per-decision state pill are visual-only). Scheduled for **17.8** (AI Director & Copilot), since that's where decision-action feedback surfaces most directly to the user.
- Standard: any async action with a visible pending/success/error state gets a paired `aria-live="polite"` (non-urgent) or `"assertive"` (errors only) announcement — never a purely visual toast/badge for a state change the user didn't directly click to see.

## Summary of what's fixed now vs. deferred

| Item | Status in 17.1 |
|---|---|
| Reduced-motion coverage (app-wide) | **Fixed** (CSS token foundation) |
| Focus ring token definition | **Fixed** (token defined; per-component application deferred) |
| Disabled-state token definition | **Fixed** (token defined; per-component application deferred) |
| Dialog focus trapping | Documented gap — fix in 17.8 |
| Escape-to-close on context menus | Documented gap — fix in 17.6/17.8 |
| Keyboard-triggered tooltips | Documented gap — fix in 17.6 (AI Timeline) as the reference implementation |
| Tab semantics (`role="tablist"` etc.) | Documented gap — fix in 17.7 (Inspector) |
| Icon-only button label sweep (legacy pages) | Documented gap — fix in 17.9/17.10, verified in 17.11 |
| Processing announcements (`aria-live`) | Documented gap — fix in 17.8 |
| Full WCAG contrast audit | Documented gap — performed in 17.11 |
| Roving-tabindex for dense toolbars | Documented gap — fix in 17.5/17.11 |
