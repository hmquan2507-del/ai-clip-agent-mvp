import {
  frameToTimelineTime,
  normalizeTimelineViewport,
  timelineTimeToFrame,
} from "./coordinates";

import {
  REVIEW_TIMELINE_SNAP_CONTRACT_VERSION,
  type ProjectReviewTimelineSnapInput,
  type ReviewTimelineSnapAlignment,
  type ReviewTimelineSnapCandidate,
  type ReviewTimelineSnapClip,
  type ReviewTimelineSnapProjector,
  type ReviewTimelineSnapResult,
  type ReviewTimelineSnapTargetType,
} from "./snap-contracts";

const EPSILON = 0.000001;

export class ReviewTimelineSnapRuntime
  implements ReviewTimelineSnapProjector {
  project(
    input: ProjectReviewTimelineSnapInput,
  ): ReviewTimelineSnapResult {
    const sourceClipId = requireIdentifier(
      input.sourceClipId,
      "sourceClipId",
    );
    const targetTrackId = requireIdentifier(
      input.targetTrackId,
      "targetTrackId",
    );
    const timelineDuration =
      nonNegativeNumber(
        input.timelineDuration,
        "timelineDuration",
      );
    const clipDuration = positiveNumber(
      input.clipDuration,
      "clipDuration",
    );
    const maximumStartTime = Math.max(
      0,
      timelineDuration - clipDuration,
    );
    const rawStartTime = clamp(
      finiteNumber(
        input.projectedStartTime,
        "projectedStartTime",
      ),
      0,
      maximumStartTime,
    );
    const fps = positiveNumber(
      input.fps,
      "fps",
    );
    const viewport =
      normalizeTimelineViewport(
        input.viewport,
      );
    const thresholdPixels =
      nonNegativeNumber(
        input.context.thresholdPixels,
        "context.thresholdPixels",
      );
    const thresholdTime =
      viewport.contentWidth === 0
        ? 0
        : (
            thresholdPixels /
            viewport.contentWidth
          ) * timelineDuration;

    if (
      input.context.enabled === false ||
      timelineDuration === 0
    ) {
      return unsnappedResult(
        rawStartTime,
        clipDuration,
        thresholdTime,
      );
    }

    const candidates:
      ReviewTimelineSnapCandidate[] = [];

    if (
      input.context.includeFrames !== false
    ) {
      addFrameCandidates(
        candidates,
        rawStartTime,
        clipDuration,
        fps,
        viewport.contentWidth,
        timelineDuration,
        maximumStartTime,
      );
    }

    if (
      input.context.includePlayhead !== false &&
      input.context.playheadTime !== undefined &&
      input.context.playheadTime !== null
    ) {
      addTargetCandidates(
        candidates,
        "playhead",
        "playhead",
        clamp(
          finiteNumber(
            input.context.playheadTime,
            "context.playheadTime",
          ),
          0,
          timelineDuration,
        ),
        rawStartTime,
        clipDuration,
        viewport.contentWidth,
        timelineDuration,
        maximumStartTime,
      );
    }

    if (
      input.context.includeClipEdges !== false
    ) {
      for (const rawClip of
        input.context.clips) {
        const clip = normalizeClip(rawClip);

        if (
          clip.clipId === sourceClipId ||
          clip.trackId !== targetTrackId
        ) {
          continue;
        }

        addTargetCandidates(
          candidates,
          "clip_start",
          `${clip.clipId}:start`,
          clip.startTime,
          rawStartTime,
          clipDuration,
          viewport.contentWidth,
          timelineDuration,
          maximumStartTime,
        );
        addTargetCandidates(
          candidates,
          "clip_end",
          `${clip.clipId}:end`,
          clip.endTime,
          rawStartTime,
          clipDuration,
          viewport.contentWidth,
          timelineDuration,
          maximumStartTime,
        );
      }
    }

    const eligible = candidates
      .filter(
        (candidate) =>
          candidate.distanceTime <=
          thresholdTime + EPSILON,
      )
      .sort(compareCandidates);
    const winner = eligible[0] ?? null;

    if (!winner) {
      return {
        ...unsnappedResult(
          rawStartTime,
          clipDuration,
          thresholdTime,
        ),
        consideredCandidateCount:
          candidates.length,
      };
    }

    return {
      contractVersion:
        REVIEW_TIMELINE_SNAP_CONTRACT_VERSION,
      rawStartTime,
      snappedStartTime:
        winner.snappedStartTime,
      snappedEndTime:
        winner.snappedStartTime +
        clipDuration,
      thresholdTime,
      snapped: true,
      candidate: clone(winner),
      consideredCandidateCount:
        candidates.length,
    };
  }
}

function addFrameCandidates(
  candidates: ReviewTimelineSnapCandidate[],
  rawStartTime: number,
  clipDuration: number,
  fps: number,
  contentWidth: number,
  timelineDuration: number,
  maximumStartTime: number,
): void {
  const rawEndTime =
    rawStartTime + clipDuration;
  const startFrame = timelineTimeToFrame(
    rawStartTime,
    fps,
  );
  const endFrame = timelineTimeToFrame(
    rawEndTime,
    fps,
  );

  addTargetCandidates(
    candidates,
    "frame",
    `frame:${startFrame}`,
    frameToTimelineTime(
      startFrame,
      fps,
    ),
    rawStartTime,
    clipDuration,
    contentWidth,
    timelineDuration,
    maximumStartTime,
    ["start"],
  );
  addTargetCandidates(
    candidates,
    "frame",
    `frame:${endFrame}`,
    frameToTimelineTime(
      endFrame,
      fps,
    ),
    rawStartTime,
    clipDuration,
    contentWidth,
    timelineDuration,
    maximumStartTime,
    ["end"],
  );
}

function addTargetCandidates(
  candidates: ReviewTimelineSnapCandidate[],
  targetType: ReviewTimelineSnapTargetType,
  targetId: string,
  targetTime: number,
  rawStartTime: number,
  clipDuration: number,
  contentWidth: number,
  timelineDuration: number,
  maximumStartTime: number,
  alignments: ReviewTimelineSnapAlignment[] = [
    "start",
    "end",
  ],
): void {
  for (const alignment of alignments) {
    const snappedStartTime =
      alignment === "start"
        ? targetTime
        : targetTime - clipDuration;

    if (
      snappedStartTime < -EPSILON ||
      snappedStartTime >
        maximumStartTime + EPSILON
    ) {
      continue;
    }

    const safeStartTime = clamp(
      snappedStartTime,
      0,
      maximumStartTime,
    );
    const distanceTime = Math.abs(
      safeStartTime - rawStartTime,
    );

    candidates.push({
      targetType,
      targetId,
      targetTime,
      alignment,
      snappedStartTime: safeStartTime,
      distanceTime,
      distancePixels:
        timelineDuration === 0
          ? 0
          : (
              distanceTime /
              timelineDuration
            ) * contentWidth,
    });
  }
}

function compareCandidates(
  left: ReviewTimelineSnapCandidate,
  right: ReviewTimelineSnapCandidate,
): number {
  const distanceDifference =
    left.distanceTime - right.distanceTime;
  if (
    Math.abs(distanceDifference) > EPSILON
  ) {
    return distanceDifference;
  }

  const priorityDifference =
    targetPriority(left.targetType) -
    targetPriority(right.targetType);
  if (priorityDifference !== 0) {
    return priorityDifference;
  }

  const alignmentDifference =
    alignmentPriority(left.alignment) -
    alignmentPriority(right.alignment);
  if (alignmentDifference !== 0) {
    return alignmentDifference;
  }

  const timeDifference =
    left.targetTime - right.targetTime;
  if (Math.abs(timeDifference) > EPSILON) {
    return timeDifference;
  }

  return left.targetId.localeCompare(
    right.targetId,
  );
}

function targetPriority(
  type: ReviewTimelineSnapTargetType,
): number {
  switch (type) {
    case "clip_start":
    case "clip_end":
      return 0;
    case "playhead":
      return 1;
    case "frame":
      return 2;
  }
}

function alignmentPriority(
  alignment: ReviewTimelineSnapAlignment,
): number {
  return alignment === "start" ? 0 : 1;
}

function normalizeClip(
  clip: ReviewTimelineSnapClip,
): ReviewTimelineSnapClip {
  const startTime = nonNegativeNumber(
    clip.startTime,
    "clip.startTime",
  );
  const endTime = positiveNumber(
    clip.endTime,
    "clip.endTime",
  );

  if (endTime <= startTime) {
    throw new RangeError(
      "clip.endTime must be greater than clip.startTime.",
    );
  }

  return {
    clipId: requireIdentifier(
      clip.clipId,
      "clip.clipId",
    ),
    trackId: requireIdentifier(
      clip.trackId,
      "clip.trackId",
    ),
    startTime,
    endTime,
  };
}

function unsnappedResult(
  rawStartTime: number,
  clipDuration: number,
  thresholdTime: number,
): ReviewTimelineSnapResult {
  return {
    contractVersion:
      REVIEW_TIMELINE_SNAP_CONTRACT_VERSION,
    rawStartTime,
    snappedStartTime: rawStartTime,
    snappedEndTime:
      rawStartTime + clipDuration,
    thresholdTime,
    snapped: false,
    candidate: null,
    consideredCandidateCount: 0,
  };
}

function requireIdentifier(
  value: string,
  name: string,
): string {
  const normalized = value.trim();
  if (!normalized) {
    throw new TypeError(
      `${name} must not be empty.`,
    );
  }
  return normalized;
}

function finiteNumber(
  value: number,
  name: string,
): number {
  if (!Number.isFinite(value)) {
    throw new TypeError(
      `${name} must be finite.`,
    );
  }
  return value;
}

function nonNegativeNumber(
  value: number,
  name: string,
): number {
  const normalized = finiteNumber(
    value,
    name,
  );
  if (normalized < 0) {
    throw new RangeError(
      `${name} must be non-negative.`,
    );
  }
  return normalized;
}

function positiveNumber(
  value: number,
  name: string,
): number {
  const normalized = finiteNumber(
    value,
    name,
  );
  if (normalized <= 0) {
    throw new RangeError(
      `${name} must be positive.`,
    );
  }
  return normalized;
}

function clamp(
  value: number,
  minimum: number,
  maximum: number,
): number {
  return Math.min(
    Math.max(value, minimum),
    maximum,
  );
}

function clone<T>(value: T): T {
  return structuredClone(value);
}
