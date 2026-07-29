# Frontend Design System — AI Clip Agent

Sprint 17.1 — Frontend Audit & Design System
Date: 2026-07-25
Status: Tokens implemented in `frontend/src/app/globals.css` this sprint (foundation only — see §Implementation). Component/editor standards below are **documented standards for 17.2+ to apply**, not a wholesale primitive rewrite.

Companion documents: `frontend-architecture-audit.md`, `frontend-ux-visual-audit.md`, `frontend-design-direction.md`, `frontend-responsive-system.md`, `frontend-accessibility-system.md`, `frontend-redesign-master-plan.md`.

This is **one semantic token system**, not a fourth theme. It supersedes the need for `--review-*`/`--desktop-editor-*`/`--ai-timeline-*` to diverge further; those three keep working today via alias (see §Implementation) until each surface migrates in a later sprint.

---

## Task 4 — Semantic design tokens

All tokens live under one root scope, `--ce-*` ("Clip Editor"), defined once in `globals.css` and available everywhere (no per-feature theme class required to read them, unlike the three legacy scopes).

### Color — background

| Token | CSS variable | Value | Use |
|---|---|---|---|
| `background.app` | `--ce-bg-app` | `#0b0d12` | The outermost app canvas, one step darker than any panel |
| `background.workspace` | `--ce-bg-workspace` | `#0f1115` | Workspace/project-browser background (one step lighter than app) |
| `background.panel` | `--ce-bg-panel` | `#14161c` | Primary panel surface (Tool Rail, Asset Panel, Inspector, Timeline Workspace, Header, Status Bar) |
| `background.panelRaised` | `--ce-bg-panel-raised` | `#181b22` | Cards/rows/popovers raised one step above a panel |
| `background.canvas` | `--ce-bg-canvas` | `#070910` | Preview/Timeline drawing surfaces — the darkest, quietest background in the app (supports design direction principle 1) |
| `background.overlay` | `--ce-bg-overlay` | `rgb(10 11 15 / 72%)` | Modal/dialog scrim |

### Color — border

| Token | CSS variable | Value |
|---|---|---|
| `border.subtle` | `--ce-border-subtle` | `rgb(151 164 190 / 8%)` |
| `border.default` | `--ce-border-default` | `rgb(151 164 190 / 14%)` |
| `border.strong` | `--ce-border-strong` | `rgb(166 180 207 / 22%)` |
| `border.focus` | `--ce-border-focus` | `var(--ce-accent-primary)` |

### Color — text

| Token | CSS variable | Value |
|---|---|---|
| `text.primary` | `--ce-text-primary` | `#f4f6fb` |
| `text.secondary` | `--ce-text-secondary` | `#a8b0c1` |
| `text.muted` | `--ce-text-muted` | `#6f7887` |
| `text.disabled` | `--ce-text-disabled` | `#4d5566` |
| `text.inverse` | `--ce-text-inverse` | `#0b0d12` (for text on solid accent-colored fills) |

### Color — accent

| Token | CSS variable | Value |
|---|---|---|
| `accent.primary` | `--ce-accent-primary` | `#7c5cff` |
| `accent.primaryHover` | `--ce-accent-primary-hover` | `#8d73ff` |
| `accent.primaryActive` | `--ce-accent-primary-active` | `#6c4aef` |
| `accent.soft` | `--ce-accent-soft` | `rgb(124 92 255 / 14%)` |

### Color — state

| Token | CSS variable | Value |
|---|---|---|
| `state.selected` | `--ce-state-selected` | `var(--ce-accent-soft)` |
| `state.hover` | `--ce-state-hover` | `rgb(151 164 190 / 10%)` |
| `state.focus` | `--ce-state-focus` | `var(--ce-accent-primary)` |
| `state.processing` | `--ce-state-processing` | `#f8c76e` |
| `state.success` | `--ce-state-success` | `#65dfa9` |
| `state.warning` | `--ce-state-warning` | `#f8c76e` |
| `state.error` | `--ce-state-error` | `#ff819d` |
| `state.disabled` | `--ce-state-disabled` | `var(--ce-text-disabled)` (paired with `--ce-opacity-disabled: 0.45` applied to the element) |

### Color — timeline (domain-specific, deliberately distinct hues per design direction principle 4)

| Token | CSS variable | Value |
|---|---|---|
| `timeline.video` | `--ce-timeline-video` | `#6654d9` |
| `timeline.audio` | `--ce-timeline-audio` | `#218a63` |
| `timeline.subtitle` | `--ce-timeline-subtitle` | `#bd7a26` |
| `timeline.broll` | `--ce-timeline-broll` | `#207f9c` |
| `timeline.ai` | `--ce-timeline-ai` | `#a855f7` |
| `timeline.playhead` | `--ce-timeline-playhead` | `#ff557d` |
| `timeline.selection` | `--ce-timeline-selection` | `rgb(124 92 255 / 28%)` |

### Color — AI decision lifecycle

| Token | CSS variable | Value | Notes |
|---|---|---|---|
| `decision.draft` | `--ce-decision-draft` | `var(--ce-text-secondary)` | Neutral — not yet acted on |
| `decision.applied` | `--ce-decision-applied` | `var(--ce-accent-primary)` | Currently in effect |
| `decision.accepted` | `--ce-decision-accepted` | `var(--ce-state-success)` | |
| `decision.rejected` | `--ce-decision-rejected` | `var(--ce-text-muted)` | Dismissed, not an error |
| `decision.disabled` | `--ce-decision-disabled` | `var(--ce-text-disabled)` | |
| `decision.manual` | `--ce-decision-manual` | `var(--ce-timeline-broll)` | Distinct hue: "user took over" is a meaningfully different state from any AI lifecycle state |
| `decision.processing` | `--ce-decision-processing` | `var(--ce-state-processing)` | |
| `decision.stale` | `--ce-decision-stale` | `var(--ce-state-warning)` | |
| `decision.error` | `--ce-decision-error` | `var(--ce-state-error)` | |

### Typography roles

Each role defines size/line-height/weight/letter-spacing as three variables plus one ready-to-use utility class (`.ce-text-{role}`, kebab-case).

| Role | Class | Size | Line-height | Weight | Use |
|---|---|---|---|---|---|
| `display` | `.ce-text-display` | 28px | 1.15 | 600 | Marketing/Workspace hero only — **never inside the Editor** |
| `pageTitle` | `.ce-text-page-title` | 20px | 1.25 | 600 | Non-editor page titles (Workspace, Settings) |
| `panelTitle` | `.ce-text-panel-title` | 13px | 1.3 | 600 | Editor panel titles (Inspector, Asset Panel) |
| `sectionTitle` | `.ce-text-section-title` | 11px | 1.3 | 600, uppercase, `0.08em` tracking | Section headings inside a panel |
| `body` | `.ce-text-body` | 13px | 1.5 | 400 | Default reading text |
| `bodyCompact` | `.ce-text-body-compact` | 11px | 1.4 | 400 | Dense list rows, card descriptions |
| `label` | `.ce-text-label` | 11px | 1.3 | 500 | Form labels, toolbar labels |
| `metadata` | `.ce-text-metadata` | 10px | 1.3 | 500 | Timestamps, counts, secondary metadata |
| `caption` | `.ce-text-caption` | 10px | 1.4 | 400 | Helper/description text under a control |
| `timelineLabel` | `.ce-text-timeline-label` | 9px | 1.2 | 500 | Track labels, ruler marks |
| `button` | `.ce-text-button` | 12px | 1 | 600 | Button labels |
| `input` | `.ce-text-input` | 12px | 1.4 | 400 | Form field text |
| `code` | `.ce-text-code` | 11px | 1.4 | 400, `--font-geist-mono` | Technical/id values (revision numbers, clip ids) |

### Spacing scale

| Token | Variable | Value |
|---|---|---|
| `2xs` | `--ce-space-2xs` | 2px |
| `xs` | `--ce-space-xs` | 4px |
| `sm` | `--ce-space-sm` | 8px |
| `md` | `--ce-space-md` | 16px |
| `lg` | `--ce-space-lg` | 24px |
| `xl` | `--ce-space-xl` | 32px |
| `2xl` | `--ce-space-2xl` | 48px |

### Editor dimensions

| Token | Variable | Value | Source |
|---|---|---|---|
| Header height | `--ce-dim-header-height` | 48px | Current Desktop Editor header (`h-12`) |
| Tool Rail width (expanded) | `--ce-dim-tool-rail-width` | 64px | 16.10.6.1 target |
| Tool Rail width (compact) | `--ce-dim-tool-rail-width-compact` | 48px | Current implementation |
| Asset Panel min/default/max | `--ce-dim-asset-panel-min` / `-default` / `-max` | 280 / 300 / 320px | 16.10.6.1 target |
| Inspector min/default/max | `--ce-dim-inspector-min` / `-default` / `-max` | 300 / 320 / 340px | 16.10.6.1 target |
| Timeline toolbar height | `--ce-dim-timeline-toolbar-height` | 40px | Matches control-height-lg |
| Track height (expanded) | `--ce-dim-track-height` | 40px | Current AI Timeline track row |
| Track height (collapsed) | `--ce-dim-track-height-collapsed` | 24px | Current AI Timeline collapsed row |
| AI Timeline height (min/default/max) | `--ce-dim-ai-timeline-height-min` / `-default` / `-max` | 110 / 140 / 150px | Target range |
| Control height sm/md/lg | `--ce-dim-control-height-sm` / `-md` / `-lg` | 28 / 32 / 40px | |
| Icon size sm/md | `--ce-icon-size-sm` / `-md` | 14 / 16px | |

### Radius scale

| Token | Variable | Value |
|---|---|---|
| sm | `--ce-radius-sm` | 8px — controls, inputs, small buttons |
| md | `--ce-radius-md` | 12px — panels, cards |
| lg | `--ce-radius-lg` | 16px — modals, large surfaces |
| pill | `--ce-radius-pill` | 999px — badges, pills |

### Elevation scale

| Token | Variable | Value |
|---|---|---|
| panel | `--ce-shadow-panel` | `0 12px 32px rgb(0 0 0 / 24%)` |
| floating | `--ce-shadow-floating` | `0 24px 80px rgb(0 0 0 / 42%)` |
| accent | `--ce-shadow-accent` | `0 8px 24px rgb(91 60 224 / 28%)` |

### Motion

| Token | Variable | Value |
|---|---|---|
| Duration fast | `--ce-motion-duration-fast` | 120ms — hover/focus feedback |
| Duration base | `--ce-motion-duration-base` | 180ms — panel/tab transitions |
| Duration slow | `--ce-motion-duration-slow` | 280ms — panel resize/collapse |
| Easing standard | `--ce-motion-easing-standard` | `cubic-bezier(0.2, 0, 0, 1)` |
| Easing decelerate | `--ce-motion-easing-decelerate` | `cubic-bezier(0, 0, 0, 1)` |
| Easing accelerate | `--ce-motion-easing-accelerate` | `cubic-bezier(0.3, 0, 1, 1)` |

`prefers-reduced-motion: reduce` disables all of the above app-wide in one rule (see §Implementation) — fixing the gap identified in the UX audit (previously only `.review-editor-theme` was covered).

---

## Task 5 — Component design standards

These are **standards to apply as each primitive is touched in 17.2+**, mapping today's fragmented implementations (`components/ui/*`, `features/review/design-system`, ad hoc Desktop Editor components) onto one spec. Per the sprint's explicit instruction: **audit → map → consolidate → add missing variants** — no wholesale replacement in 17.1.

| Component | Variants | Sizes | States | A11y | Keyboard | Icon rule | Loading | Disabled |
|---|---|---|---|---|---|---|---|---|
| **Button** | primary / secondary / ghost / danger | sm(28) / md(32) / lg(40) | default, hover, active, focus, disabled, loading | `aria-disabled` when loading | Enter/Space activates | Leading icon only, `--ce-icon-size-sm` | Spinner replaces label, width preserved | `opacity: var(--ce-opacity-disabled)`, `pointer-events: none` |
| **IconButton** | primary / secondary / ghost / danger | sm/md/lg (square, same heights as Button) | same as Button | **`aria-label` required**, `title` recommended | Enter/Space | icon only, centered | spinner replaces icon | same as Button |
| **ToggleButton** | default | sm/md | off / on / disabled | `aria-pressed` | Enter/Space toggles | optional leading icon | n/a | dims + `pointer-events: none` |
| **SegmentedControl** | default | sm/md | per-segment selected/hover/disabled | `role="radiogroup"`, segments `role="radio"`/`aria-checked` | Arrow keys move selection, Enter/Space selects | optional per-segment icon | n/a | per-segment disabled |
| **Tabs** | underline (current pattern) / pill | sm/md | active (strong: `border-b-2 accent-primary` or filled pill), inactive, hover, disabled | `role="tablist"`/`role="tab"`/`aria-selected`/`aria-controls` | Arrow keys move focus, Enter/Space activates | optional leading icon | n/a | tab hidden or disabled+`aria-disabled` |
| **TextInput** | default / error | sm/md | default, focus (`border-focus` + `ring`), error, disabled | `<label>` association, `aria-invalid` on error | standard text input | none | n/a | `opacity` + `cursor-not-allowed` |
| **SearchInput** | default | sm/md | default, focus, has-value (shows clear button) | `aria-label` when no visible label | Escape clears (when focused, per Accessibility System) | leading search icon + optional trailing clear | n/a | disabled |
| **Select** | default | sm/md | default, focus, disabled, open | native `<select>` or a `role="listbox"` custom impl — prefer native unless a custom trigger is required | Arrow keys navigate options (native handles this for free) | optional leading icon in trigger | n/a | disabled |
| **Slider** | default | sm/md track height | default, focus, dragging, disabled | `role="slider"`, `aria-valuemin/max/now` | Arrow keys ±step, Home/End to min/max | n/a | n/a | disabled |
| **Checkbox** | default | sm/md | unchecked/checked/indeterminate/focus/disabled | native `<input type="checkbox">` where possible | Space toggles | n/a | n/a | disabled |
| **Switch** | default | sm/md | off/on/focus/disabled | `role="switch"`/`aria-checked` | Space/Enter toggles | n/a | n/a | disabled |
| **Tooltip** | default | — | shown/hidden, **edge-clamped** (pattern already proven in `AiTooltip`) | `role="tooltip"`, referenced via `aria-describedby` | shows on focus as well as hover; Escape dismisses | n/a | n/a | n/a |
| **Popover** | default | — | open/closed | `role="dialog"` (non-modal) or native `popover` attribute where supported | Escape closes, focus returns to trigger | n/a | n/a | n/a |
| **DropdownMenu** | default | — | open/closed, item hover/active/disabled | `role="menu"`/`role="menuitem"` (pattern already proven in AI Timeline's context menu) | Arrow keys navigate, Enter/Space activates, Escape closes | optional per-item leading icon | n/a | per-item disabled |
| **Dialog** | default / danger (confirm) | sm/md/lg | open/closed | `role="dialog"` + `aria-modal="true"` (pattern already proven in `AiRegenerateDialog`), labelled via `aria-label` | **focus trapped inside while open**, Escape closes, focus returns to trigger on close | n/a | n/a | action buttons follow Button disabled rule |
| **Sheet** | left/right/bottom slide-in | — | open/closed | same as Dialog | same as Dialog | n/a | n/a | same as Dialog |
| **Badge** | neutral/brand/info/success/warning/danger | sm/md | static (non-interactive) | decorative unless conveying otherwise-unavailable info (then needs text, not color alone) | n/a | optional leading dot | n/a | n/a |
| **StatusBadge** | one per lifecycle/decision state (§Tokens) | sm | static | text label always accompanies color (never color-only) | n/a | optional state icon | n/a | n/a |
| **SectionHeader** | default | — | static | heading semantics (`<h2>`/`<h3>` as appropriate to nesting) | n/a | optional trailing action | n/a | n/a |
| **PanelHeader** | default, sticky | — | static | landmark-appropriate heading | n/a | optional leading icon + trailing actions | n/a | n/a |
| **EmptyState** | default | — | static | icon is `aria-hidden`, message is real text | n/a | centered icon well | n/a | n/a |
| **LoadingState** | inline spinner / full-panel / skeleton | — | static | `aria-live="polite"` region announces when content resolves (see Accessibility System) | n/a | n/a | is the loading treatment itself | n/a |
| **ErrorState** | inline / full-panel | — | static, optional retry action | `role="alert"` for the message | Enter/Space on retry button | warning/error icon | n/a | n/a |
| **Divider** | horizontal/vertical | — | static | `role="separator"` if interactive (resizable), otherwise purely decorative (`aria-hidden`) | n/a | n/a | n/a | n/a |
| **ScrollArea** | default (thin scrollbar utility) | — | static | native scroll semantics preserved | native (arrow keys/Page Up/Down when focused) | n/a | n/a | n/a |
| **Toolbar** | grouped (role="group" clusters, pattern proven in Desktop Editor header) | — | per-control states | `role="toolbar"` on the container, `role="group"` per cluster | Arrow-key roving tabindex recommended for dense toolbars (not yet implemented anywhere — flag for 17.5/17.11) | consistent icon size within a toolbar | n/a | per-control disabled |
| **ResizablePanel** | horizontal/vertical (pattern proven: `PanelDivider`/`useLayoutResizer`) | — | default/dragging/focus | `role="separator"`, `aria-valuenow/min/max` (already implemented) | Arrow keys resize, Enter/Space or double-click resets to default (already implemented) | n/a | n/a | n/a |
| **CollapsiblePanel** | left/right/top/bottom collapse direction (pattern proven: `PanelCollapseButton`) | — | expanded/collapsed | button exposes current + resulting state in its `aria-label` (already implemented, e.g. "Collapse asset library"/"Expand asset library") | Enter/Space toggles | direction-matching chevron icon | n/a | n/a |

**Consolidation targets already identified** (map, don't replace yet):
- `Button`/`IconButton`: reconcile `components/ui/button.tsx` (literal Tailwind colors, `rounded-xl` always) with `ReviewButton`/`ReviewIconButton` (tokenized, size-based radius) — the review version is the correct target shape.
- `Badge`: reconcile `components/ui/badge.tsx` (Tailwind palette tones) with `ReviewBadge` (tokenized tones) — same tone names exist in both (neutral/info/success/warning/danger) with different color sources; unify on tokens.
- `EmptyState`/`LoadingState`: reconcile `components/ui/*` (untokenized, `rounded-3xl`) with `ReviewEmptyState`/`ReviewSkeleton` (tokenized) and AI Timeline's bespoke inline empty-state text (no shared component at all) — one primitive, three current call sites to migrate later.
- `Toolbar`: `ReviewToolbarGroup` already matches the target shape; Desktop Editor's header groups (`role="group"`) should adopt the same primitive rather than re-implementing it ad hoc.

---

## Task 6 — Editor-specific design standards

### Tool Rail
- Width: `--ce-dim-tool-rail-width` (expanded) / `-compact`. Background: `--ce-bg-panel`. Active tool: `--ce-state-selected` fill + `--ce-accent-primary` icon/text. Collapse affordance: `CollapsiblePanel` standard.

### Asset Panel
- Width: `--ce-dim-asset-panel-*`. Background: `--ce-bg-panel`; asset cards: `--ce-bg-panel-raised`. Selected asset: `--ce-state-selected` border (not fill, to keep the thumbnail legible). Density: two-column grid, thumbnail-dominant (already established in 16.10.6.1) — carried forward unchanged.

### Preview
- Canvas background: `--ce-bg-canvas` (the darkest token in the system — supports "Preview leads hierarchy" via near-zero chrome contrast against the video itself). Chrome (toolbar, transport bar) uses `--ce-bg-overlay`-style translucency so it recedes when not hovered (ties to UX audit F4 — full idle-dim treatment is a 17.3 implementation task, this is the token it will use).

### Timeline (Manual)
- **Owned by Timeline Runtime — this section documents target visual values for a future, separately-approved styling pass, not a change made now.**
  - Track header: `--ce-bg-panel`, separated from canvas by `--ce-border-default` (one border, not a border-per-lane).
  - Track canvas: `--ce-bg-canvas`, ruler ticks in `--ce-text-muted`.
  - Clip colors: `--ce-timeline-video`/`-audio`/`-subtitle`/`-broll`.
  - Selected clip: `--ce-state-selected` fill + `--ce-accent-primary` 2px border.
  - Locked clip: reduced-opacity fill + a lock glyph, never color alone.
  - Disabled clip: `--ce-state-disabled` treatment, matching AI Timeline's disabled block styling for consistency between manual and AI-authored clips.
  - Drag preview: semi-transparent ghost of the clip at `--ce-accent-soft`.
  - Trim handles: `--ce-accent-primary` on hover/active, invisible otherwise (revealed on clip hover).
  - Playhead: `--ce-timeline-playhead`, full-height, 1–2px.
  - Snap guides: `--ce-accent-primary` thin line, appears only during an active drag/trim.
  - Empty tracks: `--ce-bg-canvas` with a faint `--ce-text-muted` "no clips" watermark, not a bordered empty-state card (would be too heavy for a track row).
  - Toolbar grouping (History/Edit/Clipboard/View): **documented target, not implementable without a separately-approved Timeline Runtime exception** — see UX audit F9.

### AI Timeline
- Decision type: icon (already implemented, `TRACK_ICON` map) + category color (`--ce-timeline-ai` family / the existing 10-color decision-type palette, which stays a deliberate multi-hue exception per design direction principle 4).
- Confidence: shown as `NN%` text when block width ≥ the existing `CONFIDENCE_WIDTH_THRESHOLD` (92px) — already implemented, carried forward.
- Lifecycle status: maps to `decision.*` tokens (§Tokens) — every state (processing/regenerating/disabled/stale/selected/hovered/pinned/normal) gets a token-driven treatment that must remain legible even at the icon-only compact tier (fixes UX audit F6 — e.g. a small corner dot in the state color, visible regardless of block width).
- Narrow block behavior: icon-only below `COMPACT_WIDTH_THRESHOLD` (30px) — already implemented, carried forward, now paired with the compact-safe lifecycle indicator above.
- Selection: `--ce-state-selected`, synchronized bidirectionally with real timeline clip selection (already implemented via `TimelineViewportContext`) — unchanged.
- Tooltip: edge-clamped (already implemented) — becomes the canonical `Tooltip` primitive pattern (§Task 5).
- Search: highlights matches, dims non-matches, centers+flashes the first match on Enter (already implemented) — carried forward.
- Filters: chip-based, `--ce-accent-soft` when active (already implemented) — carried forward.
- Empty state: uses the canonical `EmptyState` primitive once consolidated (§Task 5), replacing today's bespoke inline message.

### Inspector
- Tabs: `Tabs` standard (§Task 5), underline variant (current pattern), strong active state via `--ce-accent-primary` 2px underline.
- Sticky panel header (tab bar) — already the structural pattern (tab bar outside the scroll container); formalize as the standard, not an accident of layout.
- Consistent section spacing: `--ce-space-md` between sections, `--ce-space-sm` within a section — applied identically across Properties/AI Copilot/Decision (fixes UX audit F7).
- Compact scrollbar: the existing `.desktop-editor-scroll` utility, generalized to `.ce-scroll` (§Implementation).
- Sticky bottom actions: AI Director's command input (already sticky) is the reference pattern for any tab needing a persistent bottom action.

### AI Director
- Reuses `ReviewAICommandBar` verbatim (Review Runtime, natural-language command boundary) — no visual fork. Only the surrounding chrome (label, section spacing, sticky positioning) is a design-system concern.
