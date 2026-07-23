import type {
  ProfessionalPlaybackViewportPort,
  PlaybackSessionState,
} from "../contracts";
import type { PlayheadRuntime } from "./playhead-runtime";

export class PlaybackSyncRuntime {
  constructor(
    private readonly playhead: PlayheadRuntime,
    private readonly viewport?: ProfessionalPlaybackViewportPort,
  ) {}

  synchronize(
    state: PlaybackSessionState,
    followPlayhead: boolean,
    autoScroll: boolean,
  ): void {
    this.playhead.syncFromPlayback(state);
    if (followPlayhead && autoScroll) {
      this.viewport?.revealTime(state.currentTime, "smooth");
    }
  }
}
