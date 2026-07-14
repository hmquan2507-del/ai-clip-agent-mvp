import {
  AlertTriangle,
  LoaderCircle,
  RefreshCw,
  RotateCcw,
} from "lucide-react";

import {
  ReviewButton,
  ReviewEditorSurface,
  ReviewPanel,
  ReviewPanelBody,
} from "../design-system";
import type { ReviewWorkspaceRuntimeError } from "../state";

export function ReviewWorkspaceLoadingState() {
  return (
    <ReviewEditorSurface className="flex h-dvh items-center justify-center px-5">
      <div className="text-center">
        <div className="mx-auto flex size-12 items-center justify-center rounded-2xl border border-[var(--review-accent-border)] bg-[var(--review-accent-soft)] text-[var(--review-accent-text)]">
          <LoaderCircle className="size-5 animate-spin" />
        </div>
        <h1 className="mt-4 text-sm font-semibold">Đang mở AI Video Editor</h1>
        <p className="mt-1 text-xs text-[var(--review-text-subtle)]">
          Đang đồng bộ preview, timeline và phiên chỉnh sửa…
        </p>
      </div>
    </ReviewEditorSurface>
  );
}

export function ReviewWorkspaceErrorState({
  error,
  retrying,
  onRetry,
}: {
  error: ReviewWorkspaceRuntimeError | null;
  retrying: boolean;
  onRetry: () => void;
}) {
  return (
    <ReviewEditorSurface className="flex h-dvh items-center justify-center px-5">
      <ReviewPanel className="w-full max-w-md shadow-[var(--review-shadow-floating)]">
        <ReviewPanelBody className="p-6 text-center">
          <div className="mx-auto flex size-11 items-center justify-center rounded-xl border border-[var(--review-danger-border)] bg-[var(--review-danger-soft)] text-[var(--review-danger-text)]">
            <AlertTriangle className="size-5" />
          </div>
          <h1 className="mt-4 text-sm font-semibold">Không thể mở Review Workspace</h1>
          <p className="mt-2 text-xs leading-5 text-[var(--review-text-muted)]">
            {error?.message ?? "Đã xảy ra lỗi khi tải dữ liệu editor."}
          </p>
          {error?.code ? (
            <p className="mt-2 font-mono text-[10px] text-[var(--review-text-subtle)]">
              {error.code} · HTTP {error.status ?? "—"}
            </p>
          ) : null}
          <ReviewButton className="mt-5" onClick={onRetry} disabled={retrying}>
            <RefreshCw className={retrying ? "size-4 animate-spin" : "size-4"} />
            Thử mở lại
          </ReviewButton>
        </ReviewPanelBody>
      </ReviewPanel>
    </ReviewEditorSurface>
  );
}

export function ReviewWorkspaceClosedState({
  reopening,
  onReopen,
}: {
  reopening: boolean;
  onReopen: () => void;
}) {
  return (
    <ReviewEditorSurface className="flex h-dvh items-center justify-center px-5">
      <ReviewPanel className="w-full max-w-md">
        <ReviewPanelBody className="p-6 text-center">
          <RotateCcw className="mx-auto size-6 text-[var(--review-text-muted)]" />
          <h1 className="mt-3 text-sm font-semibold">Phiên chỉnh sửa đã đóng</h1>
          <p className="mt-2 text-xs text-[var(--review-text-subtle)]">
            Mở một session mới để tiếp tục review production này.
          </p>
          <ReviewButton className="mt-5" onClick={onReopen} disabled={reopening}>
            Mở lại editor
          </ReviewButton>
        </ReviewPanelBody>
      </ReviewPanel>
    </ReviewEditorSurface>
  );
}

