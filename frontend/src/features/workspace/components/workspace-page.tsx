"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  FolderKanban,
  Plus,
  RefreshCw,
  Search,
  Sparkles,
} from "lucide-react";

import { apiClient, type ApiProduction } from "@/lib/api-client";
import { ProjectCard, type ProjectCardData } from "./project-card";

export function WorkspacePage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [remoteProjects, setRemoteProjects] = useState<ApiProduction[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    let isMounted = true;
    apiClient.getProductions().then((data) => {
      if (!isMounted) return;
      setLoading(false);
      if (data && Array.isArray(data)) {
        setRemoteProjects(data);
      } else {
        setLoadError(true);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const projectList: ProjectCardData[] = useMemo(() => {
    const list = remoteProjects ?? [];
    return list.map((p, idx) => ({
      id: p.id,
      title: p.title,
      description: p.description,
      status: p.status,
      revision: idx + 1,
      updatedAt: p.updatedAt,
      duration: p.duration ?? "—",
      style: p.style,
      aiDecisionsCount: undefined,
    }));
  }, [remoteProjects]);

  const filteredProjects = useMemo(() => {
    return projectList.filter((project) => {
      const matchesSearch =
        search.trim() === "" ||
        project.title.toLowerCase().includes(search.toLowerCase()) ||
        (project.description && project.description.toLowerCase().includes(search.toLowerCase()));

      const matchesStatus =
        statusFilter === "all" || project.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [projectList, search, statusFilter]);

  const processingProjects = useMemo(
    () => projectList.filter((p) => p.status === "processing"),
    [projectList],
  );

  return (
    <div className="space-y-6" data-workspace-page="true">
      {/* Hero Welcome Banner */}
      <section className="relative overflow-hidden rounded-[var(--ce-radius-md,6px)] border border-[var(--ce-border-subtle,rgb(151_164_190/0.1))] bg-gradient-to-r from-[var(--ce-bg-panel,#131722)] via-[#161a29] to-[var(--ce-bg-panel,#131722)] p-6 shadow-sm">
        <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full bg-[var(--ce-accent-soft,rgb(124_92_255/0.15))] px-2.5 py-1 text-[10px] font-semibold text-[var(--ce-accent-primary,#7c5cff)]">
              <Sparkles className="size-3" />
              AI Studio Workspace
            </div>
            <h1 className="mt-3 text-2xl font-bold tracking-tight text-[var(--ce-text-primary,#f4f6fb)] md:text-3xl">
              Turn Raw Footage into Published Cuts
            </h1>
            <p className="mt-2 max-w-xl text-[12px] leading-5 text-[var(--ce-text-muted,#78839b)]">
              Manage your productions, monitor AI queue execution, and jump directly into the Desktop Editor.
            </p>
          </div>

          <div className="flex shrink-0 items-center gap-3">
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 rounded-[var(--ce-radius-md,6px)] bg-[var(--ce-accent-primary,#7c5cff)] px-4 py-2 text-[12px] font-semibold text-white shadow-sm transition hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ce-border-focus,#7c5cff)]"
            >
              <Plus className="size-4" />
              New Production
            </Link>
          </div>
        </div>
      </section>

      {/* AI Processing Banner (if active tasks exist) */}
      {processingProjects.length > 0 ? (
        <section className="flex items-center justify-between gap-4 rounded-[var(--ce-radius-md,6px)] border border-[var(--ce-state-warning,#f8c76e)]/30 bg-[var(--ce-state-warning-soft,#f8c76e1a)] p-3 px-4 text-[12px] text-[var(--ce-state-warning,#f8c76e)]">
          <div className="flex items-center gap-2">
            <RefreshCw className="size-4 animate-spin shrink-0" />
            <span>
              <strong>{processingProjects.length} production(s)</strong> currently processing in AI Queue.
            </span>
          </div>
          <Link
            href="/ai-queue"
            className="inline-flex items-center gap-1 font-semibold underline hover:brightness-110"
          >
            View Queue <ArrowRight className="size-3" />
          </Link>
        </section>
      ) : null}

      {/* Controls & Search Bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-[var(--ce-text-muted,#78839b)]" />
            <input
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search projects..."
              className="w-full rounded-[var(--ce-radius-md,6px)] border border-[var(--ce-border-subtle,rgb(151_164_190/0.1))] bg-[var(--ce-bg-panel,#131722)] pl-8 pr-3 py-1.5 text-[11px] text-[var(--ce-text-primary,#f4f6fb)] outline-none placeholder:text-[var(--ce-text-muted,#78839b)] focus:border-[var(--ce-border-focus,#7c5cff)]"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            aria-label="Filter by status"
            className="rounded-[var(--ce-radius-md,6px)] border border-[var(--ce-border-subtle,rgb(151_164_190/0.1))] bg-[var(--ce-bg-panel,#131722)] px-2.5 py-1.5 text-[11px] text-[var(--ce-text-primary,#f4f6fb)] outline-none focus:border-[var(--ce-border-focus,#7c5cff)]"
          >
            <option value="all">All Statuses</option>
            <option value="review_ready">Ready for Review</option>
            <option value="processing">AI Processing</option>
            <option value="uploaded">Uploaded</option>
          </select>
        </div>

        <div className="flex items-center gap-2 text-[11px] text-[var(--ce-text-muted,#78839b)]">
          <span>Total: <strong>{filteredProjects.length}</strong> projects</span>
        </div>
      </div>

      {/* Projects Grid */}
      <section aria-label="Projects Grid">
        {loading ? (
          <div className="flex h-48 flex-col items-center justify-center rounded-[var(--ce-radius-md,6px)] border border-dashed border-[var(--ce-border-subtle,rgb(151_164_190/0.1))] bg-[var(--ce-bg-panel,#131722)] p-6 text-center">
            <RefreshCw className="size-8 animate-spin text-[var(--ce-text-muted,#78839b)]" />
            <p className="mt-2 text-[13px] font-semibold text-[var(--ce-text-primary,#f4f6fb)]">Loading productions…</p>
          </div>
        ) : loadError ? (
          <div className="flex h-48 flex-col items-center justify-center rounded-[var(--ce-radius-md,6px)] border border-dashed border-[var(--ce-state-error,#f87171)]/40 bg-[var(--ce-bg-panel,#131722)] p-6 text-center">
            <FolderKanban className="size-8 text-[var(--ce-state-error,#f87171)]" />
            <p className="mt-2 text-[13px] font-semibold text-[var(--ce-text-primary,#f4f6fb)]">Could not load productions</p>
            <p className="mt-1 text-[11px] text-[var(--ce-text-muted,#78839b)]">Is the backend running? Try refreshing the page.</p>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="flex h-48 flex-col items-center justify-center rounded-[var(--ce-radius-md,6px)] border border-dashed border-[var(--ce-border-subtle,rgb(151_164_190/0.1))] bg-[var(--ce-bg-panel,#131722)] p-6 text-center">
            <FolderKanban className="size-8 text-[var(--ce-text-muted,#78839b)]" />
            <p className="mt-2 text-[13px] font-semibold text-[var(--ce-text-primary,#f4f6fb)]">
              {projectList.length === 0 ? "No productions yet" : "No projects found"}
            </p>
            <p className="mt-1 text-[11px] text-[var(--ce-text-muted,#78839b)]">
              {projectList.length === 0
                ? "Upload a video to create your first production."
                : "Try adjusting your search query or status filter."}
            </p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredProjects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
