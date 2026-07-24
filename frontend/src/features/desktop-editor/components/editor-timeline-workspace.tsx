import { useMemo } from "react";

import {
  AiTimeline,
  TimelineViewportObservedRegion,
  TimelineViewportProvider,
  type RealTimelineClipRef,
} from "../../ai-timeline";
import { ReviewTimelinePanel, type ReviewTimelinePanelProps } from "../../review/shell";
import { PanelCollapseButton } from "./panel-collapse-button";

export interface EditorTimelineWorkspaceProps extends ReviewTimelinePanelProps {
  collapsed?: boolean;
  onToggleCollapsed?: () => void;
}

/**
 * Modern shell around the existing, untouched timeline runtime UI
 * (`ReviewTimelinePanel`). No timeline logic is implemented or duplicated here.
 *
 * Both the AI Timeline layer and the real timeline now share ONE
 * `TimelineViewportProvider` — see `features/ai-timeline/context` for how
 * playhead/revision/selection (real props, no DOM tricks) and zoom/scroll
 * (observed from the real timeline's own scroll container, read-only) are
 * unified into a single coordinate system without editing `ReviewTimelinePanel`.
 */
export function EditorTimelineWorkspace({
  collapsed = false,
  onToggleCollapsed,
  ...panelProps
}: EditorTimelineWorkspaceProps) {
  const realClips = useMemo<RealTimelineClipRef[]>(
    () =>
      (panelProps.view?.tracks ?? []).flatMap((track) =>
        track.clips.map((clip) => ({ id: clip.id, startTime: clip.startTime, endTime: clip.endTime })),
      ),
    [panelProps.view],
  );

  if (collapsed) {
    return (
      <div className="flex h-full w-full items-center justify-between border-t border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-surface)] px-3">
        <span className="text-[11px] font-semibold uppercase tracking-[0.1em] text-[var(--desktop-editor-text-subtle)]">
          Timeline
        </span>
        <PanelCollapseButton direction="up" label="Restore timeline" onClick={() => onToggleCollapsed?.()} />
      </div>
    );
  }

  return (
    <TimelineViewportProvider
      duration={panelProps.view?.duration ?? 0}
      playheadTime={panelProps.view?.playheadTime ?? 0}
      revision={panelProps.view?.revision ?? 0}
      selectedClipIds={panelProps.view?.clipboard.selectedClipIds ?? []}
    >
      <div className="flex h-full min-h-0 w-full flex-col border-t border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-surface)]">
        <div className="flex h-7 shrink-0 items-center justify-between border-b border-[var(--desktop-editor-border-subtle)] px-2.5">
          <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--desktop-editor-text-subtle)]">
            Timeline
          </span>
          <PanelCollapseButton direction="down" label="Collapse timeline" onClick={() => onToggleCollapsed?.()} />
        </div>

        <div className="h-[140px] shrink-0 overflow-hidden">
          <AiTimeline
            realClips={realClips}
            onRequestSelectClip={(clipId) =>
              panelProps.onSelectClip?.({ clipId, additive: false, moveCursor: true })
            }
          />
        </div>

        <TimelineViewportObservedRegion className="min-h-0 flex-1">
          <ReviewTimelinePanel {...panelProps} />
        </TimelineViewportObservedRegion>
      </div>
    </TimelineViewportProvider>
  );
}
