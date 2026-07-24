"use client";

import { useRouter } from "next/navigation";
import { useCallback } from "react";

import {
  buildExportWorkspaceHref,
  extractExportRenderContract,
  storeReviewToExportContract,
} from "../export-workspace";

import {
  ReviewWorkspaceProvider,
  useReviewWorkspaceActions,
  useReviewWorkspaceState,
} from "../review/react";
import type { ReviewWorkspaceActions } from "../review/react";
import type { ReviewWorkspaceRuntimeState } from "../review/state";

import {
  buildReviewEditorViewModel,
  useReviewRuntimeClipDrag,
  useReviewRuntimeClipTrim,
  useReviewRuntimeKeyboardEditing,
} from "../review/integration";
import type {
  ReviewAICommandSubmissionIntent,
  ReviewAISuggestionIntent,
  ReviewTimelineClipboardIntent,
  ReviewTimelineCommandIntent,
  ReviewTimelineSelectionIntent,
} from "../review/integration/contracts";

import { DesktopEditorShell } from "./components/desktop-editor-shell";

/**
 * Runtime Adapter — the ONLY bridge between the untouched Review runtime
 * (ReviewWorkspaceProvider, session hooks, drag/trim/keyboard hooks, view-model
 * adapter) and the brand new Desktop Editor UI. It consumes the exact same
 * public hooks that `features/review/integration/runtime-workspace.tsx` uses,
 * and renders `DesktopEditorShell` instead of the legacy `ReviewEditorShell`.
 *
 * No runtime file is imported-and-modified here — only imported-and-consumed.
 */
export interface DesktopEditorRuntimeAdapterProps {
  productionId: string;
}

export function DesktopEditorRuntimeAdapter({
  productionId,
}: DesktopEditorRuntimeAdapterProps) {
  return (
    <ReviewWorkspaceProvider productionId={productionId}>
      <DesktopEditorRuntimeContent />
    </ReviewWorkspaceProvider>
  );
}

function DesktopEditorRuntimeContent() {
  const state = useReviewWorkspaceState();
  const actions = useReviewWorkspaceActions();

  const retry = useCallback(() => {
    void actions.open({ replace_existing: true }).catch(() => undefined);
  }, [actions]);

  const refresh = useCallback(() => {
    void actions.refresh().catch(() => undefined);
  }, [actions]);

  const selectClip = useCallback(
    (intent: ReviewTimelineSelectionIntent) => {
      void actions
        .selectClip({
          clip_id: intent.clipId,
          additive: intent.additive,
          move_cursor: intent.moveCursor,
        })
        .catch(() => undefined);
    },
    [actions],
  );

  const undoTimeline = useCallback(() => {
    void actions.undoTimeline().catch(() => undefined);
  }, [actions]);

  const redoTimeline = useCallback(() => {
    void actions.redoTimeline().catch(() => undefined);
  }, [actions]);

  const executeTimelineCommand = useCallback(
    (intent: ReviewTimelineCommandIntent) => {
      switch (intent.operation) {
        case "move_clips":
          void actions
            .moveClips({ clip_ids: [...intent.clipIds], delta_time: intent.deltaTime })
            .catch(() => undefined);
          return;
        case "duplicate_clips":
          void actions
            .duplicateClips({ clip_ids: [...intent.clipIds], time_offset: intent.timeOffset })
            .catch(() => undefined);
          return;
        case "delete_clips":
          void actions.deleteClips({ clip_ids: [...intent.clipIds] }).catch(() => undefined);
          return;
        case "split_clip":
          void actions
            .splitClip({ clip_id: intent.clipId, split_time: intent.splitTime })
            .catch(() => undefined);
          return;
        case "duplicate_clip":
          void actions.duplicateClip({ clip_id: intent.clipId }).catch(() => undefined);
          return;
        case "delete_clip":
          void actions
            .deleteClip({ clip_id: intent.clipId, close_gap: false })
            .catch(() => undefined);
          return;
        case "close_gap":
          void actions
            .closeGap({ track_id: intent.trackId, gap_start: intent.gapStart, gap_end: intent.gapEnd })
            .catch(() => undefined);
      }
    },
    [actions],
  );

  const executeClipboardCommand = useCallback(
    (intent: ReviewTimelineClipboardIntent) => {
      switch (intent.operation) {
        case "copy":
          void actions.copyTimelineClips({ clip_ids: [...intent.clipIds] }).catch(() => undefined);
          return;
        case "cut":
          void actions.cutTimelineClips({ clip_ids: [...intent.clipIds] }).catch(() => undefined);
          return;
        case "paste":
          void actions.pasteTimelineClips({ at_time: intent.atTime }).catch(() => undefined);
          return;
        case "restore_history":
          void actions
            .restoreTimelineClipboardHistory({ entry_id: intent.entryId })
            .catch(() => undefined);
          return;
        case "clear_content":
          void actions.clearTimelineClipboard().catch(() => undefined);
          return;
        case "clear_history":
          void actions.clearTimelineClipboardHistory().catch(() => undefined);
      }
    },
    [actions],
  );

  const executeAISuggestionCommand = useCallback(
    (intent: ReviewAISuggestionIntent) => {
      switch (intent.operation) {
        case "refresh_suggestions":
          void actions.refreshAISuggestions().catch(() => undefined);
          return;
        case "select_suggestion":
          void actions
            .selectAISuggestion({ suggestion_id: intent.suggestionId })
            .catch(() => undefined);
          return;
        case "apply_suggestion":
          void actions
            .applyAISuggestion({ suggestion_id: intent.suggestionId })
            .catch(() => undefined);
          return;
        case "dismiss_suggestion":
          void actions
            .dismissAISuggestion({ suggestion_id: intent.suggestionId })
            .catch(() => undefined);
          return;
        case "regenerate_suggestions":
          void actions.regenerateAISuggestions().catch(() => undefined);
      }
    },
    [actions],
  );

  const submitAICommand = useCallback(
    (intent: ReviewAICommandSubmissionIntent) => {
      void actions
        .submitAICommand({ command_text: intent.commandText, client_request_id: intent.clientRequestId })
        .catch(() => undefined);
    },
    [actions],
  );

  const runtimeError =
    state.status === "error" && !state.snapshot
      ? (state.error?.message ?? "Không thể tải phiên chỉnh sửa.")
      : null;

  if (
    state.status === "idle" ||
    state.status === "opening" ||
    (state.status === "ready" && !state.snapshot)
  ) {
    return <DesktopEditorShell view={undefined} pendingCommand={null} pendingClipboardOperation={null} />;
  }

  if (state.status === "closed") {
    return (
      <DesktopEditorShell
        view={undefined}
        pendingCommand={null}
        pendingClipboardOperation={null}
        runtimeError="Phiên chỉnh sửa đã đóng."
        onRefresh={retry}
      />
    );
  }

  if (!state.snapshot) {
    return (
      <DesktopEditorShell
        view={undefined}
        pendingCommand={null}
        pendingClipboardOperation={null}
        runtimeError={runtimeError ?? "Không thể tải phiên chỉnh sửa."}
        onRefresh={retry}
      />
    );
  }

  return (
    <DesktopEditorRuntimeEditor
      state={state}
      actions={actions}
      onRefresh={refresh}
      onSelectClip={selectClip}
      onUndo={undoTimeline}
      onRedo={redoTimeline}
      onTimelineCommand={executeTimelineCommand}
      onClipboardCommand={executeClipboardCommand}
      onAISuggestionCommand={executeAISuggestionCommand}
      onAICommandSubmit={submitAICommand}
    />
  );
}

interface DesktopEditorRuntimeEditorProps {
  state: ReviewWorkspaceRuntimeState;
  actions: ReviewWorkspaceActions;
  onRefresh(): void;
  onUndo(): void;
  onRedo(): void;
  onSelectClip(intent: ReviewTimelineSelectionIntent): void;
  onTimelineCommand(intent: ReviewTimelineCommandIntent): void;
  onClipboardCommand(intent: ReviewTimelineClipboardIntent): void;
  onAISuggestionCommand(intent: ReviewAISuggestionIntent): void;
  onAICommandSubmit(intent: ReviewAICommandSubmissionIntent): void;
}

function DesktopEditorRuntimeEditor({
  state,
  actions,
  onRefresh,
  onUndo,
  onRedo,
  onSelectClip,
  onTimelineCommand,
  onClipboardCommand,
  onAISuggestionCommand,
  onAICommandSubmit,
}: DesktopEditorRuntimeEditorProps) {
  const view = buildReviewEditorViewModel(state);
  const router = useRouter();
  const renderContract = extractExportRenderContract(state.snapshot);
  const openExportWorkspace = useCallback(() => {
    if (!renderContract) return;
    storeReviewToExportContract(renderContract);
    router.push(buildExportWorkspaceHref(renderContract.production_id));
  }, [renderContract, router]);

  const commandPending = state.status === "executing" && state.pendingOperation === "timeline_command";
  const clipboardPending = state.status === "executing" && state.pendingOperation === "clipboard_command";
  const selecting = state.status === "selecting";
  const suggestionPending = state.pendingOperation === "ai_suggestion";
  const aiCommandPending = state.pendingOperation === "ai_command_submission";

  const clipDrag = useReviewRuntimeClipDrag({
    productionId: view.header.productionId,
    view,
    disabled: selecting || commandPending || clipboardPending || suggestionPending || aiCommandPending,
    moveClip: actions.moveClip,
  });

  const clipTrim = useReviewRuntimeClipTrim({
    productionId: view.header.productionId,
    view,
    disabled:
      selecting ||
      commandPending ||
      clipboardPending ||
      suggestionPending ||
      aiCommandPending ||
      clipDrag.drag.active,
    trimClipStart: actions.trimClipStart,
    trimClipEnd: actions.trimClipEnd,
  });

  const keyboard = useReviewRuntimeKeyboardEditing({
    productionId: view.header.productionId,
    view,
    disabled:
      selecting ||
      commandPending ||
      clipboardPending ||
      suggestionPending ||
      aiCommandPending ||
      clipDrag.drag.active ||
      clipTrim.trim.active,
    onUndo,
    onRedo,
    onTimelineCommand,
    onClipboardCommand,
  });

  const dropClip = useCallback(() => {
    void clipDrag.drop().catch(() => undefined);
  }, [clipDrag]);

  const dropClipTrim = useCallback(() => {
    void clipTrim.drop().catch(() => undefined);
  }, [clipTrim]);

  return (
    <DesktopEditorShell
      view={view}
      refreshing={state.status === "refreshing"}
      selecting={selecting}
      commandPending={commandPending}
      pendingCommand={state.pendingCommand}
      clipboardPending={clipboardPending}
      pendingClipboardOperation={state.pendingClipboardOperation}
      suggestionPending={suggestionPending}
      aiCommandPending={aiCommandPending}
      lastAICommandSubmission={state.lastAICommandSubmission?.submission ?? null}
      drag={clipDrag.drag}
      trim={clipTrim.trim}
      keyboard={keyboard}
      onClipDragStart={clipDrag.begin}
      onClipDragMove={clipDrag.move}
      onClipDragDrop={dropClip}
      onClipDragCancel={clipDrag.cancel}
      onClipTrimStart={clipTrim.begin}
      onClipTrimMove={clipTrim.move}
      onClipTrimDrop={dropClipTrim}
      onClipTrimCancel={clipTrim.cancel}
      onRefresh={onRefresh}
      onExport={openExportWorkspace}
      exportDisabled={!renderContract}
      onSelectClip={onSelectClip}
      onUndo={onUndo}
      onRedo={onRedo}
      onTimelineCommand={onTimelineCommand}
      onClipboardCommand={onClipboardCommand}
      onAISuggestionCommand={onAISuggestionCommand}
      onAICommandSubmit={onAICommandSubmit}
    />
  );
}
