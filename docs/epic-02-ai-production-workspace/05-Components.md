# Components - AI Production Workspace

Status: Active
Owner: Ho Quan
Last Updated: 2026-07-01
Related Epic: EPIC 2.2

---

## Layout Components

- AppShell
- Sidebar
- Topbar
- PageHeader
- EmptyState
- ErrorState
- LoadingState

---

## Production Components

- ProductionCard
- ProductionStatusBadge
- ProductionStageStepper
- RecentProductionsList

---

## Upload Components

- UploadDropzone
- FilePreview
- StyleSelector
- ObjectiveInput
- UploadProgress

---

## AI Queue Components

- PipelineStageList
- PipelineStageItem
- QueueProgress
- RetryStageButton

---

## Review Components

- GeneratedClipList
- GeneratedClipCard
- ClipPreview
- AIReasonPanel
- EditPlanPanel
- ReviewActions
- RegenerateMenu

---

## Export Components

- ApprovedClipList
- RenderJobCard
- ExportOutputCard
- DownloadButton

---

## Component Rules

- Components should be product-specific before becoming generic.
- Repeated production objects can use cards.
- Do not nest cards inside cards.
- Keep one primary action per screen.
