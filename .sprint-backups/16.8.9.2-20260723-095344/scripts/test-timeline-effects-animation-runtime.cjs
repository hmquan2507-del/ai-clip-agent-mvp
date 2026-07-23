const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const playback = path.join(root, "src", "features", "playback");
const checks = [
  ["contracts/timeline-effects-animation-contracts.ts", ["TimelineKeyframe", "TimelineEffectDefinition", "TimelineTransitionDefinition", "TimelineMotionPreset", "TimelineEffectsAnimationSnapshot"]],
  ["runtime/timeline-keyframe-model.ts", ["export class TimelineKeyframeModel", "static evaluate(", "ease-in-out", "hold"]],
  ["runtime/timeline-animation-track-runtime.ts", ["export class TimelineAnimationTrackRuntime", "addKeyframe(", "moveKeyframe(", "evaluateClip(", "restore("]],
  ["runtime/timeline-effect-stack-runtime.ts", ["export class TimelineEffectStackRuntime", "updateParameters(", "setEnabled(", "reorderEffect("]],
  ["runtime/timeline-transition-runtime.ts", ["export class TimelineTransitionRuntime", "addTransition(", "evaluate(", "fromOpacity", "toOpacity"]],
  ["runtime/timeline-motion-preset-registry.ts", ["export class TimelineMotionPresetRegistry", "fade-in", "zoom-in", "instantiate("]],
  ["runtime/timeline-effects-animation-runtime.ts", ["export class TimelineEffectsAnimationRuntime", "applyPreset(", "evaluateFrame(", "getSnapshot()", "restore("]],
  ["runtime/timeline-effects-history-bridge.ts", ["export class TimelineEffectsHistoryBridge", "custom", "executeCommand"]],
];
for (const [relative, symbols] of checks) {
  const source = fs.readFileSync(path.join(playback, relative), "utf8");
  for (const symbol of symbols) if (!source.includes(symbol)) throw new Error(`Missing Timeline Effects capability: ${relative} -> ${symbol}`);
  if (/\b(document|window|HTMLElement|React)\b/.test(source) && relative.includes("runtime/")) throw new Error(`Runtime is not UI-independent: ${relative}`);
}
const contractsIndex = fs.readFileSync(path.join(playback, "contracts", "index.ts"), "utf8");
const runtimeIndex = fs.readFileSync(path.join(playback, "runtime", "index.ts"), "utf8");
if (!contractsIndex.includes('export * from "./timeline-effects-animation-contracts"')) throw new Error("Contracts index missing effects contracts export.");
for (const item of ["timeline-keyframe-model", "timeline-animation-track-runtime", "timeline-effect-stack-runtime", "timeline-transition-runtime", "timeline-motion-preset-registry", "timeline-effects-animation-runtime", "timeline-effects-history-bridge"]) {
  if (!runtimeIndex.includes(`export * from "./${item}"`)) throw new Error(`Runtime index missing ${item}.`);
}
console.log("SPRINT 16.8.9 TIMELINE EFFECTS & ANIMATION RUNTIME: PASS");
