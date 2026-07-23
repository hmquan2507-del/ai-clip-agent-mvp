const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

require.extensions[".ts"] = function compile(module, filename) {
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

const commandApi = require(path.resolve(
  __dirname,
  "../src/features/playback/runtime/timeline-command-runtime.ts",
));
const keyboardApi = require(path.resolve(
  __dirname,
  "../src/features/playback/runtime/timeline-keyboard-runtime.ts",
));

function initialDocument() {
  return {
    version: 0,
    tracks: [{ id: "video-1" }],
    clips: [
      {
        id: "a",
        trackId: "video-1",
        startFrame: 0,
        endFrame: 100,
        sourceStartFrame: 0,
        sourceEndFrame: 100,
      },
      {
        id: "b",
        trackId: "video-1",
        startFrame: 100,
        endFrame: 180,
        sourceStartFrame: 0,
        sourceEndFrame: 80,
      },
    ],
    selection: ["a"],
  };
}

function key(key, extra = {}) {
  return { key, timestamp: Date.now(), ...extra };
}

function main() {
  const playbackEvents = [];
  const selectionEvents = [];
  const commandRuntime =
    commandApi.createTimelineCommandRuntime(initialDocument());
  const keyboardRuntime =
    keyboardApi.createTimelineKeyboardRuntime({
      commandRuntime,
      profileId: "default",
      chordTimeoutMs: 500,
      onPlaybackCommand: (commandId) => playbackEvents.push(commandId),
      onSelectionCommand: (commandId) => selectionEvents.push(commandId),
    });

  assert.equal(keyboardRuntime.getSnapshot().version, "16.9.7");
  assert.equal(keyboardRuntime.getSnapshot().profileId, "default");
  assert.equal(keyboardRuntime.getSnapshot().focus.context, "timeline");
  assert.equal(keyboardRuntime.getSnapshot().disposed, false);

  const split = keyboardRuntime.dispatch(
    key("k", { ctrlKey: true }),
    { playheadFrame: 40 },
  );
  assert.equal(split.handled, true);
  assert.equal(split.commandId, "timeline.split");
  assert.equal(commandRuntime.getSnapshot().document.clips.length, 3);

  keyboardRuntime.dispatch(key("z", { ctrlKey: true }));
  assert.equal(commandRuntime.getSnapshot().document.clips.length, 2);
  keyboardRuntime.dispatch(key("z", { ctrlKey: true, shiftKey: true }));
  assert.equal(commandRuntime.getSnapshot().document.clips.length, 3);

  commandRuntime.reset(initialDocument());
  keyboardRuntime.dispatch(key("d", { ctrlKey: true }), {
    command: { deltaFrames: 25 },
  });
  assert.equal(commandRuntime.getSnapshot().document.clips.length, 3);

  commandRuntime.reset(initialDocument());
  const firstChord = keyboardRuntime.dispatch(
    key("k", { ctrlKey: true, altKey: true, timestamp: 100 }),
  );
  assert.equal(firstChord.pendingChord, true);
  const secondChord = keyboardRuntime.dispatch(
    key("r", { timestamp: 200 }),
  );
  assert.equal(secondChord.commandId, "timeline.ripple-delete");
  assert.equal(commandRuntime.getSnapshot().document.clips.length, 1);
  assert.equal(
    commandRuntime.getSnapshot().document.clips[0].startFrame,
    0,
  );

  commandRuntime.reset(initialDocument());
  keyboardRuntime.dispatch(key("k", { ctrlKey: true, altKey: true, timestamp: 1000 }));
  const expired = keyboardRuntime.dispatch(
    key("r", { timestamp: 1700 }),
  );
  assert.equal(expired.handled, false);
  assert.equal(keyboardRuntime.getSnapshot().pendingSequence.length, 0);

  keyboardRuntime.setFocus({
    context: "text-input",
    targetId: "title-input",
    editable: true,
  });
  const textIgnored = keyboardRuntime.dispatch(
    key("k", { ctrlKey: true }),
    { playheadFrame: 50 },
  );
  assert.equal(textIgnored.handled, false);
  assert.equal(commandRuntime.getSnapshot().document.clips.length, 2);

  keyboardRuntime.setFocus({
    context: "preview",
    targetId: "preview",
    editable: false,
  });
  keyboardRuntime.dispatch(key(" "));
  assert.deepEqual(playbackEvents, ["playback.toggle"]);

  keyboardRuntime.setFocus({
    context: "timeline",
    targetId: "timeline",
    editable: false,
  });
  keyboardRuntime.dispatch(key("Escape"));
  assert.deepEqual(selectionEvents, ["selection.clear"]);

  keyboardRuntime.dispatch(
    key("p", { ctrlKey: true, shiftKey: true }),
  );
  assert.equal(keyboardRuntime.getSnapshot().paletteOpen, true);
  const palette = keyboardRuntime.getCommandPalette("split");
  assert.equal(palette.length, 1);
  assert.equal(palette[0].commandId, "timeline.split");
  assert.equal(palette[0].shortcuts.length > 0, true);
  keyboardRuntime.closeCommandPalette();
  assert.equal(keyboardRuntime.getSnapshot().paletteOpen, false);

  keyboardRuntime.registerBinding({
    id: "custom-delete-conflict",
    commandId: "timeline.ripple-delete",
    sequence: [{ key: "Delete" }],
    contexts: ["timeline"],
    enabled: true,
  });
  const conflicts = keyboardRuntime.detectConflicts();
  assert.equal(conflicts.length, 1);
  assert.equal(
    conflicts[0].commandIds.includes("timeline.delete"),
    true,
  );
  assert.equal(
    conflicts[0].commandIds.includes("timeline.ripple-delete"),
    true,
  );

  keyboardRuntime.updateBinding("custom-delete-conflict", {
    sequence: [{ key: "Backspace" }],
  });
  assert.equal(keyboardRuntime.detectConflicts().length, 0);
  keyboardRuntime.removeBinding("custom-delete-conflict");

  keyboardRuntime.setProfile("capcut");
  assert.equal(keyboardRuntime.getSnapshot().profileId, "capcut");
  commandRuntime.reset(initialDocument());
  keyboardRuntime.setFocus({
    context: "timeline",
    targetId: "timeline",
    editable: false,
  });
  const capcutSplit = keyboardRuntime.dispatch(
    key("b", { ctrlKey: true }),
    { playheadFrame: 60 },
  );
  assert.equal(capcutSplit.commandId, "timeline.split");
  assert.equal(commandRuntime.getSnapshot().document.clips.length, 3);

  keyboardRuntime.resetBindings("premiere");
  assert.equal(keyboardRuntime.getSnapshot().profileId, "premiere");
  assert.equal(keyboardRuntime.getSnapshot().bindings.length > 10, true);

  const repeated = keyboardRuntime.dispatch(
    key("Delete", { repeat: true }),
  );
  assert.equal(repeated.handled, false);

  const snapshot = keyboardRuntime.getSnapshot();
  snapshot.bindings.push?.({
    id: "mutation",
    commandId: "timeline.delete",
    sequence: [{ key: "X" }],
    contexts: ["timeline"],
  });
  assert.equal(
    keyboardRuntime.getSnapshot().bindings.some(
      (item) => item.id === "mutation",
    ),
    false,
  );

  keyboardRuntime.dispose();
  assert.equal(keyboardRuntime.getSnapshot().disposed, true);
  assert.throws(() => keyboardRuntime.dispatch(key("Delete")));

  const source = fs.readFileSync(
    path.resolve(
      __dirname,
      "../src/features/playback/runtime/timeline-keyboard-runtime.ts",
    ),
    "utf8",
  );
  assert.equal(source.includes('from "react"'), false);
  assert.equal(source.includes("addEventListener"), false);
  assert.equal(source.includes("window."), false);
  assert.equal(source.includes("document.createElement"), false);

  console.log(
    "SPRINT 16.9.7 PROFESSIONAL TIMELINE KEYBOARD RUNTIME: PASS",
  );
}

main();
