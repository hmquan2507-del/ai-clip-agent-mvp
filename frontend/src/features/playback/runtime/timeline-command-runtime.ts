import {
  TIMELINE_COMMAND_RUNTIME_VERSION,
  type TimelineCommandClip,
  type TimelineCommandDescriptor,
  type TimelineCommandDocument,
  type TimelineCommandHistoryEntry,
  type TimelineCommandKind,
  type TimelineCommandResult,
  type TimelineCommandRuntime,
  type TimelineCommandRuntimeSnapshot,
  type TimelineCommandTrack,
  type TimelineCommandValidation,
  type TimelineShortcut,
} from "../contracts/professional-timeline-command-contracts";

function cloneValue<T>(value: T): T {
  return structuredClone(value);
}

function normalizeDocument(document: TimelineCommandDocument): TimelineCommandDocument {
  return {
    version: Math.max(0, Math.floor(document.version)),
    clips: document.clips
      .map((clip) => ({ ...cloneValue(clip) }))
      .sort((a, b) => a.trackId.localeCompare(b.trackId) || a.startFrame - b.startFrame || a.id.localeCompare(b.id)),
    tracks: document.tracks.map((track) => ({ ...cloneValue(track) })),
    selection: [...new Set(document.selection)],
  };
}

function bump(
  document: TimelineCommandDocument,
  clips = document.clips,
  tracks = document.tracks,
  selection = document.selection,
): TimelineCommandDocument {
  return normalizeDocument({
    version: document.version + 1,
    clips,
    tracks,
    selection,
  });
}

function emptyDocument(): TimelineCommandDocument {
  return { version: 0, clips: [], tracks: [], selection: [] };
}

function clipDuration(clip: TimelineCommandClip): number {
  return clip.endFrame - clip.startFrame;
}

function selectedIds(command: TimelineCommandDescriptor, document: TimelineCommandDocument): string[] {
  return [...new Set(command.clipIds?.length ? command.clipIds : document.selection)];
}

function findClip(document: TimelineCommandDocument, id: string): TimelineCommandClip {
  const clip = document.clips.find((candidate) => candidate.id === id);
  if (!clip) {
    throw new Error(`Clip not found: ${id}`);
  }
  return clip;
}

function isClipEditable(document: TimelineCommandDocument, clip: TimelineCommandClip): boolean {
  const track = document.tracks.find((candidate) => candidate.id === clip.trackId);
  return !clip.locked && !track?.locked;
}

function uniqueId(prefix: string, existing: Set<string>): string {
  let index = 1;
  let candidate = `${prefix}-${index}`;
  while (existing.has(candidate)) {
    index += 1;
    candidate = `${prefix}-${index}`;
  }
  existing.add(candidate);
  return candidate;
}

function documentsEqual(a: TimelineCommandDocument, b: TimelineCommandDocument): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}

function commandKindFromShortcut(shortcut: TimelineShortcut): TimelineCommandKind | null {
  switch (shortcut) {
    case "Ctrl+K":
      return "split";
    case "Delete":
      return "delete";
    case "Shift+Delete":
      return "ripple-delete";
    case "Ctrl+D":
      return "duplicate";
    case "Ctrl+G":
      return "group";
    case "Ctrl+Shift+G":
      return "ungroup";
    default:
      return null;
  }
}

export function createTimelineCommandRuntime(
  initialDocument: TimelineCommandDocument = emptyDocument(),
): TimelineCommandRuntime {
  let document = normalizeDocument(initialDocument);
  let undoStack: TimelineCommandHistoryEntry[] = [];
  let redoStack: TimelineCommandHistoryEntry[] = [];
  let transaction:
    | {
        readonly label: string;
        readonly before: TimelineCommandDocument;
        readonly commands: TimelineCommandResult[];
      }
    | null = null;
  let disposed = false;
  let sequence = 0;

  const assertActive = (): void => {
    if (disposed) {
      throw new Error("Timeline command runtime is disposed.");
    }
  };

  const nextId = (prefix: string): string => {
    sequence += 1;
    return `${prefix}-${sequence}`;
  };

  const validate = (command: TimelineCommandDescriptor): TimelineCommandValidation => {
    if (disposed) {
      return { valid: false, reason: "runtime-disposed" };
    }

    const ids = selectedIds(command, document);
    const clipRequired = !["mute", "unmute", "hide", "show"].includes(command.kind) || !(command.trackIds?.length);

    if (clipRequired && ids.length === 0) {
      return { valid: false, reason: "no-clips-selected" };
    }

    for (const id of ids) {
      const clip = document.clips.find((candidate) => candidate.id === id);
      if (!clip) {
        return { valid: false, reason: `clip-not-found:${id}` };
      }
      if (!isClipEditable(document, clip) && !["unlock"].includes(command.kind)) {
        return { valid: false, reason: `clip-locked:${id}` };
      }
    }

    if (command.kind === "split") {
      const frame = command.frame;
      if (!Number.isFinite(frame)) {
        return { valid: false, reason: "split-frame-required" };
      }
      for (const id of ids) {
        const clip = findClip(document, id);
        if ((frame as number) <= clip.startFrame || (frame as number) >= clip.endFrame) {
          return { valid: false, reason: `split-frame-out-of-range:${id}` };
        }
      }
    }

    if (["move", "duplicate"].includes(command.kind) && !Number.isFinite(command.deltaFrames ?? 0)) {
      return { valid: false, reason: "invalid-delta" };
    }

    if (command.kind === "trim") {
      const startDelta = command.startDeltaFrames ?? 0;
      const endDelta = command.endDeltaFrames ?? 0;
      for (const id of ids) {
        const clip = findClip(document, id);
        if (clipDuration(clip) + endDelta - startDelta < 1) {
          return { valid: false, reason: `minimum-duration:${id}` };
        }
        if (clip.sourceStartFrame + startDelta < 0) {
          return { valid: false, reason: `source-underflow:${id}` };
        }
      }
    }

    return { valid: true };
  };

  const apply = (command: TimelineCommandDescriptor): TimelineCommandDocument => {
    const ids = selectedIds(command, document);
    const idSet = new Set(ids);
    let clips = document.clips.map((clip) => ({ ...clip }));
    let tracks = document.tracks.map((track) => ({ ...track }));
    let selection = [...document.selection];

    switch (command.kind) {
      case "split": {
        const existing = new Set(clips.map((clip) => clip.id));
        const frame = command.frame as number;
        const replacements: TimelineCommandClip[] = [];
        for (const clip of clips) {
          if (!idSet.has(clip.id)) {
            replacements.push(clip);
            continue;
          }
          const sourceSplit = clip.sourceStartFrame + (frame - clip.startFrame);
          const rightId = uniqueId(`${clip.id}-split`, existing);
          replacements.push(
            { ...clip, endFrame: frame, sourceEndFrame: sourceSplit },
            {
              ...clip,
              id: rightId,
              startFrame: frame,
              sourceStartFrame: sourceSplit,
            },
          );
          selection = [rightId];
        }
        clips = replacements;
        break;
      }

      case "delete":
      case "lift":
        clips = clips.filter((clip) => !idSet.has(clip.id));
        selection = selection.filter((id) => !idSet.has(id));
        break;

      case "ripple-delete":
      case "extract": {
        const removed = clips.filter((clip) => idSet.has(clip.id));
        clips = clips.filter((clip) => !idSet.has(clip.id));
        for (const target of removed) {
          const gap = clipDuration(target);
          clips = clips.map((clip) =>
            clip.trackId === target.trackId && clip.startFrame >= target.endFrame
              ? {
                  ...clip,
                  startFrame: clip.startFrame - gap,
                  endFrame: clip.endFrame - gap,
                }
              : clip,
          );
        }
        selection = selection.filter((id) => !idSet.has(id));
        break;
      }

      case "duplicate": {
        const existing = new Set(clips.map((clip) => clip.id));
        const delta = command.deltaFrames ?? 1;
        const duplicates = clips
          .filter((clip) => idSet.has(clip.id))
          .map((clip) => ({
            ...clip,
            id: uniqueId(`${clip.id}-copy`, existing),
            startFrame: clip.startFrame + delta,
            endFrame: clip.endFrame + delta,
          }));
        clips = [...clips, ...duplicates];
        selection = duplicates.map((clip) => clip.id);
        break;
      }

      case "move": {
        const delta = command.deltaFrames ?? 0;
        clips = clips.map((clip) =>
          idSet.has(clip.id)
            ? {
                ...clip,
                startFrame: Math.max(0, clip.startFrame + delta),
                endFrame: Math.max(clipDuration(clip), clip.endFrame + delta),
              }
            : clip,
        );
        break;
      }

      case "trim": {
        const startDelta = command.startDeltaFrames ?? 0;
        const endDelta = command.endDeltaFrames ?? 0;
        clips = clips.map((clip) =>
          idSet.has(clip.id)
            ? {
                ...clip,
                startFrame: clip.startFrame + startDelta,
                endFrame: clip.endFrame + endDelta,
                sourceStartFrame: clip.sourceStartFrame + startDelta,
                sourceEndFrame: clip.sourceEndFrame + endDelta,
              }
            : clip,
        );
        break;
      }

      case "group": {
        const groupId = command.groupId ?? nextId("group");
        clips = clips.map((clip) => (idSet.has(clip.id) ? { ...clip, groupId } : clip));
        break;
      }

      case "ungroup":
        clips = clips.map((clip) => (idSet.has(clip.id) ? { ...clip, groupId: null } : clip));
        break;

      case "lock":
        clips = clips.map((clip) => (idSet.has(clip.id) ? { ...clip, locked: true } : clip));
        break;

      case "unlock":
        clips = clips.map((clip) => (idSet.has(clip.id) ? { ...clip, locked: false } : clip));
        break;

      case "mute":
      case "unmute":
      case "hide":
      case "show": {
        const flag = command.kind === "mute" || command.kind === "hide";
        const field = command.kind === "mute" || command.kind === "unmute" ? "muted" : "hidden";
        const trackIds = new Set(command.trackIds ?? []);
        clips = clips.map((clip) =>
          idSet.has(clip.id) ? { ...clip, [field]: flag } : clip,
        );
        tracks = tracks.map((track) =>
          trackIds.has(track.id) ? { ...track, [field]: flag } : track,
        );
        break;
      }
    }

    return bump(document, clips, tracks, selection);
  };

  const execute = (command: TimelineCommandDescriptor): TimelineCommandResult => {
    assertActive();
    const validation = validate(command);
    if (!validation.valid) {
      throw new Error(`Command rejected: ${validation.reason ?? "invalid"}`);
    }

    const before = cloneValue(document);
    const candidate = apply(command);
    const changed = !documentsEqual(before, candidate);
    document = candidate;

    const result: TimelineCommandResult = {
      commandId: command.id,
      kind: command.kind,
      before,
      after: cloneValue(document),
      changed,
    };

    if (changed) {
      if (transaction) {
        transaction.commands.push(result);
      } else {
        undoStack.push({
          id: nextId("history"),
          label: command.kind,
          commands: [result],
          before,
          after: cloneValue(document),
        });
        redoStack = [];
      }
    }

    return cloneValue(result);
  };

  const getSnapshot = (): TimelineCommandRuntimeSnapshot => ({
    version: TIMELINE_COMMAND_RUNTIME_VERSION,
    document: cloneValue(document),
    canUndo: undoStack.length > 0,
    canRedo: redoStack.length > 0,
    undoDepth: undoStack.length,
    redoDepth: redoStack.length,
    transactionActive: transaction !== null,
    disposed,
  });

  const undo = (): TimelineCommandHistoryEntry | null => {
    assertActive();
    if (transaction) {
      throw new Error("Cannot undo during an active transaction.");
    }
    const entry = undoStack.pop();
    if (!entry) {
      return null;
    }
    document = cloneValue(entry.before);
    redoStack.push(entry);
    return cloneValue(entry);
  };

  const redo = (): TimelineCommandHistoryEntry | null => {
    assertActive();
    if (transaction) {
      throw new Error("Cannot redo during an active transaction.");
    }
    const entry = redoStack.pop();
    if (!entry) {
      return null;
    }
    document = cloneValue(entry.after);
    undoStack.push(entry);
    return cloneValue(entry);
  };

  const beginTransaction = (label: string): void => {
    assertActive();
    if (transaction) {
      throw new Error("Nested transactions are not supported.");
    }
    transaction = { label, before: cloneValue(document), commands: [] };
  };

  const commitTransaction = (): TimelineCommandHistoryEntry | null => {
    assertActive();
    if (!transaction) {
      return null;
    }
    const current = transaction;
    transaction = null;
    if (current.commands.length === 0 || documentsEqual(current.before, document)) {
      return null;
    }
    const entry: TimelineCommandHistoryEntry = {
      id: nextId("transaction"),
      label: current.label,
      commands: cloneValue(current.commands),
      before: cloneValue(current.before),
      after: cloneValue(document),
    };
    undoStack.push(entry);
    redoStack = [];
    return cloneValue(entry);
  };

  const rollbackTransaction = (): void => {
    assertActive();
    if (!transaction) {
      return;
    }
    document = cloneValue(transaction.before);
    transaction = null;
  };

  const dispatchShortcut = (
    shortcut: TimelineShortcut,
    payload: Omit<TimelineCommandDescriptor, "id" | "kind"> = {},
  ): TimelineCommandResult | TimelineCommandHistoryEntry | null => {
    assertActive();
    if (shortcut === "Ctrl+Z") {
      return undo();
    }
    if (shortcut === "Ctrl+Shift+Z" || shortcut === "Ctrl+Y") {
      return redo();
    }
    const kind = commandKindFromShortcut(shortcut);
    if (!kind) {
      return null;
    }
    return execute({
      ...payload,
      id: nextId("shortcut-command"),
      kind,
    });
  };

  const reset = (nextDocument: TimelineCommandDocument = emptyDocument()): void => {
    assertActive();
    document = normalizeDocument(nextDocument);
    undoStack = [];
    redoStack = [];
    transaction = null;
  };

  const dispose = (): void => {
    disposed = true;
    undoStack = [];
    redoStack = [];
    transaction = null;
  };

  return {
    getSnapshot,
    validate,
    execute,
    undo,
    redo,
    beginTransaction,
    commitTransaction,
    rollbackTransaction,
    dispatchShortcut,
    reset,
    dispose,
  };
}
