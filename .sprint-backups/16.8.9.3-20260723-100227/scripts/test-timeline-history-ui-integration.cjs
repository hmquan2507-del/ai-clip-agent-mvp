const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const playback = path.join(root, "src", "features", "playback");
const contracts = fs.readFileSync(path.join(playback, "contracts", "timeline-history-ui-contracts.ts"), "utf8");
const controller = fs.readFileSync(path.join(playback, "runtime", "timeline-history-ui-controller.ts"), "utf8");
const ui = fs.readFileSync(path.join(playback, "ui", "timeline-history-ui.tsx"), "utf8");
const checks = [
  [contracts, ["TimelineHistoryUiState", "TimelineHistoryToastMessage", "TimelineHistoryUiActions"]],
  [controller, ["export class TimelineHistoryUiController", "async undo()", "async redo()", "togglePanel(", "createCheckpoint(", "restoreCheckpoint(", "deleteCheckpoint(", "dismissToast()"]],
  [ui, ["export function TimelineHistoryToolbar", "export function TimelineHistoryPanel", "TimelineCheckpointList", "export function TimelineHistoryToast", "export function TimelineHistoryContextMenu", "aria-live=\"polite\"", "scrollIntoView", "Ctrl"]],
];
for (const [source, symbols] of checks) for (const symbol of symbols) if (!source.includes(symbol)) throw new Error(`Missing timeline history UI capability: ${symbol}`);
if (!fs.readFileSync(path.join(playback, "runtime", "index.ts"), "utf8").includes('export * from "./timeline-history-ui-controller"')) throw new Error("Runtime index does not export UI controller.");
if (!fs.readFileSync(path.join(playback, "contracts", "index.ts"), "utf8").includes('export * from "./timeline-history-ui-contracts"')) throw new Error("Contracts index does not export UI contracts.");
if (!fs.readFileSync(path.join(playback, "index.ts"), "utf8").includes('export * from "./ui"')) throw new Error("Playback index does not export UI components.");
console.log("SPRINT 16.8.8.8 TIMELINE HISTORY UI INTEGRATION: PASS");
