import type { DesktopEditorRuntimeProps } from "../types";
import { AiDecisionActionProvider } from "../../ai-decision-actions";
import {
  ASSET_LIBRARY_LAYOUT,
  INSPECTOR_LAYOUT,
  TIMELINE_LAYOUT,
  useDesktopEditorLayout,
} from "../hooks/use-desktop-editor-layout";

import { DesktopEditorHeader } from "./desktop-editor-header";
import { DesktopGrid } from "./desktop-grid";
import { EditorAssetPanel } from "./editor-asset-panel";
import { EditorInspector } from "./editor-inspector";
import { EditorPreviewCanvas } from "./editor-preview-canvas";
import { EditorStatusBar } from "./editor-status-bar";
import { EditorTimelineWorkspace } from "./editor-timeline-workspace";
import { EditorToolRail } from "./editor-tool-rail";
import { PanelDivider } from "./panel-divider";

function formatClockLabel(totalSeconds: number): string {
  if (!Number.isFinite(totalSeconds) || totalSeconds < 0) {
    return "00:00";
  }

  const minutes = Math.floor(totalSeconds / 60);
  const seconds = Math.floor(totalSeconds % 60);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

export type DesktopEditorShellProps = DesktopEditorRuntimeProps;

/**
 * Brand new Desktop Editor Shell — occupies the entire viewport, no
 * application sidebar, no dashboard, no workspace navigation. Owns layout
 * only; every piece of interactive editing behavior (preview, timeline,
 * drag/trim/keyboard, AI command submission) is delegated to the existing,
 * untouched Review runtime via the components it renders.
 *
 * Docking layout: Tool Rail (fixed) | Asset Library (resizable, left) |
 * Preview (flexible, centered) on top; Timeline (resizable height, visual
 * focus) | Inspector (resizable) on the bottom; Status Bar spans the full
 * width. Every divider drags to resize, every panel (except Tool Rail width)
 * can collapse.
 *
 * Per the error-handling rule, a runtime failure is shown only inside the
 * preview canvas — the rest of the shell (header, rail, asset panel,
 * inspector, timeline, status bar) always renders and never disappears.
 */
export function DesktopEditorShell({
  view,
  refreshing = false,
  selecting = false,
  commandPending = false,
  clipboardPending = false,
  suggestionPending = false,
  aiCommandPending = false,
  lastAICommandSubmission = null,
  drag,
  trim,
  keyboard,
  pendingCommand,
  pendingClipboardOperation,
  runtimeError = null,
  onRefresh,
  onUndo,
  onRedo,
  onExport,
  exportDisabled = false,
  onSelectClip,
  onTimelineCommand,
  onClipboardCommand,
  onAISuggestionCommand,
  onAICommandSubmit,
  onClipDragStart,
  onClipDragMove,
  onClipDragDrop,
  onClipDragCancel,
  onClipTrimStart,
  onClipTrimMove,
  onClipTrimDrop,
  onClipTrimCancel,
}: DesktopEditorShellProps) {
  // AI-suggestion apply/dismiss/regenerate has no surface in this sprint's
  // placeholder Properties tab; the AI Copilot tab's preset cards are
  // intentionally callback-only (no API, no timeline mutation) per spec.
  void onAISuggestionCommand;

  const layout = useDesktopEditorLayout();

  return (
    <div
      className="desktop-editor-theme h-dvh min-h-[640px] w-full overflow-hidden bg-[var(--desktop-editor-bg)] text-[var(--desktop-editor-text)]"
      data-desktop-editor-shell="true"
      data-desktop-editor-keyboard-controls={keyboard?.enabled ? "active" : "inactive"}
      data-desktop-editor-keyboard-operation={keyboard?.lastOperation ?? undefined}
    >
      <AiDecisionActionProvider>
      <DesktopGrid
        toolRailWidth={layout.resolvedToolRailWidth}
        assetLibraryWidth={layout.resolvedAssetLibraryWidth}
        inspectorWidth={layout.resolvedInspectorWidth}
        timelineHeight={layout.resolvedTimelineHeight}
        header={
          <DesktopEditorHeader
            productionTitle={view?.header?.title}
            autosaveLabel={view?.header?.statusLabel}
            dirty={view?.header?.dirty}
            canUndo={view?.header?.canUndo}
            canRedo={view?.header?.canRedo}
            exportDisabled={exportDisabled}
            refreshing={refreshing}
            onUndo={onUndo}
            onRedo={onRedo}
            onExport={onExport}
            onRefresh={onRefresh}
          />
        }
        rail={
          <EditorToolRail
            compact={layout.toolRailCompact}
            onToggleCompact={layout.toggleToolRailCompact}
          />
        }
        assets={
          <EditorAssetPanel
            collapsed={layout.assetLibraryCollapsed}
            onToggleCollapsed={layout.toggleAssetLibraryCollapsed}
          />
        }
        assetsDivider={
          <PanelDivider
            orientation="horizontal"
            label="Resize asset library"
            value={layout.assetLibraryWidth}
            defaultValue={ASSET_LIBRARY_LAYOUT.default}
            min={ASSET_LIBRARY_LAYOUT.min}
            max={ASSET_LIBRARY_LAYOUT.max}
            onChange={layout.setAssetLibraryWidth}
          />
        }
        preview={
          <EditorPreviewCanvas view={view?.preview} runtimeError={runtimeError} onRetry={onRefresh} />
        }
        timelineDivider={
          <PanelDivider
            orientation="vertical"
            label="Resize timeline"
            value={layout.timelineHeight}
            defaultValue={TIMELINE_LAYOUT.default}
            min={TIMELINE_LAYOUT.min}
            max={TIMELINE_LAYOUT.max}
            onChange={layout.setTimelineHeight}
            invert
          />
        }
        timeline={
          <EditorTimelineWorkspace
            view={view?.timeline}
            drag={drag}
            trim={trim}
            selecting={selecting}
            commandPending={commandPending || suggestionPending || aiCommandPending}
            clipboardPending={clipboardPending}
            pendingCommand={pendingCommand}
            pendingClipboardOperation={pendingClipboardOperation}
            onSelectClip={onSelectClip}
            onTimelineCommand={onTimelineCommand}
            onClipboardCommand={onClipboardCommand}
            onClipDragStart={onClipDragStart}
            onClipDragMove={onClipDragMove}
            onClipDragDrop={onClipDragDrop}
            onClipDragCancel={onClipDragCancel}
            onClipTrimStart={onClipTrimStart}
            onClipTrimMove={onClipTrimMove}
            onClipTrimDrop={onClipTrimDrop}
            onClipTrimCancel={onClipTrimCancel}
            collapsed={layout.timelineCollapsed}
            onToggleCollapsed={layout.toggleTimelineCollapsed}
          />
        }
        inspectorDivider={
          <PanelDivider
            orientation="horizontal"
            label="Resize inspector"
            value={layout.inspectorWidth}
            defaultValue={INSPECTOR_LAYOUT.default}
            min={INSPECTOR_LAYOUT.min}
            max={INSPECTOR_LAYOUT.max}
            onChange={layout.setInspectorWidth}
            invert
          />
        }
        inspector={
          <EditorInspector
            aiCommand={{
              disabled:
                !view || !onAICommandSubmit || commandPending || clipboardPending || suggestionPending,
              pending: aiCommandPending,
              acceptedSubmissionId: lastAICommandSubmission?.submission_id ?? null,
              onSubmit: onAICommandSubmit,
            }}
            onAiSuggestionSelect={undefined}
            collapsed={layout.inspectorCollapsed}
            onToggleCollapsed={layout.toggleInspectorCollapsed}
          />
        }
        statusBar={
          <EditorStatusBar
            fps={view?.timeline?.fps}
            durationLabel={view?.timeline?.durationLabel}
            cursorTimeLabel={view?.timeline ? formatClockLabel(view.timeline.playheadTime) : undefined}
            ready={!runtimeError}
          />
        }
      />
      </AiDecisionActionProvider>
    </div>
  );
}
