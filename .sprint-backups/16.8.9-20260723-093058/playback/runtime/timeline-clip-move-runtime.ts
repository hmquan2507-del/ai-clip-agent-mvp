import {
  TIMELINE_CLIP_MOVE_CONTRACT_VERSION,
  type ClipMovePreviewPosition,
  type TimelineClipMoveBeginInput,
  type TimelineClipMoveCommitResult,
  type TimelineClipMoveConfiguration,
  type TimelineClipMoveEventType,
  type TimelineClipMoveItem,
  type TimelineClipMoveListener,
  type TimelineClipMoveSnapshot,
} from "../contracts/clip-move-contracts";
import { MovePreviewModel } from "./move-preview-model";

const clonePosition = (position: ClipMovePreviewPosition): ClipMovePreviewPosition => Object.freeze({ ...position });
const cloneResult = (result: TimelineClipMoveCommitResult | null): TimelineClipMoveCommitResult | null => result == null ? null : Object.freeze({
  ...result,
  positions: Object.freeze(result.positions.map(clonePosition)),
});

export class TimelineClipMoveRuntime {
  private status: TimelineClipMoveSnapshot["status"] = "idle";
  private version = 0;
  private readonly framesPerSecond: number;
  private readonly durationFrames?: number;
  private readonly snapThresholdFrames: number;
  private snapTargets: number[];
  private originClips: TimelineClipMoveItem[] = [];
  private activeClipId: string | null = null;
  private deltaFrames = 0;
  private snappedFrame: number | null = null;
  private previewPositions: ClipMovePreviewPosition[] = [];
  private commitResult: TimelineClipMoveCommitResult | null = null;
  private readonly listeners = new Set<TimelineClipMoveListener>();

  constructor(configuration: TimelineClipMoveConfiguration) {
    if (!Number.isFinite(configuration.framesPerSecond) || configuration.framesPerSecond <= 0) {
      throw new Error("framesPerSecond must be greater than zero");
    }
    this.framesPerSecond = configuration.framesPerSecond;
    this.durationFrames = configuration.durationFrames == null ? undefined : Math.max(0, Math.round(configuration.durationFrames));
    this.snapThresholdFrames = Math.max(0, Math.round(configuration.snapThresholdFrames ?? 0));
    this.snapTargets = [...new Set((configuration.snapTargets ?? []).map((value) => Math.round(value)))];
  }

  configureSnapTargets(targets: readonly number[]): TimelineClipMoveSnapshot {
    this.assertUsable();
    this.snapTargets = [...new Set(targets.map((value) => Math.round(value)))];
    return this.getSnapshot();
  }

  beginMove(input: TimelineClipMoveBeginInput): TimelineClipMoveSnapshot {
    this.assertUsable();
    if (this.status === "moving") return this.getSnapshot();
    const clips = input.clips.map((clip) => Object.freeze({
      clipId: clip.clipId,
      trackId: clip.trackId,
      startFrame: Math.round(clip.startFrame),
      endFrame: Math.round(clip.endFrame),
    }));
    if (!input.activeClipId || !clips.length || !clips.some((clip) => clip.clipId === input.activeClipId)) return this.getSnapshot();
    this.originClips = [...clips];
    this.activeClipId = input.activeClipId;
    this.deltaFrames = 0;
    this.snappedFrame = null;
    this.commitResult = null;
    this.previewPositions = MovePreviewModel.create(this.originClips, 0, this.durationFrames).positions.map(clonePosition);
    this.status = "moving";
    return this.emit("move_started");
  }

  previewMoveFrames(requestedDeltaFrames: number, snap = true): TimelineClipMoveSnapshot {
    this.assertMoving();
    const active = this.originClips.find((clip) => clip.clipId === this.activeClipId)!;
    const snapResult = snap
      ? MovePreviewModel.snapDelta(active, requestedDeltaFrames, this.snapTargets, this.snapThresholdFrames)
      : { deltaFrames: Math.round(requestedDeltaFrames), snappedFrame: null };
    const preview = MovePreviewModel.create(this.originClips, snapResult.deltaFrames, this.durationFrames);
    const nextSnappedFrame = preview.deltaFrames === snapResult.deltaFrames ? snapResult.snappedFrame : null;
    if (preview.deltaFrames === this.deltaFrames && nextSnappedFrame === this.snappedFrame) return this.getSnapshot();
    this.deltaFrames = preview.deltaFrames;
    this.snappedFrame = nextSnappedFrame;
    this.previewPositions = preview.positions.map(clonePosition);
    return this.emit("preview_updated");
  }

  previewMoveTime(deltaTimeSeconds: number, snap = true): TimelineClipMoveSnapshot {
    return this.previewMoveFrames(deltaTimeSeconds * this.framesPerSecond, snap);
  }

  commitMove(): TimelineClipMoveSnapshot {
    this.assertMoving();
    this.commitResult = Object.freeze({
      activeClipId: this.activeClipId!,
      deltaFrames: this.deltaFrames,
      deltaTimeSeconds: this.deltaFrames / this.framesPerSecond,
      snappedFrame: this.snappedFrame,
      positions: Object.freeze(this.previewPositions.map(clonePosition)),
    });
    this.status = "committed";
    return this.emit("move_committed");
  }

  cancelMove(): TimelineClipMoveSnapshot {
    this.assertMoving();
    this.deltaFrames = 0;
    this.snappedFrame = null;
    this.previewPositions = MovePreviewModel.create(this.originClips, 0, this.durationFrames).positions.map(clonePosition);
    this.commitResult = null;
    this.status = "cancelled";
    return this.emit("move_cancelled");
  }

  reset(): TimelineClipMoveSnapshot {
    this.assertUsable();
    this.status = "idle";
    this.originClips = [];
    this.activeClipId = null;
    this.deltaFrames = 0;
    this.snappedFrame = null;
    this.previewPositions = [];
    this.commitResult = null;
    return this.emit("reset");
  }

  subscribe(listener: TimelineClipMoveListener): () => void {
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

  getSnapshot(): TimelineClipMoveSnapshot {
    return Object.freeze({
      contractVersion: TIMELINE_CLIP_MOVE_CONTRACT_VERSION,
      version: this.version,
      status: this.status,
      selectedClipIds: Object.freeze(this.originClips.map((clip) => clip.clipId)),
      activeClipId: this.activeClipId,
      deltaFrames: this.deltaFrames,
      deltaTimeSeconds: this.deltaFrames / this.framesPerSecond,
      snappedFrame: this.snappedFrame,
      previewPositions: Object.freeze(this.previewPositions.map(clonePosition)),
      commitResult: cloneResult(this.commitResult),
    });
  }

  private emit(type: TimelineClipMoveEventType): TimelineClipMoveSnapshot {
    this.version += 1;
    const snapshot = this.getSnapshot();
    for (const listener of this.listeners) listener({ type, snapshot });
    return snapshot;
  }

  private assertMoving(): void {
    this.assertUsable();
    if (this.status !== "moving") throw new Error("TimelineClipMoveRuntime is not moving");
  }

  private assertUsable(): void {
    if (this.status === "disposed") throw new Error("TimelineClipMoveRuntime is disposed");
  }
}

export const createTimelineClipMoveRuntime = (configuration: TimelineClipMoveConfiguration): TimelineClipMoveRuntime =>
  new TimelineClipMoveRuntime(configuration);
