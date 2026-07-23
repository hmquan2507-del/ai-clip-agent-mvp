import type { PlaybackDirection, PlaybackTick } from "../contracts/professional-playback-contracts";

export class PlaybackClockRuntime {
  private lastNowMs: number | null = null;

  reset(nowMs?: number): void {
    this.lastNowMs = nowMs ?? null;
  }

  tick(
    nowMs: number,
    currentTimeSeconds: number,
    speed: number,
    direction: PlaybackDirection,
    frameRate: number,
  ): PlaybackTick {
    const deltaMs = this.lastNowMs === null ? 0 : Math.max(0, nowMs - this.lastNowMs);
    this.lastNowMs = nowMs;
    const signedDelta = (deltaMs / 1000) * speed * (direction === "forward" ? 1 : -1);
    const nextTime = currentTimeSeconds + signedDelta;
    return {
      nowMs,
      deltaMs,
      currentTimeSeconds: nextTime,
      frame: Math.round(nextTime * frameRate),
      status: "playing",
    };
  }
}
