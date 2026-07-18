import type {
  ProjectReviewTimelineClipMoveInput,
  ReviewTimelineDragPoint,
  ReviewTimelineDragProjection,
  ReviewTimelineDragSource,
  ReviewTimelineTrackLane,
  ReviewTimelineViewport,
} from "./contracts";
import {
  evaluateReviewTimelineTrackCompatibility,
} from "./compatibility";

const EPSILON = 0.000001;

export function normalizeTimelineViewport(
  viewport: ReviewTimelineViewport,
): ReviewTimelineViewport {
  const left = finiteNumber(
    viewport.left,
    "viewport.left",
  );
  const top = finiteNumber(
    viewport.top,
    "viewport.top",
  );
  const width = positiveNumber(
    viewport.width,
    "viewport.width",
  );
  const height = positiveNumber(
    viewport.height,
    "viewport.height",
  );
  const contentWidth = positiveNumber(
    viewport.contentWidth,
    "viewport.contentWidth",
  );
  const maximumScrollLeft = Math.max(
    0,
    contentWidth - width,
  );

  return {
    left,
    top,
    width,
    height,
    contentWidth,
    scrollLeft: clamp(
      finiteNumber(
        viewport.scrollLeft,
        "viewport.scrollLeft",
      ),
      0,
      maximumScrollLeft,
    ),
  };
}

export function clientXToTimelineTime(
  clientX: number,
  viewport: ReviewTimelineViewport,
  duration: number,
): number {
  const normalizedViewport =
    normalizeTimelineViewport(viewport);
  const safeDuration = nonNegativeNumber(
    duration,
    "duration",
  );
  const contentX = clamp(
    normalizedViewport.scrollLeft +
      finiteNumber(clientX, "clientX") -
      normalizedViewport.left,
    0,
    normalizedViewport.contentWidth,
  );

  if (safeDuration === 0) {
    return 0;
  }

  return (
    contentX /
    normalizedViewport.contentWidth
  ) * safeDuration;
}

export function timelineTimeToClientX(
  time: number,
  viewport: ReviewTimelineViewport,
  duration: number,
): number {
  const normalizedViewport =
    normalizeTimelineViewport(viewport);
  const safeDuration = nonNegativeNumber(
    duration,
    "duration",
  );
  const safeTime = clamp(
    finiteNumber(time, "time"),
    0,
    safeDuration,
  );
  const contentX =
    safeDuration === 0
      ? 0
      : (
          safeTime /
          safeDuration
        ) *
        normalizedViewport.contentWidth;

  return (
    normalizedViewport.left +
    contentX -
    normalizedViewport.scrollLeft
  );
}

export function pointerDeltaToTimelineDelta(
  pointerDeltaX: number,
  contentWidth: number,
  duration: number,
): number {
  return (
    finiteNumber(
      pointerDeltaX,
      "pointerDeltaX",
    ) /
    positiveNumber(
      contentWidth,
      "contentWidth",
    )
  ) * nonNegativeNumber(
    duration,
    "duration",
  );
}

export function timelineTimeToFrame(
  time: number,
  fps: number,
): number {
  return Math.round(
    nonNegativeNumber(
      time,
      "time",
    ) * positiveNumber(
      fps,
      "fps",
    ),
  );
}

export function frameToTimelineTime(
  frame: number,
  fps: number,
): number {
  const normalizedFrame = Math.max(
    0,
    Math.round(
      finiteNumber(
        frame,
        "frame",
      ),
    ),
  );

  return normalizedFrame /
    positiveNumber(fps, "fps");
}

export function quantizeTimelineTimeToFrame(
  time: number,
  fps: number,
  duration: number,
): number {
  const safeDuration = nonNegativeNumber(
    duration,
    "duration",
  );
  const safeTime = clamp(
    finiteNumber(time, "time"),
    0,
    safeDuration,
  );

  return clamp(
    frameToTimelineTime(
      timelineTimeToFrame(
        safeTime,
        fps,
      ),
      fps,
    ),
    0,
    safeDuration,
  );
}

export function resolveTimelineTrackLane(
  clientY: number,
  lanes: ReviewTimelineTrackLane[],
): ReviewTimelineTrackLane | null {
  const y = finiteNumber(
    clientY,
    "clientY",
  );

  for (const lane of lanes) {
    const normalizedLane =
      normalizeTrackLane(lane);

    if (
      y >= normalizedLane.top &&
      y <
        normalizedLane.top +
          normalizedLane.height
    ) {
      return normalizedLane;
    }
  }

  return null;
}

export function isPointInsideTimelineViewport(
  point: ReviewTimelineDragPoint,
  viewport: ReviewTimelineViewport,
): boolean {
  const normalizedViewport =
    normalizeTimelineViewport(viewport);
  const x = finiteNumber(
    point.clientX,
    "point.clientX",
  );
  const y = finiteNumber(
    point.clientY,
    "point.clientY",
  );

  return (
    x >= normalizedViewport.left &&
    x <=
      normalizedViewport.left +
        normalizedViewport.width &&
    y >= normalizedViewport.top &&
    y <=
      normalizedViewport.top +
        normalizedViewport.height
  );
}

export function projectReviewTimelineClipMove(
  input: ProjectReviewTimelineClipMoveInput,
): ReviewTimelineDragProjection {
  const source = normalizeDragSource(
    input.source,
  );
  const duration = nonNegativeNumber(
    input.duration,
    "duration",
  );
  const fps = positiveNumber(
    input.fps,
    "fps",
  );
  const grabOffsetTime = clamp(
    finiteNumber(
      input.grabOffsetTime,
      "grabOffsetTime",
    ),
    0,
    source.duration,
  );
  const pointerTime =
    clientXToTimelineTime(
      input.pointer.clientX,
      input.viewport,
      duration,
    );
  const maximumStartTime = Math.max(
    0,
    duration - source.duration,
  );
  const rawStartTime =
    pointerTime - grabOffsetTime;
  const clampedStartTime = clamp(
    rawStartTime,
    0,
    maximumStartTime,
  );
  const projectedStartTime =
    input.quantizeToFrame === false
      ? clampedStartTime
      : clamp(
          quantizeTimelineTimeToFrame(
            clampedStartTime,
            fps,
            duration,
          ),
          0,
          maximumStartTime,
        );
  const lane = resolveTimelineTrackLane(
    input.pointer.clientY,
    input.lanes,
  );
  const blockedReason = !lane
    ? "track_not_found"
    : lane.locked
      ? "track_locked"
      : !evaluateReviewTimelineTrackCompatibility(
          source.clipType,
          lane.trackType,
        ).compatible
        ? "incompatible_track"
        : null;
  const targetTrackId =
    lane?.trackId ?? null;
  const valid =
    blockedReason === null &&
    targetTrackId !== null;

  return {
    source,
    targetTrackId,
    rawStartTime,
    projectedStartTime,
    projectedEndTime:
      projectedStartTime +
      source.duration,
    pointerInsideViewport:
      isPointInsideTimelineViewport(
        input.pointer,
        input.viewport,
      ),
    valid,
    blockedReason,
    moveIntent:
      valid && targetTrackId
        ? {
            clipId: source.clipId,
            newStartTime:
              projectedStartTime,
            targetTrackId,
          }
        : null,
  };
}

function normalizeTrackLane(
  lane: ReviewTimelineTrackLane,
): ReviewTimelineTrackLane {
  const trackId = requireIdentifier(
    lane.trackId,
    "lane.trackId",
  );

  return {
    trackId,
    trackType:
      lane.trackType?.trim() ||
      undefined,
    top: finiteNumber(
      lane.top,
      "lane.top",
    ),
    height: positiveNumber(
      lane.height,
      "lane.height",
    ),
    locked: Boolean(lane.locked),
  };
}

function normalizeDragSource(
  source: ReviewTimelineDragSource,
): ReviewTimelineDragSource {
  const startTime = nonNegativeNumber(
    source.startTime,
    "source.startTime",
  );
  const duration = positiveNumber(
    source.duration,
    "source.duration",
  );
  const endTime = positiveNumber(
    source.endTime,
    "source.endTime",
  );

  if (
    Math.abs(
      endTime - startTime - duration,
    ) > EPSILON
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
    clipType:
      source.clipType?.trim() ||
      undefined,
    trackId: requireIdentifier(
      source.trackId,
      "source.trackId",
    ),
    startTime,
    endTime,
    duration,
  };
}

function requireIdentifier(
  value: string,
  name: string,
): string {
  const normalized =
    value.trim();

  if (!normalized) {
    throw new TypeError(
      `${name} is required.`,
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
  return Math.min(
    Math.max(value, minimum),
    maximum,
  );
}
