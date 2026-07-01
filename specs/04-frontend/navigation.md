# Navigation

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define navigation for the product UI.

Navigation should support the AI production flow instead of exposing every module inside one dashboard.

---

## Main Navigation

Primary routes:

```text
/home
/upload
/ai-queue
/review
/export
/productions
/styles
/settings
```

Optional later routes:

```text
/analytics
/billing
/team
/automation
```

---

## Route Intent

### Home

Entry point for starting or resuming productions.

Should show:

- Start Production
- Recent productions
- Current active production states

### Upload

Upload source video and start production.

### AI Queue

Show processing stages and progress.

### Review

Review generated clips, approve, reject, or regenerate.

### Export

Download or publish completed outputs.

### Productions

List all productions.

### Styles

Browse and select production styles.

### Settings

Account, workspace, storage, provider, and API configuration.

---

## Sidebar Behavior

- Use links, not static buttons.
- Active state follows the current route.
- Do not scroll to sections on one long page.
- Each route should render one focused page.

---

## MVP Routing Decision

Use the Next.js frontend in `frontend/` for product navigation.

The old static UI remains a reference for existing upload/render logic until migrated.
