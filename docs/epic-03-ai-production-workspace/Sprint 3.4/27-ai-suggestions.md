# AI Suggestions

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.4 Review Workspace

---


## Purpose

Define how AI suggestions are displayed during review.

AI suggestions help users understand what AI selected and why.

## Suggestion Types

Possible suggestions:

- highlight clip
- B-roll
- subtitle style
- music
- sound effect
- zoom
- CTA
- pacing adjustment

## Suggestion Card

Each suggestion should include:

- suggestion type
- affected timestamp or segment
- reason
- confidence
- action buttons

## User Actions

Users can:

- accept suggestion
- reject suggestion
- regenerate suggestion
- inspect reason
- comment on suggestion

## Explainability

Every suggestion should answer:

```text
Why did AI suggest this?
```

## States

- Suggestions loading
- Suggestions ready
- No suggestions
- Suggestions failed

## Cross References

- specs/03-ai/style-engine.md
- specs/03-ai/model-routing.md
- specs/03-ai/prompt-library.md
