import {
  ChevronLeft,
  CloudCheck,
  Download,
  Play,
  RefreshCw,
  Redo2,
  Sparkles,
  Undo2,
} from "lucide-react";

import Link from "next/link";

import {
  ReviewBadge,
  ReviewIconButton,
  ReviewToolbarGroup,
} from "../design-system";

import type {
  ReviewEditorHeaderView,
} from "../integration/contracts";

export interface ReviewEditorTopbarProps {
  view?: ReviewEditorHeaderView;
  refreshing?: boolean;
  commandPending?: boolean;
  onRefresh?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
}

export function ReviewEditorTopbar({
  view,
  refreshing = false,
  commandPending = false,
  onRefresh,
  onUndo,
  onRedo,
}: ReviewEditorTopbarProps) {
  const title =
    view?.title ??
    "Video bán hàng · Bản AI dựng";

  const productionId =
    view?.productionId.slice(
      0,
      8,
    ) ??
    "221e4b01";

  const duration =
    view?.durationLabel ??
    "00:28";

  return (
    <header className="flex h-14 shrink-0 items-center justify-between gap-3 border-b border-[var(--review-border)] bg-[var(--review-bg-elevated)] px-3 md:px-4">
      <div className="flex min-w-0 items-center gap-2.5">
        <Link
          href="/productions"
          aria-label="Quay lại danh sách production"
          className="inline-flex size-9 shrink-0 items-center justify-center rounded-[10px] text-[var(--review-text-muted)] transition hover:bg-[var(--review-surface-hover)] hover:text-[var(--review-text)]"
        >
          <ChevronLeft className="size-4" />
        </Link>

        <div className="flex size-8 shrink-0 items-center justify-center rounded-[10px] bg-[var(--review-accent)] text-white shadow-[var(--review-shadow-accent)]">
          <Sparkles className="size-4" />
        </div>

        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h1 className="truncate text-sm font-semibold">
              {title}
            </h1>

            <ReviewBadge
              tone="brand"
              className="hidden sm:inline-flex"
            >
              AI Cut
            </ReviewBadge>
          </div>

          <p className="truncate text-[10px] text-[var(--review-text-subtle)]">
            Production{" "}
            {productionId} ·{" "}
            {duration}
          </p>
        </div>
      </div>

      <div className="hidden items-center gap-2 lg:flex">
        <ReviewToolbarGroup>
          <ReviewIconButton
            aria-label="Hoàn tác"
            size="sm"
            onClick={onUndo}
            disabled={
              commandPending ||
              !onUndo ||
              !view?.canUndo
            }
          >
            <Undo2 />
          </ReviewIconButton>

          <ReviewIconButton
            aria-label="Làm lại"
            size="sm"
            onClick={onRedo}
            disabled={
              commandPending ||
              !onRedo ||
              !view?.canRedo
            }
          >
            <Redo2 />
          </ReviewIconButton>
        </ReviewToolbarGroup>

        <ReviewBadge
          tone={
            commandPending
              ? "brand"
              : view?.statusTone ??
                "success"
          }
          dot
        >
          <CloudCheck className="size-3" />

          {commandPending
            ? "Đang chỉnh sửa"
            : view?.statusLabel ??
              "Đã lưu"}
        </ReviewBadge>
      </div>

      <div className="flex shrink-0 items-center gap-1.5">
        <ReviewIconButton
          aria-label="Xem thử video"
          variant="secondary"
          size="sm"
        >
          <Play />
        </ReviewIconButton>

        <ReviewIconButton
          aria-label="Làm mới workspace"
          size="sm"
          onClick={onRefresh}
          disabled={
            !onRefresh ||
            refreshing ||
            commandPending
          }
        >
          <RefreshCw
            className={
              refreshing
                ? "animate-spin"
                : undefined
            }
          />
        </ReviewIconButton>

        <Link
          href="/export"
          className="inline-flex h-8 items-center justify-center gap-1.5 rounded-lg bg-[var(--review-accent)] px-3 text-xs font-semibold text-white shadow-[var(--review-shadow-accent)] transition hover:bg-[var(--review-accent-hover)]"
        >
          <Download className="size-3.5" />

          <span className="hidden sm:inline">
            Xuất video
          </span>
        </Link>
      </div>
    </header>
  );
}