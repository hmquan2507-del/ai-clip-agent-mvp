# Storage Architecture

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define storage direction for uploaded source videos and exported outputs.

---

## Storage Types

- Source videos
- Rendered outputs
- Thumbnails
- Subtitle files
- Style assets
- B-roll assets
- Music assets

---

## MVP Direction

Local MVP can use filesystem storage under `data/jobs/`.

Production should use object storage such as S3 or R2.

---

## Storage Rules

- Database stores metadata and storage keys, not binary video content.
- Large video files should not be stored directly in the database.
- Source video and output file ownership must be tied to workspace/production.
- URLs should expire when needed.

---

## Metadata

Store:

- storage_provider
- storage_key
- storage_url
- file_size
- mime_type
- duration
- width
- height
- checksum when available

---

## Future Direction

Use direct browser upload:

```text
Browser
  ↓
Presigned Upload URL
  ↓
Object Storage
  ↓
API stores metadata
```

Render workers read from object storage and write outputs back to object storage.
