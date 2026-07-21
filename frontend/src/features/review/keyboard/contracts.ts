export const REVIEW_TIMELINE_KEYBOARD_CONTRACT_VERSION =
  "16.7.4" as const;

export type ReviewTimelineKeyboardPlatform =
  | "windows"
  | "macos"
  | "linux";

export type ReviewTimelineKeyboardOperation =
  | "undo"
  | "redo"
  | "split_clip"
  | "duplicate_clip"
  | "delete_clip"
  | "copy"
  | "cut"
  | "paste";

export type ReviewTimelineKeyboardBlockedReason =
  | "workspace_inactive"
  | "workspace_busy"
  | "editable_target"
  | "unsupported_shortcut"
  | "command_unavailable"
  | "key_repeat"
  | "shortcut_already_active";

export interface ReviewTimelineKeyboardTarget {
  tagName?: string | null;
  role?: string | null;
  contentEditable?: boolean;
}

export interface ReviewTimelineKeyboardInput {
  key: string;
  code?: string | null;
  ctrlKey?: boolean;
  metaKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  repeat?: boolean;
  target?: ReviewTimelineKeyboardTarget | null;
}

export interface ReviewTimelineKeyboardContext {
  productionId: string;
  timelineRevision: number;
  platform: ReviewTimelineKeyboardPlatform;
  workspaceActive: boolean;
  busy: boolean;
  selectedClipIds: string[];
  editableClipIds: string[];
  activeClipId: string | null;
  cursorTime: number;
  activeClipStartTime: number | null;
  activeClipEndTime: number | null;
  canUndo: boolean;
  canRedo: boolean;
  canPaste: boolean;
}

export type ReviewTimelineKeyboardCommandIntent =
  | {
      operation: "undo";
    }
  | {
      operation: "redo";
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
    };

export interface ReviewTimelineKeyboardShortcut {
  operation: ReviewTimelineKeyboardOperation;
  chord: string;
  triggerKey: string;
}

export interface ReviewTimelineKeyboardResult {
  contractVersion:
    typeof REVIEW_TIMELINE_KEYBOARD_CONTRACT_VERSION;
  handled: boolean;
  preventDefault: boolean;
  operation: ReviewTimelineKeyboardOperation | null;
  intent: ReviewTimelineKeyboardCommandIntent | null;
  blockedReason:
    ReviewTimelineKeyboardBlockedReason | null;
  chord: string | null;
}

export interface ReviewTimelineKeyboardRuntimeState {
  contractVersion:
    typeof REVIEW_TIMELINE_KEYBOARD_CONTRACT_VERSION;
  activeShortcut:
    ReviewTimelineKeyboardShortcut | null;
  lastIntent:
    ReviewTimelineKeyboardCommandIntent | null;
  lastResult:
    ReviewTimelineKeyboardResult | null;
  handledCount: number;
  stateRevision: number;
  updatedAt: string | null;
}

export type ReviewTimelineKeyboardRuntimeListener = (
  state: ReviewTimelineKeyboardRuntimeState,
  previousState: ReviewTimelineKeyboardRuntimeState,
) => void;
