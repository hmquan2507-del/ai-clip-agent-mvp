# API Specification

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define the backend API direction for AI Clip Agent.

The API should support the Production lifecycle.

---

## Core Resources

- Workspace
- Production
- Source Video
- AI Job
- Generated Clip
- Review
- Render Job
- Export
- Style

---

## MVP Endpoints

### Dashboard / Home

```text
GET /api/dashboard
```

Temporary MVP endpoint for account, quota, stats, and recent jobs.

Future direction: replace with production-focused home payload.

### Production Detail

```text
GET /api/jobs/<job_id>
```

Temporary MVP endpoint for opening a job.

Future direction:

```text
GET /api/productions/<production_id>
```

### Upload

```text
POST /api/upload
```

Creates a Production from a source video and starts AI analysis.

### Presigned Upload

```text
POST /api/uploads/presign
```

Creates direct upload target for object storage.

### Render

```text
POST /api/render
```

Creates render jobs for selected clips.

---

## Future API Direction

```text
POST /api/productions
GET /api/productions
GET /api/productions/:id
POST /api/productions/:id/upload
POST /api/productions/:id/start
GET /api/productions/:id/queue
GET /api/productions/:id/clips
POST /api/clips/:id/approve
POST /api/clips/:id/reject
POST /api/clips/:id/regenerate
POST /api/productions/:id/export
GET /api/exports/:id
```

---

## API Rules

- Do not expose internal render worker details to normal users.
- Return stable statuses for production stages.
- Preserve Production state on failures.
- Use structured error responses.
- Keep compatibility while migrating from `job` language to `production` language.

---

## Error Shape

```json
{
  "error": {
    "code": "render_failed",
    "message": "Render failed.",
    "stage": "render",
    "retryable": true
  }
}
```
