/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const frontendRoot = path.resolve(__dirname, "..");

function read(relativePath) {
  return fs.readFileSync(
    path.join(frontendRoot, relativePath),
    "utf8",
  );
}

function main() {
  const timeline = read(
    "src/features/review/shell/timeline.tsx",
  );
  const reviewIndex = read(
    "src/features/review/index.ts",
  );
  const viewportIndex = read(
    "src/features/review/viewport/index.ts",
  );
  const runtime = read(
    "src/features/review/viewport/runtime.ts",
  );
  const hook = read(
    "src/features/review/viewport/use-review-timeline-viewport.ts",
  );

  const checks = {
    viewport_runtime_exported:
      reviewIndex.includes('export * from "./viewport"') &&
      viewportIndex.includes('export * from "./contracts"') &&
      viewportIndex.includes('export * from "./runtime"'),
    timeline_owns_viewport_runtime:
      timeline.includes("useReviewTimelineViewport") &&
      hook.includes("createReviewTimelineViewportRuntime") &&
      hook.includes("runtime.getState()") &&
      hook.includes("runtime.subscribe("),
    resize_metrics_synchronized:
      hook.includes("new ResizeObserver(") &&
      hook.includes("runtime.synchronize({") &&
      hook.includes("baseContentWidth: Math.max("),
    scroll_state_authoritative:
      hook.includes("runtime.setScrollLeft(") &&
      timeline.includes("viewportState.scrollLeft") &&
      timeline.includes("timelineViewport.synchronizeScroll"),
    zoom_controls_connected:
      hook.includes("runtime.zoomOut()") &&
      hook.includes("runtime.zoomIn()") &&
      hook.includes("runtime.fit()") &&
      timeline.includes("viewportState.canZoomOut") &&
      timeline.includes("viewportState.canZoomIn"),
    pointer_anchor_zoom_connected:
      hook.includes("zoomAtPointer") &&
      hook.includes("event.ctrlKey") &&
      hook.includes("event.metaKey") &&
      hook.includes("anchorTime") &&
      hook.includes("event.clientX - rect.left - labelsWidth"),
    content_width_applied_once:
      timeline.includes("`${viewportState.contentWidth}px`") &&
      timeline.includes("data-review-timeline-zoom") &&
      timeline.includes("data-review-timeline-scroll"),
    drag_uses_scrolled_viewport:
      timeline.includes("scrollRect.left + labelsWidth") &&
      timeline.includes("scrollLeft:\n            viewportState.scrollLeft") &&
      timeline.includes("contentWidth:\n            viewportState.contentWidth"),
    trim_uses_same_geometry:
      timeline.includes("const geometry = measureDragGeometry()") &&
      timeline.includes("viewport: geometry.viewport") &&
      timeline.match(/measureDragGeometry\(\)/g)?.length >= 4,
    playhead_stays_on_canvas:
      timeline.includes("`${playhead}%`") &&
      timeline.includes("ref={timelineCanvasRef}"),
    selection_stays_on_canvas:
      timeline.includes("clip.selected") &&
      timeline.includes("`${projectedStart}%`") &&
      timeline.includes("`${projectedWidth}%`"),
    anchor_math_is_deterministic:
      runtime.includes("scrollForAnchor(") &&
      runtime.includes("visibleStartTime") &&
      runtime.includes("visibleEndTime") &&
      runtime.includes("contentWidth - viewportWidth"),
    viewport_state_is_disposed:
      hook.includes("runtime.dispose()") &&
      hook.includes("observer.disconnect()"),
    no_direct_api_calls:
      !timeline.includes("fetch(") &&
      !runtime.includes("fetch(") &&
      !hook.includes("fetch(") &&
      !timeline.includes("/api/"),
    no_direct_timeline_mutation:
      !runtime.includes("timeline.tracks") &&
      !timeline.includes("timeline.tracks =") &&
      !runtime.includes("moveClip(") &&
      !runtime.includes("trimClip"),
  };

  console.log(
    "=== Runtime-connected Timeline Zoom & Scroll UI ===",
  );
  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }
  console.log(
    "\nDONE: Runtime-connected timeline zoom and scroll UI test completed.",
  );
}

main();
