const fs = require("node:fs");
const path = require("node:path");

const root = process.cwd();
const runtimePath = path.join(root, "src", "features", "playback", "runtime", "timeline-undo-redo-history-runtime.ts");
const indexPath = path.join(root, "src", "features", "playback", "runtime", "index.ts");
const source = fs.readFileSync(runtimePath, "utf8");
const index = fs.readFileSync(indexPath, "utf8");

const required = [
  "export class TimelineUndoRedoHistoryRuntime",
  "configure(",
  "replaceBaseline(",
  "record(",
  "beginTransaction(",
  "appendTransactionChange(",
  "appendTransactionChanges(",
  "commitTransaction(",
  "cancelTransaction(",
  "peekUndo(",
  "peekRedo(",
  "undo(",
  "redo(",
  "clearHistory(",
  "reset(",
  "subscribe(",
  "getSnapshot(",
  "dispose(",
  "TimelineHistoryMergeModel.decide",
  "TimelineHistoryTransactionModel.create",
  "TIMELINE_UNDO_REDO_HISTORY_CONTRACT_VERSION",
];

for (const symbol of required) {
  if (!source.includes(symbol)) throw new Error(`Missing runtime capability: ${symbol}`);
}
if (!index.includes('export * from "./timeline-undo-redo-history-runtime"')) {
  throw new Error("Runtime index does not export timeline undo/redo history runtime.");
}
if (/(?:\bwindow\.|\bdocument\.|\bHTMLElement\b|from ["']react["'])/.test(source)) {
  throw new Error("Timeline undo/redo history runtime must remain framework and DOM independent.");
}
if (!source.includes("this.past.pop()") || !source.includes("this.future.push(entry!)")) {
  throw new Error("Undo stack transition is missing.");
}
if (!source.includes("this.future.pop()") || !source.includes("this.past.push(entry!)")) {
  throw new Error("Redo stack transition is missing.");
}
console.log("SPRINT 16.8.8.6.3 TIMELINE UNDO / REDO RUNTIME: PASS");
