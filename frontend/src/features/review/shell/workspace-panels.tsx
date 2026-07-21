import {
  Captions,
  ChevronDown,
  Crop,
  Maximize2,
  Play,
  RefreshCw,
  RotateCcw,
  SlidersHorizontal,
  Sparkles,
  Volume2,
  WandSparkles,
} from "lucide-react";

import {
  ReviewBadge,
  ReviewButton,
  ReviewIconButton,
  ReviewPanel,
  ReviewPanelBody,
  ReviewPanelHeader,
  ReviewPanelTitle,
  ReviewToolbarGroup,
} from "../design-system";
import type {
  ReviewAISuggestionIntent,
  ReviewInspectorView,
  ReviewPreviewView,
} from "../integration/contracts";

export interface ReviewPreviewStageProps {
  view?: ReviewPreviewView;
}

export function ReviewPreviewStage({ view }: ReviewPreviewStageProps) {
  const headline = view?.headline ?? "VIDEO KHÔNG RA ĐƠN";
  const subtitle =
    view?.subtitle ?? "Hook mạnh giúp người xem dừng lại ngay từ giây đầu tiên";

  return (
    <section className="relative flex min-h-0 flex-1 flex-col overflow-hidden bg-[var(--review-bg)]">
      <div className="flex h-11 shrink-0 items-center justify-between border-b border-[var(--review-border-subtle)] px-3">
        <ReviewToolbarGroup>
          <ReviewIconButton aria-label="Chọn công cụ" size="sm" variant="secondary">
            <SlidersHorizontal />
          </ReviewIconButton>
          <ReviewIconButton aria-label="Cắt khung" size="sm">
            <Crop />
          </ReviewIconButton>
          <ReviewIconButton aria-label="Đặt lại khung" size="sm">
            <RotateCcw />
          </ReviewIconButton>
        </ReviewToolbarGroup>

        <button
          type="button"
          className="flex items-center gap-1 text-[11px] text-[var(--review-text-muted)]"
        >
          Fit 58% <ChevronDown className="size-3" />
        </button>

        <ReviewIconButton aria-label="Toàn màn hình" size="sm">
          <Maximize2 />
        </ReviewIconButton>
      </div>

      <div className="relative flex min-h-[250px] flex-1 items-center justify-center overflow-hidden px-5 py-5">
        <div className="absolute inset-0 opacity-35 [background-image:linear-gradient(var(--review-timeline-grid)_1px,transparent_1px),linear-gradient(90deg,var(--review-timeline-grid)_1px,transparent_1px)] [background-size:24px_24px]" />

        <div className="relative flex h-full max-h-[530px] min-h-[230px] aspect-[9/16] items-center justify-center overflow-hidden rounded-[18px] border border-white/10 bg-[linear-gradient(155deg,#242044_0%,#101521_52%,#071c25_100%)] shadow-[0_28px_80px_rgb(0_0_0/55%)]">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgb(124_92_255/32%),transparent_42%)]" />

          {view?.available && view.videoUrl ? (
            // Playback synchronization is implemented in Sprint 16.5.
            <video
              aria-label="Video preview"
              src={view.videoUrl}
              poster={view.thumbnailUrl ?? undefined}
              preload="metadata"
              playsInline
              className="absolute inset-0 size-full object-contain"
            />
          ) : null}

          <div className="absolute left-4 top-4">
            <ReviewBadge tone="brand" dot>
              AI Preview
            </ReviewBadge>
          </div>

          <div className="relative px-7 text-center">
            <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-[var(--review-cyan)]">
              {view?.eyebrow ?? "3 giây đầu quyết định tất cả"}
            </p>
            <h2 className="mt-3 text-2xl font-black leading-[1.05] tracking-[-0.04em] text-white sm:text-3xl">
              {headline}
            </h2>
            <div className="mx-auto mt-5 h-1 w-16 rounded-full bg-[var(--review-cyan)]" />
          </div>

          <div className="absolute bottom-5 left-4 right-4 rounded-xl bg-black/65 px-3 py-2 text-center text-[11px] font-semibold leading-4 text-white backdrop-blur">
            {subtitle}
          </div>
        </div>
      </div>

      <div className="absolute bottom-3 left-1/2 flex -translate-x-1/2 items-center gap-2 rounded-full border border-[var(--review-border-strong)] bg-[var(--review-surface-floating)] p-1.5 shadow-[var(--review-shadow-floating)] backdrop-blur-xl">
        <ReviewIconButton aria-label="Âm lượng" size="sm">
          <Volume2 />
        </ReviewIconButton>
        <ReviewIconButton aria-label="Phát video" variant="primary">
          <Play />
        </ReviewIconButton>
        <span className="min-w-20 px-1 font-mono text-[10px] text-[var(--review-text-muted)]">
          {view?.currentTimeLabel ?? "00:03.18"} / {view?.durationLabel ?? "00:28"}
        </span>
      </div>
    </section>
  );
}

export interface ReviewInspectorPanelProps {
  view?: ReviewInspectorView;
  pending?: boolean;
  onSuggestionIntent?: (
    intent: ReviewAISuggestionIntent,
  ) => void;
}

export function ReviewInspectorPanel({
  view,
  pending = false,
  onSuggestionIntent,
}: ReviewInspectorPanelProps) {
  const hasSelection = Boolean(view?.selectedClipId);
  const suggestionReview =
    view?.suggestionReview;
  const suggestions =
    suggestionReview?.suggestions ?? [];

  return (
    <aside className="min-h-0 overflow-y-auto border-l border-[var(--review-border)] bg-[var(--review-bg-elevated)] max-xl:hidden">
      <div className="sticky top-0 z-10 flex h-11 items-center border-b border-[var(--review-border)] bg-[var(--review-bg-elevated)] px-2">
        {[
          ["Clip", true],
          ["Text", false],
          ["Audio", false],
          ["AI", false],
        ].map(([label, active]) => (
          <button
            key={String(label)}
            type="button"
            className={
              active
                ? "h-full border-b-2 border-[var(--review-accent)] px-2.5 text-[11px] font-semibold text-[var(--review-text)]"
                : "h-full px-2.5 text-[11px] font-medium text-[var(--review-text-subtle)]"
            }
          >
            {label}
          </button>
        ))}
      </div>

      <div className="space-y-3 p-3">
        <ReviewPanel variant="subtle">
          <ReviewPanelHeader>
            <ReviewPanelTitle>
              {view?.selectedClipLabel ?? "Chưa chọn clip"}
            </ReviewPanelTitle>
            <ReviewBadge tone="neutral">
              {view?.selectedClipRange ?? "—"}
            </ReviewBadge>
          </ReviewPanelHeader>
          <ReviewPanelBody className="space-y-3">
            <InspectorField label="Vị trí" value={view?.positionLabel ?? "X 0 · Y 0"} />
            <div className="grid grid-cols-2 gap-2">
              <InspectorField label="Tỷ lệ" value={view?.scaleLabel ?? "100%"} />
              <InspectorField label="Xoay" value={view?.rotationLabel ?? "0°"} />
            </div>
            <InspectorRange
              label="Độ trong suốt"
              value={view?.opacityLabel ?? "100%"}
            />
          </ReviewPanelBody>
        </ReviewPanel>

        <ReviewPanel variant="subtle">
          <ReviewPanelHeader>
            <ReviewPanelTitle>Phụ đề thông minh</ReviewPanelTitle>
            <Captions className="size-4 text-[var(--review-accent-text)]" />
          </ReviewPanelHeader>
          <ReviewPanelBody className="space-y-3">
            <InspectorField
              label="Preset"
              value={view?.subtitlePreset ?? "Mặc định"}
            />
          </ReviewPanelBody>
        </ReviewPanel>

        <ReviewPanel variant="active">
          <ReviewPanelHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="size-4 text-[var(--review-accent-text)]" />
              <ReviewPanelTitle>Đề xuất từ AI</ReviewPanelTitle>
            </div>
            <ReviewBadge tone="brand">
              {suggestionReview?.available
                ? `${suggestionReview.actionableCount}/${suggestionReview.count}`
                : "AI"}
            </ReviewBadge>
          </ReviewPanelHeader>
          <ReviewPanelBody className="space-y-3">
            {!suggestionReview?.available ? (
              <SuggestionEmptyState
                pending={pending}
                message="Đang tải các đề xuất phù hợp với timeline hiện tại."
                onRefresh={() =>
                  onSuggestionIntent?.({
                    operation: "refresh_suggestions",
                  })
                }
              />
            ) : suggestions.length === 0 ? (
              <SuggestionEmptyState
                pending={pending}
                message={
                  hasSelection
                    ? "AI chưa có đề xuất mới cho clip đang chọn."
                    : "AI chưa có đề xuất mới cho timeline này."
                }
                onRefresh={() =>
                  onSuggestionIntent?.({
                    operation: "regenerate_suggestions",
                  })
                }
              />
            ) : (
              <div className="space-y-2">
                {suggestions.map((suggestion) => (
                  <div
                    key={suggestion.id}
                    className={
                      suggestion.selected
                        ? "rounded-xl border border-[var(--review-accent)] bg-[var(--review-accent-soft)] p-2.5"
                        : "rounded-xl border border-[var(--review-border)] bg-[var(--review-bg)] p-2.5"
                    }
                  >
                    <button
                      type="button"
                      disabled={pending}
                      className="block w-full text-left disabled:cursor-wait"
                      onClick={() =>
                        onSuggestionIntent?.({
                          operation: "select_suggestion",
                          suggestionId: suggestion.id,
                        })
                      }
                    >
                      <span className="flex items-start justify-between gap-2">
                        <span className="text-[11px] font-semibold leading-4 text-[var(--review-text)]">
                          {suggestion.title}
                        </span>
                        {suggestion.score !== null ? (
                          <ReviewBadge tone="brand">
                            {Math.round(suggestion.score)}
                          </ReviewBadge>
                        ) : null}
                      </span>
                      <span className="mt-1 block text-[10px] leading-4 text-[var(--review-text-muted)]">
                        {suggestion.description}
                      </span>
                      {suggestion.stale ? (
                        <span className="mt-1.5 block text-[10px] font-medium text-[var(--review-warning-text)]">
                          Đề xuất đã cũ — hãy tạo lại trước khi áp dụng.
                        </span>
                      ) : null}
                    </button>

                    <div className="mt-2 flex gap-1.5">
                      <ReviewButton
                        size="sm"
                        disabled={
                          pending ||
                          !suggestion.actionable ||
                          suggestion.stale
                        }
                        onClick={() =>
                          onSuggestionIntent?.({
                            operation: "apply_suggestion",
                            suggestionId: suggestion.id,
                          })
                        }
                      >
                        <WandSparkles className="size-3.5" />
                        Áp dụng
                      </ReviewButton>
                      <ReviewButton
                        size="sm"
                        variant="ghost"
                        disabled={pending}
                        onClick={() =>
                          onSuggestionIntent?.({
                            operation: "dismiss_suggestion",
                            suggestionId: suggestion.id,
                          })
                        }
                      >
                        Bỏ qua
                      </ReviewButton>
                    </div>
                  </div>
                ))}

                <ReviewButton
                  size="sm"
                  variant="ghost"
                  disabled={pending}
                  onClick={() =>
                    onSuggestionIntent?.({
                      operation: "regenerate_suggestions",
                    })
                  }
                >
                  <RefreshCw className={pending ? "size-3.5 animate-spin" : "size-3.5"} />
                  Tạo lại đề xuất
                </ReviewButton>
              </div>
            )}
          </ReviewPanelBody>
        </ReviewPanel>
      </div>
    </aside>
  );
}

function SuggestionEmptyState({
  pending,
  message,
  onRefresh,
}: {
  pending: boolean;
  message: string;
  onRefresh(): void;
}) {
  return (
    <div className="space-y-3">
      <p className="text-xs leading-5 text-[var(--review-text-muted)]">
        {message}
      </p>
      <ReviewButton
        size="sm"
        variant="ghost"
        disabled={pending}
        onClick={onRefresh}
      >
        <RefreshCw className={pending ? "size-3.5 animate-spin" : "size-3.5"} />
        {pending ? "Đang xử lý…" : "Làm mới đề xuất"}
      </ReviewButton>
    </div>
  );
}

function InspectorField({ label, value }: { label: string; value: string }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-[10px] font-medium text-[var(--review-text-subtle)]">
        {label}
      </span>
      <span className="flex h-8 items-center rounded-lg border border-[var(--review-border)] bg-[var(--review-bg)] px-2.5 text-[11px] text-[var(--review-text-muted)]">
        {value}
      </span>
    </label>
  );
}

function InspectorRange({ label, value }: { label: string; value: string }) {
  const numericValue = Number.parseFloat(value);
  const width = Number.isFinite(numericValue)
    ? Math.min(Math.max(numericValue, 0), 100)
    : 100;

  return (
    <div>
      <div className="mb-2 flex justify-between text-[10px] text-[var(--review-text-subtle)]">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <div className="h-1.5 rounded-full bg-[var(--review-surface-3)]">
        <div
          className="h-full rounded-full bg-[var(--review-accent)]"
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}

