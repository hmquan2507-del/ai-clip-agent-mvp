import Link from "next/link";
import { Clock, Film, MoreHorizontal } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  type Production,
  statusLabel,
  statusTone,
} from "@/lib/mock-productions";

type ProductionCardProps = {
  production: Production;
};

export function ProductionCard({ production }: ProductionCardProps) {
  return (
    <Card className="overflow-hidden transition hover:border-slate-700 hover:bg-slate-900">
      <CardContent>
        <div className="flex gap-4">
          <div className="flex h-20 w-28 shrink-0 items-center justify-center rounded-2xl bg-slate-800 text-slate-400">
            <Film className="h-7 w-7" />
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <Link
                  href={`/productions/${production.id}`}
                  className="line-clamp-1 font-semibold text-white hover:text-violet-300"
                >
                  {production.title}
                </Link>

                <p className="mt-1 line-clamp-2 text-sm leading-6 text-slate-400">
                  {production.description}
                </p>
              </div>

              <button
                type="button"
                className="rounded-lg p-1 text-slate-500 transition hover:bg-slate-800 hover:text-white"
                aria-label="Production actions"
              >
                <MoreHorizontal className="h-5 w-5" />
              </button>
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-2">
              <Badge tone={statusTone[production.status]}>
                {statusLabel[production.status]}
              </Badge>

              <Badge>{production.style}</Badge>

              <span className="inline-flex items-center gap-1 text-xs text-slate-500">
                <Clock className="h-3.5 w-3.5" />
                {production.updatedAt}
              </span>

              <span className="text-xs text-slate-500">
                {production.duration}
              </span>
            </div>

            <div className="mt-4">
              <Progress
                value={production.progress}
                label="Production progress"
                helperText={`${production.progress}%`}
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}