# Frontend Design Direction

Sprint 17.1 — Frontend Audit & Design System
Date: 2026-07-25

## The product, in one sentence

AI Clip Agent is a professional, AI-first desktop video editor where AI does 80–90% of the work and the timeline is for refinement, not creation from scratch — the workflow is **source media/idea → AI analyzes and edits → user reviews AI decisions → user refines on the timeline → export**.

## What it must not look like

- A generic SaaS dashboard (hero banners, stat-card grids, sidebar nav as the primary metaphor) — this is what most of the app's legacy surfaces look like today, and it's wrong for the product.
- A landing page — no marketing headlines, no oversized decorative typography, inside the editor.
- A ChatGPT clone — AI is a collaborator embedded in the editing surface, not a chat window bolted to the side.
- A collection of disconnected cards — every panel belongs to one continuous editing surface, not a grid of independent widgets.
- A mobile UI enlarged for desktop — dense, precise controls, not touch-sized tap targets with excess whitespace.

## What it must feel like

Professional · Calm · Precise · Dense but readable · Creator-focused · AI-native · Modern.

## Reference points (interaction principles, not visual identity)

- **DaVinci Resolve** — page-based workflow discipline, restrained chrome, color used sparingly and meaningfully (not decoratively).
- **Premiere Pro** — dockable/resizable panel model (already the Desktop Editor's own architecture), dense toolbars organized by function.
- **Final Cut Pro** — magnetic timeline clarity, confident use of negative space around the canvas.
- **Descript** — the closest existing product to "AI decisions reviewed alongside a transcript/timeline" — worth studying for how it keeps AI suggestions legible without turning the whole UI into a chat log.
- **OpusClip** — AI-first clip generation UX; worth studying for how confidence/reasoning is surfaced compactly, which is directly relevant to the AI Timeline and AI Copilot.

None of these are cloned. Their *information density, panel discipline, and restraint* inform this product's own direction; their specific colors, iconography, or branding do not.

## Core design principles

1. **Preview and Timeline lead visual hierarchy.** Every other panel (Asset Library, Inspector, AI Copilot, Tool Rail) is secondary — sized, colored, and weighted to recede, not compete. This is a sizing decision already largely correct (16.10.6.1 narrowed Asset/Inspector defaults) and now becomes a *visual* decision too (Preview gets the quietest chrome in the app — see UX audit F4).
2. **AI intelligence is visible but not visually overwhelming.** AI-authored content (AI Timeline blocks, AI Copilot suggestions, Decision inspector) gets one small, consistent, restrained marker — not a badge-per-card, not a gradient, not a persistent "AI" watermark. The goal is "I can tell this came from AI at a glance," not "AI branding everywhere."
3. **Surface contrast before borders.** Three elevation steps (app → panel → raised) separate regions primarily through background-color contrast; visible 1px borders are reserved for interactive affordances (dividers you can drag, inputs you can focus, selected states) — not used as the default separator between every panel and its neighbor (UX audit F11).
4. **Color communicates state, not decoration.** Every non-neutral color in the UI means something specific (selected, processing, error, a decision-type category, the brand accent on a primary action) — never chosen for visual variety. If a component is using color and it isn't a documented state or category token, that's a bug.
5. **Controls are dense but readable.** Match the Desktop Editor's already-established control heights (~28–36px), 10–12px type for dense UI — do not inflate controls to "comfortable SaaS" sizing, but never let density compromise legibility (contrast and the type scale, §Design System, exist specifically to prevent that trade-off).
6. **Avoid generic dashboard cards.** A "card" (bordered box with padding, icon, title, description) is the right shape for genuinely discrete, comparable items (an asset, a suggestion, a decision) — it is the wrong shape for a page's *primary* content, which should feel like one continuous workspace, not a card grid pretending to be one.
7. **Avoid excessive gradients.** Gradients are permitted only for functional purposes already in use (the Preview canvas's placeholder background, the AI Timeline's playhead/selection guide) — never as decorative panel backgrounds or button fills.
8. **Avoid excessive rounded containers.** One deliberate radius scale (sm/md/lg, §Design System) replaces today's five-value inconsistency (8/10/12/14/24px) — no `rounded-3xl` cards inside a dense editing tool.
9. **Avoid decorative motion.** Motion communicates a state change (a panel resizing, a decision regenerating, a value updating) — never plays for its own sake. `prefers-reduced-motion` must be honored everywhere, not just inside one theme scope (a fix already scoped into the token foundation, §Accessibility System).
10. **Avoid oversized marketing headings inside the editor.** The `display`/`pageTitle` type roles exist for Workspace/marketing-adjacent contexts only; nothing inside the Editor shell should ever use them — Editor panel titles top out at `panelTitle`/`sectionTitle`.

## How this resolves the audit's top findings

- F1/F2 (three token systems + one un-tokenized legacy system) → one semantic token namespace, §Design System.
- F3 (placeholder pages posing as real) → honest "Pending Runtime"-style states everywhere real data doesn't exist yet, never a fake-populated mockup.
- F4 (Preview doesn't yet lead hierarchy) → principle 1 + 3, applied in 17.3.
- F8 (AI content doesn't read as AI-authored) → principle 2, applied in 17.6/17.8.
- F11/F12/F14 (borders, typography, state inconsistency) → principles 3–5, resolved by the token system this sprint defines and later sprints apply.
