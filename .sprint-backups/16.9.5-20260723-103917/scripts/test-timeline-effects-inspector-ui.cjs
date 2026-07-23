const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const playback = path.join(root, "src", "features", "playback");
const checks = [
  ["contracts/timeline-effects-inspector-contracts.ts", ["TimelineInspectorPropertyDescriptor", "TimelineInspectorEffectCatalogItem", "TimelineInspectorTransitionCatalogItem"]],
  ["runtime/timeline-effects-inspector-controller.ts", ["export class TimelineEffectsInspectorController", "getPropertyDescriptors", "getEffectCatalog", "getTransitionCatalog", "clamp("]],
  ["ui/timeline-effects-inspector-ui.tsx", ["export function TimelineEffectsAnimationInspector", "Transform & keyframes", "Motion presets", "Effect browser", "Effect stack", "Transitions", "Add keyframe", "Add transition"]],
];
for (const [relative, symbols] of checks) {
  const source = fs.readFileSync(path.join(playback, relative), "utf8");
  for (const symbol of symbols) if (!source.includes(symbol)) throw new Error(`Missing inspector UI capability: ${relative} -> ${symbol}`);
}
const runtime = fs.readFileSync(path.join(playback, "runtime", "timeline-effects-inspector-controller.ts"), "utf8");
if (/\b(document|window|HTMLElement|React)\b/.test(runtime)) throw new Error("Inspector controller must remain DOM and React independent.");
const exportChecks = [
  ["contracts/index.ts", 'export * from "./timeline-effects-inspector-contracts"'],
  ["runtime/index.ts", 'export * from "./timeline-effects-inspector-controller"'],
  ["ui/index.ts", 'export * from "./timeline-effects-inspector-ui"'],
];
for (const [relative, symbol] of exportChecks) if (!fs.readFileSync(path.join(playback, relative), "utf8").includes(symbol)) throw new Error(`Missing export: ${relative}`);
console.log("SPRINT 16.8.9.2 EFFECTS & ANIMATION INSPECTOR UI: PASS");
