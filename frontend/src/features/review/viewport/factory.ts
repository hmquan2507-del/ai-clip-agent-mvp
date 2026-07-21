import type {
  ReviewTimelineViewportRuntimeOptions,
} from "./runtime";
import {
  ReviewTimelineViewportRuntime,
} from "./runtime";

export function createReviewTimelineViewportRuntime(
  options: ReviewTimelineViewportRuntimeOptions = {},
): ReviewTimelineViewportRuntime {
  return new ReviewTimelineViewportRuntime(options);
}
