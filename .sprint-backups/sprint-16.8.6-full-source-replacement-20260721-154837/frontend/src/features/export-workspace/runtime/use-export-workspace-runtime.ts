"use client";

import { useEffect, useMemo, useSyncExternalStore } from "react";

import { ExportWorkspaceApiClient } from "./api-client";
import { ExportWorkspaceRuntime } from "./runtime";
import type { ExportRenderContract } from "./types";

export function useExportWorkspaceRuntime(options?: {
  apiBaseUrl?: string;
  pollIntervalMs?: number;
}) {
  const runtime = useMemo(
    () =>
      new ExportWorkspaceRuntime(
        new ExportWorkspaceApiClient({
          baseUrl: options?.apiBaseUrl,
        }),
        {
          pollIntervalMs: options?.pollIntervalMs,
        },
      ),
    [options?.apiBaseUrl, options?.pollIntervalMs],
  );

  const state = useSyncExternalStore(
    runtime.subscribe,
    runtime.getSnapshot,
    runtime.getSnapshot,
  );

  useEffect(() => () => runtime.cancel(), [runtime]);

  return {
    state,
    submit: (contract: ExportRenderContract) => runtime.submit(contract),
    cancel: () => runtime.cancel(),
    reset: () => runtime.reset(),
  };
}
