import type {
  PlaybackSyncSnapshot,
  PlaybackViewportPort,
} from "../contracts/professional-playback-contracts";

export class PlaybackSyncRuntime {
  private audioSeconds = 0;
  private videoSeconds = 0;
  private viewportStartSeconds = 0;
  private viewportEndSeconds = 10;

  constructor(
    private thresholdSeconds = 0.08,
    private readonly viewport?: PlaybackViewportPort,
  ) {}

  updateMediaTimes(audioSeconds: number, videoSeconds: number): void {
    this.audioSeconds = audioSeconds;
    this.videoSeconds = videoSeconds;
  }

  setViewport(startSeconds: number, endSeconds: number): void {
    if (endSeconds <= startSeconds) throw new Error("Viewport end must be greater than start.");
    this.viewportStartSeconds = startSeconds;
    this.viewportEndSeconds = endSeconds;
  }

  synchronize(playheadSeconds: number, followPlayhead: boolean, autoScroll: boolean): PlaybackSyncSnapshot {
    const driftSeconds = this.audioSeconds - this.videoSeconds;
    const correctionSeconds = Math.abs(driftSeconds) > this.thresholdSeconds ? -driftSeconds : 0;

    this.viewport?.updatePlayhead(playheadSeconds);
    if (
      followPlayhead &&
      autoScroll &&
      (playheadSeconds < this.viewportStartSeconds || playheadSeconds > this.viewportEndSeconds)
    ) {
      this.viewport?.revealTime(playheadSeconds, "smooth");
    }

    return {
      playheadSeconds,
      audioSeconds: this.audioSeconds,
      videoSeconds: this.videoSeconds,
      driftSeconds,
      correctionSeconds,
      viewportStartSeconds: this.viewportStartSeconds,
      viewportEndSeconds: this.viewportEndSeconds,
    };
  }
}
