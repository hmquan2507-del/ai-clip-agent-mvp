import {
  Clapperboard,
  Layers,
  Music2,
  Palette,
  Sparkle,
  Sticker,
  Type,
  Wallpaper,
  Wand2,
} from "lucide-react";

import type { EditorToolRailTabKey } from "../types";
import { PanelCollapseButton } from "./panel-collapse-button";

const TOOLS: Array<{ key: EditorToolRailTabKey; label: string; icon: typeof Clapperboard }> = [
  { key: "media", label: "Media", icon: Clapperboard },
  { key: "audio", label: "Audio", icon: Music2 },
  { key: "text", label: "Text", icon: Type },
  { key: "stickers", label: "Stickers", icon: Sticker },
  { key: "effects", label: "Effects", icon: Sparkle },
  { key: "transitions", label: "Transitions", icon: Wand2 },
  { key: "filters", label: "Filters", icon: Palette },
  { key: "templates", label: "Templates", icon: Layers },
  { key: "brand-kit", label: "Brand Kit", icon: Wallpaper },
  { key: "ai-assets", label: "AI Assets", icon: Sparkle },
];

export interface EditorToolRailProps {
  activeTab?: EditorToolRailTabKey;
  onTabChange?: (tab: EditorToolRailTabKey) => void;
  compact?: boolean;
  onToggleCompact?: () => void;
}

/**
 * Shell tool rail — Sprint 17.2 token cutover. Navigation only, no editing
 * logic. Cut directly onto `--ce-*` per `frontend-redesign-master-plan.md`
 * §17.2; no prop/behavior change.
 */
export function EditorToolRail({
  activeTab = "media",
  onTabChange,
  compact = false,
  onToggleCompact,
}: EditorToolRailProps) {
  return (
    <nav
      aria-label="Editor tool rail"
      data-editor-focus-zone="tool-rail"
      className="ce-scroll flex h-full w-full flex-col items-center gap-1 overflow-y-auto border-r border-[var(--ce-border-default)] bg-[var(--ce-bg-panel-raised)] py-2"
    >
      {TOOLS.map((tool) => {
        const Icon = tool.icon;
        const active = tool.key === activeTab;

        return (
          <button
            key={tool.key}
            type="button"
            aria-label={tool.label}
            aria-pressed={active}
            title={tool.label}
            onClick={() => onTabChange?.(tool.key)}
            className={
              active
                ? "ce-focus-ring flex w-11 flex-col items-center gap-1 rounded-[var(--ce-radius-sm)] bg-[var(--ce-accent-soft)] px-1 py-2 text-[var(--ce-accent-primary)]"
                : "ce-focus-ring flex w-11 flex-col items-center gap-1 rounded-[var(--ce-radius-sm)] px-1 py-2 text-[var(--ce-text-muted)] transition hover:bg-[var(--ce-state-hover)] hover:text-[var(--ce-text-primary)]"
            }
          >
            <Icon className="size-4" />
            {compact ? null : <span className="text-[9px] font-medium leading-tight">{tool.label}</span>}
          </button>
        );
      })}

      <PanelCollapseButton
        direction={compact ? "right" : "left"}
        label={compact ? "Expand tool rail" : "Compact tool rail"}
        onClick={() => onToggleCompact?.()}
      />
    </nav>
  );
}
