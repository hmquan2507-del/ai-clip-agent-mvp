export const TIMELINE_COMMAND_RUNTIME_VERSION = "16.9.6" as const;

export type TimelineCommandKind =
  | "split"
  | "delete"
  | "ripple-delete"
  | "duplicate"
  | "move"
  | "trim"
  | "lift"
  | "extract"
  | "group"
  | "ungroup"
  | "lock"
  | "unlock"
  | "mute"
  | "unmute"
  | "hide"
  | "show";

export type TimelineShortcut =
  | "Ctrl+K"
  | "Delete"
  | "Shift+Delete"
  | "Ctrl+D"
  | "Ctrl+G"
  | "Ctrl+Shift+G"
  | "Ctrl+Z"
  | "Ctrl+Shift+Z"
  | "Ctrl+Y";

export interface TimelineCommandClip {
  readonly id: string;
  readonly trackId: string;
  readonly startFrame: number;
  readonly endFrame: number;
  readonly sourceStartFrame: number;
  readonly sourceEndFrame: number;
  readonly locked?: boolean;
  readonly groupId?: string | null;
  readonly muted?: boolean;
  readonly hidden?: boolean;
  readonly metadata?: Readonly<Record<string, unknown>>;
}

export interface TimelineCommandTrack {
  readonly id: string;
  readonly locked?: boolean;
  readonly muted?: boolean;
  readonly hidden?: boolean;
}

export interface TimelineCommandDocument {
  readonly version: number;
  readonly clips: readonly TimelineCommandClip[];
  readonly tracks: readonly TimelineCommandTrack[];
  readonly selection: readonly string[];
}

export interface TimelineCommandContext {
  readonly document: TimelineCommandDocument;
  readonly playheadFrame: number;
}

export interface TimelineCommandDescriptor {
  readonly id: string;
  readonly kind: TimelineCommandKind;
  readonly clipIds?: readonly string[];
  readonly trackIds?: readonly string[];
  readonly frame?: number;
  readonly deltaFrames?: number;
  readonly startDeltaFrames?: number;
  readonly endDeltaFrames?: number;
  readonly groupId?: string;
}

export interface TimelineCommandValidation {
  readonly valid: boolean;
  readonly reason?: string;
}

export interface TimelineCommandResult {
  readonly commandId: string;
  readonly kind: TimelineCommandKind;
  readonly before: TimelineCommandDocument;
  readonly after: TimelineCommandDocument;
  readonly changed: boolean;
}

export interface TimelineCommandHistoryEntry {
  readonly id: string;
  readonly label: string;
  readonly commands: readonly TimelineCommandResult[];
  readonly before: TimelineCommandDocument;
  readonly after: TimelineCommandDocument;
}

export interface TimelineCommandRuntimeSnapshot {
  readonly version: typeof TIMELINE_COMMAND_RUNTIME_VERSION;
  readonly document: TimelineCommandDocument;
  readonly canUndo: boolean;
  readonly canRedo: boolean;
  readonly undoDepth: number;
  readonly redoDepth: number;
  readonly transactionActive: boolean;
  readonly disposed: boolean;
}

export interface TimelineCommandRuntime {
  getSnapshot(): TimelineCommandRuntimeSnapshot;
  validate(command: TimelineCommandDescriptor): TimelineCommandValidation;
  execute(command: TimelineCommandDescriptor): TimelineCommandResult;
  undo(): TimelineCommandHistoryEntry | null;
  redo(): TimelineCommandHistoryEntry | null;
  beginTransaction(label: string): void;
  commitTransaction(): TimelineCommandHistoryEntry | null;
  rollbackTransaction(): void;
  dispatchShortcut(
    shortcut: TimelineShortcut,
    command?: Omit<TimelineCommandDescriptor, "id" | "kind">,
  ): TimelineCommandResult | TimelineCommandHistoryEntry | null;
  reset(document?: TimelineCommandDocument): void;
  dispose(): void;
}
