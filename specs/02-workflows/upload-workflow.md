# Upload Workflow

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define how users upload source videos into a Production.

---

## Workflow

```text
Start New Production
  ↓
Select Source Video
  ↓
Validate File
  ↓
Upload
  ↓
Extract Metadata
  ↓
Choose / Confirm Style
  ↓
Start AI Queue
```

---

## Inputs

- Video file
- Production title
- Optional niche
- Optional objective
- Optional style

---

## Validation

Validate:

- File type
- File size
- Duration
- Video stream exists
- Audio stream exists when transcript is needed
- Upload completion

---

## Metadata To Extract

- Duration
- Width
- Height
- FPS
- Codec
- Audio availability
- Orientation
- File size
- MIME type
- Storage key

---

## User Feedback

During upload, show:

- Upload progress
- Processing state
- Clear errors
- Retry option

---

## Success State

The Production has a stored Source Video and can enter AI Queue.

---

## Failure States

- Unsupported file
- Upload interrupted
- Storage failed
- Metadata extraction failed
- Video has no usable stream

Failures should not create duplicate productions unless the user starts a new upload.
