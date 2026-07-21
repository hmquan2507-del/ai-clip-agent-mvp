import {
  REVIEW_TIMELINE_KEYBOARD_CONTRACT_VERSION,
  type ReviewTimelineKeyboardCommandIntent,
  type ReviewTimelineKeyboardContext,
  type ReviewTimelineKeyboardInput,
  type ReviewTimelineKeyboardOperation,
  type ReviewTimelineKeyboardResult,
  type ReviewTimelineKeyboardShortcut,
} from "./contracts";

const EPSILON = 0.000001;

export function resolveReviewTimelineKeyboardShortcut(
  input: ReviewTimelineKeyboardInput,
  context: ReviewTimelineKeyboardContext,
): ReviewTimelineKeyboardResult {
  const normalizedInput = normalizeInput(input);
  const normalizedContext = normalizeContext(context);

  if (isEditableKeyboardTarget(normalizedInput.target)) {
    return blocked("editable_target", false);
  }

  const shortcut = matchShortcut(
    normalizedInput,
    normalizedContext.platform,
  );
  if (!shortcut) {
    return blocked("unsupported_shortcut", false);
  }
  if (!normalizedContext.workspaceActive) {
    return blocked(
      "workspace_inactive",
      false,
      shortcut,
    );
  }
  if (normalizedContext.busy) {
    return blocked(
      "workspace_busy",
      true,
      shortcut,
    );
  }
  if (normalizedInput.repeat) {
    return blocked(
      "key_repeat",
      true,
      shortcut,
    );
  }

  const intent = buildIntent(
    shortcut.operation,
    normalizedContext,
  );
  if (!intent) {
    return blocked(
      "command_unavailable",
      true,
      shortcut,
    );
  }

  return {
    contractVersion:
      REVIEW_TIMELINE_KEYBOARD_CONTRACT_VERSION,
    handled: true,
    preventDefault: true,
    operation: shortcut.operation,
    intent,
    blockedReason: null,
    chord: shortcut.chord,
  };
}

export function identifyReviewTimelineKeyboardShortcut(
  input: ReviewTimelineKeyboardInput,
  platform:
    ReviewTimelineKeyboardContext["platform"],
): ReviewTimelineKeyboardShortcut | null {
  return matchShortcut(
    normalizeInput(input),
    platform,
  );
}

export function isEditableKeyboardTarget(
  target:
    ReviewTimelineKeyboardInput["target"],
): boolean {
  if (!target) return false;
  if (target.contentEditable) return true;

  const tagName =
    target.tagName?.trim().toLowerCase() ?? "";
  const role =
    target.role?.trim().toLowerCase() ?? "";

  return (
    tagName === "input" ||
    tagName === "textarea" ||
    tagName === "select" ||
    role === "textbox" ||
    role === "searchbox" ||
    role === "combobox" ||
    role === "spinbutton"
  );
}

function matchShortcut(
  input: NormalizedKeyboardInput,
  platform:
    ReviewTimelineKeyboardContext["platform"],
): ReviewTimelineKeyboardShortcut | null {
  const primary =
    platform === "macos"
      ? input.metaKey && !input.ctrlKey
      : input.ctrlKey && !input.metaKey;
  const noPrimary =
    !input.ctrlKey && !input.metaKey;

  if (input.altKey) return null;

  if (primary && input.key === "z") {
    return shortcut(
      input.shiftKey ? "redo" : "undo",
      input,
      platform,
    );
  }
  if (
    platform !== "macos" &&
    primary &&
    !input.shiftKey &&
    input.key === "y"
  ) {
    return shortcut("redo", input, platform);
  }
  if (primary && !input.shiftKey) {
    const operations:
      Partial<Record<string, ReviewTimelineKeyboardOperation>> = {
        b: "split_clip",
        d: "duplicate_clip",
        c: "copy",
        x: "cut",
        v: "paste",
      };
    const operation = operations[input.key];
    if (operation) {
      return shortcut(operation, input, platform);
    }
  }
  if (
    noPrimary &&
    !input.shiftKey &&
    (
      input.key === "delete" ||
      input.key === "backspace"
    )
  ) {
    return shortcut("delete_clip", input, platform);
  }
  return null;
}

function buildIntent(
  operation: ReviewTimelineKeyboardOperation,
  context: NormalizedKeyboardContext,
): ReviewTimelineKeyboardCommandIntent | null {
  const activeClipId = context.activeClipId;
  const activeEditable =
    activeClipId !== null &&
    context.editableClipIds.includes(
      activeClipId,
    );
  const selected = uniqueIdentifiers(
    context.selectedClipIds,
  );
  const editableSelected = selected.filter(
    (clipId) =>
      context.editableClipIds.includes(clipId),
  );

  switch (operation) {
    case "undo":
      return context.canUndo
        ? { operation: "undo" }
        : null;
    case "redo":
      return context.canRedo
        ? { operation: "redo" }
        : null;
    case "split_clip":
      if (
        !activeEditable ||
        activeClipId === null ||
        context.activeClipStartTime === null ||
        context.activeClipEndTime === null ||
        context.cursorTime <=
          context.activeClipStartTime + EPSILON ||
        context.cursorTime >=
          context.activeClipEndTime - EPSILON
      ) {
        return null;
      }
      return {
        operation: "split_clip",
        clipId: activeClipId,
        splitTime: context.cursorTime,
      };
    case "duplicate_clip":
      return activeEditable && activeClipId !== null
        ? {
            operation: "duplicate_clip",
            clipId: activeClipId,
          }
        : null;
    case "delete_clip":
      return activeEditable && activeClipId !== null
        ? {
            operation: "delete_clip",
            clipId: activeClipId,
          }
        : null;
    case "copy":
      return selected.length > 0
        ? { operation: "copy", clipIds: selected }
        : null;
    case "cut":
      return (
        selected.length > 0 &&
        editableSelected.length === selected.length
      )
        ? { operation: "cut", clipIds: selected }
        : null;
    case "paste":
      return context.canPaste
        ? {
            operation: "paste",
            atTime: context.cursorTime,
          }
        : null;
  }
}

function shortcut(
  operation: ReviewTimelineKeyboardOperation,
  input: NormalizedKeyboardInput,
  platform:
    ReviewTimelineKeyboardContext["platform"],
): ReviewTimelineKeyboardShortcut {
  const modifiers = [
    input.ctrlKey ? "ctrl" : null,
    input.metaKey ? "meta" : null,
    input.shiftKey ? "shift" : null,
  ].filter(Boolean);
  const triggerKey = input.key;
  return {
    operation,
    chord: [platform, ...modifiers, triggerKey]
      .join("+"),
    triggerKey,
  };
}

function blocked(
  reason:
    ReviewTimelineKeyboardResult["blockedReason"],
  preventDefault: boolean,
  shortcutValue:
    ReviewTimelineKeyboardShortcut | null = null,
): ReviewTimelineKeyboardResult {
  return {
    contractVersion:
      REVIEW_TIMELINE_KEYBOARD_CONTRACT_VERSION,
    handled: false,
    preventDefault,
    operation:
      shortcutValue?.operation ?? null,
    intent: null,
    blockedReason: reason,
    chord: shortcutValue?.chord ?? null,
  };
}

interface NormalizedKeyboardInput {
  key: string;
  code: string | null;
  ctrlKey: boolean;
  metaKey: boolean;
  shiftKey: boolean;
  altKey: boolean;
  repeat: boolean;
  target:
    ReviewTimelineKeyboardInput["target"];
}

type NormalizedKeyboardContext =
  ReviewTimelineKeyboardContext;

function normalizeInput(
  input: ReviewTimelineKeyboardInput,
): NormalizedKeyboardInput {
  const key = input.key.trim().toLowerCase();
  if (!key) {
    throw new TypeError("input.key is required.");
  }
  return {
    key,
    code: input.code?.trim() || null,
    ctrlKey: Boolean(input.ctrlKey),
    metaKey: Boolean(input.metaKey),
    shiftKey: Boolean(input.shiftKey),
    altKey: Boolean(input.altKey),
    repeat: Boolean(input.repeat),
    target: input.target
      ? { ...input.target }
      : null,
  };
}

function normalizeContext(
  context: ReviewTimelineKeyboardContext,
): NormalizedKeyboardContext {
  const productionId = context.productionId.trim();
  if (!productionId) {
    throw new TypeError("productionId is required.");
  }
  if (
    !Number.isInteger(context.timelineRevision) ||
    context.timelineRevision < 1
  ) {
    throw new TypeError(
      "timelineRevision must be a positive integer.",
    );
  }
  if (!Number.isFinite(context.cursorTime) || context.cursorTime < 0) {
    throw new TypeError(
      "cursorTime must be a non-negative finite number.",
    );
  }
  return {
    ...context,
    productionId,
    selectedClipIds: uniqueIdentifiers(
      context.selectedClipIds,
    ),
    editableClipIds: uniqueIdentifiers(
      context.editableClipIds,
    ),
    activeClipId:
      context.activeClipId?.trim() || null,
    activeClipStartTime: optionalNonNegative(
      context.activeClipStartTime,
      "activeClipStartTime",
    ),
    activeClipEndTime: optionalNonNegative(
      context.activeClipEndTime,
      "activeClipEndTime",
    ),
  };
}

function uniqueIdentifiers(
  values: string[],
): string[] {
  const identifiers = values.map((value) => {
    const normalized = value.trim();
    if (!normalized) {
      throw new TypeError(
        "clip identifiers must not be empty.",
      );
    }
    return normalized;
  });
  return [...new Set(identifiers)];
}

function optionalNonNegative(
  value: number | null,
  name: string,
): number | null {
  if (value === null) return null;
  if (!Number.isFinite(value) || value < 0) {
    throw new TypeError(
      `${name} must be non-negative and finite.`,
    );
  }
  return value;
}
