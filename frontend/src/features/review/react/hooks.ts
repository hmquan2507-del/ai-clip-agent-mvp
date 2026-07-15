"use client";

import {
  useContext,
} from "react";

import type {
  EditableTimeline,
  ReviewRuntimeSessionSnapshot,
} from "../api";

import {
  ReviewWorkspaceContext,
} from "./context";

import type {
  ReviewTimelineCommandActions,
  ReviewWorkspaceActions,
  ReviewWorkspaceContextValue,
  ReviewWorkspaceSessionView,
  ReviewWorkspaceSnapshotView,
  ReviewWorkspaceStatusView,
} from "./contracts";

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

export function useReviewTimelineCommands():
  ReviewTimelineCommandActions {
  return useReviewWorkspace().actions;
}

export function useReviewWorkspaceStatus():
  ReviewWorkspaceStatusView {
  const {
    status,
    pendingOperation,
    pendingCommand,
    error,
  } = useReviewWorkspaceState();

  return {
    status,
    pendingOperation,
    pendingCommand,
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
    executing:
      status === "executing",
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