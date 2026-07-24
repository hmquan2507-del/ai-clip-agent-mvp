import {
  ChevronsDown,
  ChevronsLeft,
  ChevronsRight,
  ChevronsUp,
} from "lucide-react";

export type PanelCollapseDirection = "left" | "right" | "up" | "down";

const ICON: Record<PanelCollapseDirection, typeof ChevronsLeft> = {
  left: ChevronsLeft,
  right: ChevronsRight,
  up: ChevronsUp,
  down: ChevronsDown,
};

export interface PanelCollapseButtonProps {
  /** Direction the chevron points — i.e. the direction the panel collapses toward. */
  direction: PanelCollapseDirection;
  label: string;
  onClick: () => void;
}

export function PanelCollapseButton({ direction, label, onClick }: PanelCollapseButtonProps) {
  const Icon = ICON[direction];

  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      className="flex size-6 shrink-0 items-center justify-center rounded-md text-[var(--desktop-editor-text-subtle)] transition hover:bg-[var(--desktop-editor-surface-hover)] hover:text-[var(--desktop-editor-text)]"
    >
      <Icon className="size-3.5" />
    </button>
  );
}
