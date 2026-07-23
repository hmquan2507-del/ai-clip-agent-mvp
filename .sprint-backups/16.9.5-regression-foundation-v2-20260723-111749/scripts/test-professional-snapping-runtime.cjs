const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const playback = path.join(root, "src", "features", "playback");
const checks = [
  ["contracts/professional-snapping-contracts.ts", ["PROFESSIONAL_SNAPPING_CONTRACT_VERSION", "ProfessionalSnapCandidate", "ProfessionalSnapRequest", "ProfessionalSnapGuide", "ProfessionalSnappingHistoryPort"]],
  ["runtime/professional-snap-candidate-runtime.ts", ["export class ProfessionalSnapCandidateRuntime", "static normalizeMany", "static eligible"]],
  ["runtime/professional-snap-distance-runtime.ts", ["export class ProfessionalSnapDistanceRuntime", "evaluate", "chooseBest"]],
  ["runtime/professional-snapping-guide-runtime.ts", ["export class ProfessionalSnappingGuideRuntime", "createMany"]],
  ["runtime/professional-magnetic-timeline-runtime.ts", ["export class ProfessionalMagneticTimelineRuntime", "createPreview"]],
  ["runtime/timeline-professional-snapping-runtime.ts", ["export class TimelineProfessionalSnappingRuntime", "setCandidates", "preview", "clearPreview", "async commit", "setHistoryPort", "restore"]],
];
for (const [relative, symbols] of checks) {
  const source = fs.readFileSync(path.join(playback, relative), "utf8");
  for (const symbol of symbols) if (!source.includes(symbol)) throw new Error(`Missing 16.9.4 capability: ${relative} -> ${symbol}`);
  if (relative.startsWith("runtime/") && /\b(document|window|HTMLElement|React)\b/.test(source)) throw new Error(`Runtime must remain DOM/React independent: ${relative}`);
}
for (const [relative, symbol] of [
  ["contracts/index.ts", 'export * from "./professional-snapping-contracts"'],
  ["runtime/index.ts", 'export * from "./timeline-professional-snapping-runtime"'],
]) if (!fs.readFileSync(path.join(playback, relative), "utf8").includes(symbol)) throw new Error(`Missing export: ${relative}`);
console.log("SPRINT 16.9.4 PROFESSIONAL SNAPPING RUNTIME: PASS");
