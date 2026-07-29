import { memo } from "react";
import {
  Clapperboard,
  Film,
  Megaphone,
  Music2,
  Scissors,
  Smile,
  Sparkles,
  Type,
  Volume2,
  ZoomIn,
} from "lucide-react";

import type { AiBlock, AiBlockVisualState, AiTrackKind } from "../types";

export const TRACK_COLOR: Record<AiTrackKind, string> = {
  "hook-detection": "#a855f7", // purple
  "ai-cuts": "#06b6d4", // cyan
  broll: "#3b82f6", // blue
  "subtitle-highlight": "#eab308", // yellow
  zoom: "#f97316", // orange
  emoji: "#ec4899",
  cta: "#22c55e", // green
  "silence-removed": "#6b7280", // gray
  "emotion-peak": "#ef4444", // red
  "story-beat": "#14b8a6",
};

export const TRACK_ICON: Record<AiTrackKind, typeof Sparkles> = {
  "hook-detection": Sparkles,
  "ai-cuts": Scissors,
  broll: Film,
  "subtitle-highlight": Type,
  zoom: ZoomIn,
  emoji: Smile,
  cta: Megaphone,
  "silence-removed": Volume2,
  "emotion-peak": Music2,
  "story-beat": Clapperboard,
};

const VISUAL_STATE_CLASS: Record<AiBlockVisualState, string> = {
  processing: "animate-pulse border-2",
  regenerating: "animate-pulse border-2 border-dashed",
  disabled: "border opacity-35",
  stale: "border border-dashed",
  selected: "border-2 shadow-[0_0_0_1px_rgba(255,255,255,0.6)]",
  hovered: "border brightness-125",
  pinned: "border",
  normal: "border transition hover:brightness-110",
};

/** Below this rendered width, only the decision-type icon is shown (no title/confidence) — keeps narrow blocks readable instead of clipping garbled text. */
const COMPACT_WIDTH_THRESHOLD = 30;
/** Above this rendered width, there's room to also show the confidence value next to the title. */
const CONFIDENCE_WIDTH_THRESHOLD = 92;
/** Minimum clickable/visible width regardless of the decision's real duration. */
const MIN_HIT_WIDTH = 16;

export interface AiBlockProps {
  block: AiBlock;
  left: number;
  width: number;
  visualState: AiBlockVisualState;
  onHoverChange: (blockId: string | null) => void;
  onSelect: (block: AiBlock) => void;
  onOpenDetails: (block: AiBlock) => void;
  onContextMenu: (block: AiBlock, x: number, y: number) => void;
}

function AiBlockImpl({
  block,
  left,
  width,
  visualState,
  onHoverChange,
  onSelect,
  onOpenDetails,
  onContextMenu,
}: AiBlockProps) {
  const Icon = TRACK_ICON[block.trackKind];
  const color = TRACK_COLOR[block.trackKind];
  const compact = width < COMPACT_WIDTH_THRESHOLD;
  const showConfidence = width >= CONFIDENCE_WIDTH_THRESHOLD;

  return (
    <button
      type="button"
      data-ai-block-id={block.id}
      data-ai-block-state={visualState}
      data-ai-block-compact={compact}
      aria-label={`${block.title} — ${Math.round(block.confidence * 100)}% confidence${visualState !== "normal" ? ` (${visualState})` : ""}`}
      title={compact ? block.title : undefined}
      onMouseEnter={() => onHoverChange(block.id)}
      onMouseLeave={() => onHoverChange(null)}
      onClick={() => onSelect(block)}
      onDoubleClick={() => onOpenDetails(block)}
      onContextMenu={(event) => {
        event.preventDefault();
        onContextMenu(block, event.clientX, event.clientY);
      }}
      style={{
        left,
        width: Math.max(width, MIN_HIT_WIDTH),
        borderColor: color,
        backgroundColor: `${color}26`,
      }}
      className={`absolute top-1 bottom-1 flex items-center gap-1 overflow-hidden rounded-md text-left ${compact ? "justify-center px-0.5" : "px-1.5"} ${VISUAL_STATE_CLASS[visualState]}`}
    >
      <Icon className="size-3 shrink-0" style={{ color }} />
      {compact ? null : (
        <span className="min-w-0 flex-1 truncate text-[10px] font-medium text-white">{block.title}</span>
      )}
      {!compact && showConfidence ? (
        <span className="shrink-0 text-[9px] font-semibold text-white/70">{Math.round(block.confidence * 100)}%</span>
      ) : null}
      {!compact && block.pinned ? (
        <span aria-hidden className="shrink-0 text-[9px]">📌</span>
      ) : null}
    </button>
  );
}

export const AiBlockView = memo(AiBlockImpl);
