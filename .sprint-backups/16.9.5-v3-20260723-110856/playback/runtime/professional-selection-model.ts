import type {
  ProfessionalSelectionEntity,
  ProfessionalSelectionMode,
  TimelineSelectionPoint,
  TimelineSelectionRect,
  TimelineSelectableBounds,
} from "../contracts/professional-selection-tool-contracts";

const normalizeRect = (a: TimelineSelectionPoint, b: TimelineSelectionPoint): TimelineSelectionRect => Object.freeze({
  left: Math.min(a.x, b.x), top: Math.min(a.y, b.y), right: Math.max(a.x, b.x), bottom: Math.max(a.y, b.y),
});

export class ProfessionalSelectionModel {
  static normalizeEntity(entity: ProfessionalSelectionEntity): ProfessionalSelectionEntity {
    const entityId = entity.entityId.trim();
    if (!entityId) throw new Error("Selection entityId is required");
    return Object.freeze({
      ...entity,
      entityId,
      trackId: entity.trackId ?? null,
      groupId: entity.groupId ?? null,
      startTime: entity.startTime == null ? null : Math.max(0, entity.startTime),
      endTime: entity.endTime == null ? null : Math.max(0, entity.endTime),
      metadata: Object.freeze({ ...(entity.metadata ?? {}) }),
    });
  }

  static apply(current: readonly ProfessionalSelectionEntity[], incoming: readonly ProfessionalSelectionEntity[], mode: ProfessionalSelectionMode): readonly ProfessionalSelectionEntity[] {
    const normalized = incoming.map(item => this.normalizeEntity(item));
    const map = new Map(current.map(item => [item.entityId, item]));
    if (mode === "replace") return Object.freeze([...new Map(normalized.map(item => [item.entityId, item])).values()]);
    for (const item of normalized) {
      if (mode === "subtract") map.delete(item.entityId);
      else if (mode === "toggle" && map.has(item.entityId)) map.delete(item.entityId);
      else map.set(item.entityId, item);
    }
    return Object.freeze([...map.values()]);
  }

  static rectangle(start: TimelineSelectionPoint, current: TimelineSelectionPoint): TimelineSelectionRect { return normalizeRect(start, current); }

  static hitTest(rect: TimelineSelectionRect, candidates: readonly TimelineSelectableBounds[], containment: "intersect" | "contain"): readonly ProfessionalSelectionEntity[] {
    return Object.freeze(candidates.filter(candidate => containment === "contain"
      ? candidate.bounds.left >= rect.left && candidate.bounds.right <= rect.right && candidate.bounds.top >= rect.top && candidate.bounds.bottom <= rect.bottom
      : candidate.bounds.right >= rect.left && candidate.bounds.left <= rect.right && candidate.bounds.bottom >= rect.top && candidate.bounds.top <= rect.bottom)
      .map(({ bounds: _bounds, ...entity }) => this.normalizeEntity(entity)));
  }
}
