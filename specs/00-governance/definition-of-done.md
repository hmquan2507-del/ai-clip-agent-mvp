# Definition of Done

Status: Active
Owner: Ho Quan
Version: 1.0
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

# Purpose

This document defines the minimum completion criteria for every deliverable inside AI Clip Agent.

No specification, feature, workflow, API, database model, UI, or implementation should be considered complete unless all required Definition of Done (DoD) criteria have been satisfied.

The purpose of this document is to ensure consistent quality across the entire product lifecycle.

---

# Principles

Definition of Done is a quality gate.

Completing implementation is not equivalent to completing a feature.

Every deliverable must satisfy documentation, architecture, implementation, testing, and review requirements before it is considered complete.

---

# Product Lifecycle

Every product feature follows the same lifecycle.

```text
Idea
    ↓
Product Specification
    ↓
Workflow
    ↓
UX
    ↓
UI
    ↓
API Contract
    ↓
Data Model
    ↓
Implementation
    ↓
Testing
    ↓
Review
    ↓
Release
```

Skipping stages is not allowed unless explicitly approved through an Architecture Decision Record (ADR).

---

# Definition of Done

A deliverable is Done only when every applicable requirement has been completed.

---

# Documentation

Documentation must:

- clearly describe the purpose
- define responsibilities
- explain assumptions
- describe expected behavior
- include cross references where applicable
- use repository terminology consistently

Documentation should not describe implementation details unless the document is intended for implementation.

---

# Architecture

Architecture must:

- follow Product Principles
- respect Core Domain
- align with Domain Model
- remain consistent with existing workflows
- avoid duplicated concepts
- support future SaaS scalability

No architecture should introduce conflicting business concepts.

---

# Workflows

Workflow documents must include:

- objective
- trigger
- inputs
- outputs
- state transitions
- success conditions
- failure conditions
- exception handling

---

# AI Components

Every AI module must define:

- purpose
- inputs
- outputs
- model routing
- prompt source
- retry strategy
- failure handling
- quality expectations

AI behavior must be deterministic whenever possible.

---

# API

API specifications must define:

- endpoint
- method
- authentication
- request schema
- response schema
- error responses
- validation rules
- version compatibility

Breaking API changes require an ADR.

---

# Database

Database specifications must include:

- entities
- relationships
- ownership
- lifecycle
- indexes
- constraints

Entity ownership must always be clearly defined.

---

# State Machines

Every state machine must define:

- initial state
- valid transitions
- terminal states
- invalid transitions
- recovery strategy

Undefined states are not allowed.

---

# Frontend

Frontend specifications must define:

- navigation
- screen purpose
- user actions
- loading states
- empty states
- error states
- accessibility considerations

UI should always support the Production workflow.

---

# Infrastructure

Infrastructure specifications must include:

- deployment strategy
- environment separation
- monitoring
- logging
- backup
- recovery
- security considerations

---

# Implementation

Implementation is complete only when:

- specification has been approved
- implementation follows specification
- no critical TODO remains
- technical debt is documented
- code passes review

---

# Testing

Every implementation must include appropriate testing.

Possible testing includes:

- unit testing
- integration testing
- workflow testing
- AI validation
- manual review

The required testing level depends on feature complexity.

---

# Review

Every deliverable requires review.

Review should verify:

- specification consistency
- architectural consistency
- implementation quality
- naming consistency
- documentation completeness

No feature should bypass review.

---

# Release

A feature may be released only after:

- review approval
- testing completion
- documentation update
- deployment verification

---

# Definition of Done Checklist

Before marking a deliverable as complete, verify:

- [ ] Purpose is documented
- [ ] Scope is clear
- [ ] Specification approved
- [ ] Architecture consistent
- [ ] Workflow defined
- [ ] API documented (if applicable)
- [ ] Database documented (if applicable)
- [ ] UI documented (if applicable)
- [ ] Tests completed
- [ ] Review completed
- [ ] Documentation updated
- [ ] Cross references verified

---

# Exceptions

Exceptions to this Definition of Done require approval through an ADR.

Temporary exceptions must include:

- reason
- owner
- expiration
- follow-up action

---

# Cross References

Related documents:

- Vision
- Product Principles
- Documentation Standards
- Decision Process
- Core Domain
- Domain Model
- AI Pipeline
- API Specification
- Database Model
- State Machine

---

# Exit Criteria

A document, feature, or implementation is considered complete only when every applicable requirement defined in this document has been satisfied.

Otherwise, its status remains **In Progress**.
