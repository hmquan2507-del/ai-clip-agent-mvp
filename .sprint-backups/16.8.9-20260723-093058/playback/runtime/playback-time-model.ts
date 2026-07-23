export function assertFiniteNumber(value: number, name: string): number {
  if (!Number.isFinite(value)) {
    throw new Error(`${name} must be a finite number.`);
  }
  return value;
}

export function assertPositiveNumber(value: number, name: string): number {
  assertFiniteNumber(value, name);
  if (value <= 0) {
    throw new Error(`${name} must be greater than zero.`);
  }
  return value;
}

export function assertNonNegativeNumber(value: number, name: string): number {
  assertFiniteNumber(value, name);
  if (value < 0) {
    throw new Error(`${name} must be greater than or equal to zero.`);
  }
  return value;
}

export function clampPlaybackTime(time: number, duration: number): number {
  return Math.min(duration, Math.max(0, assertFiniteNumber(time, "time")));
}

export function timeToFrame(time: number, fps: number, duration: number): number {
  const boundedTime = clampPlaybackTime(time, duration);
  const maximumFrame = Math.max(0, Math.round(duration * fps));
  return Math.min(maximumFrame, Math.max(0, Math.round(boundedTime * fps)));
}

export function frameToTime(frame: number, fps: number, duration: number): number {
  assertFiniteNumber(frame, "frame");
  const maximumFrame = Math.max(0, Math.round(duration * fps));
  const boundedFrame = Math.min(maximumFrame, Math.max(0, Math.round(frame)));
  return clampPlaybackTime(boundedFrame / fps, duration);
}
