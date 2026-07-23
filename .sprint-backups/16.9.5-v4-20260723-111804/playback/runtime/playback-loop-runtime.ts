import type {
  ProfessionalPlaybackLoopMode,
  ProfessionalPlaybackRange,
} from "../contracts";

export interface ProfessionalLoopResolution {
  readonly time: number;
  readonly looped: boolean;
  readonly completed: boolean;
}

export class PlaybackLoopRuntime {
  resolve(
    candidateTime: number,
    duration: number,
    direction: 1 | -1,
    mode: ProfessionalPlaybackLoopMode,
    range: ProfessionalPlaybackRange | null,
  ): ProfessionalLoopResolution {
    const activeRange =
      mode === "timeline"
        ? { startTime: 0, endTime: duration }
        : mode === "in-out"
          ? range
          : null;

    if (!activeRange) {
      if (direction === 1 && candidateTime >= duration) {
        return { time: duration, looped: false, completed: true };
      }
      if (direction === -1 && candidateTime <= 0) {
        return { time: 0, looped: false, completed: true };
      }
      return {
        time: Math.min(duration, Math.max(0, candidateTime)),
        looped: false,
        completed: false,
      };
    }

    if (activeRange.endTime <= activeRange.startTime) {
      throw new Error("Professional playback loop range is invalid.");
    }

    if (direction === 1 && candidateTime >= activeRange.endTime) {
      const overflow = Math.max(0, candidateTime - activeRange.endTime);
      return {
        time: Math.min(activeRange.endTime, activeRange.startTime + overflow),
        looped: true,
        completed: false,
      };
    }

    if (direction === -1 && candidateTime <= activeRange.startTime) {
      const overflow = Math.max(0, activeRange.startTime - candidateTime);
      return {
        time: Math.max(activeRange.startTime, activeRange.endTime - overflow),
        looped: true,
        completed: false,
      };
    }

    return {
      time: Math.min(activeRange.endTime, Math.max(activeRange.startTime, candidateTime)),
      looped: false,
      completed: false,
    };
  }
}
