"use client";

import { useState } from "react";
import {
  ChevronDown,
  Film,
  ImageIcon,
  LayoutGrid,
  List,
  Music2,
  Search,
  Upload,
} from "lucide-react";

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

const MOCK_ASSETS: MediaAsset[] = [
  { id: "asset-1", name: "raw_interview_a.mp4", durationLabel: "04:12", kind: "video" },
  { id: "asset-2", name: "raw_interview_b.mp4", durationLabel: "03:47", kind: "video" },
  { id: "asset-3", name: "broll_city_night.mp4", durationLabel: "00:32", kind: "video" },
  { id: "asset-4", name: "cover_thumbnail.png", durationLabel: "—", kind: "image" },
  { id: "asset-5", name: "background_lofi.mp3", durationLabel: "02:58", kind: "audio" },
  { id: "asset-6", name: "broll_office.mp4", durationLabel: "00:48", kind: "video" },
];

const KIND_ICON: Record<MediaAsset["kind"], typeof Film> = {
  video: Film,
  image: ImageIcon,
  audio: Music2,
};

export interface EditorAssetPanelProps {
  assets?: MediaAsset[];
  onImport?: () => void;
  onSelectAsset?: (assetId: string) => void;
  collapsed?: boolean;
  onToggleCollapsed?: () => void;
}

export function EditorAssetPanel({
  assets = MOCK_ASSETS,
  onImport,
  onSelectAsset,
  collapsed = false,
  onToggleCollapsed,
}: EditorAssetPanelProps) {
  const [collection, setCollection] = useState<EditorAssetCollectionKey>("local");
  const [query, setQuery] = useState("");
  const [view, setView] = useState<"grid" | "list">("grid");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [moreOpen, setMoreOpen] = useState(false);

  const filtered = assets.filter((asset) => asset.name.toLowerCase().includes(query.toLowerCase()));
  const activeOverflowCollection = OVERFLOW_COLLECTIONS.find((item) => item.key === collection);

  if (collapsed) {
    return (
      <section
        aria-label="Asset library"
        className="flex h-full w-full flex-col items-center gap-2 border-r border-[var(--desktop-editor-border-subtle)] bg-[var(--desktop-editor-surface)] py-2"
      >
        <PanelCollapseButton direction="right" label="Expand asset library" onClick={() => onToggleCollapsed?.()} />
        <span className="mt-1 rotate-180 text-[10px] font-medium tracking-[0.16em] text-[var(--desktop-editor-text-subtle)] [writing-mode:vertical-rl]">
          MEDIA
        </span>
      </section>
    );
  }

  return (
    <section
      aria-label="Asset library"
      className="flex h-full w-full min-h-0 flex-col border-r border-[var(--desktop-editor-border-subtle)] bg-[var(--desktop-editor-surface)]"
    >
      <div className="flex h-8 shrink-0 items-center justify-between px-2.5">
        <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--desktop-editor-text-subtle)]">
          Media
        </span>
        <PanelCollapseButton direction="left" label="Collapse asset library" onClick={() => onToggleCollapsed?.()} />
      </div>

      <div className="flex shrink-0 items-center gap-1.5 px-2 pb-2">
        <label className="flex h-7 min-w-0 flex-1 items-center gap-1.5 rounded-[var(--desktop-editor-radius-control)] border border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-bg)] px-2">
          <Search className="size-3.5 shrink-0 text-[var(--desktop-editor-text-subtle)]" />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search assets"
            aria-label="Search media assets"
            className="min-w-0 flex-1 bg-transparent text-[11px] text-[var(--desktop-editor-text)] outline-none placeholder:text-[var(--desktop-editor-text-subtle)]"
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
                ? "flex size-7 items-center justify-center rounded-md bg-[var(--desktop-editor-surface-hover)] text-[var(--desktop-editor-text)]"
                : "flex size-7 items-center justify-center rounded-md text-[var(--desktop-editor-text-subtle)] hover:text-[var(--desktop-editor-text)]"
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
                ? "flex size-7 items-center justify-center rounded-md bg-[var(--desktop-editor-surface-hover)] text-[var(--desktop-editor-text)]"
                : "flex size-7 items-center justify-center rounded-md text-[var(--desktop-editor-text-subtle)] hover:text-[var(--desktop-editor-text)]"
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
                ? "shrink-0 rounded-md bg-[var(--desktop-editor-primary-soft)] px-2 py-1 text-[10.5px] font-semibold text-[var(--desktop-editor-primary-text)]"
                : "shrink-0 rounded-md px-2 py-1 text-[10.5px] font-medium text-[var(--desktop-editor-text-subtle)] transition hover:text-[var(--desktop-editor-text)]"
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
                ? "flex items-center gap-0.5 rounded-md bg-[var(--desktop-editor-primary-soft)] px-2 py-1 text-[10.5px] font-semibold text-[var(--desktop-editor-primary-text)]"
                : "flex items-center gap-0.5 rounded-md px-2 py-1 text-[10.5px] font-medium text-[var(--desktop-editor-text-subtle)] hover:text-[var(--desktop-editor-text)]"
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
                className="absolute right-0 top-full z-20 mt-1 w-32 rounded-md border border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-surface)] py-1 shadow-[var(--desktop-editor-shadow-panel)]"
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
                      className="block w-full px-2.5 py-1.5 text-left text-[11px] text-[var(--desktop-editor-text)] hover:bg-white/5"
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
                  onSelectAsset?.(asset.id);
                }}
                aria-pressed={selected}
                className={
                  view === "grid"
                    ? `flex flex-col overflow-hidden rounded-[var(--desktop-editor-radius-control)] border text-left transition ${
                        selected
                          ? "border-[var(--desktop-editor-primary)]"
                          : "border-transparent hover:border-[var(--desktop-editor-border-hover)]"
                      }`
                    : `flex items-center gap-2 rounded-[var(--desktop-editor-radius-control)] border px-2 py-1.5 text-left transition ${
                        selected
                          ? "border-[var(--desktop-editor-primary)] bg-[var(--desktop-editor-surface-hover)]"
                          : "border-transparent hover:bg-[var(--desktop-editor-surface-hover)]"
                      }`
                }
              >
                {view === "grid" ? (
                  <span className="relative flex aspect-square items-center justify-center bg-[var(--desktop-editor-bg)] text-[var(--desktop-editor-text-subtle)]">
                    <Icon className="size-5" />
                    {asset.durationLabel !== "—" ? (
                      <span className="absolute bottom-1 right-1 rounded bg-black/70 px-1 py-px text-[8.5px] font-medium leading-tight text-white">
                        {asset.durationLabel}
                      </span>
                    ) : null}
                  </span>
                ) : (
                  <span className="flex size-7 shrink-0 items-center justify-center rounded-md bg-[var(--desktop-editor-bg)] text-[var(--desktop-editor-text-subtle)]">
                    <Icon className="size-4" />
                  </span>
                )}

                {view === "grid" ? (
                  <span className="truncate px-1 py-1 text-[9.5px] font-medium text-[var(--desktop-editor-text)]">
                    {asset.name}
                  </span>
                ) : (
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-[10px] font-medium text-[var(--desktop-editor-text)]">
                      {asset.name}
                    </span>
                    <span className="text-[9px] text-[var(--desktop-editor-text-subtle)]">
                      {asset.durationLabel}
                    </span>
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      <div className="shrink-0 border-t border-[var(--desktop-editor-border-subtle)] p-2">
        <button
          type="button"
          onClick={onImport}
          className="flex h-8 w-full items-center justify-center gap-1.5 rounded-[var(--desktop-editor-radius-control)] bg-[var(--desktop-editor-primary)] text-[11px] font-medium text-white transition hover:bg-[var(--desktop-editor-primary-hover)]"
        >
          <Upload className="size-3.5" />
          Import
        </button>
      </div>
    </section>
  );
}
