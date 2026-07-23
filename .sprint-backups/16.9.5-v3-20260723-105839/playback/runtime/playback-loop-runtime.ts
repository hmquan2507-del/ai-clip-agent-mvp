import type { PlaybackDirection, PlaybackLoopMode, PlaybackRange } from "../contracts/professional-playback-contracts";

export interface LoopResolution {
  timeSeconds: number;
  looped: boolean;
  ended: boolean;
}

export class PlaybackLoopRuntime {
  private mode: PlaybackLoopMode = "off";
  private range: PlaybackRange | null = null;
  private loopCount = 0;

  setMode(mode: PlaybackLoopMode, range: PlaybackRange | null = this.range): void {
    if ((mode === "in-out" || mode === "region") && !range) {
      throw new Error(`${mode} loop mode requires a range.`);
    }
    if (range && range.endSeconds <= range.startSeconds) {
      throw new Error("Loop range end must be greater than start.");
    }
    this.mode = mode;
    this.range = range;
  }

  getMode(): PlaybackLoopMode { return this.mode; }
  getRange(): PlaybackRange | null { return this.range ? { ...this.range } : null; }
  getLoopCount(): number { return this.loopCount; }
  resetCount(): void { this.loopCount = 0; }

  resolve(timeSeconds: number, durationSeconds: number, direction: PlaybackDirection): LoopResolution {
    const activeRange =
      this.mode === "timeline"
        ? { startSeconds: 0, endSeconds: durationSeconds }
        : this.mode === "in-out" || this.mode === "region"
          ? this.range
          : null;

    if (!activeRange) {
      if (direction === "forward" && timeSeconds >= durationSeconds) {
        return { timeSeconds: durationSeconds, looped: false, ended: true };
      }
      if (direction === "reverse" && timeSeconds <= 0) {
        return { timeSeconds: 0, looped: false, ended: true };
      }
      return { timeSeconds, looped: false, ended: false };
    }

    if (direction === "forward" && timeSeconds >= activeRange.endSeconds) {
      this.loopCount += 1;
      const overflow = Math.max(0, timeSeconds - activeRange.endSeconds);
      return { timeSeconds: activeRange.startSeconds + overflow, looped: true, ended: false };
    }

    if (direction === "reverse" && timeSeconds <= activeRange.startSeconds) {
      this.loopCount += 1;
      const overflow = Math.max(0, activeRange.startSeconds - timeSeconds);
      return { timeSeconds: activeRange.endSeconds - overflow, looped: true, ended: false };
    }

    return { timeSeconds, looped: false, ended: false };
  }
}
