const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const playback = path.join(root, "src", "features", "playback");
const contracts = fs.readFileSync(path.join(playback, "contracts", "timeline-history-integration-contracts.ts"), "utf8");
const runtimeRoot = path.join(playback, "runtime");
const sources = {
  integration: fs.readFileSync(path.join(runtimeRoot, "timeline-history-integration-runtime.ts"), "utf8"),
  keyboard: fs.readFileSync(path.join(runtimeRoot, "timeline-history-keyboard-integration.ts"), "utf8"),
  toolbar: fs.readFileSync(path.join(runtimeRoot, "timeline-history-toolbar-controller.ts"), "utf8"),
  workspace: fs.readFileSync(path.join(runtimeRoot, "timeline-history-workspace-session-bridge.ts"), "utf8"),
  index: fs.readFileSync(path.join(runtimeRoot, "index.ts"), "utf8"),
};
const checks = [
  [contracts, ["TimelineHistoryStateAdapter", "TimelineHistoryCommand", "TimelineHistoryIntegrationSnapshot", "TimelineHistoryKeyboardEventLike"]],
  [sources.integration, ["export class TimelineHistoryIntegrationRuntime", "executeCommand(", "async undo(", "async redo(", "restoreWorkspaceSnapshot(", "saveWorkspace(", "loadWorkspace("]],
  [sources.keyboard, ["export class TimelineHistoryKeyboardIntegration", "handleKeyDown(", "preventDefault()", 'event.key.toLowerCase() !== "z"']],
  [sources.toolbar, ["export class TimelineHistoryToolbarController", "getState(", "undo()", "redo()", "subscribe("]],
  [sources.workspace, ["export class TimelineHistoryWorkspaceSessionBridge", "attach()", "detach()", "isAttached()"]],
];
for (const [source, symbols] of checks) {
  for (const symbol of symbols) if (!source.includes(symbol)) throw new Error(`Missing timeline history integration capability: ${symbol}`);
  if (/from ["']react["']/.test(source)) throw new Error("Timeline history integration must remain framework independent.");
}
for (const moduleName of [
  "timeline-history-integration-runtime",
  "timeline-history-keyboard-integration",
  "timeline-history-toolbar-controller",
  "timeline-history-workspace-session-bridge",
]) if (!sources.index.includes(`export * from "./${moduleName}"`)) throw new Error(`Runtime index does not export ${moduleName}.`);
console.log("SPRINT 16.8.8.7 TIMELINE HISTORY INTEGRATION: PASS");
