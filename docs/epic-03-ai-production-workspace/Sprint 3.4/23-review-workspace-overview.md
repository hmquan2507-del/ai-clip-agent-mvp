# Review Workspace Overview

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.4 Review Workspace

---


## Purpose

Define the Review Workspace as the primary place where users review AI-generated production output.

The Review Workspace is not a professional timeline editor. It is a guided review environment.

## User Goal

The user wants to quickly answer:

- Is this AI-generated video good enough?
- What should be regenerated?
- Can this Production move to export?

## Product Principle

The default action is:

```text
Review
    ↓
Approve
    ↓
Export
```

Manual editing should exist only as a correction layer.

## Entry Conditions

A Production can enter Review Workspace when:

- source video has been uploaded
- AI processing has produced reviewable output
- at least one clip, transcript, subtitle, or preview is available

## Main Layout

```text
Header
    ├── Production title
    ├── Status
    ├── Save state
    └── Primary action

Main Area
    ├── Video Player
    ├── Transcript Panel
    ├── AI Suggestions
    └── Review Actions
```

## Primary Actions

- Play preview
- Inspect transcript
- Inspect subtitle timing
- Review AI suggestions
- Add comments
- Regenerate
- Approve

## Exit Conditions

The user exits Review Workspace through:

- Approve to Export
- Regenerate and return to Production Center
- Save draft and leave
- Cancel review

## Cross References

- specs/01-product/product-principles.md
- specs/02-workflows/review-workflow.md
- specs/03-ai/ai-pipeline.md
- specs/06-data/state-machine.md
