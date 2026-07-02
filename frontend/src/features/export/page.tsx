import { DashboardShell } from "@/components/layout/dashboard-shell";
import { SectionHeader } from "@/components/ui/section-header";
import { ExportWorkspace } from "@/features/export";

export default function ExportPage() {
  return (
    <DashboardShell
      title="Export"
      eyebrow="Export Workspace"
      actionHref="/productions"
      actionLabel="Back to Productions"
    >
      <div className="grid gap-6">
        <SectionHeader
          eyebrow="Sprint 4.7"
          title="Export Production"
          description="Configure export settings, monitor rendering progress, download completed videos, and share them."
        />

        <ExportWorkspace />
      </div>
    </DashboardShell>
  );
}