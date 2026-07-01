# AI Clip Agent Specifications

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01

---

## Final Goal

Build an AI Video Production Platform that helps users save 80-95% of video editing time.

---

## Product Direction

AI Clip Agent is not an admin dashboard and not a timeline-first video editor.

The product flow is:

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

The user reviews AI output instead of manually editing from scratch.

---

## Required Working Process

Every feature must follow this sequence:

```text
Idea
  ↓
Product Spec
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
Tasks
  ↓
Implementation
  ↓
Testing
  ↓
Review
  ↓
Release
```

Do not skip directly from idea to implementation unless the feature is a small fix with no product impact.

---

## Current Roadmap Status

### EPIC 1 - Foundation

Status: Complete

- Repository Foundation
- Frontend Foundation
- Specification Repository
- Governance
- Git Workflow

### EPIC 2 - Product Specification

Status: In Progress

Goal: define the whole product before building more product features.

This epic is currently focused on solidifying the core governance and product principles. The following documents are being actively reviewed and updated:

- Governance: Vision
- Governance: Product Principles
- Governance: Documentation Standards
- Governance: ADR Process
- Governance: Roadmap
- Governance: Glossary
- Product: Core Domain
- Product: Domain Model
- Product: Value Proposition
- Product: User Personas
- Product: User Journey
- Product: Success Metrics
- Product: Pricing Strategy
- Workflows: AI Production Workflow
- Workflows: Upload Workflow
- Workflows: Review Workflow
- Workflows: Export Workflow
- AI: AI Pipeline
- AI: Style Engine
- AI: Prompt Library
- AI: Model Routing
- Frontend: Design System
- Frontend: Navigation
- Frontend: Workspace Layout
- Backend: API Specification
- Backend: Queue Architecture
- Backend: Rendering Architecture
- Data: Database Model
- Data: Entity Relationship
- Data: State Machine
- Infrastructure: Deployment
- Infrastructure: Docker
- Infrastructure: Monitoring

### EPIC 2.2 - AI Production Workspace

Status: In Progress

Start only after EPIC 2 Product Specification is complete.


---

# Repository Status

## Current Progress

| Epic | Status |
|------|---------|
| EPIC 01 Foundation | ✅ Complete |
| EPIC 02 Product Specification | ✅ Approved |
| EPIC 03 AI Production Workspace | ⏳ Next |
| EPIC 04 Review Workspace | Planned |
| EPIC 05 Style Engine | Planned |
| EPIC 06 Render Engine | Planned |
| EPIC 07 SaaS Platform | Planned |
| EPIC 08 Automation | Planned |
| EPIC 09 Analytics | Planned |
| EPIC 10 Production Ready | Planned |

---

## Repository Rules

All implementation must follow:

Idea

↓

Specification

↓

Workflow

↓

Architecture

↓

Implementation

↓

Testing

↓

Review

↓

Release

Product Specification is the single source of truth.

Changes to approved specifications require an ADR.
