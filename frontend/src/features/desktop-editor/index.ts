export { DesktopEditorRuntimeAdapter } from "./runtime-adapter";
export type { DesktopEditorRuntimeAdapterProps } from "./runtime-adapter";

export { DesktopEditorShell } from "./components/desktop-editor-shell";
export type { DesktopEditorShellProps } from "./components/desktop-editor-shell";

export { DesktopEditorHeader } from "./components/desktop-editor-header";
export type { DesktopEditorHeaderProps } from "./components/desktop-editor-header";

export { EditorToolRail } from "./components/editor-tool-rail";
export type { EditorToolRailProps } from "./components/editor-tool-rail";

export { EditorAssetPanel } from "./components/editor-asset-panel";
export type { EditorAssetPanelProps } from "./components/editor-asset-panel";

export { EditorPreviewCanvas } from "./components/editor-preview-canvas";
export type { EditorPreviewCanvasProps } from "./components/editor-preview-canvas";

export { EditorInspector } from "./components/editor-inspector";
export type { EditorInspectorProps } from "./components/editor-inspector";

export { EditorAiCopilot } from "./components/editor-ai-copilot";
export type { EditorAiCopilotProps } from "./components/editor-ai-copilot";

export { EditorTimelineWorkspace } from "./components/editor-timeline-workspace";
export type { EditorTimelineWorkspaceProps } from "./components/editor-timeline-workspace";

export { EditorStatusBar } from "./components/editor-status-bar";
export type { EditorStatusBarProps } from "./components/editor-status-bar";

export { DesktopGrid } from "./components/desktop-grid";
export type { DesktopGridProps } from "./components/desktop-grid";

export { PanelDivider } from "./components/panel-divider";
export type { PanelDividerProps } from "./components/panel-divider";

export { PanelCollapseButton } from "./components/panel-collapse-button";
export type { PanelCollapseButtonProps, PanelCollapseDirection } from "./components/panel-collapse-button";

export { useLayoutResizer } from "./components/layout-resizer";
export type {
  LayoutResizerHandlers,
  LayoutResizerOrientation,
  UseLayoutResizerOptions,
} from "./components/layout-resizer";

export {
  ASSET_LIBRARY_LAYOUT,
  INSPECTOR_LAYOUT,
  TIMELINE_LAYOUT,
  TOOL_RAIL_LAYOUT,
  useDesktopEditorLayout,
} from "./hooks/use-desktop-editor-layout";
export type { DesktopEditorLayoutState } from "./hooks/use-desktop-editor-layout";

export { usePanelCollapse } from "./hooks/use-panel-collapse";

export * from "./types";
