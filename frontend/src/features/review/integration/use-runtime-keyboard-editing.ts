"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  createReviewTimelineKeyboardShortcutRuntime,
  type ReviewTimelineKeyboardCommandIntent,
  type ReviewTimelineKeyboardContext,
  type ReviewTimelineKeyboardInput,
  type ReviewTimelineKeyboardPlatform,
  type ReviewTimelineKeyboardRuntimeState,
} from "../keyboard";

import type {
  ReviewEditorViewModel,
  ReviewRuntimeKeyboardEditingView,
  ReviewTimelineClipboardIntent,
  ReviewTimelineCommandIntent,
} from "./contracts";

export interface ReviewRuntimeKeyboardEditingOptions {
  productionId: string;
  view: ReviewEditorViewModel;
  disabled: boolean;
  onUndo(): void;
  onRedo(): void;
  onTimelineCommand(
    intent: ReviewTimelineCommandIntent,
  ): void;
  onClipboardCommand(
    intent: ReviewTimelineClipboardIntent,
  ): void;
}

export function useReviewRuntimeKeyboardEditing({
  productionId,
  view,
  disabled,
  onUndo,
  onRedo,
  onTimelineCommand,
  onClipboardCommand,
}: ReviewRuntimeKeyboardEditingOptions):
ReviewRuntimeKeyboardEditingView {
  const runtime = useMemo(
    () =>
      createReviewTimelineKeyboardShortcutRuntime(),
    [],
  );
  const [runtimeState, setRuntimeState] =
    useState<ReviewTimelineKeyboardRuntimeState>(
      () => runtime.getState(),
    );

  const context = useMemo(
    () =>
      buildKeyboardContext(
        productionId,
        view,
        disabled,
      ),
    [productionId, view, disabled],
  );

  const executeIntent = useCallback(
    (
      intent:
        ReviewTimelineKeyboardCommandIntent,
    ) => {
      switch (intent.operation) {
        case "undo":
          onUndo();
          return;

        case "redo":
          onRedo();
          return;

        case "split_clip":
          onTimelineCommand({
            operation: "split_clip",
            clipId: intent.clipId,
            splitTime: intent.splitTime,
          });
          return;

        case "duplicate_clip":
          if (view.timeline.clipboard.selectedClipIds.length > 1) {
            onTimelineCommand({
              operation: "duplicate_clips",
              clipIds: [...view.timeline.clipboard.selectedClipIds],
            });
            return;
          }
          onTimelineCommand({
            operation: "duplicate_clip",
            clipId: intent.clipId,
          });
          return;

        case "delete_clip":
          if (view.timeline.clipboard.selectedClipIds.length > 1) {
            onTimelineCommand({
              operation: "delete_clips",
              clipIds: [...view.timeline.clipboard.selectedClipIds],
            });
            return;
          }
          onTimelineCommand({
            operation: "delete_clip",
            clipId: intent.clipId,
          });
          return;

        case "copy":
          onClipboardCommand({
            operation: "copy",
            clipIds: [...intent.clipIds],
          });
          return;

        case "cut":
          onClipboardCommand({
            operation: "cut",
            clipIds: [...intent.clipIds],
          });
          return;

        case "paste":
          onClipboardCommand({
            operation: "paste",
            atTime: intent.atTime,
          });
      }
    },
    [
      onClipboardCommand,
      onRedo,
      onTimelineCommand,
      onUndo,
      view.timeline.clipboard.selectedClipIds,
    ],
  );

  useEffect(() => {
    return runtime.subscribe((nextState) => {
      setRuntimeState(nextState);
    });
  }, [runtime]);

  useEffect(() => {
    const handleKeyDown = (
      event: KeyboardEvent,
    ) => {
      const result = runtime.handleKeyDown(
        keyboardEventToInput(event),
        context,
      );

      if (result.preventDefault) {
        event.preventDefault();
      }

      if (result.handled && result.intent) {
        executeIntent(result.intent);
      }
    };

    const handleKeyUp = (
      event: KeyboardEvent,
    ) => {
      runtime.handleKeyUp(
        keyboardEventToInput(event),
      );
    };

    window.addEventListener(
      "keydown",
      handleKeyDown,
    );
    window.addEventListener(
      "keyup",
      handleKeyUp,
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleKeyDown,
      );
      window.removeEventListener(
        "keyup",
        handleKeyUp,
      );
    };
  }, [context, executeIntent, runtime]);

  useEffect(() => {
    return () => {
      runtime.dispose();
    };
  }, [runtime]);

  return {
    enabled: !disabled,
    state: runtimeState,
    lastOperation:
      runtimeState.lastResult?.operation ?? null,
  };
}

function buildKeyboardContext(
  productionId: string,
  view: ReviewEditorViewModel,
  disabled: boolean,
): ReviewTimelineKeyboardContext {
  const clips = view.timeline.tracks.flatMap(
    (track) => track.clips,
  );
  const activeClipId =
    view.timeline.commandTarget?.clipId ?? null;
  const activeClip =
    clips.find(
      (clip) => clip.id === activeClipId,
    ) ?? null;

  return {
    productionId,
    timelineRevision:
      view.timeline.revision,
    platform: detectKeyboardPlatform(),
    workspaceActive: true,
    busy: disabled,
    selectedClipIds: [
      ...view.timeline.clipboard.selectedClipIds,
    ],
    editableClipIds: clips
      .filter((clip) => clip.editable)
      .map((clip) => clip.id),
    activeClipId,
    cursorTime:
      view.timeline.playheadTime,
    activeClipStartTime:
      activeClip?.startTime ?? null,
    activeClipEndTime:
      activeClip?.endTime ?? null,
    canUndo: view.header.canUndo,
    canRedo: view.header.canRedo,
    canPaste:
      view.timeline.clipboard.canPaste,
  };
}

function keyboardEventToInput(
  event: KeyboardEvent,
): ReviewTimelineKeyboardInput {
  const target =
    event.target instanceof HTMLElement
      ? event.target
      : null;

  return {
    key: event.key,
    code: event.code,
    ctrlKey: event.ctrlKey,
    metaKey: event.metaKey,
    shiftKey: event.shiftKey,
    altKey: event.altKey,
    repeat: event.repeat,
    target: target
      ? {
          tagName: target.tagName,
          role: target.getAttribute("role"),
          contentEditable:
            target.isContentEditable,
        }
      : null,
  };
}

function detectKeyboardPlatform():
ReviewTimelineKeyboardPlatform {
  const platform =
    typeof navigator === "undefined"
      ? ""
      : navigator.platform.toLowerCase();

  if (platform.includes("mac")) {
    return "macos";
  }

  if (platform.includes("linux")) {
    return "linux";
  }

  return "windows";
}
