"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

// 16.10.6.1 UI/UX refinement: Asset/Inspector defaults narrowed and Tool Rail
// shrunk to the sprint's target ranges so Preview gets more of the width by
// default (Requirement 1) — panels remain fully resizable/collapsible within
// their new ranges, nothing about the resize/collapse mechanism changed.
export const ASSET_LIBRARY_LAYOUT = { default: 300, min: 280, max: 320, collapsed: 40 };
export const INSPECTOR_LAYOUT = { default: 320, min: 300, max: 340, collapsed: 40 };
export const TIMELINE_LAYOUT = { default: 320, min: 240, max: 520, collapsed: 64 };
export const TOOL_RAIL_LAYOUT = { expanded: 64, compact: 48 };

// Sprint 17.2 responsive shell behavior. "Usable" per
// `frontend-responsive-system.md`: the preview retains a legible aspect
// ratio. 480px is comfortably below the 630px worst-case remainder already
// verified at 1366×768 with every panel at its max width, so this only
// engages the auto-narrow/collapse priority in genuinely tight windows
// (e.g. a user manually dragging every divider to max on a small monitor).
const PREVIEW_MIN_WIDTH_PX = 480;
const DIVIDER_WIDTH_PX = 6;

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

/**
 * Applies the collapse priority order from `desktop-editor-ux-blueprint.md`
 * §5 / `frontend-responsive-system.md`: compact tool rail → narrow Asset
 * Panel → collapse Asset Panel → narrow Inspector → collapse Inspector.
 * Preview and Timeline are never touched — they are the floor.
 *
 * Pure function of the user's current preferences + viewport width; it never
 * mutates the underlying width/collapse state, so widening the window back
 * out restores exactly what the user had chosen.
 */
export function computeResponsiveDesktopEditorLayout(input: {
  viewportWidth: number;
  toolRailCompact: boolean;
  assetLibraryWidth: number;
  assetLibraryCollapsed: boolean;
  inspectorWidth: number;
  inspectorCollapsed: boolean;
}) {
  const {
    viewportWidth,
    toolRailCompact,
    assetLibraryWidth,
    assetLibraryCollapsed,
    inspectorWidth,
    inspectorCollapsed,
  } = input;

  let autoToolRailCompact = toolRailCompact;
  let autoAssetWidth = assetLibraryCollapsed ? ASSET_LIBRARY_LAYOUT.collapsed : assetLibraryWidth;
  let autoAssetCollapsed = assetLibraryCollapsed;
  let autoInspectorWidth = inspectorCollapsed ? INSPECTOR_LAYOUT.collapsed : inspectorWidth;
  let autoInspectorCollapsed = inspectorCollapsed;

  const previewBudget = () =>
    viewportWidth -
    (autoToolRailCompact ? TOOL_RAIL_LAYOUT.compact : TOOL_RAIL_LAYOUT.expanded) -
    autoAssetWidth -
    autoInspectorWidth -
    DIVIDER_WIDTH_PX * 2;

  const steps: Array<() => void> = [
    () => {
      autoToolRailCompact = true;
    },
    () => {
      autoAssetWidth = ASSET_LIBRARY_LAYOUT.min;
    },
    () => {
      autoAssetWidth = ASSET_LIBRARY_LAYOUT.collapsed;
      autoAssetCollapsed = true;
    },
    () => {
      autoInspectorWidth = INSPECTOR_LAYOUT.min;
    },
    () => {
      autoInspectorWidth = INSPECTOR_LAYOUT.collapsed;
      autoInspectorCollapsed = true;
    },
  ];

  for (const step of steps) {
    if (previewBudget() >= PREVIEW_MIN_WIDTH_PX) break;
    step();
  }

  return {
    toolRailCompact: autoToolRailCompact,
    assetLibraryWidth: autoAssetWidth,
    assetLibraryAutoCollapsed: autoAssetCollapsed && !assetLibraryCollapsed,
    inspectorWidth: autoInspectorWidth,
    inspectorAutoCollapsed: autoInspectorCollapsed && !inspectorCollapsed,
    previewFloorProtected: previewBudget() >= PREVIEW_MIN_WIDTH_PX,
  };
}

/** rAF-throttled window width tracker — reuses the observe-then-throttle
 * pattern already proven in `TimelineViewportContext` rather than adding a
 * second, uncoordinated observer mechanism. */
function useViewportWidth(): number {
  const [width, setWidth] = useState(() => (typeof window === "undefined" ? 1920 : window.innerWidth));

  useEffect(() => {
    if (typeof window === "undefined") return;

    let frame = 0;
    const handleResize = () => {
      if (frame) return;
      frame = window.requestAnimationFrame(() => {
        frame = 0;
        setWidth(window.innerWidth);
      });
    };

    handleResize();
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      if (frame) window.cancelAnimationFrame(frame);
    };
  }, []);

  return width;
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

  const viewportWidth = useViewportWidth();

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

  const toggleTimelineCollapsed = useCallback(() => setTimelineCollapsed((value) => !value), []);

  const responsive = useMemo(
    () =>
      computeResponsiveDesktopEditorLayout({
        viewportWidth,
        toolRailCompact,
        assetLibraryWidth,
        assetLibraryCollapsed,
        inspectorWidth,
        inspectorCollapsed,
      }),
    [viewportWidth, toolRailCompact, assetLibraryWidth, assetLibraryCollapsed, inspectorWidth, inspectorCollapsed],
  );

  const effectiveAssetLibraryCollapsed = assetLibraryCollapsed || responsive.assetLibraryAutoCollapsed;
  const effectiveInspectorCollapsed = inspectorCollapsed || responsive.inspectorAutoCollapsed;

  // Toggle flips the EFFECTIVE (visible) state, not just the raw preference —
  // otherwise clicking "expand" while auto-collapsed (raw=false already)
  // would flip raw to true and collapse it further instead of expanding it.
  const toggleAssetLibraryCollapsed = useCallback(
    () => setAssetLibraryCollapsed(!effectiveAssetLibraryCollapsed),
    [effectiveAssetLibraryCollapsed],
  );
  const toggleInspectorCollapsed = useCallback(
    () => setInspectorCollapsed(!effectiveInspectorCollapsed),
    [effectiveInspectorCollapsed],
  );
  const toggleToolRailCompact = useCallback(() => setToolRailCompact((value) => !value), []);

  const resolvedAssetLibraryWidth = responsive.assetLibraryWidth;
  const resolvedInspectorWidth = responsive.inspectorWidth;
  const resolvedTimelineHeight = timelineCollapsed ? TIMELINE_LAYOUT.collapsed : timelineHeight;
  const resolvedToolRailWidth = responsive.toolRailCompact ? TOOL_RAIL_LAYOUT.compact : TOOL_RAIL_LAYOUT.expanded;

  return useMemo(
    () => ({
      assetLibraryWidth,
      inspectorWidth,
      timelineHeight,
      resolvedAssetLibraryWidth,
      resolvedInspectorWidth,
      resolvedTimelineHeight,
      resolvedToolRailWidth,
      assetLibraryCollapsed: effectiveAssetLibraryCollapsed,
      inspectorCollapsed: effectiveInspectorCollapsed,
      timelineCollapsed,
      toolRailCompact: responsive.toolRailCompact,
      previewFloorProtected: responsive.previewFloorProtected,
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
      effectiveAssetLibraryCollapsed,
      effectiveInspectorCollapsed,
      timelineCollapsed,
      responsive,
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
