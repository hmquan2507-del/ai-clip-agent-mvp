/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

function compileTypeScript(module, filename) {
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
}

require.extensions[".ts"] = compileTypeScript;

const drag = require(path.resolve(
  __dirname,
  "../src/features/review/drag/index.ts",
));

function main() {
  const viewport = {
    left: 100,
    top: 100,
    width: 500,
    height: 200,
    scrollLeft: 0,
    contentWidth: 1000,
  };
  const scrolledViewport = {
    ...viewport,
    scrollLeft: 500,
  };
  const source = {
    clipId: "clip-1",
    trackId: "track-1",
    startTime: 2,
    endTime: 7,
    duration: 5,
  };
  const lanes = [
    {
      trackId: "track-1",
      top: 120,
      height: 40,
      locked: false,
    },
    {
      trackId: "track-2",
      top: 160,
      height: 40,
      locked: false,
    },
  ];
  const sourceBefore = structuredClone(source);
  const lanesBefore = structuredClone(lanes);

  const scrolledTime =
    drag.clientXToTimelineTime(
      350,
      scrolledViewport,
      20,
    );
  const roundTripClientX =
    drag.timelineTimeToClientX(
      scrolledTime,
      scrolledViewport,
      20,
    );
  const projection =
    drag.projectReviewTimelineClipMove({
      source,
      pointer: {
        clientX: 575,
        clientY: 175,
      },
      grabOffsetTime: 1.5,
      viewport,
      duration: 20,
      fps: 30,
      lanes,
    });
  const lockedProjection =
    drag.projectReviewTimelineClipMove({
      source,
      pointer: {
        clientX: 575,
        clientY: 175,
      },
      grabOffsetTime: 1.5,
      viewport,
      duration: 20,
      fps: 30,
      lanes: lanes.map(
        (lane) => ({
          ...lane,
          locked:
            lane.trackId ===
            "track-2",
        }),
      ),
    });
  const outsideTrackProjection =
    drag.projectReviewTimelineClipMove({
      source,
      pointer: {
        clientX: 575,
        clientY: 260,
      },
      grabOffsetTime: 1.5,
      viewport,
      duration: 20,
      fps: 30,
      lanes,
    });
  const clampedProjection =
    drag.projectReviewTimelineClipMove({
      source,
      pointer: {
        clientX: 1000,
        clientY: 130,
      },
      grabOffsetTime: 0,
      viewport,
      duration: 20,
      fps: 30,
      lanes,
    });

  let invalidSourceBlocked = false;

  try {
    drag.projectReviewTimelineClipMove({
      source: {
        ...source,
        duration: 4,
      },
      pointer: {
        clientX: 200,
        clientY: 130,
      },
      grabOffsetTime: 0,
      viewport,
      duration: 20,
      fps: 30,
      lanes,
    });
  } catch (error) {
    invalidSourceBlocked =
      error instanceof RangeError;
  }

  const contractSource = fs.readFileSync(
    path.resolve(
      __dirname,
      "../src/features/review/drag/contracts.ts",
    ),
    "utf8",
  );
  const coordinateSource = fs.readFileSync(
    path.resolve(
      __dirname,
      "../src/features/review/drag/coordinates.ts",
    ),
    "utf8",
  );

  const checks = {
    contract_version_valid:
      drag.REVIEW_TIMELINE_DRAG_CONTRACT_VERSION ===
      "16.5.1",
    scrolled_coordinate_valid:
      Math.abs(scrolledTime - 15) < 0.000001,
    coordinate_round_trip:
      Math.abs(roundTripClientX - 350) < 0.000001,
    pointer_delta_valid:
      Math.abs(
        drag.pointerDeltaToTimelineDelta(
          100,
          1000,
          20,
        ) - 2,
      ) < 0.000001,
    frame_conversion_valid:
      drag.timelineTimeToFrame(1.5, 30) === 45 &&
      drag.frameToTimelineTime(45, 30) === 1.5,
    frame_quantization_valid:
      Math.abs(
        drag.quantizeTimelineTimeToFrame(
          1.51,
          30,
          20,
        ) -
          45 / 30,
      ) < 0.000001,
    track_lane_resolved:
      drag.resolveTimelineTrackLane(
        175,
        lanes,
      )?.trackId === "track-2",
    projection_valid:
      projection.valid === true &&
      projection.targetTrackId === "track-2" &&
      projection.projectedStartTime === 8 &&
      projection.projectedEndTime === 13,
    move_intent_runtime_ready:
      projection.moveIntent?.clipId === "clip-1" &&
      projection.moveIntent?.newStartTime === 8 &&
      projection.moveIntent?.targetTrackId === "track-2" &&
      !("expectedRevision" in projection.moveIntent),
    locked_track_blocked:
      lockedProjection.valid === false &&
      lockedProjection.blockedReason === "track_locked" &&
      lockedProjection.moveIntent === null,
    missing_track_blocked:
      outsideTrackProjection.valid === false &&
      outsideTrackProjection.blockedReason === "track_not_found",
    timeline_bounds_enforced:
      clampedProjection.projectedStartTime === 15 &&
      clampedProjection.projectedEndTime === 20,
    invalid_source_blocked:
      invalidSourceBlocked,
    inputs_unchanged:
      JSON.stringify(source) === JSON.stringify(sourceBefore) &&
      JSON.stringify(lanes) === JSON.stringify(lanesBefore),
    no_react_dependency:
      !contractSource.includes("react") &&
      !coordinateSource.includes("react"),
    no_api_or_mutation_access:
      !coordinateSource.includes("fetch(") &&
      !coordinateSource.includes("moveClip(") &&
      !coordinateSource.includes("timeline.tracks"),
  };

  console.log(
    "=== Timeline Drag Interaction Contracts & Coordinate Model ===",
  );

  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }

  console.log(
    "\nDONE: Timeline drag interaction contracts and coordinate model test completed.",
  );
}

main();
