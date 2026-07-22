import {
  TIMELINE_SLIP_SLIDE_EDIT_CONTRACT_VERSION,
  type BeginTimelineSlideRequest,
  type BeginTimelineSlipRequest,
  type PreviewSlideWithSnapRequest,
  type SlipSlideClipPosition,
  type SlipSlideConflict,
  type SlipSlideTimelineClip,
  type TimelineSlipSlideCommitResult,
  type TimelineSlipSlideConfiguration,
  type TimelineSlipSlideEventType,
  type TimelineSlipSlideListener,
  type TimelineSlipSlideSession,
  type TimelineSlipSlideSnapshot,
} from "../contracts/slip-slide-edit-contracts";
import { SlipPreviewModel } from "./slip-preview-model";
import { SlidePreviewModel, type SlideSnapProjection } from "./slide-preview-model";

type NormalizedConfiguration = Required<Omit<TimelineSlipSlideConfiguration, "timelineEndFrame">> & { readonly timelineEndFrame: number | null };
const freezeConflicts = (items: readonly SlipSlideConflict[]): readonly SlipSlideConflict[] => Object.freeze(items.map((item) => Object.freeze({ ...item })));
const freezePositions = (items: readonly SlipSlideClipPosition[]): readonly SlipSlideClipPosition[] => Object.freeze(items.map((item) => Object.freeze({ ...item })));

export class TimelineSlipSlideEditRuntime {
  private configuration: NormalizedConfiguration;
  private version = 0;
  private status: TimelineSlipSlideSnapshot["status"] = "idle";
  private session: TimelineSlipSlideSession | null = null;
  private activeClip: SlipSlideTimelineClip | null = null;
  private previousClip: SlipSlideTimelineClip | null = null;
  private nextClip: SlipSlideTimelineClip | null = null;
  private slipPreview: TimelineSlipSlideSnapshot["slipPreview"] = null;
  private slidePreview: TimelineSlipSlideSnapshot["slidePreview"] = null;
  private lastCommit: TimelineSlipSlideCommitResult | null = null;
  private conflicts: readonly SlipSlideConflict[] = Object.freeze([]);
  private readonly listeners = new Set<TimelineSlipSlideListener>();

  constructor(configuration: TimelineSlipSlideConfiguration) {
    this.configuration = this.normalizeConfiguration(configuration);
  }

  configure(configuration: Partial<TimelineSlipSlideConfiguration>): TimelineSlipSlideSnapshot {
    this.assertUsable();
    this.configuration = this.normalizeConfiguration({ ...this.configuration, ...configuration });
    return this.emit("configured");
  }

  beginSlipEdit(request: BeginTimelineSlipRequest): TimelineSlipSlideSnapshot {
    this.assertUsable();
    if (this.session) return this.getSnapshot();
    const clip = SlipPreviewModel.normalizeClip(request.clip);
    const conflicts = SlipPreviewModel.beginConflicts(clip, this.configuration);
    this.activeClip = clip; this.previousClip = null; this.nextClip = null;
    this.session = Object.freeze({ sessionId: request.sessionId, operation: "slip", activeClipId: clip.clipId, previousClipId: null, nextClipId: null, startedAtVersion: this.version });
    this.slipPreview = null; this.slidePreview = null; this.lastCommit = null; this.conflicts = freezeConflicts(conflicts);
    this.status = conflicts.some((item) => item.blocking) ? "blocked" : "editing";
    return this.emit(this.status === "blocked" ? "edit_blocked" : "slip_started");
  }

  beginSlideEdit(request: BeginTimelineSlideRequest): TimelineSlipSlideSnapshot {
    this.assertUsable();
    if (this.session) return this.getSnapshot();
    const active = SlipPreviewModel.normalizeClip(request.activeClip);
    const previous = request.previousClip ? SlipPreviewModel.normalizeClip(request.previousClip) : null;
    const next = request.nextClip ? SlipPreviewModel.normalizeClip(request.nextClip) : null;
    const conflicts = SlidePreviewModel.beginConflicts(previous, active, next, this.configuration);
    this.activeClip = active; this.previousClip = previous; this.nextClip = next;
    this.session = Object.freeze({ sessionId: request.sessionId, operation: "slide", activeClipId: active.clipId, previousClipId: previous?.clipId ?? null, nextClipId: next?.clipId ?? null, startedAtVersion: this.version });
    this.slipPreview = null; this.slidePreview = null; this.lastCommit = null; this.conflicts = freezeConflicts(conflicts);
    this.status = conflicts.some((item) => item.blocking) ? "blocked" : "editing";
    return this.emit(this.status === "blocked" ? "edit_blocked" : "slide_started");
  }

  previewSlipFrames(deltaFrames: number): TimelineSlipSlideSnapshot {
    this.assertSession("slip");
    if (!this.activeClip) return this.getSnapshot();
    const preview = SlipPreviewModel.calculate(this.activeClip, deltaFrames, this.configuration);
    if (this.slipPreview && JSON.stringify(this.slipPreview) === JSON.stringify(preview)) return this.getSnapshot();
    this.slipPreview = preview; this.slidePreview = null; this.conflicts = freezeConflicts(preview.conflicts);
    this.status = preview.blocked ? "blocked" : "previewing";
    return this.emit(preview.blocked ? "edit_blocked" : "slip_preview_updated");
  }

  previewSlipTime(deltaSeconds: number): TimelineSlipSlideSnapshot {
    return this.previewSlipFrames(deltaSeconds * this.configuration.framesPerSecond);
  }

  previewSlideFrames(deltaFrames: number): TimelineSlipSlideSnapshot {
    return this.calculateSlide(deltaFrames);
  }

  previewSlideTime(deltaSeconds: number): TimelineSlipSlideSnapshot {
    return this.previewSlideFrames(deltaSeconds * this.configuration.framesPerSecond);
  }

  previewSlideWithSnap(request: PreviewSlideWithSnapRequest): TimelineSlipSlideSnapshot {
    this.assertSession("slide");
    if (!this.activeClip) return this.getSnapshot();
    const normalized = Number.isFinite(request.deltaFrames) ? Math.round(request.deltaFrames) : request.deltaFrames;
    const snap: SlideSnapProjection = this.configuration.magneticSnapEnabled
      ? request.resolver.resolveSlideDelta({ activeClip: this.activeClip, requestedDeltaFrames: normalized, excludedOwnerIds: Object.freeze([this.activeClip.clipId, this.previousClip?.clipId ?? "", this.nextClip?.clipId ?? ""].filter(Boolean)) })
      : { resolvedDeltaFrames: normalized, snapped: false, targetId: null, targetFrame: null };
    return this.calculateSlide(request.deltaFrames, snap);
  }

  commitEdit(): TimelineSlipSlideSnapshot {
    this.assertUsable();
    if (!this.session) throw new Error("TimelineSlipSlideEditRuntime has no active session");
    if (this.status === "blocked") throw new Error("TimelineSlipSlideEditRuntime is blocked");
    let positions: readonly SlipSlideClipPosition[];
    let requestedDeltaFrames: number;
    let resolvedDeltaFrames: number;
    let previewConflicts: readonly SlipSlideConflict[];
    if (this.session.operation === "slip") {
      if (!this.slipPreview) throw new Error("TimelineSlipSlideEditRuntime has no preview");
      positions = [this.slipPreview.preview];
      requestedDeltaFrames = this.slipPreview.requestedDeltaFrames;
      resolvedDeltaFrames = this.slipPreview.resolvedDeltaFrames;
      previewConflicts = this.slipPreview.conflicts;
    } else {
      if (!this.slidePreview) throw new Error("TimelineSlipSlideEditRuntime has no preview");
      positions = [this.slidePreview.previousPreview, this.slidePreview.activePreview, this.slidePreview.nextPreview];
      requestedDeltaFrames = this.slidePreview.requestedDeltaFrames;
      resolvedDeltaFrames = this.slidePreview.resolvedDeltaFrames;
      previewConflicts = this.slidePreview.conflicts;
    }
    this.lastCommit = Object.freeze({ sessionId: this.session.sessionId, operation: this.session.operation, committed: true, positions: freezePositions(positions), requestedDeltaFrames, resolvedDeltaFrames, conflicts: freezeConflicts(previewConflicts) });
    this.status = "committed";
    return this.emit("edit_committed");
  }

  cancelEdit(): TimelineSlipSlideSnapshot {
    this.assertUsable();
    if (!this.session) return this.getSnapshot();
    this.status = "cancelled"; this.slipPreview = null; this.slidePreview = null; this.conflicts = Object.freeze([]); this.lastCommit = null;
    const snapshot = this.emit("edit_cancelled");
    this.session = null; this.activeClip = null; this.previousClip = null; this.nextClip = null;
    return snapshot;
  }

  subscribe(listener: TimelineSlipSlideListener): () => void {
    this.assertUsable(); this.listeners.add(listener); return () => this.listeners.delete(listener);
  }

  getSnapshot(): TimelineSlipSlideSnapshot {
    return Object.freeze({
      contractVersion: TIMELINE_SLIP_SLIDE_EDIT_CONTRACT_VERSION,
      version: this.version, status: this.status, configured: true,
      session: this.session ? Object.freeze({ ...this.session }) : null,
      slipPreview: this.slipPreview,
      slidePreview: this.slidePreview,
      lastCommit: this.lastCommit,
      conflicts: freezeConflicts(this.conflicts),
    });
  }

  snapshot(): TimelineSlipSlideSnapshot { return this.getSnapshot(); }

  reset(): TimelineSlipSlideSnapshot {
    this.assertUsable();
    if (this.status === "idle" && !this.session && !this.lastCommit && this.conflicts.length === 0) return this.getSnapshot();
    this.status = "idle"; this.session = null; this.activeClip = null; this.previousClip = null; this.nextClip = null; this.slipPreview = null; this.slidePreview = null; this.lastCommit = null; this.conflicts = Object.freeze([]);
    return this.emit("reset");
  }

  dispose(): TimelineSlipSlideSnapshot {
    if (this.status === "disposed") return this.getSnapshot();
    this.status = "disposed"; const snapshot = this.emit("disposed"); this.listeners.clear(); return snapshot;
  }

  private calculateSlide(deltaFrames: number, snap?: SlideSnapProjection): TimelineSlipSlideSnapshot {
    this.assertSession("slide");
    if (!this.previousClip || !this.activeClip || !this.nextClip) return this.getSnapshot();
    const preview = SlidePreviewModel.calculate(this.previousClip, this.activeClip, this.nextClip, deltaFrames, this.configuration, snap);
    if (this.slidePreview && JSON.stringify(this.slidePreview) === JSON.stringify(preview)) return this.getSnapshot();
    this.slidePreview = preview; this.slipPreview = null; this.conflicts = freezeConflicts(preview.conflicts); this.status = preview.blocked ? "blocked" : "previewing";
    return this.emit(preview.blocked ? "edit_blocked" : snap?.snapped ? "slide_snap_applied" : "slide_preview_updated");
  }

  private normalizeConfiguration(configuration: TimelineSlipSlideConfiguration): NormalizedConfiguration {
    if (!Number.isFinite(configuration.framesPerSecond) || configuration.framesPerSecond <= 0) throw new Error("framesPerSecond must be greater than zero");
    const minimumClipDurationFrames = Math.max(1, Math.round(configuration.minimumClipDurationFrames ?? 1));
    const timelineStartFrame = Math.round(configuration.timelineStartFrame ?? 0);
    const timelineEndFrame = configuration.timelineEndFrame == null ? null : Math.round(configuration.timelineEndFrame);
    if (timelineEndFrame !== null && timelineEndFrame <= timelineStartFrame) throw new Error("timelineEndFrame must be greater than timelineStartFrame");
    return Object.freeze({ framesPerSecond: configuration.framesPerSecond, minimumClipDurationFrames, timelineStartFrame, timelineEndFrame, requireContiguousNeighbors: configuration.requireContiguousNeighbors ?? true, blockOnLockedClip: configuration.blockOnLockedClip ?? true, clampPreviewToValidRange: configuration.clampPreviewToValidRange ?? true, magneticSnapEnabled: configuration.magneticSnapEnabled ?? true });
  }

  private emit(type: TimelineSlipSlideEventType): TimelineSlipSlideSnapshot {
    this.version += 1; const snapshot = this.getSnapshot(); for (const listener of this.listeners) listener({ type, snapshot }); return snapshot;
  }

  private assertSession(operation: "slip" | "slide"): void {
    this.assertUsable();
    if (!this.session || this.session.operation !== operation) throw new Error(`TimelineSlipSlideEditRuntime is not editing ${operation}`);
    if (this.status === "blocked" && !this.slipPreview && !this.slidePreview) throw new Error("TimelineSlipSlideEditRuntime is blocked");
  }

  private assertUsable(): void { if (this.status === "disposed") throw new Error("TimelineSlipSlideEditRuntime is disposed"); }
}

export const createTimelineSlipSlideEditRuntime = (configuration: TimelineSlipSlideConfiguration): TimelineSlipSlideEditRuntime => new TimelineSlipSlideEditRuntime(configuration);
