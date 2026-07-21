"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  ReviewWorkspaceAPIError,
} from "../api";
import type {
  ReviewWorkspaceRuntimeState,
  TrimTimelineClipEndInput,
  TrimTimelineClipStartInput,
} from "../state";
import {
  createReviewTimelineTrimSessionRuntime,
  type ReviewTimelineTrimCancelReason,
  type ReviewTimelineTrimEnvironment,
  type ReviewTimelineTrimFailure,
  type ReviewTimelineTrimRuntimeState,
} from "../trim";

import type {
  ReviewEditorViewModel,
  ReviewTimelineClipTrimMoveIntent,
  ReviewTimelineClipTrimStartIntent,
  ReviewTimelineClipTrimView,
  ReviewTimelineClipView,
  ReviewTimelineTrackView,
} from "./contracts";

export interface UseReviewRuntimeClipTrimInput {
  productionId: string;
  view: ReviewEditorViewModel;
  disabled?: boolean;
  trimClipStart(
    input: TrimTimelineClipStartInput,
  ): Promise<ReviewWorkspaceRuntimeState>;
  trimClipEnd(
    input: TrimTimelineClipEndInput,
  ): Promise<ReviewWorkspaceRuntimeState>;
}

export interface ReviewRuntimeClipTrimController {
  trim: ReviewTimelineClipTrimView;
  begin(
    intent: ReviewTimelineClipTrimStartIntent,
  ): void;
  move(
    intent: ReviewTimelineClipTrimMoveIntent,
  ): void;
  drop(): Promise<void>;
  cancel(
    reason?: ReviewTimelineTrimCancelReason,
  ): void;
}

export function useReviewRuntimeClipTrim({
  productionId,
  view,
  disabled = false,
  trimClipStart,
  trimClipEnd,
}: UseReviewRuntimeClipTrimInput):
  ReviewRuntimeClipTrimController {
  const [runtime] = useState(
    () =>
      createReviewTimelineTrimSessionRuntime(),
  );
  const [trimState, setTrimState] =
    useState<ReviewTimelineTrimRuntimeState>(
      () => runtime.getState(),
    );

  useEffect(
    () =>
      runtime.subscribe((state) => {
        setTrimState(state);
      }),
    [runtime],
  );

  useEffect(() => {
    const current = runtime.getState();
    const session = current.session;

    if (
      session &&
      (
        current.phase === "armed" ||
        current.phase === "trimming"
      ) &&
      (
        session.productionId !== productionId ||
        session.timelineRevision !==
          view.timeline.revision
      )
    ) {
      runtime.cancel("workspace_changed");
    }
  }, [
    productionId,
    runtime,
    view.timeline.revision,
  ]);

  const buildEnvironment = useCallback(
    (
      geometry: ReviewTimelineClipTrimMoveIntent,
    ): ReviewTimelineTrimEnvironment => ({
      viewport: geometry.viewport,
      timelineDuration: view.timeline.duration,
      fps: view.timeline.fps,
      minimumDuration:
        1 / Math.max(view.timeline.fps, 1),
      quantizeToFrame: true,
    }),
    [view.timeline.duration, view.timeline.fps],
  );

  const begin = useCallback(
    (
      intent: ReviewTimelineClipTrimStartIntent,
    ) => {
      if (disabled) return;

      const context = findClip(
        view.timeline.tracks,
        intent.clipId,
      );

      if (
        !context ||
        !context.clip.selected ||
        !context.clip.editable ||
        context.track.locked
      ) {
        return;
      }

      runtime.arm({
        productionId,
        timelineRevision:
          view.timeline.revision,
        handle: intent.handle,
        source: {
          clipId: context.clip.id,
          trackId: context.track.id,
          startTime: context.clip.startTime,
          endTime: context.clip.endTime,
          duration: context.clip.duration,
          editable: context.clip.editable,
          trackLocked: context.track.locked,
        },
        pointer: intent.pointer,
        environment: buildEnvironment(intent),
      });
    },
    [
      buildEnvironment,
      disabled,
      productionId,
      runtime,
      view.timeline.revision,
      view.timeline.tracks,
    ],
  );

  const move = useCallback(
    (
      intent: ReviewTimelineClipTrimMoveIntent,
    ) => {
      const phase = runtime.getState().phase;
      if (
        phase !== "armed" &&
        phase !== "trimming"
      ) {
        return;
      }

      runtime.move({
        pointer: intent.pointer,
        environment: buildEnvironment(intent),
      });
    },
    [buildEnvironment, runtime],
  );

  const drop = useCallback(async () => {
    const current = runtime.getState();

    if (current.phase === "armed") {
      runtime.reset();
      return;
    }
    if (current.phase !== "trimming") {
      return;
    }
    if (!current.projection?.valid) {
      runtime.cancel("invalid_projection");
      return;
    }

    try {
      const intent = runtime.prepareCommit();

      if (intent.operation === "trim_clip_start") {
        await trimClipStart({
          clip_id: intent.clipId,
          new_start_time: intent.newStartTime,
        });
      } else {
        await trimClipEnd({
          clip_id: intent.clipId,
          new_end_time: intent.newEndTime,
        });
      }

      runtime.completeCommit();
    } catch (error) {
      if (
        runtime.getState().phase === "committing"
      ) {
        runtime.failCommit(
          normalizeTrimFailure(error),
        );
      }
      throw error;
    }
  }, [runtime, trimClipEnd, trimClipStart]);

  const cancel = useCallback(
    (
      reason: ReviewTimelineTrimCancelReason =
        "pointer_cancelled",
    ) => {
      const phase = runtime.getState().phase;
      if (
        phase === "armed" ||
        phase === "trimming"
      ) {
        runtime.cancel(reason);
      }
    },
    [runtime],
  );

  return {
    trim: {
      state: trimState,
      active:
        trimState.phase === "armed" ||
        trimState.phase === "trimming" ||
        trimState.phase === "committing",
      trimming: trimState.phase === "trimming",
      committing: trimState.phase === "committing",
      failed: trimState.phase === "failed",
      cancelReason: trimState.cancelReason,
    },
    begin,
    move,
    drop,
    cancel,
  };
}

function normalizeTrimFailure(
  error: unknown,
): ReviewTimelineTrimFailure {
  if (error instanceof ReviewWorkspaceAPIError) {
    return {
      code: error.isRevisionConflict
        ? "revision_conflict"
        : "command_rejected",
      message: error.message,
      technicalMessage: error.technicalMessage,
      isRevisionConflict: error.isRevisionConflict,
      expectedRevision: error.expectedRevision,
      currentRevision: error.currentRevision,
    };
  }

  return {
    code: "unknown_error",
    message:
      error instanceof Error && error.message
        ? error.message
        : "Timeline trim command failed.",
    technicalMessage: null,
    isRevisionConflict: false,
    expectedRevision: null,
    currentRevision: null,
  };
}

function findClip(
  tracks: ReviewTimelineTrackView[],
  clipId: string,
): {
  clip: ReviewTimelineClipView;
  track: ReviewTimelineTrackView;
} | null {
  for (const track of tracks) {
    const clip = track.clips.find(
      (candidate) => candidate.id === clipId,
    );
    if (clip) return { clip, track };
  }
  return null;
}
