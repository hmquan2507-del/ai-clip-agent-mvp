# Acceptance Criteria - AI Production Workspace

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC 2.2

---

## Product Acceptance

- Workspace follows Home -> Upload -> AI Queue -> Review -> Export.
- Home is not an admin dashboard.
- Each major category is a separate page.
- User can understand the production flow without reading docs.

---

## Frontend Acceptance

- Sidebar links navigate to routes.
- Active nav state matches current route.
- Home does not contain every module.
- Upload is its own page.
- AI Queue is its own page.
- Review is its own page.
- Export is its own page.
- Layout works on desktop and mobile.

---

## Integration Acceptance

- Existing MVP backend can still run.
- Existing upload/render logic is not broken.
- New frontend can call backend APIs or has a clear API migration path.

---

## Quality Acceptance

- `npm run lint` passes in frontend.
- Root `npm run check` passes.
- No empty EPIC 2.2 docs.
- No product direction contradicts AI-first review workflow.
