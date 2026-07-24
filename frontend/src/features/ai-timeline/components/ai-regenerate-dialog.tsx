"use client";

import { useState } from "react";
import { RefreshCw, Sparkles, X } from "lucide-react";

import type { AiBlock } from "../types";
import type { AiDialogState } from "../hooks/use-ai-timeline-state";

export interface AiRegenerateDialogProps {
  dialog: AiDialogState;
  onClose: () => void;
  onRegenerate?: (block: AiBlock) => void;
}

/**
 * Single dialog covering both "Explain Decision" and "Regenerate this
 * decision" — the two per-block detail flows the sprint calls for. Confirming
 * regenerate only ever targets the ONE block passed in; there is no
 * "regenerate the entire production" affordance here.
 */
export function AiRegenerateDialog({ dialog, onClose, onRegenerate }: AiRegenerateDialogProps) {
  const { mode, block } = dialog;
  const [submitting, setSubmitting] = useState(false);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={mode === "explain" ? "Explain AI decision" : "Regenerate AI decision"}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        onClick={(event) => event.stopPropagation()}
        className="w-full max-w-md rounded-[var(--ai-timeline-radius)] border border-[var(--ai-timeline-border)] bg-[var(--ai-timeline-surface)] p-4 shadow-2xl"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            {mode === "explain" ? (
              <Sparkles className="size-4 text-[var(--ai-timeline-primary)]" />
            ) : (
              <RefreshCw className="size-4 text-[var(--ai-timeline-primary)]" />
            )}
            <h2 className="text-[13px] font-semibold text-[var(--ai-timeline-text)]">
              {mode === "explain" ? "Explain decision" : `Regenerate this ${block.title.toLowerCase()}`}
            </h2>
          </div>
          <button
            type="button"
            aria-label="Close dialog"
            onClick={onClose}
            className="flex size-6 items-center justify-center rounded-md text-[var(--ai-timeline-text-subtle)] hover:bg-white/5 hover:text-[var(--ai-timeline-text)]"
          >
            <X className="size-4" />
          </button>
        </div>

        {mode === "explain" ? (
          <div className="mt-3 space-y-2 text-[12px] leading-5 text-[var(--ai-timeline-text-muted)]">
            <p>&ldquo;{block.reason}&rdquo;</p>
            <p className="text-[10px] text-[var(--ai-timeline-text-subtle)]">
              Confidence {Math.round(block.confidence * 100)}% · Model {block.aiModel}
            </p>
          </div>
        ) : (
          <div className="mt-3 space-y-3">
            <p className="text-[12px] leading-5 text-[var(--ai-timeline-text-muted)]">
              This regenerates only this one AI decision (
              <span className="font-medium text-[var(--ai-timeline-text)]">{block.title}</span>). The rest of
              the production is left untouched.
            </p>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={onClose}
                className="rounded-[var(--ai-timeline-radius-control)] px-3 py-1.5 text-[12px] font-medium text-[var(--ai-timeline-text-muted)] hover:bg-white/5"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={submitting}
                onClick={() => {
                  setSubmitting(true);
                  onRegenerate?.(block);
                }}
                className="rounded-[var(--ai-timeline-radius-control)] bg-[var(--ai-timeline-primary)] px-3.5 py-1.5 text-[12px] font-semibold text-white transition hover:brightness-110 disabled:opacity-60"
              >
                {submitting ? "Regenerating…" : "Regenerate"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
