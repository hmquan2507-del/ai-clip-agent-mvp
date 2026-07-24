import { memo } from "react";

import type { AiBlock, AiBlockVisualState } from "../types";
import { TRACK_COLOR } from "./ai-block";

const VISUAL_STATE_CLASS: Record<AiBlockVisualState, string> = {
  processing: "animate-pulse ring-2 ring-white/70",
  regenerating: "animate-pulse ring-2 ring-dashed ring-white/70",
  disabled: "opacity-35",
  stale: "ring-1 ring-dashed ring-white/50",
  selected: "ring-2 ring-white/70",
  hovered: "ring-2 ring-white/50",
  pinned: "ring-1 ring-white/40",
  normal: "transition hover:ring-2 hover:ring-white/50",
};

export interface AiMarkerProps {
  block: AiBlock;
  left: number;
  visualState: AiBlockVisualState;
  onHoverChange: (blockId: string | null) => void;
  onSelect: (block: AiBlock) => void;
  onOpenDetails: (block: AiBlock) => void;
  onContextMenu: (block: AiBlock, x: number, y: number) => void;
}

/**
 * A near-instant AI decision (e.g. an emoji insertion or a cut point) —
 * rendered as a small diamond marker instead of a ranged block.
 */
function AiMarkerImpl({
  block,
  left,
  visualState,
  onHoverChange,
  onSelect,
  onOpenDetails,
  onContextMenu,
}: AiMarkerProps) {
  const color = TRACK_COLOR[block.trackKind];

  return (
    <button
      type="button"
      data-ai-block-id={block.id}
      data-ai-block-state={visualState}
      aria-label={block.title}
      onMouseEnter={() => onHoverChange(block.id)}
      onMouseLeave={() => onHoverChange(null)}
      onClick={() => onSelect(block)}
      onDoubleClick={() => onOpenDetails(block)}
      onContextMenu={(event) => {
        event.preventDefault();
        onContextMenu(block, event.clientX, event.clientY);
      }}
      style={{ left: left - 5, backgroundColor: color }}
      className={`absolute top-1/2 size-2.5 -translate-y-1/2 rotate-45 rounded-[2px] ${VISUAL_STATE_CLASS[visualState]}`}
    />
  );
}

export const AiMarkerView = memo(AiMarkerImpl);
