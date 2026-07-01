# Documentation Standards

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

This document defines how specs should be written and maintained.

Specs are the source of truth for product, workflow, UI, API, data, AI, and infrastructure decisions.

---

## Required Header

Every spec file should start with:

```text
# Title

Status: Draft | Active | Deprecated
Owner: Ho Quan
Last Updated: YYYY-MM-DD
Related Epic: EPIC-XX Name
```

---

## Status Rules

- Draft: being written or still open for change.
- Active: accepted as current direction.
- Deprecated: kept for history but no longer current.

---

## Writing Style

- Use clear headings.
- Prefer product language over technical jargon unless the file is technical.
- Define nouns before using them.
- Use short lists for decisions.
- Use diagrams as text blocks when they clarify flow.
- Avoid mixing implementation details into product specs unless needed.

---

## Required Sections By Spec Type

### Product Spec

- Purpose
- Problem
- User
- Desired outcome
- Scope
- Non-goals
- Success criteria

### Workflow Spec

- Trigger
- Inputs
- Steps
- Outputs
- Failure states
- User decisions

### UX/UI Spec

- User intent
- Screen structure
- Primary actions
- Empty states
- Loading states
- Error states
- Mobile behavior

### API Spec

- Endpoint
- Request
- Response
- Error cases
- Auth requirements
- Data ownership

### Data Spec

- Entities
- Fields
- Relationships
- State machine
- Events
- Retention rules

---

## Change Rules

When product direction changes:

1. Update the relevant spec first.
2. Update roadmap or task docs if scope changes.
3. Then update code.

When implementation reveals a better direction:

1. Write the proposed change in the relevant spec.
2. Mark old behavior as replaced or deprecated.
3. Keep the roadmap consistent.

---

## Completion Rule

A spec is complete enough to implement only when:

- The user flow is clear.
- API or data contracts are clear enough for engineering.
- Empty, loading, error, and review states are considered.
- Non-goals are stated.
