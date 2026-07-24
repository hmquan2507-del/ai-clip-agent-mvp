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

  return (
    <button
      type="button"
      data-ai-block-id={block.id}
      data-ai-block-state={visualState}
      aria-label={`${block.title} — ${Math.round(block.confidence * 100)}% confidence${visualState !== "normal" ? ` (${visualState})` : ""}`}
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
        width: Math.max(width, 6),
        borderColor: color,
        backgroundColor: `${color}26`,
      }}
      className={`absolute top-1 bottom-1 flex items-center gap-1 overflow-hidden rounded-md px-1.5 text-left ${VISUAL_STATE_CLASS[visualState]}`}
    >
      <Icon className="size-3 shrink-0" style={{ color }} />
      <span className="truncate text-[10px] font-medium text-white">{block.title}</span>
      {block.pinned ? <span aria-hidden className="ml-auto shrink-0 text-[9px]">📌</span> : null}
    </button>
  );
}

export const AiBlockView = memo(AiBlockImpl);
