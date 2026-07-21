"use client";

import {
  useContext,
} from "react";

import type {
  AISuggestion,
  EditableTimeline,
  ReviewRuntimeSessionSnapshot,
} from "../api";

import {
  ReviewWorkspaceContext,
} from "./context";

import type {
  ReviewAISuggestionActions,
  ReviewAISuggestionView,
  ReviewTimelineClipboardActions,
  ReviewTimelineCommandActions,
  ReviewTimelineSelectionActions,
  ReviewWorkspaceActions,
  ReviewWorkspaceContextValue,
  ReviewWorkspaceSessionView,
  ReviewWorkspaceSnapshotView,
  ReviewWorkspaceStatusView,
} from "./contracts";

export function useReviewAICommandActions() {
  const { submitAICommand } = useReviewWorkspace().actions;
  return { submitAICommand };
}

export function useReviewAICommandSubmission() {
  const {
    aiCommandSubmissionPending,
    lastAICommandSubmission,
  } = useReviewWorkspaceState();
  return {
    pending: aiCommandSubmissionPending,
    response: lastAICommandSubmission,
    submission:
      lastAICommandSubmission?.submission ?? null,
  };
}

export function useReviewWorkspace():
  ReviewWorkspaceContextValue {
  const context = useContext(
    ReviewWorkspaceContext,
  );

  if (!context) {
    throw new Error(
      "useReviewWorkspace must be used inside ReviewWorkspaceProvider.",
    );
  }

  return context;
}

export function useReviewWorkspaceState() {
  return useReviewWorkspace().state;
}

export function useReviewWorkspaceActions():
  ReviewWorkspaceActions {
  return useReviewWorkspace().actions;
}

export function useReviewTimelineSelectionActions():
  ReviewTimelineSelectionActions {
  return useReviewWorkspace().actions;
}

export function useReviewTimelineCommands():
  ReviewTimelineCommandActions {
  return useReviewWorkspace().actions;
}

export function useReviewTimelineClipboard():
  ReviewTimelineClipboardActions {
  return useReviewWorkspace().actions;
}

export function useReviewAISuggestionActions():
  ReviewAISuggestionActions {
  return useReviewWorkspace().actions;
}

export function useReviewAISuggestions():
  ReviewAISuggestionView {
  const {
    pendingOperation,
    pendingSuggestionOperation,
    suggestionSnapshot,
  } = useReviewWorkspaceState();

  const suggestions =
    suggestionSnapshot?.read_model.suggestions ?? [];

  const selectedSuggestionId =
    suggestionSnapshot
      ?.read_model.selected_suggestion_id ?? null;

  const selectedSuggestion =
    suggestions.find(
      (suggestion) =>
        suggestion.suggestion_id ===
        selectedSuggestionId,
    ) ?? null;

  return {
    snapshot: suggestionSnapshot,
    suggestions,
    selectedSuggestion,
    available: suggestionSnapshot !== null,
    pending: pendingOperation === "ai_suggestion",
    operation: pendingSuggestionOperation,
    lifecycleRevision:
      suggestionSnapshot?.lifecycle_revision ?? null,
    timelineRevision:
      suggestionSnapshot?.timeline_revision ?? null,
  };
}

export function useSelectedAISuggestion():
  AISuggestion | null {
  return useReviewAISuggestions().selectedSuggestion;
}

export function useReviewWorkspaceStatus():
  ReviewWorkspaceStatusView {
  const {
    status,
    pendingOperation,
    pendingCommand,
    pendingClipboardOperation,
    pendingSuggestionOperation,
    aiCommandSubmissionPending,
    error,
  } = useReviewWorkspaceState();

  return {
    status,
    pendingOperation,
    pendingCommand,
    pendingClipboardOperation,
    pendingSuggestionOperation,
    aiCommandSubmissionPending,

    idle:
      status === "idle",

    loading:
      status === "opening",

    ready:
      status === "ready",

    refreshing:
      status === "refreshing",

    resetting:
      status === "resetting",

    selecting:
      status === "selecting",

    executing:
      status === "executing",

    executingClipboard:
      pendingOperation ===
      "clipboard_command",

    suggesting:
      pendingOperation === "ai_suggestion",

    submittingCommand:
      pendingOperation === "ai_command_submission",

    closing:
      status === "closing",

    closed:
      status === "closed",

    failed:
      status === "error",

    error,
  };
}

export function useReviewWorkspaceSession():
  ReviewWorkspaceSessionView {
  const {
    productionId,
    sessionId,
    session,
  } = useReviewWorkspaceState();

  return {
    productionId,
    sessionId,
    session,
  };
}

export function useReviewWorkspaceSnapshot():
  ReviewWorkspaceSnapshotView {
  const snapshot =
    useReviewWorkspaceState()
      .snapshot;

  return {
    snapshot,
    available:
      snapshot !== null,
  };
}

export function useReviewSnapshot():
  ReviewRuntimeSessionSnapshot | null {
  return useReviewWorkspaceState()
    .snapshot;
}

export function useReviewTimeline():
  EditableTimeline | null {
  return (
    useReviewWorkspaceState()
      .snapshot?.timeline ?? null
  );
}

export function useReviewPreview() {
  return (
    useReviewWorkspaceState()
      .snapshot?.preview ?? null
  );
}

export function useReviewSelection() {
  return (
    useReviewWorkspaceState()
      .snapshot?.selection ?? null
  );
}

export function useReviewHistory() {
  return (
    useReviewWorkspaceState()
      .snapshot?.history ?? null
  );
}

export function useReviewClipboard() {
  return (
    useReviewWorkspaceState()
      .snapshot?.clipboard ?? null
  );
}
