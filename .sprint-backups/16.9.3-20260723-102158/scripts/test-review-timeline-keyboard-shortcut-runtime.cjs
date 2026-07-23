/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

require.extensions[".ts"] = function compileTypeScript(module, filename) {
  const source = fs.readFileSync(filename, "utf8");
  const output = ts.transpileModule(source, {
    fileName: filename,
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      moduleResolution: ts.ModuleResolutionKind.NodeJs,
      esModuleInterop: true,
    },
  });
  module._compile(output.outputText, filename);
};

const keyboardIndexPath = path.resolve(
  __dirname,
  "../src/features/review/keyboard/index.ts",
);
const runtimePath = path.resolve(
  __dirname,
  "../src/features/review/keyboard/runtime.ts",
);
const resolverPath = path.resolve(
  __dirname,
  "../src/features/review/keyboard/resolver.ts",
);
const runtimeSource = fs.readFileSync(runtimePath, "utf8");
const resolverSource = fs.readFileSync(resolverPath, "utf8");

const {
  REVIEW_TIMELINE_KEYBOARD_CONTRACT_VERSION,
  createReviewTimelineKeyboardShortcutRuntime,
  isEditableKeyboardTarget,
  resolveReviewTimelineKeyboardShortcut,
} = require(keyboardIndexPath);

const context = {
  productionId: "production-1",
  timelineRevision: 12,
  platform: "windows",
  workspaceActive: true,
  busy: false,
  selectedClipIds: ["clip-1", "clip-2"],
  editableClipIds: ["clip-1", "clip-2"],
  activeClipId: "clip-1",
  cursorTime: 4,
  activeClipStartTime: 2,
  activeClipEndTime: 6,
  canUndo: true,
  canRedo: true,
  canPaste: true,
};
const contextBefore = structuredClone(context);

function main() {
  const transitions = [];
  const runtime = createReviewTimelineKeyboardShortcutRuntime({
    now: () => "2026-07-19T09:00:00.000Z",
  });
  const initial = runtime.getState();
  const unsubscribe = runtime.subscribe((state, previous) => {
    transitions.push(
      `${previous.stateRevision}->${state.stateRevision}`,
    );
  });

  const undo = press(runtime, { key: "z", ctrlKey: true }, context);
  const redoShift = press(
    runtime,
    { key: "Z", ctrlKey: true, shiftKey: true },
    context,
  );
  const redoY = press(runtime, { key: "y", ctrlKey: true }, context);
  const split = press(runtime, { key: "b", ctrlKey: true }, context);
  const duplicate = press(runtime, { key: "d", ctrlKey: true }, context);
  const deleted = press(runtime, { key: "Delete" }, context);
  const copied = press(runtime, { key: "c", ctrlKey: true }, context);
  const cut = press(runtime, { key: "x", ctrlKey: true }, context);
  const pasted = press(runtime, { key: "v", ctrlKey: true }, context);
  const macCopy = press(
    runtime,
    { key: "c", metaKey: true },
    { ...context, platform: "macos" },
  );

  const editableBlocked = runtime.handleKeyDown(
    {
      key: "z",
      ctrlKey: true,
      target: { tagName: "textarea" },
    },
    context,
  );
  const busyBlocked = runtime.handleKeyDown(
    { key: "Delete" },
    { ...context, busy: true },
  );
  const inactiveBlocked = runtime.handleKeyDown(
    { key: "z", ctrlKey: true },
    { ...context, workspaceActive: false },
  );
  const unavailableBlocked = runtime.handleKeyDown(
    { key: "d", ctrlKey: true },
    { ...context, activeClipId: null },
  );
  const repeatBlocked = runtime.handleKeyDown(
    { key: "c", ctrlKey: true, repeat: true },
    context,
  );
  const unsupported = runtime.handleKeyDown(
    { key: "q" },
    context,
  );

  const firstHeld = runtime.handleKeyDown(
    { key: "c", ctrlKey: true },
    context,
  );
  const duplicateHeld = runtime.handleKeyDown(
    { key: "c", ctrlKey: true },
    context,
  );
  const released = runtime.handleKeyUp({ key: "c" });
  const rearmed = runtime.handleKeyDown(
    { key: "c", ctrlKey: true },
    context,
  );

  const isolatedState = runtime.getState();
  isolatedState.lastIntent.clipIds[0] = "changed-outside";
  isolatedState.lastResult.intent.clipIds[0] = "changed-outside";
  const stateIsolated =
    runtime.getState().lastIntent.clipIds[0] === "clip-1" &&
    runtime.getState().lastResult.intent.clipIds[0] === "clip-1";

  const pureResolved = resolveReviewTimelineKeyboardShortcut(
    { key: "Backspace" },
    context,
  );
  pureResolved.intent.clipId = "changed-outside";
  const inputsUnchanged =
    JSON.stringify(context) === JSON.stringify(contextBefore);

  const reset = runtime.reset();
  unsubscribe();
  runtime.dispose();

  let disposedBlocked = false;
  try {
    runtime.handleKeyDown(
      { key: "z", ctrlKey: true },
      context,
    );
  } catch {
    disposedBlocked = true;
  }

  const checks = {
    contract_version_valid:
      REVIEW_TIMELINE_KEYBOARD_CONTRACT_VERSION === "16.7.4" &&
      initial.contractVersion === "16.7.4",
    initial_state_valid:
      initial.activeShortcut === null &&
      initial.handledCount === 0,
    undo_redo_shortcuts_valid:
      undo.intent.operation === "undo" &&
      redoShift.intent.operation === "redo" &&
      redoY.intent.operation === "redo",
    split_shortcut_valid:
      split.intent.operation === "split_clip" &&
      split.intent.clipId === "clip-1" &&
      split.intent.splitTime === 4,
    duplicate_delete_valid:
      duplicate.intent.operation === "duplicate_clip" &&
      deleted.intent.operation === "delete_clip" &&
      deleted.intent.clipId === "clip-1",
    clipboard_shortcuts_valid:
      copied.intent.operation === "copy" &&
      copied.intent.clipIds.length === 2 &&
      cut.intent.operation === "cut" &&
      pasted.intent.operation === "paste" &&
      pasted.intent.atTime === 4,
    mac_modifier_valid:
      macCopy.intent.operation === "copy" &&
      macCopy.chord.includes("macos+meta"),
    editable_targets_ignored:
      editableBlocked.handled === false &&
      editableBlocked.preventDefault === false &&
      editableBlocked.blockedReason === "editable_target" &&
      isEditableKeyboardTarget({ contentEditable: true }),
    busy_shortcut_blocked:
      busyBlocked.handled === false &&
      busyBlocked.preventDefault === true &&
      busyBlocked.blockedReason === "workspace_busy",
    inactive_workspace_ignored:
      inactiveBlocked.blockedReason === "workspace_inactive" &&
      inactiveBlocked.preventDefault === false,
    unavailable_command_blocked:
      unavailableBlocked.blockedReason === "command_unavailable" &&
      unavailableBlocked.intent === null,
    repeat_blocked:
      repeatBlocked.blockedReason === "key_repeat",
    unsupported_key_ignored:
      unsupported.blockedReason === "unsupported_shortcut" &&
      unsupported.preventDefault === false,
    held_key_deduplicated:
      firstHeld.handled === true &&
      duplicateHeld.handled === false &&
      duplicateHeld.blockedReason === "shortcut_already_active",
    keyup_rearms_shortcut:
      released.activeShortcut === null &&
      rearmed.handled === true,
    runtime_owns_context:
      !("expectedRevision" in rearmed.intent) &&
      !("expected_revision" in rearmed.intent),
    state_snapshots_isolated: stateIsolated,
    inputs_unchanged: inputsUnchanged,
    transitions_emitted:
      transitions.length > 0 &&
      new Set(transitions).size === transitions.length,
    reset_valid:
      reset.activeShortcut === null &&
      reset.lastIntent === null &&
      reset.handledCount === 0,
    disposed_blocked: disposedBlocked,
    no_react_dependency:
      !runtimeSource.includes("react") &&
      !resolverSource.includes("react"),
    no_api_or_timeline_mutation:
      !runtimeSource.includes("fetch(") &&
      !resolverSource.includes("fetch(") &&
      !runtimeSource.includes("timeline.tracks") &&
      !resolverSource.includes("timeline.tracks") &&
      !runtimeSource.includes("undoTimeline(") &&
      !runtimeSource.includes("deleteClip("),
  };

  console.log("=== Timeline Keyboard Shortcut Runtime ===");
  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }
  console.log(
    "\nDONE: Timeline keyboard shortcut runtime test completed.",
  );
}

function press(runtime, input, activeContext) {
  const result = runtime.handleKeyDown(input, activeContext);
  runtime.handleKeyUp({ key: input.key });
  return result;
}

main();
