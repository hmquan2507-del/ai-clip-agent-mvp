import type { ProfessionalTrimClip, ProfessionalTrimPosition, TimelineGap } from "../contracts/professional-trim-contracts";

export class TimelineGapModel {
  static detect(clips: readonly (ProfessionalTrimClip | ProfessionalTrimPosition)[]): readonly TimelineGap[] {
    const tracks = new Map<string, (ProfessionalTrimClip | ProfessionalTrimPosition)[]>();
    for (const clip of clips) {
      const bucket = tracks.get(clip.trackId) ?? [];
      bucket.push(clip);
      tracks.set(clip.trackId, bucket);
    }
    const gaps: TimelineGap[] = [];
    for (const [trackId, trackClips] of tracks) {
      const sorted = [...trackClips].sort((a, b) => a.timelineStartFrame - b.timelineStartFrame || a.clipId.localeCompare(b.clipId));
      for (let index = 1; index < sorted.length; index += 1) {
        const previous = sorted[index - 1];
        const next = sorted[index];
        if (next.timelineStartFrame <= previous.timelineEndFrame) continue;
        gaps.push(Object.freeze({
          gapId: `${trackId}:${previous.timelineEndFrame}-${next.timelineStartFrame}`,
          trackId,
          startFrame: previous.timelineEndFrame,
          endFrame: next.timelineStartFrame,
          durationFrames: next.timelineStartFrame - previous.timelineEndFrame,
          previousClipId: previous.clipId,
          nextClipId: next.clipId,
        }));
      }
    }
    return Object.freeze(gaps);
  }
}
