import {
  ReviewTimelineTrimSessionRuntime,
  type ReviewTimelineTrimSessionRuntimeOptions,
} from "./runtime";

export function createReviewTimelineTrimSessionRuntime(
  options:
    ReviewTimelineTrimSessionRuntimeOptions = {},
): ReviewTimelineTrimSessionRuntime {
  return new ReviewTimelineTrimSessionRuntime(
    options,
  );
}
