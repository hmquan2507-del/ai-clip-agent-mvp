import type {
  PlaybackBufferHealth,
  PlaybackBufferSnapshot,
  PlaybackRange,
} from "../contracts/professional-playback-contracts";

export class PlaybackBufferRuntime {
  private ranges: PlaybackRange[] = [];

  constructor(
    private targetSeconds = 6,
    private lowThresholdSeconds = 1.5,
  ) {}

  replace(ranges: PlaybackRange[]): PlaybackBufferSnapshot {
    this.ranges = this.normalize(ranges);
    return this.snapshot(0);
  }

  add(range: PlaybackRange): void {
    this.ranges = this.normalize([...this.ranges, range]);
  }

  removeBefore(timeSeconds: number): void {
    this.ranges = this.ranges
      .filter((range) => range.endSeconds > timeSeconds)
      .map((range) => ({ startSeconds: Math.max(range.startSeconds, timeSeconds), endSeconds: range.endSeconds }));
  }

  secondsAhead(timeSeconds: number): number {
    const range = this.ranges.find((item) => item.startSeconds <= timeSeconds && item.endSeconds >= timeSeconds);
    return range ? Math.max(0, range.endSeconds - timeSeconds) : 0;
  }

  snapshot(timeSeconds: number): PlaybackBufferSnapshot {
    const secondsAhead = this.secondsAhead(timeSeconds);
    let health: PlaybackBufferHealth = "empty";
    if (secondsAhead >= this.targetSeconds) health = "full";
    else if (secondsAhead >= this.lowThresholdSeconds) health = "healthy";
    else if (secondsAhead > 0) health = "low";

    return {
      buffered: this.ranges.map((range) => ({ ...range })),
      currentTimeSeconds: timeSeconds,
      secondsAhead,
      health,
    };
  }

  private normalize(ranges: PlaybackRange[]): PlaybackRange[] {
    const sorted = ranges
      .filter((range) => Number.isFinite(range.startSeconds) && Number.isFinite(range.endSeconds) && range.endSeconds > range.startSeconds)
      .map((range) => ({ ...range }))
      .sort((a, b) => a.startSeconds - b.startSeconds);
    const merged: PlaybackRange[] = [];
    for (const range of sorted) {
      const last = merged[merged.length - 1];
      if (!last || range.startSeconds > last.endSeconds) merged.push(range);
      else last.endSeconds = Math.max(last.endSeconds, range.endSeconds);
    }
    return merged;
  }
}
