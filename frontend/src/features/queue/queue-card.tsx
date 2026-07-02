import { Bot, Clock3 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  type QueueProduction,
  queueStatusLabel,
  queueStatusTone,
} from "@/lib/mock-queue";

type QueueCardProps = {
  production: QueueProduction;
};

export function QueueCard({ production }: QueueCardProps) {
  return (
    <Card className="transition hover:border-slate-700 hover:bg-slate-900">
      <CardContent>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex gap-4">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300">
              <Bot className="h-6 w-6" />
            </div>

            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone={queueStatusTone[production.status]}>
                  {queueStatusLabel[production.status]}
                </Badge>
                <Badge>{production.style}</Badge>
              </div>

              <h3 className="mt-3 text-lg font-semibold text-white">
                {production.title}
              </h3>

              <p className="mt-1 text-sm text-slate-400">
                Current stage: {production.stage}
              </p>

              <p className="mt-2 flex items-center gap-1 text-xs text-slate-500">
                <Clock3 className="h-3.5 w-3.5" />
                ETA: {production.eta} · Updated {production.updatedAt}
              </p>
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="ghost" size="sm">
              Retry
            </Button>
            <Button variant="danger" size="sm">
              Cancel
            </Button>
          </div>
        </div>

        <div className="mt-5">
          <Progress
            value={production.progress}
            label="Processing progress"
            helperText={`${production.progress}%`}
          />
        </div>
      </CardContent>
    </Card>
  );
}
