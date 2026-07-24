import type {
  AICommandSubmission,
  ReviewClipboardOperation,
  ReviewTimelineCommandOperation,
} from "../review/api";
import type {
  ReviewTimelineDragCancelReason,
} from "../review/drag";
import type {
  ReviewAICommandSubmissionIntent,
  ReviewAISuggestionIntent,
  ReviewEditorViewModel,
  ReviewRuntimeKeyboardEditingView,
  ReviewTimelineClipDragMoveIntent,
  ReviewTimelineClipDragStartIntent,
  ReviewTimelineClipDragView,
  ReviewTimelineClipTrimMoveIntent,
  ReviewTimelineClipTrimStartIntent,
  ReviewTimelineClipTrimView,
  ReviewTimelineClipboardIntent,
  ReviewTimelineCommandIntent,
  ReviewTimelineSelectionIntent,
} from "../review/integration/contracts";
import type {
  ReviewTimelineTrimCancelReason,
} from "../review/trim";

/**
 * Shape of the runtime data + callbacks the Desktop Editor Shell needs.
 * Mirrors `ReviewEditorShellProps` (the existing Review runtime's shell contract)
 * since `runtime-adapter.tsx` sources this data from the same, untouched runtime.
 */
export interface DesktopEditorRuntimeProps {
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

  pendingCommand: ReviewTimelineCommandOperation | null;
  pendingClipboardOperation: ReviewClipboardOperation | null;

  runtimeError?: string | null;

  onRefresh?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
  onExport?: () => void;
  exportDisabled?: boolean;

  onSelectClip?: (intent: ReviewTimelineSelectionIntent) => void;
  onTimelineCommand?: (intent: ReviewTimelineCommandIntent) => void;
  onClipboardCommand?: (intent: ReviewTimelineClipboardIntent) => void;
  onAISuggestionCommand?: (intent: ReviewAISuggestionIntent) => void;
  onAICommandSubmit?: (intent: ReviewAICommandSubmissionIntent) => void;

  onClipDragStart?: (intent: ReviewTimelineClipDragStartIntent) => void;
  onClipDragMove?: (intent: ReviewTimelineClipDragMoveIntent) => void;
  onClipDragDrop?: () => void;
  onClipDragCancel?: (reason?: ReviewTimelineDragCancelReason) => void;

  onClipTrimStart?: (intent: ReviewTimelineClipTrimStartIntent) => void;
  onClipTrimMove?: (intent: ReviewTimelineClipTrimMoveIntent) => void;
  onClipTrimDrop?: () => void;
  onClipTrimCancel?: (reason?: ReviewTimelineTrimCancelReason) => void;
}

export type EditorToolRailTabKey =
  | "media"
  | "audio"
  | "text"
  | "stickers"
  | "effects"
  | "transitions"
  | "filters"
  | "templates"
  | "brand-kit"
  | "ai-assets";

export type EditorAssetCollectionKey =
  | "local"
  | "ai-assets"
  | "stock"
  | "photos"
  | "music"
  | "sfx"
  | "templates"
  | "brand-kit";

export type MediaAssetKind = "video" | "image" | "audio";

export interface MediaAsset {
  id: string;
  name: string;
  durationLabel: string;
  kind: MediaAssetKind;
}

export type EditorInspectorTabKey = "properties" | "ai-copilot";

export interface AiCopilotSuggestion {
  key: string;
  label: string;
  description: string;
}

export type RecentAiTaskStatus = "done" | "failed";

export interface RecentAiTask {
  id: string;
  label: string;
  status: RecentAiTaskStatus;
  timeLabel: string;
}
