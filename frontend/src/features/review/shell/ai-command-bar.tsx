import { ArrowUp, Command, Mic, Sparkles } from "lucide-react";

import { ReviewIconButton, ReviewKeyboardHint } from "../design-system";

export interface ReviewAICommandBarProps {
  disabled?: boolean;
}

export function ReviewAICommandBar({
  disabled = false,
}: ReviewAICommandBarProps) {
  return (
    <section
      data-review-command-bar="true"
      aria-label="AI Command Bar"
      className="flex h-[66px] shrink-0 items-center border-t border-[var(--review-border)] bg-[var(--review-bg-elevated)] px-3 py-2"
    >
      <div className="mx-auto flex w-full max-w-4xl items-center gap-2 rounded-2xl border border-[var(--review-accent-border)] bg-[var(--review-surface-floating)] p-2 shadow-[var(--review-shadow-panel)] backdrop-blur-xl">
        <div className="flex size-8 shrink-0 items-center justify-center rounded-xl bg-[var(--review-accent-soft)] text-[var(--review-accent-text)]">
          <Sparkles className="size-4" />
        </div>

        <input
          aria-label="Ra lệnh cho AI Editor"
          placeholder="Làm hook mạnh hơn, thêm B-roll..."
          className="min-w-0 flex-1 bg-transparent text-xs text-[var(--review-text)] outline-none placeholder:text-[var(--review-text-subtle)]"
          disabled={disabled}
        />

        <ReviewKeyboardHint className="hidden sm:inline-flex">
          <Command className="size-2.5" />K
        </ReviewKeyboardHint>

        <ReviewIconButton aria-label="Nhập bằng giọng nói" size="sm" disabled={disabled}>
          <Mic />
        </ReviewIconButton>

        <ReviewIconButton aria-label="Gửi lệnh AI" size="sm" variant="primary" disabled={disabled}>
          <ArrowUp />
        </ReviewIconButton>
      </div>
    </section>
  );
}
