# Frontend Responsive Desktop System

Sprint 17.1 — Frontend Audit & Design System
Date: 2026-07-25

Desktop-only. Mobile editor support is explicitly out of scope for this and every subsequent sprint in this program.

## Target viewports

| Viewport | Class | Status today |
|---|---|---|
| 1920×1080 | Primary/large | Verified (Desktop Editor) |
| 1600×900 | Comfortable | Verified (Desktop Editor) |
| 1440×900 | Standard | Verified (Desktop Editor) |
| 1366×768 | Minimum supported | Verified (Desktop Editor); **not yet verified** on any legacy (`DashboardShell`) page |

## Collapse priority (applies at any width where the Editor's fixed-width chrome would otherwise overflow)

1. **Compact secondary labels** — Tool Rail switches to compact mode (icon-only, 48px vs. 64px) first; AI Timeline/Asset Panel drop secondary metadata text (e.g. asset filenames stay, durations may hide) before any panel resizes.
2. **Asset Panel narrows** — down to its documented minimum (`--ce-dim-asset-panel-min`, 280px) before collapsing.
3. **Asset Panel collapses** — to its 40px slim strip (existing `CollapsiblePanel` pattern) once narrowing alone isn't enough.
4. **Inspector narrows** — down to its minimum (`--ce-dim-inspector-min`, 300px).
5. **Inspector collapses** — to its 40px slim strip, same pattern as Asset Panel.

Preview and Timeline are never candidates for narrowing/collapsing — they are the floor of the collapse priority, matching design direction principle 1 (Preview and Timeline lead visual hierarchy).

## Verified minimum-width math (Desktop Editor)

Worst case — every resizable panel pulled to maximum simultaneously:

```
Tool Rail (fixed) 64 + Asset Panel (max) 320 + divider 6 + divider 6 + Inspector (max) 340 = 736px
```

At 1366×768 (smallest supported width): `1366 − 736 = 630px` remaining for Preview + Timeline area — comfortably usable. This was established and verified in Sprint 16.10.6.1 and re-confirmed here; the token foundation in this sprint does not change any of these pixel values (see `frontend-design-system.md` §Editor dimensions, which encodes the same numbers as tokens rather than introducing new ones).

## What still needs first-time verification (not done in 17.1, scheduled below)

- `/`, `/workspace`, `/upload`, `/productions`, `/ai-queue`, `/styles`, `/settings` — the fixed 256px `Sidebar` plus unconstrained content grids have never been checked at any of the four target widths. Risk is concentrated in stat-card rows and the asset/production grids, which may use fixed column counts rather than `minmax()`/`auto-fill`.
- **Scheduled:** first-time verification lands with each surface's own redesign sprint (17.9 for Workspace/Projects/Upload, 17.10 for Export/Settings/Templates), full sweep confirmation in **17.11**.

## Behavioral rules for 17.2+ implementers

- Preview and Timeline must remain usable (not just "not zero-width") at every target viewport — "usable" means the portrait preview retains a legible aspect ratio and the timeline retains enough vertical space to show at least one full track row plus the ruler.
- Header actions (Undo/Redo/History/Refresh/Share/Export) remain accessible at every width — never hidden behind an overflow menu as the *first* response to width pressure; the collapse priority above (steps 1–5) must be exhausted first, since those panels are lower-value than always-visible primary actions.
- No horizontal overflow at the application level at any target width — this was true of the Desktop Editor before this sprint and remains a hard requirement for every surface as it's redesigned.
- Any new responsive logic must reuse the existing `ResizeObserver`/rAF-throttling pattern already proven in `TimelineViewportContext` and `DesktopGrid` — no new, uncoordinated observer per surface (see Performance risks in the master plan).
