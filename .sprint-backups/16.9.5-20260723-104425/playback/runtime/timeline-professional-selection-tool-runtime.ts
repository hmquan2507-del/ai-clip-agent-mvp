import {
  PROFESSIONAL_SELECTION_TOOL_CONTRACT_VERSION,
  type ProfessionalSelectionConfiguration,
  type ProfessionalSelectionEntity,
  type ProfessionalSelectionEventType,
  type ProfessionalSelectionHistoryPort,
  type ProfessionalSelectionListener,
  type ProfessionalSelectionMode,
  type ProfessionalSelectionSnapshot,
  type ProfessionalTimelineRangeSelection,
  type ProfessionalTimelineTool,
  type TimelineSelectableBounds,
  type TimelineSelectionPoint,
} from "../contracts/professional-selection-tool-contracts";
import { ProfessionalSelectionModel } from "./professional-selection-model";

type Config = Required<Omit<ProfessionalSelectionConfiguration, "maximumSelectionSize">> & { readonly maximumSelectionSize: number | null };
const unique = (items: readonly string[]) => Object.freeze([...new Set(items)]);

export class TimelineProfessionalSelectionToolRuntime {
  private version = 0;
  private disposed = false;
  private activeTool: ProfessionalTimelineTool;
  private selectedEntities: readonly ProfessionalSelectionEntity[] = Object.freeze([]);
  private focusedEntityId: string | null = null;
  private marqueeStart: TimelineSelectionPoint | null = null;
  private marqueeCurrent: TimelineSelectionPoint | null = null;
  private rangeSelection: ProfessionalTimelineRangeSelection | null = null;
  private historyPort: ProfessionalSelectionHistoryPort | null = null;
  private readonly listeners = new Set<ProfessionalSelectionListener>();
  private readonly configuration: Config;

  constructor(configuration: ProfessionalSelectionConfiguration = {}) {
    this.configuration = Object.freeze({
      initialTool: configuration.initialTool ?? "selection",
      allowMixedEntityTypes: configuration.allowMixedEntityTypes ?? true,
      preserveSelectionOnToolChange: configuration.preserveSelectionOnToolChange ?? true,
      marqueeContainment: configuration.marqueeContainment ?? "intersect",
      maximumSelectionSize: configuration.maximumSelectionSize == null ? null : Math.max(1, Math.round(configuration.maximumSelectionSize)),
    });
    this.activeTool = this.configuration.initialTool;
  }

  initialize(initialSelection: readonly ProfessionalSelectionEntity[] = []): ProfessionalSelectionSnapshot {
    this.assertUsable();
    this.selectedEntities = this.validateSelection(initialSelection);
    return this.emit("initialized");
  }

  setHistoryPort(port: ProfessionalSelectionHistoryPort | null): void { this.assertUsable(); this.historyPort = port; }
  subscribe(listener: ProfessionalSelectionListener): () => void { this.assertUsable(); this.listeners.add(listener); return () => this.listeners.delete(listener); }

  async setTool(tool: ProfessionalTimelineTool): Promise<ProfessionalSelectionSnapshot> {
    return this.mutate("Change timeline tool", [], "tool-changed", () => {
      this.activeTool = tool;
      this.cancelMarqueeInternal();
      if (!this.configuration.preserveSelectionOnToolChange) this.selectedEntities = Object.freeze([]);
      if (tool !== "range") this.rangeSelection = null;
    });
  }

  async select(entity: ProfessionalSelectionEntity, mode: ProfessionalSelectionMode = "replace"): Promise<ProfessionalSelectionSnapshot> {
    return this.selectMany([entity], mode, "Select timeline entity");
  }

  async selectMany(entities: readonly ProfessionalSelectionEntity[], mode: ProfessionalSelectionMode = "replace", label = "Select timeline entities"): Promise<ProfessionalSelectionSnapshot> {
    return this.mutate(label, entities.map(item => item.entityId), "selection-changed", () => {
      const next = ProfessionalSelectionModel.apply(this.selectedEntities, entities, mode);
      this.selectedEntities = this.validateSelection(next);
      this.focusedEntityId = entities.length ? entities[entities.length - 1].entityId : this.focusedEntityId;
    });
  }

  async selectTrack(trackId: string, candidates: readonly ProfessionalSelectionEntity[], mode: ProfessionalSelectionMode = "replace"): Promise<ProfessionalSelectionSnapshot> {
    return this.selectMany(candidates.filter(item => item.trackId === trackId), mode, "Select track contents");
  }

  async selectGroup(groupId: string, candidates: readonly ProfessionalSelectionEntity[], mode: ProfessionalSelectionMode = "replace"): Promise<ProfessionalSelectionSnapshot> {
    return this.selectMany(candidates.filter(item => item.groupId === groupId), mode, "Select clip group");
  }

  async selectTimeRange(startTime: number, endTime: number, trackIds: readonly string[] = []): Promise<ProfessionalSelectionSnapshot> {
    return this.mutate("Select timeline range", trackIds, "range-updated", () => {
      const start = Math.max(0, Math.min(startTime, endTime));
      const end = Math.max(start, Math.max(startTime, endTime));
      this.rangeSelection = Object.freeze({ startTime: start, endTime: end, trackIds: unique(trackIds) });
      this.activeTool = "range";
    });
  }

  startMarquee(point: TimelineSelectionPoint): ProfessionalSelectionSnapshot {
    this.assertUsable();
    this.marqueeStart = Object.freeze({ ...point }); this.marqueeCurrent = Object.freeze({ ...point });
    return this.emit("marquee-started");
  }

  updateMarquee(point: TimelineSelectionPoint): ProfessionalSelectionSnapshot {
    this.assertUsable();
    if (!this.marqueeStart) throw new Error("Marquee selection has not started");
    this.marqueeCurrent = Object.freeze({ ...point });
    return this.emit("marquee-updated");
  }

  async commitMarquee(candidates: readonly TimelineSelectableBounds[], mode: ProfessionalSelectionMode = "replace"): Promise<ProfessionalSelectionSnapshot> {
    if (!this.marqueeStart || !this.marqueeCurrent) throw new Error("Marquee selection has not started");
    const rectangle = ProfessionalSelectionModel.rectangle(this.marqueeStart, this.marqueeCurrent);
    const hits = ProfessionalSelectionModel.hitTest(rectangle, candidates, this.configuration.marqueeContainment);
    return this.mutate("Marquee select timeline entities", hits.map(item => item.entityId), "marquee-committed", () => {
      this.selectedEntities = this.validateSelection(ProfessionalSelectionModel.apply(this.selectedEntities, hits, mode));
      this.cancelMarqueeInternal();
    });
  }

  cancelMarquee(): ProfessionalSelectionSnapshot { this.assertUsable(); this.cancelMarqueeInternal(); return this.emit("marquee-cancelled"); }

  async clearSelection(): Promise<ProfessionalSelectionSnapshot> {
    return this.mutate("Clear timeline selection", this.selectedEntities.map(item => item.entityId), "selection-changed", () => {
      this.selectedEntities = Object.freeze([]); this.focusedEntityId = null; this.rangeSelection = null;
    });
  }

  setFocusedEntity(entityId: string | null): ProfessionalSelectionSnapshot {
    this.assertUsable();
    if (entityId !== null && !this.selectedEntities.some(item => item.entityId === entityId)) throw new Error(`Focused entity is not selected: ${entityId}`);
    this.focusedEntityId = entityId;
    return this.emit("focus-changed");
  }

  restore(snapshot: ProfessionalSelectionSnapshot): ProfessionalSelectionSnapshot {
    this.assertUsable();
    if (snapshot.contractVersion !== PROFESSIONAL_SELECTION_TOOL_CONTRACT_VERSION) throw new Error("Unsupported professional selection snapshot version");
    this.activeTool = snapshot.activeTool;
    this.selectedEntities = this.validateSelection(snapshot.selectedEntities);
    this.focusedEntityId = snapshot.focusedEntityId;
    this.rangeSelection = snapshot.rangeSelection ? Object.freeze({ ...snapshot.rangeSelection, trackIds: unique(snapshot.rangeSelection.trackIds) }) : null;
    this.cancelMarqueeInternal();
    return this.emit("state-restored");
  }

  reset(): ProfessionalSelectionSnapshot { this.assertUsable(); this.activeTool = this.configuration.initialTool; this.selectedEntities = Object.freeze([]); this.focusedEntityId = null; this.rangeSelection = null; this.cancelMarqueeInternal(); return this.emit("reset"); }
  dispose(): void { if (this.disposed) return; this.disposed = true; this.version++; const snapshot = this.getSnapshot(); for (const listener of this.listeners) listener({ type: "disposed", snapshot }); this.listeners.clear(); }

  isSelected(entityId: string): boolean { return this.selectedEntities.some(item => item.entityId === entityId); }
  getSelectedByType(entityType: ProfessionalSelectionEntity["entityType"]): readonly ProfessionalSelectionEntity[] { return Object.freeze(this.selectedEntities.filter(item => item.entityType === entityType)); }

  getSnapshot(): ProfessionalSelectionSnapshot {
    const marquee = this.marqueeStart && this.marqueeCurrent ? ProfessionalSelectionModel.rectangle(this.marqueeStart, this.marqueeCurrent) : null;
    return Object.freeze({
      contractVersion: PROFESSIONAL_SELECTION_TOOL_CONTRACT_VERSION,
      version: this.version,
      disposed: this.disposed,
      activeTool: this.activeTool,
      selectedEntities: Object.freeze([...this.selectedEntities]),
      selectedEntityIds: unique(this.selectedEntities.map(item => item.entityId)),
      focusedEntityId: this.focusedEntityId,
      marquee,
      rangeSelection: this.rangeSelection,
    });
  }

  private async mutate(label: string, affectedEntityIds: readonly string[], eventType: ProfessionalSelectionEventType, operation: () => void): Promise<ProfessionalSelectionSnapshot> {
    this.assertUsable();
    const before = this.getSnapshot();
    operation();
    const after = this.emit(eventType);
    if (this.historyPort) await this.historyPort.commitSelectionMutation({ label, before, after, affectedEntityIds: unique(affectedEntityIds) });
    return after;
  }

  private validateSelection(items: readonly ProfessionalSelectionEntity[]): readonly ProfessionalSelectionEntity[] {
    let normalized = items.map(item => ProfessionalSelectionModel.normalizeEntity(item));
    if (!this.configuration.allowMixedEntityTypes && normalized.length) normalized = normalized.filter(item => item.entityType === normalized[0].entityType);
    normalized = [...new Map(normalized.map(item => [item.entityId, item])).values()];
    if (this.configuration.maximumSelectionSize !== null && normalized.length > this.configuration.maximumSelectionSize) throw new Error("Maximum selection size exceeded");
    return Object.freeze(normalized);
  }

  private cancelMarqueeInternal(): void { this.marqueeStart = null; this.marqueeCurrent = null; }
  private emit(type: ProfessionalSelectionEventType): ProfessionalSelectionSnapshot { this.version++; const snapshot = this.getSnapshot(); for (const listener of this.listeners) listener({ type, snapshot }); return snapshot; }
  private assertUsable(): void { if (this.disposed) throw new Error("TimelineProfessionalSelectionToolRuntime is disposed"); }
}

export const createTimelineProfessionalSelectionToolRuntime = (configuration: ProfessionalSelectionConfiguration = {}) => new TimelineProfessionalSelectionToolRuntime(configuration);
