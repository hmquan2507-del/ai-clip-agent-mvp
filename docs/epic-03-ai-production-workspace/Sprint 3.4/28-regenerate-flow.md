# Regenerate Flow

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.4 Review Workspace

---


## Purpose

Define how users request regeneration from the Review Workspace.

Regeneration is the main correction mechanism.

## Regeneration Types

Supported regeneration levels:

- regenerate full Production
- regenerate selected clip
- regenerate transcript segment
- regenerate subtitles
- regenerate AI suggestions
- regenerate style application

## User Flow

```text
Select Issue
    ↓
Choose Regenerate
    ↓
Select Scope
    ↓
Confirm
    ↓
Production returns to processing
    ↓
New output becomes reviewable
```

## Confirmation Rules

Before regeneration, show:

- what will be regenerated
- what will be preserved
- estimated time
- possible cost impact

## Preserve Rules

Regeneration should preserve:

- original source video
- user comments
- previous output history
- accepted suggestions where possible

## States

- Regeneration requested
- Regeneration queued
- Regeneration processing
- Regeneration completed
- Regeneration failed

## Exit Criteria

Users can correct AI output without needing manual editing.
