# Product Principles

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

These principles guide product decisions for AI Clip Agent.

When a feature idea creates conflict, choose the option that best supports these principles.

---

## 1. AI First

AI should perform the work before asking the user to configure details.

The user should not start from an empty editor. The user should start from AI-generated output.

---

## 2. Production First

The product is centered around Productions, not admin dashboards and not manual projects.

A Production represents the full workflow from source video to reviewed export.

---

## 3. Review Instead Of Edit

The default user action is review, approve, regenerate, or export.

Manual editing exists only as a correction layer after AI output.

---

## 4. Automation Over Configuration

Avoid asking users to make too many choices before AI runs.

Prefer smart defaults, style presets, and automatic decisions.

---

## 5. Time Saved Is The Core Value

Every product decision should answer one question:

Does this save the user editing time?

If a feature does not reduce production time, reduce manual work, or improve review speed, it is lower priority.

---

## 6. One Clear Flow

The primary flow is:

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

Screens should support this flow instead of distracting from it.

---

## 7. Style Is A System

Styles are reusable production recipes, not only visual themes.

Each style controls subtitle behavior, motion, zoom, B-roll, sound FX, music, pacing, and CTA.

---

## 8. Quality Must Be Reviewable

AI output must be easy to inspect.

Users should understand why a clip was selected, what edits were applied, and what can be regenerated.

---

## 9. Build For Scale Later, But Do Not Fake It Now

The MVP can be simple, but the domain model should not block future SaaS needs such as workspaces, credits, render workers, billing, organizations, analytics, and automation.

---

## 10. Specification Before Implementation

For product features, follow:

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
