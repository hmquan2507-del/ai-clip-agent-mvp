"use client";

import type {
  MouseEvent,
  PointerEvent as ReactPointerEvent,
} from "react";
import {
  Fragment,
  useRef,
} from "react";

import {
  Captions,
  ChevronDown,
  Clapperboard,
  ClipboardCopy,
  ClipboardPaste,
  ClipboardX,
  Eraser,
  Files,
  History,
  ImagePlus,
  Layers3,
  Lock,
  Minus,
  MoveLeft,
  MoveRight,
  Music2,
  Plus,
  Scissors,
  Trash2,
  Volume2,
  ZoomIn,
  type LucideIcon,
} from "lucide-react";

import type {
  ReviewClipboardOperation,
  ReviewTimelineCommandOperation,
} from "../api";

import {
  ReviewIconButton,
  ReviewToolbarGroup,
  reviewClassNames,
} from "../design-system";

import type {
  ReviewTimelineClipTone,
  ReviewTimelineClipDragMoveIntent,
  ReviewTimelineClipDragStartIntent,
  ReviewTimelineClipDragView,
  ReviewTimelineClipTrimMoveIntent,
  ReviewTimelineClipTrimStartIntent,
  ReviewTimelineClipTrimView,
  ReviewTimelineClipboardIntent,
  ReviewTimelineCommandIntent,
  ReviewTimelineSelectionIntent,
  ReviewTimelineTrackView,
  ReviewTimelineView,
} from "../integration/contracts";
import type {
  ReviewTimelineDragCancelReason,
  ReviewTimelineTrackLane,
  ReviewTimelineViewport,
} from "../drag";
import type {
  ReviewTimelineTrimCancelReason,
  ReviewTimelineTrimHandle,
} from "../trim";
import {
  useReviewTimelineViewport,
} from "../viewport";

import {
  rulerMarks,
  timelineTracks,
} from "./data";

const clipToneClasses:
  Record<
    ReviewTimelineClipTone,
    string
  > = {
    video:
      "border-[#8d7cff]/40 bg-[var(--review-clip-video)]",

    broll:
      "border-[#36bddc]/35 bg-[var(--review-clip-broll)]",

    subtitle:
      "border-[#edb456]/35 bg-[var(--review-clip-subtitle)]",

    audio:
      "border-[#56d5a7]/35 bg-[var(--review-clip-audio)]",
  };

export interface ReviewTimelinePanelProps {
  view?: ReviewTimelineView;
  selecting?: boolean;
  commandPending?: boolean;
  clipboardPending?: boolean;
  drag?: ReviewTimelineClipDragView;
  trim?: ReviewTimelineClipTrimView;

  pendingCommand:
    ReviewTimelineCommandOperation | null;

  pendingClipboardOperation:
    ReviewClipboardOperation | null;

  onSelectClip?: (
    intent:
      ReviewTimelineSelectionIntent,
  ) => void;

  onTimelineCommand?: (
    intent:
      ReviewTimelineCommandIntent,
  ) => void;

  onClipboardCommand?: (
    intent:
      ReviewTimelineClipboardIntent,
  ) => void;

  onClipDragStart?: (
    intent: ReviewTimelineClipDragStartIntent,
  ) => void;

  onClipDragMove?: (
    intent: ReviewTimelineClipDragMoveIntent,
  ) => void;

  onClipDragDrop?: () => void;

  onClipDragCancel?: (
    reason?: ReviewTimelineDragCancelReason,
  ) => void;

  onClipTrimStart?: (
    intent: ReviewTimelineClipTrimStartIntent,
  ) => void;

  onClipTrimMove?: (
    intent: ReviewTimelineClipTrimMoveIntent,
  ) => void;

  onClipTrimDrop?: () => void;

  onClipTrimCancel?: (
    reason?: ReviewTimelineTrimCancelReason,
  ) => void;
}

export function ReviewTimelinePanel({
  view,
  selecting = false,
  commandPending = false,
  clipboardPending = false,
  drag,
  trim,
  pendingCommand,
  pendingClipboardOperation,
  onSelectClip,
  onTimelineCommand,
  onClipboardCommand,
  onClipDragStart,
  onClipDragMove,
  onClipDragDrop,
  onClipDragCancel,
  onClipTrimStart,
  onClipTrimMove,
  onClipTrimDrop,
  onClipTrimCancel,
}: ReviewTimelinePanelProps) {
  const timelineCanvasRef =
    useRef<HTMLDivElement | null>(null);
  const timelineScrollRef =
    useRef<HTMLDivElement | null>(null);
  const timelineLabelsRef =
    useRef<HTMLDivElement | null>(null);
  const laneElementsRef = useRef(
    new Map<string, HTMLDivElement>(),
  );
  const activePointerRef =
    useRef<number | null>(null);
  const activeTrimPointerRef =
    useRef<number | null>(null);
  const pointerOriginRef = useRef<{
    clientX: number;
    clientY: number;
  } | null>(null);
  const suppressClickRef =
    useRef(false);

  const timelineViewport =
    useReviewTimelineViewport({
      duration: view?.duration ?? 30,
      scrollRef: timelineScrollRef,
      labelsRef: timelineLabelsRef,
    });
  const viewportState =
    timelineViewport.state;
  const tracks:
    ReviewTimelineTrackView[] =
      view?.tracks ??
      timelineTracks.map(
        (track) => ({
          id: track.id,
          label: track.label,
          trackType: track.id,
          locked: false,
          muted: false,

          clips:
            track.clips.map(
              (clip) => ({
                ...clip,
                trackId: track.id,
                clipType:
                  fallbackClipType(
                    track.id,
                  ),
                startTime:
                  clip.start,
                endTime:
                  clip.start +
                  clip.width,
                duration:
                  clip.width,
                editable: true,
                selected: false,
              }),
            ),
        }),
      );

  const marks =
    view?.rulerMarks ??
    rulerMarks;

  const trackCount =
    view?.trackCount ??
    tracks.length;

  const clipCount =
    view?.clipCount ??
    tracks.reduce(
      (total, track) =>
        total +
        track.clips.length,
      0,
    );

  const playhead =
    view?.playheadPercent ??
    12.4;

  const activeDragSource =
    drag?.active
      ? drag.state.session?.source ?? null
      : null;
  const activeDragClip = activeDragSource
    ? tracks
        .flatMap((track) => track.clips)
        .find(
          (clip) =>
            clip.id ===
            activeDragSource.clipId,
        ) ?? null
    : null;
  const dragProjection =
    drag?.active
      ? drag.state.projection
      : null;
  const crossTrackDrag = Boolean(
    activeDragSource &&
      activeDragClip &&
      dragProjection?.valid &&
      dragProjection.targetTrackId &&
      dragProjection.targetTrackId !==
        activeDragSource.trackId,
  );
  const activeTrimSource =
    trim?.active
      ? trim.state.session?.source ?? null
      : null;
  const trimProjection =
    trim?.active
      ? trim.state.projection
      : null;

  const target =
    view?.commandTarget ??
    null;

  const clipboard =
    view?.clipboard ?? {
      selectedClipIds: [],
      pasteTime: 0,
      available: false,
      itemCount: 0,
      historyEntryCount: 0,
      latestHistoryEntryId: null,
      canCopy: false,
      canCut: false,
      canPaste: false,
      canClear: false,
      canRestoreHistory: false,
      canClearHistory: false,
    };

  const controlsDisabled =
    selecting ||
    commandPending ||
    clipboardPending ||
    Boolean(drag?.active) ||
    Boolean(trim?.active) ||
    !onTimelineCommand;

  const clipboardControlsDisabled =
    selecting ||
    commandPending ||
    clipboardPending ||
    Boolean(drag?.active) ||
    Boolean(trim?.active) ||
    !onClipboardCommand;

  const canEditTarget =
    Boolean(
      target?.editable,
    ) &&
    !controlsDisabled;

  const multiSelectedClipIds =
    clipboard.selectedClipIds;
  const hasMultiSelection =
    multiSelectedClipIds.length > 1;
  const canEditMultiSelection =
    hasMultiSelection &&
    clipboard.canCut &&
    !controlsDisabled;

  const canSplit =
    canEditTarget &&
    !hasMultiSelection &&
    Boolean(
      target?.canSplit &&
      target.splitTime !==
        null,
    );

  const canCloseGap =
    canEditTarget &&
    target?.gapBefore !==
      null;

  const handleClipClick = (
  event:
    MouseEvent<HTMLButtonElement>,
  clipId: string,
) => {
  if (suppressClickRef.current) {
    suppressClickRef.current = false;
    event.preventDefault();
    event.stopPropagation();
    return;
  }

  if (
    selecting ||
    commandPending ||
    !onSelectClip
  ) {
    return;
  }

  const additive =
    event.ctrlKey ||
    event.metaKey;

  onSelectClip({
    clipId,
    additive,
    moveCursor: true,
  });
};

  const measureDragGeometry = ():
    {
      viewport: ReviewTimelineViewport;
      lanes: ReviewTimelineTrackLane[];
    } | null => {
      const canvas =
        timelineCanvasRef.current;
      const scrollElement =
        timelineScrollRef.current;
      const labelsElement =
        timelineLabelsRef.current;

      if (
        !canvas ||
        !scrollElement ||
        !labelsElement
      ) {
        return null;
      }

      const canvasRect =
        canvas.getBoundingClientRect();
      const scrollRect =
        scrollElement.getBoundingClientRect();
      const labelsWidth =
        labelsElement.getBoundingClientRect().width;
      const lanes = tracks.flatMap(
        (track) => {
          const element =
            laneElementsRef.current.get(
              track.id,
            );

          if (!element) {
            return [];
          }

          const rect =
            element.getBoundingClientRect();

          return [{
            trackId: track.id,
            trackType:
              track.trackType,
            top: rect.top,
            height: rect.height,
            locked: track.locked,
          }];
        },
      );

      return {
        viewport: {
          left:
            scrollRect.left + labelsWidth,
          top: canvasRect.top + 28,
          width:
            viewportState.viewportWidth,
          height: Math.max(
            1,
            canvasRect.height - 28,
          ),
          scrollLeft:
            viewportState.scrollLeft,
          contentWidth:
            viewportState.contentWidth,
        },
        lanes,
      };
    };

  const beginClipDrag = (
    event:
      ReactPointerEvent<HTMLButtonElement>,
    clipId: string,
    editable: boolean,
  ) => {
    if (
      event.button !== 0 ||
      !editable ||
      selecting ||
      commandPending ||
      clipboardPending ||
      drag?.active ||
      trim?.active ||
      !onClipDragStart
    ) {
      return;
    }

    const geometry =
      measureDragGeometry();
    if (!geometry) {
      return;
    }

    activePointerRef.current =
      event.pointerId;
    pointerOriginRef.current = {
      clientX: event.clientX,
      clientY: event.clientY,
    };
    suppressClickRef.current = false;
    event.currentTarget.setPointerCapture(
      event.pointerId,
    );

    onClipDragStart({
      clipId,
      pointer: {
        clientX: event.clientX,
        clientY: event.clientY,
      },
      ...geometry,
    });
  };

  const beginClipTrim = (
    event: ReactPointerEvent<HTMLButtonElement>,
    clipId: string,
    handle: ReviewTimelineTrimHandle,
    editable: boolean,
  ) => {
    event.preventDefault();
    event.stopPropagation();

    if (
      event.button !== 0 ||
      !editable ||
      selecting ||
      commandPending ||
      clipboardPending ||
      drag?.active ||
      trim?.active ||
      !onClipTrimStart
    ) {
      return;
    }

    const geometry = measureDragGeometry();
    if (!geometry) return;

    activeTrimPointerRef.current =
      event.pointerId;
    suppressClickRef.current = true;
    event.currentTarget.setPointerCapture(
      event.pointerId,
    );

    onClipTrimStart({
      clipId,
      handle,
      pointer: {
        clientX: event.clientX,
        clientY: event.clientY,
      },
      viewport: geometry.viewport,
    });
  };

  const moveClipTrim = (
    event: ReactPointerEvent<HTMLButtonElement>,
  ) => {
    event.stopPropagation();
    if (
      activeTrimPointerRef.current !==
        event.pointerId ||
      !onClipTrimMove
    ) {
      return;
    }

    const geometry = measureDragGeometry();
    if (!geometry) return;

    onClipTrimMove({
      pointer: {
        clientX: event.clientX,
        clientY: event.clientY,
      },
      viewport: geometry.viewport,
    });
  };

  const dropClipTrim = (
    event: ReactPointerEvent<HTMLButtonElement>,
  ) => {
    event.preventDefault();
    event.stopPropagation();
    if (
      activeTrimPointerRef.current !==
      event.pointerId
    ) {
      return;
    }

    if (
      event.currentTarget.hasPointerCapture(
        event.pointerId,
      )
    ) {
      event.currentTarget.releasePointerCapture(
        event.pointerId,
      );
    }

    activeTrimPointerRef.current = null;
    onClipTrimDrop?.();
  };

  const cancelClipTrim = (
    event: ReactPointerEvent<HTMLButtonElement>,
  ) => {
    event.stopPropagation();
    if (
      activeTrimPointerRef.current !==
      event.pointerId
    ) {
      return;
    }

    activeTrimPointerRef.current = null;
    suppressClickRef.current = true;
    onClipTrimCancel?.("pointer_cancelled");
  };

  const moveClipDrag = (
    event:
      ReactPointerEvent<HTMLButtonElement>,
  ) => {
    if (
      activePointerRef.current !==
        event.pointerId ||
      !onClipDragMove
    ) {
      return;
    }

    const geometry =
      measureDragGeometry();
    if (!geometry) {
      return;
    }

    const origin = pointerOriginRef.current;
    if (
      origin &&
      Math.hypot(
        event.clientX - origin.clientX,
        event.clientY - origin.clientY,
      ) >= 3
    ) {
      suppressClickRef.current = true;
    }

    onClipDragMove({
      pointer: {
        clientX: event.clientX,
        clientY: event.clientY,
      },
      ...geometry,
    });
  };

  const dropClipDrag = (
    event:
      ReactPointerEvent<HTMLButtonElement>,
  ) => {
    if (
      activePointerRef.current !==
      event.pointerId
    ) {
      return;
    }

    if (
      event.currentTarget.hasPointerCapture(
        event.pointerId,
      )
    ) {
      event.currentTarget.releasePointerCapture(
        event.pointerId,
      );
    }

    activePointerRef.current = null;
    pointerOriginRef.current = null;
    onClipDragDrop?.();
  };

  const cancelClipDrag = (
    event:
      ReactPointerEvent<HTMLButtonElement>,
  ) => {
    if (
      activePointerRef.current !==
      event.pointerId
    ) {
      return;
    }

    activePointerRef.current = null;
    pointerOriginRef.current = null;
    suppressClickRef.current = true;
    onClipDragCancel?.(
      "pointer_cancelled",
    );
  };

  const splitSelectedClip =
    () => {
      if (
        !target ||
        !canSplit ||
        target.splitTime ===
          null
      ) {
        return;
      }

      onTimelineCommand?.({
        operation:
          "split_clip",
        clipId:
          target.clipId,
        splitTime:
          target.splitTime,
      });
    };

  const duplicateSelectedClip =
    () => {
      if (canEditMultiSelection) {
        onTimelineCommand?.({
          operation: "duplicate_clips",
          clipIds: [...multiSelectedClipIds],
        });
        return;
      }
      if (
        !target ||
        !canEditTarget
      ) {
        return;
      }

      onTimelineCommand?.({
        operation:
          "duplicate_clip",
        clipId:
          target.clipId,
      });
    };

  const deleteSelectedClip =
    () => {
      if (canEditMultiSelection) {
        onTimelineCommand?.({
          operation: "delete_clips",
          clipIds: [...multiSelectedClipIds],
        });
        return;
      }
      if (
        !target ||
        !canEditTarget
      ) {
        return;
      }

      onTimelineCommand?.({
        operation:
          "delete_clip",
        clipId:
          target.clipId,
      });
    };

  const moveSelectedClips = (direction: -1 | 1) => {
    if (!canEditMultiSelection) {
      return;
    }
    onTimelineCommand?.({
      operation: "move_clips",
      clipIds: [...multiSelectedClipIds],
      deltaTime: direction / Math.max(view?.fps ?? 30, 1),
    });
  };

  const closeGapBeforeClip =
    () => {
      const gap =
        target?.gapBefore;

      if (
        !gap ||
        !canCloseGap
      ) {
        return;
      }

      onTimelineCommand?.({
        operation:
          "close_gap",
        trackId:
          gap.trackId,
        gapStart:
          gap.startTime,
        gapEnd:
          gap.endTime,
      });
    };

  const copySelectedClips =
    () => {
      if (
        clipboardControlsDisabled ||
        !clipboard.canCopy
      ) {
        return;
      }

      onClipboardCommand?.({
        operation: "copy",
        clipIds:
          [...clipboard.selectedClipIds],
      });
    };

  const cutSelectedClips =
    () => {
      if (
        clipboardControlsDisabled ||
        !clipboard.canCut
      ) {
        return;
      }

      onClipboardCommand?.({
        operation: "cut",
        clipIds:
          [...clipboard.selectedClipIds],
      });
    };

  const pasteClips = () => {
    if (
      clipboardControlsDisabled ||
      !clipboard.canPaste
    ) {
      return;
    }

    onClipboardCommand?.({
      operation: "paste",
      atTime:
        clipboard.pasteTime,
    });
  };

  const clearClipboard = () => {
    if (
      clipboardControlsDisabled ||
      !clipboard.canClear
    ) {
      return;
    }

    onClipboardCommand?.({
      operation: "clear_content",
    });
  };

  const restoreClipboardHistory =
    () => {
      const entryId =
        clipboard.latestHistoryEntryId;

      if (
        clipboardControlsDisabled ||
        !clipboard.canRestoreHistory ||
        !entryId
      ) {
        return;
      }

      onClipboardCommand?.({
        operation: "restore_history",
        entryId,
      });
    };

  const clearClipboardHistory =
    () => {
      if (
        clipboardControlsDisabled ||
        !clipboard.canClearHistory
      ) {
        return;
      }

      onClipboardCommand?.({
        operation: "clear_history",
      });
    };

  return (
    <section
      aria-label="Timeline dựng video"
      aria-busy={
        selecting ||
        commandPending ||
        clipboardPending ||
        Boolean(drag?.active) ||
        Boolean(trim?.active)
      }
      className="h-[252px] shrink-0 border-t border-[var(--review-border)] bg-[var(--review-timeline-ruler)] max-md:h-[220px]"
    >
      <div className="flex h-10 items-center justify-between border-b border-[var(--review-border)] px-2.5">
        <div className="flex items-center gap-2">
          <ReviewToolbarGroup>
            <ReviewIconButton
              aria-label="Dịch nhóm clip sang trái một frame"
              title="Dịch nhóm sang trái"
              size="sm"
              onClick={() => moveSelectedClips(-1)}
              disabled={!canEditMultiSelection}
            >
              <MoveLeft />
            </ReviewIconButton>

            <ReviewIconButton
              aria-label="Dịch nhóm clip sang phải một frame"
              title="Dịch nhóm sang phải"
              size="sm"
              onClick={() => moveSelectedClips(1)}
              disabled={!canEditMultiSelection}
            >
              <MoveRight />
            </ReviewIconButton>

            <ReviewIconButton
              aria-label="Tách clip đang chọn"
              title="Tách clip tại con trỏ"
              size="sm"
              onClick={
                splitSelectedClip
              }
              disabled={!canSplit}
            >
              <Scissors />
            </ReviewIconButton>

            <ReviewIconButton
              aria-label="Nhân đôi clip đang chọn"
              title="Nhân đôi clip"
              size="sm"
              onClick={
                duplicateSelectedClip
              }
              disabled={
                !canEditTarget && !canEditMultiSelection
              }
            >
              <Files />
            </ReviewIconButton>

            <ReviewIconButton
              aria-label="Xóa clip đang chọn"
              title="Xóa clip"
              size="sm"
              onClick={
                deleteSelectedClip
              }
              disabled={
                !canEditTarget && !canEditMultiSelection
              }
            >
              <Trash2 />
            </ReviewIconButton>

            <ReviewIconButton
              aria-label="Đóng khoảng trống trước clip"
              title="Đóng khoảng trống trước clip"
              size="sm"
              onClick={
                closeGapBeforeClip
              }
              disabled={
                !canCloseGap
              }
            >
              <MoveLeft />
            </ReviewIconButton>
          </ReviewToolbarGroup>

          <ReviewToolbarGroup>
            <ReviewIconButton
              aria-label="Sao chép clip đã chọn"
              title="Sao chép vào clipboard"
              size="sm"
              onClick={copySelectedClips}
              disabled={
                clipboardControlsDisabled ||
                !clipboard.canCopy
              }
            >
              <ClipboardCopy />
            </ReviewIconButton>

            <ReviewIconButton
              aria-label="Cắt clip đã chọn"
              title="Cắt vào clipboard"
              size="sm"
              onClick={cutSelectedClips}
              disabled={
                clipboardControlsDisabled ||
                !clipboard.canCut
              }
            >
              <Scissors />
            </ReviewIconButton>

            <ReviewIconButton
              aria-label="Dán clip tại con trỏ"
              title={`Dán ${clipboard.itemCount} mục tại con trỏ`}
              size="sm"
              onClick={pasteClips}
              disabled={
                clipboardControlsDisabled ||
                !clipboard.canPaste
              }
            >
              <ClipboardPaste />
            </ReviewIconButton>

            <ReviewIconButton
              aria-label="Xóa nội dung clipboard"
              title="Xóa nội dung clipboard"
              size="sm"
              onClick={clearClipboard}
              disabled={
                clipboardControlsDisabled ||
                !clipboard.canClear
              }
            >
              <ClipboardX />
            </ReviewIconButton>

            <ReviewIconButton
              aria-label="Khôi phục clipboard gần nhất"
              title="Khôi phục clipboard gần nhất"
              size="sm"
              onClick={
                restoreClipboardHistory
              }
              disabled={
                clipboardControlsDisabled ||
                !clipboard.canRestoreHistory
              }
            >
              <History />
            </ReviewIconButton>

            <ReviewIconButton
              aria-label="Xóa lịch sử clipboard"
              title="Xóa lịch sử clipboard"
              size="sm"
              onClick={
                clearClipboardHistory
              }
              disabled={
                clipboardControlsDisabled ||
                !clipboard.canClearHistory
              }
            >
              <Eraser />
            </ReviewIconButton>
          </ReviewToolbarGroup>

          <span className="hidden text-[10px] text-[var(--review-text-subtle)] sm:inline">
            {trackCount} tracks ·{" "}
            {clipCount} clips
          </span>

          {selecting ? (
            <span
              role="status"
              className="text-[10px] text-[var(--review-accent-text)]"
            >
              Đang chọn clip…
            </span>
          ) : null}

          {commandPending ? (
            <span
              role="status"
              className="text-[10px] text-[var(--review-accent-text)]"
            >
              {commandLabel(
                pendingCommand,
              )}
            </span>
          ) : null}

          {clipboardPending ? (
            <span
              role="status"
              className="text-[10px] text-[var(--review-accent-text)]"
            >
              {clipboardCommandLabel(
                pendingClipboardOperation,
              )}
            </span>
          ) : null}

          {drag?.dragging ? (
            <span
              role="status"
              className="text-[10px] text-[var(--review-accent-text)]"
            >
              Đang kéo clip…
            </span>
          ) : null}

          {drag?.committing ? (
            <span
              role="status"
              className="text-[10px] text-[var(--review-accent-text)]"
            >
              Đang áp dụng vị trí…
            </span>
          ) : null}

          {drag?.failed &&
          drag.state.failure ? (
            <span
              role="alert"
              data-review-drag-failure={
                drag.state.failure.code
              }
              className="max-w-sm truncate text-[10px] text-rose-300"
              title={
                drag.state.failure.message
              }
            >
              {drag.state.failure
                .isRevisionConflict
                ? "Timeline đã thay đổi · Đã đồng bộ bản mới"
                : `Không thể di chuyển clip · ${drag.state.failure.message}`}
            </span>
          ) : null}

          {trim?.trimming ? (
            <span
              role="status"
              className="text-[10px] text-[var(--review-accent-text)]"
            >
              Đang cắt mép clip…
            </span>
          ) : null}

          {trim?.committing ? (
            <span
              role="status"
              className="text-[10px] text-[var(--review-accent-text)]"
            >
              Đang áp dụng điểm cắt…
            </span>
          ) : null}

          {trim?.failed &&
          trim.state.failure ? (
            <span
              role="alert"
              data-review-trim-failure={
                trim.state.failure.code
              }
              className="max-w-sm truncate text-[10px] text-rose-300"
              title={trim.state.failure.message}
            >
              {trim.state.failure.isRevisionConflict
                ? "Timeline đã thay đổi · Đã đồng bộ bản mới"
                : `Không thể trim clip · ${trim.state.failure.message}`}
            </span>
          ) : null}
        </div>

        <div className="flex items-center gap-2">
          <ReviewIconButton
            aria-label="Thu nhỏ timeline"
            size="sm"
            onClick={() => {
              timelineViewport.zoomOut();
            }}
            disabled={
              !viewportState.canZoomOut
            }
          >
            <Minus />
          </ReviewIconButton>

          <div className="h-1 w-20 overflow-hidden rounded-full bg-[var(--review-surface-3)] max-sm:hidden">
            <div
              className="h-full rounded-full bg-[var(--review-text-subtle)]"
              style={{
                width: `${Math.max(
                  6,
                  (viewportState.zoom / 8) * 100,
                )}%`,
              }}
            />
          </div>

          <ReviewIconButton
            aria-label="Phóng to timeline"
            size="sm"
            onClick={() => {
              timelineViewport.zoomIn();
            }}
            disabled={
              !viewportState.canZoomIn
            }
          >
            <Plus />
          </ReviewIconButton>

          <ReviewIconButton
            aria-label="Vừa timeline"
            size="sm"
            onClick={() => {
              timelineViewport.fit();
            }}
            title={`Vừa timeline · ${Math.round(
              viewportState.zoom * 100,
            )}%`}
          >
            <ZoomIn />
          </ReviewIconButton>
        </div>
      </div>

      <div
        ref={timelineScrollRef}
        className="grid h-[calc(100%-40px)] grid-cols-[112px_minmax(620px,1fr)] overflow-auto max-md:grid-cols-[88px_minmax(560px,1fr)]"
        data-review-timeline-zoom={
          viewportState.zoom
        }
        data-review-timeline-scroll={
          viewportState.scrollLeft
        }
        onScroll={
          timelineViewport.synchronizeScroll
        }
        onWheel={
          timelineViewport.zoomAtPointer
        }
      >
        <div
          ref={timelineLabelsRef}
          className="sticky left-0 z-20 border-r border-[var(--review-border)] bg-[var(--review-bg-elevated)]"
        >
          <div className="h-7 border-b border-[var(--review-border-subtle)]" />

          {tracks.map((track) => {
            const Icon =
              trackIcon(
                track.trackType,
              );

            return (
              <div
                key={track.id}
                className="flex h-10 items-center gap-2 border-b border-[var(--review-border-subtle)] px-2 text-[10px] text-[var(--review-text-muted)]"
              >
                <Icon className="size-3.5 shrink-0" />

                <span className="min-w-0 flex-1 truncate">
                  {track.label}
                </span>

                {track.locked ? (
                  <Lock className="size-3" />
                ) : null}

                <ChevronDown className="size-3 text-[var(--review-text-subtle)]" />
              </div>
            );
          })}
        </div>

        <div
          ref={timelineCanvasRef}
          className="relative"
          style={{
            width:
              `${viewportState.contentWidth}px`,
          }}
        >
          <div
            className="grid h-7 border-b border-[var(--review-border-subtle)] text-[9px] text-[var(--review-text-subtle)]"
            style={{
              gridTemplateColumns:
                `repeat(${marks.length}, minmax(0, 1fr))`,
            }}
          >
            {marks.map(
              (mark, index) => (
                <div
                  key={`${mark}-${index}`}
                  className="border-l border-[var(--review-timeline-grid)] px-1.5 py-1"
                >
                  {mark}
                </div>
              ),
            )}
          </div>

          {tracks.map(
            (track) => (
              <div
                key={track.id}
                ref={(element) => {
                  if (element) {
                    laneElementsRef.current.set(
                      track.id,
                      element,
                    );
                  } else {
                    laneElementsRef.current.delete(
                      track.id,
                    );
                  }
                }}
                data-review-track-id={
                  track.id
                }
                data-drag-target={
                  dragProjection?.targetTrackId ===
                  track.id
                    ? dragProjection.valid
                      ? "valid"
                      : "blocked"
                    : undefined
                }
                className={reviewClassNames(
                  "relative h-10 border-b border-[var(--review-border-subtle)] [background-image:linear-gradient(90deg,var(--review-timeline-grid)_1px,transparent_1px)] [background-size:16.666%_100%]",
                  dragProjection?.targetTrackId ===
                    track.id &&
                    dragProjection.valid &&
                    "bg-cyan-300/5 ring-1 ring-inset ring-cyan-300/40",
                  dragProjection?.targetTrackId ===
                    track.id &&
                    !dragProjection.valid &&
                    "bg-rose-400/5 ring-1 ring-inset ring-rose-400/50",
                )}
              >
                {track.clips.map(
                  (clip) => {
                    const isDragged =
                      Boolean(
                        drag?.active &&
                        drag.state.session
                          ?.source.clipId ===
                          clip.id,
                      );
                    const isTrimmed =
                      Boolean(
                        trim?.active &&
                        activeTrimSource?.clipId ===
                          clip.id,
                      );
                    const projectedStart =
                      isTrimmed &&
                      trimProjection
                        ? (
                            trimProjection
                              .projectedStartTime /
                            Math.max(
                              view?.duration ?? 1,
                              0.000001,
                            )
                          ) * 100
                        : isDragged &&
                      drag?.state.projection
                        ? (
                            drag.state.projection
                              .projectedStartTime /
                            Math.max(
                              view?.duration ?? 1,
                              0.000001,
                            )
                          ) * 100
                        : clip.start;
                    const projectedWidth =
                      isTrimmed &&
                      trimProjection
                        ? (
                            trimProjection
                              .projectedDuration /
                            Math.max(
                              view?.duration ?? 1,
                              0.000001,
                            )
                          ) * 100
                        : clip.width;
                    const handlesVisible =
                      clip.selected &&
                      clip.editable &&
                      !track.locked &&
                      !drag?.active &&
                      Boolean(onClipTrimStart);

                    return (
                    <Fragment key={clip.id}>
                    <button
                      type="button"
                      aria-label={
                        clip.selected
                          ? `${clip.label}, đang được chọn`
                          : `Chọn clip ${clip.label}`
                      }
                      aria-pressed={
                        clip.selected
                      }
                      disabled={
                        selecting ||
                        commandPending ||
                        clipboardPending ||
                        Boolean(
                          drag?.active &&
                          !isDragged,
                        ) ||
                        Boolean(trim?.active)
                      }
                      title={
                        clip.editable
                          ? "Click để chọn · Kéo để di chuyển"
                          : "Track đang khóa"
                      }
                      data-drag-phase={
                        isDragged
                          ? drag?.state.phase
                          : undefined
                      }
                      data-trim-phase={
                        isTrimmed
                          ? trim?.state.phase
                          : undefined
                      }
                      className={reviewClassNames(
                        "absolute top-1 h-8 touch-none overflow-hidden rounded-md border px-2 text-left text-[9px] font-medium text-white/90 shadow-sm transition hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--review-focus)] disabled:cursor-wait disabled:opacity-70",
                        clipToneClasses[
                          clip.tone
                        ],
                        clip.selected &&
                          "ring-2 ring-[var(--review-focus)] ring-offset-1 ring-offset-[var(--review-timeline-ruler)]",
                        clip.editable &&
                          !isDragged &&
                          "cursor-grab",
                        isDragged &&
                          "z-20 cursor-grabbing opacity-80 shadow-lg ring-2 ring-[var(--review-focus)]",
                        isDragged &&
                          crossTrackDrag &&
                          "opacity-0",
                        isTrimmed &&
                          "z-20 opacity-80 shadow-lg ring-2 ring-amber-300",
                      )}
                      style={{
                        left:
                          `${projectedStart}%`,
                        width:
                          `${projectedWidth}%`,
                      }}
                      onClick={(
                        event,
                      ) => {
                        handleClipClick(
                          event,
                          clip.id,
                        );
                      }}
                      onPointerDown={(
                        event,
                      ) => {
                        beginClipDrag(
                          event,
                          clip.id,
                          clip.editable &&
                            !track.locked,
                        );
                      }}
                      onPointerMove={
                        moveClipDrag
                      }
                      onPointerUp={
                        dropClipDrag
                      }
                      onPointerCancel={
                        cancelClipDrag
                      }
                      onKeyDown={(event) => {
                        if (
                          event.key ===
                            "Escape" &&
                          drag?.active
                        ) {
                          const pointerId =
                            activePointerRef.current;
                          if (
                            pointerId !== null &&
                            event.currentTarget
                              .hasPointerCapture(
                                pointerId,
                              )
                          ) {
                            event.currentTarget
                              .releasePointerCapture(
                                pointerId,
                              );
                          }
                          suppressClickRef.current =
                            true;
                          activePointerRef.current =
                            null;
                          pointerOriginRef.current =
                            null;
                          onClipDragCancel?.(
                            "escape_pressed",
                          );
                        }
                      }}
                    >
                      <span className="block truncate">
                        {clip.label}
                      </span>
                    </button>

                    {handlesVisible ? (
                      <>
                        <button
                          type="button"
                          aria-label={`Trim đầu clip ${clip.label}`}
                          title="Kéo để thay đổi điểm bắt đầu"
                          data-review-trim-handle="start"
                          data-trim-active={
                            isTrimmed &&
                            trim?.state.session?.handle ===
                              "start"
                              ? "true"
                              : undefined
                          }
                          className="absolute top-1 z-30 h-8 w-2 -translate-x-1/2 touch-none cursor-ew-resize rounded-l border border-amber-200/70 bg-amber-300/80 shadow-[0_0_6px_rgba(252,211,77,0.6)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-200 disabled:cursor-wait disabled:opacity-50"
                          style={{
                            left: `${projectedStart}%`,
                          }}
                          disabled={
                            selecting ||
                            commandPending ||
                            clipboardPending ||
                            Boolean(
                              trim?.active &&
                              !isTrimmed,
                            )
                          }
                          onClick={(event) => {
                            event.preventDefault();
                            event.stopPropagation();
                          }}
                          onPointerDown={(event) => {
                            beginClipTrim(
                              event,
                              clip.id,
                              "start",
                              true,
                            );
                          }}
                          onPointerMove={moveClipTrim}
                          onPointerUp={dropClipTrim}
                          onPointerCancel={cancelClipTrim}
                          onKeyDown={(event) => {
                            if (
                              event.key === "Escape" &&
                              trim?.active
                            ) {
                              const pointerId =
                                activeTrimPointerRef.current;
                              if (
                                pointerId !== null &&
                                event.currentTarget.hasPointerCapture(
                                  pointerId,
                                )
                              ) {
                                event.currentTarget.releasePointerCapture(
                                  pointerId,
                                );
                              }
                              activeTrimPointerRef.current = null;
                              suppressClickRef.current = true;
                              onClipTrimCancel?.(
                                "escape_pressed",
                              );
                            }
                          }}
                        />

                        <button
                          type="button"
                          aria-label={`Trim cuối clip ${clip.label}`}
                          title="Kéo để thay đổi điểm kết thúc"
                          data-review-trim-handle="end"
                          data-trim-active={
                            isTrimmed &&
                            trim?.state.session?.handle ===
                              "end"
                              ? "true"
                              : undefined
                          }
                          className="absolute top-1 z-30 h-8 w-2 -translate-x-1/2 touch-none cursor-ew-resize rounded-r border border-amber-200/70 bg-amber-300/80 shadow-[0_0_6px_rgba(252,211,77,0.6)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-200 disabled:cursor-wait disabled:opacity-50"
                          style={{
                            left:
                              `${projectedStart + projectedWidth}%`,
                          }}
                          disabled={
                            selecting ||
                            commandPending ||
                            clipboardPending ||
                            Boolean(
                              trim?.active &&
                              !isTrimmed,
                            )
                          }
                          onClick={(event) => {
                            event.preventDefault();
                            event.stopPropagation();
                          }}
                          onPointerDown={(event) => {
                            beginClipTrim(
                              event,
                              clip.id,
                              "end",
                              true,
                            );
                          }}
                          onPointerMove={moveClipTrim}
                          onPointerUp={dropClipTrim}
                          onPointerCancel={cancelClipTrim}
                          onKeyDown={(event) => {
                            if (
                              event.key === "Escape" &&
                              trim?.active
                            ) {
                              const pointerId =
                                activeTrimPointerRef.current;
                              if (
                                pointerId !== null &&
                                event.currentTarget.hasPointerCapture(
                                  pointerId,
                                )
                              ) {
                                event.currentTarget.releasePointerCapture(
                                  pointerId,
                                );
                              }
                              activeTrimPointerRef.current = null;
                              suppressClickRef.current = true;
                              onClipTrimCancel?.(
                                "escape_pressed",
                              );
                            }
                          }}
                        />
                      </>
                    ) : null}
                    </Fragment>
                    );
                  },
                )}

                {crossTrackDrag &&
                activeDragClip &&
                dragProjection?.targetTrackId ===
                  track.id ? (
                  <div
                    aria-hidden="true"
                    data-review-cross-track-ghost="true"
                    className={reviewClassNames(
                      "pointer-events-none absolute top-1 z-20 h-8 overflow-hidden rounded-md border px-2 py-1 text-left text-[9px] font-medium text-white/90 opacity-80 shadow-lg ring-2 ring-cyan-300",
                      clipToneClasses[
                        activeDragClip.tone
                      ],
                    )}
                    style={{
                      left: `${(
                        dragProjection.projectedStartTime /
                        Math.max(
                          view?.duration ?? 1,
                          0.000001,
                        )
                      ) * 100}%`,
                      width:
                        `${activeDragClip.width}%`,
                    }}
                  >
                    <span className="block truncate">
                      {activeDragClip.label}
                    </span>
                  </div>
                ) : null}
              </div>
            ),
          )}

          {drag?.dragging &&
          drag.state.snapResult?.snapped &&
          view?.duration ? (
            <div
              aria-hidden="true"
              data-review-snap-guide="true"
              className="pointer-events-none absolute inset-y-0 z-30 w-px bg-cyan-300 shadow-[0_0_8px_rgba(103,232,249,0.8)]"
              style={{
                left: `${(
                  drag.state.snapResult.candidate
                    ?.targetTime ?? 0
                ) / view.duration * 100}%`,
              }}
            />
          ) : null}

          <div
            className="pointer-events-none absolute inset-y-0 z-10 w-px bg-[var(--review-timeline-playhead)] shadow-[0_0_8px_var(--review-timeline-playhead)]"
            style={{
              left:
                `${playhead}%`,
            }}
          >
            <div className="absolute -left-[4px] top-0 size-2 rotate-45 rounded-[2px] bg-[var(--review-timeline-playhead)]" />
          </div>
        </div>
      </div>
    </section>
  );
}

function commandLabel(
  operation:
    ReviewTimelineCommandOperation | null,
): string {
  switch (operation) {
    case "split_clip":
      return "Đang tách clip…";

    case "duplicate_clip":
      return "Đang nhân đôi clip…";

    case "duplicate_clips":
      return "Đang nhân đôi nhóm clip…";

    case "delete_clip":
      return "Đang xóa clip…";

    case "delete_clips":
      return "Đang xóa nhóm clip…";

    case "move_clips":
      return "Đang di chuyển nhóm clip…";

    case "close_gap":
      return "Đang đóng khoảng trống…";

    case "undo":
      return "Đang hoàn tác…";

    case "redo":
      return "Đang làm lại…";

    default:
      return "Đang chỉnh sửa…";
  }
}

function clipboardCommandLabel(
  operation:
    ReviewClipboardOperation | null,
): string {
  switch (operation) {
    case "copy":
      return "Đang sao chép clip…";

    case "cut":
      return "Đang cắt clip…";

    case "paste":
      return "Đang dán clip…";

    case "restore_history":
      return "Đang khôi phục clipboard…";

    case "clear_content":
      return "Đang xóa clipboard…";

    case "clear_history":
      return "Đang xóa lịch sử clipboard…";

    default:
      return "Đang cập nhật clipboard…";
  }
}

function trackIcon(
  trackType: string,
): LucideIcon {
  if (
    trackType.includes(
      "subtitle",
    )
  ) {
    return Captions;
  }

  if (
    trackType.includes(
      "broll",
    ) ||
    trackType.includes(
      "overlay",
    )
  ) {
    return ImagePlus;
  }

  if (
    trackType.includes(
      "music",
    )
  ) {
    return Music2;
  }

  if (
    trackType.includes(
      "audio",
    ) ||
    trackType.includes(
      "voice",
    ) ||
    trackType.includes(
      "sound",
    )
  ) {
    return Volume2;
  }

  if (
    trackType.includes(
      "video",
    )
  ) {
    return Clapperboard;
  }

  return Layers3;
}

function fallbackClipType(
  trackType: string,
): string {
  if (trackType.includes("subtitle")) {
    return "subtitle";
  }
  if (
    trackType.includes("broll") ||
    trackType.includes("overlay")
  ) {
    return "broll";
  }
  if (trackType.includes("music")) {
    return "music";
  }
  if (trackType.includes("audio")) {
    return "audio";
  }
  return "video";
}
