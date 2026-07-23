export interface ScrubbingThrottleState { lastPreviewAtMs: number | null; lastPreviewTimeSeconds: number | null; }
export function shouldEmitScrubPreview(state: ScrubbingThrottleState, nowMs: number, timeSeconds: number, intervalMs: number, minimumDeltaSeconds: number): boolean {
  if (state.lastPreviewAtMs === null || state.lastPreviewTimeSeconds === null) return true;
  return nowMs - state.lastPreviewAtMs >= intervalMs && Math.abs(timeSeconds - state.lastPreviewTimeSeconds) >= minimumDeltaSeconds;
}
