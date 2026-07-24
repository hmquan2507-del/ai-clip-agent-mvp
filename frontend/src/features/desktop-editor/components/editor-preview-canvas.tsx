import { AlertTriangle } from "lucide-react";

import { ReviewPreviewStage, type ReviewPreviewStageProps } from "../../review/shell";

export interface EditorPreviewCanvasProps extends ReviewPreviewStageProps {
  runtimeError?: string | null;
  onRetry?: () => void;
}

/**
 * Layout-only wrapper around the existing, untouched Review preview runtime UI
 * (`ReviewPreviewStage`). Per the Desktop Editor error-handling rule, a runtime
 * failure is surfaced ONLY inside this canvas — the rest of the shell (header,
 * tool rail, asset panel, inspector, timeline, status bar) keeps rendering.
 */
export function EditorPreviewCanvas({ runtimeError, onRetry, ...stageProps }: EditorPreviewCanvasProps) {
  if (runtimeError) {
    return (
      <div
        role="alert"
        className="flex h-full w-full min-h-0 min-w-0 flex-col items-center justify-center gap-3 bg-[var(--desktop-editor-bg)] px-6 text-center"
      >
        <div className="flex size-11 items-center justify-center rounded-full border border-[var(--desktop-editor-danger-border)] bg-[var(--desktop-editor-danger-soft)] text-[var(--desktop-editor-danger-text)]">
          <AlertTriangle className="size-5" />
        </div>
        <p className="text-[13px] font-semibold text-[var(--desktop-editor-text)]">
          Preview unavailable
        </p>
        <p className="max-w-xs text-[11px] leading-5 text-[var(--desktop-editor-text-subtle)]">
          {runtimeError}
        </p>
        {onRetry ? (
          <button
            type="button"
            onClick={onRetry}
            className="rounded-[var(--desktop-editor-radius-control)] bg-[var(--desktop-editor-primary)] px-3.5 py-1.5 text-[12px] font-semibold text-white transition hover:bg-[var(--desktop-editor-primary-hover)]"
          >
            Retry
          </button>
        ) : null}
      </div>
    );
  }

  return (
    <div className="flex h-full w-full min-h-0 min-w-0 flex-col bg-[var(--desktop-editor-bg)]">
      <ReviewPreviewStage {...stageProps} />
    </div>
  );
}
