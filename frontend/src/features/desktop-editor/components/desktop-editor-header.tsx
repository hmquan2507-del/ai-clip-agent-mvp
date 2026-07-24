import {
  ChevronRight,
  Circle,
  History,
  Redo2,
  RefreshCw,
  Share2,
  Sparkles,
  Undo2,
} from "lucide-react";

export interface DesktopEditorHeaderProps {
  projectName?: string;
  productionTitle?: string;
  autosaveLabel?: string;
  dirty?: boolean;
  canUndo?: boolean;
  canRedo?: boolean;
  exportDisabled?: boolean;
  exportPending?: boolean;
  refreshing?: boolean;
  onUndo?: () => void;
  onRedo?: () => void;
  onHistory?: () => void;
  onShare?: () => void;
  onExport?: () => void;
  onRefresh?: () => void;
}

export function DesktopEditorHeader({
  projectName = "AI Clip Agent",
  productionTitle = "Untitled production",
  autosaveLabel,
  dirty = false,
  canUndo = false,
  canRedo = false,
  exportDisabled = false,
  exportPending = false,
  refreshing = false,
  onUndo,
  onRedo,
  onHistory,
  onShare,
  onExport,
  onRefresh,
}: DesktopEditorHeaderProps) {
  return (
    <header className="flex h-12 shrink-0 items-center justify-between gap-3 border-b border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-surface)] pl-3 pr-2">
      <div className="flex min-w-0 items-center gap-2.5">
        <span
          aria-hidden
          className="flex items-center gap-1.5"
          data-desktop-editor-window-controls="true"
        >
          <Circle className="size-2.5 fill-[#ff5f57] text-[#ff5f57]" />
          <Circle className="size-2.5 fill-[#febc2e] text-[#febc2e]" />
          <Circle className="size-2.5 fill-[#28c840] text-[#28c840]" />
        </span>

        <div className="mx-1 h-5 w-px bg-[var(--desktop-editor-border)]" />

        <div className="flex size-7 shrink-0 items-center justify-center rounded-[var(--desktop-editor-radius-control)] bg-[var(--desktop-editor-primary)]">
          <Sparkles className="size-3.5 text-white" />
        </div>

        <nav
          aria-label="Project breadcrumb"
          className="flex min-w-0 items-center gap-1.5 text-[12px] text-[var(--desktop-editor-text-muted)]"
        >
          <span className="shrink-0">{projectName}</span>
          <ChevronRight className="size-3.5 shrink-0" />
          <span className="truncate font-medium text-[var(--desktop-editor-text)]">
            {productionTitle}
          </span>
        </nav>

        <span
          className={
            dirty
              ? "shrink-0 rounded-full border border-[var(--desktop-editor-warning-border)] bg-[var(--desktop-editor-warning-soft)] px-2 py-0.5 text-[10px] font-medium text-[var(--desktop-editor-warning-text)]"
              : "shrink-0 rounded-full border border-[var(--desktop-editor-border)] px-2 py-0.5 text-[10px] font-medium text-[var(--desktop-editor-text-subtle)]"
          }
        >
          {autosaveLabel ?? (dirty ? "Unsaved changes" : "All changes saved")}
        </span>
      </div>

      <div className="flex shrink-0 items-center gap-1">
        <HeaderIconButton label="Undo" onClick={onUndo} disabled={!canUndo}>
          <Undo2 className="size-4" />
        </HeaderIconButton>
        <HeaderIconButton label="Redo" onClick={onRedo} disabled={!canRedo}>
          <Redo2 className="size-4" />
        </HeaderIconButton>
        <HeaderIconButton label="History" onClick={onHistory}>
          <History className="size-4" />
        </HeaderIconButton>
        <HeaderIconButton label="Refresh" onClick={onRefresh}>
          <RefreshCw className={refreshing ? "size-4 animate-spin" : "size-4"} />
        </HeaderIconButton>

        <div className="mx-1.5 h-5 w-px bg-[var(--desktop-editor-border)]" />

        <button
          type="button"
          onClick={onShare}
          className="rounded-[var(--desktop-editor-radius-control)] px-2.5 py-1.5 text-[12px] font-medium text-[var(--desktop-editor-text-muted)] transition hover:bg-[var(--desktop-editor-surface-hover)] hover:text-[var(--desktop-editor-text)]"
        >
          <span className="inline-flex items-center gap-1.5">
            <Share2 className="size-3.5" />
            Share
          </span>
        </button>

        <button
          type="button"
          onClick={onExport}
          disabled={exportDisabled}
          className="rounded-[var(--desktop-editor-radius-control)] bg-[var(--desktop-editor-primary)] px-3.5 py-1.5 text-[12px] font-semibold text-white transition hover:bg-[var(--desktop-editor-primary-hover)] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {exportPending ? "Exporting…" : "Export"}
        </button>
      </div>
    </header>
  );
}

function HeaderIconButton({
  label,
  onClick,
  disabled,
  children,
}: {
  label: string;
  onClick?: () => void;
  disabled?: boolean;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      disabled={disabled}
      className="flex size-7 items-center justify-center rounded-[var(--desktop-editor-radius-control)] text-[var(--desktop-editor-text-muted)] transition hover:bg-[var(--desktop-editor-surface-hover)] hover:text-[var(--desktop-editor-text)] disabled:cursor-not-allowed disabled:opacity-40"
    >
      {children}
    </button>
  );
}
