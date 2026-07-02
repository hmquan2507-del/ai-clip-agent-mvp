# Transcript Panel

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.4 Review Workspace

---


## Purpose

Define the transcript panel used during review.

The transcript helps users inspect speech recognition quality, jump through the video, and identify segments that need regeneration.

## Responsibilities

The transcript panel must show:

- speaker labels
- timestamps
- transcript text
- active playback segment
- search results
- confidence indicators where available

## User Actions

Users can:

- click transcript text to jump video
- search transcript
- select a segment
- comment on a segment
- flag incorrect text
- request regeneration for selected segment

## Layout

```text
Transcript Header
    ├── Search
    ├── Filter
    └── Confidence Summary

Transcript Body
    ├── Timestamp
    ├── Speaker
    └── Text Segment
```

## States

- Transcript loading
- Transcript ready
- Transcript missing
- Low confidence transcript
- Transcript failed

## Accessibility

Transcript text must be readable and keyboard navigable.

## Cross References

- specs/03-ai/ai-pipeline.md
- specs/03-ai/prompt-library.md
- specs/02-workflows/review-workflow.md
