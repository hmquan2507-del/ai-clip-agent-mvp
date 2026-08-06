"use client";

import { useEffect, useState } from "react";
import { RefreshCw, FolderKanban } from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { apiClient } from "@/lib/api-client";
import { ProjectCard, type ProjectCardData } from "@/features/workspace/components/project-card";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectCardData[] | null>(null);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    let isMounted = true;
    apiClient.getProductions().then((data) => {
      if (!isMounted) return;
      if (data && Array.isArray(data)) {
        setProjects(
          data.map((p, idx) => ({
            id: p.id,
            title: p.title,
            description: p.description,
            status: p.status,
            revision: idx + 1,
            updatedAt: p.updatedAt,
            duration: p.duration ?? "—",
            style: p.style,
          })),
        );
      } else {
        setLoadError(true);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <AppShell title="Projects" subtitle="All video productions in your workspace">
      <div className="space-y-6" data-projects-page="true">
        <div className="flex items-center justify-between">
          <p className="text-[12px] text-[var(--ce-text-muted,#78839b)]">
            {projects
              ? <>Showing all <strong>{projects.length}</strong> production(s)</>
              : "Loading productions…"}
          </p>
        </div>

        {projects === null && !loadError ? (
          <div className="flex h-48 flex-col items-center justify-center rounded-[var(--ce-radius-md,6px)] border border-dashed border-[var(--ce-border-subtle,rgb(151_164_190/0.1))] bg-[var(--ce-bg-panel,#131722)] p-6 text-center">
            <RefreshCw className="size-8 animate-spin text-[var(--ce-text-muted,#78839b)]" />
          </div>
        ) : loadError ? (
          <div className="flex h-48 flex-col items-center justify-center rounded-[var(--ce-radius-md,6px)] border border-dashed border-[var(--ce-state-error,#f87171)]/40 bg-[var(--ce-bg-panel,#131722)] p-6 text-center">
            <FolderKanban className="size-8 text-[var(--ce-state-error,#f87171)]" />
            <p className="mt-2 text-[13px] font-semibold text-[var(--ce-text-primary,#f4f6fb)]">Could not load productions</p>
            <p className="mt-1 text-[11px] text-[var(--ce-text-muted,#78839b)]">Is the backend running? Try refreshing the page.</p>
          </div>
        ) : projects && projects.length === 0 ? (
          <div className="flex h-48 flex-col items-center justify-center rounded-[var(--ce-radius-md,6px)] border border-dashed border-[var(--ce-border-subtle,rgb(151_164_190/0.1))] bg-[var(--ce-bg-panel,#131722)] p-6 text-center">
            <FolderKanban className="size-8 text-[var(--ce-text-muted,#78839b)]" />
            <p className="mt-2 text-[13px] font-semibold text-[var(--ce-text-primary,#f4f6fb)]">No productions yet</p>
            <p className="mt-1 text-[11px] text-[var(--ce-text-muted,#78839b)]">Upload a video to create your first production.</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects?.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
