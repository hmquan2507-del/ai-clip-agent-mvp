# EPIC 16 — Usable Product Integration Roadmap

Status: In Progress  
Owner: Ho Quan  
Last Updated: 2026-07-18  
Current Milestone: 16.6.2 — AI Suggestion Lifecycle Store & Runtime

---

## Purpose

EPIC 16 turns the completed AI intelligence, editing, timeline, and render runtimes into a usable AI-first video editing product.

The product flow is:

```text
Upload
  -> AI understands and edits
  -> Review Workspace
  -> Optional manual refinement
  -> Optional natural-language revision
  -> Render and export
```

AI remains the primary editor. The manual editor is a refinement layer, not a second source of timeline truth.

---

## Non-negotiable Architecture

- `TimelineRuntimeStore` is the only owner of the active editable timeline.
- UI components never mutate timeline data directly.
- Timeline changes flow through Runtime -> Application Service -> API -> Mutation Runtime.
- History uses isolated before/after snapshots for the MVP.
- Clipboard operations use Clipboard Runtime together with Mutation and History Runtime.
- Successful atomic commands commit once, increment revision once, mark dirty once, and emit one event.
- Failed commands do not commit timeline state.
- Backend runtime snapshots remain authoritative for timeline, selection, history, clipboard, and preview state.
- Frontend interaction state may preview intent, but cannot become a second timeline store.
- Public factories remain backward-compatible unless a deliberate migration is approved.
- Runtime domain code does not depend on FastAPI or React unless required by its boundary.

---

## Completed Milestones

### 16.0 — Product Architecture Reconciliation

Status: Complete

- 16.0.1 — Product Architecture Contracts
- 16.0.2 — Product Adapter Layer
- 16.0.3 — Product Workspace Service
- 16.0.4 — Repository Workspace Adapters
- 16.0.5 — Product Workspace API Foundation

### 16.1 — Review Workspace Foundation

Status: Complete

- 16.1.1 — Review Workspace Domain
- 16.1.2 — Preview Session Runtime
- 16.1.3 — Timeline Selection Runtime
- 16.1.4 — Timeline Editing Runtime
  - 16.1.4.1 — Editable Timeline Domain
  - 16.1.4.2 — Editing Validator
  - 16.1.4.3 — Core Clip Mutation Runtime
  - 16.1.4.4 — Split, Duplicate, Delete & Gap Runtime
- 16.1.5 — Timeline Command History & Undo/Redo Runtime
- 16.1.5.5 — Timeline Runtime Refactor
  - 16.1.5.5.1 — Timeline Runtime Store
  - 16.1.5.5.2 — Mutation Runtime Refactor
  - 16.1.5.5.3 — History Runtime Refactor
  - 16.1.5.5.4 — Clipboard Runtime Refactor
  - 16.1.5.5.5 — Integration & Regression Tests
- 16.1.6 — Timeline Clipboard Runtime
- 16.1.7 — Review Runtime Session Orchestration
  - 16.1.7.1 — Review Runtime Session Domain
  - 16.1.7.2 — Runtime Graph Factory
  - 16.1.7.3 — Runtime State Synchronization
  - 16.1.7.4 — Workspace Runtime Snapshot
  - 16.1.7.5 — Review Runtime Lifecycle & Integration Tests

### 16.2 — Review Workspace API Foundation

Status: Complete

- 16.2.1 — Review Runtime Session Registry
- 16.2.2 — Review Workspace Application Service
- 16.2.3 — Review Workspace API Contracts & Schemas
- 16.2.4 — Review Workspace API Controller & Dependencies
- 16.2.5 — Review Workspace API Integration & Regression Tests

### 16.3 — Frontend Review Workspace Integration

Status: Complete

- 16.3.1 — Frontend Review API Contracts & Client Foundation
- 16.3.2 — Frontend Review Workspace State & Session Runtime
- 16.3.3 — React Review Workspace Provider & Hooks
- 16.3.4 — New Review Workspace Design System
- 16.3.5 — New Review Workspace Shell
- 16.3.6 — Runtime-connected Review UI
- 16.3.7 — Review Workspace Integration & Regression

### 16.4 — Manual Timeline Editor MVP

Status: Complete

- 16.4.1 — Timeline Mutation API Contracts & Schemas
- 16.4.2 — Timeline Mutation Application Service
- 16.4.3 — Timeline Mutation API Mapper & Controller
- 16.4.4 — Frontend Timeline Mutation API Client
- 16.4.5 — Frontend Timeline Command State Runtime
- 16.4.6 — React Timeline Command Provider & Hooks
- 16.4.7 — Runtime-connected Timeline Editing UI
  - 16.4.7.1 — Selection API Contracts & Controller
  - 16.4.7.2 — Frontend Selection API Client & State Runtime
  - 16.4.7.3 — Runtime-connected Timeline Selection UI
  - 16.4.7.4 — Runtime-connected Timeline Command Controls
  - 16.4.7.5 — Timeline Editing UI Integration & Regression
- 16.4.8 — Timeline Clipboard UI Integration
  - 16.4.8.1 — Backend Clipboard Application & API Integration
  - 16.4.8.2 — Frontend Clipboard API Client & State Runtime
  - 16.4.8.3 — React Clipboard Provider, Hooks & UI
  - 16.4.8.4 — Timeline Clipboard UI Integration & Regression Tests

---

## Completed Milestone

### 16.5 — Drag & Drop Timeline

Status: Complete

Goal: provide CapCut-style clip movement while preserving the backend-authoritative mutation architecture.

- 16.5.1 — Timeline Drag Interaction Contracts & Coordinate Model (Completed)
- 16.5.2 — Frontend Drag Session State Runtime (Completed)
- 16.5.3 — Timeline Snap Runtime (Completed)
- 16.5.4 — Runtime-connected Clip Drag UI (Completed)
- 16.5.5 — Cross-track Drag & Drop (Completed)
- 16.5.6 — Drag Preview, Cancel & Conflict Recovery (Completed)
- 16.5.7 — Drag & Drop Integration & Regression Tests (Completed)

### 16.5 Definition of Done

- A clip can be dragged horizontally on its current track.
- A compatible clip can be moved to another editable track.
- Drag preview never mutates the authoritative timeline.
- Drop delegates exactly one `move_clip` command through the frontend runtime boundary.
- Frame, playhead, and clip-edge snapping are deterministic.
- Locked tracks, overlap, incompatibility, and revision conflicts remain atomic and read-only on failure.
- Escape/pointer cancellation restores the visual state without a backend command.
- Selection, history, clipboard, undo/redo, and source timeline isolation regressions remain green.

---

## Active Milestone

### 16.6 — AI Suggestions & Command Panel

Status: In Progress

Goal: expose AI editing recommendations and natural-language revision commands while keeping the backend timeline and mutation runtimes authoritative.

- 16.6.1 — AI Suggestion Contracts & Read Model (Completed)
- 16.6.2 — AI Suggestion Lifecycle Store & Runtime (In Progress)
- 16.6.3 — AI Suggestion Application Service
- 16.6.4 — AI Suggestion API Contracts, Mapper & Controller
- 16.6.5 — Frontend AI Suggestion API Client & State Runtime
- 16.6.6 — React AI Suggestion Provider & Hooks
- 16.6.7 — Runtime-connected Suggestion Review UI
- 16.6.8 — Natural-language Command Submission Boundary
- 16.6.9 — AI Suggestions Integration & Regression Tests

### 16.6 Definition of Done

- Backend snapshots expose structured, revision-aware AI suggestions.
- Legacy suggestion payloads remain readable through a normalized read model.
- Apply delegates one atomic command through Application Service and Mutation/History Runtime.
- Dismiss and regenerate do not mutate timeline state.
- Revision conflicts and stale suggestions remain read-only on failure.
- Frontend suggestion components never call timeline APIs or mutate snapshot data directly.
- Natural-language commands cross a dedicated runtime/API boundary before producing any timeline command.
- Suggestion lifecycle, timeline, history, selection, clipboard, drag, and source isolation regressions remain green.

---

## Remaining EPIC 16 Milestones

### 16.7 — Manual Editing Completion

- Trim handles
- Keyboard shortcuts
- Timeline zoom and scroll coordination
- Multi-select editing
- Ripple edit policy
- Advanced snapping and edit affordances

### 16.8 — Export Workspace Integration

- Review-to-render handoff
- Render status and recovery
- Quality gate presentation
- Final artifact download and export lifecycle

### 16.9 — Product Polish

- Loading, empty, failure, and recovery states
- Accessibility and responsive behavior
- Performance profiling
- Product copy and Vietnamese UX polish

### 16.10 — MVP Release Candidate

- End-to-end product regression
- Production configuration validation
- Security and operational readiness
- Release checklist and known limitations

---

## Post-EPIC 16 Product Roadmap

- EPIC 17 — Media Library & User Assets
- EPIC 18 — Canvas & Visual Editing
- EPIC 19 — Advanced Subtitle System
- EPIC 20 — Text & Graphic Intelligence
- EPIC 21 — Audio & TTS Editing
- EPIC 22 — Meme, Sticker & Effect Library
- EPIC 23 — AI Partial Re-edit
- EPIC 24 — Preview & Render Consistency

---

## Change Control

This document is the canonical implementation roadmap for EPIC 16. Any sprint renumbering, insertion, or scope change must update this file in the same commit that introduces the change.
