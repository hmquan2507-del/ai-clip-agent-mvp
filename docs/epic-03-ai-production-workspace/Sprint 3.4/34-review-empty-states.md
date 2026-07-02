# Review Empty States

Status: Draft
Owner: Ho Quan
Version: 0.1
Related Epic: EPIC-03 AI Production Workspace Blueprint
Related Sprint: Sprint 3.4 Review Workspace

---


## Purpose

Define empty, loading, and unavailable states for Review Workspace.

## Empty State Types

Possible states:

- AI output not ready
- no clips found
- transcript unavailable
- subtitles unavailable
- suggestions unavailable
- preview unavailable
- comments empty

## Loading States

Loading states include:

- loading preview
- loading transcript
- loading suggestions
- loading quality indicators

## Error States

Error states include:

- preview failed
- transcript failed
- subtitles failed
- suggestions failed
- approval blocked
- regeneration failed

## Empty State Message Rules

Messages should:

- explain what happened
- avoid blaming the user
- show next action
- link to Production Center when needed

## Example

```text
AI output is not ready yet.

Your Production is still being processed. You can return to the Production Center to track progress.
```

## Exit Criteria

Users should never see a blank or confusing Review Workspace.
