import {
  PROFESSIONAL_MULTI_TRACK_CONTRACT_VERSION,
  type AddProfessionalTrackRequest,
  type ProfessionalMultiTrackConfiguration,
  type ProfessionalMultiTrackEventType,
  type ProfessionalMultiTrackHistoryPort,
  type ProfessionalMultiTrackListener,
  type ProfessionalMultiTrackSnapshot,
  type ProfessionalTrack,
  type ProfessionalTrackClipAssignment,
  type ProfessionalTrackGroup,
  type UpdateProfessionalTrackRequest,
} from "../contracts/professional-multi-track-contracts";
import { ProfessionalTrackGroupModel } from "./professional-track-group-model";
import { ProfessionalTrackModel } from "./professional-track-model";

type Config = Required<Omit<ProfessionalMultiTrackConfiguration, "maxTracks" | "defaultTrackColor">> & {
  readonly maxTracks: number | null;
  readonly defaultTrackColor: string | null;
};

const freezeStrings = (items: readonly string[]) => Object.freeze([...new Set(items)]);

export class TimelineProfessionalMultiTrackRuntime {
  private version = 0;
  private disposed = false;
  private tracks: readonly ProfessionalTrack[] = Object.freeze([]);
  private groups: readonly ProfessionalTrackGroup[] = Object.freeze([]);
  private assignments: readonly ProfessionalTrackClipAssignment[] = Object.freeze([]);
  private historyPort: ProfessionalMultiTrackHistoryPort | null = null;
  private readonly listeners = new Set<ProfessionalMultiTrackListener>();
  private readonly configuration: Config;

  constructor(configuration: ProfessionalMultiTrackConfiguration = {}) {
    this.configuration = Object.freeze({
      maxTracks: configuration.maxTracks == null ? null : Math.max(1, Math.round(configuration.maxTracks)),
      allowEmptyTimeline: configuration.allowEmptyTimeline ?? true,
      enforceUniqueNames: configuration.enforceUniqueNames ?? false,
      defaultTrackColor: configuration.defaultTrackColor ?? null,
      autoRenameDuplicates: configuration.autoRenameDuplicates ?? true,
      soloIsExclusive: configuration.soloIsExclusive ?? false,
    });
  }

  initialize(tracks: readonly AddProfessionalTrackRequest[] = []): ProfessionalMultiTrackSnapshot {
    this.assertUsable();
    if (this.tracks.length || this.groups.length || this.assignments.length) throw new Error("Runtime is already initialized");
    for (const track of tracks) this.addTrackInternal(track);
    return this.emit("initialized");
  }

  setHistoryPort(port: ProfessionalMultiTrackHistoryPort | null): void { this.assertUsable(); this.historyPort = port; }
  subscribe(listener: ProfessionalMultiTrackListener): () => void { this.assertUsable(); this.listeners.add(listener); return () => this.listeners.delete(listener); }

  async addTrack(request: AddProfessionalTrackRequest): Promise<ProfessionalMultiTrackSnapshot> {
    return this.mutate("Add track", [request.trackId], "track-added", () => this.addTrackInternal(request));
  }

  async updateTrack(trackId: string, request: UpdateProfessionalTrackRequest): Promise<ProfessionalMultiTrackSnapshot> {
    return this.mutate("Update track", [trackId], "track-updated", () => {
      const index = this.indexOfTrack(trackId);
      let updated = ProfessionalTrackModel.update(this.tracks[index], request);
      if (request.solo && this.configuration.soloIsExclusive) {
        this.tracks = Object.freeze(this.tracks.map((track, i) => i === index ? updated : Object.freeze({ ...track, solo: false })));
      } else {
        this.tracks = Object.freeze(this.tracks.map((track, i) => i === index ? updated : track));
      }
      if (request.groupId !== undefined) this.rebuildGroupsFromTracks();
      this.ensureNamePolicy(updated.trackId);
    });
  }

  async removeTrack(trackId: string, reassignClipTrackId: string | null = null): Promise<ProfessionalMultiTrackSnapshot> {
    return this.mutate("Remove track", [trackId], "track-removed", () => {
      this.indexOfTrack(trackId);
      if (!this.configuration.allowEmptyTimeline && this.tracks.length === 1) throw new Error("Timeline must keep at least one track");
      const assigned = this.assignments.filter(a => a.trackId === trackId);
      if (assigned.length && !reassignClipTrackId) throw new Error("Track contains clips; provide a reassignment track");
      if (reassignClipTrackId) this.indexOfTrack(reassignClipTrackId);
      this.assignments = Object.freeze(this.assignments.map(a => a.trackId === trackId ? Object.freeze({ ...a, trackId: reassignClipTrackId! }) : a));
      this.tracks = Object.freeze(this.tracks.filter(t => t.trackId !== trackId));
      this.normalizeOrders();
      this.rebuildGroupsFromTracks();
    });
  }

  async duplicateTrack(trackId: string, newTrackId: string, newName?: string): Promise<ProfessionalMultiTrackSnapshot> {
    return this.mutate("Duplicate track", [trackId, newTrackId], "track-duplicated", () => {
      const source = this.getTrack(trackId);
      const created = this.addTrackInternal({ trackId: newTrackId, name: newName ?? `${source.name} Copy`, kind: source.kind, order: source.order + 1, color: source.color, groupId: source.groupId, metadata: source.metadata });
      this.tracks = Object.freeze(this.tracks.map(t => t.trackId === created.trackId ? Object.freeze({ ...created, locked: source.locked, muted: source.muted, hidden: source.hidden, collapsed: source.collapsed, rippleEnabled: source.rippleEnabled, magneticEnabled: source.magneticEnabled }) : t));
    });
  }

  async reorderTrack(trackId: string, targetOrder: number): Promise<ProfessionalMultiTrackSnapshot> {
    return this.mutate("Reorder track", [trackId], "track-reordered", () => {
      const index = this.indexOfTrack(trackId);
      const next = [...this.tracks];
      const [track] = next.splice(index, 1);
      const destination = Math.max(0, Math.min(next.length, Math.round(targetOrder)));
      next.splice(destination, 0, track);
      this.tracks = Object.freeze(next.map((item, order) => ProfessionalTrackModel.withOrder(item, order)));
      this.rebuildGroupsFromTracks();
    });
  }

  async createGroup(groupId: string, name: string, trackIds: readonly string[] = [], color: string | null = null): Promise<ProfessionalMultiTrackSnapshot> {
    return this.mutate("Create track group", trackIds, "track-group-created", () => {
      if (this.groups.some(g => g.groupId === groupId)) throw new Error(`Duplicate groupId: ${groupId}`);
      for (const id of trackIds) this.indexOfTrack(id);
      const group = ProfessionalTrackGroupModel.create(groupId, name, trackIds, color);
      this.groups = Object.freeze([...this.groups, group]);
      const members = new Set(trackIds);
      this.tracks = Object.freeze(this.tracks.map(t => members.has(t.trackId) ? Object.freeze({ ...t, groupId }) : t));
      this.rebuildGroupsFromTracks();
    });
  }

  async updateGroup(groupId: string, patch: Partial<Pick<ProfessionalTrackGroup, "name" | "color" | "collapsed" | "locked">>): Promise<ProfessionalMultiTrackSnapshot> {
    const group = this.getGroup(groupId);
    return this.mutate("Update track group", group.trackIds, "track-group-updated", () => {
      this.groups = Object.freeze(this.groups.map(g => g.groupId === groupId ? ProfessionalTrackGroupModel.update(g, patch) : g));
      if (patch.locked !== undefined) this.tracks = Object.freeze(this.tracks.map(t => t.groupId === groupId ? Object.freeze({ ...t, locked: patch.locked! }) : t));
      if (patch.collapsed !== undefined) this.tracks = Object.freeze(this.tracks.map(t => t.groupId === groupId ? Object.freeze({ ...t, collapsed: patch.collapsed! }) : t));
    });
  }

  async removeGroup(groupId: string): Promise<ProfessionalMultiTrackSnapshot> {
    const group = this.getGroup(groupId);
    return this.mutate("Remove track group", group.trackIds, "track-group-removed", () => {
      this.groups = Object.freeze(this.groups.filter(g => g.groupId !== groupId));
      this.tracks = Object.freeze(this.tracks.map(t => t.groupId === groupId ? Object.freeze({ ...t, groupId: null }) : t));
    });
  }

  async assignClip(clipId: string, trackId: string): Promise<ProfessionalMultiTrackSnapshot> {
    return this.mutate("Assign clip to track", [trackId], "clip-assigned", () => {
      this.indexOfTrack(trackId);
      if (!clipId.trim()) throw new Error("clipId is required");
      const existing = this.assignments.find(a => a.clipId === clipId);
      this.assignments = Object.freeze(existing
        ? this.assignments.map(a => a.clipId === clipId ? Object.freeze({ clipId, trackId }) : a)
        : [...this.assignments, Object.freeze({ clipId, trackId })]);
    });
  }

  async unassignClip(clipId: string): Promise<ProfessionalMultiTrackSnapshot> {
    const assignment = this.assignments.find(a => a.clipId === clipId);
    if (!assignment) return this.getSnapshot();
    return this.mutate("Unassign clip", [assignment.trackId], "clip-unassigned", () => {
      this.assignments = Object.freeze(this.assignments.filter(a => a.clipId !== clipId));
    });
  }

  async restore(snapshot: ProfessionalMultiTrackSnapshot): Promise<ProfessionalMultiTrackSnapshot> {
    this.assertUsable();
    this.tracks = Object.freeze(snapshot.tracks.map(t => Object.freeze({ ...t, metadata: Object.freeze({ ...t.metadata }) })));
    this.groups = Object.freeze(snapshot.groups.map(g => Object.freeze({ ...g, trackIds: Object.freeze([...g.trackIds]) })));
    this.assignments = Object.freeze(snapshot.assignments.map(a => Object.freeze({ ...a })));
    this.normalizeOrders();
    return this.emit("state-restored");
  }

  reset(): ProfessionalMultiTrackSnapshot { this.assertUsable(); this.tracks = Object.freeze([]); this.groups = Object.freeze([]); this.assignments = Object.freeze([]); return this.emit("reset"); }
  dispose(): void { if (this.disposed) return; this.disposed = true; this.version++; const snapshot = this.getSnapshot(); for (const listener of this.listeners) listener({ type: "disposed", snapshot }); this.listeners.clear(); }

  getTrack(trackId: string): ProfessionalTrack { return this.tracks[this.indexOfTrack(trackId)]; }
  getGroup(groupId: string): ProfessionalTrackGroup { const group = this.groups.find(g => g.groupId === groupId); if (!group) throw new Error(`Unknown groupId: ${groupId}`); return group; }
  getTracksByKind(kind: ProfessionalTrack["kind"]): readonly ProfessionalTrack[] { return Object.freeze(this.tracks.filter(t => t.kind === kind)); }
  getClipsForTrack(trackId: string): readonly string[] { this.indexOfTrack(trackId); return Object.freeze(this.assignments.filter(a => a.trackId === trackId).map(a => a.clipId)); }

  getSnapshot(): ProfessionalMultiTrackSnapshot {
    const soloIds = this.tracks.filter(t => t.solo && t.status === "active").map(t => t.trackId);
    const audible = this.tracks.filter(t => t.kind === "audio" && t.status === "active" && !t.muted && (soloIds.length === 0 || t.solo)).map(t => t.trackId);
    const visible = this.tracks.filter(t => t.status === "active" && !t.hidden).map(t => t.trackId);
    const locked = this.tracks.filter(t => t.locked).map(t => t.trackId);
    return Object.freeze({
      contractVersion: PROFESSIONAL_MULTI_TRACK_CONTRACT_VERSION,
      version: this.version,
      disposed: this.disposed,
      tracks: Object.freeze([...this.tracks]),
      groups: Object.freeze([...this.groups]),
      assignments: Object.freeze([...this.assignments]),
      audibleTrackIds: freezeStrings(audible),
      visibleTrackIds: freezeStrings(visible),
      lockedTrackIds: freezeStrings(locked),
    });
  }

  private async mutate(label: string, affectedTrackIds: readonly string[], eventType: ProfessionalMultiTrackEventType, operation: () => void): Promise<ProfessionalMultiTrackSnapshot> {
    this.assertUsable();
    const before = this.getSnapshot();
    operation();
    const after = this.emit(eventType);
    if (this.historyPort) await this.historyPort.commitTrackMutation({ label, before, after, affectedTrackIds: freezeStrings(affectedTrackIds) });
    return after;
  }

  private addTrackInternal(request: AddProfessionalTrackRequest): ProfessionalTrack {
    if (this.configuration.maxTracks !== null && this.tracks.length >= this.configuration.maxTracks) throw new Error("Maximum track count reached");
    if (this.tracks.some(t => t.trackId === request.trackId.trim())) throw new Error(`Duplicate trackId: ${request.trackId}`);
    if (request.groupId && !this.groups.some(g => g.groupId === request.groupId)) throw new Error(`Unknown groupId: ${request.groupId}`);
    const track = ProfessionalTrackModel.create(request, this.tracks.length, this.configuration.defaultTrackColor);
    this.tracks = Object.freeze([...this.tracks, track]);
    this.normalizeOrders();
    this.ensureNamePolicy(track.trackId);
    this.rebuildGroupsFromTracks();
    return this.getTrack(track.trackId);
  }

  private ensureNamePolicy(trackId: string): void {
    const index = this.indexOfTrack(trackId);
    const target = this.tracks[index];
    const duplicates = this.tracks.filter(t => t.trackId !== trackId && t.name.toLowerCase() === target.name.toLowerCase());
    if (!duplicates.length) return;
    if (this.configuration.enforceUniqueNames && !this.configuration.autoRenameDuplicates) throw new Error(`Duplicate track name: ${target.name}`);
    if (this.configuration.autoRenameDuplicates) {
      let suffix = 2;
      let candidate = `${target.name} ${suffix}`;
      while (this.tracks.some(t => t.trackId !== trackId && t.name.toLowerCase() === candidate.toLowerCase())) candidate = `${target.name} ${++suffix}`;
      this.tracks = Object.freeze(this.tracks.map((t, i) => i === index ? Object.freeze({ ...t, name: candidate }) : t));
    }
  }

  private rebuildGroupsFromTracks(): void {
    this.groups = Object.freeze(this.groups.map(group => ProfessionalTrackGroupModel.withTracks(group, this.tracks.filter(t => t.groupId === group.groupId).map(t => t.trackId))));
  }

  private normalizeOrders(): void {
    this.tracks = Object.freeze([...this.tracks].sort((a, b) => a.order - b.order || a.trackId.localeCompare(b.trackId)).map((track, order) => ProfessionalTrackModel.withOrder(track, order)));
  }

  private indexOfTrack(trackId: string): number { const index = this.tracks.findIndex(t => t.trackId === trackId); if (index < 0) throw new Error(`Unknown trackId: ${trackId}`); return index; }
  private emit(type: ProfessionalMultiTrackEventType): ProfessionalMultiTrackSnapshot { this.version++; const snapshot = this.getSnapshot(); for (const listener of this.listeners) listener({ type, snapshot }); return snapshot; }
  private assertUsable(): void { if (this.disposed) throw new Error("TimelineProfessionalMultiTrackRuntime is disposed"); }
}

export const createTimelineProfessionalMultiTrackRuntime = (configuration: ProfessionalMultiTrackConfiguration = {}) => new TimelineProfessionalMultiTrackRuntime(configuration);
