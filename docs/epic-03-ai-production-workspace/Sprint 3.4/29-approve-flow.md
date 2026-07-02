# Approve Flow

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.4 Review Workspace

---


## Purpose

Define how users approve AI output and move a Production toward export.

Approval is the final review gate before rendering/export.

## Approval Conditions

A Production can be approved when:

- preview is available
- required AI outputs exist
- no blocking errors remain
- user confirms review completion

## User Flow

```text
Review Output
    ↓
Click Approve
    ↓
Validation
    ↓
Confirm Approval
    ↓
Production state changes to Approved
    ↓
Move to Export
```

## Validation

Before approval, validate:

- preview exists
- selected clips exist
- subtitles are generated
- export path is possible
- Production is not currently regenerating

## Confirmation

The approval confirmation should explain:

- approval locks current review output
- user can still create a new version later
- export will use approved output

## States

- Ready to approve
- Approval blocked
- Approving
- Approved
- Approval failed

## Cross References

- specs/06-data/state-machine.md
- specs/02-workflows/export-workflow.md
