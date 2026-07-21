import {
  clientXToTimelineTime,
  isPointInsideTimelineViewport,
  quantizeTimelineTimeToFrame,
} from "../drag";

import type {
  ProjectReviewTimelineClipTrimInput,
  ReviewTimelineTrimBlockedReason,
  ReviewTimelineTrimHandle,
  ReviewTimelineTrimHandleGeometry,
  ReviewTimelineTrimIntent,
  ReviewTimelineTrimProjection,
  ReviewTimelineTrimSource,
} from "./contracts";
import {
  REVIEW_TIMELINE_TRIM_CONTRACT_VERSION,
} from "./contracts";

const EPSILON = 0.000001;

export function projectReviewTimelineClipTrim(
  input: ProjectReviewTimelineClipTrimInput,
): ReviewTimelineTrimProjection {
  const timelineDuration = nonNegativeNumber(
    input.timelineDuration,
    "timelineDuration",
  );
  const fps = positiveNumber(input.fps, "fps");
  const source = normalizeTrimSource(
    input.source,
    timelineDuration,
  );
  const handle = normalizeTrimHandle(input.handle);
  const minimumDuration = normalizeMinimumDuration(
    input.minimumDuration,
    fps,
  );
  const rawTime = clientXToTimelineTime(
    input.pointer.clientX,
    input.viewport,
    timelineDuration,
  );
  const candidateTime =
    input.quantizeToFrame === false
      ? rawTime
      : quantizeTimelineTimeToFrame(
          rawTime,
          fps,
          timelineDuration,
        );

  const projectedTime =
    handle === "start"
      ? clamp(
          candidateTime,
          0,
          Math.max(
            0,
            source.endTime - minimumDuration,
          ),
        )
      : clamp(
          candidateTime,
          Math.min(
            timelineDuration,
            source.startTime + minimumDuration,
          ),
          timelineDuration,
        );

  const projectedStartTime =
    handle === "start"
      ? projectedTime
      : source.startTime;
  const projectedEndTime =
    handle === "end"
      ? projectedTime
      : source.endTime;
  const projectedDuration =
    projectedEndTime - projectedStartTime;
  const originalTime =
    handle === "start"
      ? source.startTime
      : source.endTime;
  const deltaTime = projectedTime - originalTime;
  const changed = Math.abs(deltaTime) > EPSILON;
  const blockedReason = resolveBlockedReason(
    source,
    minimumDuration,
    changed,
  );
  const valid = blockedReason === null;

  return {
    contractVersion:
      REVIEW_TIMELINE_TRIM_CONTRACT_VERSION,
    handle,
    source,
    rawTime,
    projectedTime,
    projectedStartTime,
    projectedEndTime,
    projectedDuration,
    deltaTime,
    minimumDuration,
    pointerInsideViewport:
      isPointInsideTimelineViewport(
        input.pointer,
        input.viewport,
      ),
    changed,
    valid,
    blockedReason,
    trimIntent:
      valid
        ? buildTrimIntent(
            handle,
            source.clipId,
            projectedTime,
          )
        : null,
  };
}

export function resolveReviewTimelineTrimHandle(
  geometry: ReviewTimelineTrimHandleGeometry,
): ReviewTimelineTrimHandle | null {
  const clipLeft = finiteNumber(
    geometry.clipLeft,
    "clipLeft",
  );
  const clipWidth = positiveNumber(
    geometry.clipWidth,
    "clipWidth",
  );
  const clientX = finiteNumber(
    geometry.clientX,
    "clientX",
  );
  const hitSlop = nonNegativeNumber(
    geometry.hitSlop ?? 8,
    "hitSlop",
  );
  const startDistance = Math.abs(clientX - clipLeft);
  const endDistance = Math.abs(
    clientX - (clipLeft + clipWidth),
  );
  const startHit = startDistance <= hitSlop;
  const endHit = endDistance <= hitSlop;

  if (startHit && endHit) {
    return startDistance <= endDistance
      ? "start"
      : "end";
  }
  if (startHit) return "start";
  if (endHit) return "end";
  return null;
}

function buildTrimIntent(
  handle: ReviewTimelineTrimHandle,
  clipId: string,
  projectedTime: number,
): ReviewTimelineTrimIntent {
  return handle === "start"
    ? {
        operation: "trim_clip_start",
        clipId,
        newStartTime: projectedTime,
      }
    : {
        operation: "trim_clip_end",
        clipId,
        newEndTime: projectedTime,
      };
}

function resolveBlockedReason(
  source: ReviewTimelineTrimSource,
  minimumDuration: number,
  changed: boolean,
): ReviewTimelineTrimBlockedReason | null {
  if (!source.editable) {
    return "clip_not_editable";
  }
  if (source.trackLocked) {
    return "track_locked";
  }
  if (source.duration <= minimumDuration + EPSILON) {
    return "range_not_trimmable";
  }
  if (!changed) {
    return "no_change";
  }
  return null;
}

function normalizeTrimSource(
  source: ReviewTimelineTrimSource,
  timelineDuration: number,
): ReviewTimelineTrimSource {
  const startTime = nonNegativeNumber(
    source.startTime,
    "source.startTime",
  );
  const endTime = positiveNumber(
    source.endTime,
    "source.endTime",
  );
  const duration = positiveNumber(
    source.duration,
    "source.duration",
  );

  if (endTime > timelineDuration + EPSILON) {
    throw new RangeError(
      "source.endTime exceeds timelineDuration.",
    );
  }
  if (
    Math.abs(endTime - startTime - duration) > EPSILON
  ) {
    throw new RangeError(
      "source duration must match its time range.",
    );
  }

  return {
    clipId: requireIdentifier(
      source.clipId,
      "source.clipId",
    ),
    trackId: requireIdentifier(
      source.trackId,
      "source.trackId",
    ),
    startTime,
    endTime,
    duration,
    editable: Boolean(source.editable),
    trackLocked: Boolean(source.trackLocked),
  };
}

function normalizeTrimHandle(
  value: ReviewTimelineTrimHandle,
): ReviewTimelineTrimHandle {
  if (value !== "start" && value !== "end") {
    throw new TypeError(
      "handle must be start or end.",
    );
  }
  return value;
}

function normalizeMinimumDuration(
  value: number | undefined,
  fps: number,
): number {
  const minimum = positiveNumber(
    value ?? 1 / fps,
    "minimumDuration",
  );
  const minimumFrames = Math.max(
    1,
    Math.ceil(minimum * fps - EPSILON),
  );
  return minimumFrames / fps;
}

function requireIdentifier(
  value: string,
  name: string,
): string {
  const normalized = value.trim();
  if (!normalized) {
    throw new TypeError(`${name} is required.`);
  }
  return normalized;
}

function finiteNumber(
  value: number,
  name: string,
): number {
  if (!Number.isFinite(value)) {
    throw new TypeError(`${name} must be finite.`);
  }
  return value;
}

function nonNegativeNumber(
  value: number,
  name: string,
): number {
  const normalized = finiteNumber(value, name);
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
  const normalized = finiteNumber(value, name);
  if (normalized <= 0) {
    throw new RangeError(
      `${name} must be greater than zero.`,
    );
  }
  return normalized;
}

function clamp(
  value: number,
  minimum: number,
  maximum: number,
): number {
  return Math.min(Math.max(value, minimum), maximum);
}
