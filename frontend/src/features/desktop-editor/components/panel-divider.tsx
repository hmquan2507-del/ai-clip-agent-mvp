"use client";

import { useLayoutResizer, type LayoutResizerOrientation } from "./layout-resizer";

export interface PanelDividerProps {
  orientation: LayoutResizerOrientation;
  value: number;
  defaultValue: number;
  min: number;
  max: number;
  onChange: (next: number) => void;
  invert?: boolean;
  label: string;
}

/**
 * Draggable separator between two panels. Double-click resets to the default
 * size. Purely a layout control — no editing/runtime behavior.
 */
export function PanelDivider({
  orientation,
  value,
  defaultValue,
  min,
  max,
  onChange,
  invert = false,
  label,
}: PanelDividerProps) {
  const { onPointerDown, onDoubleClick } = useLayoutResizer({
    orientation,
    value,
    defaultValue,
    min,
    max,
    onChange,
    invert,
  });

  return (
    <div
      role="separator"
      aria-label={label}
      aria-orientation={orientation === "horizontal" ? "vertical" : "horizontal"}
      aria-valuenow={Math.round(value)}
      aria-valuemin={min}
      aria-valuemax={max}
      tabIndex={0}
      onPointerDown={onPointerDown}
      onDoubleClick={onDoubleClick}
      onKeyDown={(event) => {
        const step = event.shiftKey ? 24 : 8;
        if (orientation === "horizontal" && event.key === "ArrowLeft") {
          onChange(Math.max(min, value - (invert ? -step : step)));
        } else if (orientation === "horizontal" && event.key === "ArrowRight") {
          onChange(Math.min(max, value + (invert ? -step : step)));
        } else if (orientation === "vertical" && event.key === "ArrowUp") {
          onChange(Math.max(min, value - (invert ? -step : step)));
        } else if (orientation === "vertical" && event.key === "ArrowDown") {
          onChange(Math.min(max, value + (invert ? -step : step)));
        } else if (event.key === "Enter" || event.key === " ") {
          onChange(defaultValue);
        }
      }}
      className={
        orientation === "horizontal"
          ? "group relative w-1 shrink-0 cursor-col-resize touch-none select-none bg-[var(--desktop-editor-border)] outline-none focus-visible:bg-[var(--desktop-editor-primary)]"
          : "group relative h-1 shrink-0 cursor-row-resize touch-none select-none bg-[var(--desktop-editor-border)] outline-none focus-visible:bg-[var(--desktop-editor-primary)]"
      }
    >
      <div
        className={
          orientation === "horizontal"
            ? "absolute inset-y-0 -left-1 -right-1 group-hover:bg-[var(--desktop-editor-primary-soft)]"
            : "absolute inset-x-0 -top-1 -bottom-1 group-hover:bg-[var(--desktop-editor-primary-soft)]"
        }
      />
    </div>
  );
}
