const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const playback = path.join(root, "src", "features", "playback");
const checks = [
  ["contracts/professional-multi-track-contracts.ts", ["PROFESSIONAL_MULTI_TRACK_CONTRACT_VERSION", "ProfessionalTrackKind", "ProfessionalMultiTrackHistoryPort", "ProfessionalTrackGroup"]],
  ["runtime/professional-track-model.ts", ["export class ProfessionalTrackModel", "static create", "static update", "static withOrder"]],
  ["runtime/professional-track-group-model.ts", ["export class ProfessionalTrackGroupModel", "static create", "static withTracks"]],
  ["runtime/timeline-professional-multi-track-runtime.ts", ["export class TimelineProfessionalMultiTrackRuntime", "async addTrack", "async reorderTrack", "async createGroup", "async assignClip", "audibleTrackIds", "visibleTrackIds", "setHistoryPort"]],
];
for (const [relative, symbols] of checks) {
  const source = fs.readFileSync(path.join(playback, relative), "utf8");
  for (const symbol of symbols) if (!source.includes(symbol)) throw new Error(`Missing 16.9.2 capability: ${relative} -> ${symbol}`);
  if (relative.startsWith("runtime/") && /\b(document|window|HTMLElement|React)\b/.test(source)) throw new Error(`Runtime must remain DOM/React independent: ${relative}`);
}
for (const [relative, symbol] of [
  ["contracts/index.ts", 'export * from "./professional-multi-track-contracts"'],
  ["runtime/index.ts", 'export * from "./timeline-professional-multi-track-runtime"'],
]) if (!fs.readFileSync(path.join(playback, relative), "utf8").includes(symbol)) throw new Error(`Missing export: ${relative}`);
console.log("SPRINT 16.9.2 MULTI TRACK RUNTIME: PASS");
