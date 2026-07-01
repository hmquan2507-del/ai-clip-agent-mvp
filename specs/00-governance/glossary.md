# Glossary

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

This glossary defines shared product language for AI Clip Agent.

Use these terms consistently across specs, UI, API, data model, and implementation.

---

## Core Terms

### AI Clip Agent

The product name.

An AI Video Production Platform that turns source videos into reviewed and exported short-form videos.

### AI Video Production Platform

A system where AI performs the video production workflow and the user reviews the result.

### Production

The core domain object.

A Production represents the full lifecycle from source video upload to final export.

### Workspace

A container for users, productions, assets, styles, credits, billing, and organization settings.

### Source Video

The original uploaded video file.

### AI Pipeline

The sequence of AI and processing steps that transform a source video into generated clips.

### AI Queue

The user-facing state where the system is processing uploaded videos through the AI pipeline.

### Generated Clip

A short-form video candidate created by the AI pipeline.

### Review Workspace

The screen where users review AI output, approve clips, request regeneration, make small corrections, and export.

### Export

The final rendered video output ready for download or publishing.

---

## AI Terms

### Transcript

Text generated from source video audio.

### Scene Detection

Detecting visual scene changes or meaningful visual segments.

### Speaker Detection

Identifying speaker changes or speaker segments.

### Highlight Detection

Finding moments likely to be useful, emotional, educational, persuasive, or viral.

### Clip Selection

Choosing the best segments to convert into short-form clips.

### Style Engine

The system that applies reusable production styles to clips.

### Style

A reusable recipe that defines subtitle behavior, motion, zoom, B-roll, music, sound FX, pacing, and CTA.

### Prompt Library

Versioned prompts used by the AI pipeline.

### Model Routing

Rules for choosing AI models by task, cost, quality, and fallback needs.

---

## Review Terms

### Approve

Accept an AI-generated clip for export.

### Regenerate

Ask AI to produce a new version of a clip or edit layer.

### Reject

Remove a generated clip from the final output set.

### Needs Changes

Mark a clip as useful but requiring a correction.

---

## Business Terms

### Credits

Usage units consumed by AI processing, rendering, storage, or export.

### Subscription

A recurring plan that gives the user access to usage limits and features.

### Organization

A shared account container for teams, agencies, and businesses.
