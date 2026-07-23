export class PlaybackClockRuntime {
  private previousNowMs: number | null = null;

  reset(nowMs?: number): void {
    this.previousNowMs = nowMs ?? null;
  }

  measure(nowMs: number): number {
    if (!Number.isFinite(nowMs)) throw new Error("nowMs must be finite.");
    const deltaMs = this.previousNowMs === null ? 0 : Math.max(0, nowMs - this.previousNowMs);
    this.previousNowMs = nowMs;
    return deltaMs / 1000;
  }
}
