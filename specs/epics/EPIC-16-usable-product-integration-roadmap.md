# EPIC 16 â€” Usable Product Integration Roadmap

Status: In Progress  
Owner: Ho Quan  
Last Updated: 2026-07-21  
Current Milestone: 16.8.2 â€” Render Job Submission & Queue Integration

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

### 16.0 â€” Product Architecture Reconciliation

Status: Complete

- 16.0.1 â€” Product Architecture Contracts
- 16.0.2 â€” Product Adapter Layer
- 16.0.3 â€” Product Workspace Service
- 16.0.4 â€” Repository Workspace Adapters
- 16.0.5 â€” Product Workspace API Foundation

### 16.1 â€” Review Workspace Foundation

Status: Complete

- 16.1.1 â€” Review Workspace Domain
- 16.1.2 â€” Preview Session Runtime
- 16.1.3 â€” Timeline Selection Runtime
- 16.1.4 â€” Timeline Editing Runtime
  - 16.1.4.1 â€” Editable Timeline Domain
  - 16.1.4.2 â€” Editing Validator
  - 16.1.4.3 â€” Core Clip Mutation Runtime
  - 16.1.4.4 â€” Split, Duplicate, Delete & Gap Runtime
- 16.1.5 â€” Timeline Command History & Undo/Redo Runtime
- 16.1.5.5 â€” Timeline Runtime Refactor
  - 16.1.5.5.1 â€” Timeline Runtime Store
  - 16.1.5.5.2 â€” Mutation Runtime Refactor
  - 16.1.5.5.3 â€” History Runtime Refactor
  - 16.1.5.5.4 â€” Clipboard Runtime Refactor
  - 16.1.5.5.5 â€” Integration & Regression Tests
- 16.1.6 â€” Timeline Clipboard Runtime
- 16.1.7 â€” Review Runtime Session Orchestration
  - 16.1.7.1 â€” Review Runtime Session Domain
  - 16.1.7.2 â€” Runtime Graph Factory
  - 16.1.7.3 â€” Runtime State Synchronization
  - 16.1.7.4 â€” Workspace Runtime Snapshot
  - 16.1.7.5 â€” Review Runtime Lifecycle & Integration Tests

### 16.2 â€” Review Workspace API Foundation

Status: Complete

- 16.2.1 â€” Review Runtime Session Registry
- 16.2.2 â€” Review Workspace Application Service
- 16.2.3 â€” Review Workspace API Contracts & Schemas
- 16.2.4 â€” Review Workspace API Controller & Dependencies
- 16.2.5 â€” Review Workspace API Integration & Regression Tests

### 16.3 â€” Frontend Review Workspace Integration

Status: Complete

- 16.3.1 â€” Frontend Review API Contracts & Client Foundation
- 16.3.2 â€” Frontend Review Workspace State & Session Runtime
- 16.3.3 â€” React Review Workspace Provider & Hooks
- 16.3.4 â€” New Review Workspace Design System
- 16.3.5 â€” New Review Workspace Shell
- 16.3.6 â€” Runtime-connected Review UI
- 16.3.7 â€” Review Workspace Integration & Regression

### 16.4 â€” Manual Timeline Editor MVP

Status: Complete

- 16.4.1 â€” Timeline Mutation API Contracts & Schemas
- 16.4.2 â€” Timeline Mutation Application Service
- 16.4.3 â€” Timeline Mutation API Mapper & Controller
- 16.4.4 â€” Frontend Timeline Mutation API Client
- 16.4.5 â€” Frontend Timeline Command State Runtime
- 16.4.6 â€” React Timeline Command Provider & Hooks
- 16.4.7 â€” Runtime-connected Timeline Editing UI
  - 16.4.7.1 â€” Selection API Contracts & Controller
  - 16.4.7.2 â€” Frontend Selection API Client & State Runtime
  - 16.4.7.3 â€” Runtime-connected Timeline Selection UI
  - 16.4.7.4 â€” Runtime-connected Timeline Command Controls
  - 16.4.7.5 â€” Timeline Editing UI Integration & Regression
- 16.4.8 â€” Timeline Clipboard UI Integration
  - 16.4.8.1 â€” Backend Clipboard Application & API Integration
  - 16.4.8.2 â€” Frontend Clipboard API Client & State Runtime
  - 16.4.8.3 â€” React Clipboard Provider, Hooks & UI
  - 16.4.8.4 â€” Timeline Clipboard UI Integration & Regression Tests

---

## Completed Milestone

### 16.5 â€” Drag & Drop Timeline

Status: Complete

Goal: provide CapCut-style clip movement while preserving the backend-authoritative mutation architecture.

- 16.5.1 â€” Timeline Drag Interaction Contracts & Coordinate Model (Completed)
- 16.5.2 â€” Frontend Drag Session State Runtime (Completed)
- 16.5.3 â€” Timeline Snap Runtime (Completed)
- 16.5.4 â€” Runtime-connected Clip Drag UI (Completed)
- 16.5.5 â€” Cross-track Drag & Drop (Completed)
- 16.5.6 â€” Drag Preview, Cancel & Conflict Recovery (Completed)
- 16.5.7 â€” Drag & Drop Integration & Regression Tests (Completed)

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

### 16.6 â€” AI Suggestions & Command Panel

Status: Completed

Goal: expose AI editing recommendations and natural-language revision commands while keeping the backend timeline and mutation runtimes authoritative.

- 16.6.1 â€” AI Suggestion Contracts & Read Model (Completed)
- 16.6.2 â€” AI Suggestion Lifecycle Store & Runtime (Completed)
- 16.6.3 â€” AI Suggestion Application Service (Completed)
- 16.6.4 â€” AI Suggestion API Contracts, Mapper & Controller (Completed)
- 16.6.5 â€” Frontend AI Suggestion API Client & State Runtime (Completed)
- 16.6.6 â€” React AI Suggestion Provider & Hooks (Completed)
- 16.6.7 â€” Runtime-connected Suggestion Review UI (Completed)
- 16.6.8 â€” Natural-language Command Submission Boundary (Completed)
- 16.6.9 â€” AI Suggestions Integration & Regression Tests (Completed)

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

## Active Milestone

### 16.7 â€” Manual Editing Completion

Status: Complete

Goal: complete precise manual timeline refinement while preserving the backend timeline, command history, and revision checks as the only source of committed editing state.

- 16.7.1 â€” Timeline Trim Interaction Contracts & Coordinate Model (Completed)
- 16.7.2 â€” Frontend Trim Session State Runtime (Completed)
- 16.7.3 â€” Runtime-connected Clip Trim Handles (Completed)
- 16.7.4 â€” Timeline Keyboard Shortcut Runtime (Completed)
- 16.7.5 â€” Runtime-connected Keyboard Editing Controls (Completed)
- 16.7.6 â€” Timeline Zoom & Scroll Coordination (Completed)
- 16.7.7 â€” Multi-select Editing Commands (Completed)
- 16.7.8 â€” Ripple Edit Policy & Runtime (Completed)
- 16.7.9 â€” Manual Editing Integration & Regression Tests (Completed)

### 16.7 Definition of Done

- Start/end trim previews are frame-quantized, bounded, cancellable, and never mutate authoritative state directly.
- Every committed trim, shortcut, multi-select, or ripple operation crosses the runtime command boundary exactly once.
- Locked tracks, minimum duration, invalid ranges, and revision conflicts remain atomic and read-only on failure.
- Timeline zoom and horizontal scrolling preserve pointer-to-time accuracy and playhead/selection alignment.
- Keyboard commands respect focus, editable elements, platform modifiers, and active workspace state.
- Multi-select edits use deterministic targets and remain compatible with history, clipboard, selection, and drag runtimes.
- Manual editing, AI suggestions, command submission, clipboard, drag, and source-isolation regressions remain green.

---

## Active Milestone

### 16.8 â€” Export Workspace Integration

Status: In Progress

Goal: connect the authoritative Review Workspace timeline to render and export through immutable, revision-aware contracts without allowing the render layer to read or mutate the active editing store directly.

- 16.8.1 â€” Review-to-Render Handoff Contracts & Runtime (Completed)
- 16.8.2 â€” Render Job Submission & Queue Integration (In Progress)
- 16.8.3 â€” Export Workspace API Contracts & Controller
- 16.8.4 â€” Frontend Export State Runtime & API Client
- 16.8.5 â€” Render Status, Failure Recovery & Retry UX
- 16.8.6 â€” Quality Gate, Artifact Download & Export Lifecycle
- 16.8.7 â€” Export Workspace Integration & Regression Tests

### 16.8.1 Scope

- Create an immutable `ReviewRenderContract` from the authoritative review timeline snapshot.
- Preserve production ID, timeline revision, snapshot identity, track payload, render options, metadata, and checksum.
- Reject dirty workspaces, stale expected revisions, invalid snapshots, and checksum mismatches without mutating timeline state.
- Ensure render consumers receive the handoff contract rather than direct access to `TimelineRuntimeStore`.
- Preserve older Review Workspace, history, clipboard, drag, trim, multi-select, ripple, and render architecture regressions.


### 16.8.2 Scope

- Accept only the immutable ReviewRenderContract created by the 16.8.1 handoff runtime.
- Validate contract structure and checksum before creating a render queue job.
- Submit through a dedicated queue port and the existing QueueService adapter.
- Serialize a deep-copied contract into a QueueType.RENDER_RUNTIME payload.
- Use a deterministic idempotency key to prevent duplicate queue submissions.
- Keep queue submission isolated from TimelineRuntimeStore, FastAPI controllers, and frontend state.
- Preserve review, timeline, history, manual editing, handoff, and render architecture regressions.
### 16.8 Definition of Done

- A saved Review Workspace revision can produce one deterministic immutable render handoff contract.
- Later timeline edits cannot mutate a previously issued render contract.
- Dirty state and revision conflicts are rejected before render submission.
- Contract checksum validation detects tampering or malformed payloads.
- Render and export boundaries do not read mutable timeline state directly.
- Render status, retry, quality gate, artifact lifecycle, and frontend export integration are implemented in subsequent 16.8 sprints.
- Review, manual editing, AI suggestion, clipboard, drag, history, source-isolation, and render regressions remain green.

---

## Remaining EPIC 16 Milestones

### 16.9 â€” Product Polish

- Loading, empty, failure, and recovery states
- Accessibility and responsive behavior
- Performance profiling
- Product copy and Vietnamese UX polish

### 16.10 â€” MVP Release Candidate

- End-to-end product regression
- Production configuration validation
- Security and operational readiness
- Release checklist and known limitations

---

## Post-EPIC 16 Product Roadmap

- EPIC 17 â€” Media Library & User Assets
- EPIC 18 â€” Canvas & Visual Editing
- EPIC 19 â€” Advanced Subtitle System
- EPIC 20 â€” Text & Graphic Intelligence
- EPIC 21 â€” Audio & TTS Editing
- EPIC 22 â€” Meme, Sticker & Effect Library
- EPIC 23 â€” AI Partial Re-edit
- EPIC 24 â€” Preview & Render Consistency

---

## Change Control

This document is the canonical implementation roadmap for EPIC 16. Any sprint renumbering, insertion, or scope change must update this file in the same commit that introduces the change.





## Sprint 16.8.3 - Export Workspace API Contracts & Controller

Status: Completed

Scope:

- Export Workspace API request/response contracts
- Export Workspace application service
- FastAPI controller and dependency factory
- Render submission endpoint
- Component health endpoint
- OpenAPI and controller regression tests


## Sprint 16.8.4 - Export Workspace Router Integration & Render Status API

Status: Completed

Scope:

- Root FastAPI router integration
- Render submission status endpoint
- Read-only QueueService status projection
- Missing job and UUID validation
- OpenAPI and integration regression tests


## Sprint 16.8.5 - Export Workspace Frontend Runtime

Status: Completed

Scope:

- Typed Export Workspace frontend API client
- Render submission state machine
- Render status polling
- Cancellation and lifecycle cleanup
- React external-store runtime hook
- Reusable Export Runtime panel
- TypeScript and frontend regression validation


- [x] Sprint 16.8.6 — Export Workspace Page Integration & Review-to-Export Navigation (Full Source Replacement)

- [x] Sprint 16.8.7.1 — Playback Session Runtime
  - Immutable playback session contracts and state snapshots
  - Deterministic play, pause, stop, seek, speed, direction, loop, frame-step, advance, reset, and disposal behavior
  - Pure frontend runtime with no React, backend, media-element, or timeline mutation dependency

- [x] Sprint 16.8.7.2 — Playhead Runtime
  - Pure time, frame, timeline-pixel, and viewport-pixel coordinate projection
  - Zoom, viewport, and scroll coordination without changing logical playback time
  - Deterministic drag preview, commit, cancellation, and single seek request boundary
  - Playback synchronization guarded during active dragging with no feedback loop

## Sprint 16.8.7.3 — Video Preview Synchronization

Status: Implemented by full-source-replacement package.

Scope:
- Video preview port contract
- Playback and playhead synchronization
- HTML video adapter isolation
- Drift correction and feedback-loop prevention
- Media event lifecycle and safe detach/dispose

## Sprint 16.8.7.4 — Audio Synchronization Runtime

Status: Completed

Delivered:
- Voice, music, and sound-effect track synchronization against the playback clock.
- Timeline-time to source-time mapping with source offsets and track bounds.
- Master/track volume, mute, solo, playback-rate, buffering, and drift handling.
- DOM-isolated audio port plus HTMLAudioElement adapter.
- Full regression coverage for Playback Session, Playhead, and Video Preview runtimes.

## Sprint 16.8.7.5 — Timeline Scrubbing Runtime

Status: Completed

Delivered:
- Deterministic scrub begin, throttled preview, commit, cancellation, and playback resume behavior.
- Timeline pixel/time/frame projection through the existing playhead runtime.
- Video and audio preview synchronization with muted-audio scrubbing policy.
- Feedback-loop guards, immutable snapshots, DOM-free core runtime, and full playback regression coverage.

## Sprint 16.8.7.6 — Timeline Selection Runtime — Complete

- Single, toggle, multi, and range selection runtime
- Independent active and focused clip state
- Keyboard focus navigation and bounded selection history
- Immutable snapshots with no React, DOM, backend, or timeline mutation dependency

## Sprint 16.8.7.7 — Timeline Clip Move Runtime — Completed

- Added immutable clip move contracts and snapshots.
- Added frame/time preview calculations with duration bounds.
- Added multi-clip movement preserving relative spacing.
- Added configurable snap targets and threshold handling.
- Added begin, preview, commit, cancel, reset, subscribe, and dispose lifecycle.
- Runtime remains independent from React, DOM, backend APIs, and timeline mutation.
- Added regression coverage through Sprint 16.8.6 and TypeScript validation.
