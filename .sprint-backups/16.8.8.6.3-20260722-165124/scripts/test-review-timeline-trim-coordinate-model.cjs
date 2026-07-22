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

const trim = require(path.resolve(
  __dirname,
  "../src/features/review/trim/index.ts",
));

function main() {
  const viewport = {
    left: 100,
    top: 100,
    width: 500,
    height: 240,
    scrollLeft: 0,
    contentWidth: 1000,
  };
  const source = {
    clipId: "clip-1",
    trackId: "track-1",
    startTime: 2,
    endTime: 8,
    duration: 6,
    editable: true,
    trackLocked: false,
  };
  const sourceBefore = structuredClone(source);
  const viewportBefore = structuredClone(viewport);

  const startProjection = trim.projectReviewTimelineClipTrim({
    handle: "start",
    source,
    pointer: { clientX: 250, clientY: 140 },
    viewport,
    timelineDuration: 20,
    fps: 30,
  });
  const endProjection = trim.projectReviewTimelineClipTrim({
    handle: "end",
    source,
    pointer: { clientX: 550, clientY: 140 },
    viewport,
    timelineDuration: 20,
    fps: 30,
  });
  const quantized = trim.projectReviewTimelineClipTrim({
    handle: "start",
    source,
    pointer: { clientX: 251, clientY: 140 },
    viewport,
    timelineDuration: 20,
    fps: 30,
  });
  const minimumBound = trim.projectReviewTimelineClipTrim({
    handle: "start",
    source,
    pointer: { clientX: 490, clientY: 140 },
    viewport,
    timelineDuration: 20,
    fps: 30,
    minimumDuration: 2,
  });
  const startBound = trim.projectReviewTimelineClipTrim({
    handle: "start",
    source,
    pointer: { clientX: -200, clientY: 140 },
    viewport,
    timelineDuration: 20,
    fps: 30,
  });
  const endBound = trim.projectReviewTimelineClipTrim({
    handle: "end",
    source,
    pointer: { clientX: 2000, clientY: 140 },
    viewport,
    timelineDuration: 20,
    fps: 30,
  });
  const locked = trim.projectReviewTimelineClipTrim({
    handle: "start",
    source: { ...source, trackLocked: true },
    pointer: { clientX: 250, clientY: 140 },
    viewport,
    timelineDuration: 20,
    fps: 30,
  });
  const readOnly = trim.projectReviewTimelineClipTrim({
    handle: "end",
    source: { ...source, editable: false },
    pointer: { clientX: 550, clientY: 140 },
    viewport,
    timelineDuration: 20,
    fps: 30,
  });
  const minimumRange = trim.projectReviewTimelineClipTrim({
    handle: "end",
    source: {
      ...source,
      endTime: 3,
      duration: 1,
    },
    pointer: { clientX: 250, clientY: 140 },
    viewport,
    timelineDuration: 20,
    fps: 30,
    minimumDuration: 1,
  });
  const noChange = trim.projectReviewTimelineClipTrim({
    handle: "start",
    source,
    pointer: { clientX: 200, clientY: 140 },
    viewport,
    timelineDuration: 20,
    fps: 30,
  });
  const scrolled = trim.projectReviewTimelineClipTrim({
    handle: "start",
    source: {
      ...source,
      startTime: 12,
      endTime: 18,
    },
    pointer: { clientX: 350, clientY: 140 },
    viewport: { ...viewport, scrollLeft: 500 },
    timelineDuration: 20,
    fps: 30,
  });

  let invalidSourceBlocked = false;
  try {
    trim.projectReviewTimelineClipTrim({
      handle: "start",
      source: { ...source, duration: 5 },
      pointer: { clientX: 250, clientY: 140 },
      viewport,
      timelineDuration: 20,
      fps: 30,
    });
  } catch (error) {
    invalidSourceBlocked = error instanceof RangeError;
  }

  const contractSource = fs.readFileSync(
    path.resolve(
      __dirname,
      "../src/features/review/trim/contracts.ts",
    ),
    "utf8",
  );
  const coordinateSource = fs.readFileSync(
    path.resolve(
      __dirname,
      "../src/features/review/trim/coordinates.ts",
    ),
    "utf8",
  );

  const checks = {
    contract_version_valid:
      trim.REVIEW_TIMELINE_TRIM_CONTRACT_VERSION === "16.7.1",
    start_projection_valid:
      startProjection.valid === true &&
      startProjection.projectedStartTime === 3 &&
      startProjection.projectedEndTime === 8 &&
      startProjection.projectedDuration === 5,
    end_projection_valid:
      endProjection.valid === true &&
      endProjection.projectedStartTime === 2 &&
      endProjection.projectedEndTime === 9 &&
      endProjection.projectedDuration === 7,
    intents_runtime_ready:
      startProjection.trimIntent.operation === "trim_clip_start" &&
      startProjection.trimIntent.newStartTime === 3 &&
      endProjection.trimIntent.operation === "trim_clip_end" &&
      endProjection.trimIntent.newEndTime === 9 &&
      !("expectedRevision" in startProjection.trimIntent),
    frame_quantization_valid:
      Math.abs(quantized.projectedTime - 91 / 30) < 0.000001,
    minimum_duration_enforced:
      minimumBound.projectedStartTime === 6 &&
      minimumBound.projectedDuration === 2,
    timeline_bounds_enforced:
      startBound.projectedStartTime === 0 &&
      endBound.projectedEndTime === 20 &&
      startBound.pointerInsideViewport === false &&
      endBound.pointerInsideViewport === false,
    scrolled_coordinate_valid:
      scrolled.projectedStartTime === 15,
    locked_track_blocked:
      locked.valid === false &&
      locked.blockedReason === "track_locked" &&
      locked.trimIntent === null,
    read_only_clip_blocked:
      readOnly.valid === false &&
      readOnly.blockedReason === "clip_not_editable",
    minimum_range_blocked:
      minimumRange.valid === false &&
      minimumRange.blockedReason === "range_not_trimmable" &&
      minimumRange.trimIntent === null,
    unchanged_projection_blocked:
      noChange.valid === false &&
      noChange.blockedReason === "no_change",
    handle_hit_testing_valid:
      trim.resolveReviewTimelineTrimHandle({
        clipLeft: 200,
        clipWidth: 300,
        clientX: 204,
      }) === "start" &&
      trim.resolveReviewTimelineTrimHandle({
        clipLeft: 200,
        clipWidth: 300,
        clientX: 496,
      }) === "end" &&
      trim.resolveReviewTimelineTrimHandle({
        clipLeft: 200,
        clipWidth: 300,
        clientX: 350,
      }) === null,
    invalid_source_blocked: invalidSourceBlocked,
    inputs_unchanged:
      JSON.stringify(source) === JSON.stringify(sourceBefore) &&
      JSON.stringify(viewport) === JSON.stringify(viewportBefore),
    no_react_dependency:
      !contractSource.includes("react") &&
      !coordinateSource.includes("react"),
    no_api_or_timeline_mutation:
      !coordinateSource.includes("fetch(") &&
      !coordinateSource.includes("trimClipStart(") &&
      !coordinateSource.includes("trimClipEnd(") &&
      !coordinateSource.includes("timeline.tracks"),
  };

  console.log(
    "=== Timeline Trim Interaction Contracts & Coordinate Model ===",
  );
  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }
  console.log(
    "\nDONE: Timeline trim interaction contracts and coordinate model test completed.",
  );
}

main();
