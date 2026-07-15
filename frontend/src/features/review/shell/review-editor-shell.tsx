import {
  ReviewEditorSurface,
} from "../design-system";

import type {
  ReviewEditorViewModel,
  ReviewTimelineCommandIntent,
  ReviewTimelineSelectionIntent,
} from "../integration/contracts";

import type {
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

  pendingCommand:
    ReviewTimelineCommandOperation | null;

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
}

export function ReviewEditorShell({
  view,
  refreshing = false,
  selecting = false,
  commandPending = false,
  pendingCommand,
  onRefresh,
  onUndo,
  onRedo,
  onSelectClip,
  onTimelineCommand,
}: ReviewEditorShellProps) {
  return (
    <ReviewEditorSurface className="flex h-dvh min-h-[620px] flex-col overflow-hidden">
      <ReviewEditorTopbar
        view={view?.header}
        refreshing={refreshing}
        commandPending={
          commandPending
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
        pendingCommand={
          pendingCommand
        }
       onSelectClip={onSelectClip}
        onTimelineCommand={
          onTimelineCommand
        }
      />

      <ReviewAICommandBar
        disabled={Boolean(view)}
      />
    </ReviewEditorSurface>
  );
}