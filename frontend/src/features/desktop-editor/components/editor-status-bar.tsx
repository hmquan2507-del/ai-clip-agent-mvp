export interface EditorStatusBarProps {
  zoomLabel?: string;
  snapEnabled?: boolean;
  fps?: number;
  resolutionLabel?: string;
  playbackSpeedLabel?: string;
  cursorTimeLabel?: string;
  durationLabel?: string;
  ready?: boolean;
}

const PENDING_RUNTIME_LABEL = "Pending Runtime";

/**
 * Shell status bar — Sprint 17.2 token cutover + honesty fix.
 *
 * Zoom/Snap/Resolution/Speed have no wired runtime source today (no prop
 * feeds them from `DesktopEditorRuntimeProps`) — previously this rendered
 * hardcoded fake values ("100%", "On", "1080×1920", "1x"), which violates
 * the "never fake API or backend success" / "no fake information" rule.
 * They now render "Pending Runtime" when no real value is supplied, exactly
 * like every other unconnected surface in this app (AI Decision Actions).
 * FPS/Cursor/Duration remain real — they are wired from `view?.timeline` by
 * `DesktopEditorShell`.
 */
export function EditorStatusBar({
  zoomLabel,
  snapEnabled,
  fps,
  resolutionLabel,
  playbackSpeedLabel,
  cursorTimeLabel,
  durationLabel,
  ready = true,
}: EditorStatusBarProps) {
  const items: Array<[string, string]> = [
    ["Zoom", zoomLabel ?? PENDING_RUNTIME_LABEL],
    ["Snap", snapEnabled == null ? PENDING_RUNTIME_LABEL : snapEnabled ? "On" : "Off"],
    ["FPS", fps != null ? String(fps) : PENDING_RUNTIME_LABEL],
    ["Resolution", resolutionLabel ?? PENDING_RUNTIME_LABEL],
    ["Speed", playbackSpeedLabel ?? PENDING_RUNTIME_LABEL],
    ["Cursor", cursorTimeLabel ?? PENDING_RUNTIME_LABEL],
    ["Duration", durationLabel ?? PENDING_RUNTIME_LABEL],
  ];

  return (
    <footer
      role="contentinfo"
      aria-label="Editor status bar"
      data-editor-focus-zone="status"
      className="flex h-6 shrink-0 items-center justify-between gap-4 border-t border-[var(--ce-border-default)] bg-[var(--ce-bg-panel-raised)] px-4 text-[10px] text-[var(--ce-text-muted)]"
    >
      <div className="flex items-center gap-4">
        {items.map(([label, value]) => (
          <span key={label} className="flex items-center gap-1">
            <span className="font-medium text-[var(--ce-text-secondary)]">{label}</span>
            <span aria-label={value === PENDING_RUNTIME_LABEL ? `${label}: pending runtime` : undefined}>
              {value}
            </span>
          </span>
        ))}
      </div>

      <span role="status" className="flex shrink-0 items-center gap-1.5">
        <span
          aria-hidden
          className={
            ready
              ? "size-1.5 rounded-full bg-[var(--ce-state-success)]"
              : "size-1.5 rounded-full bg-[var(--ce-state-warning)]"
          }
        />
        <span className="font-medium text-[var(--ce-text-secondary)]">{ready ? "Ready" : "Attention"}</span>
      </span>
    </footer>
  );
}
