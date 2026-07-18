export const REVIEW_TIMELINE_TRACK_COMPATIBILITY_VERSION =
  "16.5.5" as const;

export type ReviewTimelineTrackCompatibilityReason =
  | "compatible"
  | "unknown_contract"
  | "incompatible_clip_type";

export interface ReviewTimelineTrackCompatibility {
  version:
    typeof REVIEW_TIMELINE_TRACK_COMPATIBILITY_VERSION;
  compatible: boolean;
  reason:
    ReviewTimelineTrackCompatibilityReason;
  clipType: string | null;
  trackType: string | null;
}

const COMPATIBLE_TRACK_TYPES:
  Readonly<Record<string, readonly string[]>> = {
    video: [
      "video_primary",
      "video_overlay",
    ],
    broll: [
      "broll",
      "video_overlay",
    ],
    subtitle: ["subtitle"],
    music: ["music", "audio"],
    sound_effect: [
      "sound_effect",
      "audio",
    ],
    voice: ["voice", "audio"],
    audio: [
      "audio",
      "music",
      "sound_effect",
      "voice",
    ],
    effect: [
      "effect",
      "video_overlay",
    ],
    unknown: ["unknown"],
  };

export function evaluateReviewTimelineTrackCompatibility(
  clipType: string | null | undefined,
  trackType: string | null | undefined,
): ReviewTimelineTrackCompatibility {
  const normalizedClipType =
    normalizeType(clipType);
  const normalizedTrackType =
    normalizeType(trackType);

  if (
    !normalizedClipType ||
    !normalizedTrackType
  ) {
    return {
      version:
        REVIEW_TIMELINE_TRACK_COMPATIBILITY_VERSION,
      compatible: true,
      reason: "unknown_contract",
      clipType: normalizedClipType,
      trackType: normalizedTrackType,
    };
  }

  const accepted =
    COMPATIBLE_TRACK_TYPES[
      normalizedClipType
    ];
  const compatible = Boolean(
    accepted?.includes(
      normalizedTrackType,
    ),
  );

  return {
    version:
      REVIEW_TIMELINE_TRACK_COMPATIBILITY_VERSION,
    compatible,
    reason: compatible
      ? "compatible"
      : "incompatible_clip_type",
    clipType: normalizedClipType,
    trackType: normalizedTrackType,
  };
}

function normalizeType(
  value: string | null | undefined,
): string | null {
  const normalized =
    value?.trim().toLowerCase();

  return normalized || null;
}
