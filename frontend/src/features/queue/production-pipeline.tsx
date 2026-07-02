import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { pipelineSteps } from "@/lib/mock-queue";

export function ProductionPipeline() {
  return (
    <Card>
      <CardHeader
        title="Production Pipeline"
        description="Upload → AI Queue → Review → Export"
      />

      <CardContent>
        <div className="grid gap-3 md:grid-cols-7">
          {pipelineSteps.map((step) => {
            const Icon =
              step.status === "done"
                ? CheckCircle2
                : step.status === "active"
                  ? Loader2
                  : Circle;

            return (
              <div
                key={step.label}
                className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4"
              >
                <Icon
                  className={[
                    "h-5 w-5",
                    step.status === "done" && "text-emerald-300",
                    step.status === "active" && "animate-spin text-violet-300",
                    step.status === "waiting" && "text-slate-500",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                />

                <p className="mt-3 text-sm font-medium text-white">
                  {step.label}
                </p>

                <p className="mt-1 text-xs capitalize text-slate-500">
                  {step.status}
                </p>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
