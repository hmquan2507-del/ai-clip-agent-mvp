"use client";

import { useState } from "react";
import type { DesktopEditorRuntimeProps, EditorToolRailTabKey } from "../types";
import { AiDecisionActionProvider } from "../../ai-decision-actions";
import {
  ASSET_LIBRARY_LAYOUT,
  INSPECTOR_LAYOUT,
  TIMELINE_LAYOUT,
  useDesktopEditorLayout,
} from "../hooks/use-desktop-editor-layout";

import { DesktopEditorHeader } from "./desktop-editor-header";
import { DesktopGrid } from "./desktop-grid";
import { EditorAiDirectorDock } from "./editor-ai-director-dock";
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
  assets,
  assetsLoading = false,
  assetsError = null,
}: DesktopEditorShellProps) {
  void onAISuggestionCommand;

  const layout = useDesktopEditorLayout();
  const [activeToolTab, setActiveToolTab] = useState<EditorToolRailTabKey>("media");
  const [activeVideoUrl, setActiveVideoUrl] = useState<string | null>(null);
  const [headlineText, setHeadlineText] = useState<string>("3 GIÂY ĐẦU QUYẾT ĐỊNH TẤT CẢ");
  const [subtitleText, setSubtitleText] = useState<string>("Hook mạnh giúp người xem dừng lại ngay từ giây đầu tiên");
  const [videoScale, setVideoScale] = useState<number>(100);
  const [videoRotation, setVideoRotation] = useState<number>(0);
  const [videoOpacity, setVideoOpacity] = useState<number>(100);
  const [audioVolume, setAudioVolume] = useState<number>(100);

  return (
    <div
      className="desktop-editor-theme h-dvh min-h-[640px] w-full overflow-hidden bg-[var(--ce-bg-workspace)] text-[var(--ce-text-primary)]"
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
            activeTab={activeToolTab}
            onTabChange={setActiveToolTab}
            compact={layout.toolRailCompact}
            onToggleCompact={layout.toggleToolRailCompact}
          />
        }
        assets={
          <EditorAssetPanel
            assets={assets}
            loading={assetsLoading}
            error={assetsError}
            onSelectAsset={(_id, mediaUrl) => {
              if (mediaUrl) setActiveVideoUrl(mediaUrl);
            }}
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
          <EditorPreviewCanvas
            view={
              view?.preview
                ? {
                    ...view.preview,
                    headline: headlineText,
                    subtitle: subtitleText,
                    videoUrl: activeVideoUrl ?? view.preview.videoUrl,
                  }
                : undefined
            }
            runtimeError={runtimeError}
            onRetry={onRefresh}
          />
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
            headline={headlineText}
            onHeadlineChange={setHeadlineText}
            subtitle={subtitleText}
            onSubtitleChange={setSubtitleText}
            scale={videoScale}
            onScaleChange={setVideoScale}
            rotation={videoRotation}
            onRotationChange={setVideoRotation}
            opacity={videoOpacity}
            onOpacityChange={setVideoOpacity}
            volume={audioVolume}
            onVolumeChange={setAudioVolume}
            onAiSuggestionSelect={undefined}
            collapsed={layout.inspectorCollapsed}
            onToggleCollapsed={layout.toggleInspectorCollapsed}
          />
        }
        aiDirectorDock={<EditorAiDirectorDock />}
        statusBar={
          <EditorStatusBar
            zoomLabel="58%"
            snapEnabled={true}
            fps={view?.timeline?.fps ?? 30}
            resolutionLabel="1080×1920"
            playbackSpeedLabel="1.0x"
            cursorTimeLabel={view?.timeline ? formatClockLabel(view.timeline.playheadTime) : "00:00"}
            durationLabel={view?.timeline?.durationLabel ?? "00:18"}
            ready={!runtimeError}
          />
        }
      />
      </AiDecisionActionProvider>
    </div>
  );
}
