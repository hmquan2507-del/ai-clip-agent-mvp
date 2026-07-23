export function clampUnit(value: number): number {
  if (!Number.isFinite(value)) throw new Error("volume must be a finite number.");
  return Math.min(1, Math.max(0, value));
}

export function timelineToAudioSourceTime(
  playbackTime: number,
  startTime: number,
  sourceOffset: number,
): number {
  return Math.max(0, playbackTime - startTime + sourceOffset);
}

export function isAudioTrackActive(
  playbackTime: number,
  startTime: number,
  endTime: number,
): boolean {
  return playbackTime >= startTime && playbackTime < endTime;
}

export function createAudioDriftThreshold(fps: number, requested?: number): number {
  if (!Number.isFinite(fps) || fps <= 0) throw new Error("fps must be positive.");
  return Math.max(requested ?? 0, 1 / fps, 0.04);
}
