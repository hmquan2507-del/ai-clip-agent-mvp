"use client";

import { useCallback } from "react";

export type LayoutResizerOrientation = "horizontal" | "vertical";

export interface UseLayoutResizerOptions {
  /** "horizontal" = dragging left/right changes the value (a width). "vertical" = dragging up/down changes the value (a height). */
  orientation: LayoutResizerOrientation;
  value: number;
  defaultValue: number;
  min: number;
  max: number;
  onChange: (next: number) => void;
  /** Set true when increasing the pointer coordinate should DECREASE the value (e.g. a divider whose panel sits to its right/below). */
  invert?: boolean;
}

export interface LayoutResizerHandlers {
  onPointerDown: (event: React.PointerEvent<HTMLElement>) => void;
  onDoubleClick: () => void;
}

/**
 * Pure drag-to-resize logic shared by every panel divider. No editing/runtime
 * logic — this only computes a clamped size value from pointer movement.
 */
export function useLayoutResizer({
  orientation,
  value,
  defaultValue,
  min,
  max,
  onChange,
  invert = false,
}: UseLayoutResizerOptions): LayoutResizerHandlers {
  const onPointerDown = useCallback(
    (event: React.PointerEvent<HTMLElement>) => {
      event.preventDefault();

      const startPos = orientation === "horizontal" ? event.clientX : event.clientY;
      const startValue = value;

      function handleMove(moveEvent: PointerEvent) {
        const pos = orientation === "horizontal" ? moveEvent.clientX : moveEvent.clientY;
        const rawDelta = pos - startPos;
        const delta = invert ? -rawDelta : rawDelta;
        const next = Math.min(max, Math.max(min, startValue + delta));
        onChange(next);
      }

      function handleUp() {
        window.removeEventListener("pointermove", handleMove);
        window.removeEventListener("pointerup", handleUp);
      }

      window.addEventListener("pointermove", handleMove);
      window.addEventListener("pointerup", handleUp);
    },
    [invert, max, min, onChange, orientation, value],
  );

  const onDoubleClick = useCallback(() => {
    onChange(defaultValue);
  }, [defaultValue, onChange]);

  return { onPointerDown, onDoubleClick };
}
