# ADR Process

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

ADR means Architecture Decision Record.

Use ADRs to document important product, technical, AI, data, or infrastructure decisions that affect future work.

---

## When To Create An ADR

Create an ADR when deciding:

- Product direction that changes the main workflow.
- Frontend architecture.
- Backend architecture.
- Data model ownership.
- Queue or worker design.
- AI provider or model routing.
- Storage provider.
- Billing or credits logic.
- Security or deployment strategy.

Do not create ADRs for small UI copy changes or obvious bug fixes.

---

## ADR Format

```text
# ADR-XXX: Decision Title

Status: Proposed | Accepted | Replaced | Deprecated
Date: YYYY-MM-DD
Owner: Ho Quan

## Context

What problem are we solving?

## Decision

What did we decide?

## Options Considered

What alternatives were considered?

## Consequences

What becomes easier?
What becomes harder?
What must be watched later?
```

---

## Decision Rules

Prefer decisions that:

- Reduce manual editing work.
- Preserve the AI-first production flow.
- Keep users in review mode instead of manual editing mode.
- Support future SaaS scale without overbuilding the MVP.
- Keep implementation understandable.

---

## Current Accepted Decisions

### Product Direction

AI Clip Agent is an AI Video Production Platform, not an admin dashboard and not a traditional timeline-first editor.

### Main Flow

The main product flow is:

```text
Home
  ↓
Upload
  ↓
AI Queue
  ↓
Review
  ↓
Export
```

### Frontend Direction

The Next.js frontend in `frontend/` is the new product UI direction.

The old root `static/` UI is the local MVP implementation reference until logic is migrated.

### Backend Direction

The Python backend remains the local API/render engine while product specs are completed.
