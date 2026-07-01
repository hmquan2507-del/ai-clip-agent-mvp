# System Boundaries

Status: Active
Owner: Ho Quan
Version: 1.0
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

# Purpose

This document defines the architectural boundaries of AI Clip Agent.

Its purpose is to clearly separate responsibilities between systems, services, external providers, and users.

A clear boundary prevents duplicated logic, simplifies maintenance, and supports future scaling.

---

# Core Principle

AI Clip Agent orchestrates AI video production.

It is **not** responsible for implementing AI foundation models, payment providers, cloud storage providers, or external publishing platforms.

Instead, it coordinates these systems through well-defined interfaces.

---

# System Overview

```text
                User
                  │
                  ▼
        AI Production Workspace
                  │
                  ▼
            Frontend Application
                  │
                  ▼
               API Layer
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 Business Services      Background Queue
        │                   │
        ▼                   ▼
 Production Engine     Worker Processes
        │                   │
        └─────────┬─────────┘
                  ▼
             AI Providers
                  │
                  ▼
          Storage / Rendering
                  │
                  ▼
               Final Export
```

---

# Internal System

The internal system includes:

- Frontend
- API
- Authentication
- Production Engine
- Queue
- Workers
- Database
- Storage Abstraction
- Style Engine
- Review Workspace
- Render Engine

These components are owned by AI Clip Agent.

---

# External Systems

External systems include:

- AI Models
- LLM Providers
- Video Generation Providers
- Speech Recognition
- Cloud Storage
- Payment Providers
- Authentication Providers
- Email Providers
- Analytics Providers
- Social Platforms

These services may be replaced without changing the product domain.

---

# User Boundary

Users interact only through the Production Workspace.

Users never communicate directly with:

- Queue
- Workers
- AI Pipeline
- Database
- Rendering Infrastructure

All communication flows through the API.

---

# Frontend Boundary

Frontend responsibilities:

- Upload assets
- Display production progress
- Review AI output
- Manage productions
- Display errors
- Trigger exports

Frontend must never contain business rules.

---

# API Boundary

API responsibilities:

- Validate requests
- Authenticate users
- Authorize actions
- Orchestrate workflows
- Trigger asynchronous jobs
- Return production state

API must remain stateless.

---

# Production Engine Boundary

Production Engine owns:

- production lifecycle
- production orchestration
- workflow execution
- production state transitions

Business rules belong here.

---

# Queue Boundary

Queue responsibilities:

- background execution
- retries
- scheduling
- prioritization

Queue never owns business logic.

---

# Worker Boundary

Workers perform:

- transcription
- scene detection
- subtitle generation
- rendering
- exports
- AI inference

Workers should remain independent and horizontally scalable.

---

# AI Boundary

AI Providers perform:

- language generation
- vision analysis
- transcription
- clip selection
- subtitle generation
- style inference

AI providers do not own business rules.

Business decisions remain inside AI Clip Agent.

---

# Database Boundary

Database stores:

- Productions
- Assets
- Clips
- Styles
- Render Jobs
- Users
- Workspaces

Database should never contain workflow logic.

---

# Storage Boundary

Storage manages:

- uploads
- generated assets
- exports
- thumbnails
- temporary files

Storage is replaceable.

---

# Render Boundary

Rendering responsibilities:

- video assembly
- subtitle burn-in
- transitions
- overlays
- audio mixing
- export

Rendering should remain independent from workflow orchestration.

---

# Review Boundary

Review Workspace owns:

- approval
- regeneration
- comments
- quality validation

Review never performs rendering.

---

# Authentication Boundary

Authentication owns:

- identity
- sessions
- permissions

Authentication never owns business entities.

---

# Billing Boundary

Billing owns:

- subscriptions
- credits
- invoices
- usage

Billing should not control production logic.

---

# Observability Boundary

Monitoring includes:

- logs
- metrics
- tracing
- alerts
- queue health
- worker health

Monitoring never changes production state.

---

# Ownership Rules

Every feature must have exactly one owner.

Ownership must not overlap.

Example:

Production State

Owner:

Production Engine

NOT

Frontend

NOT

Database

NOT

Queue

---

# Boundary Violations

The following are considered architecture violations:

- business logic inside frontend
- business logic inside workers
- business logic inside database
- AI providers deciding product behavior
- rendering changing workflow state

These violations require an ADR before implementation.

---

# Future Expansion

Future modules may include:

- Batch Production
- Auto Publishing
- Team Collaboration
- Marketplace
- Plugin System
- AI Agent Marketplace

New modules should integrate through existing boundaries rather than bypass them.

---

# Cross References

Related documents:

- Core Domain
- Domain Model
- AI Pipeline
- Queue Architecture
- API Specification
- Database Model
- State Machine
- Production Workflow

---

# Exit Criteria

The architecture is considered valid only when every subsystem has:

- clearly defined responsibilities
- clear ownership
- explicit boundaries
- no duplicated business logic
- replaceable external dependencies
