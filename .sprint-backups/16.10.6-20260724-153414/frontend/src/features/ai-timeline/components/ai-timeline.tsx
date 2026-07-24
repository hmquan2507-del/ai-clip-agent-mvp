"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { RefreshCw, Search, X } from "lucide-react";

import type { AiBlock, AiBlockAction, AiBlockActionIntent, AiFilterKey, AiTrackState } from "../types";
import { useTimelineViewportContext } from "../context/timeline-viewport-context";
import { useAiTimelineMockData, type RealTimelineClipRef } from "../hooks/use-ai-timeline-mock-data";
import { useAiTimelineState } from "../hooks/use-ai-timeline-state";
import { AiConnectionView } from "./ai-connection";
import { AiRegenerateDialog } from "./ai-regenerate-dialog";
import { AiTooltip } from "./ai-tooltip";
import { AiTrackRow, AI_TRACK_HEADER_WIDTH } from "./ai-track";
import { TRACK_COLOR } from "./ai-block";

const FILTERS: Array<{ key: AiFilterKey; label: string }> = [
  { key: "hook", label: "Hook" },
  { key: "subtitle", label: "Subtitle" },
  { key: "broll", label: "B-roll" },
  { key: "cta", label: "CTA" },
  { key: "emotion", label: "Emotion" },
  { key: "zoom", label: "Zoom" },
  { key: "silence", label: "Silence" },
];

const HIDDEN_TRACK_STATE: AiTrackState = { visibility: "hidden", locked: false, muted: false, collapsed: false };
const PLAYHEAD_COLOR = "#ff4d6d";

export interface AiTimelineProps {
  realClips?: RealTimelineClipRef[];
  onBlockAction?: (intent: AiBlockActionIntent) => void;
  /** Bubbles an AI block's linked real clip id up so a parent can call the real (untouched) selectClip action — the AI layer never calls it directly. */
  onRequestSelectClip?: (clipId: string) => void;
}

/**
 * The AI Timeline layer. This sprint removes its independent viewport —
 * position, scroll, zoom, playhead, and selection are all read from
 * `TimelineViewportContext`, the single shared coordinate system also
 * observed from the real (untouched) Timeline Runtime. See
 * `context/timeline-viewport-context.tsx` for exactly how that's sourced
 * without editing any runtime file.
 */
export function AiTimeline({ realClips = [], onBlockAction, onRequestSelectClip }: AiTimelineProps) {
  const viewport = useTimelineViewportContext();
  const { tracks, blocks: rawBlocks } = useAiTimelineMockData(viewport.duration, viewport.revision, realClips);
  const state = useAiTimelineState();

  const scrollRef = useRef<HTMLDivElement | null>(null);
  const [pointerPosition, setPointerPosition] = useState<{ x: number; y: number } | null>(null);
  const isRelayingScroll = useRef(false);

  // Keep this timeline's own scroll container mirrored to the shared
  // viewport's scrollLeft (which itself mirrors the real timeline's scroll).
  useEffect(() => {
    const node = scrollRef.current;
    if (!node || isRelayingScroll.current) return;
    if (Math.abs(node.scrollLeft - viewport.scrollLeft) > 0.5) {
      node.scrollLeft = viewport.scrollLeft;
    }
  }, [viewport.scrollLeft]);

  const handleScroll = useCallback(
    (event: React.UIEvent<HTMLDivElement>) => {
      isRelayingScroll.current = true;
      viewport.setScrollLeft(event.currentTarget.scrollLeft);
      isRelayingScroll.current = false;
    },
    [viewport],
  );

  const blocks = useMemo(
    () => rawBlocks.map((block) => ({ ...block, ...state.blockOverrides[block.id] })),
    [rawBlocks, state.blockOverrides],
  );

  const blocksByTrack = useMemo(() => {
    const map = new Map<string, AiBlock[]>();
    for (const block of blocks) {
      const list = map.get(block.trackKind) ?? [];
      list.push(block);
      map.set(block.trackKind, list);
    }
    return map;
  }, [blocks]);

  const staleBlocks = useMemo(
    () => blocks.filter((block) => block.generatedAtRevision != null && block.generatedAtRevision !== viewport.revision),
    [blocks, viewport.revision],
  );
  const staleBannerVisible = staleBlocks.length > 0 && state.dismissedStaleRevision !== viewport.revision;

  const query = state.search.trim().toLowerCase();
  const matchingBlockIds = useMemo(() => {
    if (!query) return null;
    const ids = new Set<string>();
    for (const block of blocks) {
      if (block.title.toLowerCase().includes(query) || block.reason.toLowerCase().includes(query)) {
        ids.add(block.id);
      }
    }
    return ids;
  }, [blocks, query]);

  const [flashBlockId, setFlashBlockId] = useState<string | null>(null);

  const jumpToFirstMatch = useCallback(() => {
    if (!matchingBlockIds || matchingBlockIds.size === 0) return;
    const first = blocks.find((block) => matchingBlockIds.has(block.id));
    if (!first) return;
    viewport.setScrollLeft(
      Math.max(0, first.startTime * viewport.pixelsPerSecond - viewport.timelineWidth / 2),
    );
    setFlashBlockId(first.id);
    window.setTimeout(() => setFlashBlockId((current) => (current === first.id ? null : current)), 900);
  }, [blocks, matchingBlockIds, viewport]);

  const hoveredBlock = state.hoveredBlockId ? blocks.find((block) => block.id === state.hoveredBlockId) : null;

  const handleOpenDetails = useCallback((block: AiBlock) => state.openExplain(block), [state]);

  const handleSelect = useCallback(
    (block: AiBlock) => {
      state.setSelectedBlockId(block.id);
      if (block.linkedClipId) onRequestSelectClip?.(block.linkedClipId);
    },
    [onRequestSelectClip, state],
  );

  const handleContextAction = useCallback(
    (action: AiBlockAction, block: AiBlock) => {
      switch (action) {
        case "explain":
          state.openExplain(block);
          break;
        case "regenerate":
          state.openRegenerate(block);
          break;
        case "pin":
          state.togglePinned(block);
          break;
        case "disable":
          state.toggleDisabled(block);
          break;
        case "convert-to-manual":
          state.convertToManual(block);
          break;
        default:
          break;
      }
      onBlockAction?.({ action, block });
      state.closeContextMenu();
    },
    [onBlockAction, state],
  );

  const totalRowsHeight = useMemo(
    () =>
      tracks.reduce((sum, track) => {
        if (state.trackStates[track.kind]?.visibility === "hidden") return sum;
        return sum + (state.trackStates[track.kind]?.collapsed ? 24 : 40);
      }, 0),
    [tracks, state.trackStates],
  );

  const playheadLeft = AI_TRACK_HEADER_WIDTH + viewport.playheadTime * viewport.pixelsPerSecond - viewport.scrollLeft;

  return (
    <div
      className="ai-timeline-theme flex h-full min-h-0 flex-col border-b border-[var(--ai-timeline-border)] bg-[var(--ai-timeline-bg)]"
      data-ai-timeline="true"
      data-ai-timeline-connected={viewport.connected}
    >
      <div className="flex h-9 shrink-0 items-center gap-2 border-b border-[var(--ai-timeline-border-subtle)] px-2">
        <span className="flex shrink-0 items-center gap-1.5 text-[11px] font-semibold text-[var(--ai-timeline-primary-text)]">
          ✨ AI Timeline
        </span>

        <label className="flex h-6 w-40 shrink-0 items-center gap-1 rounded-md border border-[var(--ai-timeline-border)] bg-[var(--ai-timeline-surface)] px-1.5">
          <Search className="size-3 shrink-0 text-[var(--ai-timeline-text-subtle)]" />
          <input
            type="search"
            value={state.search}
            onChange={(event) => state.setSearch(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") jumpToFirstMatch();
            }}
            placeholder="Search AI decisions"
            aria-label="Search AI decisions"
            className="min-w-0 flex-1 bg-transparent text-[10px] text-[var(--ai-timeline-text)] outline-none placeholder:text-[var(--ai-timeline-text-subtle)]"
          />
          {state.search ? (
            <button
              type="button"
              aria-label="Clear search"
              onClick={() => state.setSearch("")}
              className="text-[var(--ai-timeline-text-subtle)] hover:text-[var(--ai-timeline-text)]"
            >
              <X className="size-3" />
            </button>
          ) : null}
        </label>

        <div className="flex flex-1 items-center gap-1 overflow-x-auto">
          {FILTERS.map((filter) => {
            const active = state.activeFilters.has(filter.key);
            return (
              <button
                key={filter.key}
                type="button"
                aria-pressed={active}
                onClick={() => state.toggleFilter(filter.key)}
                className={
                  active
                    ? "shrink-0 rounded-full bg-[var(--ai-timeline-primary-soft)] px-2 py-0.5 text-[10px] font-semibold text-[var(--ai-timeline-primary-text)]"
                    : "shrink-0 rounded-full border border-[var(--ai-timeline-border)] px-2 py-0.5 text-[10px] font-medium text-[var(--ai-timeline-text-subtle)] hover:text-[var(--ai-timeline-text)]"
                }
              >
                {filter.label}
              </button>
            );
          })}
          {state.activeFilters.size > 0 ? (
            <button
              type="button"
              onClick={state.clearFilters}
              className="shrink-0 text-[10px] font-medium text-[var(--ai-timeline-text-subtle)] underline hover:text-[var(--ai-timeline-text)]"
            >
              Clear
            </button>
          ) : null}
        </div>

        <RevisionIndicator revision={viewport.revision} connected={viewport.connected} staleCount={staleBlocks.length} />

        <AiMiniMap
          blocks={blocks}
          duration={viewport.duration}
          trackStates={state.trackStates}
          activeFilters={state.activeFilters}
          tracks={tracks.map((t) => ({ kind: t.kind, filterKey: t.filterKey }))}
          viewportStart={viewport.visibleRange.startTime}
          viewportEnd={viewport.visibleRange.endTime}
          playheadTime={viewport.playheadTime}
          onSeek={(time) =>
            viewport.setScrollLeft(Math.max(0, time * viewport.pixelsPerSecond - viewport.timelineWidth / 2))
          }
        />
      </div>

      {staleBannerVisible ? (
        <div className="flex h-7 shrink-0 items-center gap-2 border-b border-[var(--ai-timeline-warning-text)]/30 bg-[var(--ai-timeline-warning-text)]/10 px-2 text-[10px] text-[var(--ai-timeline-warning-text)]">
          <span>
            {staleBlocks.length} AI decision{staleBlocks.length === 1 ? "" : "s"} may be stale — the timeline changed
            since they were generated.
          </span>
          <div className="ml-auto flex items-center gap-2">
            <button
              type="button"
              className="font-semibold underline"
              onClick={() => state.refreshStaleBlocks(staleBlocks.map((b) => b.id), viewport.revision)}
            >
              Refresh
            </button>
            <button
              type="button"
              className="font-semibold underline"
              onClick={() => state.dismissStaleBanner(viewport.revision)}
            >
              Keep
            </button>
            <button type="button" className="font-semibold underline" onClick={() => state.openExplain(staleBlocks[0])}>
              Compare
            </button>
          </div>
        </div>
      ) : null}

      <div
        ref={scrollRef}
        onScroll={handleScroll}
        onMouseMove={(event) => setPointerPosition({ x: event.clientX, y: event.clientY })}
        className="relative min-h-0 flex-1 overflow-auto"
      >
        <div style={{ position: "relative", width: AI_TRACK_HEADER_WIDTH + viewport.duration * viewport.pixelsPerSecond }}>
          {tracks.map((track) => {
            const activeFilterCount = state.activeFilters.size;
            const passesFilter =
              activeFilterCount === 0 || (track.filterKey ? state.activeFilters.has(track.filterKey) : false);
            const trackState = passesFilter ? state.trackStates[track.kind] : HIDDEN_TRACK_STATE;

            return (
              <AiTrackRow
                key={track.kind}
                track={track}
                state={trackState}
                blocks={blocksByTrack.get(track.kind) ?? []}
                pixelsPerSecond={viewport.pixelsPerSecond}
                visibleRange={viewport.visibleRange}
                highlightedBlockIds={matchingBlockIds ?? (flashBlockId ? new Set([flashBlockId]) : null)}
                hoveredBlockId={state.hoveredBlockId}
                selectedBlockId={state.selectedBlockId}
                selectedClipIds={viewport.selection}
                currentRevision={viewport.revision}
                onToggleCollapsed={() => state.toggleTrackCollapsed(track.kind)}
                onToggleVisibility={() => state.toggleTrackVisibility(track.kind)}
                onToggleLocked={() => state.toggleTrackLocked(track.kind)}
                onToggleMuted={() => state.toggleTrackMuted(track.kind)}
                onHoverChange={state.setHoveredBlockId}
                onSelect={handleSelect}
                onOpenDetails={handleOpenDetails}
                onContextMenu={state.openContextMenu}
              />
            );
          })}

          {hoveredBlock ? (
            <AiConnectionView
              left={AI_TRACK_HEADER_WIDTH + hoveredBlock.startTime * viewport.pixelsPerSecond}
              height={totalRowsHeight}
              color={TRACK_COLOR[hoveredBlock.trackKind]}
            />
          ) : null}

          <AiConnectionView left={playheadLeft} height={totalRowsHeight} color={PLAYHEAD_COLOR} />
        </div>
      </div>

      {hoveredBlock && pointerPosition ? (
        <AiTooltip block={hoveredBlock} x={pointerPosition.x} y={pointerPosition.y} />
      ) : null}

      {state.contextMenu ? (
        <AiContextMenu
          x={state.contextMenu.x}
          y={state.contextMenu.y}
          block={state.contextMenu.block}
          onAction={handleContextAction}
          onClose={state.closeContextMenu}
        />
      ) : null}

      {state.dialog ? (
        <AiRegenerateDialog
          dialog={state.dialog}
          onClose={state.closeDialog}
          onRegenerate={(block) => {
            onBlockAction?.({ action: "regenerate", block });
            state.closeDialog();
          }}
        />
      ) : null}
    </div>
  );
}

function RevisionIndicator({
  revision,
  connected,
  staleCount,
}: {
  revision: number;
  connected: boolean;
  staleCount: number;
}) {
  return (
    <div className="flex shrink-0 items-center gap-1.5 rounded-md border border-[var(--ai-timeline-border)] px-2 py-0.5 text-[9px] text-[var(--ai-timeline-text-subtle)]">
      <span
        aria-hidden
        className={connected ? "size-1.5 rounded-full bg-[#65dfa9]" : "size-1.5 rounded-full bg-[var(--ai-timeline-warning-text)]"}
      />
      <span>Rev {revision}</span>
      {staleCount > 0 ? (
        <span className="flex items-center gap-0.5 font-semibold text-[var(--ai-timeline-warning-text)]">
          <RefreshCw className="size-2.5" />
          {staleCount} stale
        </span>
      ) : null}
    </div>
  );
}

const CONTEXT_MENU_ITEMS: Array<{ action: AiBlockAction; label: string }> = [
  { action: "regenerate", label: "Regenerate" },
  { action: "disable", label: "Disable" },
  { action: "duplicate", label: "Duplicate" },
  { action: "convert-to-manual", label: "Convert to Manual" },
  { action: "delete", label: "Delete" },
  { action: "pin", label: "Pin" },
  { action: "explain", label: "Explain" },
];

function AiContextMenu({
  x,
  y,
  block,
  onAction,
  onClose,
}: {
  x: number;
  y: number;
  block: AiBlock;
  onAction: (action: AiBlockAction, block: AiBlock) => void;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-40" onClick={onClose} onContextMenu={(event) => event.preventDefault()}>
      <ul
        role="menu"
        aria-label={`Actions for ${block.title}`}
        style={{ left: x, top: y }}
        className="fixed z-50 w-44 rounded-[var(--ai-timeline-radius)] border border-[var(--ai-timeline-border)] bg-[var(--ai-timeline-surface)] py-1 shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        {CONTEXT_MENU_ITEMS.map((item) => (
          <li key={item.action}>
            <button
              type="button"
              role="menuitem"
              onClick={() => onAction(item.action, block)}
              className="block w-full px-3 py-1.5 text-left text-[11px] text-[var(--ai-timeline-text)] hover:bg-white/5"
            >
              {item.label}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function AiMiniMap({
  blocks,
  duration,
  trackStates,
  activeFilters,
  tracks,
  viewportStart,
  viewportEnd,
  playheadTime,
  onSeek,
}: {
  blocks: AiBlock[];
  duration: number;
  trackStates: ReturnType<typeof useAiTimelineState>["trackStates"];
  activeFilters: Set<AiFilterKey>;
  tracks: Array<{ kind: AiBlock["trackKind"]; filterKey?: AiFilterKey }>;
  viewportStart: number;
  viewportEnd: number;
  playheadTime: number;
  onSeek: (time: number) => void;
}) {
  const safeDuration = duration > 0 ? duration : 1;
  const visibleKinds = useMemo(() => {
    const kinds = new Set<AiBlock["trackKind"]>();
    for (const track of tracks) {
      const passesFilter = activeFilters.size === 0 || (track.filterKey ? activeFilters.has(track.filterKey) : false);
      if (passesFilter && trackStates[track.kind]?.visibility === "shown") {
        kinds.add(track.kind);
      }
    }
    return kinds;
  }, [tracks, trackStates, activeFilters]);

  const viewportLeftPct = Math.min(100, Math.max(0, (viewportStart / safeDuration) * 100));
  const viewportWidthPct = Math.min(100 - viewportLeftPct, Math.max(0, ((viewportEnd - viewportStart) / safeDuration) * 100));
  const playheadPct = Math.min(100, Math.max(0, (playheadTime / safeDuration) * 100));

  return (
    <div
      role="img"
      aria-label="Production overview mini map"
      onClick={(event) => {
        const rect = event.currentTarget.getBoundingClientRect();
        const pct = (event.clientX - rect.left) / rect.width;
        onSeek(pct * safeDuration);
      }}
      className="relative h-5 w-40 shrink-0 cursor-pointer overflow-hidden rounded-md border border-[var(--ai-timeline-border)] bg-[var(--ai-timeline-surface)]"
    >
      {blocks
        .filter((block) => visibleKinds.has(block.trackKind))
        .map((block) => (
          <span
            key={block.id}
            style={{
              left: `${(block.startTime / safeDuration) * 100}%`,
              backgroundColor: TRACK_COLOR[block.trackKind],
            }}
            className="absolute top-1/2 size-1 -translate-y-1/2 rounded-full"
          />
        ))}
      <span
        style={{ left: `${viewportLeftPct}%`, width: `${viewportWidthPct}%` }}
        className="absolute top-0 h-full border border-white/70 bg-white/10"
      />
      <span style={{ left: `${playheadPct}%` }} className="absolute top-0 h-full w-px bg-[#ff4d6d]" />
    </div>
  );
}
