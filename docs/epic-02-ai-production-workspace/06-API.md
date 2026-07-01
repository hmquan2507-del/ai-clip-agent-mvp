# API - AI Production Workspace

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC 2.2

---

## API Direction

The UI should use production language even while the MVP backend still uses job language internally.

---

## Required API Surface

### Home

```text
GET /api/dashboard
```

Temporary MVP source for recent productions and status.

Future:

```text
GET /api/productions/recent
```

---

### Upload

```text
POST /api/upload
```

Creates a production from uploaded video.

---

### Production Detail

```text
GET /api/jobs/:id
```

Temporary MVP source for production detail.

Future:

```text
GET /api/productions/:id
```

---

### Review Actions

Future:

```text
POST /api/clips/:id/approve
POST /api/clips/:id/reject
POST /api/clips/:id/regenerate
```

MVP can map approve/reject to frontend state first if backend support is not ready.

---

### Export

```text
POST /api/render
```

Creates render tasks for selected clips.

---

## API Migration Rule

Keep existing backend endpoints working while the Next.js UI is built.

Introduce production-named endpoints after the workspace flow is stable.
