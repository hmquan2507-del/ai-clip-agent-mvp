import { memo, useMemo } from "react";

import { resolveAiBlockVisualState, type AiBlock, type AiTrackDefinition, type AiTrackState } from "../types";
import { AiBlockView } from "./ai-block";
import { AiMarkerView } from "./ai-marker";
import { AiTrackHeader } from "./ai-track-header";

/** Matches the real Timeline Runtime's label column width (`shell/timeline.tsx`'s `grid-cols-[112px_...]`) so both timelines' canvases share the same x-origin. */
export const AI_TRACK_HEADER_WIDTH = 112;
export const AI_TRACK_ROW_HEIGHT = 40;
export const AI_TRACK_ROW_HEIGHT_COLLAPSED = 24;

const MARKER_DURATION_THRESHOLD = 0.4;
const VIEWPORT_BUFFER_SECONDS = 5;

export interface AiTrackProps {
  track: AiTrackDefinition;
  state: AiTrackState;
  blocks: AiBlock[];
  pixelsPerSecond: number;
  visibleRange: { startTime: number; endTime: number };
  highlightedBlockIds: Set<string> | null;
  hoveredBlockId: string | null;
  selectedBlockId: string | null;
  selectedClipIds: Set<string>;
  currentRevision: number;
  onToggleCollapsed: () => void;
  onToggleVisibility: () => void;
  onToggleLocked: () => void;
  onToggleMuted: () => void;
  onHoverChange: (blockId: string | null) => void;
  onSelect: (block: AiBlock) => void;
  onOpenDetails: (block: AiBlock) => void;
  onContextMenu: (block: AiBlock, x: number, y: number) => void;
}

function AiTrackImpl({
  track,
  state,
  blocks,
  pixelsPerSecond,
  visibleRange,
  highlightedBlockIds,
  hoveredBlockId,
  selectedBlockId,
  selectedClipIds,
  currentRevision,
  onToggleCollapsed,
  onToggleVisibility,
  onToggleLocked,
  onToggleMuted,
  onHoverChange,
  onSelect,
  onOpenDetails,
  onContextMenu,
}: AiTrackProps) {
  const rowHeight = state.collapsed ? AI_TRACK_ROW_HEIGHT_COLLAPSED : AI_TRACK_ROW_HEIGHT;

  // Windowing: only render blocks that intersect the visible time range (plus
  // a small buffer) — this is what keeps thousands of AI blocks smooth.
  const windowedBlocks = useMemo(() => {
    const start = visibleRange.startTime - VIEWPORT_BUFFER_SECONDS;
    const end = visibleRange.endTime + VIEWPORT_BUFFER_SECONDS;
    return blocks.filter((block) => block.endTime >= start && block.startTime <= end);
  }, [blocks, visibleRange.startTime, visibleRange.endTime]);

  if (state.visibility === "hidden") {
    return null;
  }

  return (
    <div
      className="flex shrink-0 border-b border-[var(--ai-timeline-border-subtle)]"
      style={{ height: rowHeight }}
      data-ai-track={track.kind}
    >
      <div className="shrink-0 bg-[var(--ai-timeline-surface)]" style={{ width: AI_TRACK_HEADER_WIDTH }}>
        <AiTrackHeader
          track={track}
          state={state}
          blockCount={blocks.length}
          onToggleCollapsed={onToggleCollapsed}
          onToggleVisibility={onToggleVisibility}
          onToggleLocked={onToggleLocked}
          onToggleMuted={onToggleMuted}
        />
      </div>

      {state.collapsed ? null : (
        <div className="relative min-w-0 flex-1">
          {windowedBlocks.map((block) => {
            const left = block.startTime * pixelsPerSecond;
            const width = (block.endTime - block.startTime) * pixelsPerSecond;
            const isMarker = block.endTime - block.startTime < MARKER_DURATION_THRESHOLD;
            const dimmed = Boolean(highlightedBlockIds) && !highlightedBlockIds?.has(block.id);

            const selected =
              selectedBlockId === block.id || Boolean(block.linkedClipId && selectedClipIds.has(block.linkedClipId));
            const stale = block.generatedAtRevision != null && block.generatedAtRevision !== currentRevision;
            const visualState = resolveAiBlockVisualState({
              status: block.status,
              disabled: block.disabled,
              stale,
              selected,
              hovered: hoveredBlockId === block.id,
              pinned: block.pinned,
            });

            return (
              <div key={block.id} style={{ opacity: dimmed ? 0.35 : 1 }} className="contents">
                {isMarker ? (
                  <AiMarkerView
                    block={block}
                    left={left}
                    visualState={visualState}
                    onHoverChange={onHoverChange}
                    onSelect={onSelect}
                    onOpenDetails={onOpenDetails}
                    onContextMenu={onContextMenu}
                  />
                ) : (
                  <AiBlockView
                    block={block}
                    left={left}
                    width={width}
                    visualState={visualState}
                    onHoverChange={onHoverChange}
                    onSelect={onSelect}
                    onOpenDetails={onOpenDetails}
                    onContextMenu={onContextMenu}
                  />
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export const AiTrackRow = memo(AiTrackImpl);
