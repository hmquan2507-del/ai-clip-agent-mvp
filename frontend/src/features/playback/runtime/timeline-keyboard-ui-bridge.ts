import type {
  TimelineKeyboardDispatchPayload,
  TimelineKeyboardDispatchResult,
  TimelineKeyboardEvent,
  TimelineKeyboardRuntime,
} from "../contracts/professional-timeline-keyboard-contracts";

export interface TimelineKeyboardUiBridge {
  dispatch(
    event: TimelineKeyboardEvent,
    payload?: TimelineKeyboardDispatchPayload,
  ): TimelineKeyboardDispatchResult;
}

export function createTimelineKeyboardUiBridge(
  runtime: TimelineKeyboardRuntime,
): TimelineKeyboardUiBridge {
  return {
    dispatch: (event, payload) => runtime.dispatch(event, payload),
  };
}
