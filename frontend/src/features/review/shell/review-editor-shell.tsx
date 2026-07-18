import {
  ReviewEditorSurface,
} from "../design-system";

import type {
  ReviewEditorViewModel,
  ReviewTimelineClipboardIntent,
  ReviewTimelineCommandIntent,
  ReviewTimelineSelectionIntent,
} from "../integration/contracts";

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
}

export function ReviewEditorShell({
  view,
  refreshing = false,
  selecting = false,
  commandPending = false,
  clipboardPending = false,
  pendingCommand,
  pendingClipboardOperation,
  onRefresh,
  onUndo,
  onRedo,
  onSelectClip,
  onTimelineCommand,
  onClipboardCommand,
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
      />

      <ReviewAICommandBar
        disabled={Boolean(view)}
      />
    </ReviewEditorSurface>
  );
}
