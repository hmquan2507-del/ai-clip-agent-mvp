const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const playback = path.join(root, "src", "features", "playback");
const checks = [
  ["contracts/timeline-keyframe-overlay-contracts.ts", ["TimelineKeyframeOverlayState", "TimelineKeyframeDragPreview", "TimelineKeyframeSnapResult"]],
  ["runtime/timeline-keyframe-selection-runtime.ts", ["export class TimelineKeyframeSelectionRuntime", "selectRange", "toggle"]],
  ["runtime/timeline-keyframe-snap-runtime.ts", ["export class TimelineKeyframeSnapRuntime", "resolve("]],
  ["runtime/timeline-keyframe-overlay-runtime.ts", ["export class TimelineKeyframeOverlayRuntime", "buildState", "TimelineAnimationRangeOverlay"]],
  ["runtime/timeline-keyframe-drag-runtime.ts", ["export class TimelineKeyframeDragRuntime", "begin(", "update(", "commit("]],
  ["runtime/timeline-animation-overlay-runtime.ts", ["export class TimelineAnimationOverlayRuntime", "buildSegments"]],
  ["runtime/timeline-keyframe-lane-controller.ts", ["export class TimelineKeyframeLaneController", "duplicateSelected", "deleteSelected", "setInterpolation"]],
  ["ui/timeline-keyframe-lane.tsx", ["export function TimelineKeyframeLane", "Timeline keyframe lane", "Drag keyframes to retime", "Snap:"]],
];
for (const [relative, symbols] of checks) {
  const source = fs.readFileSync(path.join(playback, relative), "utf8");
  for (const symbol of symbols) if (!source.includes(symbol)) throw new Error(`Missing 16.8.9.3 capability: ${relative} -> ${symbol}`);
}
const runtimeFiles = checks.filter(([file]) => file.startsWith("runtime/")).map(([file]) => file);
for (const relative of runtimeFiles) {
  const source = fs.readFileSync(path.join(playback, relative), "utf8");
  if (/\b(document|window|HTMLElement|React)\b/.test(source)) throw new Error(`Runtime must remain DOM/React independent: ${relative}`);
}
for (const [relative, symbol] of [
  ["contracts/index.ts", 'export * from "./timeline-keyframe-overlay-contracts"'],
  ["runtime/index.ts", 'export * from "./timeline-keyframe-lane-controller"'],
  ["ui/index.ts", 'export * from "./timeline-keyframe-lane"'],
]) if (!fs.readFileSync(path.join(playback, relative), "utf8").includes(symbol)) throw new Error(`Missing export: ${relative}`);
console.log("SPRINT 16.8.9.3 TIMELINE KEYFRAME LANE & ANIMATION OVERLAY: PASS");
