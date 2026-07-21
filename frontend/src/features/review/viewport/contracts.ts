export const REVIEW_TIMELINE_VIEWPORT_CONTRACT_VERSION =
  "16.7.6" as const;

export interface ReviewTimelineViewportLimits {
  minimumZoom: number;
  maximumZoom: number;
  zoomStep: number;
}

export interface ReviewTimelineViewportMetrics {
  duration: number;
  viewportWidth: number;
  baseContentWidth: number;
}

export interface ReviewTimelineViewportState {
  contractVersion:
    typeof REVIEW_TIMELINE_VIEWPORT_CONTRACT_VERSION;
  zoom: number;
  scrollLeft: number;
  duration: number;
  viewportWidth: number;
  baseContentWidth: number;
  contentWidth: number;
  visibleStartTime: number;
  visibleEndTime: number;
  canZoomIn: boolean;
  canZoomOut: boolean;
  stateRevision: number;
  updatedAt: string | null;
}

export type ReviewTimelineViewportListener = (
  state: ReviewTimelineViewportState,
  previousState: ReviewTimelineViewportState,
) => void;
