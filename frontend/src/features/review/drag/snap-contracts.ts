import type {
  ReviewTimelineViewport,
} from "./contracts";

export const REVIEW_TIMELINE_SNAP_CONTRACT_VERSION =
  "16.5.3" as const;

export type ReviewTimelineSnapTargetType =
  | "clip_start"
  | "clip_end"
  | "playhead"
  | "frame";

export type ReviewTimelineSnapAlignment =
  | "start"
  | "end";

export interface ReviewTimelineSnapClip {
  clipId: string;
  trackId: string;
  startTime: number;
  endTime: number;
}

export interface ReviewTimelineSnapContext {
  enabled?: boolean;
  thresholdPixels: number;
  playheadTime?: number | null;
  clips: ReviewTimelineSnapClip[];
  includeFrames?: boolean;
  includePlayhead?: boolean;
  includeClipEdges?: boolean;
}

export interface ProjectReviewTimelineSnapInput {
  sourceClipId: string;
  targetTrackId: string;
  projectedStartTime: number;
  clipDuration: number;
  timelineDuration: number;
  fps: number;
  viewport: ReviewTimelineViewport;
  context: ReviewTimelineSnapContext;
}

export interface ReviewTimelineSnapCandidate {
  targetType: ReviewTimelineSnapTargetType;
  targetId: string;
  targetTime: number;
  alignment: ReviewTimelineSnapAlignment;
  snappedStartTime: number;
  distanceTime: number;
  distancePixels: number;
}

export interface ReviewTimelineSnapResult {
  contractVersion:
    typeof REVIEW_TIMELINE_SNAP_CONTRACT_VERSION;
  rawStartTime: number;
  snappedStartTime: number;
  snappedEndTime: number;
  thresholdTime: number;
  snapped: boolean;
  candidate:
    ReviewTimelineSnapCandidate | null;
  consideredCandidateCount: number;
}

export interface ReviewTimelineSnapProjector {
  project(
    input: ProjectReviewTimelineSnapInput,
  ): ReviewTimelineSnapResult;
}
