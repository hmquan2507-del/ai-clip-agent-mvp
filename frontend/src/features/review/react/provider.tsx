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
  type ReviewWorkspaceRuntimeActionOptions,
  type ReviewWorkspaceRuntimeOpenOptions,
  type ReviewWorkspaceRuntimeState,
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

  const onErrorRef = useRef(onError);

  const forceRefresh =
    openOptions?.force_refresh;

  const replaceExisting =
    openOptions?.replace_existing;

  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  useEffect(() => {
    const unsubscribe = runtime.subscribe(
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
    ) => runtime.open(productionId, options),
    [productionId, runtime],
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

  const actions =
    useMemo<ReviewWorkspaceActions>(
      () => ({
        open,
        refresh,
        reset,
        close,
        clear,
      }),
      [
        open,
        refresh,
        reset,
        close,
        clear,
      ],
    );

  useEffect(() => {
    if (!autoOpen) {
      return;
    }

    const controller =
      new AbortController();

    void open({
      force_refresh: forceRefresh,
      replace_existing:
        replaceExisting,
      signal: controller.signal,
    }).catch((error: unknown) => {
      if (!controller.signal.aborted) {
        onErrorRef.current?.(error);
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