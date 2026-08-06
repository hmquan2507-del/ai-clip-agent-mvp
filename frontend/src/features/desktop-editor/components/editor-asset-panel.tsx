"use client";

import { useEffect, useRef, useState } from "react";
import {
  AlertCircle,
  ChevronDown,
  Film,
  FolderSearch,
  ImageIcon,
  LayoutGrid,
  List,
  Music2,
  Search,
  Upload,
} from "lucide-react";

import { EmptyState } from "../../../components/ui/empty-state";
import { LoadingState } from "../../../components/ui/loading-state";
import type { EditorAssetCollectionKey, MediaAsset } from "../types";
import { PanelCollapseButton } from "./panel-collapse-button";

const COLLECTIONS: Array<{ key: EditorAssetCollectionKey; label: string }> = [
  { key: "local", label: "Local" },
  { key: "ai-assets", label: "AI Assets" },
  { key: "stock", label: "Stock" },
  { key: "photos", label: "Photos" },
  { key: "music", label: "Music" },
  { key: "sfx", label: "SFX" },
  { key: "templates", label: "Templates" },
  { key: "brand-kit", label: "Brand Kit" },
];

const PRIMARY_COLLECTION_COUNT = 4;
const PRIMARY_COLLECTIONS = COLLECTIONS.slice(0, PRIMARY_COLLECTION_COUNT);
const OVERFLOW_COLLECTIONS = COLLECTIONS.slice(PRIMARY_COLLECTION_COUNT);

const KIND_ICON: Record<MediaAsset["kind"], typeof Film> = {
  video: Film,
  image: ImageIcon,
  audio: Music2,
};

export interface EditorAssetPanelProps {
  assets?: MediaAsset[];
  loading?: boolean;
  error?: string | null;
  onImport?: () => void;
  onSelectAsset?: (assetId: string, mediaUrl?: string) => void;
  collapsed?: boolean;
  onToggleCollapsed?: () => void;
}

export function EditorAssetPanel({
  assets = [],
  loading = false,
  error = null,
  onImport,
  onSelectAsset,
  collapsed = false,
  onToggleCollapsed,
}: EditorAssetPanelProps) {
  const [localAssets, setLocalAssets] = useState<MediaAsset[]>(assets);

  // `assets` starts as [] while the parent's fetch is in flight and is
  // replaced once with the real list - useState's initial value alone
  // wouldn't pick that up, since it only runs on first render.
  useEffect(() => {
    setLocalAssets(assets);
  }, [assets]);

  const [collection, setCollection] = useState<EditorAssetCollectionKey>("local");
  const [query, setQuery] = useState("");
  const [view, setView] = useState<"grid" | "list">("grid");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [moreOpen, setMoreOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImportClick = () => {
    onImport?.();
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);
    if (files.length === 0) return;
    const newItems: (MediaAsset & { url?: string })[] = files.map((file, i) => {
      const url = URL.createObjectURL(file);
      return {
        id: `imported-${Date.now()}-${i}`,
        name: file.name,
        durationLabel: file.type.startsWith("image") ? "—" : "00:15",
        kind: file.type.startsWith("image") ? "image" : file.type.startsWith("audio") ? "audio" : "video",
        url,
      };
    });
    setLocalAssets((prev) => [...newItems, ...prev]);
    if (newItems[0]) {
      setSelectedId(newItems[0].id);
      onSelectAsset?.(newItems[0].id, newItems[0].url);
    }
  };

  const filtered = localAssets.filter((asset) => asset.name.toLowerCase().includes(query.toLowerCase()));
  const activeOverflowCollection = OVERFLOW_COLLECTIONS.find((item) => item.key === collection);

  if (collapsed) {
    return (
      <section
        aria-label="Asset library"
        className="flex h-full w-full flex-col items-center gap-2 border-r border-[var(--ce-border-subtle)] bg-[var(--ce-bg-panel)] py-2"
      >
        <PanelCollapseButton direction="right" label="Expand asset library" onClick={() => onToggleCollapsed?.()} />
        <span className="mt-1 rotate-180 text-[10px] font-medium tracking-[0.16em] text-[var(--ce-text-muted)] [writing-mode:vertical-rl]">
          MEDIA
        </span>
      </section>
    );
  }

  return (
    <section
      aria-label="Asset library"
      className="flex h-full w-full min-h-0 flex-col border-r border-[var(--ce-border-subtle)] bg-[var(--ce-bg-panel)]"
    >
      <div className="flex h-8 shrink-0 items-center justify-between px-2.5">
        <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--ce-text-muted)]">
          Media
        </span>
        <PanelCollapseButton direction="left" label="Collapse asset library" onClick={() => onToggleCollapsed?.()} />
      </div>

      <div className="flex shrink-0 items-center gap-1.5 px-2 pb-2">
        <label className="flex h-7 min-w-0 flex-1 items-center gap-1.5 rounded-[var(--ce-radius-sm)] border border-[var(--ce-border-default)] bg-[var(--ce-bg-workspace)] px-2 focus-within:border-[var(--ce-border-focus)] focus-within:ring-1 focus-within:ring-[var(--ce-border-focus)]">
          <Search className="size-3.5 shrink-0 text-[var(--ce-text-muted)]" />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search assets"
            aria-label="Search media assets"
            className="min-w-0 flex-1 bg-transparent text-[11px] text-[var(--ce-text-primary)] outline-none placeholder:text-[var(--ce-text-muted)]"
          />
        </label>

        <div className="flex shrink-0 items-center gap-0.5">
          <button
            type="button"
            aria-label="Grid view"
            aria-pressed={view === "grid"}
            onClick={() => setView("grid")}
            className={
              view === "grid"
                ? "flex size-7 items-center justify-center rounded-md bg-[var(--ce-state-hover)] text-[var(--ce-text-primary)] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--ce-border-focus)]"
                : "flex size-7 items-center justify-center rounded-md text-[var(--ce-text-muted)] hover:text-[var(--ce-text-primary)] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--ce-border-focus)]"
            }
          >
            <LayoutGrid className="size-3.5" />
          </button>
          <button
            type="button"
            aria-label="List view"
            aria-pressed={view === "list"}
            onClick={() => setView("list")}
            className={
              view === "list"
                ? "flex size-7 items-center justify-center rounded-md bg-[var(--ce-state-hover)] text-[var(--ce-text-primary)] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--ce-border-focus)]"
                : "flex size-7 items-center justify-center rounded-md text-[var(--ce-text-muted)] hover:text-[var(--ce-text-primary)] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--ce-border-focus)]"
            }
          >
            <List className="size-3.5" />
          </button>
        </div>
      </div>

      <div className="relative flex h-7 shrink-0 items-center gap-1 px-2">
        {PRIMARY_COLLECTIONS.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => {
              setCollection(item.key);
              setMoreOpen(false);
            }}
            aria-pressed={collection === item.key}
            className={
              collection === item.key
                ? "shrink-0 rounded-md bg-[var(--ce-accent-soft)] px-2 py-1 text-[10.5px] font-semibold text-[var(--ce-accent-primary)] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--ce-border-focus)]"
                : "shrink-0 rounded-md px-2 py-1 text-[10.5px] font-medium text-[var(--ce-text-muted)] transition hover:text-[var(--ce-text-primary)] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--ce-border-focus)]"
            }
          >
            {item.label}
          </button>
        ))}

        <div className="relative ml-auto shrink-0">
          <button
            type="button"
            aria-haspopup="menu"
            aria-expanded={moreOpen}
            onClick={() => setMoreOpen((value) => !value)}
            className={
              activeOverflowCollection
                ? "flex items-center gap-0.5 rounded-md bg-[var(--ce-accent-soft)] px-2 py-1 text-[10.5px] font-semibold text-[var(--ce-accent-primary)] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--ce-border-focus)]"
                : "flex items-center gap-0.5 rounded-md px-2 py-1 text-[10.5px] font-medium text-[var(--ce-text-muted)] hover:text-[var(--ce-text-primary)] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--ce-border-focus)]"
            }
          >
            {activeOverflowCollection?.label ?? "More"}
            <ChevronDown className="size-3" />
          </button>

          {moreOpen ? (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setMoreOpen(false)} />
              <ul
                role="menu"
                className="absolute right-0 top-full z-20 mt-1 w-32 rounded-md border border-[var(--ce-border-default)] bg-[var(--ce-bg-panel-raised)] py-1 shadow-[var(--ce-shadow-panel)]"
              >
                {OVERFLOW_COLLECTIONS.map((item) => (
                  <li key={item.key}>
                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => {
                        setCollection(item.key);
                        setMoreOpen(false);
                      }}
                      className="block w-full px-2.5 py-1.5 text-left text-[11px] text-[var(--ce-text-primary)] hover:bg-[var(--ce-state-hover)] focus-visible:outline-none focus-visible:bg-[var(--ce-state-hover)]"
                    >
                      {item.label}
                    </button>
                  </li>
                ))}
              </ul>
            </>
          ) : null}
        </div>
      </div>

      <div className="desktop-editor-scroll min-h-0 flex-1 overflow-y-auto px-2 pb-2 pt-1">
        {loading ? (
          <LoadingState title="Loading Assets" description="Preparing media library..." />
        ) : error ? (
          <EmptyState
            icon={<AlertCircle className="size-5 text-[var(--ce-state-error)]" />}
            title="Failed to load assets"
            description={error}
            action={
              onImport ? (
                <button
                  type="button"
                  onClick={onImport}
                  className="rounded-[var(--ce-radius-sm)] bg-[var(--ce-state-hover)] px-3 py-1 text-[11px] font-medium text-[var(--ce-text-primary)] transition hover:bg-[var(--ce-accent-soft)] hover:text-[var(--ce-accent-primary)]"
                >
                  Retry Import
                </button>
              ) : undefined
            }
          />
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={<FolderSearch className="size-5" />}
            title={query ? "No matching assets" : "No assets in collection"}
            description={
              query
                ? `No media items matching "${query}" were found.`
                : "Import media files or select a different category to view assets."
            }
            action={
              query ? (
                <button
                  type="button"
                  onClick={() => setQuery("")}
                  className="rounded-[var(--ce-radius-sm)] bg-[var(--ce-state-hover)] px-3 py-1 text-[11px] font-medium text-[var(--ce-text-primary)] transition hover:bg-[var(--ce-accent-soft)] hover:text-[var(--ce-accent-primary)]"
                >
                  Clear Search
                </button>
              ) : onImport ? (
                <button
                  type="button"
                  onClick={onImport}
                  className="rounded-[var(--ce-radius-sm)] bg-[var(--ce-accent-primary)] px-3 py-1 text-[11px] font-medium text-white transition hover:bg-[var(--ce-accent-primary-hover)]"
                >
                  Import Media
                </button>
              ) : undefined
            }
          />
        ) : (
          <div className={view === "grid" ? "grid grid-cols-2 gap-2" : "flex flex-col gap-1"}>
            {filtered.map((asset) => {
              const Icon = KIND_ICON[asset.kind];
              const selected = selectedId === asset.id;

              return (
                <button
                  key={asset.id}
                  type="button"
                  onClick={() => {
                    setSelectedId(asset.id);
                    const mediaUrl = (asset as { url?: string }).url;
                    onSelectAsset?.(asset.id, mediaUrl);
                  }}
                  aria-pressed={selected}
                  className={
                    view === "grid"
                      ? `flex flex-col overflow-hidden rounded-[var(--ce-radius-sm)] border text-left transition focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--ce-border-focus)] ${
                          selected
                            ? "border-[var(--ce-accent-primary)] bg-[var(--ce-accent-soft)]/20 shadow-sm"
                            : "border-transparent hover:border-[var(--ce-border-default)] hover:bg-[var(--ce-state-hover)]"
                        }`
                      : `flex items-center gap-2 rounded-[var(--ce-radius-sm)] border px-2 py-1.5 text-left transition focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--ce-border-focus)] ${
                          selected
                            ? "border-[var(--ce-accent-primary)] bg-[var(--ce-accent-soft)]/20"
                            : "border-transparent hover:bg-[var(--ce-state-hover)]"
                        }`
                  }
                >
                  {view === "grid" ? (
                    <span className="relative flex aspect-square items-center justify-center bg-[var(--ce-bg-workspace)] text-[var(--ce-text-muted)]">
                      <Icon className="size-5" />
                      {asset.durationLabel !== "—" ? (
                        <span className="absolute bottom-1 right-1 rounded bg-black/75 px-1 py-px text-[8.5px] font-medium leading-tight text-white">
                          {asset.durationLabel}
                        </span>
                      ) : null}
                    </span>
                  ) : (
                    <span className="flex size-7 shrink-0 items-center justify-center rounded-md bg-[var(--ce-bg-workspace)] text-[var(--ce-text-muted)]">
                      <Icon className="size-4" />
                    </span>
                  )}

                  {view === "grid" ? (
                    <span className="truncate px-1 py-1 text-[9.5px] font-medium text-[var(--ce-text-primary)]">
                      {asset.name}
                    </span>
                  ) : (
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-[10px] font-medium text-[var(--ce-text-primary)]">
                        {asset.name}
                      </span>
                      <span className="text-[9px] text-[var(--ce-text-muted)]">
                        {asset.durationLabel}
                      </span>
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        )}
      </div>

      <div className="shrink-0 border-t border-[var(--ce-border-subtle)] p-2">
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*,audio/*,image/*"
          multiple
          className="hidden"
          onChange={handleFileChange}
        />
        <button
          type="button"
          onClick={handleImportClick}
          className="flex h-8 w-full items-center justify-center gap-1.5 rounded-[var(--ce-radius-sm)] bg-[var(--ce-accent-primary)] text-[11px] font-medium text-white transition hover:bg-[var(--ce-accent-primary-hover)] active:bg-[var(--ce-accent-primary-active)] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--ce-border-focus)]"
        >
          <Upload className="size-3.5" />
          Import
        </button>
      </div>
    </section>
  );
}
