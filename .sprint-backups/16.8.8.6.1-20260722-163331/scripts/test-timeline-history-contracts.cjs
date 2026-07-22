const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const contractPath = path.join(root, "src", "features", "playback", "contracts", "timeline-history-contracts.ts");
const indexPath = path.join(root, "playback", "contracts", "index.ts");
const source = fs.readFileSync(contractPath, "utf8");
const index = fs.readFileSync(indexPath, "utf8");

const required = [
  'TIMELINE_UNDO_REDO_HISTORY_CONTRACT_VERSION = "16.8.8.6"',
  "TimelineHistoryOperationKind",
  "TimelineHistoryConflictCode",
  "TimelineHistoryStatePayload",
  "TimelineHistoryChange",
  "TimelineHistoryEntry",
  "TimelineHistoryTransaction",
  "TimelineHistoryCheckpoint",
  "TimelineHistoryRecordResult",
  "TimelineHistoryRestoreResult",
  "TimelineUndoRedoHistorySnapshot",
  "TimelineUndoRedoHistoryConfiguration",
  "RecordTimelineHistoryEntryRequest",
  "BeginTimelineHistoryTransactionRequest",
  "UndoTimelineHistoryRequest",
  "RedoTimelineHistoryRequest",
  "CreateTimelineHistoryCheckpointRequest",
];
for (const token of required) {
  if (!source.includes(token)) throw new Error(`Missing contract token: ${token}`);
}
if (!index.includes('export * from "./timeline-history-contracts";')) {
  throw new Error("contracts/index.ts does not export timeline history contracts");
}
if (/(?:\bwindow\.|\bdocument\.|\bHTMLElement\b|from ["\']react["\'])/.test(source)) {
  throw new Error("Contracts must remain framework and DOM independent");
}
console.log("SPRINT 16.8.8.6.1 TIMELINE HISTORY CONTRACTS & TYPES: PASS");


