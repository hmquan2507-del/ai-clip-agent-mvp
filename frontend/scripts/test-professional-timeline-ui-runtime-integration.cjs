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
const uiApi = require(path.resolve(
  __dirname,
  "../src/features/playback/runtime/timeline-ui-integration-controller.ts",
));

function documentFixture() {
  return {
    version: 0,
    tracks: [{ id: "video-1" }, { id: "audio-1" }],
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
        id: "music",
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

function main() {
  const commandRuntime =
    commandApi.createTimelineCommandRuntime(documentFixture());
  const keyboardRuntime =
    keyboardApi.createTimelineKeyboardRuntime({
      commandRuntime,
      profileId: "default",
    });
  const controller =
    uiApi.createTimelineUiIntegrationController({
      commandRuntime,
      keyboardRuntime,
      initialPlayheadFrame: 40,
      initialViewport: {
        widthPx: 1000,
        pixelsPerFrame: 2,
      },
      snapThresholdPx: 8,
    });

  assert.equal(controller.getSnapshot().version, "16.9.8");
  assert.equal(controller.getSnapshot().tool, "select");
  assert.equal(controller.getSnapshot().playheadFrame, 40);
  assert.equal(controller.frameToPixel(50), 100);
  assert.equal(controller.pixelToFrame(100), 50);

  controller.setTool("trim");
  assert.equal(controller.getSnapshot().tool, "trim");

  controller.setViewport({ zoom: 2 });
  assert.equal(controller.getSnapshot().viewport.pixelsPerFrame, 4);

  controller.selectClip("b");
  assert.deepEqual(
    controller.getSnapshot().document.selection,
    ["b"],
  );
  controller.selectClip("a", { additive: true });
  assert.deepEqual(
    new Set(controller.getSnapshot().document.selection),
    new Set(["a", "b"]),
  );
  controller.selectClip("a", { toggle: true });
  assert.deepEqual(
    controller.getSnapshot().document.selection,
    ["b"],
  );

  controller.marqueeSelect(0, 105, ["video-1"]);
  assert.deepEqual(
    new Set(controller.getSnapshot().document.selection),
    new Set(["a", "b"]),
  );

  commandRuntime.reset(documentFixture());
  controller.setViewport({ pixelsPerFrame: 2, scrollFrame: 0 });
  controller.pointerDown({
    pointerId: 1,
    x: 20,
    clipIds: ["a"],
    mode: "move",
  });
  controller.pointerMove({
    pointerId: 1,
    x: 60,
    snapFrames: [30],
  });
  assert.equal(controller.getSnapshot().snapGuide.frame, 30);
  controller.pointerUp({ pointerId: 1 });
  assert.equal(
    controller.getSnapshot().document.clips.find(
      (clip) => clip.id === "a",
    ).startFrame,
    20,
  );
  assert.equal(controller.getSnapshot().canUndo, true);

  controller.undo();
  assert.equal(
    controller.getSnapshot().document.clips.find(
      (clip) => clip.id === "a",
    ).startFrame,
    0,
  );
  controller.redo();
  assert.equal(
    controller.getSnapshot().document.clips.find(
      (clip) => clip.id === "a",
    ).startFrame,
    20,
  );

  commandRuntime.reset(documentFixture());
  controller.setPlayheadFrame(40);
  controller.splitAtPlayhead();
  assert.equal(controller.getSnapshot().document.clips.length, 4);

  commandRuntime.reset(documentFixture());
  controller.duplicateSelection(25);
  assert.equal(controller.getSnapshot().document.clips.length, 4);

  commandRuntime.reset(documentFixture());
  controller.deleteSelection(false);
  assert.equal(
    controller.getSnapshot().document.clips.some(
      (clip) => clip.id === "a",
    ),
    false,
  );

  commandRuntime.reset(documentFixture());
  controller.deleteSelection(true);
  assert.equal(
    controller.getSnapshot().document.clips.find(
      (clip) => clip.id === "b",
    ).startFrame,
    0,
  );

  controller.openContextMenu(120, 90, ["b"]);
  assert.equal(controller.getSnapshot().contextMenu.open, true);
  assert.deepEqual(
    controller.getSnapshot().contextMenu.clipIds,
    ["b"],
  );
  controller.closeContextMenu();
  assert.equal(controller.getSnapshot().contextMenu.open, false);

  controller.openCommandPalette();
  assert.equal(controller.getSnapshot().commandPaletteOpen, true);
  controller.closeCommandPalette();
  assert.equal(controller.getSnapshot().commandPaletteOpen, false);

  controller.pointerDown({
    pointerId: 2,
    x: 20,
    clipIds: ["b"],
    mode: "move",
  });
  controller.cancelPointer();
  assert.equal(controller.getSnapshot().pointer.active, false);

  const snapshot = controller.getSnapshot();
  snapshot.document.selection.push?.("mutation");
  assert.equal(
    controller.getSnapshot().document.selection.includes("mutation"),
    false,
  );

  const uiSource = fs.readFileSync(
    path.resolve(
      __dirname,
      "../src/features/playback/ui/professional-timeline-ui.tsx",
    ),
    "utf8",
  );
  assert.equal(
    uiSource.includes('data-testid="professional-timeline-ui"'),
    true,
  );
  assert.equal(uiSource.includes("aria-selected"), true);
  assert.equal(uiSource.includes("onPointerDown"), true);
  assert.equal(uiSource.includes("onContextMenu"), true);
  assert.equal(uiSource.includes("command palette"), true);

  controller.dispose();
  assert.equal(controller.getSnapshot().disposed, true);
  assert.throws(() => controller.setTool("select"));

  console.log(
    "SPRINT 16.9.8 PROFESSIONAL TIMELINE UI RUNTIME INTEGRATION: PASS",
  );
}

main();
