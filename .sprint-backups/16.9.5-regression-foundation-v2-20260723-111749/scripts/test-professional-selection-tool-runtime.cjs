const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const playback = path.join(root, "src", "features", "playback");
const checks = [
  ["contracts/professional-selection-tool-contracts.ts", ["PROFESSIONAL_SELECTION_TOOL_CONTRACT_VERSION", "ProfessionalTimelineTool", "ProfessionalSelectionMode", "ProfessionalSelectionHistoryPort", "TimelineSelectableBounds"]],
  ["runtime/professional-selection-model.ts", ["export class ProfessionalSelectionModel", "static apply", "static rectangle", "static hitTest"]],
  ["runtime/timeline-professional-selection-tool-runtime.ts", ["export class TimelineProfessionalSelectionToolRuntime", "async setTool", "async selectMany", "async selectTrack", "async selectGroup", "startMarquee", "commitMarquee", "selectTimeRange", "setHistoryPort"]],
];
for (const [relative, symbols] of checks) {
  const source = fs.readFileSync(path.join(playback, relative), "utf8");
  for (const symbol of symbols) if (!source.includes(symbol)) throw new Error(`Missing 16.9.3 capability: ${relative} -> ${symbol}`);
  if (relative.startsWith("runtime/") && /\b(document|window|HTMLElement|React)\b/.test(source)) throw new Error(`Runtime must remain DOM/React independent: ${relative}`);
}
for (const [relative, symbol] of [
  ["contracts/index.ts", 'export * from "./professional-selection-tool-contracts"'],
  ["runtime/index.ts", 'export * from "./timeline-professional-selection-tool-runtime"'],
]) if (!fs.readFileSync(path.join(playback, relative), "utf8").includes(symbol)) throw new Error(`Missing export: ${relative}`);
console.log("SPRINT 16.9.3 PROFESSIONAL SELECTION TOOL RUNTIME: PASS");
