import {
  TIMELINE_RIPPLE_EDIT_CONTRACT_VERSION,
  type RippleClipPosition,
  type RippleConflict,
  type RippleEditCommitResult,
  type RippleTimelineClip,
  type TimelineRippleBeginInput,
  type TimelineRippleConfiguration,
  type TimelineRippleDeleteGapInput,
  type TimelineRippleEventType,
  type TimelineRippleListener,
  type TimelineRippleSnapshot,
} from "../contracts/ripple-edit-contracts";
import { RipplePreviewModel } from "./ripple-preview-model";

const freezePositions = (positions: readonly RippleClipPosition[]): readonly RippleClipPosition[] =>
  Object.freeze(positions.map((position) => Object.freeze({ ...position })));
const freezeConflicts = (conflicts: readonly RippleConflict[]): readonly RippleConflict[] =>
  Object.freeze(conflicts.map((conflict) => Object.freeze({ ...conflict })));

export class TimelineRippleEditRuntime {
  private configuration: Required<TimelineRippleConfiguration>;
  private version = 0;
  private status: TimelineRippleSnapshot["status"] = "idle";
  private operation: TimelineRippleSnapshot["operation"] = null;
  private anchorClipId: string | null = null;
  private trackId: string | null = null;
  private clips: RippleTimelineClip[] = [];
  private deltaFrames = 0;
  private affectedClipIds: readonly string[] = Object.freeze([]);
  private originPositions: readonly RippleClipPosition[] = Object.freeze([]);
  private previewPositions: readonly RippleClipPosition[] = Object.freeze([]);
  private conflicts: readonly RippleConflict[] = Object.freeze([]);
  private commitResult: RippleEditCommitResult | null = null;
  private readonly listeners = new Set<TimelineRippleListener>();

  constructor(configuration: TimelineRippleConfiguration) {
    this.configuration = this.normalizeConfiguration(configuration);
  }

  configure(configuration: Partial<TimelineRippleConfiguration>): TimelineRippleSnapshot {
    this.assertUsable();
    this.configuration = this.normalizeConfiguration({ ...this.configuration, ...configuration });
    return this.emit("configured");
  }

  beginRippleEdit(input: TimelineRippleBeginInput): TimelineRippleSnapshot {
    this.assertUsable();
    if (this.status === "editing" || this.status === "blocked") return this.getSnapshot();
    const clips = RipplePreviewModel.normalizeClips(input.clips);
    const anchor = clips.find((clip) => clip.clipId === input.anchorClipId);
    this.clips = clips;
    this.operation = input.operation;
    this.anchorClipId = input.anchorClipId;
    this.trackId = anchor?.trackId ?? null;
    this.deltaFrames = 0;
    this.affectedClipIds = Object.freeze([]);
    this.originPositions = RipplePreviewModel.origin(clips);
    this.previewPositions = freezePositions(this.originPositions);
    this.commitResult = null;
    if (!anchor) {
      this.conflicts = freezeConflicts([{ type: "missing-anchor", clipId: input.anchorClipId, message: `Anchor clip ${input.anchorClipId} was not found` }]);
      this.status = "blocked";
      return this.emit("ripple_blocked");
    }
    this.conflicts = Object.freeze([]);
    this.status = "editing";
    return this.emit("ripple_started");
  }

  previewRippleFrames(deltaFrames: number): TimelineRippleSnapshot {
    this.assertEditingOrBlocked();
    if (!this.anchorClipId || !this.operation || this.operation === "delete-gap") return this.getSnapshot();
    const anchor = this.clips.find((clip) => clip.clipId === this.anchorClipId);
    if (!anchor) return this.getSnapshot();
    const calculation = RipplePreviewModel.calculate(this.clips, anchor, this.operation, deltaFrames, this.configuration);
    if (this.samePreview(calculation.deltaFrames, calculation.affectedClipIds, calculation.positions, calculation.conflicts)) return this.getSnapshot();
    this.applyCalculation(calculation);
    return this.emit(this.conflicts.length > 0 ? "ripple_blocked" : "ripple_preview_updated");
  }

  previewRippleTime(deltaTimeSeconds: number): TimelineRippleSnapshot {
    return this.previewRippleFrames(deltaTimeSeconds * this.configuration.framesPerSecond);
  }

  previewDeleteGap(input: TimelineRippleDeleteGapInput): TimelineRippleSnapshot {
    this.assertUsable();
    const clips = RipplePreviewModel.normalizeClips(input.clips);
    this.clips = clips;
    this.operation = "delete-gap";
    this.anchorClipId = null;
    this.trackId = input.trackId;
    this.originPositions = RipplePreviewModel.origin(clips);
    this.commitResult = null;
    const calculation = RipplePreviewModel.deleteGap(clips, input.trackId, input.gapStartFrame, input.gapEndFrame, this.configuration);
    this.applyCalculation(calculation);
    return this.emit(this.conflicts.length > 0 ? "ripple_blocked" : "ripple_preview_updated");
  }

  commitRippleEdit(): TimelineRippleSnapshot {
    this.assertUsable();
    if (this.status === "blocked") throw new Error("TimelineRippleEditRuntime is blocked");
    if (this.status !== "editing") throw new Error("TimelineRippleEditRuntime is not editing");
    this.commitResult = Object.freeze({
      operation: this.operation!,
      anchorClipId: this.anchorClipId,
      trackId: this.trackId,
      deltaFrames: this.deltaFrames,
      affectedClipIds: Object.freeze([...this.affectedClipIds]),
      positions: freezePositions(this.previewPositions),
    });
    this.status = "committed";
    return this.emit("ripple_committed");
  }

  cancelRippleEdit(): TimelineRippleSnapshot {
    this.assertEditingOrBlocked();
    this.deltaFrames = 0;
    this.affectedClipIds = Object.freeze([]);
    this.previewPositions = freezePositions(this.originPositions);
    this.conflicts = Object.freeze([]);
    this.commitResult = null;
    this.status = "cancelled";
    return this.emit("ripple_cancelled");
  }

  reset(): TimelineRippleSnapshot {
    this.assertUsable();
    this.status = "idle";
    this.operation = null;
    this.anchorClipId = null;
    this.trackId = null;
    this.clips = [];
    this.deltaFrames = 0;
    this.affectedClipIds = Object.freeze([]);
    this.originPositions = Object.freeze([]);
    this.previewPositions = Object.freeze([]);
    this.conflicts = Object.freeze([]);
    this.commitResult = null;
    return this.emit("reset");
  }

  subscribe(listener: TimelineRippleListener): () => void {
    this.assertUsable();
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  dispose(): void {
    if (this.status === "disposed") return;
    this.status = "disposed";
    this.emit("disposed");
    this.listeners.clear();
  }

  getSnapshot(): TimelineRippleSnapshot {
    return Object.freeze({
      contractVersion: TIMELINE_RIPPLE_EDIT_CONTRACT_VERSION,
      version: this.version,
      status: this.status,
      operation: this.operation,
      anchorClipId: this.anchorClipId,
      trackId: this.trackId,
      deltaFrames: this.deltaFrames,
      affectedClipIds: Object.freeze([...this.affectedClipIds]),
      originPositions: freezePositions(this.originPositions),
      previewPositions: freezePositions(this.previewPositions),
      conflicts: freezeConflicts(this.conflicts),
      commitResult: this.commitResult == null ? null : Object.freeze({
        ...this.commitResult,
        affectedClipIds: Object.freeze([...this.commitResult.affectedClipIds]),
        positions: freezePositions(this.commitResult.positions),
      }),
    });
  }

  private applyCalculation(calculation: ReturnType<typeof RipplePreviewModel.calculate>): void {
    this.deltaFrames = calculation.deltaFrames;
    this.affectedClipIds = Object.freeze([...calculation.affectedClipIds]);
    this.previewPositions = freezePositions(calculation.positions);
    this.conflicts = freezeConflicts(calculation.conflicts);
    this.status = this.conflicts.length > 0 ? "blocked" : "editing";
  }

  private samePreview(deltaFrames: number, affected: readonly string[], positions: readonly RippleClipPosition[], conflicts: readonly RippleConflict[]): boolean {
    return this.deltaFrames === deltaFrames && JSON.stringify(this.affectedClipIds) === JSON.stringify(affected) && JSON.stringify(this.previewPositions) === JSON.stringify(positions) && JSON.stringify(this.conflicts) === JSON.stringify(conflicts);
  }

  private normalizeConfiguration(configuration: TimelineRippleConfiguration): Required<TimelineRippleConfiguration> {
    if (!Number.isFinite(configuration.framesPerSecond) || configuration.framesPerSecond <= 0) throw new Error("framesPerSecond must be greater than zero");
    const timelineStartFrame = Math.round(configuration.timelineStartFrame ?? 0);
    const timelineEndFrame = Math.round(configuration.timelineEndFrame ?? Number.MAX_SAFE_INTEGER);
    if (timelineEndFrame <= timelineStartFrame) throw new Error("timelineEndFrame must be greater than timelineStartFrame");
    return Object.freeze({
      framesPerSecond: configuration.framesPerSecond,
      timelineStartFrame,
      timelineEndFrame,
      affectSameTrackOnly: configuration.affectSameTrackOnly ?? true,
      preserveRelativeSpacing: configuration.preserveRelativeSpacing ?? true,
      blockOnLockedClip: configuration.blockOnLockedClip ?? true,
      preventOverlap: configuration.preventOverlap ?? true,
    });
  }

  private emit(type: TimelineRippleEventType): TimelineRippleSnapshot {
    this.version += 1;
    const snapshot = this.getSnapshot();
    for (const listener of this.listeners) listener({ type, snapshot });
    return snapshot;
  }

  private assertEditingOrBlocked(): void {
    this.assertUsable();
    if (this.status !== "editing" && this.status !== "blocked") throw new Error("TimelineRippleEditRuntime is not editing");
  }

  private assertUsable(): void {
    if (this.status === "disposed") throw new Error("TimelineRippleEditRuntime is disposed");
  }
}

export const createTimelineRippleEditRuntime = (configuration: TimelineRippleConfiguration): TimelineRippleEditRuntime =>
  new TimelineRippleEditRuntime(configuration);
