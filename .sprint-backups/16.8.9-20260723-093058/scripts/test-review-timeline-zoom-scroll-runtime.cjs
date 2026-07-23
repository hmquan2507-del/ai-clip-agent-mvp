/* eslint-disable @typescript-eslint/no-require-imports */

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

const modulePath = path.resolve(
  __dirname,
  "../src/features/review/viewport/index.ts",
);
const runtimePath = path.resolve(
  __dirname,
  "../src/features/review/viewport/runtime.ts",
);
const source = fs.readFileSync(runtimePath, "utf8");

const {
  REVIEW_TIMELINE_VIEWPORT_CONTRACT_VERSION,
  createReviewTimelineViewportRuntime,
} = require(modulePath);

function main() {
  const transitions = [];
  const runtime = createReviewTimelineViewportRuntime({
    now: () => "2026-07-19T10:00:00.000Z",
  });
  const initial = runtime.getState();
  const unsubscribe = runtime.subscribe((state, previous) => {
    transitions.push(`${previous.stateRevision}->${state.stateRevision}`);
  });

  const fitted = runtime.synchronize({
    duration: 100,
    viewportWidth: 1000,
    baseContentWidth: 1000,
  });
  const zoomed = runtime.zoomIn();
  const centerBefore = 50;
  const centerAfter =
    (zoomed.scrollLeft + zoomed.viewportWidth / 2) /
    zoomed.contentWidth * zoomed.duration;
  const scrolled = runtime.setScrollLeft(250);
  const zoomedAtAnchor = runtime.setZoom(2, 25, 200);
  const anchorClientX =
    25 / zoomedAtAnchor.duration *
      zoomedAtAnchor.contentWidth -
    zoomedAtAnchor.scrollLeft;
  const maximum = runtime.setZoom(99);
  const minimum = runtime.setZoom(-99);
  const fitAgain = runtime.fit();

  const isolated = runtime.getState();
  isolated.zoom = 99;
  const stateIsolated = runtime.getState().zoom === 1;

  let invalidBlocked = false;
  try {
    runtime.synchronize({
      duration: -1,
      viewportWidth: 100,
      baseContentWidth: 100,
    });
  } catch {
    invalidBlocked = true;
  }

  unsubscribe();
  runtime.dispose();
  let disposedBlocked = false;
  try {
    runtime.zoomIn();
  } catch {
    disposedBlocked = true;
  }

  const checks = {
    contract_version_valid:
      REVIEW_TIMELINE_VIEWPORT_CONTRACT_VERSION === "16.7.6" &&
      initial.contractVersion === "16.7.6",
    initial_fit_valid:
      fitted.zoom === 1 &&
      fitted.scrollLeft === 0 &&
      fitted.contentWidth === 1000,
    zoom_in_valid:
      zoomed.zoom === 1.5 &&
      zoomed.contentWidth === 1500,
    center_anchor_preserved:
      Math.abs(centerAfter - centerBefore) < 0.000001,
    scroll_range_valid:
      scrolled.scrollLeft === 250 &&
      scrolled.visibleStartTime > 0 &&
      scrolled.visibleEndTime <= 100,
    explicit_anchor_preserved:
      Math.abs(anchorClientX - 200) < 0.000001,
    zoom_limits_enforced:
      maximum.zoom === 8 &&
      minimum.zoom === 1,
    fit_restores_full_timeline:
      fitAgain.zoom === 1 &&
      fitAgain.scrollLeft === 0 &&
      fitAgain.visibleStartTime === 0 &&
      fitAgain.visibleEndTime === 100,
    state_snapshots_isolated: stateIsolated,
    invalid_metrics_blocked: invalidBlocked,
    transitions_emitted_once:
      transitions.length === 7 &&
      new Set(transitions).size === transitions.length,
    disposed_blocked: disposedBlocked,
    no_react_dependency:
      !source.includes("react"),
    no_api_or_timeline_mutation:
      !source.includes("fetch(") &&
      !source.includes("timeline.tracks") &&
      !source.includes("moveClip(") &&
      !source.includes("trimClip"),
  };

  console.log("=== Timeline Zoom & Scroll Runtime ===");
  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }
  console.log(
    "\nDONE: Timeline zoom and scroll runtime test completed.",
  );
}

main();
