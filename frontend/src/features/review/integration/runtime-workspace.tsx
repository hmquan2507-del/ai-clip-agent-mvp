"use client";

import {
  useCallback,
} from "react";

import {
  ReviewWorkspaceProvider,
  useReviewWorkspaceActions,
  useReviewWorkspaceState,
} from "../react";
import type {
  ReviewWorkspaceActions,
} from "../react";
import type {
  ReviewWorkspaceRuntimeState,
} from "../state";

import {
  ReviewEditorShell,
} from "../shell";

import {
  buildReviewEditorViewModel,
} from "./adapters";
import {
  useReviewRuntimeClipDrag,
} from "./use-runtime-clip-drag";

import type {
  ReviewTimelineClipboardIntent,
  ReviewTimelineCommandIntent,
  ReviewTimelineSelectionIntent,
} from "./contracts";

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
    <ReviewWorkspaceProvider
      productionId={productionId}
    >
      <ReviewRuntimeWorkspaceContent />
    </ReviewWorkspaceProvider>
  );
}

function ReviewRuntimeWorkspaceContent() {
  const state =
    useReviewWorkspaceState();

  const actions =
    useReviewWorkspaceActions();

  const retry = useCallback(() => {
    void actions.open({
      replace_existing: true,
    }).catch(() => undefined);
  }, [actions]);

  const refresh = useCallback(() => {
    void actions.refresh()
      .catch(() => undefined);
  }, [actions]);

  const reopen = useCallback(() => {
    actions.clear();

    void actions.open({
      replace_existing: true,
    }).catch(() => undefined);
  }, [actions]);

  const selectClip = useCallback(
    (
      intent:
        ReviewTimelineSelectionIntent,
    ) => {
      void actions.selectClip({
        clip_id:
          intent.clipId,
        additive:
          intent.additive,
        move_cursor:
          intent.moveCursor,
      }).catch(() => undefined);
    },
    [actions],
  );

  const undoTimeline =
    useCallback(() => {
      void actions.undoTimeline()
        .catch(() => undefined);
    }, [actions]);

  const redoTimeline =
    useCallback(() => {
      void actions.redoTimeline()
        .catch(() => undefined);
    }, [actions]);

  const executeTimelineCommand =
    useCallback(
      (
        intent:
          ReviewTimelineCommandIntent,
      ) => {
        switch (
          intent.operation
        ) {
          case "split_clip":
            void actions.splitClip({
              clip_id:
                intent.clipId,
              split_time:
                intent.splitTime,
            }).catch(
              () => undefined,
            );
            return;

          case "duplicate_clip":
            void actions.duplicateClip({
              clip_id:
                intent.clipId,
            }).catch(
              () => undefined,
            );
            return;

          case "delete_clip":
            void actions.deleteClip({
              clip_id:
                intent.clipId,
              close_gap: false,
            }).catch(
              () => undefined,
            );
            return;

          case "close_gap":
            void actions.closeGap({
              track_id:
                intent.trackId,
              gap_start:
                intent.gapStart,
              gap_end:
                intent.gapEnd,
            }).catch(
              () => undefined,
            );
        }
      },
      [actions],
    );

  const executeClipboardCommand =
    useCallback(
      (
        intent:
          ReviewTimelineClipboardIntent,
      ) => {
        switch (
          intent.operation
        ) {
          case "copy":
            void actions.copyTimelineClips({
              clip_ids:
                [...intent.clipIds],
            }).catch(
              () => undefined,
            );
            return;

          case "cut":
            void actions.cutTimelineClips({
              clip_ids:
                [...intent.clipIds],
            }).catch(
              () => undefined,
            );
            return;

          case "paste":
            void actions.pasteTimelineClips({
              at_time:
                intent.atTime,
            }).catch(
              () => undefined,
            );
            return;

          case "restore_history":
            void actions.restoreTimelineClipboardHistory({
              entry_id:
                intent.entryId,
            }).catch(
              () => undefined,
            );
            return;

          case "clear_content":
            void actions.clearTimelineClipboard()
              .catch(
                () => undefined,
              );
            return;

          case "clear_history":
            void actions.clearTimelineClipboardHistory()
              .catch(
                () => undefined,
              );
        }
      },
      [actions],
    );

  if (
    state.status === "idle" ||
    state.status === "opening" ||
    (
      state.status === "ready" &&
      !state.snapshot
    )
  ) {
    return (
      <ReviewWorkspaceLoadingState />
    );
  }

  if (
    state.status === "closed"
  ) {
    return (
      <ReviewWorkspaceClosedState
        reopening={
          state.pendingOperation ===
          "open"
        }
        onReopen={reopen}
      />
    );
  }

  if (!state.snapshot) {
    return (
      <ReviewWorkspaceErrorState
        error={state.error}
        retrying={
          state.pendingOperation ===
          "open"
        }
        onRetry={retry}
      />
    );
  }

  return (
    <ReviewRuntimeWorkspaceEditor
      state={state}
      actions={actions}
      onRefresh={refresh}
      onSelectClip={selectClip}
      onUndo={undoTimeline}
      onRedo={redoTimeline}
      onTimelineCommand={
        executeTimelineCommand
      }
      onClipboardCommand={
        executeClipboardCommand
      }
    />
  );
}

interface ReviewRuntimeWorkspaceEditorProps {
  state: ReviewWorkspaceRuntimeState;
  actions: ReviewWorkspaceActions;
  onRefresh(): void;
  onUndo(): void;
  onRedo(): void;
  onSelectClip(
    intent: ReviewTimelineSelectionIntent,
  ): void;
  onTimelineCommand(
    intent: ReviewTimelineCommandIntent,
  ): void;
  onClipboardCommand(
    intent: ReviewTimelineClipboardIntent,
  ): void;
}

function ReviewRuntimeWorkspaceEditor({
  state,
  actions,
  onRefresh,
  onUndo,
  onRedo,
  onSelectClip,
  onTimelineCommand,
  onClipboardCommand,
}: ReviewRuntimeWorkspaceEditorProps) {
  const view = buildReviewEditorViewModel(
    state,
  );
  const commandPending =
    state.status === "executing" &&
    state.pendingOperation ===
      "timeline_command";
  const clipboardPending =
    state.status === "executing" &&
    state.pendingOperation ===
      "clipboard_command";
  const selecting =
    state.status === "selecting";

  const clipDrag =
    useReviewRuntimeClipDrag({
      productionId:
        view.header.productionId,
      view,
      disabled:
        selecting ||
        commandPending ||
        clipboardPending,
      moveClip: actions.moveClip,
    });

  const dropClip = useCallback(() => {
    void clipDrag.drop()
      .catch(() => undefined);
  }, [clipDrag]);

  return (
    <ReviewEditorShell
      view={view}
      refreshing={
        state.status ===
        "refreshing"
      }
      selecting={selecting}
      commandPending={commandPending}
      pendingCommand={
        state.pendingCommand
      }
      clipboardPending={
        clipboardPending
      }
      pendingClipboardOperation={
        state.pendingClipboardOperation
      }
      drag={clipDrag.drag}
      onClipDragStart={clipDrag.begin}
      onClipDragMove={clipDrag.move}
      onClipDragDrop={dropClip}
      onClipDragCancel={clipDrag.cancel}
      onRefresh={onRefresh}
      onSelectClip={onSelectClip}
      onUndo={onUndo}
      onRedo={onRedo}
      onTimelineCommand={
        onTimelineCommand
      }
      onClipboardCommand={
        onClipboardCommand
      }
    />
  );
}
