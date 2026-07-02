# Quality Indicators

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.4 Review Workspace

---


## Purpose

Define quality indicators shown during review.

Quality indicators help users make fast decisions without inspecting every detail manually.

## Indicator Types

Possible indicators:

- transcript confidence
- subtitle timing quality
- audio clarity
- clip selection confidence
- style consistency
- render readiness
- export readiness

## Display

Indicators may appear as:

- badges
- warnings
- score cards
- inline alerts
- checklist items

## Severity

Severity levels:

- Info
- Warning
- Blocking

## Blocking Issues

Examples:

- no preview generated
- transcript failed
- no clips selected
- render cannot start
- source asset missing

## User Actions

Users can:

- inspect issue
- regenerate affected part
- dismiss non-blocking warning
- approve when no blockers remain
