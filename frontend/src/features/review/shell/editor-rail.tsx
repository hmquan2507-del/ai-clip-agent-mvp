import type {
  LucideIcon,
} from "lucide-react";

import {
  HelpCircle,
  Settings2,
} from "lucide-react";

import {
  reviewClassNames,
} from "../design-system";

import {
  reviewTools,
} from "./data";

export function ReviewEditorRail() {
  return (
    <aside
      aria-label="Công cụ dựng video"
      className="flex min-h-0 flex-col justify-between border-r border-[var(--review-border)] bg-[var(--review-bg-elevated)] py-2 max-md:hidden"
    >
      <nav className="space-y-1 px-1.5">
        {reviewTools.map((tool) => {
          const Icon = tool.icon;

          return (
            <button
              key={tool.id}
              type="button"
              aria-pressed={
                tool.active ?? false
              }
              className={reviewClassNames(
                "group flex w-full flex-col items-center gap-1 rounded-xl px-1 py-2 text-[9px] font-medium transition",
                tool.active
                  ? "bg-[var(--review-accent-soft)] text-[var(--review-accent-text)]"
                  : "text-[var(--review-text-subtle)] hover:bg-[var(--review-surface-hover)] hover:text-[var(--review-text)]",
              )}
            >
              <Icon className="size-[18px]" />

              <span className="max-w-12 truncate">
                {tool.label}
              </span>
            </button>
          );
        })}
      </nav>

      <div className="space-y-1 px-1.5">
        <RailUtility
          label="Trợ giúp"
          icon={HelpCircle}
        />

        <RailUtility
          label="Cài đặt"
          icon={Settings2}
        />
      </div>
    </aside>
  );
}

function RailUtility({
  label,
  icon: Icon,
}: {
  label: string;
  icon: LucideIcon;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      className="flex w-full items-center justify-center rounded-xl py-2.5 text-[var(--review-text-subtle)] transition hover:bg-[var(--review-surface-hover)] hover:text-[var(--review-text)]"
    >
      <Icon className="size-[18px]" />
    </button>
  );
}