import { Cpu } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { workers } from "@/lib/mock-queue";

const workerTone = {
  online: "success",
  busy: "violet",
  idle: "neutral",
  offline: "danger",
} as const;

export function WorkerStatusPanel() {
  return (
    <Card>
      <CardHeader
        title="Worker Status"
        description="Current AI and render worker availability."
      />

      <CardContent>
        <div className="space-y-3">
          {workers.map((worker) => (
            <div
              key={worker.id}
              className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4"
            >
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-800 text-slate-300">
                  <Cpu className="h-5 w-5" />
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium text-white">{worker.name}</p>
                    <Badge tone={workerTone[worker.status]}>
                      {worker.status}
                    </Badge>
                  </div>

                  <p className="mt-1 text-sm text-slate-500">{worker.role}</p>
                  <p className="mt-2 text-sm text-slate-400">
                    {worker.currentTask}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
