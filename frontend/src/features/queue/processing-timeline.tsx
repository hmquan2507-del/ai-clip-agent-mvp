import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { pipelineSteps } from "@/lib/mock-queue";

export function ProcessingTimeline() {
  return (
    <Card>
      <CardHeader
        title="Processing Timeline"
        description="AI stages completed for the selected Production."
      />

      <CardContent>
        <div className="space-y-4">
          {pipelineSteps.map((step) => {
            const Icon =
              step.status === "done"
                ? CheckCircle2
                : step.status === "active"
                  ? Loader2
                  : Circle;

            return (
              <div key={step.label} className="flex gap-3">
                <div className="mt-0.5">
                  <Icon
                    className={[
                      "h-5 w-5",
                      step.status === "done" && "text-emerald-300",
                      step.status === "active" && "animate-spin text-violet-300",
                      step.status === "waiting" && "text-slate-600",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                  />
                </div>

                <div>
                  <p className="font-medium text-white">{step.label}</p>
                  <p className="mt-1 text-sm capitalize text-slate-500">
                    {step.status}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
