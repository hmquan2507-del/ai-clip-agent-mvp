import {
  ReviewEditorSurface,
} from "../design-system";

import type {
  ReviewAICommandSubmissionIntent,
  ReviewAISuggestionIntent,
  ReviewEditorViewModel,
  ReviewTimelineClipDragMoveIntent,
  ReviewTimelineClipDragStartIntent,
  ReviewTimelineClipDragView,
  ReviewTimelineClipTrimMoveIntent,
  ReviewTimelineClipTrimStartIntent,
  ReviewTimelineClipTrimView,
  ReviewTimelineClipboardIntent,
  ReviewTimelineCommandIntent,
  ReviewRuntimeKeyboardEditingView,
  ReviewTimelineSelectionIntent,
} from "../integration/contracts";
import type {
  ReviewTimelineDragCancelReason,
} from "../drag";
import type {
  ReviewTimelineTrimCancelReason,
} from "../trim";

import type {
  AICommandSubmission,
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
  suggestionPending?: boolean;
  aiCommandPending?: boolean;
  lastAICommandSubmission?: AICommandSubmission | null;
  drag?: ReviewTimelineClipDragView;
  trim?: ReviewTimelineClipTrimView;
  keyboard?: ReviewRuntimeKeyboardEditingView;

  pendingCommand:
    ReviewTimelineCommandOperation | null;

  pendingClipboardOperation:
    ReviewClipboardOperation | null;

  onRefresh?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
  onExport?: () => void;
  exportDisabled?: boolean;

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

  onAISuggestionCommand?: (
    intent: ReviewAISuggestionIntent,
  ) => void;

  onAICommandSubmit?: (
    intent: ReviewAICommandSubmissionIntent,
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

  onClipTrimStart?: (
    intent: ReviewTimelineClipTrimStartIntent,
  ) => void;

  onClipTrimMove?: (
    intent: ReviewTimelineClipTrimMoveIntent,
  ) => void;

  onClipTrimDrop?: () => void;

  onClipTrimCancel?: (
    reason?: ReviewTimelineTrimCancelReason,
  ) => void;
}

export function ReviewEditorShell({
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
}: ReviewEditorShellProps) {
  return (
    <ReviewEditorSurface
      className="flex h-dvh min-h-[620px] flex-col overflow-hidden"
      data-review-keyboard-controls={
        keyboard?.enabled
          ? "active"
          : "inactive"
      }
      data-review-keyboard-operation={
        keyboard?.lastOperation ?? undefined
      }
    >
      <ReviewEditorTopbar
        view={view?.header}
        refreshing={refreshing}
        commandPending={
          commandPending ||
          clipboardPending ||
          suggestionPending ||
          aiCommandPending
        }
        onRefresh={onRefresh}
        onUndo={onUndo}
        onRedo={onRedo}
        onExport={onExport}
        exportDisabled={exportDisabled}
      />

      <div className="grid min-h-0 flex-1 grid-cols-[64px_minmax(0,1fr)_300px] max-xl:grid-cols-[58px_minmax(0,1fr)] max-md:grid-cols-1">
        <ReviewEditorRail />

        <ReviewPreviewStage
          view={view?.preview}
        />

        <ReviewInspectorPanel
          view={view?.inspector}
          pending={suggestionPending}
          onSuggestionIntent={
            onAISuggestionCommand
          }
        />
      </div>

      <ReviewTimelinePanel
        view={view?.timeline}
        drag={drag}
        trim={trim}
        selecting={selecting}
        commandPending={
          commandPending ||
          suggestionPending ||
          aiCommandPending
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
        onClipTrimStart={
          onClipTrimStart
        }
        onClipTrimMove={
          onClipTrimMove
        }
        onClipTrimDrop={
          onClipTrimDrop
        }
        onClipTrimCancel={
          onClipTrimCancel
        }
      />

      <ReviewAICommandBar
        key={
          lastAICommandSubmission?.submission_id ??
          "new-command"
        }
        disabled={
          !view ||
          !onAICommandSubmit ||
          commandPending ||
          clipboardPending ||
          suggestionPending
        }
        pending={aiCommandPending}
        acceptedSubmissionId={
          lastAICommandSubmission?.submission_id ?? null
        }
        onSubmit={onAICommandSubmit}
      />
    </ReviewEditorSurface>
  );
}
