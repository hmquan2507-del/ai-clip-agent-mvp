import { PROFESSIONAL_TRIM_CONTRACT_VERSION, type ProfessionalTrimBeginRequest, type ProfessionalTrimCommitResult, type ProfessionalTrimConfiguration, type ProfessionalTrimHistoryPort, type ProfessionalTrimListener, type ProfessionalTrimPosition, type ProfessionalTrimPreview, type ProfessionalTrimSnapshot } from "../contracts/professional-trim-contracts";
import { ProfessionalTrimCalculator } from "./professional-trim-calculator";
import { TimelineGapModel } from "./timeline-gap-model";

type Configuration = Required<Omit<ProfessionalTrimConfiguration, "timelineEndFrame">> & { readonly timelineEndFrame: number | null };
const freezePositions = (items: readonly ProfessionalTrimPosition[]): readonly ProfessionalTrimPosition[] => Object.freeze(items.map((item) => Object.freeze({ ...item })));

export class TimelineProfessionalTrimEngine {
  private readonly configuration: Configuration;
  private version = 0;
  private status: ProfessionalTrimSnapshot["status"] = "idle";
  private request: ProfessionalTrimBeginRequest | null = null;
  private origin: readonly ProfessionalTrimPosition[] = Object.freeze([]);
  private preview: ProfessionalTrimPreview | null = null;
  private lastCommit: ProfessionalTrimCommitResult | null = null;
  private historyPort: ProfessionalTrimHistoryPort | null = null;
  private readonly listeners = new Set<ProfessionalTrimListener>();

  constructor(configuration: ProfessionalTrimConfiguration) {
    if (!Number.isFinite(configuration.framesPerSecond) || configuration.framesPerSecond <= 0) throw new Error("framesPerSecond must be greater than zero");
    this.configuration = Object.freeze({ framesPerSecond: configuration.framesPerSecond, minimumDurationFrames: Math.max(1, Math.round(configuration.minimumDurationFrames ?? 1)), timelineStartFrame: Math.round(configuration.timelineStartFrame ?? 0), timelineEndFrame: configuration.timelineEndFrame == null ? null : Math.round(configuration.timelineEndFrame), magneticTimeline: configuration.magneticTimeline ?? true, autoCloseGaps: configuration.autoCloseGaps ?? true, blockOnLockedClip: configuration.blockOnLockedClip ?? true });
  }

  setHistoryPort(port: ProfessionalTrimHistoryPort | null): ProfessionalTrimSnapshot { this.assertUsable(); this.historyPort = port; return this.emit(); }

  begin(request: ProfessionalTrimBeginRequest): ProfessionalTrimSnapshot {
    this.assertUsable();
    this.request = Object.freeze({ ...request, clips: Object.freeze(request.clips.map((clip) => Object.freeze({ ...clip }))), secondaryClipId: request.secondaryClipId ?? null });
    this.origin = freezePositions(request.clips.map((clip) => ({ ...clip, shiftedByFrames: 0 })));
    this.preview = null; this.lastCommit = null; this.status = "editing";
    return this.emit();
  }

  previewFrames(deltaFrames: number): ProfessionalTrimSnapshot {
    if (!this.request) throw new Error("Professional trim session has not started");
    const calculation = ProfessionalTrimCalculator.calculate(this.request.clips, this.request.mode, this.request.activeClipId, this.request.secondaryClipId ?? null, deltaFrames, this.configuration);
    let positions = calculation.positions;
    let gaps = TimelineGapModel.detect(positions);
    if (this.configuration.magneticTimeline && this.configuration.autoCloseGaps && this.request.mode !== "ripple-start") {
      const activeTrack = this.request.clips.find((clip) => clip.clipId === this.request!.activeClipId)?.trackId;
      const relevant = gaps.filter((gap) => gap.trackId === activeTrack && gap.previousClipId === this.request!.activeClipId);
      for (const gap of relevant) positions = freezePositions(positions.map((item) => item.trackId === gap.trackId && item.timelineStartFrame >= gap.endFrame ? { ...item, timelineStartFrame: item.timelineStartFrame - gap.durationFrames, timelineEndFrame: item.timelineEndFrame - gap.durationFrames, shiftedByFrames: item.shiftedByFrames - gap.durationFrames } : item));
      gaps = TimelineGapModel.detect(positions);
    }
    this.preview = Object.freeze({ requestedDeltaFrames: Math.round(deltaFrames), resolvedDeltaFrames: calculation.resolvedDeltaFrames, positions: freezePositions(positions), gaps, conflicts: calculation.conflicts, blocked: calculation.conflicts.some((item) => item.blocking) });
    this.status = this.preview.blocked ? "blocked" : "editing";
    return this.emit();
  }

  async commit(): Promise<ProfessionalTrimSnapshot> {
    if (!this.request || !this.preview) throw new Error("Professional trim preview is required before commit");
    if (this.preview.blocked) throw new Error("Professional trim is blocked");
    const affectedClipIds = this.preview.positions.filter((item, index) => JSON.stringify(item) !== JSON.stringify(this.origin[index])).map((item) => item.clipId);
    const originalGaps = TimelineGapModel.detect(this.origin);
    const previewGapIds = new Set(this.preview.gaps.map((gap) => gap.gapId));
    this.lastCommit = Object.freeze({ sessionId: this.request.sessionId, mode: this.request.mode, positions: this.preview.positions, affectedClipIds: Object.freeze(affectedClipIds), resolvedDeltaFrames: this.preview.resolvedDeltaFrames, autoClosedGapIds: Object.freeze(originalGaps.filter((gap) => !previewGapIds.has(gap.gapId)).map((gap) => gap.gapId)) });
    if (this.historyPort) await this.historyPort.commitTrim({ label: `Professional ${this.request.mode} trim`, before: this.origin, after: this.preview.positions, affectedClipIds });
    this.status = "committed";
    return this.emit();
  }

  cancel(): ProfessionalTrimSnapshot { this.assertUsable(); this.status = "cancelled"; this.preview = null; this.lastCommit = null; return this.emit(); }
  reset(): ProfessionalTrimSnapshot { this.assertUsable(); this.status = "idle"; this.request = null; this.origin = Object.freeze([]); this.preview = null; this.lastCommit = null; return this.emit(); }
  subscribe(listener: ProfessionalTrimListener): () => void { this.assertUsable(); this.listeners.add(listener); return () => this.listeners.delete(listener); }
  dispose(): void { if (this.status === "disposed") return; this.status = "disposed"; this.emit(); this.listeners.clear(); }
  getSnapshot(): ProfessionalTrimSnapshot { return Object.freeze({ contractVersion: PROFESSIONAL_TRIM_CONTRACT_VERSION, version: this.version, status: this.status, sessionId: this.request?.sessionId ?? null, mode: this.request?.mode ?? null, activeClipId: this.request?.activeClipId ?? null, secondaryClipId: this.request?.secondaryClipId ?? null, origin: freezePositions(this.origin), preview: this.preview, lastCommit: this.lastCommit }); }
  private emit(): ProfessionalTrimSnapshot { this.version += 1; const snapshot = this.getSnapshot(); for (const listener of this.listeners) listener(snapshot); return snapshot; }
  private assertUsable(): void { if (this.status === "disposed") throw new Error("TimelineProfessionalTrimEngine is disposed"); }
}

export const createTimelineProfessionalTrimEngine = (configuration: ProfessionalTrimConfiguration): TimelineProfessionalTrimEngine => new TimelineProfessionalTrimEngine(configuration);
