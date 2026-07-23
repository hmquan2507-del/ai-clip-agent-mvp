import type {
  ProfessionalPlaybackBufferSnapshot,
  ProfessionalPlaybackRange,
} from "../contracts";

export class PlaybackBufferRuntime {
  private ranges: ProfessionalPlaybackRange[] = [];

  constructor(
    private readonly targetSeconds = 6,
    private readonly lowThresholdSeconds = 1.5,
  ) {}

  replace(ranges: readonly ProfessionalPlaybackRange[], currentTime = 0): ProfessionalPlaybackBufferSnapshot {
    this.ranges = normalizeRanges(ranges);
    return this.getSnapshot(currentTime);
  }

  getSnapshot(currentTime: number): ProfessionalPlaybackBufferSnapshot {
    const active = this.ranges.find(
      (range) => range.startTime <= currentTime && range.endTime >= currentTime,
    );
    const secondsAhead = active ? Math.max(0, active.endTime - currentTime) : 0;
    const health =
      secondsAhead >= this.targetSeconds
        ? "full"
        : secondsAhead >= this.lowThresholdSeconds
          ? "healthy"
          : secondsAhead > 0
            ? "low"
            : "empty";

    return {
      ranges: this.ranges.map((range) => ({ ...range })),
      currentTime,
      secondsAhead,
      health,
    };
  }
}

function normalizeRanges(
  ranges: readonly ProfessionalPlaybackRange[],
): ProfessionalPlaybackRange[] {
  const sorted = ranges
    .filter(
      (range) =>
        Number.isFinite(range.startTime) &&
        Number.isFinite(range.endTime) &&
        range.endTime > range.startTime,
    )
    .map((range) => ({ ...range }))
    .sort((left, right) => left.startTime - right.startTime);

  const merged: ProfessionalPlaybackRange[] = [];
  for (const range of sorted) {
    const previous = merged[merged.length - 1];
    if (!previous || range.startTime > previous.endTime) {
      merged.push(range);
    } else {
      merged[merged.length - 1] = {
        startTime: previous.startTime,
        endTime: Math.max(previous.endTime, range.endTime),
      };
    }
  }
  return merged;
}
