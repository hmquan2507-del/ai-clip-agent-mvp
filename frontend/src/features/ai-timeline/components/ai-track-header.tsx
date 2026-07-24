import { ChevronDown, ChevronRight, Eye, EyeOff, Lock, LockOpen, Volume2, VolumeX } from "lucide-react";

import type { AiTrackDefinition, AiTrackState } from "../types";
import { TRACK_ICON } from "./ai-block";

export interface AiTrackHeaderProps {
  track: AiTrackDefinition;
  state: AiTrackState;
  blockCount: number;
  onToggleCollapsed: () => void;
  onToggleVisibility: () => void;
  onToggleLocked: () => void;
  onToggleMuted: () => void;
}

export function AiTrackHeader({
  track,
  state,
  blockCount,
  onToggleCollapsed,
  onToggleVisibility,
  onToggleLocked,
  onToggleMuted,
}: AiTrackHeaderProps) {
  const Icon = TRACK_ICON[track.kind];

  return (
    <div className="flex h-full items-center gap-1.5 border-r border-[var(--ai-timeline-border-subtle)] px-2">
      <button
        type="button"
        aria-label={state.collapsed ? `Expand ${track.label}` : `Collapse ${track.label}`}
        onClick={onToggleCollapsed}
        className="flex size-5 shrink-0 items-center justify-center text-[var(--ai-timeline-text-subtle)] hover:text-[var(--ai-timeline-text)]"
      >
        {state.collapsed ? <ChevronRight className="size-3.5" /> : <ChevronDown className="size-3.5" />}
      </button>

      <Icon className="size-3.5 shrink-0 text-[var(--ai-timeline-text-muted)]" />

      <span className="min-w-0 flex-1 truncate text-[11px] font-medium text-[var(--ai-timeline-text)]">
        {track.label}
      </span>

      <span className="shrink-0 text-[9px] text-[var(--ai-timeline-text-subtle)]">{blockCount}</span>

      <div className="ml-1 flex shrink-0 items-center gap-0.5">
        <IconToggle
          active={state.visibility === "shown"}
          onLabel="Hide track"
          offLabel="Show track"
          onIcon={Eye}
          offIcon={EyeOff}
          onClick={onToggleVisibility}
        />
        <IconToggle
          active={!state.locked}
          onLabel="Lock track"
          offLabel="Unlock track"
          onIcon={LockOpen}
          offIcon={Lock}
          onClick={onToggleLocked}
        />
        <IconToggle
          active={!state.muted}
          onLabel="Mute track"
          offLabel="Unmute track"
          onIcon={Volume2}
          offIcon={VolumeX}
          onClick={onToggleMuted}
        />
      </div>
    </div>
  );
}

function IconToggle({
  active,
  onLabel,
  offLabel,
  onIcon: OnIcon,
  offIcon: OffIcon,
  onClick,
}: {
  active: boolean;
  onLabel: string;
  offLabel: string;
  onIcon: typeof Eye;
  offIcon: typeof EyeOff;
  onClick: () => void;
}) {
  const Icon = active ? OnIcon : OffIcon;

  return (
    <button
      type="button"
      aria-label={active ? onLabel : offLabel}
      aria-pressed={!active}
      onClick={onClick}
      className={
        active
          ? "flex size-5 items-center justify-center rounded text-[var(--ai-timeline-text-subtle)] hover:bg-white/5 hover:text-[var(--ai-timeline-text)]"
          : "flex size-5 items-center justify-center rounded text-[var(--ai-timeline-warning-text)] hover:bg-white/5"
      }
    >
      <Icon className="size-3" />
    </button>
  );
}
