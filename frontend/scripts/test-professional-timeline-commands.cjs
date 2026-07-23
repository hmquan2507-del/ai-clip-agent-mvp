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

const api = require(path.resolve(
  __dirname,
  "../src/features/playback/runtime/timeline-command-runtime.ts",
));

function initialDocument() {
  return {
    version: 0,
    tracks: [
      { id: "video-1" },
      { id: "audio-1" },
    ],
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
      {
        id: "c",
        trackId: "audio-1",
        startFrame: 0,
        endFrame: 180,
        sourceStartFrame: 0,
        sourceEndFrame: 180,
      },
    ],
    selection: ["a"],
  };
}

function command(id, kind, extra = {}) {
  return { id, kind, ...extra };
}

function main() {
  const runtime = api.createTimelineCommandRuntime(initialDocument());

  assert.equal(runtime.getSnapshot().version, "16.9.6");
  assert.equal(runtime.getSnapshot().undoDepth, 0);
  assert.equal(runtime.getSnapshot().canUndo, false);

  assert.equal(runtime.validate(command("split-invalid", "split", { frame: 0 })).valid, false);
  const split = runtime.execute(command("split", "split", { frame: 40 }));
  assert.equal(split.changed, true);
  assert.equal(runtime.getSnapshot().document.clips.length, 4);
  assert.equal(runtime.getSnapshot().document.clips.some((clip) => clip.startFrame === 40), true);

  runtime.undo();
  assert.equal(runtime.getSnapshot().document.clips.length, 3);
  runtime.redo();
  assert.equal(runtime.getSnapshot().document.clips.length, 4);

  runtime.reset(initialDocument());
  runtime.execute(command("duplicate", "duplicate", { deltaFrames: 200 }));
  assert.equal(runtime.getSnapshot().document.clips.length, 4);
  assert.equal(runtime.getSnapshot().document.selection.length, 1);

  runtime.execute(command("move", "move", { deltaFrames: 10 }));
  const duplicateId = runtime.getSnapshot().document.selection[0];
  assert.equal(runtime.getSnapshot().document.clips.find((clip) => clip.id === duplicateId).startFrame, 210);

  runtime.execute(command("trim", "trim", { startDeltaFrames: 5, endDeltaFrames: -5 }));
  const trimmed = runtime.getSnapshot().document.clips.find((clip) => clip.id === duplicateId);
  assert.equal(trimmed.startFrame, 215);
  assert.equal(trimmed.endFrame, 305);

  runtime.execute(command("group", "group", { clipIds: ["a", "b"], groupId: "g-1" }));
  assert.equal(runtime.getSnapshot().document.clips.filter((clip) => clip.groupId === "g-1").length, 2);
  runtime.execute(command("ungroup", "ungroup", { clipIds: ["a", "b"] }));
  assert.equal(runtime.getSnapshot().document.clips.filter((clip) => clip.groupId).length, 0);

  runtime.execute(command("mute-track", "mute", { clipIds: [], trackIds: ["audio-1"] }));
  assert.equal(runtime.getSnapshot().document.tracks.find((track) => track.id === "audio-1").muted, true);
  runtime.execute(command("hide-track", "hide", { clipIds: [], trackIds: ["video-1"] }));
  assert.equal(runtime.getSnapshot().document.tracks.find((track) => track.id === "video-1").hidden, true);
  runtime.execute(command("show-track", "show", { clipIds: [], trackIds: ["video-1"] }));
  assert.equal(runtime.getSnapshot().document.tracks.find((track) => track.id === "video-1").hidden, false);

  runtime.reset(initialDocument());
  runtime.execute(command("lock", "lock", { clipIds: ["a"] }));
  assert.equal(runtime.validate(command("blocked", "move", { clipIds: ["a"], deltaFrames: 1 })).valid, false);
  runtime.execute(command("unlock", "unlock", { clipIds: ["a"] }));
  assert.equal(runtime.validate(command("allowed", "move", { clipIds: ["a"], deltaFrames: 1 })).valid, true);

  runtime.reset(initialDocument());
  runtime.execute(command("delete", "delete", { clipIds: ["a"] }));
  assert.equal(runtime.getSnapshot().document.clips.some((clip) => clip.id === "a"), false);
  runtime.undo();

  runtime.execute(command("ripple", "ripple-delete", { clipIds: ["a"] }));
  const shiftedB = runtime.getSnapshot().document.clips.find((clip) => clip.id === "b");
  assert.equal(shiftedB.startFrame, 0);
  assert.equal(shiftedB.endFrame, 80);

  runtime.reset(initialDocument());
  runtime.beginTransaction("move-and-trim");
  runtime.execute(command("tx-move", "move", { clipIds: ["a"], deltaFrames: 10 }));
  runtime.execute(command("tx-trim", "trim", { clipIds: ["a"], endDeltaFrames: 10 }));
  const transaction = runtime.commitTransaction();
  assert.equal(transaction.commands.length, 2);
  assert.equal(runtime.getSnapshot().undoDepth, 1);
  runtime.undo();
  assert.equal(runtime.getSnapshot().document.clips.find((clip) => clip.id === "a").startFrame, 0);

  runtime.beginTransaction("rollback");
  runtime.execute(command("rollback-move", "move", { clipIds: ["a"], deltaFrames: 20 }));
  runtime.rollbackTransaction();
  assert.equal(runtime.getSnapshot().document.clips.find((clip) => clip.id === "a").startFrame, 0);

  runtime.reset(initialDocument());
  runtime.dispatchShortcut("Ctrl+K", { frame: 50 });
  assert.equal(runtime.getSnapshot().document.clips.length, 4);
  runtime.dispatchShortcut("Ctrl+Z");
  assert.equal(runtime.getSnapshot().document.clips.length, 3);
  runtime.dispatchShortcut("Ctrl+Shift+Z");
  assert.equal(runtime.getSnapshot().document.clips.length, 4);

  const snapshot = runtime.getSnapshot();
  snapshot.document.selection.push?.("mutation");
  assert.equal(runtime.getSnapshot().document.selection.includes("mutation"), false);

  runtime.dispose();
  assert.equal(runtime.getSnapshot().disposed, true);
  assert.throws(() => runtime.execute(command("disposed", "delete", { clipIds: ["a"] })));

  const source = fs.readFileSync(
    path.resolve(__dirname, "../src/features/playback/runtime/timeline-command-runtime.ts"),
    "utf8",
  );
  assert.equal(source.includes("react"), false);
  assert.equal(source.includes("document.createElement"), false);
  assert.equal(source.includes("window."), false);

  console.log("SPRINT 16.9.6 PROFESSIONAL TIMELINE COMMANDS: PASS");
}

main();
