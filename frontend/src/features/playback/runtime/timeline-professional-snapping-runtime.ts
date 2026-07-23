import {
  PROFESSIONAL_SNAPPING_CONTRACT_VERSION,
  type ProfessionalMagneticPreview,
  type ProfessionalSnapCandidate,
  type ProfessionalSnapRequest,
  type ProfessionalSnappingConfiguration,
  type ProfessionalSnappingEventType,
  type ProfessionalSnappingHistoryPort,
  type ProfessionalSnappingListener,
  type ProfessionalSnappingSnapshot,
} from "../contracts/professional-snapping-contracts";
import { ProfessionalMagneticTimelineRuntime } from "./professional-magnetic-timeline-runtime";
import { ProfessionalSnapCandidateRuntime } from "./professional-snap-candidate-runtime";
import { ProfessionalSnapDistanceRuntime } from "./professional-snap-distance-runtime";
import { ProfessionalSnappingGuideRuntime } from "./professional-snapping-guide-runtime";

const unique = (values: readonly string[]): readonly string[] => Object.freeze([...new Set(values)]);

export class TimelineProfessionalSnappingRuntime {
  private version = 0;
  private disposed = false;
  private enabled: boolean;
  private candidates: readonly ProfessionalSnapCandidate[] = Object.freeze([]);
  private activePreview: ProfessionalMagneticPreview | null = null;
  private historyPort: ProfessionalSnappingHistoryPort | null = null;
  private readonly listeners = new Set<ProfessionalSnappingListener>();
  private readonly frameRate: number;
  private readonly frameAccurate: boolean;
  private readonly distanceRuntime: ProfessionalSnapDistanceRuntime;
  private readonly guideRuntime = new ProfessionalSnappingGuideRuntime();
  private readonly magneticRuntime = new ProfessionalMagneticTimelineRuntime();

  constructor(configuration: ProfessionalSnappingConfiguration = {}) {
    this.enabled = configuration.enabled ?? true;
    this.frameRate = Math.max(1, configuration.frameRate ?? 30);
    this.frameAccurate = configuration.frameAccurate ?? true;
    this.distanceRuntime = new ProfessionalSnapDistanceRuntime(
      configuration.defaultThresholdPixels ?? 10,
      configuration.defaultThresholdSeconds ?? 0.08,
      configuration.preferSameTrack ?? true,
      configuration.sourcePriorities ?? {},
    );
  }

  initialize(candidates: readonly ProfessionalSnapCandidate[] = []): ProfessionalSnappingSnapshot {
    this.assertUsable();
    this.candidates = ProfessionalSnapCandidateRuntime.normalizeMany(candidates);
    return this.emit("initialized");
  }

  subscribe(listener: ProfessionalSnappingListener): () => void { this.assertUsable(); this.listeners.add(listener); return () => this.listeners.delete(listener); }
  setHistoryPort(port: ProfessionalSnappingHistoryPort | null): void { this.assertUsable(); this.historyPort = port; }

  setEnabled(enabled: boolean): ProfessionalSnappingSnapshot {
    this.assertUsable(); this.enabled = enabled;
    if (!enabled) this.activePreview = null;
    return this.emit("enabled-changed");
  }

  setCandidates(candidates: readonly ProfessionalSnapCandidate[]): ProfessionalSnappingSnapshot {
    this.assertUsable(); this.candidates = ProfessionalSnapCandidateRuntime.normalizeMany(candidates);
    return this.emit("candidates-changed");
  }

  addCandidates(candidates: readonly ProfessionalSnapCandidate[]): ProfessionalSnappingSnapshot {
    return this.setCandidates([...this.candidates, ...candidates]);
  }

  removeCandidates(candidateIds: readonly string[]): ProfessionalSnappingSnapshot {
    const ids = new Set(candidateIds);
    return this.setCandidates(this.candidates.filter(candidate => !ids.has(candidate.candidateId)));
  }

  preview(request: ProfessionalSnapRequest): ProfessionalMagneticPreview {
    this.assertUsable();
    if (!Number.isFinite(request.proposedTime)) throw new Error("Proposed snap time must be finite");
    const originalTime = Math.max(0, request.proposedTime);
    const normalizedRequest: ProfessionalSnapRequest = { ...request, proposedTime: originalTime };
    const eligible = ProfessionalSnapCandidateRuntime.eligible(this.candidates, normalizedRequest);
    const match = !this.enabled || request.forceDisable ? null : this.distanceRuntime.chooseBest(eligible, normalizedRequest);
    const guides = this.guideRuntime.createMany(match);
    this.activePreview = this.magneticRuntime.createPreview(originalTime, match, guides);
    this.emit("preview-updated");
    return this.activePreview;
  }

  clearPreview(): ProfessionalSnappingSnapshot { this.assertUsable(); this.activePreview = null; return this.emit("preview-cleared"); }

  async commit(label = "Snap timeline entity", affectedEntityIds: readonly string[] = []): Promise<ProfessionalSnappingSnapshot> {
    this.assertUsable();
    const before = this.getSnapshot();
    if (!this.activePreview) throw new Error("No snapping preview is active");
    if (this.frameAccurate) {
      const rounded = Math.round(this.activePreview.previewTime * this.frameRate) / this.frameRate;
      this.activePreview = this.magneticRuntime.createPreview(this.activePreview.originalTime, this.activePreview.match ? Object.freeze({ ...this.activePreview.match, snappedTime: rounded, deltaSeconds: rounded - this.activePreview.originalTime }) : null, this.activePreview.guides.map(guide => Object.freeze({ ...guide, time: rounded, deltaSeconds: rounded - this.activePreview!.originalTime })));
    }
    const after = this.emit("snap-committed");
    if (this.historyPort) await this.historyPort.commitSnappingMutation({ label, before, after, affectedEntityIds: unique(affectedEntityIds) });
    return after;
  }

  restore(snapshot: ProfessionalSnappingSnapshot): ProfessionalSnappingSnapshot {
    this.assertUsable();
    if (snapshot.contractVersion !== PROFESSIONAL_SNAPPING_CONTRACT_VERSION) throw new Error("Unsupported professional snapping snapshot version");
    this.enabled = snapshot.enabled;
    this.candidates = ProfessionalSnapCandidateRuntime.normalizeMany(snapshot.candidates);
    this.activePreview = snapshot.activePreview;
    return this.emit("state-restored");
  }

  reset(): ProfessionalSnappingSnapshot { this.assertUsable(); this.enabled = true; this.candidates = Object.freeze([]); this.activePreview = null; return this.emit("reset"); }
  dispose(): void { if (this.disposed) return; this.disposed = true; this.version++; const snapshot = this.getSnapshot(); for (const listener of this.listeners) listener({ type: "disposed", snapshot }); this.listeners.clear(); }

  getSnapshot(): ProfessionalSnappingSnapshot {
    return Object.freeze({ contractVersion: PROFESSIONAL_SNAPPING_CONTRACT_VERSION, version: this.version, disposed: this.disposed, enabled: this.enabled, candidateCount: this.candidates.length, candidates: Object.freeze([...this.candidates]), activePreview: this.activePreview });
  }

  private emit(type: ProfessionalSnappingEventType): ProfessionalSnappingSnapshot { this.version++; const snapshot = this.getSnapshot(); for (const listener of this.listeners) listener({ type, snapshot }); return snapshot; }
  private assertUsable(): void { if (this.disposed) throw new Error("TimelineProfessionalSnappingRuntime is disposed"); }
}

export const createTimelineProfessionalSnappingRuntime = (configuration: ProfessionalSnappingConfiguration = {}) => new TimelineProfessionalSnappingRuntime(configuration);
