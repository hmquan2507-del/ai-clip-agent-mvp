"use client";
import React, { useEffect, useMemo, useRef, useState } from "react";
import type { TimelineAnimatableProperty } from "../contracts/timeline-effects-animation-contracts";
import type { TimelineKeyframeLaneGeometry, TimelineKeyframeSnapCandidate } from "../contracts/timeline-keyframe-overlay-contracts";
import type { TimelineKeyframeLaneController } from "../runtime/timeline-keyframe-lane-controller";

export interface TimelineKeyframeLaneProps {
  readonly controller: TimelineKeyframeLaneController;
  readonly geometry: TimelineKeyframeLaneGeometry;
  readonly playheadSeconds: number;
  readonly markers?: readonly number[];
  readonly className?: string;
}

const PROPERTY_LABELS: Record<TimelineAnimatableProperty, string> = { "position-x": "X", "position-y": "Y", "scale-x": "Scale X", "scale-y": "Scale Y", rotation: "Rotation", opacity: "Opacity", volume: "Volume", blur: "Blur", brightness: "Brightness", contrast: "Contrast", saturation: "Saturation" };

export function TimelineKeyframeLane({ controller, geometry, playheadSeconds, markers = [], className = "" }: TimelineKeyframeLaneProps) {
  const [state, setState] = useState(() => controller.getState());
  const dragStart = useRef<{ x: number; keyframeId: string } | null>(null);
  useEffect(() => controller.subscribe(setState), [controller]);
  useEffect(() => controller.setGeometry(geometry), [controller, geometry]);
  const snapCandidates = useMemo<readonly TimelineKeyframeSnapCandidate[]>(() => [
    { kind: "playhead", timeSeconds: playheadSeconds, priority: 100, sourceId: "playhead" },
    { kind: "clip-start", timeSeconds: geometry.clipStartSeconds, priority: 90, sourceId: geometry.clipId },
    { kind: "clip-end", timeSeconds: geometry.clipEndSeconds, priority: 90, sourceId: geometry.clipId },
    ...markers.map((timeSeconds, index) => ({ kind: "marker" as const, timeSeconds, priority: 80, sourceId: `marker-${index}` })),
  ], [geometry, markers, playheadSeconds]);

  return <section className={`relative overflow-hidden border-y bg-background ${className}`} aria-label="Timeline keyframe lane" onPointerMove={(event) => { if (!dragStart.current) return; controller.updateDrag(event.clientX - dragStart.current.x, snapCandidates); }} onPointerUp={() => { if (!dragStart.current) return; dragStart.current = null; controller.commitDrag(); }} onPointerCancel={() => { dragStart.current = null; controller.cancelDrag(); }}>
    <header className="flex h-8 items-center justify-between border-b px-2 text-xs"><strong>Animation</strong><div className="flex items-center gap-1"><span>{state.points.length} keys</span><button type="button" onClick={() => controller.duplicateSelected()} disabled={!state.selectedKeyframeIds.length}>Duplicate</button><button type="button" onClick={() => controller.deleteSelected()} disabled={!state.selectedKeyframeIds.length}>Delete</button></div></header>
    <div className="relative h-16" onPointerDown={(event) => { if (event.target === event.currentTarget) controller.clearSelection(); }}>
      {state.ranges.map((range) => <div key={`${range.property}-${range.startSeconds}`} className="absolute top-1/2 h-1 -translate-y-1/2 rounded bg-current opacity-20" style={{ left: range.startX, width: Math.max(1, range.endX - range.startX) }} title={`${PROPERTY_LABELS[range.property]} animation`}/>) }
      {state.points.map((point) => {
        const previewTime = state.dragPreview?.targetTimes[point.keyframeId];
        const x = typeof previewTime === "number" ? (previewTime - geometry.viewportStartSeconds) * geometry.pixelsPerSecond : point.x;
        return <button key={point.keyframeId} type="button" aria-label={`${PROPERTY_LABELS[point.property]} keyframe at ${point.timeSeconds.toFixed(2)} seconds`} aria-pressed={point.selected} title={`${PROPERTY_LABELS[point.property]} · ${point.value} · ${point.interpolation}`} className={`absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rotate-45 border ${point.selected ? "bg-foreground" : "bg-background"}`} style={{ left: x }} onPointerEnter={() => controller.overlay.setHoveredKeyframe(point.keyframeId)} onPointerLeave={() => controller.overlay.setHoveredKeyframe(null)} onPointerDown={(event) => { event.stopPropagation(); controller.select(point.keyframeId, { toggle: event.ctrlKey || event.metaKey, range: event.shiftKey }); controller.beginDrag(point.keyframeId); dragStart.current = { x: event.clientX, keyframeId: point.keyframeId }; event.currentTarget.setPointerCapture(event.pointerId); }}/>
      })}
      {state.dragPreview?.snap.snapped ? <div className="absolute inset-y-0 w-px bg-current" style={{ left: (state.dragPreview.snap.resolvedTimeSeconds - geometry.viewportStartSeconds) * geometry.pixelsPerSecond }} aria-hidden="true"/> : null}
    </div>
    <footer className="flex h-7 items-center justify-between border-t px-2 text-[10px] opacity-70"><span>{state.selectedKeyframeIds.length} selected</span><span>{state.dragPreview?.snap.snapped ? `Snap: ${state.dragPreview.snap.kind}` : "Drag keyframes to retime"}</span></footer>
  </section>;
}
