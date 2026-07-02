# Render Progress

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.5 Export Experience

---


## Purpose

Define how users track rendering progress after export starts.

## Display

Render progress should show:

- overall progress
- current render stage
- estimated time remaining
- render status
- started time
- last updated time

## Render Stages

Possible stages:

- Preparing assets
- Applying subtitles
- Applying motion
- Mixing audio
- Rendering video
- Finalizing export
- Uploading result
- Completed

## User Actions

During rendering, users can:

- view progress
- leave and return later
- cancel if allowed
- retry failed render

## States

- Queued
- Rendering
- Finalizing
- Completed
- Failed
- Cancelled
