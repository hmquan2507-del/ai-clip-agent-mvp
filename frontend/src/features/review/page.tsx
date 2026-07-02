import { DashboardShell } from "@/components/layout/dashboard-shell";
import { SectionHeader } from "@/components/ui/section-header";
import { ReviewWorkspace } from "@/features/review";

export default function ReviewPage() {
  return (
    <DashboardShell
      title="Review"
      eyebrow="Review Workspace"
      actionHref="/export"
      actionLabel="Go to Export"
    >
      <div className="grid gap-6">
        <SectionHeader
          eyebrow="Sprint 4.6"
          title="Review AI Output"
          description="Review video preview, transcript, subtitles, AI suggestions, then approve or regenerate."
        />

        <ReviewWorkspace />
      </div>
    </DashboardShell>
  );
}