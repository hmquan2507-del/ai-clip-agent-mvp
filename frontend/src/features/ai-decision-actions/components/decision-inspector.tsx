"use client";

import { AlertCircle, Check, CircleSlash2, GitCompare, History, Pin, RefreshCw, Sparkles, Undo2 } from "lucide-react";

import { useAiDecisionActions } from "../context";
import type { AiDecisionAction } from "../types";

const ACTIONS: Array<{ action: AiDecisionAction; label: string; icon: typeof Check }> = [
  { action: "accept", label: "Accept", icon: Check },
  { action: "reject", label: "Reject", icon: Undo2 },
  { action: "regenerate", label: "Regenerate", icon: RefreshCw },
  { action: "disable", label: "Disable", icon: CircleSlash2 },
  { action: "pin", label: "Pin", icon: Pin },
  { action: "compare", label: "Compare", icon: GitCompare },
];

export function AiDecisionInspector() {
  const actions = useAiDecisionActions();
  const selection = actions.selected;

  if (!selection) {
    return (
      <div className="flex h-full min-h-56 flex-col items-center justify-center px-6 text-center">
        <Sparkles className="size-7 text-[var(--desktop-editor-primary)]" />
        <p className="mt-3 text-[12px] font-semibold text-[var(--desktop-editor-text)]">Select an AI decision</p>
        <p className="mt-1 max-w-52 text-[10px] leading-4 text-[var(--desktop-editor-text-subtle)]">
          Choose a block on the AI Timeline to inspect its lifecycle, explanation, history, and available actions.
        </p>
      </div>
    );
  }

  const { decision, record } = selection;
  const pending = record.runtimeStatus === "pending";

  return (
    <div className="space-y-3 p-3" data-ai-decision-inspector="true">
      <div className="rounded-lg border border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-bg)] p-3">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-[10px] uppercase tracking-[0.12em] text-[var(--desktop-editor-text-subtle)]">AI Decision</p>
            <h3 className="mt-1 text-[13px] font-semibold text-[var(--desktop-editor-text)]">{decision.title}</h3>
          </div>
          <span className="rounded-full border border-[var(--desktop-editor-border)] px-2 py-0.5 text-[9px] font-semibold uppercase text-[var(--desktop-editor-text-subtle)]">
            {record.state}
          </span>
        </div>
        <p className="mt-2 text-[11px] leading-5 text-[var(--desktop-editor-text-muted)]">{decision.reason}</p>
        <dl className="mt-3 grid grid-cols-2 gap-2 text-[10px]">
          <Meta label="Confidence" value={`${Math.round(decision.confidence * 100)}%`} />
          <Meta label="Model" value={decision.aiModel} />
          <Meta label="Revision" value={String(decision.generatedAtRevision ?? "—")} />
          <Meta label="Range" value={`${decision.startTime.toFixed(1)}–${decision.endTime.toFixed(1)}s`} />
          <Meta label="Affected clip" value={decision.linkedClipId ?? "Not linked"} />
          <Meta label="Impact" value={decision.estimatedImpact ?? "Not scored"} />
        </dl>
      </div>

      {record.runtimeStatus === "pending-runtime" ? (
        <div className="flex gap-2 rounded-lg border border-amber-400/30 bg-amber-400/10 p-2.5 text-[10px] leading-4 text-amber-200">
          <AlertCircle className="mt-0.5 size-3.5 shrink-0" />
          <span>Pending Runtime: the UI recorded this action, but no backend decision-action contract is connected. No timeline mutation was faked.</span>
        </div>
      ) : null}

      {record.error ? (
        <div className="rounded-lg border border-red-400/30 bg-red-400/10 p-2.5 text-[10px] text-red-200">
          <p>{record.error}</p>
          <button type="button" onClick={() => actions.clearError(decision.id)} className="mt-1 font-semibold underline">Dismiss</button>
        </div>
      ) : null}

      <div className="grid grid-cols-2 gap-2">
        {ACTIONS.map(({ action, label, icon: Icon }) => (
          <button
            key={action}
            type="button"
            disabled={pending}
            onClick={() => void actions.runAction(action, decision)}
            className="flex h-9 items-center justify-center gap-1.5 rounded-md border border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-bg)] text-[10px] font-semibold text-[var(--desktop-editor-text)] hover:bg-white/5 disabled:opacity-50"
          >
            <Icon className="size-3.5" />
            {label}
          </button>
        ))}
      </div>

      <button
        type="button"
        onClick={() => void actions.runAction("convert-to-manual", decision)}
        className="h-9 w-full rounded-md bg-[var(--desktop-editor-primary)] text-[10px] font-semibold text-white hover:brightness-110"
      >
        Convert to Manual
      </button>

      <div className="rounded-lg border border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-bg)] p-3">
        <div className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--desktop-editor-text-subtle)]">
          <History className="size-3.5" /> Decision history
        </div>
        <ol className="mt-2 space-y-2">
          {[...record.history].reverse().map((entry) => (
            <li key={entry.id} className="border-l border-[var(--desktop-editor-border)] pl-2 text-[10px]">
              <p className="font-semibold capitalize text-[var(--desktop-editor-text)]">{entry.action.replaceAll("-", " ")}</p>
              <p className="text-[var(--desktop-editor-text-subtle)]">{new Date(entry.createdAt).toLocaleString()}</p>
              {entry.message ? <p className="mt-0.5 leading-4 text-[var(--desktop-editor-text-muted)]">{entry.message}</p> : null}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[var(--desktop-editor-text-subtle)]">{label}</dt>
      <dd className="mt-0.5 truncate font-medium text-[var(--desktop-editor-text)]" title={value}>{value}</dd>
    </div>
  );
}
