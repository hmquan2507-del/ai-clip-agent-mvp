import { CheckCircle2, Sparkles, XCircle } from "lucide-react";

import { ReviewAICommandBar, type ReviewAICommandBarProps } from "../../review/shell";

import type { AiCopilotSuggestion, RecentAiTask } from "../types";

const QUICK_ACTIONS: AiCopilotSuggestion[] = [
  { key: "highlight-intro", label: "Highlight first 15s", description: "Boost the hook viewers see first." },
  { key: "remove-silence", label: "Remove silence", description: "Trim dead air across the timeline." },
  { key: "add-broll", label: "Add B-roll", description: "Insert supporting footage automatically." },
  { key: "generate-cta", label: "Generate CTA", description: "Draft a closing call-to-action." },
];

const SUGGESTIONS: AiCopilotSuggestion[] = [
  { key: "replace-music", label: "Replace music", description: "Swap the soundtrack for a better match." },
  { key: "improve-subtitles", label: "Improve subtitles", description: "Tighten wording and timing of captions." },
  { key: "rewrite-hook", label: "Rewrite hook", description: "Generate stronger opening lines." },
  { key: "translate-subtitles", label: "Translate subtitles", description: "Translate captions to another language." },
];

const RECENT_TASKS: RecentAiTask[] = [];

export interface EditorAiCopilotProps {
  aiCommand?: ReviewAICommandBarProps;
  onSuggestionSelect?: (suggestion: AiCopilotSuggestion) => void;
  recentTasks?: RecentAiTask[];
}

/**
 * AI Copilot panel. The custom-prompt input reuses the existing, untouched
 * `ReviewAICommandBar` (same AI runtime submission boundary as the legacy
 * Review UI) rather than reimplementing command submission. Quick Actions and
 * Suggestions are callback-only — no API calls, no timeline mutation — ready
 * for a future sprint to wire to real AI operations. Recent AI Tasks is a
 * layout-only, future-ready list (empty by default; no backend yet).
 */
export function EditorAiCopilot({ aiCommand, onSuggestionSelect, recentTasks = RECENT_TASKS }: EditorAiCopilotProps) {
  return (
    <div className="flex h-full flex-col">
      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-3">
        <SectionHeading>Quick actions</SectionHeading>
        <div className="grid grid-cols-2 gap-1.5">
          {QUICK_ACTIONS.map((action) => (
            <button
              key={action.key}
              type="button"
              title={action.description}
              onClick={() => onSuggestionSelect?.(action)}
              className="rounded-[var(--desktop-editor-radius-control)] border border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-bg)] px-2 py-2 text-left text-[10.5px] font-medium leading-4 text-[var(--desktop-editor-text)] transition hover:border-[var(--desktop-editor-border-hover)] hover:bg-[var(--desktop-editor-surface-hover)]"
            >
              {action.label}
            </button>
          ))}
        </div>

        <SectionHeading>Suggestions</SectionHeading>
        <div className="space-y-2">
          {SUGGESTIONS.map((suggestion) => (
            <button
              key={suggestion.key}
              type="button"
              onClick={() => onSuggestionSelect?.(suggestion)}
              className="block w-full rounded-[var(--desktop-editor-radius-control)] border border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-bg)] p-2.5 text-left transition hover:border-[var(--desktop-editor-border-hover)] hover:bg-[var(--desktop-editor-surface-hover)]"
            >
              <span className="block text-[11px] font-semibold text-[var(--desktop-editor-text)]">
                {suggestion.label}
              </span>
              <span className="mt-0.5 block text-[10px] leading-4 text-[var(--desktop-editor-text-subtle)]">
                {suggestion.description}
              </span>
            </button>
          ))}
        </div>

        <SectionHeading>Recent AI tasks</SectionHeading>
        {recentTasks.length === 0 ? (
          <p className="rounded-[var(--desktop-editor-radius-control)] border border-dashed border-[var(--desktop-editor-border)] px-2.5 py-3 text-center text-[10.5px] leading-4 text-[var(--desktop-editor-text-subtle)]">
            AI tasks you run will show up here.
          </p>
        ) : (
          <ul className="space-y-1.5">
            {recentTasks.map((task) => (
              <li
                key={task.id}
                className="flex items-center gap-2 rounded-[var(--desktop-editor-radius-control)] border border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-bg)] px-2.5 py-2"
              >
                {task.status === "done" ? (
                  <CheckCircle2 className="size-3.5 shrink-0 text-[var(--desktop-editor-success-text)]" />
                ) : (
                  <XCircle className="size-3.5 shrink-0 text-[var(--desktop-editor-danger-text)]" />
                )}
                <span className="min-w-0 flex-1 truncate text-[11px] text-[var(--desktop-editor-text)]">
                  {task.label}
                </span>
                <span className="shrink-0 text-[9px] text-[var(--desktop-editor-text-subtle)]">
                  {task.timeLabel}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="shrink-0 border-t border-[var(--desktop-editor-border-subtle)] px-1 pb-1 pt-2">
        <p className="mb-1 flex items-center gap-1 px-2 text-[10px] font-medium text-[var(--desktop-editor-text-subtle)]">
          <Sparkles className="size-3" />
          Custom prompt
        </p>
        <ReviewAICommandBar {...aiCommand} />
      </div>
    </div>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <p className="px-0.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--desktop-editor-text-subtle)]">
      {children}
    </p>
  );
}
