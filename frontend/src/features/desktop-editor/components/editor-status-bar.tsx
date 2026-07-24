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

export function EditorStatusBar({
  zoomLabel = "100%",
  snapEnabled = true,
  fps,
  resolutionLabel = "1080×1920",
  playbackSpeedLabel = "1x",
  cursorTimeLabel,
  durationLabel,
  ready = true,
}: EditorStatusBarProps) {
  const items: Array<[string, string]> = [
    ["Zoom", zoomLabel],
    ["Snap", snapEnabled ? "On" : "Off"],
    ["FPS", fps != null ? String(fps) : "—"],
    ["Resolution", resolutionLabel],
    ["Speed", playbackSpeedLabel],
    ["Cursor", cursorTimeLabel ?? "—"],
    ["Duration", durationLabel ?? "—"],
  ];

  return (
    <footer className="flex h-6 shrink-0 items-center justify-between gap-4 border-t border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-surface)] px-4 text-[10px] text-[var(--desktop-editor-text-subtle)]">
      <div className="flex items-center gap-4">
        {items.map(([label, value]) => (
          <span key={label} className="flex items-center gap-1">
            <span className="font-medium text-[var(--desktop-editor-text-muted)]">{label}</span>
            <span>{value}</span>
          </span>
        ))}
      </div>

      <span className="flex shrink-0 items-center gap-1.5">
        <span
          aria-hidden
          className={
            ready
              ? "size-1.5 rounded-full bg-[var(--desktop-editor-success-text)]"
              : "size-1.5 rounded-full bg-[var(--desktop-editor-warning-text)]"
          }
        />
        <span className="font-medium text-[var(--desktop-editor-text-muted)]">
          {ready ? "Ready" : "Attention"}
        </span>
      </span>
    </footer>
  );
}
