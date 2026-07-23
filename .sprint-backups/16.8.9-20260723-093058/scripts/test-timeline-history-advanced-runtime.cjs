const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const runtimeRoot = path.join(root, "src", "features", "playback", "runtime");
const index = fs.readFileSync(path.join(runtimeRoot, "index.ts"), "utf8");
const files = {
  branch: fs.readFileSync(path.join(runtimeRoot, "timeline-history-branch-manager.ts"), "utf8"),
  merge: fs.readFileSync(path.join(runtimeRoot, "timeline-history-merge-strategy.ts"), "utf8"),
  transaction: fs.readFileSync(path.join(runtimeRoot, "timeline-history-transaction-coordinator.ts"), "utf8"),
};
const checks = [
  [files.branch, ["export class TimelineHistoryBranchManager", "synchronize(", "getLineage(", "findCommonAncestorBranch(", "planSwitch("]],
  [files.merge, ["export class TimelineHistoryMergeStrategy", "static merge", '"reject"', '"prefer-source"', '"prefer-target"', '"latest-wins"', "unresolved-conflicts"]],
  [files.transaction, ["export class TimelineHistoryTransactionCoordinator", "createSavepoint(", "rollbackToSavepoint(", "rollback(", "commit(", "run<", "getSnapshot("]],
];
for (const [source, symbols] of checks) {
  for (const symbol of symbols) if (!source.includes(symbol)) throw new Error(`Missing advanced history capability: ${symbol}`);
  if (/(?:\bwindow\.|\bdocument\.|\bHTMLElement\b|from ["']react["'])/.test(source)) throw new Error("Advanced timeline history runtime must remain framework and DOM independent.");
}
for (const moduleName of ["timeline-history-branch-manager", "timeline-history-merge-strategy", "timeline-history-transaction-coordinator"]) {
  if (!index.includes(`export * from "./${moduleName}"`)) throw new Error(`Runtime index does not export ${moduleName}.`);
}
console.log("SPRINT 16.8.8.6.4 BRANCH MANAGER + MERGE STRATEGY + TRANSACTION COORDINATOR: PASS");
