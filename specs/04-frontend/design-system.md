# Design System

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC-02 Product Specification

---

## Purpose

Define the visual and interaction direction for AI Clip Agent.

The UI should feel like an AI production workspace, not an admin dashboard.

---

## Product Feel

The interface should feel:

- Fast
- Focused
- Modern
- Production-oriented
- AI-first
- Review-first

Avoid:

- Admin dashboard clutter
- Too many charts before product value exists
- Timeline-first editor patterns
- Marketing landing page as the product home

---

## Core Layout Direction

Use a sidebar or compact navigation to move through the production flow:

```text
Home
Upload
AI Queue
Review
Export
Productions
Styles
Settings
```

Home is a product entry point, not an admin analytics dashboard.

---

## Visual Direction

- Dark product workspace
- High contrast content areas
- Clear production status
- Strong primary action per screen
- Cards only for repeated objects such as productions, clips, styles, outputs
- Avoid putting every module on one long dashboard screen

---

## Components

Initial components:

- App shell
- Sidebar navigation
- Production cards
- Upload dropzone
- AI queue status
- Clip review card
- Style selector
- Export card
- Empty state
- Loading state
- Error state

---

## Primary Actions

Each screen should have one obvious primary action.

Examples:

- Home: Start Production
- Upload: Upload Video
- AI Queue: View Progress
- Review: Export Approved Clips
- Export: Download

---

## Accessibility

- Buttons must have clear labels.
- Interactive items must be keyboard reachable.
- Text contrast must be readable on dark backgrounds.
- Loading and error states must be visible.
