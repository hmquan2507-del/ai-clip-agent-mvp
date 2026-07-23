const fs = require("node:fs");
const path = require("node:path");

const frontendRoot = path.resolve(__dirname, "..");
const runtimeRoot = path.join(frontendRoot, "src", "features", "playback", "runtime");
const contractsRoot = path.join(frontendRoot, "src", "features", "playback", "contracts");
const files = {
  entry: path.join(runtimeRoot, "timeline-history-entry-model.ts"),
  transaction: path.join(runtimeRoot, "timeline-history-transaction-model.ts"),
  checkpoint: path.join(runtimeRoot, "timeline-history-checkpoint-model.ts"),
  merge: path.join(runtimeRoot, "timeline-history-merge-model.ts"),
  runtimeIndex: path.join(runtimeRoot, "index.ts"),
  contracts: path.join(contractsRoot, "timeline-history-contracts.ts"),
};

for (const [name, filePath] of Object.entries(files)) {
  if (!fs.existsSync(filePath)) throw new Error(`Missing ${name} file: ${filePath}`);
}

const sources = Object.fromEntries(Object.entries(files).map(([name, filePath]) => [name, fs.readFileSync(filePath, "utf8")]));
const expectations = {
  entry: ["class TimelineHistoryEntryModel", "normalizeChanges", "cloneState", "static create", "static replace"],
  transaction: ["class TimelineHistoryTransactionModel", "static create", "static append", "static commit"],
  checkpoint: ["class TimelineHistoryCheckpointModel", "static create", "static sort", "static enforceCapacity"],
  merge: ["class TimelineHistoryMergeModel", "static decide", "merge-key-mismatch", "state-version-not-contiguous", "checksum-not-contiguous"],
};
for (const [name, tokens] of Object.entries(expectations)) {
  for (const token of tokens) if (!sources[name].includes(token)) throw new Error(`${name} model is missing token: ${token}`);
}

for (const exportName of [
  "timeline-history-entry-model",
  "timeline-history-transaction-model",
  "timeline-history-checkpoint-model",
  "timeline-history-merge-model",
]) {
  if (!sources.runtimeIndex.includes(`export * from "./${exportName}";`)) throw new Error(`runtime/index.ts does not export ${exportName}`);
}

if (!sources.contracts.includes("TimelineHistoryMergeDecision<TState = TimelineHistoryJsonValue>")) {
  throw new Error("TimelineHistoryMergeDecision must preserve generic state type.");
}

const allModelSource = [sources.entry, sources.transaction, sources.checkpoint, sources.merge].join("\n");
if (/(?:\bwindow\.|\bdocument\.|\bHTMLElement\b|from ["']react["'])/.test(allModelSource)) {
  throw new Error("History models must remain framework and DOM independent.");
}
if (!allModelSource.includes("Object.freeze")) throw new Error("History models must produce immutable values.");

console.log("SPRINT 16.8.8.6.2 TIMELINE HISTORY MODELS: PASS");
