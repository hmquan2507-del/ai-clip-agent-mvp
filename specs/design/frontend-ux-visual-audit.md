# Frontend UX & Visual Audit

Sprint 17.1 — Frontend Audit & Design System
Date: 2026-07-25
Status: Audit only — no code changed.

Findings are classified **Critical / High / Medium / Low** and each includes current behavior, user impact, root cause, recommended direction, and the future sprint where it should be fixed (per the master plan). Nothing here is fixed in 17.1 except where explicitly noted as "token foundation only."

---

### F1 — Three parallel token systems for one visual intent
**Severity:** Critical
**Current behavior:** `.review-editor-theme`, `.desktop-editor-theme`, `.ai-timeline-theme` each redefine background/surface/border/text/accent colors under different CSS variable prefixes, mostly reusing the same underlying hex values (`#7c5cff` accent, `#f8c76e` warning, `#ff819d` danger, `#65dfa9` success) except AI Timeline's accent (`#a855f7`).
**User impact:** Subtle but real visual inconsistency moving between `/review` and `/editor/:id`; any future global visual change (e.g. adjusting the accent) requires editing three places and risks drift.
**Root cause:** Each feature was built in its own sprint without a shared token layer to consume.
**Recommended direction:** One semantic token namespace (`--ce-*`, defined in `frontend-design-system.md`), applied via an alias-first migration so nothing visually changes until a deliberate cutover.
**Fixed in:** **17.1 (token foundation only — aliasing, not visual cutover)**, full cutover in **17.2**.

---

### F2 — A fourth, un-tokenized legacy visual language
**Severity:** Critical
**Current behavior:** `components/ui/*` and all `DashboardShell`-based pages use literal Tailwind slate/violet/rose/emerald colors, not CSS variables.
**User impact:** These surfaces cannot pick up token changes at all; they look and feel like a different, older product.
**Root cause:** Predates the token-driven pattern established by `features/review/design-system`.
**Recommended direction:** Migrate onto `--ce-*` incrementally, reusing the already-correct shapes in `features/review/design-system/primitives.tsx` as the starting point rather than inventing new primitives.
**Fixed in:** **17.9/17.10** (per-surface, as each legacy page is rebuilt).

---

### F3 — Four routes are non-functional placeholders wearing production chrome
**Severity:** Critical
**Current behavior:** `/productions`, `/ai-queue`, `/styles`, `/settings` render hard-coded arrays with non-wired buttons; `/settings` literally labels its cards "Configuration placeholder."
**User impact:** A user cannot tell these are inert until clicking — actively misrepresents product maturity, and is in direct conflict with the "not a collection of disconnected cards" design constraint.
**Root cause:** Scaffolded early, never completed.
**Recommended direction:** Rebuild for real (even if backed by mock data honestly labeled, matching the "Pending Runtime" pattern already proven in `ai-decision-actions`).
**Fixed in:** **17.9 (Projects)**, **17.10 (Templates, Settings)**.

---

### F4 — Preview does not yet lead visual hierarchy at every viewport
**Severity:** High
**Current behavior:** Preview already got materially larger in 16.10.6.1 (Asset Panel/Inspector narrowed to 280–320/300–340px), but its *visual treatment* (quiet chrome, idle-dim controls) is unimplemented — `EditorPreviewCanvas` has no idle state, and its border/background don't yet read as "the most important thing on screen" versus the surrounding panels.
**User impact:** Preview is appropriately sized but not yet visually prioritized — panels compete with it rather than receding.
**Root cause:** Prior sprints focused on sizing math, not surface-contrast hierarchy.
**Recommended direction:** Preview gets the lowest-noise chrome in the entire shell (minimal border, canvas-dark background, no decorative treatment) so surface *contrast*, not borders, establishes hierarchy — a principle formalized in `frontend-design-direction.md`.
**Fixed in:** **17.3**.

---

### F5 — AI Timeline track spacing and empty space
**Severity:** Medium
**Current behavice:** 10 tracks at fixed 40px/24px (collapsed) row heights inside a 110–150px viewport means only 2–3 tracks are visible without scrolling; empty-state and spacing were addressed in 16.10.6.1 but track density itself wasn't revisited.
**User impact:** Users must scroll within an already-small area to see most AI decision categories.
**Root cause:** Track height/spacing was inherited from the initial visualization sprint (16.10.4) and never re-tuned once real content density was known.
**Recommended direction:** Reconsider default track height, collapse-by-default for low-signal tracks (e.g. Emoji, Story Beat) versus always-expanded high-signal tracks (Hook, AI Cuts, Subtitle).
**Fixed in:** **17.6**.

---

### F6 — AI decision blocks: readability solved for width, not for density
**Severity:** Medium
**Current behavior:** 16.10.6.1 added width-aware compact/confidence rendering tiers (icon-only <30px, icon+title 30–92px, icon+title+confidence ≥92px) — good — but color alone still carries lifecycle state (processing/stale/disabled/selected) without a consistently legible secondary cue (icon or pattern) at the icon-only tier.
**User impact:** At maximum zoom-out (narrow blocks), a stale vs. disabled vs. normal decision may be indistinguishable.
**Root cause:** Lifecycle-state styling was designed for the wider tiers first.
**Recommended direction:** Every lifecycle state needs a treatment that survives icon-only compaction (e.g. a corner indicator or border-style, not just a body-opacity/dash change that a 16px icon-only block can't show).
**Fixed in:** **17.6**.

---

### F7 — Inspector: visually consolidated, not yet hierarchically consistent
**Severity:** Medium
**Current behavior:** Properties/AI Copilot/Decision tabs share a scrollbar utility and softened borders (16.10.6.1) but each still has its own internal spacing rhythm and empty-state design (Properties: flat "coming soon" cards; AI Copilot: sectioned with headings; Decision: a single detail card + action grid + history list).
**User impact:** Switching tabs feels like switching apps, just slightly less than before.
**Root cause:** Three genuinely different data shapes were visually harmonized at the surface level (borders/scrollbar) but not at the layout-rhythm level (section spacing, heading style, empty-state pattern).
**Recommended direction:** One shared `PanelSection`/`EmptyState` primitive used identically by all three tabs, per `frontend-design-system.md` §Component Standards.
**Fixed in:** **17.7**.

---

### F8 — AI Copilot / AI Director: hierarchy present, but Suggestions and Quick Actions look visually equal in weight
**Severity:** Medium
**Current behavior:** Quick Actions (2-col compact chips) and Suggestions (full-width cards) are already differentiated by shape, but both use the same border/background treatment as the Properties placeholder cards — no visual signal that "this is AI-authored content" vs. "this is a static UI section."
**User impact:** Doesn't yet read as "AI is visibly present but not overwhelming" — it reads as "more of the same card list."
**Root cause:** No dedicated AI-content visual treatment exists yet (see design direction principle "AI intelligence is visible but not visually overwhelming").
**Recommended direction:** A restrained, consistent AI-content marker (e.g. a thin accent-colored left rule or a small AI glyph, not a gradient or badge-heavy treatment) applied uniformly to Suggestions, AI Copilot cards, and AI Timeline blocks.
**Fixed in:** **17.8**.

---

### F9 — Toolbar grouping is real in the header, absent in the areas that most need it
**Severity:** Medium
**Current behavior:** 16.10.6.1 grouped the Desktop Editor header's History/View button clusters with `role="group"`. The Manual Timeline's own toolbar (move/split/duplicate/copy/cut/paste/undo/redo) lives entirely inside `ReviewTimelinePanel` (Timeline Runtime) and has no visual grouping at all today.
**User impact:** The busiest, most-used toolbar in the product is the least organized.
**Root cause:** That toolbar is inside a file this program has never been authorized to edit (Timeline Runtime boundary).
**Recommended direction:** Requires an explicit, separately-approved exception to the Timeline Runtime boundary before any visual grouping can be applied there — **not solvable by a styling-only sprint**. Flagged clearly rather than silently worked around.
**Fixed in:** **Not scheduled** — requires a future, explicitly-approved runtime-boundary exception; tracked as a known limitation in every relevant sprint until then.

---

### F10 — Spacing consistency
**Severity:** Medium
**Current behavior:** Desktop Editor already standardized on an 8/16/24/32px scale (`--desktop-editor-space-*`), but legacy pages use ad hoc Tailwind spacing (`p-6`, `p-8`, `gap-3`, `gap-4`, `gap-6` inconsistently) with no shared scale reference.
**User impact:** Minor visual unevenness when navigating between old and new surfaces.
**Root cause:** No shared spacing tokens existed before the Desktop Editor sprints.
**Recommended direction:** Adopt the `--ce-space-*` scale (2xs/xs/sm/md/lg/xl) app-wide.
**Fixed in:** **17.1 (tokens defined)**, applied per-surface in 17.2–17.10.

---

### F11 — Border usage is heavier than necessary
**Severity:** Medium
**Current behavior:** Even after 16.10.6.1's border-softening pass, most panels/cards still default to a visible 1px border rather than relying on surface-color contrast to separate regions.
**User impact:** Visual noise, works against the "surface contrast before borders" principle.
**Root cause:** Border-first separation is the default Tailwind authoring pattern; no prior sprint challenged it structurally, only softened opacity.
**Recommended direction:** Prefer `background` contrast between adjacent surfaces (app/panel/raised) as the primary separator; reserve visible borders for interactive/focus/selected states only.
**Fixed in:** **17.2** (Desktop Editor shell), then per-surface.

---

### F12 — Typography has no documented scale
**Severity:** Medium
**Current behavior:** At least 8 distinct font sizes are in ad hoc use across the Desktop Editor alone (9px/9.5px/10px/10.5px/11px/12px/13px+), each chosen per-component with no shared role names.
**User impact:** No user-visible bug today, but makes every future component inconsistent by default and slows down design decisions.
**Root cause:** No type scale was ever defined.
**Recommended direction:** The 12-role type scale in `frontend-design-system.md` (display/pageTitle/panelTitle/sectionTitle/body/bodyCompact/label/metadata/caption/timelineLabel/button/input/code).
**Fixed in:** **17.1 (defined + utility classes added)**, applied per-surface thereafter.

---

### F13 — Icon consistency
**Severity:** Low
**Current behavior:** `lucide-react` is used exclusively (good, no fragmentation), but icon sizing varies (`size-3`, `size-3.5`, `size-4`, `size-5`, `size-7`) without a documented scale, and icon-only buttons inconsistently include `title` alongside `aria-label` (some do, some don't).
**User impact:** Minor visual inconsistency; accessibility is *mostly* covered (aria-label present almost everywhere already) but not verified as 100%.
**Root cause:** No documented icon-size scale.
**Recommended direction:** Two-step scale (14px dense UI / 16px primary actions), documented in `frontend-design-system.md`; audit remaining icon-only buttons for `aria-label` completeness in 17.11.
**Fixed in:** **17.1 (scale defined)**, verification sweep in **17.11**.

---

### F14 — Selected / hover / focus / disabled / processing / error states: inconsistent expression across features
**Severity:** High
**Current behavior:** Each feature invented its own version of these states: AI Timeline blocks use a priority-ordered `AiBlockVisualState` (processing → regenerating → disabled → stale → selected → hovered → pinned → normal) with per-state CSS classes; Asset Panel uses `aria-pressed` + border-color swap; Decision Inspector uses literal action-button `disabled` + a color-coded lifecycle pill; legacy pages barely have hover states at all (`hover:bg-slate-100` ad hoc).
**User impact:** No unified visual vocabulary for "this is selected" vs. "this is disabled" across the app — a user re-learns the visual language per panel.
**Root cause:** No shared state-token system existed before this sprint.
**Recommended direction:** The `state.*` token group (`frontend-design-system.md` §Tokens) — selected/hover/focus/processing/success/warning/error/disabled — consumed identically everywhere a state is expressed.
**Fixed in:** **17.1 (tokens defined)**, applied per-surface in 17.2–17.8.

---

### F15 — Empty / loading / error states exist in three different visual idioms
**Severity:** Medium
**Current behavior:** `components/ui/empty-state.tsx` + `loading-state.tsx` (legacy, `rounded-3xl` dashed border); `features/review/design-system`'s `ReviewEmptyState`/`ReviewSkeleton` (tokenized, `.review-skeleton` shimmer); AI Timeline's inline empty-state message (plain text, no shared component at all); Export Workspace's "No immutable render contract found" state (bespoke, one-off markup).
**User impact:** Four different "nothing to show" visual treatments across one product.
**Root cause:** No shared `EmptyState`/`LoadingState`/`ErrorState` primitive was ever promoted app-wide.
**Recommended direction:** One shared set (§Component Standards), used by all four contexts above.
**Fixed in:** **17.1 (standards documented)**, primitive consolidation in **17.7/17.9/17.10** as each surface is touched.

---

### F16 — Scrollbar behavior: solved for Desktop Editor, absent elsewhere
**Severity:** Low
**Current behavior:** `.desktop-editor-scroll` (thin, low-contrast) is applied across Desktop Editor/AI Timeline panels; `.review-editor-theme` has its own separate (slightly different) thin-scrollbar rule; legacy pages get the plain OS-default scrollbar.
**User impact:** Minor visual inconsistency, no functional issue.
**Root cause:** Two scrollbar utilities were built independently for two different theme scopes.
**Recommended direction:** One shared scrollbar utility class, defined once against `--ce-*`, applied universally.
**Fixed in:** **17.1 (unified utility added, aliased)**, applied per-surface thereafter.

---

### F17 — Panel collapse / resizable panels: solved well in Desktop Editor, absent in legacy shell
**Severity:** Low
**Current behavior:** Desktop Editor's `PanelDivider`/`PanelCollapseButton`/`useDesktopEditorLayout` are a genuinely good, keyboard-accessible (arrow keys, double-click reset), well-tested pattern. `DashboardShell`'s `Sidebar` has no resize or collapse at all (fixed 256px).
**User impact:** Legacy shell can't adapt to smaller viewports at all today (though this matters less since those pages are lower priority).
**Root cause:** Sidebar predates the resizable-panel pattern.
**Recommended direction:** If the new shared app shell (17.9) needs a collapsible side element, reuse the exact `PanelDivider`/`useDesktopEditorLayout` pattern rather than inventing a second one.
**Fixed in:** **17.9**.

---

### F18 — Viewport usability: 1920×1080 / 1600×900 / 1440×900 / 1366×768
**Severity:** Low (Desktop Editor), Medium (legacy pages, untested)
**Current behavior:** Desktop Editor's panel min/max math was verified arithmetically down to 1366×768 in 16.10.6.1 (worst case leaves 630px+ for Preview). Legacy `DashboardShell` pages have never been checked at any of these four widths — their fixed 256px sidebar plus unconstrained content grids could overflow at 1366px, especially `/` and `/workspace`'s stat-card rows.
**User impact:** Unknown/unverified risk on legacy pages; none currently known on the Editor.
**Root cause:** No responsive verification has ever been done outside the Editor.
**Recommended direction:** Extend the same verification discipline (documented in `frontend-responsive-system.md`) to every surface as it's rebuilt.
**Fixed in:** **17.2 (Editor re-verified after token cutover)**, **17.9/17.10 (legacy pages, first-time verification)**, full sweep in **17.11**.

---

## Severity summary

| Severity | Count | IDs |
|---|---|---|
| Critical | 3 | F1, F2, F3 |
| High | 2 | F4, F14 |
| Medium | 10 | F5, F6, F7, F8, F9, F10, F11, F12, F15, F18 |
| Low | 3 | F13, F16, F17 |

Note F9 (Manual Timeline toolbar grouping) is Medium severity but **not schedulable** without a separate, explicit runtime-boundary exception — it is the one finding this plan cannot resolve through visual redesign alone.
