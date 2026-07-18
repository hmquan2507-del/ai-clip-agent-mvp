"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  createReviewTimelineDragSessionRuntime,
  type ReviewTimelineDragCancelReason,
  type ReviewTimelineDragEnvironment,
  type ReviewTimelineDragFailure,
  type ReviewTimelineDragRuntimeState,
} from "../drag";
import {
  ReviewWorkspaceAPIError,
} from "../api";

import type {
  MoveTimelineClipInput,
  ReviewWorkspaceRuntimeState,
} from "../state";

import type {
  ReviewEditorViewModel,
  ReviewTimelineClipDragMoveIntent,
  ReviewTimelineClipDragStartIntent,
  ReviewTimelineClipDragView,
  ReviewTimelineClipView,
  ReviewTimelineTrackView,
} from "./contracts";

export interface UseReviewRuntimeClipDragInput {
  productionId: string;
  view: ReviewEditorViewModel;
  disabled?: boolean;
  moveClip(
    input: MoveTimelineClipInput,
  ): Promise<ReviewWorkspaceRuntimeState>;
}

export interface ReviewRuntimeClipDragController {
  drag: ReviewTimelineClipDragView;
  begin(
    intent: ReviewTimelineClipDragStartIntent,
  ): void;
  move(
    intent: ReviewTimelineClipDragMoveIntent,
  ): void;
  drop(): Promise<void>;
  cancel(
    reason?: ReviewTimelineDragCancelReason,
  ): void;
}

export function useReviewRuntimeClipDrag({
  productionId,
  view,
  disabled = false,
  moveClip,
}: UseReviewRuntimeClipDragInput):
  ReviewRuntimeClipDragController {
  const [runtime] = useState(
    () =>
      createReviewTimelineDragSessionRuntime(),
  );
  const [dragState, setDragState] =
    useState<ReviewTimelineDragRuntimeState>(
      () => runtime.getState(),
    );

  useEffect(
    () =>
      runtime.subscribe((state) => {
        setDragState(state);
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
        current.phase === "dragging"
      ) &&
      (
        session.productionId !==
          productionId ||
        session.timelineRevision !==
          view.timeline.revision
      )
    ) {
      runtime.cancel(
        "workspace_changed",
      );
    }
  }, [
    productionId,
    runtime,
    view.timeline.revision,
  ]);

  const buildEnvironment = useCallback(
    (
      geometry:
        ReviewTimelineClipDragMoveIntent,
    ): ReviewTimelineDragEnvironment => ({
      viewport: geometry.viewport,
      timelineDuration:
        view.timeline.duration,
      fps: view.timeline.fps,
      lanes: geometry.lanes,
      quantizeToFrame: false,
      snap: {
        thresholdPixels: 8,
        playheadTime:
          view.timeline.playheadTime,
        clips: view.timeline.tracks.flatMap(
          (track) =>
            track.clips.map(
              (clip) => ({
                clipId: clip.id,
                trackId: track.id,
                startTime:
                  clip.startTime,
                endTime:
                  clip.endTime,
              }),
            ),
        ),
      },
    }),
    [view],
  );

  const begin = useCallback(
    (
      intent:
        ReviewTimelineClipDragStartIntent,
    ) => {
      if (disabled) {
        return;
      }

      const context = findClip(
        view.timeline.tracks,
        intent.clipId,
      );

      if (
        !context ||
        !context.clip.editable ||
        context.track.locked
      ) {
        return;
      }

      runtime.arm({
        productionId,
        timelineRevision:
          view.timeline.revision,
        source: {
          clipId: context.clip.id,
          clipType:
            context.clip.clipType,
          trackId: context.track.id,
          startTime:
            context.clip.startTime,
          endTime:
            context.clip.endTime,
          duration:
            context.clip.duration,
        },
        pointer: intent.pointer,
        environment: buildEnvironment(
          intent,
        ),
      });
    },
    [
      buildEnvironment,
      disabled,
      productionId,
      runtime,
      view,
    ],
  );

  const move = useCallback(
    (
      intent:
        ReviewTimelineClipDragMoveIntent,
    ) => {
      const current = runtime.getState();
      const sourceTrackId =
        current.session?.source.trackId;

      if (
        !sourceTrackId ||
        (
          current.phase !== "armed" &&
          current.phase !== "dragging"
        )
      ) {
        return;
      }

      runtime.move({
        pointer: intent.pointer,
        environment: buildEnvironment(
          intent,
        ),
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

    if (current.phase !== "dragging") {
      return;
    }

    if (!current.projection?.valid) {
      runtime.cancel("invalid_drop");
      return;
    }

    try {
      const intent = runtime.prepareCommit();

      await moveClip({
        clip_id: intent.clipId,
        new_start_time:
          intent.newStartTime,
        target_track_id:
          intent.targetTrackId,
      });
      runtime.completeCommit();
    } catch (error) {
      if (
        runtime.getState().phase ===
        "committing"
      ) {
        runtime.failCommit(
          normalizeDragFailure(error),
        );
      }
      throw error;
    }
  }, [moveClip, runtime]);

  const cancel = useCallback(
    (
      reason:
        ReviewTimelineDragCancelReason =
          "pointer_cancelled",
    ) => {
      const phase =
        runtime.getState().phase;

      if (
        phase === "armed" ||
        phase === "dragging"
      ) {
        runtime.cancel(reason);
      }
    },
    [runtime],
  );

  return {
    drag: {
      state: dragState,
      active:
        dragState.phase === "armed" ||
        dragState.phase === "dragging" ||
        dragState.phase === "committing",
      dragging:
        dragState.phase === "dragging",
      committing:
        dragState.phase === "committing",
      failed:
        dragState.phase === "failed",
    },
    begin,
    move,
    drop,
    cancel,
  };
}

function normalizeDragFailure(
  error: unknown,
): ReviewTimelineDragFailure {
  if (
    error instanceof ReviewWorkspaceAPIError
  ) {
    return {
      code: error.isRevisionConflict
        ? "revision_conflict"
        : "command_rejected",
      message: error.message,
      technicalMessage:
        error.technicalMessage,
      isRevisionConflict:
        error.isRevisionConflict,
      expectedRevision:
        error.expectedRevision,
      currentRevision:
        error.currentRevision,
    };
  }

  if (error instanceof Error) {
    return {
      code: "unknown_error",
      message: error.message ||
        "Timeline drag command failed.",
      technicalMessage: null,
      isRevisionConflict: false,
      expectedRevision: null,
      currentRevision: null,
    };
  }

  return {
    code: "unknown_error",
    message:
      "Timeline drag command failed.",
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
      (candidate) =>
        candidate.id === clipId,
    );

    if (clip) {
      return { clip, track };
    }
  }

  return null;
}
