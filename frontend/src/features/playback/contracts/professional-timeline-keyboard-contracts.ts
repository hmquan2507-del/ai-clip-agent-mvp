import type {
  TimelineCommandDescriptor,
  TimelineCommandHistoryEntry,
  TimelineCommandResult,
  TimelineCommandRuntime,
} from "./professional-timeline-command-contracts";

export const TIMELINE_KEYBOARD_RUNTIME_VERSION = "16.9.7" as const;

export type TimelineKeyboardProfileId =
  | "default"
  | "capcut"
  | "premiere"
  | "custom";

export type TimelineKeyboardContext =
  | "global"
  | "timeline"
  | "preview"
  | "text-input"
  | "modal"
  | "command-palette";

export type TimelineKeyboardCommandId =
  | "timeline.split"
  | "timeline.delete"
  | "timeline.ripple-delete"
  | "timeline.duplicate"
  | "timeline.group"
  | "timeline.ungroup"
  | "history.undo"
  | "history.redo"
  | "playback.toggle"
  | "playback.stop"
  | "playback.step-backward"
  | "playback.step-forward"
  | "selection.clear"
  | "command-palette.open";

export interface TimelineKeyboardStroke {
  readonly key: string;
  readonly ctrl?: boolean;
  readonly shift?: boolean;
  readonly alt?: boolean;
  readonly meta?: boolean;
}

export interface TimelineKeyboardBinding {
  readonly id: string;
  readonly commandId: TimelineKeyboardCommandId;
  readonly sequence: readonly TimelineKeyboardStroke[];
  readonly contexts: readonly TimelineKeyboardContext[];
  readonly preventDefault?: boolean;
  readonly enabled?: boolean;
  readonly profileId?: TimelineKeyboardProfileId;
  readonly description?: string;
}

export interface TimelineKeyboardEvent {
  readonly key: string;
  readonly ctrlKey?: boolean;
  readonly shiftKey?: boolean;
  readonly altKey?: boolean;
  readonly metaKey?: boolean;
  readonly repeat?: boolean;
  readonly timestamp?: number;
}

export interface TimelineKeyboardFocusState {
  readonly context: TimelineKeyboardContext;
  readonly targetId?: string | null;
  readonly editable?: boolean;
}

export interface TimelineKeyboardConflict {
  readonly signature: string;
  readonly context: TimelineKeyboardContext;
  readonly bindingIds: readonly string[];
  readonly commandIds: readonly TimelineKeyboardCommandId[];
}

export interface TimelineKeyboardDispatchPayload {
  readonly command?: Omit<TimelineCommandDescriptor, "id" | "kind">;
  readonly playheadFrame?: number;
}

export interface TimelineKeyboardDispatchResult {
  readonly handled: boolean;
  readonly pendingChord: boolean;
  readonly bindingId?: string;
  readonly commandId?: TimelineKeyboardCommandId;
  readonly preventDefault: boolean;
  readonly result?:
    | TimelineCommandResult
    | TimelineCommandHistoryEntry
    | null;
}

export interface TimelineKeyboardPaletteItem {
  readonly commandId: TimelineKeyboardCommandId;
  readonly label: string;
  readonly description: string;
  readonly shortcuts: readonly string[];
}

export interface TimelineKeyboardRuntimeSnapshot {
  readonly version: typeof TIMELINE_KEYBOARD_RUNTIME_VERSION;
  readonly profileId: TimelineKeyboardProfileId;
  readonly focus: TimelineKeyboardFocusState;
  readonly bindings: readonly TimelineKeyboardBinding[];
  readonly conflicts: readonly TimelineKeyboardConflict[];
  readonly pendingSequence: readonly TimelineKeyboardStroke[];
  readonly paletteOpen: boolean;
  readonly disposed: boolean;
}

export interface TimelineKeyboardRuntimeOptions {
  readonly commandRuntime: TimelineCommandRuntime;
  readonly profileId?: TimelineKeyboardProfileId;
  readonly chordTimeoutMs?: number;
  readonly bindings?: readonly TimelineKeyboardBinding[];
  readonly onPlaybackCommand?: (
    commandId: TimelineKeyboardCommandId,
  ) => unknown;
  readonly onSelectionCommand?: (
    commandId: TimelineKeyboardCommandId,
  ) => unknown;
}

export interface TimelineKeyboardRuntime {
  getSnapshot(): TimelineKeyboardRuntimeSnapshot;
  dispatch(
    event: TimelineKeyboardEvent,
    payload?: TimelineKeyboardDispatchPayload,
  ): TimelineKeyboardDispatchResult;
  dispatchCommand(
    commandId: TimelineKeyboardCommandId,
    payload?: TimelineKeyboardDispatchPayload,
  ): TimelineKeyboardDispatchResult;
  setFocus(focus: TimelineKeyboardFocusState): void;
  setProfile(profileId: TimelineKeyboardProfileId): void;
  registerBinding(binding: TimelineKeyboardBinding): void;
  updateBinding(
    bindingId: string,
    patch: Partial<Omit<TimelineKeyboardBinding, "id">>,
  ): void;
  removeBinding(bindingId: string): void;
  resetBindings(profileId?: TimelineKeyboardProfileId): void;
  detectConflicts(): readonly TimelineKeyboardConflict[];
  getCommandPalette(query?: string): readonly TimelineKeyboardPaletteItem[];
  closeCommandPalette(): void;
  clearPendingChord(): void;
  reset(): void;
  dispose(): void;
}
