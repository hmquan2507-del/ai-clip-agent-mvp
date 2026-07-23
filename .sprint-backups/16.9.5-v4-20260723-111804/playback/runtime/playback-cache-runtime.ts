import type {
  ProfessionalPlaybackCacheEntry,
  ProfessionalPlaybackCacheSnapshot,
} from "../contracts";

export class PlaybackCacheRuntime<T = unknown> {
  private readonly entries = new Map<string, ProfessionalPlaybackCacheEntry<T>>();
  private hits = 0;
  private misses = 0;
  private evictions = 0;

  constructor(private readonly capacity = 240) {
    if (!Number.isInteger(capacity) || capacity < 1) {
      throw new Error("Professional playback cache capacity must be at least one.");
    }
  }

  put(entry: Omit<ProfessionalPlaybackCacheEntry<T>, "lastAccessedAt">): void {
    this.entries.set(entry.key, { ...entry, lastAccessedAt: Date.now() });
    this.evict();
  }

  get(key: string): T | undefined {
    const entry = this.entries.get(key);
    if (!entry) {
      this.misses += 1;
      return undefined;
    }
    this.hits += 1;
    this.entries.set(key, { ...entry, lastAccessedAt: Date.now() });
    return entry.value;
  }

  clear(): void {
    this.entries.clear();
  }

  getSnapshot(): ProfessionalPlaybackCacheSnapshot {
    let bytes = 0;
    for (const entry of this.entries.values()) bytes += entry.sizeBytes;
    return {
      entries: this.entries.size,
      bytes,
      hits: this.hits,
      misses: this.misses,
      evictions: this.evictions,
    };
  }

  private evict(): void {
    while (this.entries.size > this.capacity) {
      let oldestKey: string | null = null;
      let oldestTime = Number.POSITIVE_INFINITY;
      for (const [key, entry] of this.entries) {
        if (entry.lastAccessedAt < oldestTime) {
          oldestTime = entry.lastAccessedAt;
          oldestKey = key;
        }
      }
      if (oldestKey === null) return;
      this.entries.delete(oldestKey);
      this.evictions += 1;
    }
  }
}
