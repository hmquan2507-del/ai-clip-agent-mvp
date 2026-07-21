import type {
  ReviewAISuggestionOperation,
} from "../api";
import type {
  ReviewBadgeTone,
} from "../design-system";
import type {
  ReviewTimelineDragPoint,
  ReviewTimelineDragRuntimeState,
  ReviewTimelineTrackLane,
  ReviewTimelineViewport,
} from "../drag";
import type {
  ReviewTimelineTrimCancelReason,
  ReviewTimelineTrimHandle,
  ReviewTimelineTrimRuntimeState,
} from "../trim";
import type {
  ReviewTimelineKeyboardOperation,
  ReviewTimelineKeyboardRuntimeState,
} from "../keyboard";

export type ReviewTimelineClipTone =
  | "video"
  | "broll"
  | "subtitle"
  | "audio";

export interface ReviewTimelineSelectionIntent {
  clipId: string;
  additive: boolean;
  moveCursor: boolean;
}

export interface ReviewTimelineGapView {
  trackId: string;
  startTime: number;
  endTime: number;
}

export interface ReviewTimelineCommandTargetView {
  clipId: string;
  editable: boolean;
  canSplit: boolean;
  splitTime: number | null;
  gapBefore: ReviewTimelineGapView | null;
}

export type ReviewTimelineCommandIntent =
  | {
      operation: "move_clips";
      clipIds: string[];
      deltaTime: number;
    }
  | {
      operation: "duplicate_clips";
      clipIds: string[];
      timeOffset?: number;
    }
  | {
      operation: "delete_clips";
      clipIds: string[];
    }
  | {
      operation: "split_clip";
      clipId: string;
      splitTime: number;
    }
  | {
      operation: "duplicate_clip";
      clipId: string;
    }
  | {
      operation: "delete_clip";
      clipId: string;
    }
  | {
      operation: "close_gap";
      trackId: string;
      gapStart: number;
      gapEnd: number;
    };

export type ReviewTimelineClipboardIntent =
  | {
      operation: "copy";
      clipIds: string[];
    }
  | {
      operation: "cut";
      clipIds: string[];
    }
  | {
      operation: "paste";
      atTime: number;
    }
  | {
      operation: "restore_history";
      entryId: string;
    }
  | {
      operation: "clear_content";
    }
  | {
      operation: "clear_history";
    };

export type ReviewAISuggestionIntent =
  | {
      operation: "refresh_suggestions";
    }
  | {
      operation: "select_suggestion";
      suggestionId: string | null;
    }
  | {
      operation: "apply_suggestion";
      suggestionId: string;
    }
  | {
      operation: "dismiss_suggestion";
      suggestionId: string;
    }
  | {
      operation: "regenerate_suggestions";
    };

export interface ReviewAICommandSubmissionIntent {
  commandText: string;
  clientRequestId: string;
}

export interface ReviewAISuggestionItemView {
  id: string;
  title: string;
  description: string;
  kind: string;
  score: number | null;
  selected: boolean;
  actionable: boolean;
  stale: boolean;
  status: string;
}

export interface ReviewAISuggestionPanelView {
  available: boolean;
  suggestions: ReviewAISuggestionItemView[];
  selectedSuggestionId: string | null;
  count: number;
  actionableCount: number;
  staleCount: number;
  lifecycleRevision: number | null;
  timelineRevision: number | null;
  pending: boolean;
  pendingOperation: ReviewAISuggestionOperation | null;
}

export interface ReviewTimelineClipboardView {
  selectedClipIds: string[];
  pasteTime: number;
  available: boolean;
  itemCount: number;
  historyEntryCount: number;
  latestHistoryEntryId: string | null;
  canCopy: boolean;
  canCut: boolean;
  canPaste: boolean;
  canClear: boolean;
  canRestoreHistory: boolean;
  canClearHistory: boolean;
}

export interface ReviewEditorHeaderView {
  productionId: string;
  title: string;
  durationLabel: string;
  statusLabel: string;
  statusTone: ReviewBadgeTone;
  dirty: boolean;
  canUndo: boolean;
  canRedo: boolean;
}

export interface ReviewPreviewView {
  available: boolean;
  videoUrl: string | null;
  thumbnailUrl: string | null;
  currentTime: number;
  duration: number;
  currentTimeLabel: string;
  durationLabel: string;
  headline: string;
  eyebrow: string;
  subtitle: string | null;
}

export interface ReviewTimelineClipView {
  id: string;
  trackId: string;
  clipType: string;
  label: string;
  startTime: number;
  endTime: number;
  duration: number;
  start: number;
  width: number;
  tone: ReviewTimelineClipTone;
  selected: boolean;
  editable: boolean;
}

export interface ReviewTimelineTrackView {
  id: string;
  label: string;
  trackType: string;
  locked: boolean;
  muted: boolean;
  clips: ReviewTimelineClipView[];
}

export interface ReviewTimelineView {
  duration: number;
  fps: number;
  revision: number;
  playheadTime: number;
  durationLabel: string;
  trackCount: number;
  clipCount: number;
  playheadPercent: number;
  rulerMarks: string[];
  tracks: ReviewTimelineTrackView[];

  commandTarget:
    ReviewTimelineCommandTargetView | null;

  clipboard:
    ReviewTimelineClipboardView;
}

export interface ReviewTimelineClipDragGeometry {
  viewport: ReviewTimelineViewport;
  lanes: ReviewTimelineTrackLane[];
}

export interface ReviewTimelineClipDragStartIntent
  extends ReviewTimelineClipDragGeometry {
  clipId: string;
  pointer: ReviewTimelineDragPoint;
}

export interface ReviewTimelineClipDragMoveIntent
  extends ReviewTimelineClipDragGeometry {
  pointer: ReviewTimelineDragPoint;
}

export interface ReviewTimelineClipDragView {
  state: ReviewTimelineDragRuntimeState;
  active: boolean;
  dragging: boolean;
  committing: boolean;
  failed: boolean;
}

export interface ReviewTimelineClipTrimGeometry {
  viewport: ReviewTimelineViewport;
}

export interface ReviewTimelineClipTrimStartIntent
  extends ReviewTimelineClipTrimGeometry {
  clipId: string;
  handle: ReviewTimelineTrimHandle;
  pointer: ReviewTimelineDragPoint;
}

export interface ReviewTimelineClipTrimMoveIntent
  extends ReviewTimelineClipTrimGeometry {
  pointer: ReviewTimelineDragPoint;
}

export interface ReviewTimelineClipTrimView {
  state: ReviewTimelineTrimRuntimeState;
  active: boolean;
  trimming: boolean;
  committing: boolean;
  failed: boolean;
  cancelReason:
    ReviewTimelineTrimCancelReason | null;
}

export interface ReviewRuntimeKeyboardEditingView {
  enabled: boolean;
  state: ReviewTimelineKeyboardRuntimeState;
  lastOperation:
    ReviewTimelineKeyboardOperation | null;
}

export interface ReviewInspectorView {
  selectedClipId: string | null;
  selectedClipLabel: string | null;
  selectedClipRange: string | null;
  positionLabel: string;
  scaleLabel: string;
  rotationLabel: string;
  opacityLabel: string;
  subtitlePreset: string;
  aiScore: number | null;
  aiSuggestion: string | null;
  suggestionReview: ReviewAISuggestionPanelView;
}

export interface ReviewEditorViewModel {
  header: ReviewEditorHeaderView;
  preview: ReviewPreviewView;
  timeline: ReviewTimelineView;
  inspector: ReviewInspectorView;
}
