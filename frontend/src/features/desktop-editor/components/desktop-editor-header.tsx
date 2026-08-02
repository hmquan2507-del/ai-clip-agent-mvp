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

/**
 * Shell header — Sprint 17.2 token cutover. Cut directly onto the `ce`
 * semantic tokens (bypassing the legacy desktop-editor alias layer per
 * `frontend-redesign-master-plan.md` §17.2); no prop/behavior change.
 */
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
    <header
      role="banner"
      aria-label="Editor header"
      data-editor-focus-zone="header"
      className="flex h-[var(--ce-dim-header-height)] shrink-0 items-center justify-between gap-3 border-b border-[var(--ce-border-default)] bg-[var(--ce-bg-panel-raised)] pl-3 pr-2"
    >
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

        <div className="mx-1 h-5 w-px bg-[var(--ce-border-default)]" />

        <div className="flex size-7 shrink-0 items-center justify-center rounded-[var(--ce-radius-sm)] bg-[var(--ce-accent-primary)]">
          <Sparkles className="size-3.5 text-white" />
        </div>

        <nav
          aria-label="Project breadcrumb"
          className="flex min-w-0 items-center gap-1.5 text-[12px] text-[var(--ce-text-secondary)]"
        >
          <span className="shrink-0">{projectName}</span>
          <ChevronRight className="size-3.5 shrink-0" />
          <span className="truncate font-medium text-[var(--ce-text-primary)]">{productionTitle}</span>
        </nav>

        <span
          role="status"
          className={
            dirty
              ? "shrink-0 rounded-[var(--ce-radius-pill)] border border-[color-mix(in_srgb,var(--ce-state-warning)_30%,transparent)] bg-[color-mix(in_srgb,var(--ce-state-warning)_12%,transparent)] px-2 py-0.5 text-[10px] font-medium text-[var(--ce-state-warning)]"
              : "shrink-0 rounded-[var(--ce-radius-pill)] border border-[var(--ce-border-default)] px-2 py-0.5 text-[10px] font-medium text-[var(--ce-text-muted)]"
          }
        >
          {autosaveLabel ?? (dirty ? "Unsaved changes" : "All changes saved")}
        </span>
      </div>

      <div className="flex shrink-0 items-center gap-1">
        <div role="group" aria-label="History" className="flex items-center gap-0.5">
          <HeaderIconButton label="Undo" onClick={onUndo} disabled={!canUndo}>
            <Undo2 className="size-4" />
          </HeaderIconButton>
          <HeaderIconButton label="Redo" onClick={onRedo} disabled={!canRedo}>
            <Redo2 className="size-4" />
          </HeaderIconButton>
          <HeaderIconButton label="History" onClick={onHistory}>
            <History className="size-4" />
          </HeaderIconButton>
        </div>

        <div className="mx-1 h-5 w-px bg-[var(--ce-border-subtle)]" />

        <div role="group" aria-label="View" className="flex items-center gap-0.5">
          <HeaderIconButton label="Refresh" onClick={onRefresh}>
            <RefreshCw className={refreshing ? "size-4 animate-spin" : "size-4"} />
          </HeaderIconButton>
        </div>

        <div className="mx-1.5 h-5 w-px bg-[var(--ce-border-subtle)]" />

        <button
          type="button"
          onClick={onShare}
          className="ce-focus-ring rounded-[var(--ce-radius-sm)] px-2.5 py-1.5 text-[12px] font-medium text-[var(--ce-text-secondary)] transition hover:bg-[var(--ce-state-hover)] hover:text-[var(--ce-text-primary)]"
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
          className="ce-focus-ring rounded-[var(--ce-radius-sm)] bg-[var(--ce-accent-primary)] px-3.5 py-1.5 text-[12px] font-semibold text-white transition hover:bg-[var(--ce-accent-primary-hover)] disabled:cursor-not-allowed disabled:opacity-50"
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
      className="ce-focus-ring flex size-7 items-center justify-center rounded-[var(--ce-radius-sm)] text-[var(--ce-text-secondary)] transition hover:bg-[var(--ce-state-hover)] hover:text-[var(--ce-text-primary)] disabled:cursor-not-allowed disabled:opacity-40"
    >
      {children}
    </button>
  );
}
