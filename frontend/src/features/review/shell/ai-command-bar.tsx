"use client";

import { useState } from "react";
import { ArrowUp, Command, Mic, Sparkles } from "lucide-react";

import { ReviewIconButton, ReviewKeyboardHint } from "../design-system";
import type {
  ReviewAICommandSubmissionIntent,
} from "../integration/contracts";

export interface ReviewAICommandBarProps {
  disabled?: boolean;
  pending?: boolean;
  acceptedSubmissionId?: string | null;
  onSubmit?: (
    intent: ReviewAICommandSubmissionIntent,
  ) => void;
}

export function ReviewAICommandBar({
  disabled = false,
  pending = false,
  acceptedSubmissionId = null,
  onSubmit,
}: ReviewAICommandBarProps) {
  const [commandText, setCommandText] = useState("");

  const normalized = commandText.trim().replace(/\s+/g, " ");
  const canSubmit =
    !disabled &&
    !pending &&
    normalized.length > 0 &&
    normalized.length <= 2000 &&
    Boolean(onSubmit);

  return (
    <section
      data-review-command-bar="true"
      aria-label="AI Command Bar"
      className="flex h-[66px] shrink-0 items-center border-t border-[var(--review-border)] bg-[var(--review-bg-elevated)] px-3 py-2"
    >
      <form
        className="mx-auto flex w-full max-w-4xl items-center gap-2 rounded-2xl border border-[var(--review-accent-border)] bg-[var(--review-surface-floating)] p-2 shadow-[var(--review-shadow-panel)] backdrop-blur-xl"
        onSubmit={(event) => {
          event.preventDefault();
          if (!canSubmit) return;
          onSubmit?.({
            commandText: normalized,
            clientRequestId: createClientRequestId(),
          });
        }}
      >
        <div className="flex size-8 shrink-0 items-center justify-center rounded-xl bg-[var(--review-accent-soft)] text-[var(--review-accent-text)]">
          <Sparkles className="size-4" />
        </div>

        <input
          aria-label="Ra lệnh cho AI Editor"
          placeholder="Làm hook mạnh hơn, thêm B-roll..."
          className="min-w-0 flex-1 bg-transparent text-xs text-[var(--review-text)] outline-none placeholder:text-[var(--review-text-subtle)]"
          disabled={disabled}
          value={commandText}
          maxLength={2000}
          onChange={(event) => setCommandText(event.target.value)}
        />

        <ReviewKeyboardHint className="hidden sm:inline-flex">
          <Command className="size-2.5" />K
        </ReviewKeyboardHint>

        <ReviewIconButton aria-label="Nhập bằng giọng nói" size="sm" disabled>
          <Mic />
        </ReviewIconButton>

        <ReviewIconButton
          aria-label="Gửi lệnh AI"
          type="submit"
          size="sm"
          variant="primary"
          disabled={!canSubmit}
        >
          <ArrowUp />
        </ReviewIconButton>
      </form>
      <span className="sr-only" aria-live="polite">
        {pending
          ? "Đang gửi lệnh AI"
          : acceptedSubmissionId
            ? "Lệnh AI đã được tiếp nhận"
            : ""}
      </span>
    </section>
  );
}

function createClientRequestId(): string {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return crypto.randomUUID();
  }
  return `ai-command-${Date.now()}`;
}
