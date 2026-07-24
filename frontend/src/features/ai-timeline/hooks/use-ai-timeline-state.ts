"use client";

import { useCallback, useMemo, useState } from "react";

import type { AiBlock, AiFilterKey, AiTrackKind, AiTrackState } from "../types";
import { AI_TRACK_DEFINITIONS } from "./use-ai-timeline-mock-data";

const DEFAULT_TRACK_STATE: AiTrackState = {
  visibility: "shown",
  locked: false,
  muted: false,
  collapsed: false,
};

function buildInitialTrackStates(): Record<AiTrackKind, AiTrackState> {
  const entries = AI_TRACK_DEFINITIONS.map((track) => [track.kind, { ...DEFAULT_TRACK_STATE }] as const);
  return Object.fromEntries(entries) as Record<AiTrackKind, AiTrackState>;
}

export interface AiDialogState {
  mode: "explain" | "regenerate";
  block: AiBlock;
}

export interface AiContextMenuState {
  block: AiBlock;
  x: number;
  y: number;
}

/**
 * Pure UI state for the AI Timeline layer — track show/hide/lock/mute,
 * collapse, active filters, search, hover/select, dialog + context menu.
 * No editing/runtime state lives here.
 */
export function useAiTimelineState() {
  const [trackStates, setTrackStates] = useState<Record<AiTrackKind, AiTrackState>>(buildInitialTrackStates);
  const [activeFilters, setActiveFilters] = useState<Set<AiFilterKey>>(new Set());
  const [search, setSearch] = useState("");
  const [hoveredBlockId, setHoveredBlockId] = useState<string | null>(null);
  const [selectedBlockId, setSelectedBlockId] = useState<string | null>(null);
  const [dialog, setDialog] = useState<AiDialogState | null>(null);
  const [contextMenu, setContextMenu] = useState<AiContextMenuState | null>(null);
  const [blockOverrides, setBlockOverrides] = useState<
    Record<string, Partial<Pick<AiBlock, "pinned" | "disabled" | "manual" | "generatedAtRevision">>>
  >({});
  const [dismissedStaleRevision, setDismissedStaleRevision] = useState<number | null>(null);

  const updateTrack = useCallback((kind: AiTrackKind, patch: Partial<AiTrackState>) => {
    setTrackStates((current) => ({ ...current, [kind]: { ...current[kind], ...patch } }));
  }, []);

  const toggleTrackVisibility = useCallback(
    (kind: AiTrackKind) => {
      updateTrack(kind, {
        visibility: trackStates[kind]?.visibility === "shown" ? "hidden" : "shown",
      });
    },
    [trackStates, updateTrack],
  );

  const toggleTrackLocked = useCallback(
    (kind: AiTrackKind) => updateTrack(kind, { locked: !trackStates[kind]?.locked }),
    [trackStates, updateTrack],
  );

  const toggleTrackMuted = useCallback(
    (kind: AiTrackKind) => updateTrack(kind, { muted: !trackStates[kind]?.muted }),
    [trackStates, updateTrack],
  );

  const toggleTrackCollapsed = useCallback(
    (kind: AiTrackKind) => updateTrack(kind, { collapsed: !trackStates[kind]?.collapsed }),
    [trackStates, updateTrack],
  );

  const toggleFilter = useCallback((key: AiFilterKey) => {
    setActiveFilters((current) => {
      const next = new Set(current);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  }, []);

  const clearFilters = useCallback(() => setActiveFilters(new Set()), []);

  const openExplain = useCallback((block: AiBlock) => setDialog({ mode: "explain", block }), []);
  const openRegenerate = useCallback((block: AiBlock) => setDialog({ mode: "regenerate", block }), []);
  const closeDialog = useCallback(() => setDialog(null), []);

  const openContextMenu = useCallback((block: AiBlock, x: number, y: number) => {
    setContextMenu({ block, x, y });
  }, []);
  const closeContextMenu = useCallback(() => setContextMenu(null), []);

  const togglePinned = useCallback((block: AiBlock) => {
    setBlockOverrides((current) => ({
      ...current,
      [block.id]: { ...current[block.id], pinned: !(current[block.id]?.pinned ?? block.pinned) },
    }));
  }, []);

  const toggleDisabled = useCallback((block: AiBlock) => {
    setBlockOverrides((current) => ({
      ...current,
      [block.id]: { ...current[block.id], disabled: !(current[block.id]?.disabled ?? block.disabled) },
    }));
  }, []);

  const convertToManual = useCallback((block: AiBlock) => {
    setBlockOverrides((current) => ({ ...current, [block.id]: { ...current[block.id], manual: true } }));
  }, []);

  const refreshStaleBlocks = useCallback((staleBlockIds: string[], revision: number) => {
    setBlockOverrides((current) => {
      const next = { ...current };
      for (const id of staleBlockIds) {
        next[id] = { ...next[id], generatedAtRevision: revision };
      }
      return next;
    });
  }, []);

  const dismissStaleBanner = useCallback((revision: number) => setDismissedStaleRevision(revision), []);

  return useMemo(
    () => ({
      trackStates,
      toggleTrackVisibility,
      toggleTrackLocked,
      toggleTrackMuted,
      toggleTrackCollapsed,
      activeFilters,
      toggleFilter,
      clearFilters,
      search,
      setSearch,
      hoveredBlockId,
      setHoveredBlockId,
      selectedBlockId,
      setSelectedBlockId,
      dialog,
      openExplain,
      openRegenerate,
      closeDialog,
      contextMenu,
      openContextMenu,
      closeContextMenu,
      blockOverrides,
      togglePinned,
      toggleDisabled,
      convertToManual,
      refreshStaleBlocks,
      dismissedStaleRevision,
      dismissStaleBanner,
    }),
    [
      trackStates,
      toggleTrackVisibility,
      toggleTrackLocked,
      toggleTrackMuted,
      toggleTrackCollapsed,
      activeFilters,
      toggleFilter,
      clearFilters,
      search,
      hoveredBlockId,
      selectedBlockId,
      dialog,
      openExplain,
      openRegenerate,
      closeDialog,
      contextMenu,
      openContextMenu,
      closeContextMenu,
      blockOverrides,
      togglePinned,
      toggleDisabled,
      refreshStaleBlocks,
      dismissedStaleRevision,
      dismissStaleBanner,
      convertToManual,
    ],
  );
}

export type AiTimelineState = ReturnType<typeof useAiTimelineState>;
