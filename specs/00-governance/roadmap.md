# Official Roadmap

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01

---

## Final Goal

Build an AI Video Production Platform that helps users save 80-95% of video editing time.

The product is not an admin dashboard and not a traditional timeline-first editor. The product is an AI production system where users upload, wait for AI output, review, approve, regenerate when needed, and export.

---

## Phase 1 - Foundation

### EPIC 1 - Foundation

Status: Complete

- Repository Foundation
- Frontend Foundation
- Specification Repository
- Governance
- Git Workflow

### EPIC 2 - Product Specification

Status: In Progress

Goal: define the full product before implementation.

#### Sprint 2.2.1 - Governance Foundation

Status: In Progress
Goal: Solidify the core governance and product principles.

Governance:

- In Progress: Vision
- In Progress: Product Principles
- In Progress: Documentation Standards
- In Progress: ADR Process
- In Progress: Roadmap
- In Progress: Glossary

Product:

- Done: Core Domain
- Done: Domain Model
- Done: Value Proposition
- Done: User Personas
- Done: User Journey
- Done: Success Metrics
- Done: Pricing Strategy

Workflows:

- Done: AI Production Workflow
- Done: Upload Workflow
- Done: Review Workflow
- Done: Export Workflow

AI:

- Done: AI Pipeline
- Done: Style Engine
- Done: Prompt Library
- Done: Model Routing

Frontend:

- Done: Design System
- Done: Navigation
- Done: Workspace Layout

Backend:

- Done: API Specification
- Done: Queue Architecture
- Done: Rendering Architecture

Data:

- Done: Database Model
- Done: Entity Relationship
- Done: State Machine

Infrastructure:

- Done: Deployment
- Done: Docker
- Done: Monitoring

### EPIC 2.2 - AI Production Workspace

Status: In Progress

Start only after Product Specification is complete.

Core flow:

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

No admin-style dashboard. Home may show recent productions and shortcuts, but production flow is the center.

---

## Future Epics

### EPIC 3 - AI Pipeline

Status: Not Started

This is the heart of the product.

```text
Upload
  ↓
Transcript
  ↓
Scene Detection
  ↓
Speaker Detection
  ↓
Highlight Detection
  ↓
Clip Selection
  ↓
Apply Style
  ↓
Subtitle
  ↓
B-roll
  ↓
Music
  ↓
Sound FX
  ↓
Motion
  ↓
Render
  ↓
Review
  ↓
Export
```

### EPIC 4 - Review Workspace

Status: Not Started

This is not a timeline editor. It is a review-first workspace.

```text
AI Output
  ↓
Review
  ↓
Approve
  ↓
Regenerate
  ↓
Export
```

### EPIC 5 - Style Engine

Status: Not Started

Example styles:

- Talking Head
- Podcast
- Education
- Business
- Finance
- Storytelling
- Gaming
- Luxury
- Real Estate

Each style defines:

- Subtitle
- Motion
- Zoom
- B-roll
- Sound FX
- Music
- CTA

### EPIC 6 - Render Engine

Status: Not Started

- Render Queue
- Background Workers
- Retry
- Progress
- Export

### EPIC 7 - SaaS Platform

Status: Not Started

- Authentication
- Workspace
- Billing
- Credits
- Subscription
- Organization

### EPIC 8 - Automation

Status: Not Started

- Batch Production
- Auto Publish
- Scheduling
- Webhooks
- Notifications

### EPIC 9 - Analytics

Status: Not Started

- AI Quality
- Production Time
- Render Time
- Usage
- Cost

### EPIC 10 - Production Ready

Status: Not Started

- CI/CD
- Monitoring
- Logging
- Backup
- Security
- Performance
- Scaling
