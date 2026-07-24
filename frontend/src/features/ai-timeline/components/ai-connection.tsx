import { memo } from "react";

export interface AiConnectionProps {
  left: number;
  height: number;
  color?: string;
}

/**
 * Vertical guide line spanning every AI track (and, conceptually, down into
 * the real timeline below it) at the hovered/selected block's time position —
 * the visual expression of "hovering an AI block highlights everything in
 * sync." Purely decorative positioning; it does not read or write any
 * runtime state.
 */
function AiConnectionImpl({ left, height, color = "#ffffff" }: AiConnectionProps) {
  return (
    <div
      aria-hidden
      style={{ left, height, backgroundColor: color }}
      className="pointer-events-none absolute top-0 z-10 w-px opacity-60"
    />
  );
}

export const AiConnectionView = memo(AiConnectionImpl);
