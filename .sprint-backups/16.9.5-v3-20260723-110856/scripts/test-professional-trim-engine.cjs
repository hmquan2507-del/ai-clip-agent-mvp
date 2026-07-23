const fs = require("node:fs");
const path = require("node:path");
const root = process.cwd();
const playback = path.join(root, "src", "features", "playback");
const checks = [
  ["contracts/professional-trim-contracts.ts", ["ProfessionalTrimMode", "ProfessionalTrimHistoryPort", "TimelineGap"]],
  ["runtime/timeline-gap-model.ts", ["export class TimelineGapModel", "static detect"]],
  ["runtime/professional-trim-calculator.ts", ["export class ProfessionalTrimCalculator", 'mode === "roll"', 'mode === "slip"', 'mode === "slide"']],
  ["runtime/timeline-professional-trim-engine.ts", ["export class TimelineProfessionalTrimEngine", "previewFrames", "async commit", "autoCloseGaps", "setHistoryPort"]],
];
for (const [relative, symbols] of checks) {
  const source = fs.readFileSync(path.join(playback, relative), "utf8");
  for (const symbol of symbols) if (!source.includes(symbol)) throw new Error(`Missing 16.9.1 capability: ${relative} -> ${symbol}`);
  if (relative.startsWith("runtime/") && /\b(document|window|HTMLElement|React)\b/.test(source)) throw new Error(`Runtime must remain DOM/React independent: ${relative}`);
}
for (const [relative, symbol] of [["contracts/index.ts", 'export * from "./professional-trim-contracts"'], ["runtime/index.ts", 'export * from "./timeline-professional-trim-engine"']]) if (!fs.readFileSync(path.join(playback, relative), "utf8").includes(symbol)) throw new Error(`Missing export: ${relative}`);
console.log("SPRINT 16.9.1 PROFESSIONAL TRIM ENGINE: PASS");
