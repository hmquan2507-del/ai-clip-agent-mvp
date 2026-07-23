import {
  TIMELINE_CLIP_TRIM_CONTRACT_VERSION,
  type ClipTrimEdge,
  type ClipTrimPreview,
  type ClipTrimSnapTarget,
  type TimelineClipTrimBeginInput,
  type TimelineClipTrimCommitResult,
  type TimelineClipTrimConfiguration,
  type TimelineClipTrimEventType,
  type TimelineClipTrimListener,
  type TimelineClipTrimSnapshot,
  type TimelineTrimClip,
} from "../contracts/clip-trim-contracts";
import { TrimPreviewModel } from "./trim-preview-model";

const clonePreview = (preview: ClipTrimPreview | null): ClipTrimPreview | null =>
  preview == null ? null : Object.freeze({ ...preview });

const cloneResult = (result: TimelineClipTrimCommitResult | null): TimelineClipTrimCommitResult | null =>
  result == null ? null : Object.freeze({ ...result, preview: Object.freeze({ ...result.preview }) });

export class TimelineClipTrimRuntime {
  private status: TimelineClipTrimSnapshot["status"] = "idle";
  private version = 0;
  private readonly framesPerSecond: number;
  private readonly minimumDurationFrames: number;
  private readonly snapThresholdFrames: number;
  private snapTargets: ClipTrimSnapTarget[];
  private originClip: TimelineTrimClip | null = null;
  private edge: ClipTrimEdge | null = null;
  private deltaFrames = 0;
  private snappedFrame: number | null = null;
  private snappedTargetId: string | null = null;
  private origin: ClipTrimPreview | null = null;
  private preview: ClipTrimPreview | null = null;
  private commitResult: TimelineClipTrimCommitResult | null = null;
  private readonly listeners = new Set<TimelineClipTrimListener>();

  constructor(configuration: TimelineClipTrimConfiguration) {
    if (!Number.isFinite(configuration.framesPerSecond) || configuration.framesPerSecond <= 0) {
      throw new Error("framesPerSecond must be greater than zero");
    }
    this.framesPerSecond = configuration.framesPerSecond;
    this.minimumDurationFrames = Math.max(1, Math.round(configuration.minimumDurationFrames ?? 1));
    this.snapThresholdFrames = Math.max(0, Math.round(configuration.snapThresholdFrames ?? 0));
    this.snapTargets = this.normalizeTargets(configuration.snapTargets ?? []);
  }

  configureSnapTargets(targets: readonly ClipTrimSnapTarget[]): TimelineClipTrimSnapshot {
    this.assertUsable();
    this.snapTargets = this.normalizeTargets(targets);
    return this.getSnapshot();
  }

  beginTrim(input: TimelineClipTrimBeginInput): TimelineClipTrimSnapshot {
    this.assertUsable();
    if (this.status === "trimming") return this.getSnapshot();
    const clip = this.normalizeClip(input.clip);
    if (!this.isValidClip(clip)) return this.getSnapshot();
    this.originClip = clip;
    this.edge = input.edge;
    this.deltaFrames = 0;
    this.snappedFrame = null;
    this.snappedTargetId = null;
    this.origin = TrimPreviewModel.origin(clip, input.edge);
    this.preview = clonePreview(this.origin);
    this.commitResult = null;
    this.status = "trimming";
    return this.emit("trim_started");
  }

  previewTrimFrames(requestedDeltaFrames: number, snap = true): TimelineClipTrimSnapshot {
    this.assertTrimming();
    const snapResult = snap
      ? TrimPreviewModel.snapDelta(
          this.originClip!,
          this.edge!,
          requestedDeltaFrames,
          this.snapTargets,
          this.snapThresholdFrames,
        )
      : { deltaFrames: Math.round(requestedDeltaFrames), snappedFrame: null, snappedTargetId: null };
    const calculation = TrimPreviewModel.create(
      this.originClip!,
      this.edge!,
      snapResult.deltaFrames,
      this.minimumDurationFrames,
    );
    const snapWasApplied = calculation.deltaFrames === snapResult.deltaFrames;
    const nextSnappedFrame = snapWasApplied ? snapResult.snappedFrame : null;
    const nextSnappedTargetId = snapWasApplied ? snapResult.snappedTargetId : null;
    if (
      calculation.deltaFrames === this.deltaFrames &&
      nextSnappedFrame === this.snappedFrame &&
      nextSnappedTargetId === this.snappedTargetId
    ) return this.getSnapshot();

    this.deltaFrames = calculation.deltaFrames;
    this.snappedFrame = nextSnappedFrame;
    this.snappedTargetId = nextSnappedTargetId;
    this.preview = clonePreview(calculation.preview);
    return this.emit("preview_updated");
  }

  previewTrimTime(deltaTimeSeconds: number, snap = true): TimelineClipTrimSnapshot {
    return this.previewTrimFrames(deltaTimeSeconds * this.framesPerSecond, snap);
  }

  commitTrim(): TimelineClipTrimSnapshot {
    this.assertTrimming();
    this.commitResult = Object.freeze({
      clipId: this.originClip!.clipId,
      edge: this.edge!,
      deltaFrames: this.deltaFrames,
      deltaTimeSeconds: this.deltaFrames / this.framesPerSecond,
      snappedFrame: this.snappedFrame,
      snappedTargetId: this.snappedTargetId,
      preview: Object.freeze({ ...this.preview! }),
    });
    this.status = "committed";
    return this.emit("trim_committed");
  }

  cancelTrim(): TimelineClipTrimSnapshot {
    this.assertTrimming();
    this.deltaFrames = 0;
    this.snappedFrame = null;
    this.snappedTargetId = null;
    this.preview = clonePreview(this.origin);
    this.commitResult = null;
    this.status = "cancelled";
    return this.emit("trim_cancelled");
  }

  reset(): TimelineClipTrimSnapshot {
    this.assertUsable();
    this.status = "idle";
    this.originClip = null;
    this.edge = null;
    this.deltaFrames = 0;
    this.snappedFrame = null;
    this.snappedTargetId = null;
    this.origin = null;
    this.preview = null;
    this.commitResult = null;
    return this.emit("reset");
  }

  subscribe(listener: TimelineClipTrimListener): () => void {
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

  getSnapshot(): TimelineClipTrimSnapshot {
    return Object.freeze({
      contractVersion: TIMELINE_CLIP_TRIM_CONTRACT_VERSION,
      version: this.version,
      status: this.status,
      clipId: this.originClip?.clipId ?? null,
      edge: this.edge,
      deltaFrames: this.deltaFrames,
      deltaTimeSeconds: this.deltaFrames / this.framesPerSecond,
      snappedFrame: this.snappedFrame,
      snappedTargetId: this.snappedTargetId,
      origin: clonePreview(this.origin),
      preview: clonePreview(this.preview),
      commitResult: cloneResult(this.commitResult),
    });
  }

  private normalizeClip(clip: TimelineTrimClip): TimelineTrimClip {
    return Object.freeze({
      clipId: clip.clipId,
      trackId: clip.trackId,
      timelineStartFrame: Math.round(clip.timelineStartFrame),
      timelineEndFrame: Math.round(clip.timelineEndFrame),
      sourceStartFrame: Math.round(clip.sourceStartFrame),
      sourceEndFrame: Math.round(clip.sourceEndFrame),
      sourceDurationFrames: Math.max(0, Math.round(clip.sourceDurationFrames)),
    });
  }

  private isValidClip(clip: TimelineTrimClip): boolean {
    return Boolean(clip.clipId) &&
      Boolean(clip.trackId) &&
      clip.timelineStartFrame >= 0 &&
      clip.timelineEndFrame > clip.timelineStartFrame &&
      clip.sourceStartFrame >= 0 &&
      clip.sourceEndFrame > clip.sourceStartFrame &&
      clip.sourceEndFrame <= clip.sourceDurationFrames &&
      clip.timelineEndFrame - clip.timelineStartFrame >= this.minimumDurationFrames &&
      clip.sourceEndFrame - clip.sourceStartFrame >= this.minimumDurationFrames;
  }

  private normalizeTargets(targets: readonly ClipTrimSnapTarget[]): ClipTrimSnapTarget[] {
    const byId = new Map<string, ClipTrimSnapTarget>();
    for (const target of targets) {
      if (!target.id || !Number.isFinite(target.frame)) continue;
      byId.set(target.id, Object.freeze({ ...target, frame: Math.round(target.frame) }));
    }
    return [...byId.values()];
  }

  private emit(type: TimelineClipTrimEventType): TimelineClipTrimSnapshot {
    this.version += 1;
    const snapshot = this.getSnapshot();
    for (const listener of this.listeners) listener({ type, snapshot });
    return snapshot;
  }

  private assertTrimming(): void {
    this.assertUsable();
    if (this.status !== "trimming") throw new Error("TimelineClipTrimRuntime is not trimming");
  }

  private assertUsable(): void {
    if (this.status === "disposed") throw new Error("TimelineClipTrimRuntime is disposed");
  }
}

export const createTimelineClipTrimRuntime = (
  configuration: TimelineClipTrimConfiguration,
): TimelineClipTrimRuntime => new TimelineClipTrimRuntime(configuration);
