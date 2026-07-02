# Video Player

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.4 Review Workspace

---


## Purpose

Define the video preview player used inside the Review Workspace.

The player helps users inspect AI output without exposing a complex timeline editor.

## Responsibilities

The video player must support:

- preview playback
- seek
- pause
- jump to timestamp
- subtitle preview
- clip boundary preview
- playback speed
- current time display

## Non-Goals

The video player must not become:

- a full editing timeline
- a multi-track editor
- a frame-by-frame compositor

## Layout

```text
Video Preview
    ↓
Playback Controls
    ↓
Time / Duration
    ↓
Clip Boundary Indicators
```

## Controls

Required controls:

- Play / Pause
- Seek
- Volume
- Playback speed
- Fullscreen
- Current timestamp
- Jump to next clip
- Jump to previous clip

## Review Interactions

The player should allow:

- adding a comment at current timestamp
- selecting a problematic segment
- jumping from transcript to video
- previewing subtitle timing

## States

- Loading preview
- Ready
- Playing
- Paused
- Buffering
- Failed to load preview

## Exit Criteria

The player is ready when users can inspect generated output quickly and confidently without needing a manual editor.
