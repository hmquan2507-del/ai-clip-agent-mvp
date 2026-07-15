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
  type CloseTimelineGapInput,
  type DeleteTimelineClipInput,
  type DuplicateTimelineClipInput,
  type MoveTimelineClipInput,
  type ReviewWorkspaceRuntimeActionOptions,
  type ReviewWorkspaceRuntimeOpenOptions,
  type ReviewWorkspaceRuntimeState,
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
        trimClipStart,
        trimClipEnd,
        splitClip,
        duplicateClip,
        deleteClip,
        closeGap,
        undoTimeline,
        redoTimeline,
      }),
      [
        open,
        refresh,
        reset,
        close,
        clear,
        selectClip,
        moveClip,
        trimClipStart,
        trimClipEnd,
        splitClip,
        duplicateClip,
        deleteClip,
        closeGap,
        undoTimeline,
        redoTimeline,
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