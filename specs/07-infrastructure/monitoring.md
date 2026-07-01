# Monitoring

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define monitoring direction for AI Clip Agent.

Monitoring should help understand production quality, render reliability, cost, and user time saved.

---

## What To Monitor

### Product Flow

- Productions started
- Productions completed
- Time to first AI output
- Time to export
- Approval rate
- Regeneration rate

### AI Pipeline

- Transcript success/failure
- Highlight detection success/failure
- Clip selection quality
- AI provider errors
- AI cost per production

### Render

- Render jobs pending/running/failed
- Render duration
- Retry count
- Output validation failures

### System

- API errors
- Worker errors
- Queue depth
- Storage errors
- Database errors

---

## Logging Requirements

Logs should include:

- production_id
- workspace_id when available
- job_id
- stage
- status
- error code
- retry count

Do not log secrets, API keys, or private video contents.

---

## MVP Direction

Start with structured logs and database status fields.

Full observability can come in EPIC 10 Production Ready.
