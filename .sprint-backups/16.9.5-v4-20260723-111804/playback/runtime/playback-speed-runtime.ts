import type { PlaybackDirection, PlaybackSessionState } from "../contracts";

const SPEED_LADDER = [0.25, 0.5, 1, 1.5, 2, 4, 8] as const;

export class PlaybackSpeedRuntime {
  nextShuttleSpeed(state: PlaybackSessionState, direction: PlaybackDirection): number {
    if (state.direction !== direction) return 1;
    const next = SPEED_LADDER.find((speed) => speed > state.speed + Number.EPSILON);
    return next ?? SPEED_LADDER[SPEED_LADDER.length - 1];
  }

  normalize(speed: number): number {
    if (!Number.isFinite(speed) || speed <= 0) {
      throw new Error("Professional playback speed must be positive.");
    }
    return Math.min(8, Math.max(0.25, speed));
  }
}
