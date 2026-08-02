import { Sparkles } from "lucide-react";

/**
 * Reserved AI Director dock region — Sprint 17.2 shell scope only.
 *
 * Per `desktop-editor-ux-blueprint.md`'s canonical layout, the AI Director
 * has its own docked strip at the bottom of the Timeline Workspace. This
 * sprint reserves that grid location so 17.8 has a stable place to land the
 * real AI Director UI; it intentionally renders no input, no submission
 * path, and calls nothing — `ReviewAICommandBar` (the real, single
 * submission boundary) stays exactly where it already lives today, inside
 * `EditorAiCopilot`, untouched, until 17.8 decides how/whether to relocate
 * it. This is presentation-only placeholder space, never a second command
 * surface.
 */
export function EditorAiDirectorDock() {
  return (
    <div
      role="region"
      aria-label="AI Director (reserved, not yet implemented)"
      data-editor-focus-zone="ai-director-dock"
      className="flex h-8 shrink-0 items-center gap-2 border-t border-[var(--ce-border-subtle)] bg-[var(--ce-bg-panel)] px-3 text-[10px] text-[var(--ce-text-muted)]"
    >
      <Sparkles aria-hidden className="size-3" />
      <span>AI Director — reserved for Sprint 17.8</span>
    </div>
  );
}
