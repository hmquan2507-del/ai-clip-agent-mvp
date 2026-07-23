const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const runtimeRoot = path.join(root, "src", "features", "playback", "runtime");
const index = fs.readFileSync(path.join(runtimeRoot, "index.ts"), "utf8");
const files = {
  checkpoint: fs.readFileSync(path.join(runtimeRoot, "timeline-history-checkpoint-manager.ts"), "utf8"),
  persistence: fs.readFileSync(path.join(runtimeRoot, "timeline-history-snapshot-persistence.ts"), "utf8"),
  restore: fs.readFileSync(path.join(runtimeRoot, "timeline-history-restore-runtime.ts"), "utf8"),
};
const checks = [
  [files.checkpoint, ["export class TimelineHistoryCheckpointManager", "createFromSnapshot(", "maybeCreateAutomatic(", "remove(", "getLatest(", "clear("]],
  [files.persistence, ["export class TimelineHistorySnapshotPersistence", "serialize(", "deserialize(", "async save(", "async load(", "checksum", "schemaVersion"]],
  [files.restore, ["export class TimelineHistoryRestoreRuntime", "restoreCheckpoint(", "restoreLatest(", "restoreSnapshot("]],
];
for (const [source, symbols] of checks) {
  for (const symbol of symbols) if (!source.includes(symbol)) throw new Error(`Missing checkpoint/persistence capability: ${symbol}`);
  if (/(?:\bwindow\.|\bdocument\.|\bHTMLElement\b|from ["']react["'])/.test(source)) throw new Error("Timeline history checkpoint runtime must remain framework and DOM independent.");
}
for (const moduleName of ["timeline-history-checkpoint-manager", "timeline-history-snapshot-persistence", "timeline-history-restore-runtime"]) {
  if (!index.includes(`export * from "./${moduleName}"`)) throw new Error(`Runtime index does not export ${moduleName}.`);
}
console.log("SPRINT 16.8.8.6.5 CHECKPOINT + SNAPSHOT PERSISTENCE + FULL REGRESSION: PASS");
