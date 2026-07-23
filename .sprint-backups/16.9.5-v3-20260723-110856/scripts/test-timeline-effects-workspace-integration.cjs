const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const playback = path.join(root, "src", "features", "playback");
const checks = [
  ["contracts/timeline-effects-workspace-contracts.ts", ["TimelineEffectsWorkspaceSelectionPort", "TimelineEffectsWorkspacePlayheadPort", "TimelineEffectsPreviewPort", "TimelineEffectsWorkspaceState"]],
  ["runtime/timeline-effects-workspace-controller.ts", ["export class TimelineEffectsWorkspaceController", "attach(", "addKeyframe(", "addEffect(", "applyPreset(", "refreshPreview(", "TimelineEffectsHistoryBridge"]],
  ["adapters/html-timeline-effects-preview-adapter.ts", ["export class HtmlTimelineEffectsPreviewAdapter", "applyFrame(", "style.transform", "style.filter", "style.opacity"]],
  ["ui/timeline-effects-workspace-ui.tsx", ["export function TimelineEffectsInspector", "Motion presets", "Effect stack", "Add keyframe", "TimelineEffectsWorkspaceStatusBar"]],
];
for (const [relative, symbols] of checks) {
  const source = fs.readFileSync(path.join(playback, relative), "utf8");
  for (const symbol of symbols) if (!source.includes(symbol)) throw new Error(`Missing workspace integration capability: ${relative} -> ${symbol}`);
}
const runtime = fs.readFileSync(path.join(playback, "runtime", "timeline-effects-workspace-controller.ts"), "utf8");
if (/\b(document|window|HTMLElement|React)\b/.test(runtime)) throw new Error("Workspace controller must remain DOM and React independent.");
const exportChecks = [
  ["contracts/index.ts", 'export * from "./timeline-effects-workspace-contracts"'],
  ["runtime/index.ts", 'export * from "./timeline-effects-workspace-controller"'],
  ["adapters/index.ts", 'export * from "./html-timeline-effects-preview-adapter"'],
  ["ui/index.ts", 'export * from "./timeline-effects-workspace-ui"'],
];
for (const [relative, symbol] of exportChecks) if (!fs.readFileSync(path.join(playback, relative), "utf8").includes(symbol)) throw new Error(`Missing export: ${relative}`);
console.log("SPRINT 16.8.9.1 EFFECTS & ANIMATION WORKSPACE INTEGRATION: PASS");
