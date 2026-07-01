# Queue Architecture

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define the queue direction for AI and render work.

Long-running production tasks should not block the web request.

---

## Queue Jobs

Queue work should include:

- Transcript job
- Scene detection job
- Speaker detection job
- Highlight detection job
- Clip selection job
- Style application job
- Subtitle job
- B-roll planning job
- Music planning job
- Sound FX planning job
- Render job
- Export job

---

## Job Statuses

```text
pending
running
succeeded
failed
retrying
cancelled
skipped
```

---

## MVP Direction

Current MVP supports `RENDER_MODE=sync` and `RENDER_MODE=queue`.

Keep this behavior while evolving toward production queue architecture.

---

## Worker Rules

- Worker picks pending jobs.
- Worker updates progress and status.
- Worker stores errors.
- Worker supports retry where safe.
- Worker should be idempotent where possible.

---

## Retry Policy

Retry is allowed for:

- Provider timeout
- Temporary storage failure
- Render process failure
- Queue worker crash

Retry is not automatic for:

- Unsupported file
- Missing source video
- Invalid style config
- Invalid user request

---

## Future Direction

Use dedicated queues for:

- AI pipeline
- Render
- Export
- Notifications

This supports scaling workers separately by workload.
