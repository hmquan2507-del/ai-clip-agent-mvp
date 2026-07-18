import type {
  MouseEvent,
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
  ReviewTimelineClipboardIntent,
  ReviewTimelineCommandIntent,
  ReviewTimelineSelectionIntent,
  ReviewTimelineTrackView,
  ReviewTimelineView,
} from "../integration/contracts";

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
}

export function ReviewTimelinePanel({
  view,
  selecting = false,
  commandPending = false,
  clipboardPending = false,
  pendingCommand,
  pendingClipboardOperation,
  onSelectClip,
  onTimelineCommand,
  onClipboardCommand,
}: ReviewTimelinePanelProps) {
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
    !onTimelineCommand;

  const clipboardControlsDisabled =
    selecting ||
    commandPending ||
    clipboardPending ||
    !onClipboardCommand;

  const canEditTarget =
    Boolean(
      target?.editable,
    ) &&
    !controlsDisabled;

  const canSplit =
    canEditTarget &&
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
        clipboardPending
      }
      className="h-[252px] shrink-0 border-t border-[var(--review-border)] bg-[var(--review-timeline-ruler)] max-md:h-[220px]"
    >
      <div className="flex h-10 items-center justify-between border-b border-[var(--review-border)] px-2.5">
        <div className="flex items-center gap-2">
          <ReviewToolbarGroup>
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
                !canEditTarget
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
                !canEditTarget
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
        </div>

        <div className="flex items-center gap-2">
          <ReviewIconButton
            aria-label="Thu nhỏ timeline"
            size="sm"
          >
            <Minus />
          </ReviewIconButton>

          <div className="h-1 w-20 overflow-hidden rounded-full bg-[var(--review-surface-3)] max-sm:hidden">
            <div className="h-full w-1/2 rounded-full bg-[var(--review-text-subtle)]" />
          </div>

          <ReviewIconButton
            aria-label="Phóng to timeline"
            size="sm"
          >
            <Plus />
          </ReviewIconButton>

          <ReviewIconButton
            aria-label="Vừa timeline"
            size="sm"
          >
            <ZoomIn />
          </ReviewIconButton>
        </div>
      </div>

      <div className="grid h-[calc(100%-40px)] grid-cols-[112px_minmax(620px,1fr)] overflow-auto max-md:grid-cols-[88px_minmax(560px,1fr)]">
        <div className="sticky left-0 z-20 border-r border-[var(--review-border)] bg-[var(--review-bg-elevated)]">
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

        <div className="relative">
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
                className="relative h-10 border-b border-[var(--review-border-subtle)] [background-image:linear-gradient(90deg,var(--review-timeline-grid)_1px,transparent_1px)] [background-size:16.666%_100%]"
              >
                {track.clips.map(
                  (clip) => (
                    <button
                      key={clip.id}
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
                        clipboardPending
                      }
                      title="Click để chọn · Ctrl/Cmd + click để chọn nhiều"
                      className={reviewClassNames(
                        "absolute top-1 h-8 overflow-hidden rounded-md border px-2 text-left text-[9px] font-medium text-white/90 shadow-sm transition hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--review-focus)] disabled:cursor-wait disabled:opacity-70",
                        clipToneClasses[
                          clip.tone
                        ],
                        clip.selected &&
                          "ring-2 ring-[var(--review-focus)] ring-offset-1 ring-offset-[var(--review-timeline-ruler)]",
                      )}
                      style={{
                        left:
                          `${clip.start}%`,
                        width:
                          `${clip.width}%`,
                      }}
                      onClick={(
                        event,
                      ) => {
                        handleClipClick(
                          event,
                          clip.id,
                        );
                      }}
                    >
                      <span className="block truncate">
                        {clip.label}
                      </span>
                    </button>
                  ),
                )}
              </div>
            ),
          )}

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

    case "delete_clip":
      return "Đang xóa clip…";

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
