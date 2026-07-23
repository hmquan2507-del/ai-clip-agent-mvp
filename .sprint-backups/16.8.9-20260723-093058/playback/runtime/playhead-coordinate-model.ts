import { assertFiniteNumber, assertNonNegativeNumber, assertPositiveNumber, clampPlaybackTime, frameToTime, timeToFrame } from "./playback-time-model";

export function normalizePixelsPerSecond(value: number): number {
  return assertPositiveNumber(value, "pixelsPerSecond");
}

export function normalizeViewportWidth(value: number): number {
  return assertNonNegativeNumber(value, "viewportWidth");
}

export function totalTimelineWidth(duration: number, pixelsPerSecond: number): number {
  return assertNonNegativeNumber(duration, "duration") * normalizePixelsPerSecond(pixelsPerSecond);
}

export function clampScrollOffset(
  scrollOffset: number,
  duration: number,
  pixelsPerSecond: number,
  viewportWidth: number,
): number {
  assertFiniteNumber(scrollOffset, "scrollOffset");
  const maximum = Math.max(0, totalTimelineWidth(duration, pixelsPerSecond) - normalizeViewportWidth(viewportWidth));
  return Math.min(maximum, Math.max(0, scrollOffset));
}

export function timeToTimelinePixel(time: number, duration: number, pixelsPerSecond: number): number {
  return clampPlaybackTime(time, duration) * normalizePixelsPerSecond(pixelsPerSecond);
}

export function timelinePixelToTime(pixel: number, duration: number, pixelsPerSecond: number): number {
  assertFiniteNumber(pixel, "pixel");
  return clampPlaybackTime(Math.max(0, pixel) / normalizePixelsPerSecond(pixelsPerSecond), duration);
}

export function timeToViewportPixel(
  time: number,
  duration: number,
  pixelsPerSecond: number,
  scrollOffset: number,
): number {
  return timeToTimelinePixel(time, duration, pixelsPerSecond) - Math.max(0, scrollOffset);
}

export function viewportPixelToTime(
  viewportPixel: number,
  duration: number,
  pixelsPerSecond: number,
  scrollOffset: number,
): number {
  assertFiniteNumber(viewportPixel, "viewportPixel");
  return timelinePixelToTime(viewportPixel + Math.max(0, scrollOffset), duration, pixelsPerSecond);
}

export function coordinateFromTime(time: number, duration: number, fps: number, pixelsPerSecond: number, scrollOffset: number) {
  const timeSeconds = clampPlaybackTime(time, duration);
  return {
    timeSeconds,
    frame: timeToFrame(timeSeconds, fps, duration),
    timelinePixel: timeToTimelinePixel(timeSeconds, duration, pixelsPerSecond),
    viewportPixel: timeToViewportPixel(timeSeconds, duration, pixelsPerSecond, scrollOffset),
  };
}

export function coordinateFromFrame(frame: number, duration: number, fps: number, pixelsPerSecond: number, scrollOffset: number) {
  return coordinateFromTime(frameToTime(frame, fps, duration), duration, fps, pixelsPerSecond, scrollOffset);
}
