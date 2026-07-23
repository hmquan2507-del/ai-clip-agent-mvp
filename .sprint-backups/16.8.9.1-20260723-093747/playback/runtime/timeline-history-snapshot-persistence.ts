import { TIMELINE_UNDO_REDO_HISTORY_CONTRACT_VERSION, type TimelineHistoryJsonValue, type TimelineUndoRedoHistorySnapshot } from "../contracts/timeline-history-contracts";

export const TIMELINE_HISTORY_SNAPSHOT_SCHEMA_VERSION = 1 as const;

export interface TimelineHistoryPersistedEnvelope<TState = TimelineHistoryJsonValue> {
  readonly schemaVersion: typeof TIMELINE_HISTORY_SNAPSHOT_SCHEMA_VERSION;
  readonly contractVersion: typeof TIMELINE_UNDO_REDO_HISTORY_CONTRACT_VERSION;
  readonly persistedAt: number;
  readonly checksum: string;
  readonly snapshot: TimelineUndoRedoHistorySnapshot<TState>;
}

export interface TimelineHistorySnapshotStorageAdapter {
  load(key: string): string | null | Promise<string | null>;
  save(key: string, value: string): void | Promise<void>;
  remove(key: string): void | Promise<void>;
}

function stableStringify(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(",")}]`;
  const object = value as Record<string, unknown>;
  return `{${Object.keys(object).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(object[key])}`).join(",")}}`;
}

function hash(value: string): string {
  let result = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    result ^= value.charCodeAt(index);
    result = Math.imul(result, 16777619);
  }
  return `fnv1a-${(result >>> 0).toString(16).padStart(8, "0")}`;
}

export class TimelineHistoryMemoryStorageAdapter implements TimelineHistorySnapshotStorageAdapter {
  private readonly values = new Map<string, string>();
  load(key: string): string | null { return this.values.get(key) ?? null; }
  save(key: string, value: string): void { this.values.set(key, value); }
  remove(key: string): void { this.values.delete(key); }
}

export class TimelineHistorySnapshotPersistence<TState = TimelineHistoryJsonValue> {
  constructor(private readonly adapter: TimelineHistorySnapshotStorageAdapter) {}

  serialize(snapshot: TimelineUndoRedoHistorySnapshot<TState>, persistedAt = Date.now()): string {
    const snapshotJson = stableStringify(snapshot);
    const envelope: TimelineHistoryPersistedEnvelope<TState> = Object.freeze({
      schemaVersion: TIMELINE_HISTORY_SNAPSHOT_SCHEMA_VERSION,
      contractVersion: TIMELINE_UNDO_REDO_HISTORY_CONTRACT_VERSION,
      persistedAt,
      checksum: hash(snapshotJson),
      snapshot,
    });
    return stableStringify(envelope);
  }

  deserialize(serialized: string): TimelineHistoryPersistedEnvelope<TState> {
    const parsed = JSON.parse(serialized) as TimelineHistoryPersistedEnvelope<TState>;
    if (parsed.schemaVersion !== TIMELINE_HISTORY_SNAPSHOT_SCHEMA_VERSION) throw new Error("Unsupported timeline history snapshot schema version.");
    if (parsed.contractVersion !== TIMELINE_UNDO_REDO_HISTORY_CONTRACT_VERSION) throw new Error("Timeline history contract version mismatch.");
    if (!parsed.snapshot || parsed.snapshot.contractVersion !== TIMELINE_UNDO_REDO_HISTORY_CONTRACT_VERSION) throw new Error("Invalid timeline history snapshot payload.");
    const expected = hash(stableStringify(parsed.snapshot));
    if (parsed.checksum !== expected) throw new Error("Timeline history snapshot checksum mismatch.");
    return Object.freeze(parsed);
  }

  async save(key: string, snapshot: TimelineUndoRedoHistorySnapshot<TState>): Promise<TimelineHistoryPersistedEnvelope<TState>> {
    const serialized = this.serialize(snapshot);
    await this.adapter.save(key, serialized);
    return this.deserialize(serialized);
  }

  async load(key: string): Promise<TimelineHistoryPersistedEnvelope<TState> | null> {
    const serialized = await this.adapter.load(key);
    return serialized == null ? null : this.deserialize(serialized);
  }

  async remove(key: string): Promise<void> { await this.adapter.remove(key); }

  export(snapshot: TimelineUndoRedoHistorySnapshot<TState>): string { return this.serialize(snapshot); }
  import(serialized: string): TimelineUndoRedoHistorySnapshot<TState> { return this.deserialize(serialized).snapshot; }
}
