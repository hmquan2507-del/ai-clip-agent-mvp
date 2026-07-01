# Docker

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define containerization direction for AI Clip Agent.

---

## Docker Services

Future Docker setup should include:

- frontend
- api
- worker
- database
- queue
- object-storage-compatible dev service when needed

---

## MVP Direction

Docker is not required before the core production workflow is proven.

Prepare for Docker by keeping:

- Frontend separated in `frontend/`
- Backend runnable from root
- Worker runnable separately
- Configuration via environment variables

---

## Future Compose Shape

```text
frontend
api
worker
postgres
redis
object-storage
```

---

## Container Rules

- Do not bake secrets into images.
- FFmpeg must be available in worker images.
- AI provider keys come from environment variables.
- Source videos and outputs should use mounted dev volumes or object storage.
