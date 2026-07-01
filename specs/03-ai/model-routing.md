# Model Routing

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define how AI Clip Agent chooses models for different tasks.

Model routing should balance quality, speed, cost, and fallback reliability.

---

## Routing Principles

- Use strong models for creative judgment and clip selection.
- Use cheaper models for repeatable formatting tasks.
- Use local or deterministic fallback when AI provider is unavailable.
- Keep output schemas stable even when models change.

---

## Provider Direction

Supported provider direction:

- OpenAI
- Gemini
- Local heuristic fallback

Current MVP config:

```text
AI_SUGGESTION_PROVIDER=auto
OPENAI_API_KEY=
OPENAI_MODEL=
GEMINI_API_KEY=
GEMINI_MODEL=
```

---

## Task Routing

### Highlight Detection

Needs high reasoning quality.

Preferred: strong LLM with transcript and metadata.

Fallback: heuristic scoring.

### Hook / Caption / CTA

Needs creative writing quality.

Preferred: LLM.

Fallback: template generation.

### Subtitle Formatting

Needs consistency.

Preferred: cheaper LLM or deterministic formatting.

### Style Plan

Needs product rules and style consistency.

Preferred: LLM with style schema.

### Render

Not an LLM task.

Use render engine and workers.

---

## Failure Behavior

If selected model fails:

1. Retry if safe.
2. Fall back to alternate provider.
3. Fall back to heuristic or template output.
4. Preserve production state and show recoverable error if no fallback works.

---

## Non-goals

- Hardcoding one provider forever
- Letting model output break product state
- Exposing provider complexity to normal users
