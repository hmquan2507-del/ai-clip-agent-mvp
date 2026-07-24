"use client";

import { useCallback, useMemo, useState } from "react";

export const ASSET_LIBRARY_LAYOUT = { default: 340, min: 280, max: 520, collapsed: 40 };
export const INSPECTOR_LAYOUT = { default: 360, min: 320, max: 500, collapsed: 40 };
export const TIMELINE_LAYOUT = { default: 320, min: 240, max: 520, collapsed: 64 };
export const TOOL_RAIL_LAYOUT = { expanded: 72, compact: 48 };

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

/**
 * Owns every resize/collapse dimension for the Desktop Editor's docking grid.
 * Pure UI layout state — no editing/runtime data flows through here.
 */
export function useDesktopEditorLayout() {
  const [assetLibraryWidth, setAssetLibraryWidthRaw] = useState(ASSET_LIBRARY_LAYOUT.default);
  const [inspectorWidth, setInspectorWidthRaw] = useState(INSPECTOR_LAYOUT.default);
  const [timelineHeight, setTimelineHeightRaw] = useState(TIMELINE_LAYOUT.default);

  const [assetLibraryCollapsed, setAssetLibraryCollapsed] = useState(false);
  const [inspectorCollapsed, setInspectorCollapsed] = useState(false);
  const [timelineCollapsed, setTimelineCollapsed] = useState(false);
  const [toolRailCompact, setToolRailCompact] = useState(false);

  const setAssetLibraryWidth = useCallback(
    (next: number) => setAssetLibraryWidthRaw(clamp(next, ASSET_LIBRARY_LAYOUT.min, ASSET_LIBRARY_LAYOUT.max)),
    [],
  );
  const setInspectorWidth = useCallback(
    (next: number) => setInspectorWidthRaw(clamp(next, INSPECTOR_LAYOUT.min, INSPECTOR_LAYOUT.max)),
    [],
  );
  const setTimelineHeight = useCallback(
    (next: number) => setTimelineHeightRaw(clamp(next, TIMELINE_LAYOUT.min, TIMELINE_LAYOUT.max)),
    [],
  );

  const toggleAssetLibraryCollapsed = useCallback(() => setAssetLibraryCollapsed((value) => !value), []);
  const toggleInspectorCollapsed = useCallback(() => setInspectorCollapsed((value) => !value), []);
  const toggleTimelineCollapsed = useCallback(() => setTimelineCollapsed((value) => !value), []);
  const toggleToolRailCompact = useCallback(() => setToolRailCompact((value) => !value), []);

  const resolvedAssetLibraryWidth = assetLibraryCollapsed ? ASSET_LIBRARY_LAYOUT.collapsed : assetLibraryWidth;
  const resolvedInspectorWidth = inspectorCollapsed ? INSPECTOR_LAYOUT.collapsed : inspectorWidth;
  const resolvedTimelineHeight = timelineCollapsed ? TIMELINE_LAYOUT.collapsed : timelineHeight;
  const resolvedToolRailWidth = toolRailCompact ? TOOL_RAIL_LAYOUT.compact : TOOL_RAIL_LAYOUT.expanded;

  return useMemo(
    () => ({
      assetLibraryWidth,
      inspectorWidth,
      timelineHeight,
      resolvedAssetLibraryWidth,
      resolvedInspectorWidth,
      resolvedTimelineHeight,
      resolvedToolRailWidth,
      assetLibraryCollapsed,
      inspectorCollapsed,
      timelineCollapsed,
      toolRailCompact,
      setAssetLibraryWidth,
      setInspectorWidth,
      setTimelineHeight,
      toggleAssetLibraryCollapsed,
      toggleInspectorCollapsed,
      toggleTimelineCollapsed,
      toggleToolRailCompact,
    }),
    [
      assetLibraryWidth,
      inspectorWidth,
      timelineHeight,
      resolvedAssetLibraryWidth,
      resolvedInspectorWidth,
      resolvedTimelineHeight,
      resolvedToolRailWidth,
      assetLibraryCollapsed,
      inspectorCollapsed,
      timelineCollapsed,
      toolRailCompact,
      setAssetLibraryWidth,
      setInspectorWidth,
      setTimelineHeight,
      toggleAssetLibraryCollapsed,
      toggleInspectorCollapsed,
      toggleTimelineCollapsed,
      toggleToolRailCompact,
    ],
  );
}

export type DesktopEditorLayoutState = ReturnType<typeof useDesktopEditorLayout>;
