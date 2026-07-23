import type {
  PlaybackCacheEntry,
  PlaybackCacheKind,
  PlaybackCacheStats,
} from "../contracts/professional-playback-contracts";

export class PlaybackCacheRuntime<T = unknown> {
  private readonly entries = new Map<string, PlaybackCacheEntry<T>>();
  private hits = 0;
  private misses = 0;
  private evictions = 0;

  constructor(private capacity = 240) {
    if (!Number.isInteger(capacity) || capacity < 1) throw new Error("Cache capacity must be at least 1.");
  }

  put(input: Omit<PlaybackCacheEntry<T>, "lastAccessedAt">): void {
    this.entries.set(input.key, { ...input, lastAccessedAt: Date.now() });
    this.evictIfNeeded();
  }

  get(key: string): T | undefined {
    const entry = this.entries.get(key);
    if (!entry) {
      this.misses += 1;
      return undefined;
    }
    this.hits += 1;
    entry.lastAccessedAt = Date.now();
    return entry.value;
  }

  has(key: string): boolean { return this.entries.has(key); }

  delete(key: string): boolean { return this.entries.delete(key); }

  clear(kind?: PlaybackCacheKind): void {
    if (!kind) {
      this.entries.clear();
      return;
    }
    for (const [key, entry] of this.entries) {
      if (entry.kind === kind) this.entries.delete(key);
    }
  }

  prefetchKeys(startFrame: number, endFrame: number, kind: PlaybackCacheKind): string[] {
    const start = Math.max(0, Math.floor(startFrame));
    const end = Math.max(start, Math.floor(endFrame));
    const keys: string[] = [];
    for (let frame = start; frame <= end; frame += 1) {
      const key = `${kind}:${frame}`;
      if (!this.entries.has(key)) keys.push(key);
    }
    return keys;
  }

  stats(): PlaybackCacheStats {
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

  private evictIfNeeded(): void {
    while (this.entries.size > this.capacity) {
      let oldest: PlaybackCacheEntry<T> | undefined;
      for (const entry of this.entries.values()) {
        if (!oldest || entry.lastAccessedAt < oldest.lastAccessedAt) oldest = entry;
      }
      if (!oldest) return;
      this.entries.delete(oldest.key);
      this.evictions += 1;
    }
  }
}
