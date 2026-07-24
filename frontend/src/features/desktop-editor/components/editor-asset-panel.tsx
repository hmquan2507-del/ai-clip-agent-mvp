"use client";

import { useState } from "react";
import {
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

  const filtered = assets.filter((asset) => asset.name.toLowerCase().includes(query.toLowerCase()));

  if (collapsed) {
    return (
      <section
        aria-label="Asset library"
        className="flex h-full w-full flex-col items-center gap-2 border-r border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-surface)] py-2"
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
      className="flex h-full w-full min-h-0 flex-col border-r border-[var(--desktop-editor-border)] bg-[var(--desktop-editor-surface)]"
    >
      <div className="flex h-9 shrink-0 items-center justify-between border-b border-[var(--desktop-editor-border-subtle)] px-2.5">
        <span className="text-[11px] font-semibold uppercase tracking-[0.1em] text-[var(--desktop-editor-text-subtle)]">
          Media
        </span>
        <PanelCollapseButton direction="left" label="Collapse asset library" onClick={() => onToggleCollapsed?.()} />
      </div>

      <div className="flex shrink-0 items-center gap-2 px-2 py-2">
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

      <div className="flex h-8 shrink-0 items-center gap-1 overflow-x-auto border-b border-[var(--desktop-editor-border-subtle)] px-2">
        {COLLECTIONS.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setCollection(item.key)}
            aria-pressed={collection === item.key}
            className={
              collection === item.key
                ? "shrink-0 rounded-md bg-[var(--desktop-editor-primary-soft)] px-2.5 py-1 text-[11px] font-semibold text-[var(--desktop-editor-primary-text)]"
                : "shrink-0 rounded-md px-2.5 py-1 text-[11px] font-medium text-[var(--desktop-editor-text-subtle)] transition hover:text-[var(--desktop-editor-text)]"
            }
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-2 pt-2">
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
                          : "border-[var(--desktop-editor-border)] hover:border-[var(--desktop-editor-border-hover)]"
                      }`
                    : `flex items-center gap-2 rounded-[var(--desktop-editor-radius-control)] border px-2 py-1.5 text-left transition ${
                        selected
                          ? "border-[var(--desktop-editor-primary)] bg-[var(--desktop-editor-surface-hover)]"
                          : "border-transparent hover:bg-[var(--desktop-editor-surface-hover)]"
                      }`
                }
              >
                <span
                  className={
                    view === "grid"
                      ? "flex aspect-video items-center justify-center bg-[var(--desktop-editor-bg)] text-[var(--desktop-editor-text-subtle)]"
                      : "flex size-7 shrink-0 items-center justify-center rounded-md bg-[var(--desktop-editor-bg)] text-[var(--desktop-editor-text-subtle)]"
                  }
                >
                  <Icon className="size-4" />
                </span>

                <span className={view === "grid" ? "flex flex-col gap-0.5 p-1.5" : "min-w-0 flex-1"}>
                  <span className="truncate text-[10px] font-medium text-[var(--desktop-editor-text)]">
                    {asset.name}
                  </span>
                  <span className="text-[9px] text-[var(--desktop-editor-text-subtle)]">
                    {asset.durationLabel}
                  </span>
                </span>
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
