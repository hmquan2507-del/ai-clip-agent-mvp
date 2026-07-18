import {
  ReviewEditorSurface,
} from "../design-system";

import type {
  ReviewEditorViewModel,
  ReviewTimelineClipDragMoveIntent,
  ReviewTimelineClipDragStartIntent,
  ReviewTimelineClipDragView,
  ReviewTimelineClipboardIntent,
  ReviewTimelineCommandIntent,
  ReviewTimelineSelectionIntent,
} from "../integration/contracts";
import type {
  ReviewTimelineDragCancelReason,
} from "../drag";

import type {
  ReviewClipboardOperation,
  ReviewTimelineCommandOperation,
} from "../api";

import {
  ReviewAICommandBar,
} from "./ai-command-bar";

import {
  ReviewEditorRail,
} from "./editor-rail";

import {
  ReviewEditorTopbar,
} from "./editor-topbar";

import {
  ReviewTimelinePanel,
} from "./timeline";

import {
  ReviewInspectorPanel,
  ReviewPreviewStage,
} from "./workspace-panels";

export interface ReviewEditorShellProps {
  view?: ReviewEditorViewModel;
  refreshing?: boolean;
  selecting?: boolean;
  commandPending?: boolean;
  clipboardPending?: boolean;
  drag?: ReviewTimelineClipDragView;

  pendingCommand:
    ReviewTimelineCommandOperation | null;

  pendingClipboardOperation:
    ReviewClipboardOperation | null;

  onRefresh?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;

  onSelectClip?: (
    intent:
      ReviewTimelineSelectionIntent,
  ) => void;

  onTimelineCommand?: (
    intent:
      ReviewTimelineCommandIntent,
  ) => void;

  onClipboardCommand?: (
    intent:
      ReviewTimelineClipboardIntent,
  ) => void;

  onClipDragStart?: (
    intent: ReviewTimelineClipDragStartIntent,
  ) => void;

  onClipDragMove?: (
    intent: ReviewTimelineClipDragMoveIntent,
  ) => void;

  onClipDragDrop?: () => void;

  onClipDragCancel?: (
    reason?: ReviewTimelineDragCancelReason,
  ) => void;
}

export function ReviewEditorShell({
  view,
  refreshing = false,
  selecting = false,
  commandPending = false,
  clipboardPending = false,
  drag,
  pendingCommand,
  pendingClipboardOperation,
  onRefresh,
  onUndo,
  onRedo,
  onSelectClip,
  onTimelineCommand,
  onClipboardCommand,
  onClipDragStart,
  onClipDragMove,
  onClipDragDrop,
  onClipDragCancel,
}: ReviewEditorShellProps) {
  return (
    <ReviewEditorSurface className="flex h-dvh min-h-[620px] flex-col overflow-hidden">
      <ReviewEditorTopbar
        view={view?.header}
        refreshing={refreshing}
        commandPending={
          commandPending ||
          clipboardPending
        }
        onRefresh={onRefresh}
        onUndo={onUndo}
        onRedo={onRedo}
      />

      <div className="grid min-h-0 flex-1 grid-cols-[64px_minmax(0,1fr)_300px] max-xl:grid-cols-[58px_minmax(0,1fr)] max-md:grid-cols-1">
        <ReviewEditorRail />

        <ReviewPreviewStage
          view={view?.preview}
        />

        <ReviewInspectorPanel
          view={view?.inspector}
        />
      </div>

      <ReviewTimelinePanel
        view={view?.timeline}
        drag={drag}
        selecting={selecting}
        commandPending={
          commandPending
        }
        clipboardPending={
          clipboardPending
        }
        pendingCommand={
          pendingCommand
        }
        pendingClipboardOperation={
          pendingClipboardOperation
        }
       onSelectClip={onSelectClip}
        onTimelineCommand={
          onTimelineCommand
        }
        onClipboardCommand={
          onClipboardCommand
        }
        onClipDragStart={
          onClipDragStart
        }
        onClipDragMove={
          onClipDragMove
        }
        onClipDragDrop={
          onClipDragDrop
        }
        onClipDragCancel={
          onClipDragCancel
        }
      />

      <ReviewAICommandBar
        disabled={Boolean(view)}
      />
    </ReviewEditorSurface>
  );
}
