import type { AiBlock } from "../types";

export interface AiTooltipProps {
  block: AiBlock;
  x: number;
  y: number;
}

const TOOLTIP_WIDTH = 256;
const TOOLTIP_ESTIMATED_HEIGHT = 190;
const CURSOR_OFFSET = 12;

function formatTimeRange(block: AiBlock): string {
  const format = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  };
  return `${format(block.startTime)} – ${format(block.endTime)}`;
}

export function AiTooltip({ block, x, y }: AiTooltipProps) {
  // Flip to the opposite side of the cursor when the tooltip would otherwise
  // overflow the viewport — computed from fixed estimates, not a DOM
  // measurement, so this never introduces a layout-measurement loop.
  const viewportWidth = typeof window !== "undefined" ? window.innerWidth : Number.POSITIVE_INFINITY;
  const viewportHeight = typeof window !== "undefined" ? window.innerHeight : Number.POSITIVE_INFINITY;

  const overflowsRight = x + CURSOR_OFFSET + TOOLTIP_WIDTH > viewportWidth;
  const overflowsBottom = y + CURSOR_OFFSET + TOOLTIP_ESTIMATED_HEIGHT > viewportHeight;

  const left = overflowsRight ? Math.max(8, x - CURSOR_OFFSET - TOOLTIP_WIDTH) : x + CURSOR_OFFSET;
  const top = overflowsBottom ? Math.max(8, y - CURSOR_OFFSET - TOOLTIP_ESTIMATED_HEIGHT) : y + CURSOR_OFFSET;

  return (
    <div
      role="tooltip"
      style={{ left, top, width: TOOLTIP_WIDTH }}
      className="pointer-events-none fixed z-50 rounded-[var(--ai-timeline-radius)] border border-[var(--ai-timeline-border)] bg-[var(--ai-timeline-surface)] p-3 shadow-xl"
    >
      <p className="text-[11px] font-semibold text-[var(--ai-timeline-text)]">{block.title}</p>
      <p className="mt-0.5 text-[10px] text-[var(--ai-timeline-text-subtle)]">{formatTimeRange(block)}</p>

      <dl className="mt-2 space-y-1 text-[10px] leading-4">
        <Row label="AI Model" value={block.aiModel} />
        <Row label="Generated at" value={new Date(block.generatedAt).toLocaleString()} />
        <Row label="Reason" value={block.reason} />
        <Row label="Confidence" value={`${Math.round(block.confidence * 100)}%`} />
        {block.promptUsed ? <Row label="Prompt used" value={block.promptUsed} /> : null}
        {block.estimatedImpact ? <Row label="Estimated impact" value={block.estimatedImpact} /> : null}
      </dl>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-2">
      <dt className="w-24 shrink-0 font-medium text-[var(--ai-timeline-text-subtle)]">{label}</dt>
      <dd className="min-w-0 flex-1 text-[var(--ai-timeline-text)]">{value}</dd>
    </div>
  );
}
