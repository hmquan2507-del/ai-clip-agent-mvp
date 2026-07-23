import { TIMELINE_KEYFRAME_OVERLAY_CONTRACT_VERSION, type TimelineAnimationRangeOverlay, type TimelineKeyframeLaneGeometry, type TimelineKeyframeOverlayPoint, type TimelineKeyframeOverlayState } from "../contracts/timeline-keyframe-overlay-contracts";
import type { TimelineKeyframe } from "../contracts/timeline-effects-animation-contracts";
import { TimelineKeyframeSelectionRuntime } from "./timeline-keyframe-selection-runtime";

export class TimelineKeyframeOverlayRuntime {
  readonly selection = new TimelineKeyframeSelectionRuntime();
  private version = 0;
  private expanded = true;
  private hoveredKeyframeId: string | null = null;
  private density: TimelineKeyframeOverlayState["density"] = "comfortable";

  setExpanded(expanded: boolean): void { this.expanded = expanded; this.version += 1; }
  setDensity(density: TimelineKeyframeOverlayState["density"]): void { this.density = density; this.version += 1; }
  setHoveredKeyframe(keyframeId: string | null): void { this.hoveredKeyframeId = keyframeId; this.version += 1; }
  notifySelectionChanged(): void { this.version += 1; }

  buildState(geometry: TimelineKeyframeLaneGeometry | null, keyframes: readonly TimelineKeyframe[], dragPreview: TimelineKeyframeOverlayState["dragPreview"] = null): TimelineKeyframeOverlayState {
    const visible = geometry ? keyframes.filter((item) => item.clipId === geometry.clipId && item.timeSeconds >= geometry.viewportStartSeconds && item.timeSeconds <= geometry.viewportEndSeconds) : [];
    const points: TimelineKeyframeOverlayPoint[] = geometry ? visible.map((item) => Object.freeze({
      ...item,
      x: (item.timeSeconds - geometry.viewportStartSeconds) * geometry.pixelsPerSecond,
      selected: this.selection.isSelected(item.keyframeId),
      hovered: this.hoveredKeyframeId === item.keyframeId,
    })) : [];
    const ranges: TimelineAnimationRangeOverlay[] = [];
    if (geometry) {
      const groups = new Map<string, TimelineKeyframe[]>();
      for (const keyframe of keyframes.filter((item) => item.clipId === geometry.clipId)) {
        const bucket = groups.get(keyframe.property) ?? [];
        bucket.push(keyframe); groups.set(keyframe.property, bucket);
      }
      for (const [property, items] of groups) {
        if (items.length < 2) continue;
        const ordered = [...items].sort((a, b) => a.timeSeconds - b.timeSeconds);
        const startSeconds = ordered[0].timeSeconds; const endSeconds = ordered[ordered.length - 1].timeSeconds;
        ranges.push(Object.freeze({ clipId: geometry.clipId, property: property as TimelineAnimationRangeOverlay["property"], startSeconds, endSeconds, startX: (startSeconds - geometry.viewportStartSeconds) * geometry.pixelsPerSecond, endX: (endSeconds - geometry.viewportStartSeconds) * geometry.pixelsPerSecond, keyframeCount: ordered.length }));
      }
    }
    return Object.freeze({ contractVersion: TIMELINE_KEYFRAME_OVERLAY_CONTRACT_VERSION, version: this.version, clipId: geometry?.clipId ?? null, expanded: this.expanded, density: this.density, selectedKeyframeIds: this.selection.getSelectedIds(), hoveredKeyframeId: this.hoveredKeyframeId, points: Object.freeze(points), ranges: Object.freeze(ranges), dragPreview });
  }
}
