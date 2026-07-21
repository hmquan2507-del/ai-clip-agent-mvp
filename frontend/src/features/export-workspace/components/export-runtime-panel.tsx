"use client";

import type { ExportRenderContract } from "../runtime/types";
import { useExportWorkspaceRuntime } from "../runtime/use-export-workspace-runtime";

type ExportRuntimePanelProps = {
  contract: ExportRenderContract | null;
  apiBaseUrl?: string;
};

function phaseLabel(phase: string): string {
  const labels: Record<string, string> = {
    idle: "Ready to render",
    submitting: "Submitting render",
    queued: "Render queued",
    polling: "Rendering",
    completed: "Render completed",
    failed: "Render failed",
    cancelled: "Render cancelled",
  };

  return labels[phase] ?? phase;
}

export function ExportRuntimePanel({
  contract,
  apiBaseUrl,
}: ExportRuntimePanelProps) {
  const { state, submit, cancel, reset } = useExportWorkspaceRuntime({
    apiBaseUrl,
  });

  const progress = Math.min(Math.max(state.status?.progress ?? 0, 0), 100);
  const busy =
    state.phase === "submitting" ||
    state.phase === "queued" ||
    state.phase === "polling";

  return (
    <section
      aria-label="Export render runtime"
      className="rounded-2xl border border-white/10 bg-black/20 p-5"
    >
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm text-white/60">Export runtime</p>
          <h2 className="text-lg font-semibold text-white">
            {phaseLabel(state.phase)}
          </h2>
        </div>

        <span className="text-sm font-medium text-white/70">{progress}%</span>
      </div>

      <div
        aria-label="Render progress"
        aria-valuemax={100}
        aria-valuemin={0}
        aria-valuenow={progress}
        className="mt-4 h-2 overflow-hidden rounded-full bg-white/10"
        role="progressbar"
      >
        <div
          className="h-full rounded-full bg-white transition-[width]"
          style={{ width: `${progress}%` }}
        />
      </div>

      {state.submission ? (
        <dl className="mt-4 grid gap-2 text-sm text-white/65">
          <div className="flex justify-between gap-4">
            <dt>Queue job</dt>
            <dd className="truncate font-mono">
              {state.submission.queue_job_id}
            </dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt>Duplicate</dt>
            <dd>{state.submission.duplicate ? "Yes" : "No"}</dd>
          </div>
        </dl>
      ) : null}

      {state.error ? (
        <p className="mt-4 rounded-lg bg-red-500/10 p-3 text-sm text-red-200">
          {state.error}
        </p>
      ) : null}

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-black disabled:cursor-not-allowed disabled:opacity-40"
          disabled={!contract || busy}
          onClick={() => {
            if (contract) {
              void submit(contract);
            }
          }}
          type="button"
        >
          {busy ? "Rendering..." : "Start render"}
        </button>

        {busy ? (
          <button
            className="rounded-lg border border-white/15 px-4 py-2 text-sm text-white"
            onClick={cancel}
            type="button"
          >
            Cancel tracking
          </button>
        ) : null}

        {state.phase !== "idle" && !busy ? (
          <button
            className="rounded-lg border border-white/15 px-4 py-2 text-sm text-white"
            onClick={reset}
            type="button"
          >
            Reset
          </button>
        ) : null}
      </div>
    </section>
  );
}
