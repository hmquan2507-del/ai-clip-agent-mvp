import { CheckCircle2, Clock3, Loader2, Video } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

type RenderProgressPanelProps = {
  progress: number;
  status?: "queued" | "rendering" | "completed" | "failed";
};

const statusConfig = {
  queued: {
    label: "Queued",
    tone: "warning" as const,
    icon: Clock3,
  },
  rendering: {
    label: "Rendering",
    tone: "violet" as const,
    icon: Loader2,
  },
  completed: {
    label: "Completed",
    tone: "success" as const,
    icon: CheckCircle2,
  },
  failed: {
    label: "Failed",
    tone: "danger" as const,
    icon: Video,
  },
};

const stages = [
  "Preparing assets",
  "Applying subtitles",
  "Mixing audio",
  "Rendering video",
  "Finalizing export",
];

export function RenderProgressPanel({
  progress,
  status = "queued",
}: RenderProgressPanelProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <Card>
      <CardHeader
        title="Render Progress"
        description="Track export rendering progress for the approved Production."
      />

      <CardContent>
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300">
            <Icon
              className={`h-5 w-5 ${
                status === "rendering" ? "animate-spin" : ""
              }`}
            />
          </div>

          <div>
            <Badge tone={config.tone}>{config.label}</Badge>
            <p className="mt-2 text-sm text-slate-400">
              Estimated time remaining: 2 minutes
            </p>
          </div>
        </div>

        <div className="mt-6">
          <Progress
            value={progress}
            label="Render progress"
            helperText={`${progress}%`}
          />
        </div>

        <div className="mt-6 grid gap-3">
          {stages.map((stage, index) => {
            const stageProgress = ((index + 1) / stages.length) * 100;
            const done = progress >= stageProgress;

            return (
              <div
                key={stage}
                className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3"
              >
                <span className="text-sm text-slate-300">{stage}</span>

                <Badge tone={done ? "success" : "neutral"}>
                  {done ? "Done" : "Pending"}
                </Badge>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}