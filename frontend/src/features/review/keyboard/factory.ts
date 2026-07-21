import {
  ReviewTimelineKeyboardShortcutRuntime,
  type ReviewTimelineKeyboardRuntimeOptions,
} from "./runtime";

export function createReviewTimelineKeyboardShortcutRuntime(
  options:
    ReviewTimelineKeyboardRuntimeOptions = {},
): ReviewTimelineKeyboardShortcutRuntime {
  return new ReviewTimelineKeyboardShortcutRuntime(
    options,
  );
}
