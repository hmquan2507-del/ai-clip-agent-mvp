# Deployment

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define deployment direction for AI Clip Agent.

---

## MVP Deployment

Local MVP:

```text
Python backend
  +
Static UI
  +
SQLite
  +
Local filesystem storage
```

New frontend direction:

```text
Next.js frontend
  +
Python API/render backend
```

---

## Production Direction

Recommended services:

- Frontend web app
- API service
- Worker service
- Object storage
- Database
- Queue
- Monitoring/logging

---

## Deployment Units

### Frontend

Hosts product UI.

### API

Handles auth, workspace, production state, upload metadata, and user actions.

### Worker

Runs AI pipeline, render, export, and retry work.

### Storage

Stores source videos and exports.

### Database

Stores product state and metadata.

---

## Deployment Rules

- API should not block on long render work.
- Workers should be separately scalable.
- Source videos and exports should use object storage in production.
- Environment variables must configure AI providers, storage, database, and queue.
