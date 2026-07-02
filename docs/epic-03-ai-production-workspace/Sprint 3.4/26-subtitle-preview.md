# Subtitle Preview

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.4 Review Workspace

---


## Purpose

Define how subtitles are previewed during review.

Subtitles are part of the AI-generated output and should be easy to inspect before export.

## Responsibilities

Subtitle preview must support:

- text preview
- timing preview
- line breaks
- overflow detection
- style preview
- language display

## User Goals

Users need to know:

- Are subtitles readable?
- Are they timed correctly?
- Do they match the selected style?
- Do they need regeneration?

## Display Rules

Subtitle preview should show:

- current active subtitle
- upcoming subtitle
- style applied
- timing boundaries

## Quality Warnings

Show warnings when:

- subtitle text is too long
- subtitle timing is too short
- subtitle overlaps are detected
- confidence is low
- language mismatch exists

## Allowed Actions

- Regenerate subtitle
- Flag subtitle issue
- Jump to subtitle timestamp
- Preview alternate style

## Non-Goals

This is not a full subtitle editor in the MVP.

Manual subtitle editing may be added later as an advanced correction layer.
