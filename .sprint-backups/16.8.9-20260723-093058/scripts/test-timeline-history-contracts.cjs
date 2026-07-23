const fs = require("node:fs");
const path = require("node:path");

const frontendRoot = path.resolve(__dirname, "..");
const playbackRoot = path.join(frontendRoot, "src", "features", "playback");
const contractPath = path.join(playbackRoot, "contracts", "timeline-history-contracts.ts");
const indexPath = path.join(playbackRoot, "contracts", "index.ts");

for (const filePath of [contractPath, indexPath]) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Required file was not found: ${filePath}`);
  }
}

const source = fs.readFileSync(contractPath, "utf8");
const index = fs.readFileSync(indexPath, "utf8");

const required = [
  'TIMELINE_UNDO_REDO_HISTORY_CONTRACT_VERSION = "16.8.8.6"',
  "TimelineHistoryOperationKind",
  "TimelineUndoRedoHistoryStatus",
  "TimelineHistoryConflictCode",
  "TimelineHistoryStatePayload",
  "TimelineHistoryChange",
  "TimelineHistoryEntry",
  "TimelineHistoryTransaction",
  "TimelineHistoryBranch",
  "TimelineHistoryCheckpoint",
  "TimelineHistoryPeekResult",
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
  if (!source.includes(token)) {
    throw new Error(`Missing contract token: ${token}`);
  }
}

if (!index.includes('export * from "./timeline-history-contracts";')) {
  throw new Error("contracts/index.ts does not export timeline history contracts");
}

if (/(?:\bwindow\.|\bdocument\.|\bHTMLElement\b|from ["']react["'])/.test(source)) {
  throw new Error("Contracts must remain framework and DOM independent");
}

console.log("SPRINT 16.8.8.6.1 TIMELINE HISTORY CONTRACTS & TYPES: PASS");
