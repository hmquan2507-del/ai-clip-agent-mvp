# Prompt Library

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define how prompts are organized, versioned, and used.

Prompts are product assets and should be treated as part of the AI system.

---

## Prompt Categories

- Transcript cleanup
- Highlight detection
- Clip selection
- Hook generation
- Caption generation
- CTA generation
- Subtitle rewriting
- B-roll planning
- Music planning
- Sound FX planning
- Style application
- Regeneration

---

## Prompt Requirements

Prompts should define:

- Task
- Input format
- Output JSON schema
- Style context
- User objective
- Constraints
- Fallback behavior

---

## Output Rules

AI output should be structured when used by the app.

Prefer JSON for:

- Clip selection
- Edit plans
- Style plans
- Subtitle plans
- Regeneration output

---

## Versioning

Each prompt should eventually have:

- Prompt ID
- Version
- Task
- Model compatibility
- Expected input
- Expected output
- Last updated date

---

## MVP Prompt Priority

1. Highlight and clip selection
2. Hook, caption, CTA
3. Style edit plan
4. Subtitle rewriting
5. Regeneration
