import {
  ReviewTimelineDragSessionRuntime,
  type ReviewTimelineDragSessionRuntimeOptions,
} from "./runtime";
import {
  ReviewTimelineSnapRuntime,
} from "./snap-runtime";

export function createReviewTimelineDragSessionRuntime(
  options:
    ReviewTimelineDragSessionRuntimeOptions = {},
): ReviewTimelineDragSessionRuntime {
  return new ReviewTimelineDragSessionRuntime(
    options,
  );
}

export function createReviewTimelineSnapRuntime():
  ReviewTimelineSnapRuntime {
  return new ReviewTimelineSnapRuntime();
}
