"use client";

import { useCallback } from "react";

import {
  ReviewWorkspaceProvider,
  useReviewWorkspaceActions,
  useReviewWorkspaceState,
} from "../react";
import { ReviewEditorShell } from "../shell";
import { buildReviewEditorViewModel } from "./adapters";
import {
  ReviewWorkspaceClosedState,
  ReviewWorkspaceErrorState,
  ReviewWorkspaceLoadingState,
} from "./runtime-states";

export interface ReviewRuntimeWorkspaceProps {
  productionId: string;
}

export function ReviewRuntimeWorkspace({
  productionId,
}: ReviewRuntimeWorkspaceProps) {
  return (
    <ReviewWorkspaceProvider productionId={productionId}>
      <ReviewRuntimeWorkspaceContent />
    </ReviewWorkspaceProvider>
  );
}

function ReviewRuntimeWorkspaceContent() {
  const state = useReviewWorkspaceState();
  const actions = useReviewWorkspaceActions();

  const retry = useCallback(() => {
    void actions.open({ replace_existing: true }).catch(() => undefined);
  }, [actions]);

  const refresh = useCallback(() => {
    void actions.refresh().catch(() => undefined);
  }, [actions]);

  const reopen = useCallback(() => {
    actions.clear();
    void actions.open({ replace_existing: true }).catch(() => undefined);
  }, [actions]);

  if (
    state.status === "idle" ||
    state.status === "opening" ||
    (state.status === "ready" && !state.snapshot)
  ) {
    return <ReviewWorkspaceLoadingState />;
  }

  if (state.status === "closed") {
    return (
      <ReviewWorkspaceClosedState
        reopening={state.pendingOperation === "open"}
        onReopen={reopen}
      />
    );
  }

  if (state.status === "error" || !state.snapshot) {
    return (
      <ReviewWorkspaceErrorState
        error={state.error}
        retrying={state.pendingOperation === "open"}
        onRetry={retry}
      />
    );
  }

  const view = buildReviewEditorViewModel(state);

  return (
    <ReviewEditorShell
      view={view}
      refreshing={state.status === "refreshing"}
      onRefresh={refresh}
    />
  );
}

