"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  createReviewWorkspaceSessionRuntime,
  type ApplyAISuggestionInput,
  type CloseTimelineGapInput,
  type CopyTimelineClipsInput,
  type CutTimelineClipsInput,
  type DeleteTimelineClipInput,
  type DeleteTimelineClipsInput,
  type DismissAISuggestionInput,
  type DuplicateTimelineClipInput,
  type DuplicateTimelineClipsInput,
  type MoveTimelineClipInput,
  type MoveTimelineClipsInput,
  type PasteTimelineClipsInput,
  type ReviewWorkspaceRuntimeActionOptions,
  type ReviewWorkspaceRuntimeOpenOptions,
  type ReviewWorkspaceRuntimeState,
  type RestoreTimelineClipboardHistoryInput,
  type SelectAISuggestionInput,
  type SubmitAICommandInput,
  type SelectTimelineClipInput,
  type SplitTimelineClipInput,
  type TrimTimelineClipEndInput,
  type TrimTimelineClipStartInput,
} from "../state";

import {
  ReviewWorkspaceContext,
} from "./context";

import type {
  ReviewWorkspaceActions,
  ReviewWorkspaceProviderProps,
} from "./contracts";

export function ReviewWorkspaceProvider({
  productionId,
  children,
  runtime: providedRuntime,
  api,
  autoOpen = true,
  autoLoadSuggestions = true,
  openOptions,
  onError,
}: ReviewWorkspaceProviderProps) {
  const [runtime] = useState(() =>
    providedRuntime ??
    createReviewWorkspaceSessionRuntime({
      api,
    }),
  );

  const [state, setState] =
    useState<ReviewWorkspaceRuntimeState>(
      () => runtime.getState(),
    );

  const onErrorRef =
    useRef(onError);

  const suggestionLoadKeyRef =
    useRef<string | null>(null);

  const forceRefresh =
    openOptions?.force_refresh;

  const replaceExisting =
    openOptions?.replace_existing;

  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  useEffect(() => {
    const unsubscribe =
      runtime.subscribe(
        (nextState) => {
          setState(nextState);
        },
      );

    return unsubscribe;
  }, [runtime]);

  const open = useCallback(
    (
      options:
        ReviewWorkspaceRuntimeOpenOptions = {},
    ) => runtime.open(
      productionId,
      options,
    ),
    [
      productionId,
      runtime,
    ],
  );

  const refresh = useCallback(
    (
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.refresh(options),
    [runtime],
  );

  const reset = useCallback(
    (
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.reset(options),
    [runtime],
  );

  const close = useCallback(
    (
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.close(options),
    [runtime],
  );

  const clear = useCallback(
    () => runtime.clear(),
    [runtime],
  );

  const selectClip = useCallback(
    (
      input: SelectTimelineClipInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.selectClip(
      input,
      options,
    ),
    [runtime],
  );

  const moveClip = useCallback(
    (
      input: MoveTimelineClipInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.moveClip(
      input,
      options,
    ),
    [runtime],
  );

  const moveClips = useCallback(
    (
      input: MoveTimelineClipsInput,
      options: ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.moveClips(input, options),
    [runtime],
  );

  const trimClipStart = useCallback(
    (
      input:
        TrimTimelineClipStartInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.trimClipStart(
      input,
      options,
    ),
    [runtime],
  );

  const trimClipEnd = useCallback(
    (
      input:
        TrimTimelineClipEndInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.trimClipEnd(
      input,
      options,
    ),
    [runtime],
  );

  const splitClip = useCallback(
    (
      input: SplitTimelineClipInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.splitClip(
      input,
      options,
    ),
    [runtime],
  );

  const duplicateClip = useCallback(
    (
      input:
        DuplicateTimelineClipInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.duplicateClip(
      input,
      options,
    ),
    [runtime],
  );

  const deleteClip = useCallback(
    (
      input: DeleteTimelineClipInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.deleteClip(
      input,
      options,
    ),
    [runtime],
  );

  const duplicateClips = useCallback(
    (
      input: DuplicateTimelineClipsInput,
      options: ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.duplicateClips(input, options),
    [runtime],
  );

  const deleteClips = useCallback(
    (
      input: DeleteTimelineClipsInput,
      options: ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.deleteClips(input, options),
    [runtime],
  );

  const closeGap = useCallback(
    (
      input: CloseTimelineGapInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.closeGap(
      input,
      options,
    ),
    [runtime],
  );

  const undoTimeline = useCallback(
    (
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.undoTimeline(
      options,
    ),
    [runtime],
  );

  const redoTimeline = useCallback(
    (
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.redoTimeline(
      options,
    ),
    [runtime],
  );

  const copyTimelineClips = useCallback(
    (
      input: CopyTimelineClipsInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.copyTimelineClips(
      input,
      options,
    ),
    [runtime],
  );

  const cutTimelineClips = useCallback(
    (
      input: CutTimelineClipsInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.cutTimelineClips(
      input,
      options,
    ),
    [runtime],
  );

  const pasteTimelineClips = useCallback(
    (
      input: PasteTimelineClipsInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.pasteTimelineClips(
      input,
      options,
    ),
    [runtime],
  );

  const restoreTimelineClipboardHistory =
    useCallback(
      (
        input:
          RestoreTimelineClipboardHistoryInput,
        options:
          ReviewWorkspaceRuntimeActionOptions = {},
      ) => runtime.restoreTimelineClipboardHistory(
        input,
        options,
      ),
      [runtime],
    );

  const clearTimelineClipboard = useCallback(
    (
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.clearTimelineClipboard(
      options,
    ),
    [runtime],
  );

  const clearTimelineClipboardHistory =
    useCallback(
      (
        options:
          ReviewWorkspaceRuntimeActionOptions = {},
      ) => runtime.clearTimelineClipboardHistory(
        options,
      ),
      [runtime],
    );

  const refreshAISuggestions = useCallback(
    (
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.refreshAISuggestions(options),
    [runtime],
  );

  const selectAISuggestion = useCallback(
    (
      input: SelectAISuggestionInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.selectAISuggestion(input, options),
    [runtime],
  );

  const applyAISuggestion = useCallback(
    (
      input: ApplyAISuggestionInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.applyAISuggestion(input, options),
    [runtime],
  );

  const dismissAISuggestion = useCallback(
    (
      input: DismissAISuggestionInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.dismissAISuggestion(input, options),
    [runtime],
  );

  const regenerateAISuggestions = useCallback(
    (
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.regenerateAISuggestions(options),
    [runtime],
  );

  const submitAICommand = useCallback(
    (
      input: SubmitAICommandInput,
      options:
        ReviewWorkspaceRuntimeActionOptions = {},
    ) => runtime.submitAICommand(input, options),
    [runtime],
  );

  const actions =
    useMemo<ReviewWorkspaceActions>(
      () => ({
        open,
        refresh,
        reset,
        close,
        clear,
        selectClip,
        moveClip,
        moveClips,
        trimClipStart,
        trimClipEnd,
        splitClip,
        duplicateClip,
        duplicateClips,
        deleteClip,
        deleteClips,
        closeGap,
        undoTimeline,
        redoTimeline,
        copyTimelineClips,
        cutTimelineClips,
        pasteTimelineClips,
        restoreTimelineClipboardHistory,
        clearTimelineClipboard,
        clearTimelineClipboardHistory,
        refreshAISuggestions,
        selectAISuggestion,
        applyAISuggestion,
        dismissAISuggestion,
        regenerateAISuggestions,
        submitAICommand,
      }),
      [
        open,
        refresh,
        reset,
        close,
        clear,
        selectClip,
        moveClip,
        moveClips,
        trimClipStart,
        trimClipEnd,
        splitClip,
        duplicateClip,
        duplicateClips,
        deleteClip,
        deleteClips,
        closeGap,
        undoTimeline,
        redoTimeline,
        copyTimelineClips,
        cutTimelineClips,
        pasteTimelineClips,
        restoreTimelineClipboardHistory,
        clearTimelineClipboard,
        clearTimelineClipboardHistory,
        refreshAISuggestions,
        selectAISuggestion,
        applyAISuggestion,
        dismissAISuggestion,
        regenerateAISuggestions,
        submitAICommand,
      ],
    );

  useEffect(() => {
    if (!autoOpen) {
      return;
    }

    const controller =
      new AbortController();

    void open({
      force_refresh:
        forceRefresh,
      replace_existing:
        replaceExisting,
      signal:
        controller.signal,
    }).catch((error: unknown) => {
      if (
        !controller.signal.aborted
      ) {
        onErrorRef.current?.(
          error,
        );
      }
    });

    return () => {
      controller.abort();
    };
  }, [
    autoOpen,
    forceRefresh,
    open,
    replaceExisting,
  ]);

  useEffect(() => {
    if (state.suggestionSnapshot !== null) {
      suggestionLoadKeyRef.current = null;
      return;
    }

    if (
      !autoLoadSuggestions ||
      state.status !== "ready" ||
      state.pendingOperation !== null ||
      state.sessionId === null ||
      state.snapshot === null
    ) {
      return;
    }

    const loadKey = [
      productionId,
      state.sessionId,
      state.snapshot.timeline.revision,
    ].join(":");

    if (suggestionLoadKeyRef.current === loadKey) {
      return;
    }

    suggestionLoadKeyRef.current = loadKey;

    void refreshAISuggestions().catch((error: unknown) => {
      if (suggestionLoadKeyRef.current === loadKey) {
        suggestionLoadKeyRef.current = null;
      }

      onErrorRef.current?.(error);
    });
  }, [
    autoLoadSuggestions,
    productionId,
    refreshAISuggestions,
    state.pendingOperation,
    state.sessionId,
    state.snapshot,
    state.status,
    state.suggestionSnapshot,
  ]);

  const value = useMemo(
    () => ({
      productionId,
      runtime,
      state,
      actions,
    }),
    [
      productionId,
      runtime,
      state,
      actions,
    ],
  );

  return (
    <ReviewWorkspaceContext.Provider
      value={value}
    >
      {children}
    </ReviewWorkspaceContext.Provider>
  );
}
