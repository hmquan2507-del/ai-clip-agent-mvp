import type {
  ClipTrimEdge,
  ClipTrimPreview,
  ClipTrimSnapTarget,
  TimelineTrimClip,
} from "../contracts/clip-trim-contracts";

const clamp = (value: number, minimum: number, maximum: number): number =>
  Math.min(maximum, Math.max(minimum, value));

export interface TrimPreviewCalculation {
  readonly deltaFrames: number;
  readonly preview: ClipTrimPreview;
}

export interface TrimSnapCalculation {
  readonly deltaFrames: number;
  readonly snappedFrame: number | null;
  readonly snappedTargetId: string | null;
}

export class TrimPreviewModel {
  static origin(clip: TimelineTrimClip, edge: ClipTrimEdge): ClipTrimPreview {
    return Object.freeze({
      clipId: clip.clipId,
      trackId: clip.trackId,
      edge,
      timelineStartFrame: Math.round(clip.timelineStartFrame),
      timelineEndFrame: Math.round(clip.timelineEndFrame),
      sourceStartFrame: Math.round(clip.sourceStartFrame),
      sourceEndFrame: Math.round(clip.sourceEndFrame),
      durationFrames: Math.round(clip.timelineEndFrame) - Math.round(clip.timelineStartFrame),
    });
  }

  static create(
    clip: TimelineTrimClip,
    edge: ClipTrimEdge,
    requestedDeltaFrames: number,
    minimumDurationFrames: number,
  ): TrimPreviewCalculation {
    const delta = Math.round(requestedDeltaFrames);
    const timelineStart = Math.round(clip.timelineStartFrame);
    const timelineEnd = Math.round(clip.timelineEndFrame);
    const sourceStart = Math.round(clip.sourceStartFrame);
    const sourceEnd = Math.round(clip.sourceEndFrame);
    const sourceDuration = Math.max(0, Math.round(clip.sourceDurationFrames));

    let appliedDelta: number;
    let nextTimelineStart = timelineStart;
    let nextTimelineEnd = timelineEnd;
    let nextSourceStart = sourceStart;
    let nextSourceEnd = sourceEnd;

    if (edge === "start") {
      const lowerBound = Math.max(-timelineStart, -sourceStart);
      const upperBound = Math.min(
        timelineEnd - timelineStart - minimumDurationFrames,
        sourceEnd - sourceStart - minimumDurationFrames,
      );
      appliedDelta = Math.round(clamp(delta, lowerBound, upperBound));
      nextTimelineStart += appliedDelta;
      nextSourceStart += appliedDelta;
    } else {
      const lowerBound = Math.max(
        minimumDurationFrames - (timelineEnd - timelineStart),
        minimumDurationFrames - (sourceEnd - sourceStart),
      );
      const upperBound = sourceDuration - sourceEnd;
      appliedDelta = Math.round(clamp(delta, lowerBound, upperBound));
      nextTimelineEnd += appliedDelta;
      nextSourceEnd += appliedDelta;
    }

    const preview: ClipTrimPreview = Object.freeze({
      clipId: clip.clipId,
      trackId: clip.trackId,
      edge,
      timelineStartFrame: nextTimelineStart,
      timelineEndFrame: nextTimelineEnd,
      sourceStartFrame: nextSourceStart,
      sourceEndFrame: nextSourceEnd,
      durationFrames: nextTimelineEnd - nextTimelineStart,
    });

    return Object.freeze({ deltaFrames: appliedDelta, preview });
  }

  static snapDelta(
    clip: TimelineTrimClip,
    edge: ClipTrimEdge,
    requestedDeltaFrames: number,
    targets: readonly ClipTrimSnapTarget[],
    thresholdFrames: number,
  ): TrimSnapCalculation {
    const originEdgeFrame = edge === "start"
      ? Math.round(clip.timelineStartFrame)
      : Math.round(clip.timelineEndFrame);
    const requestedEdgeFrame = originEdgeFrame + Math.round(requestedDeltaFrames);
    let bestTarget: ClipTrimSnapTarget | null = null;
    let bestDistance = Number.POSITIVE_INFINITY;

    for (const target of targets) {
      const normalizedFrame = Math.round(target.frame);
      const distance = Math.abs(normalizedFrame - requestedEdgeFrame);
      if (distance <= thresholdFrames && distance < bestDistance) {
        bestDistance = distance;
        bestTarget = { ...target, frame: normalizedFrame };
      }
    }

    return Object.freeze({
      deltaFrames: bestTarget == null
        ? Math.round(requestedDeltaFrames)
        : bestTarget.frame - originEdgeFrame,
      snappedFrame: bestTarget?.frame ?? null,
      snappedTargetId: bestTarget?.id ?? null,
    });
  }
}
