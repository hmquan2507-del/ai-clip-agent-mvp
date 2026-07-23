import {
  TIMELINE_KEYBOARD_RUNTIME_VERSION,
  type TimelineKeyboardBinding,
  type TimelineKeyboardCommandId,
  type TimelineKeyboardConflict,
  type TimelineKeyboardContext,
  type TimelineKeyboardDispatchPayload,
  type TimelineKeyboardDispatchResult,
  type TimelineKeyboardEvent,
  type TimelineKeyboardFocusState,
  type TimelineKeyboardPaletteItem,
  type TimelineKeyboardProfileId,
  type TimelineKeyboardRuntime,
  type TimelineKeyboardRuntimeOptions,
  type TimelineKeyboardRuntimeSnapshot,
  type TimelineKeyboardStroke,
} from "../contracts/professional-timeline-keyboard-contracts";

function cloneValue<T>(value: T): T {
  return structuredClone(value);
}

function normalizeKey(key: string): string {
  if (key === " ") return "Space";
  if (key === "Esc") return "Escape";
  if (key.length === 1) return key.toUpperCase();
  return key;
}

function normalizeStroke(
  stroke: TimelineKeyboardStroke,
): TimelineKeyboardStroke {
  return {
    key: normalizeKey(stroke.key),
    ctrl: Boolean(stroke.ctrl),
    shift: Boolean(stroke.shift),
    alt: Boolean(stroke.alt),
    meta: Boolean(stroke.meta),
  };
}

function strokeFromEvent(
  event: TimelineKeyboardEvent,
): TimelineKeyboardStroke {
  return normalizeStroke({
    key: event.key,
    ctrl: event.ctrlKey,
    shift: event.shiftKey,
    alt: event.altKey,
    meta: event.metaKey,
  });
}

function strokesEqual(
  left: TimelineKeyboardStroke,
  right: TimelineKeyboardStroke,
): boolean {
  const a = normalizeStroke(left);
  const b = normalizeStroke(right);
  return (
    a.key === b.key &&
    a.ctrl === b.ctrl &&
    a.shift === b.shift &&
    a.alt === b.alt &&
    a.meta === b.meta
  );
}

function sequenceStartsWith(
  sequence: readonly TimelineKeyboardStroke[],
  prefix: readonly TimelineKeyboardStroke[],
): boolean {
  return prefix.every((stroke, index) =>
    sequence[index] ? strokesEqual(sequence[index], stroke) : false,
  );
}

function sequenceEqual(
  left: readonly TimelineKeyboardStroke[],
  right: readonly TimelineKeyboardStroke[],
): boolean {
  return (
    left.length === right.length &&
    left.every((stroke, index) => strokesEqual(stroke, right[index]))
  );
}

function strokeLabel(stroke: TimelineKeyboardStroke): string {
  const normalized = normalizeStroke(stroke);
  return [
    normalized.ctrl ? "Ctrl" : "",
    normalized.meta ? "Meta" : "",
    normalized.alt ? "Alt" : "",
    normalized.shift ? "Shift" : "",
    normalized.key,
  ]
    .filter(Boolean)
    .join("+");
}

function sequenceLabel(
  sequence: readonly TimelineKeyboardStroke[],
): string {
  return sequence.map(strokeLabel).join(" ");
}

function signatureFor(
  sequence: readonly TimelineKeyboardStroke[],
  context: TimelineKeyboardContext,
): string {
  return `${context}:${sequenceLabel(sequence)}`;
}

function binding(
  id: string,
  commandId: TimelineKeyboardCommandId,
  sequence: readonly TimelineKeyboardStroke[],
  contexts: readonly TimelineKeyboardContext[],
  description: string,
  profileId: TimelineKeyboardProfileId = "default",
): TimelineKeyboardBinding {
  return {
    id,
    commandId,
    sequence: sequence.map(normalizeStroke),
    contexts,
    description,
    preventDefault: true,
    enabled: true,
    profileId,
  };
}

function defaultBindings(
  profileId: TimelineKeyboardProfileId,
): TimelineKeyboardBinding[] {
  const common: TimelineKeyboardBinding[] = [
    binding(
      `${profileId}-split`,
      "timeline.split",
      [{ key: "K", ctrl: true }],
      ["timeline"],
      "Split selected clip at the playhead",
      profileId,
    ),
    binding(
      `${profileId}-delete`,
      "timeline.delete",
      [{ key: "Delete" }],
      ["timeline"],
      "Delete selected clips",
      profileId,
    ),
    binding(
      `${profileId}-ripple-delete`,
      "timeline.ripple-delete",
      [{ key: "Delete", shift: true }],
      ["timeline"],
      "Ripple delete selected clips",
      profileId,
    ),
    binding(
      `${profileId}-duplicate`,
      "timeline.duplicate",
      [{ key: "D", ctrl: true }],
      ["timeline"],
      "Duplicate selected clips",
      profileId,
    ),
    binding(
      `${profileId}-group`,
      "timeline.group",
      [{ key: "G", ctrl: true }],
      ["timeline"],
      "Group selected clips",
      profileId,
    ),
    binding(
      `${profileId}-ungroup`,
      "timeline.ungroup",
      [{ key: "G", ctrl: true, shift: true }],
      ["timeline"],
      "Ungroup selected clips",
      profileId,
    ),
    binding(
      `${profileId}-undo`,
      "history.undo",
      [{ key: "Z", ctrl: true }],
      ["global", "timeline", "preview"],
      "Undo the latest timeline command",
      profileId,
    ),
    binding(
      `${profileId}-redo`,
      "history.redo",
      [{ key: "Z", ctrl: true, shift: true }],
      ["global", "timeline", "preview"],
      "Redo the latest timeline command",
      profileId,
    ),
    binding(
      `${profileId}-playback-toggle`,
      "playback.toggle",
      [{ key: "Space" }],
      ["timeline", "preview"],
      "Toggle playback",
      profileId,
    ),
    binding(
      `${profileId}-playback-stop`,
      "playback.stop",
      [{ key: "K" }],
      ["preview"],
      "Stop playback",
      profileId,
    ),
    binding(
      `${profileId}-step-backward`,
      "playback.step-backward",
      [{ key: "ArrowLeft" }],
      ["timeline", "preview"],
      "Step one frame backward",
      profileId,
    ),
    binding(
      `${profileId}-step-forward`,
      "playback.step-forward",
      [{ key: "ArrowRight" }],
      ["timeline", "preview"],
      "Step one frame forward",
      profileId,
    ),
    binding(
      `${profileId}-selection-clear`,
      "selection.clear",
      [{ key: "Escape" }],
      ["timeline"],
      "Clear the current selection",
      profileId,
    ),
    binding(
      `${profileId}-palette`,
      "command-palette.open",
      [{ key: "P", ctrl: true, shift: true }],
      ["global", "timeline", "preview"],
      "Open the command palette",
      profileId,
    ),
    binding(
      `${profileId}-chord-ripple-delete`,
      "timeline.ripple-delete",
      [{ key: "K", ctrl: true, alt: true }, { key: "R" }],
      ["timeline"],
      "Ripple delete through a keyboard chord",
      profileId,
    ),
  ];

  if (profileId === "premiere") {
    return common.map((item) =>
      item.commandId === "timeline.split"
        ? {
            ...item,
            sequence: [normalizeStroke({ key: "K", ctrl: true })],
          }
        : item,
    );
  }

  if (profileId === "capcut") {
    return common.map((item) =>
      item.commandId === "timeline.split"
        ? {
            ...item,
            sequence: [normalizeStroke({ key: "B", ctrl: true })],
          }
        : item,
    );
  }

  return common;
}

const PALETTE_LABELS: Readonly<
  Record<
    TimelineKeyboardCommandId,
    { readonly label: string; readonly description: string }
  >
> = {
  "timeline.split": {
    label: "Split clip",
    description: "Split selected clips at the current playhead.",
  },
  "timeline.delete": {
    label: "Delete clips",
    description: "Remove selected clips and keep the gap.",
  },
  "timeline.ripple-delete": {
    label: "Ripple delete",
    description: "Remove selected clips and close the gap.",
  },
  "timeline.duplicate": {
    label: "Duplicate clips",
    description: "Create timeline copies of selected clips.",
  },
  "timeline.group": {
    label: "Group clips",
    description: "Group selected clips.",
  },
  "timeline.ungroup": {
    label: "Ungroup clips",
    description: "Remove selected clips from their group.",
  },
  "history.undo": {
    label: "Undo",
    description: "Undo the latest timeline command.",
  },
  "history.redo": {
    label: "Redo",
    description: "Redo the latest undone command.",
  },
  "playback.toggle": {
    label: "Play or pause",
    description: "Toggle timeline playback.",
  },
  "playback.stop": {
    label: "Stop playback",
    description: "Stop timeline playback.",
  },
  "playback.step-backward": {
    label: "Previous frame",
    description: "Step one frame backward.",
  },
  "playback.step-forward": {
    label: "Next frame",
    description: "Step one frame forward.",
  },
  "selection.clear": {
    label: "Clear selection",
    description: "Clear selected timeline items.",
  },
  "command-palette.open": {
    label: "Open command palette",
    description: "Search all available keyboard commands.",
  },
};

export function createTimelineKeyboardRuntime(
  options: TimelineKeyboardRuntimeOptions,
): TimelineKeyboardRuntime {
  const chordTimeoutMs = Math.max(100, options.chordTimeoutMs ?? 900);
  let profileId: TimelineKeyboardProfileId =
    options.profileId ?? "default";
  let bindings = [
    ...defaultBindings(profileId),
    ...(options.bindings ?? []).map((item) => cloneValue(item)),
  ];
  let focus: TimelineKeyboardFocusState = {
    context: "timeline",
    targetId: null,
    editable: false,
  };
  let pendingSequence: TimelineKeyboardStroke[] = [];
  let pendingSince = 0;
  let paletteOpen = false;
  let disposed = false;

  const assertActive = (): void => {
    if (disposed) {
      throw new Error("Timeline keyboard runtime is disposed.");
    }
  };

  const activeBindings = (): TimelineKeyboardBinding[] =>
    bindings.filter(
      (item) =>
        item.enabled !== false &&
        item.contexts.includes(focus.context),
    );

  const detectConflicts = (): readonly TimelineKeyboardConflict[] => {
    const groups = new Map<
      string,
      {
        context: TimelineKeyboardContext;
        bindingIds: string[];
        commandIds: TimelineKeyboardCommandId[];
      }
    >();

    for (const item of bindings.filter((candidate) => candidate.enabled !== false)) {
      for (const context of item.contexts) {
        const signature = signatureFor(item.sequence, context);
        const group = groups.get(signature) ?? {
          context,
          bindingIds: [],
          commandIds: [],
        };
        group.bindingIds.push(item.id);
        group.commandIds.push(item.commandId);
        groups.set(signature, group);
      }
    }

    return [...groups.entries()]
      .filter(([, group]) => new Set(group.commandIds).size > 1)
      .map(([signature, group]) => ({
        signature,
        context: group.context,
        bindingIds: [...group.bindingIds],
        commandIds: [...group.commandIds],
      }))
      .sort((a, b) => a.signature.localeCompare(b.signature));
  };

  const getSnapshot = (): TimelineKeyboardRuntimeSnapshot => ({
    version: TIMELINE_KEYBOARD_RUNTIME_VERSION,
    profileId,
    focus: cloneValue(focus),
    bindings: cloneValue(bindings),
    conflicts: cloneValue(detectConflicts()),
    pendingSequence: cloneValue(pendingSequence),
    paletteOpen,
    disposed,
  });

  const executeCommand = (
    commandId: TimelineKeyboardCommandId,
    payload: TimelineKeyboardDispatchPayload = {},
  ): TimelineKeyboardDispatchResult => {
    assertActive();

    switch (commandId) {
      case "history.undo":
        return {
          handled: true,
          pendingChord: false,
          commandId,
          preventDefault: true,
          result: options.commandRuntime.undo(),
        };

      case "history.redo":
        return {
          handled: true,
          pendingChord: false,
          commandId,
          preventDefault: true,
          result: options.commandRuntime.redo(),
        };

      case "timeline.split":
        return {
          handled: true,
          pendingChord: false,
          commandId,
          preventDefault: true,
          result: options.commandRuntime.execute({
            id: `keyboard-split-${Date.now()}`,
            kind: "split",
            ...payload.command,
            frame:
              payload.command?.frame ??
              payload.playheadFrame ??
              0,
          }),
        };

      case "timeline.delete":
        return {
          handled: true,
          pendingChord: false,
          commandId,
          preventDefault: true,
          result: options.commandRuntime.execute({
            id: `keyboard-delete-${Date.now()}`,
            kind: "delete",
            ...payload.command,
          }),
        };

      case "timeline.ripple-delete":
        return {
          handled: true,
          pendingChord: false,
          commandId,
          preventDefault: true,
          result: options.commandRuntime.execute({
            id: `keyboard-ripple-delete-${Date.now()}`,
            kind: "ripple-delete",
            ...payload.command,
          }),
        };

      case "timeline.duplicate":
        return {
          handled: true,
          pendingChord: false,
          commandId,
          preventDefault: true,
          result: options.commandRuntime.execute({
            id: `keyboard-duplicate-${Date.now()}`,
            kind: "duplicate",
            deltaFrames: 1,
            ...payload.command,
          }),
        };

      case "timeline.group":
        return {
          handled: true,
          pendingChord: false,
          commandId,
          preventDefault: true,
          result: options.commandRuntime.execute({
            id: `keyboard-group-${Date.now()}`,
            kind: "group",
            ...payload.command,
          }),
        };

      case "timeline.ungroup":
        return {
          handled: true,
          pendingChord: false,
          commandId,
          preventDefault: true,
          result: options.commandRuntime.execute({
            id: `keyboard-ungroup-${Date.now()}`,
            kind: "ungroup",
            ...payload.command,
          }),
        };

      case "command-palette.open":
        paletteOpen = true;
        return {
          handled: true,
          pendingChord: false,
          commandId,
          preventDefault: true,
          result: null,
        };

      case "selection.clear":
        options.onSelectionCommand?.(commandId);
        return {
          handled: true,
          pendingChord: false,
          commandId,
          preventDefault: true,
          result: null,
        };

      default:
        options.onPlaybackCommand?.(commandId);
        return {
          handled: true,
          pendingChord: false,
          commandId,
          preventDefault: true,
          result: null,
        };
    }
  };

  const dispatchCommand = (
    commandId: TimelineKeyboardCommandId,
    payload: TimelineKeyboardDispatchPayload = {},
  ): TimelineKeyboardDispatchResult => executeCommand(commandId, payload);

  const clearPendingChord = (): void => {
    pendingSequence = [];
    pendingSince = 0;
  };

  const dispatch = (
    event: TimelineKeyboardEvent,
    payload: TimelineKeyboardDispatchPayload = {},
  ): TimelineKeyboardDispatchResult => {
    assertActive();

    if (event.repeat) {
      return {
        handled: false,
        pendingChord: pendingSequence.length > 0,
        preventDefault: false,
      };
    }

    if (
      focus.context === "text-input" ||
      focus.context === "modal"
    ) {
      clearPendingChord();
      return {
        handled: false,
        pendingChord: false,
        preventDefault: false,
      };
    }

    const now = event.timestamp ?? Date.now();
    if (pendingSequence.length > 0 && now - pendingSince > chordTimeoutMs) {
      clearPendingChord();
    }

    const candidateSequence = [...pendingSequence, strokeFromEvent(event)];
    const candidates = activeBindings().filter((item) =>
      sequenceStartsWith(item.sequence, candidateSequence),
    );
    const exact = candidates.find((item) =>
      sequenceEqual(item.sequence, candidateSequence),
    );

    if (exact) {
      clearPendingChord();
      const result = executeCommand(exact.commandId, payload);
      return {
        ...result,
        bindingId: exact.id,
        preventDefault: exact.preventDefault !== false,
      };
    }

    if (candidates.length > 0) {
      pendingSequence = candidateSequence;
      pendingSince = now;
      return {
        handled: true,
        pendingChord: true,
        preventDefault: true,
      };
    }

    clearPendingChord();

    const singleStroke = [strokeFromEvent(event)];
    const single = activeBindings().find((item) =>
      sequenceEqual(item.sequence, singleStroke),
    );

    if (!single) {
      return {
        handled: false,
        pendingChord: false,
        preventDefault: false,
      };
    }

    const result = executeCommand(single.commandId, payload);
    return {
      ...result,
      bindingId: single.id,
      preventDefault: single.preventDefault !== false,
    };
  };

  const setFocus = (nextFocus: TimelineKeyboardFocusState): void => {
    assertActive();
    focus = cloneValue(nextFocus);
    clearPendingChord();
  };

  const setProfile = (nextProfileId: TimelineKeyboardProfileId): void => {
    assertActive();
    profileId = nextProfileId;
    bindings = defaultBindings(profileId);
    clearPendingChord();
  };

  const registerBinding = (nextBinding: TimelineKeyboardBinding): void => {
    assertActive();
    if (bindings.some((item) => item.id === nextBinding.id)) {
      throw new Error(`Keyboard binding already exists: ${nextBinding.id}`);
    }
    if (nextBinding.sequence.length === 0) {
      throw new Error("Keyboard binding sequence cannot be empty.");
    }
    bindings.push({
      ...cloneValue(nextBinding),
      sequence: nextBinding.sequence.map(normalizeStroke),
    });
  };

  const updateBinding = (
    bindingId: string,
    patch: Partial<Omit<TimelineKeyboardBinding, "id">>,
  ): void => {
    assertActive();
    const index = bindings.findIndex((item) => item.id === bindingId);
    if (index < 0) {
      throw new Error(`Keyboard binding not found: ${bindingId}`);
    }
    const updated = {
      ...bindings[index],
      ...cloneValue(patch),
      id: bindingId,
    };
    if (updated.sequence.length === 0) {
      throw new Error("Keyboard binding sequence cannot be empty.");
    }
    bindings[index] = {
      ...updated,
      sequence: updated.sequence.map(normalizeStroke),
    };
  };

  const removeBinding = (bindingId: string): void => {
    assertActive();
    bindings = bindings.filter((item) => item.id !== bindingId);
    clearPendingChord();
  };

  const resetBindings = (
    nextProfileId: TimelineKeyboardProfileId = profileId,
  ): void => {
    assertActive();
    profileId = nextProfileId;
    bindings = defaultBindings(profileId);
    clearPendingChord();
  };

  const getCommandPalette = (
    query = "",
  ): readonly TimelineKeyboardPaletteItem[] => {
    assertActive();
    const normalizedQuery = query.trim().toLowerCase();
    const commandIds = [
      ...new Set(bindings.map((item) => item.commandId)),
    ];

    return commandIds
      .map((commandId) => ({
        commandId,
        label: PALETTE_LABELS[commandId].label,
        description: PALETTE_LABELS[commandId].description,
        shortcuts: bindings
          .filter((item) => item.commandId === commandId && item.enabled !== false)
          .map((item) => sequenceLabel(item.sequence)),
      }))
      .filter((item) => {
        if (!normalizedQuery) return true;
        return (
          item.label.toLowerCase().includes(normalizedQuery) ||
          item.description.toLowerCase().includes(normalizedQuery) ||
          item.commandId.toLowerCase().includes(normalizedQuery)
        );
      })
      .sort((a, b) => a.label.localeCompare(b.label));
  };

  const closeCommandPalette = (): void => {
    assertActive();
    paletteOpen = false;
  };

  const reset = (): void => {
    assertActive();
    profileId = options.profileId ?? "default";
    bindings = [
      ...defaultBindings(profileId),
      ...(options.bindings ?? []).map((item) => cloneValue(item)),
    ];
    focus = {
      context: "timeline",
      targetId: null,
      editable: false,
    };
    pendingSequence = [];
    pendingSince = 0;
    paletteOpen = false;
  };

  const dispose = (): void => {
    bindings = [];
    pendingSequence = [];
    pendingSince = 0;
    paletteOpen = false;
    disposed = true;
  };

  return {
    getSnapshot,
    dispatch,
    dispatchCommand,
    setFocus,
    setProfile,
    registerBinding,
    updateBinding,
    removeBinding,
    resetBindings,
    detectConflicts,
    getCommandPalette,
    closeCommandPalette,
    clearPendingChord,
    reset,
    dispose,
  };
}
