import type {
  ClipMovePreviewPosition,
  TimelineClipMoveItem,
} from "../contracts/clip-move-contracts";

const clamp = (value: number, min: number, max: number): number => Math.min(max, Math.max(min, value));

export class MovePreviewModel {
  static create(
    clips: readonly TimelineClipMoveItem[],
    requestedDeltaFrames: number,
    durationFrames?: number,
  ): { deltaFrames: number; positions: readonly ClipMovePreviewPosition[] } {
    if (!clips.length) return { deltaFrames: 0, positions: Object.freeze([]) };

    const minimumStart = Math.min(...clips.map((clip) => clip.startFrame));
    const maximumEnd = Math.max(...clips.map((clip) => clip.endFrame));
    const lowerBound = -minimumStart;
    const upperBound = durationFrames == null ? Number.POSITIVE_INFINITY : durationFrames - maximumEnd;
    const deltaFrames = Math.round(clamp(Math.round(requestedDeltaFrames), lowerBound, upperBound));

    const positions = clips.map((clip) => Object.freeze({
      clipId: clip.clipId,
      trackId: clip.trackId,
      originStartFrame: clip.startFrame,
      originEndFrame: clip.endFrame,
      previewStartFrame: clip.startFrame + deltaFrames,
      previewEndFrame: clip.endFrame + deltaFrames,
    }));

    return { deltaFrames, positions: Object.freeze(positions) };
  }

  static snapDelta(
    activeClip: TimelineClipMoveItem,
    requestedDeltaFrames: number,
    targets: readonly number[],
    thresholdFrames: number,
  ): { deltaFrames: number; snappedFrame: number | null } {
    const requestedStart = activeClip.startFrame + Math.round(requestedDeltaFrames);
    let snappedFrame: number | null = null;
    let bestDistance = Number.POSITIVE_INFINITY;

    for (const target of targets) {
      const distance = Math.abs(Math.round(target) - requestedStart);
      if (distance <= thresholdFrames && distance < bestDistance) {
        bestDistance = distance;
        snappedFrame = Math.round(target);
      }
    }

    return {
      deltaFrames: snappedFrame == null ? Math.round(requestedDeltaFrames) : snappedFrame - activeClip.startFrame,
      snappedFrame,
    };
  }
}
